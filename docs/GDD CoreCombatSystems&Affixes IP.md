# **Game Design Document & Implementation Plan: Core Combat Systems (v4.0)**

**Version:** 4.1 (Final)
**Date:** November 10, 2025

## **1.0 Core Combat Flow & Resolution Pipeline**

This document outlines the final, step-by-step process for resolving a single attack. This pipeline is executed for *each individual hit* within a skill.

| Step | Action | Description | GDD Ref. | System Interaction |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Evasion Check** | A roll is made against the Defender's `Evasion Chance` to determine if the hit is downgraded. On success (hit is "evaded"), proceed to Step 2. On failure, proceed to Step 3 as a **Normal Hit**. | 2.1 | Bonus/Penalty |
| **2** | **Dodge Check** | *Only if Step 1 succeeds.* A second roll against the Defender's `Dodge Chance` determines if the evaded hit is a full **Dodge** (ending the sequence) or a **Glancing Blow**. | 2.1 | Bonus/Penalty |
| **3** | **Critical Hit Check**| A roll against the Attacker's `Crit Chance`. **This check is automatically skipped if the hit is a Glancing Blow.** | 2.2 | Bonus/Penalty |
| **4** | **Pre-Mitigation Dmg**| Calculate initial damage: `(Base Damage + Flat Bonuses)`. Tier 2 Crits apply multiplier here. | 2.1 | - |
| **5** | **Defense Mitigation**| Apply Armor/Pierce formula: `MAX((Pre-Mit Dmg - Armor), (Pre-Mit Dmg * Pierce))`. | 2.1 | - |
| **6** | **Post-Mitigation Dmg**| Apply final multipliers to the mitigated damage. Tier 3 Crits apply here. | 2.1 | - |
| **7** | **Glancing Penalty**| If the hit is a Glancing Blow, apply the final damage penalty: `Final Damage *= 0.5`. | 2.1 | Evasion System |
| **8** | **Block Check** | A roll against the Defender's `Block Chance`. If successful, `Final Damage -= Block Amount`. Damage cannot be reduced below 1 by a block. | 2.1 | Bonus/Penalty |
| **9** | **Finalization** | Apply the final calculated damage to the Defender's health and dispatch all relevant events (`OnHit`, `OnCrit`, `OnDodge`, `OnBlock`, etc.). | 4.1 | State & Event Systems |

## **2.0 Foundational System Designs**

These three systems form the core foundation upon which all affixes and skills are built.

### **2.1 Evasion System (Glancing Blows & Dodge)**

*   **Core Concept:** A two-step avoidance system that favors damage mitigation over complete misses, providing better player feedback and more consistent damage output.
*   **Stats:**
    *   `evasion_chance`: The total percentage chance to either Glance or Dodge an attack. Capped at **75%**.
    *   `dodge_chance`: The percentage chance for a successful evasion to be a full Dodge instead of a Glance.
*   **Mechanics:**
    1.  An attack has `evasion_chance` percent chance to be "Evaded."
    2.  An "Evaded" attack then has `dodge_chance` percent chance to be a full **Dodge**.
    3.  If it is not a full Dodge, it becomes a **Glancing Blow**.
    4.  Glancing Blows deal **50% less damage** and **cannot Crit**.
*   **Event Hooks:** `OnDodge`, `OnGlancingBlow`.
**Entropy Safeguard (Clarification 1):** To prevent player frustration from "unlucky streaks" of consecutive misses, an entropy system is implemented.
New State Property: A dodge_entropy_modifier is added to EntityState, defaulting to 0.
**Logic:**
    1. When an OnDodge event occurs against a target, the StateManager adds a significant Penalty to that target's dodge_chance and evasion_chance roll modifiers (e.g., a Modifier with -0.25 value and a short duration, sourced as "Entropy").
    2. When that target is next hit by any attack (Normal Hit or Glancing Blow), all active "Entropy" modifiers on it are immediately removed.
**Result:** After an enemy dodges, the next attack is much more likely to hit, guaranteeing that long chains of full misses are statistically near-impossible and improving player feel.

### **2.2 Bonus & Penalty System**

Core Concept: A flat, additive modifier system for chance-based rolls.
Mechanics: Bonuses (+X%) and Penalties (-X%) are applied to the base chance of a roll. The final chance is clamped between 0% and 100%.
Stacking & Duration:
Tracking: All active modifiers (Bonuses/Penalties) are stored as individual Modifier objects in the EntityState.roll_modifiers dictionary, keyed by the roll type (e.g., crit_chance).
Duration: Each Modifier object has its own duration. The StateManager.update() loop decrements the duration of every active modifier each frame and removes any that have expired. This allows for numerous overlapping effects with independent timers.
Calculation (Summing): When a roll is made, the logic sums the value of all active Modifier objects for that specific roll type. This sum is the final bonus or penalty.
UI/UX Consideration (Decision):
Decision: The specific UI implementation (e.g., showing stacked "Advantage icons") is a UI/UX design concern and will be parked for now.
Action for this Document: The StateManager and EntityState will be designed to hold all the necessary data. The list of active Modifier objects on an entity will be easily queryable, so the UI can later access this list to display appropriate icons and tooltips (e.g., iterating through state.roll_modifiers['crit_chance'] to show three separate "Crit Bonus" icons if three buffs are active). The backend logic is decoupled from its final visual representation.
*   **Applicable Rolls:** Evasion, Dodge, Crit, Block, and Proc Rate rolls.

