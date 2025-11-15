# **Game Design Document: Core Combat Systems & Affixes**
**Version:** 4.0
**Date:** November 10, 2025

## 1.0 Core Combat Flow (Revised)

This document outlines the complete, step-by-step process for resolving a single attack instance, incorporating the Evasion, Glancing Blow, and Post-Calculation Block systems.

### 1.1 The Attack Resolution Pipeline

Each time an entity uses a skill or attack on a target, the following sequence is executed for **each individual hit**.

**Step 1: Evasion Check**
*   **Purpose:** To determine if the attack will be a Normal Hit or if it is "Evaded" (potentially becoming a Glancing Blow or a full Dodge).
*   **Logic:** A roll is made against the Defender's `Evasion` chance.
    *   **On Success (Roll > Evasion):** The attack is a **Normal Hit**. Proceed to Step 3.
    *   **On Failure (Roll <= Evasion):** The attack has been "Evaded". Proceed to Step 2.

**Step 2: Dodge Check**
*   **Purpose:** To determine if an "Evaded" attack is a full Dodge or a downgraded Glancing Blow. This step is *only* performed if Step 1 fails.
*   **Logic:** A roll is made against the Defender's `Dodge Chance`.
    *   **On Success (Roll <= Dodge Chance):** The attack is a **Full Dodge**. The sequence ends. Dispatch an **`OnDodge`** event.
    *   **On Failure (Roll > Dodge Chance):** The attack is a **Glancing Blow**. Proceed to Step 3 with the "Is Glancing" flag set to `True`. Dispatch an **`OnGlancingBlow`** event.

**Step 3: Critical Hit Check**
*   **Purpose:** To determine if the hit is a critical.
*   **Logic:** A roll is made against the Attacker's `Critical Hit Chance`.
    *   **CRUCIAL RULE:** A hit flagged as a **Glancing Blow** cannot become a Critical Hit. This check is skipped if the "Is Glancing" flag is `True`.

**Step 4: Pre-Mitigation Damage Calculation**
*   **Purpose:** To calculate the initial damage value before defenses are applied.
*   **Formula:** `Pre-Mitigation Damage = (Base Damage + All Flat Damage Bonuses)`
*   *Note: This is where Tier 2 "Enhanced" Critical Hit multipliers are applied if the hit is a crit.*

**Step 5: Defense Mitigation**
*   **Purpose:** To calculate the damage after Armor and Pierce are applied.
*   **Formula:** `Mitigated Damage = MAX((Pre-Mitigation Damage - Defences), (Pre-Mitigation Damage * Pierce Ratio))`

**Step 6: Post-Mitigation Modifiers**
*   **Purpose:** To apply final damage multipliers.
*   **Logic:** This is where Tier 3 "True" Critical Hit multipliers and other global damage modifiers (like "Glass Cannon") are applied to the `Mitigated Damage`.

**Step 7: Block Check (Revised Position)**
*   **Purpose:** To apply a final, flat damage reduction if the Defender successfully blocks.
*   **Logic:** A roll is made against the Defender's `Block Chance`.
    *   **On Success:** The attack is **Blocked**.
    *   **Damage Reduction:** `Damage after Block = Final Damage - Defender's Block Amount`. The damage cannot be reduced below a minimum value (e.g., 1).
    *   **Event:** Dispatch an **`OnBlock`** event containing the amount of damage blocked.

**Step 8: Glancing Blow Penalty**
*   **Purpose:** To apply the damage penalty for hits flagged as a Glancing Blow.
*   **Logic:** If the "Is Glancing" flag is `True`, the final damage value is multiplied by a set modifier.
    *   **Formula:** `Final Damage Dealt = Damage after Block * 0.5` (50% Less Damage).

**Step 9: Final Damage & Event Dispatch**
*   **Purpose:** To deal the final calculated damage and notify the system.
*   **Logic:** The final damage is applied to the defender's health. An **`OnHit`** event (and **`OnCrit`** if applicable) is dispatched with the final damage value and context.

