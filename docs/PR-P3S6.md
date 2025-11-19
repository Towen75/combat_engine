### **PR-P3S6: Project Restructuring and Tooling Integration**

## Overview

This PR executes the first step of the Finalization phase. It completely reorganizes the project from a flat `src/` directory into a clean, modular, and professional repository structure. It also introduces and configures a standard suite of modern Python development tools (`black`, `ruff`, `mypy`) via a `pyproject.toml` file.

This is a foundational step in making the codebase maintainable, scalable, and easy for new developers to navigate.

## Objectives

1.  **Restructure the Project:** Reorganize all source code, tests, and scripts into a logical, hierarchical directory structure.
2.  **Introduce Tooling:** Create a `pyproject.toml` file to manage and configure `pytest`, `black`, `ruff`, and `mypy`.
3.  **Automate Code Quality:** Run the new tools across the entire codebase to enforce consistent formatting and linting rules.

## New Project Structure

The project is reorganized as follows:

```
src/
    __init__.py
    combat/
        __init__.py
        combat_math.py
        engine.py
        orchestrator.py
    core/
        __init__.py
        events.py
        models.py
        skills.py
        state.py
    data/
        __init__.py
        data_parser.py
        game_data_provider.py
        schemas.py
        typed_models.py
    handlers/
        __init__.py
        effect_handlers.py
    simulation/
        __init__.py
        batch_runner.py
        simulation.py
    utils/
        __init__.py
        item_generator.py
tests/
    # ... (mirrors the src structure)
scripts/
    run_simulation_batch.py
    validate_data.py
    demo_item.py
data/
    # ... (all .csv files)
docs/
    # ... (placeholder for documentation)
pyproject.toml
README.md
```
*(Note: Legacy `run_phaseX` and `test_phaseX` scripts are deleted during this restructure.)*

## Tooling Configuration (`pyproject.toml`)

A new `pyproject.toml` file is added with configurations for the following tools:

*   **Black:** Enforces uncompromising code formatting.
*   **Ruff:** A high-performance linter to catch common errors and style issues.
*   **Mypy:** The static type checker, configured to enforce the strict typing rules established in Phase 1.
*   **Pytest:** Configured for test discovery within the new `tests/` structure.

## Migration Checklist

*   [ ] Create the new directory structure.
*   [ ] Move all `.py` files to their new locations.
*   [ ] Systematically update all `import` statements across the entire project to reflect the new paths.
*   [ ] Delete all legacy test and run scripts from the root directory.
*   [ ] Create and configure the `pyproject.toml` file.
*   [ ] Run `black .` and `ruff . --fix` to format and lint the entire codebase.
*   [ ] Run `mypy src/` to confirm that static type checking passes.
*   [ ] Run the full `pytest` suite to ensure all tests are discovered and pass in the new structure.

## Outcome

*   The repository is now clean, organized, and professional.
*   Code quality and style are now enforced automatically, improving consistency and reducing PR review friction.
*   The project is prepared for the final steps of integration testing and documentation.

---
