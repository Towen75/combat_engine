# Active Context: Combat Engine Development

## Current Work Focus

### Primary Active Task: UI Improvements Suite (COMPLETE)

**Status**: Fully Implemented and Verified
**Results**: Complete UI enhancement suite making weapon mechanics visible and accessible
- **UI-1: Collapsible Equipment Sections**: Equipment/backpack sections collapse to show key info, eliminating scrolling
- **UI-2: Combat Log Display**: Detailed combat logs show weapon skills, multi-hit damage, and effects in victory/defeat screens
- **Impact**: Weapon mechanics are now discoverable and testable through improved UX

### Next Phase Planning: UI-3 User Experience Polish

**Status**: Ready for Implementation
**Objective**: Elevate UI from functional to delightful with smooth transitions, weapon intelligence, and contextual guidance
**Dependencies**: UI-1 and UI-2 completed

### Future Phase: Crafting & Progression System

**Status**: Planned / Scheduled
**Objective**: Implement economic loop with item salvaging, upgrading, and XP progression
**Dependencies**: UI improvements operational

## Recent Changes

### Version 2.3.0 (2025-11-19)
- **PR-P2S4 Complete**: Entity Lifecycle Management implemented
  - Added `EntitySpawnEvent`, `EntityDeathEvent`, `EntityDespawnEvent` for proper lifecycle tracking
  - StateManager automatically triggers Death events on entity health depletion
  - EventBus cleanup prevents memory leaks from dead entity listeners
  - Comprehensive lifecycle test coverage with `test_lifecycle.py`
- **StateManager Refactoring**: Major architectural improvements for entity management
  - Enhanced state reset and initialization hooks
  - Memory leak prevention for dead entity references
  - Improved EventBus integration for lifecycle events
- **Event System Enhancement**: New lifecycle events enable complex game mechanics
  - OnSpawn/OnDeath/OnDespawn event chain for entity state transitions
  - Automatic event listener cleanup prevents zombie processes
  - Deterministic lifecycle behavior for testing and simulation

### Version 2.2.1 (2025-11-19)
- **Phase 1 Complete**: All foundational stability PRs (P1S1, P1S2, P1S3) are merged and verified.
- **Data Hardening**: Strict typing and cross-reference validation active.
- **Core Mechanics**: Dual-stats and RNG injection implemented.
- **Logging**: System-wide logging replaces print statements in core library.

### Version 2.2.0 (2025-11-17)
- **Completed GDD v4.0 Combat Engine**: Full system delivery exceeding original IP scope
- **Advanced Dual-Stat Affixes**: Single affixes affecting multiple stats simultaneously
- **Complex Reactive Effects**: Advanced trigger parsing for reflected damage, crit bonuses
- **Master Rule Data System**: CSV-driven content creation framework
- **Production Validation**: 10-second simulation with full combat verification

### Version 2.1.0 (2025-11-17)
- **Architectural Overhaul**: Action/Result pattern implementation
- **CombatOrchestrator**: Decoupled execution with dependency injection
- **Effect System Generalization**: Data-driven DoT effects (Burn, Freeze, Poison)
- **GameDataProvider Singleton**: Centralized JSON loading with validation

### Version 2.0.0 (2025-11-17)
- **Phase 5 Complete**: Procedural Item Generator system
- **CSV-to-JSON Pipeline**: Affixes, items, and quality tiers parsing
- **Sub-Quality Variation**: Items with unique characteristics within quality ceilings

## Next Steps Priority Queue

### Immediate Next: UI-3 User Experience Polish

**Priority**: HIGH - Completes weapon mechanics visibility suite
**Work Item**: `docs/work_items/WI_UI_3_User_Experience_Polish.md`
**Objective**: Transform UI from functional to delightful with smooth transitions and weapon intelligence
**Scope**: Intelligent quick-views, state transitions, weapon comparison analytics
**Timeline**: Ready for implementation

### Future Next: Crafting & Progression System

**Priority**: MEDIUM - Implements economic loop
**Feature Plan**: `docs/feature_plans/FP_Crafting_Progression.md`
**Objective**: Add item salvaging, upgrading, and XP progression
**Scope**: Currency system, crafting mechanics, entity leveling
**Dependencies**: UI improvements operational

### Long-term Goals (Phase 3: Finalization & Professionalization)

1. **PR-P3S6 Implementation**: Project restructuring and tooling integration
   - Repository restructuring with proper tooling (e.g., black/isort/mypy/pre-commit integration)
   - Automated code quality enforcement

2. **PR-P3S7 Implementation**: Final integration test for CI
   - Definitive end-to-end integration test for CI
   - Assert-based validation replacing print checks
   - Gold standard test serving as health check

