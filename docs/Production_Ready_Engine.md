### **Project Plan: The Production-Ready Engine**

This document outlines the complete, three-phase plan to transform the combat engine into a robust, maintainable, and production-ready library. Each step is defined by a corresponding Pull Request (PR) that contains the detailed technical specifications for its implementation.

### **Phase 1: Foundational Stability & Correctness**

**Objective:** To fix all outstanding bugs, establish consistent architectural patterns, and harden the data pipeline. This phase ensures the codebase is correct and stable before new features are added.

*   **Step 1: Implement System-Wide Logging and API Hardening (`PR-P1S1`)**
    *   **Objective:** Eradicate all `print()` statements from the core library, establish a structured `logging` framework, and add a missing unit test to validate the `CombatEngine` API guard.
    *   **Key Deliverables:** A `print()`-free core library, a codebase that uses logging for all output, and a more robust test suite.

*   **Step 2: Correct Core Mechanics and Unify RNG (`PR-P1S2`)**
    *   **Objective:** Fix critical bugs in proc rates, dual-stat affixes, and core game logic. Unify the Random Number Generation (RNG) system to make all simulations fully deterministic and testable.
    *   **Key Deliverables:** Functional dual-stat affixes, data-driven proc rates, and a codebase capable of perfectly reproducible, seeded test runs.

*   **Step 3: Harden Data Pipeline with Strict Typing and Validation (`PR-P1S3`)**
    *   **Objective:** Enhance the data pipeline with `Enums`, typed data models, and a second validation layer that checks for logical cross-reference errors (e.g., a skill referencing a non-existent effect).
    *   **Key Deliverables:** A data pipeline that is validated for structure, type-safety, and logical integrity, preventing a wide class of data-related bugs.

### **Phase 2: New Feature Implementation**

**Objective:** To build major new engine features on top of the stable foundation established in Phase 1.

*   **Step 4: Implement Entity Lifecycle Management (`PR-P2S4`)**
    *   **Objective:** Introduce a formal, event-driven entity lifecycle (`OnSpawn`, `OnDeath`, `OnDespawn`) to correctly manage entity state, prevent memory leaks, and enable complex mechanics like on-death effects.
    *   **Key Deliverables:** A robust system that prevents "zombie" entities, automatically cleans up event listeners for dead units, and provides clear hooks for future gameplay features.

*   **Step 5: Build Simulation Batching and Telemetry System (`PR-P2S5`)**
    *   **Objective:** Create the tools to run thousands of deterministic simulations for balancing and regression testing. This includes implementing different telemetry (logging) modes and statistical aggregators.
    *   **Key Deliverables:** A `SimulationBatchRunner` capable of producing reliable, aggregated balance data (e.g., Time-To-Kill, DPS distributions) from high-volume, automated test runs.

### **Phase 3: Finalization & Professionalization**

**Objective:** To organize, document, and polish the entire project, transforming it into a professional-grade, distributable library.

*   **Step 6: Restructure Project and Integrate Tooling (`PR-P3S6`)**
    *   **Objective:** Reorganize the repository into a clean, modular directory structure and integrate standard Python development tools (`black`, `ruff`, `mypy`) to automate code quality and formatting.
    *   **Key Deliverables:** A well-organized repository and a `pyproject.toml` file that enforces consistent code style and quality across the entire project.

*   **Step 7: Create Final Integration Test for CI (`PR-P3S7`)**
    *   **Objective:** Create a single, definitive, end-to-end integration test that is fully deterministic and uses programmatic `assert` statements instead of `print` checks, making it suitable for a Continuous Integration (CI) pipeline.
    *   **Key Deliverables:** A "gold standard" test that serves as a reliable health check for the entire engine, guaranteeing that all core systems work together correctly.

*   **Step 8: Finalize Documentation and Project Polish (`PR-P3S8`)**
    *   **Objective:** Add comprehensive documentation at both the architectural level (in a `/docs` folder) and the code level (via docstrings), and create contributor guides to make the project accessible and maintainable.
    *   **Key Deliverables:** A fully documented project with a helpful `README.md`, architectural diagrams, and contributor guides (`CONTRIBUTING.md`, `CHANGELOG.md`).

---

By executing these eight PRs in sequence, the project will be methodically and robustly transformed into a stable, feature-rich, and professional combat engine.