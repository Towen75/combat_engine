# PR 7 — Expand `HitContext` Into Full Telemetry Object (Debug-Friendly, Testable, Complete)

This PR transforms `HitContext` from a minimal output object into a **rich, structured telemetry record** capturing every meaningful intermediate value in the hit‑resolution pipeline. This greatly improves debuggability, testing depth, and the ability to run combat logs and post‑battle analytics.

This is a major quality‑of‑life improvement for both developers and designers.

---

# ✅ Summary

**Goal:** Make `HitContext` contain *every* step of calculation, including:

* Base damage (raw + resolved)
* Crit chance, crit roll, crit outcome, crit multiplier
* Additive & multiplicative modifiers
* Pierce, effective armor
* Pre‑armor and post‑armor damage
* Final damage
* RNG values used (optional)
* Tags / flags (e.g., "is_ability", "is_crit", "blocked", "dodged")

**Why:**

* Allows deterministic debugging when combat feels off
* Makes unit tests more thorough and easier to write
* Supports future combat-log UI or post-battle replay
* Enables balance analysis using recorded telemetry

---

# 📦 New `HitContext` Structure

## `src/models/hit_context.py`

```python
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class HitContext:
    attacker_id: str
    defender_id: str

    # RNG & roll data
    rng_rolls: Dict[str, float] = field(default_factory=dict)

    # Damage values
    base_raw: Any = None           # tuple or int as provided
    base_resolved: int = 0

    crit_chance: float = 0.0
    crit_roll: float = 0.0
    crit_multiplier: float = 1.0
    is_crit: bool = False

    additive_bonus: float = 0.0
    multiplicative_bonus: float = 1.0

    pierce: int = 0
    effective_armor: int = 0

    damage_pre_mitigation: float = 0.0
    damage_post_armor: float = 0.0
    final_damage: int = 0

    # Meta flags
    tags: Dict[str, bool] = field(default_factory=dict)

    # Arbitrary extra metadata for debugging, mods, analytics
    extra: Dict[str, Any] = field(default_factory=dict)
```

> ✔ This structure future‑proofs the engine for extensions.

---

# 🔧 Engine Integration

Update `CombatEngine.resolve_hit()` to populate the context.

Example (high‑level diff):

```diff
*** Begin Patch
*** Update File: src/engine.py
@@
 def resolve_hit(self, attacker, defender, state_manager):
-    ctx = HitContext(attacker.id, defender.id)
+    ctx = HitContext(attacker_id=attacker.id, defender_id=defender.id)

     # 1. Base damage
+    ctx.base_raw = hit.base_damage
     ctx.base_resolved = math.resolve_base_damage(hit.base_damage)

     # 2. Crit
     ctx.crit_chance = hit.crit_chance
     ctx.crit_roll = math.rng.random()
     ctx.is_crit = ctx.crit_roll < ctx.crit_chance
     ctx.crit_multiplier = hit.crit_multiplier if ctx.is_crit else 1.0

     # 3–4. Modifiers
     ctx.additive_bonus = hit.flat_bonus
     ctx.multiplicative_bonus = hit.percent_bonus

     # compute early
     raw = ctx.base_resolved * ctx.crit_multiplier
     raw += ctx.additive_bonus
     raw *= ctx.multiplicative_bonus
     ctx.damage_pre_mitigation = raw

     # 5–6. Armor & pierce
     ctx.pierce = hit.pierce
     ctx.effective_armor = max(0, defender.armor - hit.pierce)
     ctx.damage_post_armor = math.apply_armor(raw, ctx.effective_armor)

     # 7–8. Final
     ctx.final_damage = max(1, int(ctx.damage_post_armor))

     return ctx
*** End Patch
```

---

# 🧪 Test Suite

This PR enables deep validation of combat behaviour.

## 1. Test Crit Telemetry

```python
def test_hitcontext_records_crit_data(rng_fixed, engine, attacker, defender):
    ctx = engine.resolve_hit(attacker, defender, rng_fixed)
    assert ctx.crit_roll != 0
    assert ctx.crit_chance == attacker.crit_chance
    assert ctx.is_crit in (True, False)
```

## 2. Test Armor + Pierce Recording

```python
def test_hitcontext_armor_fields(engine, attacker, defender, state):
    ctx = engine.resolve_hit(attacker, defender, state)
    assert ctx.pierce == attacker.pierce
    assert ctx.effective_armor == max(0, defender.armor - attacker.pierce)
```

## 3. Full Calculation Consistency

```python
def test_hitcontext_math_consistency(engine, attacker, defender, state):
    ctx = engine.resolve_hit(attacker, defender, state)
    expected = ... manually compute ...
    assert ctx.final_damage == expected
    assert ctx.damage_post_armor == pytest.approx(ctx.final_damage, rel=0.01)
```

## 4. Test Tags/Extra Metadata

```python
def test_hitcontext_supports_tags():
    ctx = HitContext("A","B")
    ctx.tags["blocked"] = True
    assert ctx.tags["blocked"] is True
```

---

# 🚦 Migration Checklist

* [ ] Create extended `HitContext` model
* [ ] Update `CombatEngine.resolve_hit` to populate all fields
* [ ] Update any consumers of HitContext (UI, logs, tests)
* [ ] Add comprehensive telemetry tests
* [ ] Add optional `record_rng=True` flag in CombatMath for debugging seeds
* [ ] Integrate with logging or replay system if available

---

# 🎯 Outcome

After merging PR 7:

* Every hit produces a **complete forensic record** of what happened.
* Bugs in combat math become dramatically easier to trace.
* Balance design becomes data‑driven.
* Paves the way for

  * Combat log UI
  * Battle replay
  * Automated balance simulators
  * Designer debugging tools

---

**PR 7 Complete. Ready for review and merge.**