3. **PR-P3S8 Implementation**: Godot Ecosystem Preparation
   - GDScript port planning and architecture translation
   - Documentation finalization (API references, guides)
   - Content creation tool preparation

## Active Decisions and Considerations

**Lifecycle Ownership**: `StateManager` will be the source of truth for an entity's lifecycle state.
**Event Cleanup**: Cleanup must be explicit (`OnDespawn`) rather than relying on Python's garbage collector, due to the EventBus circular references.

### RNG Policy Decision
**Decision**: Strict deterministic testing with injectable RNG instances only
**Rationale**: Balance validation requires perfectly reproducible simulations
**Implementation**: All random calls use injected `rng` parameter, defaulting to `random.random()` for production
**Trade-off**: Additional code complexity for dual test/production paths
**Critical Constraint**: NO global `random.seed()` usage anywhere in codebase

### Dual-Stat Affix Complexity
**Decision**: Support ";" separator in affix values for multiple stat modifications
**Implementation**: ItemGenerator rolls two separate values, Entity.calculate_final_stats applies both
**Rationale**: Richer itemization allowing synergies between related stats (damage + crit, armor + resistance)

### Effect System Architecture
**Decision**: Event-driven observer pattern over direct method calls
**Rationale**: Enables complex interactions (crit bonus triggering rage, blocking triggering rebuke)
**Current Challenge**: Finding balance between flexibility and debugging complexity

### Data Integration Strategy
**Decision**: Triple-layer validation (structure + cross-reference + type safety)
**Implementation**: schemas.py + cross-reference checks + mypy static analysis
**Value**: Catches typos, invalid references, and type mismatches before runtime

## Important Patterns and Preferences

### Combat Resolution Pattern
```
resolve_hit() → gather_stats() → calculate_damage() → apply_effects() → state_updates()
```
**Why**: Clear pipeline from raw stats to final result, easy debugging and testing

### RNG Usage Pattern
```python
def __init__(self, rng=None):
    self.rng = rng or random.random

def roll_critical_hit(self, chance):
    return self.rng() < chance
```
**Why**: Deterministic testing capability while maintaining production unpredictability

### Data Loading Pattern
```python
def load_game_data():
    raw = parse_csvs()
    validated = apply_schemas(raw)
    cross_referenced = validate_references(validated)
    typed = convert_to_models(cross_referenced)
    return typed
```
**Why**: Progressive validation catches different error types at appropriate stages

## Learnings and Project Insights

### Combat Formula Evolution
**Insight**: `MAX((Attack - Defense), (Attack × Pierce))` creates meaningful armor investment decisions
**Learning**: Simple subtraction leads to binary (tank vs glass cannon) roles; pierce allows hybrid builds
**Application**: Future game design should emphasize pierce ratios over flat values

### Event System Complexity
**Insight**: Decoupled events enable emergent gameplay but create debugging challenges
**Learning**: Event chains (crit → rage → attack bonus) create unexpected player strategies
**Mitigation**: Comprehensive logging in EventBus for production debugging

### Testing ROI
**Insight**: Deterministic RNG enables property-based testing approaches
**Learning**: Seeded scenarios catch state mutation bugs that random tests miss
**Benefit**: Regression prevention more valuable than new feature implementation

### Data Integrity Investment
**Insight**: Triple validation (schema + cross-reference + type) prevents entire bug categories
**Learning**: Most runtime crashes originate from data inconsistencies, not code bugs
**ROI**: Time invested in validation infrastructure saves exponential debugging time

### Architecture Evolution
**Insight**: Pure functions + orchestrator pattern cleanly separates computation from side effects
**Learning**: Action/Result pattern provides perfect testability and Godot translation path
**Benefit**: Architecture decisions directly support both technical needs and future development

## Risk Mitigation

### Technical Debt Risks
- **RNG Injection Complexity**: Monitor for developer mistakes bypassing injection
- **Event Chain Complexity**: Keep event handlers focused on single responsibilities
- **Type Annotation Overhead**: Progressive adoption to avoid developer resistance

### Schedule Risks
- **Phase Completion Dependencies**: PR-P1S2 must complete before P1S3 implementation
- **Testing Time Underestimation**: Validation of deterministic systems requires extensive testing
- **Godot Port Translation**: Ensure Python architecture patterns remain GDScript-compatible

### Quality Risks
- **Performance Regression**: Frequent benchmarking against 6993 events/sec target
- **API Consistency**: Regular review of public interfaces for breaking changes
- **Documentation Drift**: Memory bank updates required for all significant changes