### **2.3 Active Resource & Cooldown System**

*   **Core Concept:** Resources are generated through active gameplay rather than passive regeneration, creating a more engaging combat loop. Cooldowns govern skill frequency.
*   **Stats:**
    *   `max_resource`, `resource_on_hit`, `resource_on_kill`.
    *   `base_cooldown`, `cooldown_reduction`.
*   **Mechanics:**
    *   **Resource:** Special skills cost resource. Resource is gained primarily through event-driven handlers (e.g., a `ResourceOnHitHandler` that grants resource based on the `resource_on_hit` stat).
    *   **Cooldown:** Skills have a `base_cooldown` modified by `cooldown_reduction`. Using a skill puts it on cooldown. Cooldown timers are reduced in the main game loop (`StateManager.update`).

2.4 Event System & Data Structures (Revised - Clarification 3)
Core Concept: A central, event-driven architecture using an EventBus.
Event Data Classes (events.py): Yes, all new events will have formal dataclass structures that match the existing pattern, providing clean, predictable data payloads.

Formal Definitions:
@dataclass
class OnDodgeEvent(Event):
    """Fired when an attack is fully dodged."""
    attacker: "Entity"
    defender: "Entity"

@dataclass
class OnBlockEvent(Event):
    """Fired when a hit is successfully blocked."""
    attacker: "Entity"
    defender: "Entity"
    damage_before_block: float
    damage_blocked: float
    hit_context: "HitContext" # Full context of the hit

@dataclass
class OnGlancingBlowEvent(Event):
    """Fired when a hit is downgraded to a Glancing Blow."""
    hit_event: "OnHitEvent" # Contains context of the glancing hit (with reduced damage)
    
@dataclass
class OnSkillUsedEvent(Event):
    """Fired when an entity successfully uses a skill (after cost/cooldown checks)."""
    entity: "Entity"
    skill_id: str
    skill_type: str # 'Special', 'Ultimate', etc.
(Note: The full HitContext is added to OnBlockEvent to allow complex affixes to know if the blocked hit was also, for example, a crit.)
---

## **3.0 Implementation Plan: Step-by-Step Refactoring**

This plan details the modifications required for your existing codebase.

### **Phase 1: Foundation Update (Modifying `models.py` & `state.py`)**

**Goal:** Extend your data structures to support the new mechanics.

1.  **Modify `models.py: EntityStats`:**
    *   Add the new stat fields: `evasion_chance`, `dodge_chance`, `block_chance`, `block_amount`, `max_resource`, `resource_on_hit`, `resource_on_kill`, `cooldown_reduction`.
    *   Update the `__post_init__` method to include validation for these new stats (e.g., clamping `evasion_chance` between 0 and 0.75).
    *   Remove `resource_regen_rate`.

2.  **Modify `state.py: Modifier` and `EntityState`:**
    *   Create the `Modifier` dataclass as planned to represent temporary bonuses and penalties.
    *   Add the new dynamic fields to the `EntityState` dataclass: `current_resource`, `roll_modifiers: Dict[str, List[Modifier]]`, and `active_cooldowns: Dict[str, float]`.

3.  **Modify `state.py: StateManager`:**
    *   In `register_entity()`, ensure `current_resource` is initialized to the entity's `final_stats.max_resource`.
    *   Create new methods:
        *   `add_resource(entity_id, amount)`: Increases resource, clamping at max.
        *   `spend_resource(entity_id, amount) -> bool`: Decreases resource, returns success/failure.

