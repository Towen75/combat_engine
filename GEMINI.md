# Gemini Code Assistant Context

This document provides a comprehensive overview of the Combat Engine project, designed to give the Gemini code assistant the necessary context to understand the codebase, its architecture, and its conventions.

## Project Overview

The Combat Engine is a modular, event-driven combat system for dungeon crawler RPGs, written in Python. It features a sophisticated damage calculation pipeline, a flexible character progression and itemization system, and a powerful simulation and analysis framework.

The project is designed with a clear separation of concerns, is highly data-driven, and emphasizes deterministic testing through injectable RNG.

### Key Technologies

*   **Python 3.10+**: The core language for the project.
*   **Pytest**: For unit and integration testing.
*   **Streamlit**: For the web-based dashboard.
*   **Pandas, Numpy, Matplotlib**: For data analysis and simulation reporting.
*   **Pydantic**: For data validation.
*   **PyYAML**: For configuration files.

### Architecture

The architecture is based on a few core principles:

*   **Separation of Concerns**: The engine separates pure calculation logic from state-mutating execution. The `CombatEngine` is responsible for pure calculations, while the `CombatOrchestrator` handles the execution of actions and side effects.
*   **Event-Driven Architecture**: The `EventBus` allows for loose coupling between different parts of the system. Events are fired for various combat actions (e.g., `OnHit`, `OnCrit`) and lifecycle events (e.g., `EntitySpawn`, `EntityDeath`).
*   **Data-Driven Content**: All game content, including items, skills, effects, and entities, is defined in CSV files in the `data/` directory. This allows for easy modification and extension of the game without changing the code.
*   **Dependency Injection**: Systems are designed to have their dependencies injected, which makes them highly testable.

## Building and Running

### Installation

To set up the development environment, follow these steps:

1.  Create and activate a virtual environment.
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running Tests

To run the full test suite, use the following command:

```bash
python -m pytest
```

To run tests with coverage, use:

```bash
python -m pytest --cov=src --cov-report=html
```

### Running Simulations

The `run_simulation.py` script is the main entry point for running combat simulations. It can be configured with various command-line arguments to control the simulation parameters.

```bash
python run_simulation.py --seed 42 --duration 60
```

### Running the Dashboard

The Streamlit-based dashboard can be started with the following command:

```bash
streamlit run dashboard/app.py
```

## Development Conventions

### Code Style

The project follows the standard Python conventions (PEP 8). It also uses `black` for code formatting and `ruff` for linting.

### Type Hinting

All public functions and methods must have type hints. This is enforced to ensure code clarity and to allow for static analysis.

### Docstrings

All public classes and methods must have Google-style docstrings.

### RNG and Determinism

A core principle of the project is deterministic testing. All randomness is handled through an injectable `RNG` class. This ensures that tests are reproducible and that simulations can be run with a fixed seed. **Never use `random.random()` directly.**

### Data-Driven Design

When adding new content like skills, items, or effects, the primary method is to modify the CSV files in the `data/` directory. The `src/data/data_parser.py` script is responsible for parsing and validating this data.
