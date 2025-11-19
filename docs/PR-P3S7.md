### **PR-P3S7: Final Integration Test and CI Hardening**

## Overview

This PR creates the definitive end-to-end integration test for the combat engine, ensuring all refactored and newly implemented systems work together correctly. It replaces the old, `print`-based `run_full_test.py` script with a fully automated, deterministic, and assertion-based `pytest` test.

This test will serve as the primary "health check" for the entire system in a Continuous Integration (CI) environment.

## Objectives

1.  **Create a Definitive Integration Test:** Convert the scenario from `run_full_test.py` into a proper `pytest` test.
2.  **Enforce Determinism:** Ensure the test produces the exact same result every single time it is run.
3.  **Use Programmatic Assertions:** Replace all `print()`-based checks with `assert` statements that programmatically validate the final game state.
4.  **CI Readiness:** The final test must be suitable for running automatically in a CI pipeline.

## Technical Changes

### **New Test File (`tests/test_integration.py`)**
A new test file is created to house the end-to-end test.

**Key Features of the Test:**
*   **Seeded RNG:** The test creates a single, seeded `random.Random()` instance at the beginning. This same instance is then injected into the `CombatEngine`, `ItemGenerator`, and any other component that requires randomness.
*   **Full Scenario Simulation:** The test sets up the "berserker vs. tank" scenario, including equipping items with conditional affixes.
*   **State Assertion:** After the simulation loop runs for a fixed duration, the test uses `assert` statements to verify the final state:
    *   `assert state_manager.get_current_health("defender_id") == pytest.approx(EXPECTED_HEALTH)`
    *   `assert state_manager.get_current_resource("attacker_id") == pytest.approx(EXPECTED_RESOURCE)`
    *   `assert "Bleed" in [e.definition_id for e in state_manager.get_active_effects("defender_id")]`
    *   `assert len(attacker_state.roll_modifiers.get('crit_chance', [])) > 0`

## Migration Checklist

*   [ ] Create the new `tests/test_integration.py` file.
*   [ ] Copy the setup logic from `run_full_test.py` into a new test function (e.g., `test_full_combat_scenario`).
*   [ ] Implement the deterministic RNG seeding and injection.
*   [ ] Replace all `print()` calls with `logging.info()` for visibility during test runs.
*   [ ] Remove all `print()`-based "verification checks" and replace them with `assert` statements that check the final values in the `StateManager`.
*   [D]elete the now-obsolete `run_full_test.py` script.
*   [ ] Run the new integration test and confirm that it passes reliably and deterministically.

## Outcome

*   The project now has a "gold standard" integration test that verifies the correct interaction of all major systems.
*   The test suite is now fully automated and no longer relies on manual inspection of `print` output.
*   The codebase is ready for integration into a CI pipeline where this test can act as a gatekeeper against regressions.

---
