# 📋 Work Item: Archetype Items - Weapon & Armor Families

**Phase:** Content Creation - Phase 2 of 4
**Component:** Data Pipeline / Item System
**Context:** Follows WI_Stock_Affixes. Creates the "nouns" that represent each archetype's playstyles using extended `blueprints/families.yaml`.

## 🎯 Objective
Define complete item families using archetype-appropriate implicits and affix pools. Generate CSV content where each archetype has distinctive equipment across all slots plus 2 weapon styles.

## 🏗️ Technical Implementation

### 1. Schema Changes
*   **File:** `blueprints/families.yaml`
*   **New Families:**
    *   **Spellcaster:** Magic Staff (int/magic damage), Spell Dagger (low dmg/high proc), Mage Cloak (magic resist/movement)
    *   **Warrior:** Battle Sword (str/stam bonuses), Warfare Axe (armor pen/bleed), Plate Armor (high defense/slow)
    *   **Rogue:** Precision Dagger (crit dmg/speed), Hunter Bow (rng damage/mobility), Leather Armor (evasion/speed)

### 2. Data Model Changes
*   **File:** `data/items.csv` (generated output)
*   **New Items:** ~40 base items (3 archetypes × ~3-4 items per slot × 5 rarities)
*   **Rarity Scaling:** Common→Mythic progression with increasing affix counts and values

### 3. Core Logic & Architecture
*   **Generation Tool:** Extend `scripts/build_content.py`:
    *   Input: `blueprints/families.yaml` + `blueprints/affixes.yaml`
    *   Process: Family template → Rarity expansion → Stat calculation → CSV output
    *   Output: Append to `data/items.csv` without overwriting existing content
*   **Architectural Requirements:**
    *   Archetype consistency: Each family has 1 implicit affix defining the archetype
    *   Slot coverage: Full armor sets + 2 weapons per archetype
    *   Affix progression: Quality tiers scale values predictably

## 🛡️ Architectural Constraints (Critical)
*   [ ] **Blueprint Compliance:** Must extend existing schema (families.yaml structure preserved)
*   [ ] **CSV Integrity:** Generation must be additive, never destructive to existing items.csv
*   [ ] **Performance:** Generation script completes in <30 seconds for full archetype sets
*   [ ] **Type Safety:** Generated CSV validates against existing ItemTemplate schema

## ✅ Definition of Done (Verification)
*   [ ] **Blueprint Complete:** `blueprints/families.yaml` contains 15+ family definitions
*   [ ] **Item Coverage:** Each archetype has 9+ item base IDs across weapons/armor slots
*   [ ] **Rarity Spectrum:** Every family has entries across Common→Mythic (minimum 3 tiers)
*   [ ] **Generation Valid:** `scripts/build_content.py --generate-items` creates valid CSV
*   [ ] **EntityFactory Ready:** Has required item IDs for all archetype equipment combinations