---

## 2.0 Foundational Systems in Detail

### 2.1 Evasion System (Glancing Blows & Dodge)

*   **Core Concept:** This system replaces the traditional "miss chance" with a more forgiving two-step process that provides better player feedback. Instead of attacks simply missing, they are often downgraded to weaker "Glancing Blows."
*   **New Stats:**
    *   `Evasion` (%): The total chance to "evade" an attack. This is the sum of a character's Dodge Chance and their Glance Chance. We propose a hard cap of 75%.
    *   `Dodge Chance` (%): The chance that an evaded attack results in a full Dodge (no damage). The chance for a Glancing Blow is `(Evasion - Dodge Chance)`.
*   **Detailed Mechanics:**
    1.  A single roll determines if the attack is evaded at all.
    2.  If evaded, a second roll determines if it's a full Dodge or a Glancing Blow.
    3.  Glancing Blows deal 50% less final damage and can never be critical hits.
    4.  **Entropy Safeguard:** To prevent streaks of bad luck, an "entropy" system can be implemented. After a player's attack is fully Dodged, the target gains a temporary debuff that reduces their Evasion, making the player's next attack more likely to hit. This debuff is removed on the next successful hit (Normal or Glancing).
*   **Event Hooks:** `OnDodge`, `OnGlancingBlow`.

### 2.2 Bonus and Penalty System

*   **Core Concept:** A simplified meta-system for temporary luck modifiers, granting flat percentage bonuses/penalties to random rolls for strategic skill timing.
*   **Mechanics:**
    *   **Advantage:** +x% bonus to the targeted roll chance (e.g., x @ 25% = 30% crit chance becomes 55%).
    *   **Disadvantage:** -y% penalty to the targeted roll chance (e.g., y @ 20% = 50% miss chance becomes 30%), minimum 0%.
    *   **Stacking:** To keep the system clear, all Bonuses and Penalties from different sources for the same roll are simply summed up.
    *   **Duration:** Short-lived effects (3-5 seconds) typically granted by special skills or ultimate abilities.
    *   **Clamping:** As a "Bonus" can push a chance above 100% and a "Penalty" can push it below 0%. You will need to clamp the final chance between 0% and 100% right before the roll is made.
*   **Applicable Rolls:**
    *   Evasion Rolls
    *   Dodge Rolls
    *   Critical Hit Rolls
    *   Block Chance Rolls
    *   Proc Rate Rolls (for secondary effects)
    *   Loot Quality Rolls (during item generation) - though less common for temporary effects but could you as a "booster" for rewards screen at end of level?
*   **Implementation:** A central `perform_roll()` function should be created to handle this logic, replacing all direct calls to a random number generator for these mechanics.

### 2.3 Resource & Cooldown System

*   **Core Concept:** Formalizes the system for governing skill usage, creating opportunities for resource management and cooldown-based builds.
*   **New Stats & Properties:**
    *   **Stats (Static):**
        *   `max_resource`: The maximum amount of the character's primary resource.
        *   `resource_regen_rate`: Resource regenerated per second.
        *   `cooldown_reduction` (%): Reduces the base cooldown of skills.
    *   **State (Dynamic):**
        *   `current_resource`: The character's current resource amount.
        *   `[skill]_cooldown_remaining`: Timers for each skill on cooldown.
*   **Detailed Mechanics:**
    1.  **Resource:** Special Skills have a `resource_cost`. The `process_skill_use` function will check if the character has enough `current_resource` and subtract the cost upon use. Resources will regenerate over time in the `StateManager.update()` loop.
    2.  **Cooldowns:** Special and Ultimate Skills have a `base_cooldown`. When used, a timer is set to `base_cooldown * (1 - cooldown_reduction)`. This timer is reduced every frame in the `StateManager.update()` loop. A skill cannot be used if its cooldown is greater than 0.
