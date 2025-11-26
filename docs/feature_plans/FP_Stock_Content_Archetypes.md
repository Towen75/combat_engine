# 📅 Feature Plan: Stock Content - Archetype Sets

**Status:** Approved
**Target Version:** v2.14.0
**Owner:** Product Manager

## 1. Executive Summary
Create complete starter content sets for three core player archetypes (Spellcaster, Warrior, Rogue) using the data-driven combat system. This provides tangible, playable archetypes from the existing blueprint system, enabling full Auto-Battler gameplay with strategic equipment decisions.

## 2. Goals & Success Criteria
*   **Goal 1:** Comprehensive archetype coverage - Each archetype (Spellcaster/Warrior/Rogue) has complete equipment sets across all 3 weapon types and full armor slots.
*   **Goal 2:** Self-contained vanilla content - All necessary affixes, items, and enemy sets created from blueprints without external dependencies.
*   **Goal 3:** Demonstration-quality - Content enables compelling Auto-Battler play sessions with clear tactical differences between archetypes.
*   **Metric:** Tool can generate complete player character and enemy sets for any archetype via `EntityFactory` and `ItemGenerator`.

## 3. Scope Boundaries
### ✅ In Scope
*   **Spellcaster Set:** Staff + dagger weapons; magic-focused affixes; mage enemy types with ranged/offensive capabilities
*   **Warrior Set:** Sword + axe weapons; tank/dps affixes; melee bruiser enemy types with durability
*   **Rogue Set:** Dagger + bow weapons; mobility/crit affixes; stealthy/skirmishing enemy types
*   **Complete Item Coverage:** At least 1 item per equipment slot type (plus 2 weapons per archetype)
*   **Affix Expansion:** New vanilla affixes using blueprint system for each archetype's strengths
*   **Enemy Archetypes:** 2-3 enemy types per player archetype with appropriate tactics/loot
*   **Tool-Assisted Creation:** Automated generation using `content/scripts/build_content.py`

### ⛔ Out of Scope (De-risking)
*   **Advanced Mechanics:** No proc effects, complex triggers, or dual-stat affixes in vanilla sets
*   **Balance Tuning:** Content creation focused; balance pass as separate work
*   **Asset Generation:** CSV/data creation only; no art, sound, or visual components
*   **Multiplayer Features:** Single-player archetype isolation (no team synergies)
*   **Dynamic Scaling:** Fixed vanilla power levels (no level-based progression in content)

## 4. Implementation Strategy (Phasing)

### 🔹 Phase 1: Archetype Definition & Affix Foundation
*   **Focus:** Define core distinctions and create supporting vanilla affixes using `blueprints/affixes.yaml` as template
*   **Output:** `WORK_ITEM-Stock_Affixes`

### 🔹 Phase 2: Weapon & Armor Families
*   **Focus:** Extend `blueprints/families.yaml` and generate CSV items with archetype-appropriate families
*   **Output:** `WORK_ITEM-Stock_Items`

### 🔹 Phase 3: Enemy Archetype Creation
*   **Focus:** Create enemy entity templates and loot tables that thematically oppose player archetypes
*   **Output:** `WORK_ITEM-Stock_Entities`

### 🔹 Phase 4: Content Integration & Validation
*   **Focus:** Wire all content together through loot tables and ensure archetype sets load/combine correctly
*   **Output:** `WORK_ITEM-Stock_Integration`

## 5. Risk Assessment
*   **Risk:** **Blueprint Template Limitations** - Current blueprint format may have gaps for archetype-specific content
    *   *Mitigation:* Use Phase 1 to validate and extend blueprint schemas if needed
*   **Risk:** **Quality/Scope Creep** - Vanilla content demands for advanced mechanics could delay completion
    *   *Mitigation:* Strict scope boundary enforcement - advanced features as separate work items
*   **Risk:** **Archetype Balance Conflicts** - Content created for demonstration might create balance issues
    *   *Mitigation:* Content validation focuses on archetype clarity, not numerical balance (separate phase)
*   **Risk:** **Data Schema Drift** - CSV content changes might break existing tool integration
    *   *Mitigation:* Full data pipeline testing in Phase 4 before commit
