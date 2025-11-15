# Code Review Implementation Plan

**Date:** 2025-11-14
**Target:** Address all code review recommendations except Godot port considerations
**Estimated Timeline:** 3-5 days (spread across 1-2 weeks for testing/debugging)

## Overview

This plan addresses the 6 prioritized recommendations from the code review report to transform the Combat Engine prototype from an excellent working system to an architecturally pure, highly extensible foundation. The implementation follows a phased approach that minimizes risk while maximizing architectural improvements.

**Key Design Decisions:**
- `SkillUseResult`: Future-proof structure with `hit_results` (List[HitContext]) and `actions` (List[Action]) - translates well to Godot signals
- Backward Compatibility: Replace `process_skill_use` immediately with `calculate_skill_use` after implementation
- `DamageOnHitConfig`: Includes damage_per_tick for complete DoT configuration

## Phase 1: Core Architecture Foundation (1 day)
**Goal:** Establish the new architectural contracts without disrupting existing functionality

### Step 1.1: Define Combat Engine Interfaces
- **Create**: `SkillUseResult` dataclass in `src/models.py`
  - `hit_results: List[HitContext]` - calculated hits from multi-hit skills
  - `actions: List[Action]` - executable actions (ApplyDamage, DispatchEvent, ApplyEffect)
- **Create**: `Action` base class and subclasses (`ApplyDamageAction`, `DispatchEventAction`, `ApplyEffectAction`) in `src/models.py`
- **Impact**: Zero breaking changes - pure additions
- **Testing**: New unit tests in `tests/test_models.py` for data structure validation

### Step 1.2: Combat Engine Refactor Preparation
- **Implement**: `calculate_skill_use` method returning `SkillUseResult`
- **Keep**: Old `process_skill_use` method for reference during transition
- **Modify**: Internal logic to collect `HitContext` and `Action` objects instead of direct execution
- **Impact**: `src/engine.py` - method changes internally but signature remains compatible initially
- **Testing**: New tests in `tests/test_engine.py` for `calculate_skill_use` with mocked dependencies

### Step 1.3: Create Orchestrator Controller
- **Create**: New `src/combat_orchestrator.py` module
- **Implement**: `execute_skill_use` function that takes `SkillUseResult` and executes actions via StateManager/EventBus
- **Update**: Existing skill execution code to use new orchestrator
- **Impact**: New file, updates to `run_phase3_test.py` and `run_simulation.py`
- **Testing**: Integration tests validating end-to-end execution matches previous behavior & dedicated unit tests for orchestrator

## Phase 2: Effect System Generalization (1-2 days)
**Goal:** Transform hardcoded effect handlers into data-driven system

### Step 2.1: Generic Handler Framework
- **Create**: `DamageOnHitConfig` dataclass in `src/models.py`
  - `debuff_name: str`
  - `proc_rate: float`
  - `duration: float`
  - `damage_per_tick: float`
- **Create**: Generic `DamageOnHitHandler` class in `src/effect_handlers.py`
- **Impact**: `src/models.py`, `src/effect_handlers.py`
- **Testing**: Unit tests for the generic handler with various configs

### Step 2.2: Handler Migration
- **Replace**: `BleedHandler` and `PoisonHandler` with configured `DamageOnHitHandler` instances
- **Update**: Effect registration in test scripts to use new handler system
- **Create**: Configuration constants file or data structure for handler configs
- **Future Proofing**: Design architecture to enable effects.csv file loading from data pipeline
  - **Structure**: effects.csv could define (effect_name, debuff_name, proc_rate, duration, damage_per_tick, etc.)
  - **Integration**: Extend data_parser.py to load effects into game_data.json
  - **Handler Creation**: Generic handler factory could create handlers from data configurations
  - **Extensibility**: New effects (Burn, Life Drain, etc.) would require only CSV entries, zero code changes
- **Impact**: `src/effect_handlers.py`, `run_phase2_test.py`, `run_phase3_test.py`
- **Testing**: Integration tests ensuring Bleed and Poison effects work identically to before

## Phase 3: Data Integrity & Access Patterns (0.5 days)
**Goal:** Robust data validation and centralized access

### Step 3.1: Stat Name Validation
- **Modify**: `Entity.calculate_final_stats` in `src/models.py`
- **Add**: Validation check for `affix.stat_affected` against `EntityStats.__dict__` keys
- **Implement**: Warning/Error for invalid stat names
- **Impact**: `src/models.py`
- **Testing**: Unit tests with invalid CSV data scenarios

### Step 3.2: Game Data Provider
- **Create**: `src/game_data_provider.py` module
- **Implement**: Singleton provider for `game_data.json` content
- **Refactor**: `ItemGenerator` and other data consumers to use provider
- **Impact**: New file, updates to `src/item_generator.py`
- **Testing**: Tests for provider loading and data access patterns

## Phase 4: Complete Combat Engine Decoupling (1 day)
**Goal:** Finalize the architectural separation

### Step 4.1: Final Engine Refactor
- **Remove**: Old `process_skill_use` method (direct execution pattern)
- **Rename**: `calculate_skill_use` to `process_skill_use` (same API name but **fundamentally different usage pattern**)
- **Change**: Method now returns `SkillUseResult` instead of executing actions directly
- **Pattern**: Callers must now use `orchestrator.execute_skill_use(engine.process_skill_use(skill, attacker, target))`
- **Update**: All skill execution code to use new orchestrator pattern
- **Impact**: `src/engine.py`, all test and simulation scripts - requires fundamental caller pattern change
- **Testing**: Full integration test suite validating no behavioral changes despite caller pattern shift