*   **Event Hooks:** `OnResourceGained`, `OnResourceSpent`, `OnSkillUsed`.

---

## 3.0 Foundational Affix List (Low & Medium Tiers)

This list provides a solid base of simple, effective affixes built upon the core GDD and the systems above.

| Affix Name | Tier (Low/Med) | Type | Effect & Design Rationale |
| :--- | :--- | :--- | :--- |
| **Might** | Low / Medium | Offensive | **Effect:** `+X Flat Base Damage`.<br>**Rationale:** The most basic and clear offensive upgrade. Available on many item slots (Weapons, Arms). |
| **Alacrity** | Low / Medium | Offensive | **Effect:** `+X% Attack Speed`.<br>**Rationale:** A core offensive stat. Primarily found on Hand and Weapon slots. |
| **Precision** | Medium | Offensive | **Effect:** `+X% Critical Hit Chance`.<br>**Rationale:** A staple for critical hit builds. Found on Hands, Weapons, and Jewelry. |
| **Ferocity** | Medium | Offensive | **Effect:** `+X% Critical Hit Damage`.<br>**Rationale:** The key multiplier for crit builds. Primarily found on Jewelry and specialized weapon types (e.g., Axes). |
| **Certainty** | Medium | Offensive | **Effect:** `+X Accuracy Rating`. (Note: This could be renamed `+X% Chance to Prevent Glancing/Dodge`).<br>**Rationale:** The counter to Evasion, making hits more reliable against agile enemies. |
| **Vitality** | Low / Medium | Defensive | **Effect:** `+X Max Health`.<br>**Rationale:** The primary survivability stat. Found on Chest, Pants, and Belts. |
| **Fortitude** | Low / Medium | Defensive | **Effect:** `+X Armor`.<br>**Rationale:** Core physical damage mitigation. Found on Chest, Head, and Pants. |
| **Aegis** | Low / Medium | Defensive | **Effect:** `+X% Block Chance`.<br>**Rationale:** A key stat for the post-mitigation Block system. Enables builds that want to trigger `OnBlock` effects. |
| **Barrier** | Medium | Defensive | **Effect:** `+X Block Amount`.<br>**Rationale:** Directly increases the damage reduction of a successful block, making it a powerful defensive layer. |
| **Agility** | Medium | Defensive | **Effect:** `+X% Evasion Chance`.<br>**Rationale:** Core stat for avoidance-based characters, feeding into both the Glance and Dodge mechanics. |
| **Readiness** | Medium | Utility | **Effect:** `+X% Cooldown Reduction`.<br>**Rationale:** A fundamental stat for skill-focused builds. Found on Head, Shoulders, and Staffs. |
| **Flow** | Medium | Utility | **Effect:** `+X% Resource Regeneration`.<br>**Rationale:** Supports builds that frequently use resource-intensive Special Skills. Found on Belts and Jewelry. |
| **Barbed Plating** | Medium | Reactive | **Effect:** `On-Block`: `Reflect 50% of the blocked damage back to the attacker.`<br>**Rationale:** A simple but effective way to turn defense into offense, using the new `OnBlock` event. |
| **Reactive Step** | Medium | Reactive | **Effect:** `On-Dodge`: `Gain +10% Movement Speed for 2 seconds.`<br>**Rationale:** Provides a tangible reward for successful dodges, encouraging mobile playstyles. |
| **Focused Rage** | Medium | Conditional | **Effect:** `Your next attack has Advantage on its Critical Hit roll after you use a Special Skill.`<br>**Rationale:** A simple and powerful introduction to the Advantage system, creating a clear gameplay rhythm (Special -> Attack). |
| **Blinding Rebuke** | Medium | Conditional | **Effect:** `Enemies that you Block have Disadvantage on their next Hit roll.`<br>**Rationale:** Introduces the Disadvantage mechanic as a form of "soft" crowd control, rewarding defensive play with an offensive debuff. |