Phase 2: Full Pipeline, Events, & Affix Handling (Revised - Clarification 4)
Goal: Implement the new pipeline and a robust system for handling both stat-based and reactive/conditional affixes from the CSVs.
Modify affixes.csv Schema:
Add a new column: trigger_data. This column will be used for all reactive/conditional affixes and will use the same structured text format as the skills.csv triggers.
Example affixes.csv with a reactive affix:
code
Csv
affix_id,stat_affected,mod_type,base_value,description,trigger_data
...
refl_dmg_t1,,-,,Reflect {value}% of blocked damage,OnBlock|proc_rate:1.0|reflect_damage:0.5
Note that stat_affected and mod_type are empty for purely reactive affixes.
Modify the CSV Parser: The parser must now also read and parse the trigger_data column for affixes, just as it does for skills.
Refactor Entity.calculate_final_stats():
This function will now be responsible for two things:
Calculating the final numerical stats (as before).
Aggregating a list of all active triggers from equipped items.
The Entity class will have a new property: self.active_triggers: List[Trigger] = [].
calculate_final_stats() will clear this list and then populate it with all parsed Trigger objects from its equipped Items.
Rewrite CombatEngine.process_skill_use():
This function becomes the central executor for all triggers.
Trigger Aggregation: At the start of the function, it will create a temporary list of all triggers for this specific action: action_triggers = skill.triggers + attacker.active_triggers.
Event-Driven Trigger Check: After each event is dispatched (e.g., after event_bus.dispatch(hit_event)), the function will iterate through action_triggers and check if any of them match the event type (e.g., if trigger.event == "OnHit").
If a trigger matches, it will perform its check (e.g., proc rate roll) and then execute its result. The "result" logic will need to be expanded to handle new outcomes like reflect_damage.
### **Phase 3: Simulation & Balancing**

**Goal:** Update the time-based loop and create handlers for conditional affixes.

1.  **Modify `state.py: StateManager.update_dot_effects()` -> `update(delta_time)`:**
    *   Rename the function to `update` as it now has more responsibilities.
    *   Add logic to iterate through and reduce durations for `active_cooldowns` and `roll_modifiers`, removing them when they expire.
    *   (DoT logic remains the same).

2.  **Create Handlers for Conditional Affixes (`handlers.py`):**
    *   Create a new file for event-driven handlers.
    *   Implement `FocusedRageHandler`: Subscribes to `OnSkillUsedEvent` (you'll need to create this event), checks if the skill is `Special`, and applies a `Modifier` to the attacker's `roll_modifiers['crit_chance']`.
    *   Implement `BlindingRebukeHandler`: Subscribes to `OnBlockEvent` and applies a `Modifier` to the *attacker's* `roll_modifiers['evasion_chance']` with a negative value.

4.0 Performance Considerations & Testing (New Section - Clarification 5)
Concern: The new 9-step pipeline potentially introduces multiple RNG calls per hit (Evasion, Dodge, Crit, Block, Proc Rates), which could become a performance bottleneck, especially in simulations.
Mitigation and Testing Plan:
Algorithmic Efficiency (Short-Circuiting): The proposed pipeline is already designed to be efficient by short-circuiting. For example, if an attack is Dodged in Step 2, the subsequent rolls for Crit and Block are never performed. This significantly reduces the average number of RNG calls per hit.
RNG Optimization:
Implementation: Instead of calling random.random() multiple times, a single, more performant call can be made at the start of resolve_hit to get a small array of random numbers (e.g., rng_values = [random.random() for _ in range(5)]). Each step in the pipeline then consumes the next number from this array. This can be slightly faster by reducing function call overhead in performance-critical languages.
Initial Plan: We will start with the simpler, more readable separate calls to random.random(). The optimization will only be implemented if profiling shows it to be necessary.
Dedicated Performance Testing Phase:
Task 4.1 (Simulation Stress Test): Create a new simulation script, run_stress_test.py.
Configuration: This script will run a simulation with a very high number of entities and hits (e.g., 10 attackers vs 10 defenders for 60 seconds, resulting in thousands of hit resolutions).
Profiling: We will use Python's built-in cProfile module to run this stress test and generate a performance report.
Analysis: The report from cProfile will show exactly how much time is being spent in each function (resolve_hit, _perform_evasion_check, random.random(), etc.).
Action: If the total time spent in RNG or the pipeline functions is found to be a significant bottleneck (e.g., >20% of the total simulation time), we will prioritize implementing the RNG optimization described above.

### **Phase 5: Final Testing & Data Implementation**

**Goal:** Create the CSV data for the new systems and run a comprehensive test.

1.  **Create `affixes.csv`:**
    *   Populate it with the affixes from the GDD v4.0 list.
    *   For chance-based affixes like `proc_rate_bleed`, the `stat_affected` column will contain `proc_rate_bleed`.

2.  **Run `run_full_test.py`:**
    *   This script should set up a scenario with an attacker and defender.
    *   The attacker should be given an item with affixes like `+evasion_chance` and a skill with a cooldown.
    *   The simulation should run for a few seconds, with the `StateManager.update(delta_time)` being called each frame.
    *   **Verification:**
        *   The skill should go on cooldown and be unusable until the timer expires.
        *   Glancing Blows and Blocks should be observed in the combat log/output.
        *   The effects of conditional affixes (like `Focused Rage`) should be verifiable by checking the entity's `roll_modifiers` in the `StateManager` during the simulation.
        *   The final report from your existing `ReportGenerator` should now include stats for Dodges, Glances, and Blocked Damage.