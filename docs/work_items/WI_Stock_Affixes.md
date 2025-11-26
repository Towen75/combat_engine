# 📋 Work Item: Archetype Archetypes - Vanilla Affixes

**Phase:** Content Creation - Phase 1 of 4
**Component:** Data Pipeline / Affix System
**Context:** FP_Stock_Content_Archetypes defines complete content sets. This creates the mechanical "verbs" that make archetypes distinct from `blueprints/affixes.yaml`.

## 🎯 Objective
Create archetype-defining vanilla affixes using blueprint system. Focus on simple, predictable bonuses that highlight each archetype's core strengths without complex mechanics.

## 🏗️ Technical Implementation

### 1. Schema Changes
*   **File:** `blueprints/affixes.yaml`
*   **New Affixes:**
    *   Spellcaster: `spell_power`, `mana_regen`, `magic_penetration`, `spell_crit_dmg`
    *   Warrior: `tank_armor`, `melee_damage`, `threat_generation`, `bleed_damage`
    *   Rogue: `movement_speed`, `crit_multiplier`, `stealth_value`, `poison_damage`

### 2. Data Model Changes
*   **File:** `src/data/schemas.py` (validate new affix schemas)
*   **New Pools:** Pool definitions for archetype-specific affix groups

### 3. Core Logic & Architecture
*   **Data Generation:** Extend `scripts/build_content.py` to generate CSV entries
*   **Affix Generation Logic:**
    *   Wizard: Magic/Spell-focused affixes (50% base damage, 2% crit chance, int-based stats)
    *   Fighter: Tactical affixes (armor/vitality, damage multipliers, dot mechanics)
    *   Ranger: Mobile affixes (speed/crit, attack speed modifiers)
*   **Blueprint Compatibility:** Must integrate with existing `ItemGenerator` and stat calculation

## 🛡️ Architectural Constraints (Critical)
*   [ ] **Determinism:** Affix values must be RNG-deterministic within quality tiers
*   [ ] **Blueprint Compliance:** Must use existing blueprint schema (no breaking changes)
*   [ ] **Performance:** No hot-path calculation in affixes (simple flat/multipliers only)
*   [ ] **Type Safety:** Full Pydantic validation of new affix definitions

## ✅ Definition of Done (Verification)
*   [ ] **Blueprint Valid:** `blueprints/affixes.yaml` contains 10+ new affix entries
*   [ ] **Schema Compliance:** pydantic models load affixes without errors
*   [ ] **Archtype Clarity:** Each archetype has 3-5 distinctive affixes
*   [ ] **CSV Generation:** `scripts/build_content.py` outputs affiliate CSV data
*   [ ] **ItemGenerator Integration:** Can generate items with new affixes
