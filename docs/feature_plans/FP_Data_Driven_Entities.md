# 📅 Feature Plan: Phase B - Data-Driven Entities

**Status:** Planned (APPROVED - Implementation Pending)
**Target Version:** v2.13.0
**Owner:** System Architect (Phase B lead: Data-Driven Entity Integration)
**Last Updated:** 2025-11-25
**Implementation Status:** ✅ EntityFactory skeleton exists (placeholder), ❌ Full data pipeline missing

## 1. Current Implementation Status

### ✅ Already Implemented
- **EntityFactory Class**: Placeholder exists (`src/core/factory.py`) with basic structure
- **Loot Table Integration**: Entities can specify `loot_table_id` field
- **Base Entity Model**: Supports procedural equipment generation

### ❌ Still Missing (Phase B Scope)
- `entities.csv` data file with entity templates
- `EntityTemplate` dataclass for data loading
- Equipment pool resolution logic
- Data pipeline integration in `GameDataProvider`
- Full EntityFactory implementation beyond placeholder

## 2. Executive Summary
We are shifting entity definition from hardcoded Python fixtures to a data-driven pipeline. This allows designers to define NPCs, monsters, and interactables via `data/entities.csv`. The system will parse these definitions into templates and use a Factory pattern to spawn runtime instances with procedurally generated equipment based on defined pools.

## 3. Goals & Success Criteria
*   **Goal 1 (CRITICAL):** Enable entity definition via `entities.csv` without code changes.
*   **Goal 2 (FUNCTIONAL):** Implement full `EntityFactory` to hydrate templates into runtime `Entity` objects.
*   **Goal 3 (ENHANCEMENT):** Integrate `ItemGenerator` to automatically equip entities based on `equipment_pools`.
*   **Goal 4 (QUALITY):** Maintain RNG determinism for simulation reproducibility.
*   **Success Metric:** A simulation can spawn a "Goblin Grunt" defined in CSV, and it appears with valid stats and a random weapon from the specified pool.

## 4. Prerequisites & Dependencies

### Prerequisites (Must be Complete Before Phase B)
- ✅ **Phase 1S3**: Data pipeline with cross-reference validation
- ✅ **Phase 5**: ItemGenerator for procedural equipment
- ✅ **Phase 2S5**: RNG injection architecture
- ✅ **Phase C**: Loot table system (for `loot_table_id` integration)

### New Dependencies (Created in Phase B)
- `EntityTemplate` dataclass in `src/data/typed_models.py`
- `entities.csv` schema in `src/data/schemas.py`
- `GameDataProvider` entity loading methods
- `EntityFactory` template resolution logic

## 3. Scope Boundaries

### ✅ In Scope
*   **Data Layer:** `entities.csv` schema, validation, and `EntityTemplate` model.
*   **Integration:** Updating `GameDataProvider` to load and cross-reference entities.
*   **Factory Logic:** `EntityFactory` class to hydrate templates into `Entity` runtime objects.
*   **Equipment:** Resolving `equipment_pools` (e.g., "melee_basic") into specific Items via `ItemGenerator`.

### ⛔ Out of Scope (De-risking)
*   **AI Behavior:** We define the `archetype` string, but implementing the actual AI logic is a future task.
*   **Complex Skill Trees:** Entities will spawn with base stats and equipment. Skill assignment logic is future work.
*   **Loot Tables:** While we add the `loot_table_id` field, the actual dropping logic handles in Phase C.

## 4. Implementation Strategy (Phasing)

### 🔹 Phase B1: Data Structure & Schemas (Priority: HIGH)
*   **Focus:** The "Blueprint" - Data model definition and validation
*   **Key Tasks:**
  - Define `entities.csv` schema (see section 7 for detailed format)
  - Implement `EntityTemplate` dataclass in `src/data/typed_models.py`
  - Add schema validation in `src/data/schemas.py`
  - Update `GameDataProvider` to load and validate entities
  - Add cross-reference validation (equipment pools, loot tables)
*   **Output:** `WORK_ITEM-B1`

### 🔹 Phase B2: The Entity Factory (Priority: HIGH)
*   **Focus:** The "Builder" - Runtime instantiation and equipment
*   **Key Tasks:**
  - Complete `EntityFactory` implementation beyond current placeholder
  - Add template resolution logic from `GameDataProvider`
  - Integrate `ItemGenerator` for equipment pool resolution
  - Add RNG injection for deterministic equipment generation
  - Implement instance ID generation with unique identifiers
*   **Output:** `WORK_ITEM-B2`

## 6. Detailed Data Schema (entities.csv)

### Core Entity Definition
```csv
entity_id,name,archetype,loot_table_id,base_health,base_damage,base_armor,base_crit_chance,description
goblin_grunt,"Goblin Grunt",melee_mook,goblin_drops,45,8,2,0.05,"Basic goblin minion with crude weapons"
skeleton_warrior,"Skeleton Warrior",melee_elite,skeleton_drops,70,12,5,0.08,"Reanimated warrior with rusty sword"
```

### Equipment Pool Definition
```csv
starting_weapon,starting_armor,starting_offhand,weapon_quality_range,armor_quality_range
melee_basic,light_armor,consumable_or_none,1-3,1-2
melee_advanced,medium_armor,shield_or_onehand,2-4,2-3
mage_robe,cloth_armor,staff_magic,1-5,1-2
```

