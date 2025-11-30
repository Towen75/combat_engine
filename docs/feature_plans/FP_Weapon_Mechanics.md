# 📅 Feature Plan: Phase 2 - Weapon Mechanics

**Status:** Draft
**Target Version:** v2.8.0
**Owner:** System Architect

## 1. Executive Summary
Currently, all entities use a hardcoded "Basic Attack" (1 hit, 100% damage) regardless of what they are holding. This phase introduces **Weapon-Specific Skills**.
We will allow Items to define a `default_skill_id`. When an entity attacks with that item equipped, the simulation will use that specific Skill definition (e.g., "Dagger Slash": 2 hits @ 50% damage) instead of the generic attack.

## 2. Goals & Success Criteria
*   **Goal 1:** Differentiate weapons beyond just stat sticks.
*   **Goal 2:** Support "Multi-hit" weapons (Daggers/Fists) vs "Heavy" weapons (Hammers/Axes).
*   **Goal 3:** Visualize the difference in the Combat Log (e.g., "Hero hits Goblin x2").
*   **Metric:** A simulation run with a Dagger shows significantly more "Hit Events" than a run with a Greatsword, even if DPS is similar.

## 3. Scope Boundaries
### ✅ In Scope
*   **Schema:** Add `default_skill_id` to `ItemTemplate` (and `families.yaml`).
*   **Logic:** Update `CombatEngine.process_attack` (or `SimulationRunner`) to look up the weapon's skill.
*   **Content:** Create Basic Skills for each weapon type (Dagger, Sword, Axe, Staff, Bow).
*   **Visuals:** Combat Log reflects the specific skill name used.

### ⛔ Out of Scope
*   **Active Abilities:** We are focusing on the *Auto-Attack* replacement, not a spell bar (that is Milestone 5).
*   **Ammo Systems:** Quivers are just stats for now.

## 4. Implementation Strategy (Phasing)

### 🔹 Phase 2.1: Skill Data & Mapping
*   **Focus:** The Data Layer.
*   **Task:**
    1.  Create `data/skills.csv` entries for basic weapon attacks.
    2.  Update `families.yaml` to include `default_attack_skill`.
    3.  Update `ItemTemplate` to hold this ID.
*   **Output:** `WORK_ITEM-2.1`

### 🔹 Phase 2.2: Combat Integration
*   **Focus:** The Engine.
*   **Task:**
    1.  Refactor `CombatEngine.process_attack` to accept a `Skill` object (it already does mostly).
    2.  Update `SimulationRunner` to fetch the correct skill from the Entity's Main Hand item before attacking.
*   **Output:** `WORK_ITEM-2.2`

### 🔹 Phase 2.3: Content Expansion
*   **Focus:** The "Feel".
*   **Task:** Tune the new skills.
    *   *Dagger:* 2 Hits, 0.6x Damage each.
    *   *Axe:* 1 Hit, 1.2x Damage, Bleed Trigger.
*   **Output:** `WORK_ITEM-2.3`

## 5. Risk Assessment
*   **Risk:** **Damage Inflation.**
    *   *Impact:* If we add "2 Hits" but forget to lower the damage multiplier, Daggers become OP.
    *   *Mitigation:* Use `damage_multiplier` in `Skill` definitions (requires ensuring `EntityStats` supports skill multipliers, or we handle it in `CombatEngine`).