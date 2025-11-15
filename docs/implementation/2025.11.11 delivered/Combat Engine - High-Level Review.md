# Combat Engine - High-Level Review

---

## Executive summary

The prototype is in a very strong state: architecture is modular and well-documented; the phased approach (Phase 1–4) and memory-bank are excellent for long-term maintainability. The core damage model (pierce vs mitigation) and event-driven effect system are clear and appropriate for the target design. Unit tests are plentiful and the repository claims 92 passing tests across phases. Overall: **sound design, good coverage for implemented features, and clear roadmap for porting to Godot**.

However, there are several correctness and maintainability issues that should be addressed now before further development or a Godot port. The most critical items are deterministic/randomness handling in core functions, a few inconsistent implementations of crit application and final damage assignment, and several missing unit-test scenarios (multi-hit determinism, DoT tick resolution, edge numeric cases). I list actionable recommendations with priorities below.

---

## What I reviewed

I read the project bundle (design docs, changelog, phase notes, `src/` snippets and `tests/` content, and integration run outputs) to form this report.

Key sources in the bundle: the changelog and phase notes, design doc for damage and crits, `src/engine.py` and test fragments. (Full bundle provided by you).

---

## High-level design feedback

**Strengths**

* Clear separation of concerns: `models` (data), `state` (dynamic state), `engine` (calculation), `events`/`effect_handlers` (side effects). This eases testing and porting.
* EventBus / observer pattern is appropriate for flexible interactions between skills, items and effects.
* HitContext pipeline is a good design: it makes it easy to apply staged modifiers (pre-mitigation, post-mitigation, etc.).
* Documentation and phased changelog are excellent; they will pay dividends when onboarding contributors.

**Design risks / items to review further**

1. **Crit tier semantics vs implementation mismatch** — design documents describe Tier 1..4 with specific scopes. Implementation has `_apply_pre_pierce_crit` and `_apply_post_pierce_crit`, but `resolve_hit` calls `_apply_pre_pierce_crit` and computes mitigated damage and **never** calls `_apply_post_pierce_crit` before assigning `ctx.final_damage` (i.e., `ctx.final_damage` may remain unset in many paths). This is an observable correctness hole (see Code Issues below).
2. **Randomness handling** — seeding random inside `resolve_hit` (calls `random.seed(42)` on every resolution) makes calls deterministic but also brittle: every call reseeds the global RNG, which breaks independent random draws elsewhere and can hide flaky tests. Better to control randomness in tests by injecting a Random instance or using `random.Random(seed)` local RNG.
3. **Event / effect coupling** — while EventBus is flexible, ensure effect handlers don't mutate shared state unexpectedly; use explicit state-manager APIs and document reentrancy expectations.
4. **Scaling & performance** — simulation numbers (e.g., 6993 events/sec) are impressive for prototype; ensure profiling is done on representative hardware and that micro-optimisations don't reduce readability.

---

## Code quality, readability & maintainability (priority suggestions)

**Observations**

* Code uses dataclasses and type hints consistently — this is good. Docstrings are present for public methods.
* Function and class responsibilities are mostly single-purpose.

**Areas for improvement (with priority)**

1. **(High)** - **Avoid global `random.seed` inside library code.** This should be removed; instead accept a `rng: random.Random | None` optional parameter or use dependency injection of RNG for deterministic testing. Rationale: reseeding globally will affect unrelated code and tests. Also the seed in library hides true randomness and causes spurious determinism in production runs. *Action:* refactor `CombatEngine.resolve_hit` to accept an RNG or make the RNG a per-engine attribute.

2. **(High)** - **Ensure `ctx.final_damage` is consistently set before returning.** Right now `_apply_post_pierce_crit` computes and assigns `ctx.final_damage` only when Tier 3 is active, but there is no point where the non-crit or Tier 1/2 final damage is written to `ctx.final_damage`. *Action:* after mitigation calculation, set `ctx.final_damage = ctx.mitigated_damage` and then, if necessary, call `_apply_post_pierce_crit` to overwrite it. Add tests that explicitly assert `ctx.final_damage` is assigned in all branches.

3. **(Medium)** - **Prefer local RNG or injected RNG for tests.** Create helper `make_rng(seed)` in test utilities and switch tests to use it. This avoids reseeding global random; tests become explicit about expected draws.

4. **(Medium)** - **Improve naming & docstrings consistency.** A few methods/docstrings refer to `final_damage` and `pre_mitigation_damage` interchangeably; unify terminology and document pipeline stages in one place (the HitContext docstring is a good candidate).

5. **(Low)** - **Add small unit-level contracts and invariants.** E.g. assert `0 <= pierce_ratio <= 1.0` at validation (or at least check pierce ratio is sane). The code checks `pierce_ratio >= 0.01` but not an upper bound.

6. **(Low)** - **Type hint improvements for RNG injection.** Annotate optional RNG parameters as `random.Random` and add tests covering the case when `rng` is provided vs not.

---

## Tests & coverage review

**What looks good**

* Tests exist for models, state, engine, events and HitContext. The test count and passing output in docs indicate good breadth for implemented features. The tests include seeded randomness which is a great start for reproducible behavior.

**Issues & missing tests (priority ordered)**

1. **(High)** - **Global RNG reseed can mask flaky tests:** several tests call `random.seed(42)` themselves and the code also calls `random.seed(42)` inside `resolve_hit`. This double-seeding pattern can mask flakiness by making results deterministic but also creates hidden coupling between tests and library. Tests should not rely on the library reseeding the global RNG; instead the library should accept an RNG or the test should inject an RNG. Add tests asserting that unrelated RNG draws are unaffected.