### Equipment Pool References
- `melee_basic` → Items tagged as "melee" from `items.csv`
- `goblin_drops` → Loot table defined in `loot_tables.csv` (Phase C)
- Quality ranges specify min-max tier for equipment generation

## 7. Testing Strategy

### Unit Tests (Phase B1 Completion)
- ✅ `EntityTemplate` data model validation
- ✅ Schema validation for `entities.csv`
- ✅ Cross-reference validation of equipment pools and loot tables

### Integration Tests (Phase B2 Completion)
- ✅ Factory creates entities from CSV templates
- ✅ Equipment pools resolve to valid items via `ItemGenerator`
- ✅ RNG seeding produces deterministic equipment generation

### End-to-End Testing
- ✅ Simulation can spawn "Goblin Grunt" from CSV definition
- ✅ Spawned entity has expected stats and equipment
- ✅ Equipment generates within specified quality ranges

## 8. Performance Requirements

### Load Time Impact
- **Data Loading**: <100ms for entities.csv (expected 50-200 entity templates)
- **Validation Time**: <50ms for cross-reference checks
- **Memory Usage**: <5MB for loaded entity templates

### Runtime Performance
- **Factory Creation**: <10ms per entity instantiation
- **Equipment Generation**: <5ms for equipment pool resolution
- **Simulation Impact**: No performance regression in existing spawn patterns

## 9. Acceptance Criteria & Definition of Done

### Functional Requirements
- ✅ **Data-Driven Creation**: Can define new entity types via CSV without code changes
- ✅ **Factory Integration**: `EntityFactory.create(template_id)` produces valid Entity
- ✅ **Equipment Generation**: Equipment pools resolve to appropriate items via ItemGenerator
- ✅ **Stat Consistency**: Generated entities have valid, balanced stat combinations

### Quality Requirements
- ✅ **RNG Determinism**: Same RNG seed produces identical entity equipment
- ✅ **Data Integrity**: All cross-references validated at load time
- ✅ **Performance**: Factory creation completes in <10ms per entity
- ✅ **Test Coverage**: 90%+ test coverage for all new components

### Documentation Requirements
- ✅ **API Documentation**: Factory methods and template formats documented
- ✅ **Data Schema**: CSV format fully specified with examples
- ✅ **Integration Guide**: How to extend entity types for new content

## 10. Rollback & Recovery Plan

### Rollback Triggers
- **Data Loading Failures**: Invalid CSV format or cross-reference errors
- **Performance Degradation**: Factory creation exceeds 50ms per entity
- **RNG Issues**: Equipment generation becomes non-deterministic

### Rollback Steps
1. **Immediate**: Disable EntityFactory template resolution (fallback to manual creation)
2. **Data Layer**: Remove entities.csv loading from GameDataProvider
3. **Factory**: Revert EntityFactory to basic manual instantiation only
4. **Verification**: Ensure all existing entity creation still works

### Recovery Process
1. **Fix Issues**: Address root cause (data validation, performance, etc.)
2. **Test Isolation**: Verify fixes without affecting existing entity creation
3. **Gradual Rollout**: Re-enable template resolution with monitoring
4. **Verification**: Full regression testing before marking complete

## 11. Success Metrics & Monitoring

### Implementation Metrics
- **Code Coverage**: Target 95% for EntityFactory and related classes
- **Performance Baseline**: Establish <10ms factory creation benchmark
- **Memory Usage**: Track template loading memory footprint
- **Error Rate**: Monitor factory failure rate in production scenarios

### Usage Metrics (Post-Release)
- **Entity Variety**: Track number of unique entity types spawned from templates
- **Equipment Diversity**: Monitor spread of equipment quality tiers generated
- **Factory Throughput**: Measure entities created per second in simulations
- **Error Trends**: Track factory failures and their causes for continuous improvement

### Alert Conditions
- **Factory Failure Rate**: >1% of entity creation attempts fail
- **Performance Degradation**: Factory creation >25ms consistently
- **Invalid Templates**: >0 invalid entity templates in CSV data
- **RNG Variation**: Equipment generation shows non-deterministic patterns

## 12. Future Enhancements (Out of Scope)

### Phase B+ (Future Versions)
- **AI Integration**: Connect archetype strings to actual behavior systems
- **Skill Assignment**: Data-driven skill pools for entity abilities
- **Dynamic Leveling**: Template-based stat scaling for different difficulties
- **Visual Integration**: Godot scene references for 3D/2D entity representations

### Content Authoring Tools
- **Entity Editor**: Web-based interface for designing entity templates
- **Balance Validator**: Automated checking of entity stat balance
- **Simulation Preview**: Live preview of entities in test scenarios

## 5. Risk Assessment
*   **Risk:** **Invalid Equipment Pools**.
    *   *Impact:* Factory crashes if an entity requests items that don't exist.
    *   *Mitigation:* Strict Load-Time Validation in Phase B1 to ensure `equipment_pools` reference valid affix pools or items.
*   **Risk:** **RNG Determinism**.
    *   *Impact:* Spawning entities breaks simulation reproducibility.
    *   *Mitigation:* `EntityFactory` must accept an injected `RNG` instance.

***
