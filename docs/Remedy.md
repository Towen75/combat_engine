# Combat Engine Code Review Remedy Plan

## Executive Summary

This document outlines a comprehensive plan to address all findings from the "Combat Engine - High-Level Review.md" code review. The plan prioritizes fixes based on the reviewer's recommendations, focusing first on critical correctness issues that could cause bugs, then on maintainability improvements, and finally on testing enhancements.

**Timeline Estimate:** 1-2 weeks for critical fixes, 2-3 weeks total including all recommendations.

---

## Critical Issues (Fix within days - High Priority)

### 1. RNG Handling Refactor

**Problem:** Global `random.seed(42)` inside `resolve_hit` reseeds the global RNG on every call, breaking independent random draws and hiding flaky tests.

**Solution:**
- Remove `random.seed(42)` from `src/engine.py`
- Add optional `rng: random.Random | None = None` parameter to `CombatEngine.__init__()` and `resolve_hit()`
- Use injected RNG when provided, fall back to `random.random()` without seeding
- Update all test files to inject deterministic RNG instances

**Implementation Steps:**
1. Modify `CombatEngine.__init__()` to accept `rng` parameter
2. Update `resolve_hit()` signature and implementation
3. Create `tests/conftest.py` with `make_rng(seed)` fixture
4. Update all existing tests to use injected RNG
5. Add new test: "RNG injection doesn't affect global random state"

**Files to Modify:**
- `src/engine.py` (CombatEngine class)
- `tests/test_engine.py` (all crit-related tests)
- `tests/conftest.py` (new file for test utilities)

### 2. Final Damage Assignment Fix

**Problem:** `ctx.final_damage` is not consistently set in all code paths, particularly missing assignment for non-crit and Tier 1/2 cases.

**Solution:**
- Ensure `ctx.final_damage = ctx.mitigated_damage` is set after mitigation calculation
- Only then apply post-pierce crit override if applicable
- Add explicit assignment in `resolve_hit()` return path

**Implementation Steps:**
1. Locate mitigation calculation in `resolve_hit()`
2. Add `ctx.final_damage = ctx.mitigated_damage` after mitigation
3. Ensure `_apply_post_pierce_crit()` only runs when Tier 3 is active
4. Verify `_apply_post_pierce_crit()` correctly overwrites `ctx.final_damage`

**Files to Modify:**
- `src/engine.py` (resolve_hit method)

### 3. Missing Unit Tests for Critical Paths

**Problem:** No tests specifically covering Tier 3 post-pierce crit path and final damage assignment.

**Solution:**
- Add unit tests that explicitly assert `ctx.final_damage` is set in all branches
- Add test for Tier 3 crit recalculation with expected damage values
- Add test for non-crit damage assignment

**Implementation Steps:**
1. Add `test_final_damage_always_assigned()` - tests all crit tiers set final_damage
2. Add `test_tier_3_post_pierce_crit_recalculation()` - verifies damage formula
3. Add `test_non_crit_damage_assignment()` - ensures mitigated_damage becomes final_damage

**Files to Modify:**
- `tests/test_engine.py` (new test methods)

---

## Important Issues (Fix within 1-2 weeks - Medium Priority)

### 4. Multi-Hit Skills Determinism Tests

**Problem:** Multi-hit skills lack tests for per-hit crit checks, proc rates, and aggregated state changes.

**Solution:**
- Add comprehensive tests for multi-hit skills with deterministic RNG
- Test per-hit events, crit outcomes, and state accumulation
- Ensure stacks and durations behave correctly across hits

**Implementation Steps:**
1. Create test for 3-hit skill with mixed crit outcomes (1 crit, 2 non-crit)
2. Verify per-hit OnHit events are dispatched
3. Test proc rates are independent per hit
4. Assert final state reflects aggregated changes

**Files to Modify:**
- `tests/test_engine.py` (new test methods)

### 5. DoT Tick Resolution & Time-Based Tests

**Problem:** No tests for time-based DoT ticks and damage accumulation over time.

**Solution:**
- Add tests that simulate time progression using `SimulationRunner`
- Test DoT damage accumulation and duration decrement
- Verify tick timing and damage application

**Implementation Steps:**
1. Add `test_dot_ticks_over_time()` - runs simulation for N seconds
2. Verify cumulative damage matches expected values
3. Test duration decrement and effect expiration
4. Test multiple DoTs stacking and ticking simultaneously

**Files to Modify:**
- `tests/test_simulation.py` (new test methods)

### 6. Bounds Checking & Input Validation

**Problem:** Missing upper bounds checks for `pierce_ratio` and other numeric inputs.

**Solution:**
- Add validation for `pierce_ratio` (0.01 ≤ pierce_ratio ≤ 1.0)
- Add bounds checks for damage values, armor values
- Document acceptable ranges in docstrings

**Implementation Steps:**
1. Update `validate_damage_calculation()` in `src/engine.py`
2. Add `assert 0.01 <= pierce_ratio <= 1.0` with descriptive error
3. Add bounds checks for attack_damage ≥ 0, armor ≥ 0
4. Update docstrings with valid ranges