2. **(High)** - **Missing tests for `ctx.final_damage` assignment and post-pierce crit path.** There is a test fragment asserting Tier 3 recalculation (see test snippet), but the engine implementation doesn't call `_apply_post_pierce_crit` from `resolve_hit`—add explicit unit tests that fail if `ctx.final_damage` is not set or post-pierce crit logic is not executed.

3. **(Medium)** - **DoT tick resolution & time-based simulation tests.** Phase notes reference DoT stacking and time-based delta processing, but I did not find unit tests that simulate time progression and DoT ticks (only proc application tests). Add tests that run `SimulationRunner` or `StateManager.tick(dt)` to ensure DoT ticks correctly apply damage over time and durations decrement as expected.

4. **(Medium)** - **Multi-hit skills determinism.** Multi-hit skills must be tested for per-hit crit checks, per-hit proc rates, and aggregated state changes. Add tests for a multi-hit skill with mixed crit outcomes and ensure stacks/duration behave correctly.

5. **(Medium)** - **Edge numeric cases & bounds testing.** Tests for very high armor values (e.g., 1e9), zero pierce, pierce near 1.0, negative inputs should be present. Also test underflow/overflow safety where floats may lose precision.

6. **(Low)** - **Event ordering and reentrancy tests.** If an `OnHitEvent` handler triggers another `OnHitEvent` or modifies the EventBus subscriptions, confirm event ordering is deterministic and safe.

7. **(Low)** - **Property-based tests where appropriate.** For damage formula invariants, a few Hypothesis-style tests would be valuable: e.g., final damage should always be >= 0 and `final_damage >= attack_damage * pierce_ratio` when armor=0, etc.

**Suggested immediate test additions**

* Test: `resolve_hit` with RNG injected ensures both crit/no-crit outcomes without global seeding. (High)
* Test: `resolve_hit` sets `ctx.final_damage` in all branches; Tier 3 recalculation path covered. (High)
* Test: `SimulationRunner` runs for N seconds and DoT ticks produce expected cumulative damage. (Medium)
* Test: Multi-hit skill with deterministic RNG injected, verifying per-hit events. (Medium)

---

## Specific code issues & probable bugs

1. **`random.seed(42)` inside `resolve_hit` (src/engine.py) — BUG / anti-pattern (High).** This reseeds global RNG every call. It should be removed and replaced with injected RNG or left to tests.

2. **`ctx.final_damage` sometimes left unset (High).** Implementation calculates `ctx.mitigated_damage` but doesn't always assign `ctx.final_damage` before returning. `_apply_post_pierce_crit` updates `ctx.final_damage` when tier 3 is active but `resolve_hit` should otherwise set `ctx.final_damage = ctx.mitigated_damage`. Tests may be passing because other code reads `mitigated_damage`, but the HitContext contract claims `final_damage` will hold the result. Add an explicit assignment.

3. **Inconsistent crit application order (Medium).** The design doc and code imply tier 2 applies to pre-mitigation damage while tier 3 applies post. Implementation's `_apply_post_pierce_crit` recalculates using `ctx.base_damage * crit_damage` rather than `ctx.pre_mitigation_damage * crit_damage` (which could miss flat bonuses intended to be included in pre-mitigation value once those are implemented). Consider using `ctx.pre_mitigation_damage` as the base for crit multipliers so future flat bonuses are included consistently.

4. **Validation bounds (Low).** `validate_damage_calculation` checks lower bounds but not an upper bound for `pierce_ratio`. Decide whether `pierce_ratio > 1.0` should be allowed; if not, add a check.

5. **Tests seeding both in tests and code (Medium).** Remove library-side seeding and centralize deterministic control in tests.

---

## Recommendations & prioritized action list

### Critical (fix within days)

1. Remove `random.seed(42)` from `resolve_hit`. Implement RNG injection (optional `rng: random.Random = None`) and use `rng.random()` when provided else `random.random()` without reseeding. Update tests accordingly. (Priority: **High**)
2. Ensure `ctx.final_damage` is always set before `resolve_hit` returns; set it to `ctx.mitigated_damage` by default then apply post-pierce crit override. Add tests. (Priority: **High**)
3. Add unit tests specifically covering Tier 3 post-pierce crit recalculation path and assert final damage equals expected. (Priority: **High**)

### Important (fix within 1-2 weeks)

4. Add tests for multi-hit skills and DoT tick/time progression. (Priority: **Medium**)
5. Add bounds checks for `pierce_ratio` upper limit and document acceptable ranges. (Priority: **Medium**)
6. Replace global RNG usage across codebase with injected RNG where deterministic behavior is required. (Priority: **Medium**)

### Nice-to-have (future)

7. Introduce property-based tests for invariants (Hypothesis). (Priority: **Low**)
8. Add linters (`ruff`), formatter (`black`), and static type checking (`mypy`) into CI. (Priority: **Low**)
9. Add README section with reproducibility instructions and seed-handling conventions. (Priority: **Low**)

---

## Other observations & suggestions

* The documentation and changelog are excellent and should be kept up-to-date as refactors happen.
* When porting to Godot/GDScript: keep the core deterministic-provision approach (inject RNG) so Godot's random APIs can be swapped in easily.
* Consider adding a `tests/fixtures.py` file providing `make_entity(...)`, `make_attacker(...)`, and `make_rng(seed)` helpers to reduce duplication.

---

## Final notes

This prototype is well-designed and close to a production-quality prototype. Fixing the RNG seeding and ensuring final damage is always set will move the project much closer to best practice. If you want, I can:

---

**End of report**
