# Combat Engine Code Review Report

**Date:** 2025-11-14
**Status:** Complete

## 1. Overall Assessment

This project is in an excellent state. It is well-documented, clearly architected, and follows a deliberate, phased implementation plan. The data-driven approach to itemization is a significant strength, providing a highly extensible foundation for content creation. The use of deterministic testing for probabilistic systems demonstrates a mature approach to quality assurance.

The codebase is clean, readable, and successfully implements the core features outlined in the design documents. It serves as a fantastic prototype and proof-of-concept.

The following recommendations are aimed at elevating the project from a strong prototype to an architecturally pristine and robust foundation, perfectly positioning it for the upcoming Godot port and future feature expansion. The key areas for improvement are **decoupling the core combat engine from orchestration logic** and **closing a critical gap in test coverage**.

---

## 2. Architectural Purity & Extensibility (Priority A)

Your primary goal is a solid, extensible foundation. The architecture is strong, but several areas can be improved to move from a hardcoded implementation of a pattern to a truly generic and data-driven one.

### 2.1. Combat Engine Decoupling

**Observation:** The `CombatEngine` currently has a method, `process_skill_use`, that is responsible not only for calculation but also for orchestration. It directly calls the `StateManager` to apply damage and the `EventBus` to dispatch events.

**Problem:** This tightly couples the engine to other systems. The engine's role should be purely as a calculator. This coupling makes the engine harder to test in isolation and less flexible. For example, if you wanted to introduce a "combat log" that records events *before* they are dispatched, you would have to modify the engine itself.

**Recommendation `[High]`:** Refactor the `CombatEngine` to be a pure, stateless calculator.
1.  Rename `process_skill_use` to `calculate_skill_use`.
2.  This new method should **not** accept the `state_manager` or `event_bus` as arguments.
3.  Instead, it should return a `SkillUseResult` data object containing the list of calculated `HitContext` results and a list of intended effects/triggers that were met (e.g., `{'action': 'apply_debuff', 'name': 'Bleed'}`).
4.  A higher-level "Orchestrator" (e.g., your main simulation loop) will then be responsible for iterating over this result object, calling `state_manager.apply_damage`, dispatching events via the `event_bus`, and applying triggered effects.

**Benefit:** This makes the `CombatEngine` 100% pure and reusable. The "rules" of the game (what happens after a calculation) are now cleanly separated from the "math" of the game, which is a significant architectural improvement.

### 2.2. Effect Handler Extensibility

**Observation:** The `BleedHandler` and `PoisonHandler` classes contain hardcoded values for `proc_rate`, `duration`, and the `debuff_name`.

**Problem:** To add a new "Burn" effect that procs on hit, you must create a new `BurnHandler` class, largely by copy-pasting existing code. This violates the Don't Repeat Yourself (DRY) principle and isn't truly data-driven.

**Recommendation `[Medium]`:** Generalize the specific handlers.
1.  Create a single, generic `DamageOnHitHandler` class.
2.  This class's constructor should accept a `DamageOnHitConfig` data object containing the `debuff_name`, `proc_rate`, and `duration`.
3.  When setting up your combat, you would create instances of the config (`bleed_config`, `poison_config`) and pass them to new instances of the generic `DamageOnHitHandler`.

**Benefit:** Adding a new on-hit DoT effect becomes a matter of data configuration, requiring **zero new Python code**, which dramatically improves extensibility.

### 2.3. Data Pipeline Robustness

**Observation:** The data pipeline (`data_parser.py` -> `item_generator.py`) is a major strength. However, the `Entity.calculate_final_stats` method implicitly trusts that the `stat_affected` string from `affixes.csv` is a valid stat name.

**Problem:** A typo in the CSV (e.g., "crit_chonce") would not cause a crash but would result in an item silently failing to grant its bonus, leading to a frustrating bug.

**Recommendation `[Low]`:** Add validation for stat names.
1.  Inside the loop in `Entity.calculate_final_stats`, check if the `affix.stat_affected` key exists in the `EntityStats` dictionary before attempting to modify it.
2.  If it doesn't exist, log a warning or raise an error to fail fast and immediately identify the data error.

**Benefit:** Makes the system more robust against common data-entry errors.

---

## 3. Godot Port Facilitation (Priority B)