### Step 4.2: Orchestrator Integration
- **Finalize**: Combat orchestrator as central execution point
- **Update**: Simulation framework to use orchestrator for consistency
- **Impact**: `src/combat.py`, `src/simulation.py`
- **Testing**: Simulation performance and correctness validation

## Phase 5: Test Coverage Completion (1-2 days)
**Goal:** Close all testing gaps identified in review

### Step 5.1: Missing Core Tests
- **Add**: Comprehensive `process_skill_use` tests (renamed `calculate_skill_use`)
  - Multi-hit scenarios (3-hit skill calls result in 3 HitContexts)
  - Trigger proc rates (correct Action generation on proc)
  - Event dispatching (OnHitEvent, OnCritEvent generation)
- **Impact**: `tests/test_engine.py`
- **Mock Strategy**: pytest mocking for StateManager and EventBus isolation

### Step 5.2: Boundary Condition Tests
- **Add**: Edge case tests for `resolve_hit`
  - `pierce_ratio = 1.0` (complete armor bypass)
  - `crit_damage = 1.0` (crit with no bonus)
  - `base_damage = 0` (zero damage scenarios)
- **Add**: Invalid input handling tests
- **Impact**: `tests/test_engine.py`

### Step 5.3: Integration Validation
- **Expand**: End-to-end tests for complex skill chains
- **Add**: Simulation consistency tests comparing old vs new architecture
- **Create**: Dedicated unit tests for `combat_orchestrator.py` module
  - Mock `SkillUseResult` with predefined `hit_results` and `actions`
  - Verify correct method calls on mocked `StateManager` (apply_damage) and `EventBus` (dispatch_event)
  - Test action execution order and parameter passing
- **Impact**: `tests/test_simulation.py`, `tests/test_fixtures.py`, new `tests/test_orchestrator.py`

## File Impact Summary

| File | Changes | Category |
|------|---------|----------|
| `src/models.py` | SkillUseResult, Action classes, DamageOnHitConfig, stat validation | Architecture |
| `src/engine.py` | calculate_skill_use -> process_skill_use refactoring | Architecture |
| `src/effect_handlers.py` | Generic DamageOnHitHandler, config-based instances | Extensibility |
| `src/combat_orchestrator.py` | New orchestrator for action execution | Architecture |
| `src/game_data_provider.py` | New provider for data access | Data Management |
| `src/item_generator.py` | Use data provider | Data Management |
| `tests/test_engine.py` | 8-12 new unit tests for gaps and boundaries | Testing |
| `tests/test_models.py` | New data structure validation | Testing |
| `tests/test_fixtures.py` | Expansion for orchestrator testing | Testing |
| `tests/test_orchestrator.py` | New unit tests for orchestrator module | Testing |
| Integration scripts | Update to use new orchestrator pattern | Integration |

## Testing Strategy

**Unit Testing Approach:**
- Maintain 100% pass rate at each phase
- Use pytest mocking for decoupling validation
- Add comprehensive boundary case coverage
- 8-12 new tests total focused on previously untested code paths

**Integration Testing:**
- End-to-end skill execution validation
- Simulation performance regression testing
- Data pipeline integrity checks

**Test Execution Plan:**
- Run full test suite after each phase
- Benchmark simulation performance to detect regressions
- Validate game balance metrics remain consistent

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|---------|------------|
| Regression in damage calculations | Low | High | Comprehensive unit tests + integration validation |
| Performance degradation | Medium | Medium | Benchmark testing at each phase |
| Effect system not working identically | Low | High | Extensive integration tests comparing old vs new |
| Data loading issues | Low | Medium | Provider testing + data validation |
| Godot compatibility issues | Low | High | Future-proof design using Godot patterns (signals/events) |

## Success Criteria

- ✅ All 96 existing tests pass (no regressions)
- ✅ 8-12 new tests added covering review gaps
- ✅ Combat Engine produces identical results through new architecture
- ✅ Effect system maintains exact same behavior with improved extensibility
- ✅ Simulation performance within 5% of baseline
- ✅ Zero runtime errors or warnings in all test scenarios

## Timeline Estimates

- **Phase 1:** 4-6 hours (Foundation work)
- **Phase 2:** 6-8 hours (Handler generalization)
- **Phase 3:** 2-4 hours (Data improvements)
- **Phase 4:** 4-6 hours (Final decoupling)
- **Phase 5:** 8-10 hours (Test completion)
- **Total:** 24-34 hours across 5 phases

**Recommended Pace:** 1-2 phases per day to allow thorough testing and validation.

## Architectural Benefits

- **Purity:** Calculation completely separated from execution
- **Testability:** Engine can be tested without external dependencies
- **Extensibility:** New effects and actions require zero code changes
- **Godot Ready:** Structure aligns with Godot's signal and node architecture
- **Maintainability:** Clear separation of concerns and reduced coupling

This plan transforms the excellent prototype into a production-ready system while maintaining complete behavioral compatibility.
