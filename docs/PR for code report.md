✅ PR CHECKLIST (Ordered, Production-Grade)

This list is structured so that each PR is atomic, testable, and safe to merge.

PR 1 — Standardize resolve_hit API (BLOCKING)
Goals

Ensure CombatEngine.resolve_hit() has one clear, documented signature.

Update all calling code + tests.

Remove accidental static usage and inconsistent argument counts.

Tasks

 Decide on final signature:
Recommended: resolve_hit(self, attacker, defender, state_manager: StateManager) -> HitContext

 Enforce state_manager as required (raise ValueError if missing).

 Update all occurrences in tests (test_engine, integration demos, handlers).

 Update related methods: process_attack(), execute_action(), simulation flows.

 Add test: test_resolve_hit_requires_state_manager().

 Ensure docstrings clearly explain required dependencies.

Expected outcome

Engine API is no longer ambiguous, and all components call it consistently.

PR 2 — Replace print() with proper logging across the codebase
Goals

Remove brittle print-based behaviors.

Replace with structured logging (DEBUG/INFO/WARN/ERROR).

Update tests to assert logs or state instead of print calls.

Tasks

 Add module-level logger = logging.getLogger(__name__) in all engine files.

 Replace all print() calls in handlers, data loader, simulation, debug flows.

 Change tests from patch('builtins.print') to caplog (pytest fixture).

 Add logging configuration for local dev (not required for production, but helpful).

Expected outcome

Stable, production-safe output and non-brittle tests.

PR 3 — EventBus overhaul (unsubscribe, safe dispatch, listener isolation)
Goals

Production-grade event system that cannot break the engine.

Prevent listener crashes from stopping event propagation.

Support listener cleanup in tests.

Tasks

 Add unsubscribe(event_type, listener) method.

 Wrap dispatch calls in try/except, log exceptions, continue dispatch.

 Convert listeners[event_type] iteration into list(...) to avoid mutation issues.

 Add tests:

 failing listener does not block others

 unsubscribe removes listener

 subscribing the same listener twice behaves predictably

Expected outcome

Event system is robust, testable, and ready for complex buff/debuff interactions.

PR 4 — Consolidate DoT/Tick logic into a single subsystem
Goals

Eliminate duplicated logic spread across simulation and state.

Provide a canonical tick function: StateManager.process_time(delta).

Tasks

 Create StateManager.tick(delta) or process_time(delta) that:

decrements effect durations

computes tick intervals

applies damage

dispatches tick events

 Refactor simulation to call this unified function.

 Remove duplicate loops from simulation files.

 Add tests for:

 consistent tick timing

 fractional duration handling

 inline vs accumulated delta processing

 DoT stacking and expiration ordering

Expected outcome

One stable place to modify status effects as the game grows.

PR 5 — Harden CSV parsing with schema validation
Goals

Prevent malformed data from crashing the engine.

Provide clear error messages to content designers.

Tasks

 Add explicit schema definitions per file: required columns, types, value ranges.

 Validate missing columns with clear exceptions.

 Wrap numeric conversions (float, int) in try/except with row context.

 Add tests for:

missing column

bad number ("abc" instead of float)

negative values where not allowed

duplicate IDs

Expected outcome

Robust data pipeline supporting future content scaling.

PR 6 — Refactor GameDataProvider (no global, no side-effects)
Goals

Remove implicit global mutable singleton.

Allow easy reloads in tests and modding workflows.

Tasks

 Replace global _global_data_loader with explicit factory or dependency injection.

 Create GameDataProvider.load() and GameDataProvider.reload().

 Use pathlib.Path for root detection.

 Replace print with logging.

Expected outcome

Data loading becomes testable, predictable, and suitable for production or mod systems.

PR 7 — Add module-level typing, interfaces, and Protocols
Goals

Improve clarity and IDE support.

Prevent future inconsistencies (especially with listeners & handlers).

Tasks

 Add typing.Protocol for listener signatures (e.g., EventListener).

 Add missing type hints across engine & state code.

 Run mypy --strict and fix issues.

 Add a pyproject.toml with ruff or flake8 rules.

Expected outcome

Higher correctness and maintainability with minimal risk.

PR 8 — Strengthen integration tests + add edge-case coverage
Goals

Ensure end-to-end behavior matches design specifications.

Tests to add

 Multi-hit skills, hit ordering and event dispatch order.

 Crit tiers from rarity → pre/post-pierce interactions.

 Interaction tests: block + crit, crit + pierce, dodge + roll modifiers.

 Simulated battle with fixed RNG and deterministic final HP.

 Ensure buffs/debuffs apply correctly through EventBus.

Expected outcome

Confidence in correctness and protection against regressions.



⭐ Summary: Your PR roadmap in simplest form
Critical path (PRs 1 → 4)

Fix API, logging, event handling, and effect system duplication.

Reliability & scaling (PRs 5 → 7)

Fix data pipeline, global state, and typing consistency.

Quality & regression-proofing (PRs 80)

Strengthen testing.