The Python prototype is an excellent blueprint for the Godot implementation.

*   **Data Pipeline**: The current `.csv` -> `.json` workflow is effective. For Godot, you have two primary options:
    1.  **Load JSON Globally**: Keep the current process. The final `game_data.json` can be loaded by an autoload singleton (e.g., `GameData.gd`) in Godot, making the data available globally. This is the most direct port of your current method.
    2.  **Godot-Native Resources**: A more advanced and "Godot-native" approach would be to create custom `Resource` types in GDScript (e.g., `AffixResource`, `ItemTemplateResource`). Then, you would write a Godot `@tool` script that runs in the editor, reads the CSVs, and generates/updates `.tres` files for each item and affix. This gives you full type-safety and auto-completion within the Godot editor, which is a significant advantage for long-term development. **I recommend exploring this path.**

*   **Architecture Mapping**:
    *   Your class-based structure will translate well to GDScript.
    *   The `CombatEngine` could be an autoload singleton.
    *   An `Entity` would naturally map to a `CharacterBody2D/3D` node. Its stats (`EntityStats`) could be an exported custom `Resource` attached to it.
    *   The `StateManager`'s responsibilities (tracking health, debuffs) would likely be absorbed into the `Entity` node's script itself.

---

## 4. Test Coverage & Correctness

The test suite is well-started but has one critical gap and several smaller ones.

**Observation:** The `test_engine.py` file has good coverage for the basic `resolve_hit` damage formula but completely lacks tests for the `process_skill_use` method.

**Problem:** `process_skill_use` is the most complex method in the engine, orchestrating multi-hits, events, and triggers. A bug here would be critical, and it is currently untested.

**Recommendation `[High]`:** Add comprehensive unit tests for `process_skill_use`.
1.  Create a new test class `TestCombatEngineProcessSkillUse`.
2.  Use `pytest`'s mocking capabilities to mock the `StateManager` and `EventBus`.
3.  **Test Scenarios to Add:**
    *   A 3-hit skill correctly calls `apply_damage` three times.
    *   A skill with a trigger correctly calls `add_or_refresh_debuff` when the RNG procs.
    *   A skill with a trigger does **not** call `add_or_refresh_debuff` when the RNG does not proc.
    *   A multi-hit skill where one hit is a crit correctly dispatches one `OnCritEvent` and multiple `OnHitEvent`s.

**Recommendation `[Medium]`:** Add tests for missing edge cases in `resolve_hit`.
*   Test with `pierce_ratio = 1.0` (100% pierce).
*   Test with `crit_damage = 1.0` (a crit with no damage bonus).
*   Test with `base_damage = 0`.

---

## 5. Prioritized Actionable Recommendations

*   **`[High]` Decouple the Combat Engine:** Refactor `CombatEngine.process_skill_use` to be a pure `calculate_skill_use` function that returns a result object. Move responsibility for applying damage and dispatching events to a higher-level orchestration loop.
    *   **Impact:** Massively improves architectural purity and long-term maintainability.

*   **`[High]` Add Tests for `process_skill_use`:** Create a comprehensive suite of unit tests for the skill processing logic, using mocks for external dependencies like the `StateManager` and `EventBus`.
    *   **Impact:** Closes the single largest gap in test coverage and ensures the most complex interactions work as intended.

*   **`[Medium]` Generalize Effect Handlers:** Refactor specific handlers like `BleedHandler` into a generic `DamageOnHitHandler` that is configured via a data object.
    *   **Impact:** Makes the effect system truly data-driven and adding new on-hit effects trivial.

*   **`[Medium]` Add Edge Case Tests:** Add unit tests for the boundary conditions in `resolve_hit` (e.g., 100% pierce, 0 base damage).
    *   **Impact:** Increases test suite robustness and prevents bugs in non-standard scenarios.

*   **`[Low]` Implement a Game Data Provider:** Create a central provider/registry for the `game_data.json` content and use dependency injection to provide it to systems like `ItemGenerator`.
    *   **Impact:** Decouples game systems from the file system and centralizes data access.

*   **`[Low]` Add Stat Name Validation:** Add a check in `Entity.calculate_final_stats` to warn about or prevent the use of invalid stat names from affix data.
    *   **Impact:** Improves robustness against data entry errors in CSV files.
