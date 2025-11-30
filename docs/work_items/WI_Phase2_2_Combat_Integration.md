# 📋 Work Item: Phase 2.2 - Combat Integration

**Phase:** Phase 2.2 - Weapon Mechanics
**Component:** Core Engine / Simulation
**Context:** `docs/feature_plans/FP_WEAPON_MECHANICS.md`

## 🎯 Objective
Update the simulation logic to utilize Weapon-Specific Skills. Instead of every entity using a hardcoded "Basic Attack", the system must dynamically check the entity's equipped weapon, retrieve the associated Skill (defined in Phase 2.1), and execute that skill with the correct damage multipliers and hit counts.

## 🏗️ Technical Implementation

### 1. Data Model Updates
*   **File:** `src/core/models.py`
    *   **Class:** `Entity`
    *   **New Method:** `get_default_attack_skill_id() -> str`
        *   Logic: Check "Weapon" slot. If item exists and has `default_attack_skill`, return it. Else return `"attack_unarmed"` (or `"basic_slash"`).

### 2. Engine Updates
*   **File:** `src/combat/engine.py`
    *   **Update:** `calculate_skill_use`
    *   **Logic:** Apply `skill.damage_multiplier` to the final damage of *each hit*.
        *   *Current:* `damage = hit_context.final_damage`
        *   *New:* `damage = hit_context.final_damage * skill.damage_multiplier`

### 3. Simulation Updates
*   **File:** `src/simulation/combat_simulation.py`
    *   **Update:** `SimulationRunner.update()`
    *   **Logic:** Replace the generic `resolve_hit` call with a dynamic skill execution flow:
        1.  Identify Target.
        2.  Call `attacker.get_default_attack_skill_id()`.
        3.  Look up `SkillDefinition` from `GameDataProvider`.
        4.  Convert to runtime `Skill` object (handling triggers/effects if any).
        5.  Call `combat_engine.process_skill_use()`.

### 4. Combat Log Updates
*   **File:** Combat logging system (likely `src/simulation/telemetry.py` or similar)
    *   **Update:** Replace generic "hits" messages with skill-specific names
    *   **Example:** "Hero Dual Slashes Goblin for 12 damage" instead of "Hero hits Goblin"
    *   **Logic:** Use `skill.name` from the executed skill for log messages

## 🛡️ Architectural Constraints
*   [x] **Backward Compatibility:** If an entity has no weapon, it **must** fallback to a valid skill ID (e.g., `attack_unarmed`) to prevent crashes.
*   [x] **State Safety:** Ensure `damage_multiplier` affects the *action*, not the entity's permanent stats.
*   [x] **Performance:** Skill lookup happens every attack. `GameDataProvider` uses O(1) dict lookups, which is acceptable for combat frequency.
*   [x] **Error Handling:** Phase 2.1 validation prevents missing skills, but include defensive checks for runtime safety.

## 📝 Implementation Notes
*   **Skill Object Conversion:** `SkillDefinition` (data) → `Skill` (runtime) conversion may require processing triggers/effects. Ensure the conversion handles optional fields properly.
*   **Combat Log Integration:** Update logging to use `skill.name` for more descriptive combat feedback (e.g., "Heavy Swing" instead of "Basic Attack").
*   **Testing Strategy:** Unit tests should verify skill lookup, damage multipliers, and multi-hit behavior independently before integration testing.

## ✅ Definition of Done (Verification)
1.  [ ] **Unit Test:** `tests/test_weapon_mechanics.py`
    *   **Multiplier:** Equip a Greatsword (1.4x). Verify damage > Base Damage.
    *   **Multi-Hit:** Equip a Dagger (2 hits). Verify `process_skill_use` generates 2 `ApplyDamageAction`s.
    *   **Fallback:** Equip nothing. Verify `attack_unarmed` is used.
2.  **Integration:** Run `dashboard`. A Warrior with a Greatsword should show higher damage numbers per hit than a Rogue with a Dagger (who should show more hits).
