# 📅 Feature Plan: Phase 3 - Crafting & Progression

**Status:** Draft
**Target Version:** v2.9.0
**Owner:** System Architect

## 1. Executive Summary
This phase introduces the **Economic Loop**. Players can now Salvage unwanted items into resources (Gold/Dust) and use those resources to Upgrade their equipment or Level Up. This implements the "Natural vs. Upgraded" math design we discussed earlier, ensuring that while low-rarity items can be improved, high-rarity drops remain superior.

## 2. Goals & Success Criteria
*   **Goal 1:** **Economy.** Implement a persistent currency system (Gold, Magic Dust).
*   **Goal 2:** **Recycling.** Allow players to destroy items for value ("Salvage").
*   **Goal 3:** **Crafting.** Implement the Rarity Upgrade logic (+20% stat boost per tier).
*   **Goal 4:** **Progression.** Implement XP gain on kills and Stat Scaling on Level Up.
*   **Metric:** A player can turn a "Common Sword" into a "Rare Sword" (Upgraded) and compare it against a "Natural Rare Sword" (Dropped), verifying the math holds.

## 3. Scope Boundaries
### ✅ In Scope
*   **Currency:** Tracking Gold and Dust in `GameSession`.
*   **Salvage Logic:** Converting `Item` -> `Currency` based on Rarity.
*   **Upgrade Logic:** Converting `Item` -> `Item` (Stat Multiplier) + Cost check.
*   **XP System:** `Entity` tracks XP. `LevelUp` event scales `EntityStats`.
*   **UI:** A new "The Forge" tab in the Campaign dashboard.

### ⛔ Out of Scope
*   **Item Creation:** We are not "crafting from scratch" (Blacksmithing). Only upgrading existing items.
*   **Skill Trees:** Leveling up increases *Stats*, not unlocking new abilities yet.
*   **Merchants:** No buying items, only upgrading what you have.

## 4. Implementation Strategy (Phasing)

### 🔹 Phase 3.1: The Economy Layer
*   **Focus:** State & Resources.
*   **Task:**
    *   Update `GameSession` to track Gold/Dust/XP.
    *   Update `Entity` model to track Level and XP.
    *   Define `salvage_values` and `upgrade_costs` in a new config (or constants).
*   **Output:** `WORK_ITEM-3.1`

### 🔹 Phase 3.2: The Forge (Logic)
*   **Focus:** The Math.
*   **Task:**
    *   Implement `CraftingManager`.
    *   **Salvage:** Remove item, add currency.
    *   **Upgrade:** Calculate cost. If affordable: Update `Item.rarity`, apply **Upgrade Multiplier** to existing affixes.
        *   *Recall Rule:* Upgraded items get +20% stats per tier but do *not* gain new random affixes.
*   **Output:** `WORK_ITEM-3.2`

### 🔹 Phase 3.3: Leveling & Scaling
*   **Focus:** Entity Growth.
*   **Task:**
    *   Handle `EntityDeathEvent` to award XP to the killer.
    *   Implement `check_level_up()`: If XP > Threshold, increment Level.
    *   Implement `scale_stats()`: Apply the `scaling.yaml` curve to the Entity's base stats.
*   **Output:** `WORK_ITEM-3.3`

### 🔹 Phase 3.4: UI Integration
*   **Focus:** The Dashboard.
*   **Task:**
    *   Add "The Forge" tab to Campaign.
    *   Show XP bar / Level in Preparation screen.
*   **Output:** `WORK_ITEM-3.4`

## 5. Risk Assessment
*   **Risk:** **Inflation.**
    *   *Impact:* Player gets too strong too fast via upgrading.
    *   *Mitigation:* Tune `upgrade_costs` to be exponential.
*   **Risk:** **Data Drift.**
    *   *Impact:* Upgraded items might look like "Natural" items in the UI, confusing the player.
    *   *Mitigation:* Track `base_rarity` vs `current_rarity` on the `Item` model (as designed previously) and visualize "Upgraded" status in the UI (e.g., "Iron Sword +2").
