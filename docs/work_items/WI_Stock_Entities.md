# 📋 Work Item: Archetype Entities - Enemy Types & Encounters

**Phase:** Content Creation - Phase 3 of 4
**Component:** Entity System / Combat Balance
**Context:** Follows WI_Stock_Items. Creates thematic enemy archetypes that challenge player types, using the new equipment/affixes from previous phases.

## 🎯 Objective
Define enemy entity templates and encounter structures that provide thematic opposition to player archetypes. Enable meaningful Auto-Battler campaign progression with datatype-appropriate loot drops.

## 🏗️ Technical Implementation

### 1. Schema Changes
*   **File:** `data/entities.csv`
*   **New Entities:**
    *   **Anti-Spellcaster:** Magic-absorbing golems, mana-draining casters, spell-reflection knights
    *   **Anti-Warrior:** Evading swarm mobs, heavy siege constructs, armor-piercing assassins
    *   **Anti-Rogue:** Slow but durable tanks, area-effect spellcasters, projectile turrets
*   **Loot Tables:** `data/loot_tables.csv` entries linking to archetype-appropriate drops

### 2. Data Model Changes
*   **File:** `data/loot_tables.csv`
*   **New Tables:** 9 tables (3 archetypes × 3 enemy types) with weighted loot distribution
*   **Entity Linking:** Equipment pools reference generated item families from WI_Stock_Items

### 3. Core Logic & Architecture
*   **Enemy Design Philosophy:**
    *   Thematic opposition: Counter-play mirrors player strengths as weaknesses
    *   Equipment integration: Enemies use same families/items as players (via different pools)
    *   Loot progression: Earlier enemies drop vanilla items, later enemies drop quality-scaling
*   **EntityFactory Integration:** Must work with existing EquipmentFactory pools and RNG
*   **Encounter Balancing:** Stats/scaling designed for Auto-Battler multi-round encounters

## 🛡️ Architectural Constraints (Critical)
*   [ ] **Data Integrity:** All entity references resolve to existing item/affix IDs
*   [ ] **EntityFactory Compatible:** Equipment pools work with existing factory logic
*   [ ] **Performance:** Entity loading/scaling doesn't impact hot-path combat performance
*   [ ] **Determinism:** Enemy equipment must be RNG-deterministic for replayability

## ✅ Definition of Done (Verification)
*   [ ] **Entity Coverage:** 9 enemy templates (3 archetypes × 3 enemy types per counter)
*   [ ] **Loot System:** 9 loot tables linked to enemy deaths with quality-appropriate drops
*   [ ] **Factory Integration:** Can spawn enemies via `factory.create("enemy_spellcaster_golem")`
*   [ ] **Combat Validation:** Enemies survive expected number of rounds in simulation testing
*   [ ] **Thematic Balance:** Each enemy type exploits 1-2 specific player archetype weaknesses