**Files to Modify:**
- `src/engine.py` (validation functions)

### 7. Global RNG Replacement

**Problem:** Global RNG usage throughout codebase needs replacement with injected RNG.

**Solution:**
- Audit all `random.*` calls in codebase
- Replace with injected RNG where deterministic behavior is required
- Update effect handlers and simulation code

**Implementation Steps:**
1. Audit codebase for `random.seed()`, `random.random()`, `random.randint()`
2. Update `EffectHandler` classes to accept RNG parameter
3. Update `SimulationRunner` to use injected RNG
4. Ensure tests control randomness explicitly

**Files to Modify:**
- `src/effect_handlers.py`
- `src/simulation.py`
- `tests/*.py`

---

## Nice-to-Have Improvements (Future - Low Priority)

### 8. Property-Based Testing

**Problem:** Lack of property-based tests for damage formula invariants.

**Solution:**
- Add Hypothesis-based tests for damage calculation properties
- Test invariants like "final_damage ≥ 0" and pierce ratio guarantees

**Implementation Steps:**
1. Add `hypothesis` to `requirements.txt`
2. Create `tests/test_properties.py`
3. Add property tests for damage formula invariants

**Files to Modify:**
- `requirements.txt`
- `tests/test_properties.py` (new file)

### 9. Test Fixtures for Reduced Duplication

**Problem:** Test code has duplication in entity/attacker creation and RNG setup.

**Solution:**
- Create `tests/fixtures.py` with helper functions
- Implement `make_entity()`, `make_attacker()`, `make_rng(seed)` helpers
- Refactor existing tests to use fixtures

**Implementation Steps:**
1. Create `tests/fixtures.py` with fixture functions
2. Implement `make_rng(seed)` for deterministic RNG
3. Add `make_entity()` and `make_attacker()` for common test entities
4. Update existing tests to use fixtures
5. Ensure all tests pass with new fixtures

**Files to Modify:**
- `tests/fixtures.py` (new file)
- `tests/*.py` (refactor to use fixtures)

### 10. Documentation Updates

**Problem:** Missing reproducibility instructions and RNG conventions.

**Solution:**
- Add README section on deterministic testing
- Document RNG injection patterns and policy
- Update memory bank with fixes

**Implementation Steps:**
1. Update `README.md` with testing conventions
2. Add RNG policy note: "All combat RNG must be deterministic in tests and injectable in production. No global seeding permitted."
3. Add RNG documentation to docstrings
4. Update `docs/memory-bank/activeContext.md` with fixes

**Files to Modify:**
- `README.md`
- `docs/memory-bank/activeContext.md`
- `docs/memory-bank/log_change.md`

---

## Implementation Order & Dependencies

### Phase 1: Critical Fixes (Days 1-3)
1. Test fixtures for reduced duplication (needed for RNG injection)
2. RNG injection refactor (blocks all other RNG-related work)
3. Final damage assignment fix
4. Critical path unit tests

### Phase 2: Important Fixes (Days 4-10)
4. Multi-hit skills tests
5. DoT tick tests
6. Bounds checking
7. Global RNG replacement

### Phase 3: Quality Improvements (Future)
8. Property-based testing
9. Documentation updates

## Risk Assessment

### Technical Risks
- **RNG Injection Complexity:** May require significant test refactoring
- **Backward Compatibility:** Existing code may break with RNG changes
- **Performance Impact:** RNG injection could add overhead (mitigate with optional parameter)

### Mitigation Strategies
- **Incremental Changes:** Implement RNG injection gradually, maintaining backward compatibility
- **Comprehensive Testing:** All changes require full test suite pass
- **Revert Plan:** Keep git branches for easy rollback if issues arise

## Success Criteria

### Phase 1 Success
- [ ] All existing tests pass with RNG injection
- [ ] `ctx.final_damage` is set in all code paths
- [ ] New unit tests cover critical paths
- [ ] No global RNG seeding remains

### Phase 2 Success
- [ ] Multi-hit skills fully tested with deterministic RNG
- [ ] DoT ticks tested with time progression
- [ ] Input validation prevents invalid values
- [ ] All RNG usage is injected or explicitly global

### Final Success
- [ ] All review findings addressed
- [ ] Test coverage > 95% for critical systems
- [ ] Code quality tools integrated
- [ ] Documentation updated with new patterns

## Testing Strategy

### Unit Testing
- Maintain 100% pass rate for existing tests
- Add new tests for each fix before implementation
- Use deterministic RNG in all tests

### Integration Testing
- Run full Phase 1-4 integration tests after each phase
- Verify simulation performance remains > 6000 events/second
- Test edge cases with bounds checking

### Regression Testing
- Full test suite run before any changes
- Automated testing on CI (when available)
- Manual verification of critical combat scenarios

---

## Approval Checklist

Before implementing, please review and approve:

- [ ] Phase 1 critical fixes approach
- [ ] RNG injection strategy and backward compatibility
- [ ] Test coverage plan for new scenarios
- [ ] Timeline and resource requirements
- [ ] Risk mitigation strategies

**Approved by:** ____________________
**Date:** ____________________
**Comments:** ____________________
