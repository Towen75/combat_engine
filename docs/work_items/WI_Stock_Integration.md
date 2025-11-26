# 📋 Work Item: Content Integration & Validation

**Phase:** Content Creation - Phase 4 of 4
**Component:** Data Pipeline / Integration Testing
**Context:** Final phase of FP_Stock_Content_Archetypes. Validates that all archetype content works together: affixes + items + entities in cohesive, playable sets.

## 🎯 Objective
Wire all generated content together through proper data references and tool integration. Ensure archetypes can be instantiated end-to-end for Auto-Battler gameplay.

## 🏗️ Technical Implementation

### 1. Schema Changes
*   **File:** `scripts/build_content.py`
*   **New Commands:**
    *   `--generate-archetypes`: Creates complete archetype sets from blueprints
    *   `--validate-archetypes`: Checks all cross-references and data integrity
    *   `--test-archetype-play`: Simulation validation for archetype combat viability

### 2. Data Model Changes
*   **Integration Updates:**
    *   EntityFactory: Add archetype preset methods (e.g., `create_spellcaster_set()`)
    *   Inventory: Archetype-specific initialization patterns
    *   LootManager: Archetype loot table routing and quality mapping

### 3. Core Logic & Architecture
*   **Content Validation Pipeline:**
    *   Blueprint → CSV generation (affixes, items, entities, loot)
    *   Cross-reference validation (no dangling IDs, valid pools)
    *   Factory test spawning (EntityFactory can create all archetypes)
    *   Combat simulation (test fights between archetype combinations)
*   **Tool Extensions:**
    *   Dashboard archetypes page: UI for archetype selection/testing
    *   Streamlit integration: Archetype preset loading for campaigns

## 🛡️ Architectural Constraints (Critical)
*   [ ] **Data Integrity:** Zero dangling references between affixes/items/entities/loot
*   [ ] **Backward Compatibility:** New content doesn't break existing EntityFactory workflows
*   [ ] **Performance:** Content loading <5 seconds, archetype spawning <1 second
*   [ ] **Determinism:** Archetype generation is seeded and reproducible

## ✅ Definition of Done (Verification)
*   [ ] **Blueprint Pipeline:** `--generate-archetypes` creates complete CSV data sets
*   [ ] **Cross-Reference Valid:** `--validate-archetypes` passes with zero errors
*   [ ] **EntityFactory Ready:** Can spawn all archetype combinations with equipment
*   [ ] **Combat Viable:** Simulation testing shows archetypes can defeat opposing enemy sets
*   [ ] **Dashboard Integration:** Streamlit page demonstrates archetype-based gameplay
