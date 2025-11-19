### **PR-P1S2: Core Mechanics Correction and Determinism Hardening**

## Overview

This PR executes the second step of the Foundational Stability phase. It addresses four critical bugs and inconsistencies in the core combat logic and random number generation (RNG) system.

By fixing these issues, this PR ensures that the game's combat mechanics are correct, predictable, and fully deterministic for testing and balancing purposes.

---

# ✅ Summary

**Goal:** Correct major bugs in the game's core systems:
1.  **Fix Hardcoded Proc Rate:** Make skill trigger proc rates fully data-driven.
2.  **Fix Dual-Stat Affixes:** Implement the logic to make dual-stat affixes functional.
3.  **Unify RNG Handling:** Eliminate non-deterministic behavior by ensuring all systems can use an injectable RNG instance.
4.  **Correct Minor Logic Errors:** Fix incorrect game logic related to evasion rewards and glancing blows.

**Why this is a foundational change:**
*   These bugs cause incorrect or unpredictable gameplay, making balancing impossible.
*   Inconsistent RNG prevents reliable, repeatable testing, which is essential for a CI/CD pipeline.
*   Correcting these issues now prevents them from complicating the implementation of all future features.

---

# 🔧 Technical Changes

### 1. Proc Rate Correction
The `CombatOrchestrator` is refactored to respect the `proc_rate` defined in the game data. This involves passing the `proc_rate` from the `CombatEngine` to the orchestrator via the `ApplyEffectAction`.

### 2. Dual-Stat Affix Rework
The `ItemGenerator` and `RolledAffix` model are refactored. The generator now correctly rolls two separate values for dual-stat affixes, and the `Entity.calculate_final_stats` method is updated to apply both values correctly.

### 3. RNG Unification
`ItemGenerator`, `CombatOrchestrator`, and `EffectHandler` classes are all updated to accept an optional `rng` instance in their constructors. They now use this local `rng` instance for all random operations, falling back to the global `random` module only if no instance is provided.

### 4. Gameplay Logic Fixes
*   The `resource_on_kill` reward granted to an attacker when their attack is dodged is removed.
*   The `apply_glancing_damage` function is corrected to ensure a multiplier of `0` results in `0` damage.

---

# 🔧 Code Changes (Example Diffs)

### **1. Fix Hardcoded Proc Rate (`src/combat_orchestrator.py` & `src/models.py`)**

```diff
*** Begin Patch
*** Update File: src/models.py
@@ @dataclass
 class ApplyEffectAction(Action):
     target_id: str
     effect_name: str
     stacks_to_add: int = 1
     source: str = "skill"
+    proc_rate: float = 1.0
*** Update File: src/combat_orchestrator.py
@@ def _execute_effect_action(self, action: ApplyEffectAction) -> None:
-        proc_rate = 0.5  # TODO: Make this configurable
-        should_apply = rng_value < proc_rate
+        should_apply = True
+        if action.proc_rate < 1.0:
+            rng_value = self.rng.random() if self.rng else random.random()
+            should_apply = rng_value < action.proc_rate
*** End Patch
```

### **2. Fix Dual-Stat Affixes (`src/models.py` & `src/item_generator.py`)**

```diff
*** Begin Patch
*** Update File: src/models.py
@@ @dataclass
 class RolledAffix:
     # ...
     value: float
+    dual_value: Optional[float] = None
-    # (get_dual_value() and other parsing methods removed)
*** Update File: src/item_generator.py
@@ def _roll_one_affix(self, affix_id: str, max_quality: int) -> RolledAffix:
+    # (New logic to check for ';' in base_value_str, roll two separate
+    # values, and populate both `value` and `dual_value` fields)
*** End Patch
```

### **3. Unify RNG (`src/item_generator.py` example)**

```diff
*** Begin Patch
*** Update File: src/item_generator.py
@@
-class ItemGenerator:
-    def __init__(self, game_data: dict = None):
+import random
+
+class ItemGenerator:
+    def __init__(self, game_data: dict = None, rng: random.Random = None):
         # ...
+        self.rng = rng if rng is not None else random.Random()
@@ def _roll_quality_tier(self, rarity: str) -> dict:
-        selected_tier = random.choices(possible_tiers, weights=weights, k=1)[0]
+        selected_tier = self.rng.choices(possible_tiers, weights=weights, k=1)[0]
*** End Patch
```
*(This pattern is also applied to `CombatOrchestrator` and `EffectHandler`.)*

### **4. Fix Gameplay Logic (`src/engine.py` & `src/combat_math.py`)**

```diff
*** Begin Patch
*** Update File: src/engine.py
@@ def process_skill_use(...):
         if hit_context.was_dodged:
             dodge_event = OnDodgeEvent(attacker=attacker, defender=defender)
             event_bus.dispatch(dodge_event)
-            state_manager.add_resource(attacker.id, attacker.final_stats.resource_on_kill)
             continue
*** Update File: src/combat_math.py
@@ def apply_glancing_damage(damage: float, glancing_multiplier: float) -> float:
-    if glancing_multiplier <= 0:
-        return damage
-    return damage * glancing_multiplier
+    multiplier = max(0.0, min(1.0, glancing_multiplier))
+    return damage * multiplier
*** End Patch
```

---

# 🧪 Test Suite Additions

This PR requires adding and updating tests to validate the fixes.

1.  **Proc Rate Test:** A test is added to confirm that a skill with a `proc_rate` of `0.25` in the data file correctly applies its effect approximately 25% of the time over a large number of runs with a seeded RNG.
2.  **Dual-Stat Test:** A new unit test for `Entity.calculate_final_stats` is created. It equips an item with a freshly generated dual-stat affix and asserts that *both* of the character's final stats have been correctly modified.
3.  **RNG Determinism Test:** An end-to-end integration test is added that seeds the entire simulation (including the `ItemGenerator`). It runs the simulation twice with the same seed and asserts that the final state of the `StateManager` is identical in both runs.
4.  **Gameplay Logic Tests:** The tests for `apply_glancing_damage` are updated to check for the correct `0` damage behavior. A test is added to confirm an attacker's resources do not change when their attack is dodged.

---

# 🚦 Migration Checklist

*   [ ] Refactor `CombatOrchestrator` to use the `proc_rate` from `ApplyEffectAction`.
*   [ ] Refactor `RolledAffix`, `ItemGenerator`, and `Entity.calculate_final_stats` to correctly handle dual-stat affixes.
*   [ ] Add an optional `rng` parameter to the constructors of `ItemGenerator`, `CombatOrchestrator`, and `EffectHandler` and update their internal logic.
*   [ ] Remove the incorrect resource reward on dodge from `engine.py`.
*   [ ] Correct the logic in the `apply_glancing_damage` function.
*   [ ] Add or update unit tests to validate all of the above fixes.
*   [ ] Run the full `pytest` suite to ensure no regressions have been introduced.

---

# 🎯 Outcome

After this PR is merged:
*   The game mechanics will behave correctly and as intended by the data-driven design.
*   Dual-stat items, a core RPG feature, will be fully functional.
*   The entire simulation pipeline will be capable of fully deterministic execution, which is a massive win for testing and balancing.
*   The codebase will be free of several subtle but significant logical bugs, making it a much more stable foundation for future development.

---

**PR-P1S2 Complete. Ready for review and merge.**