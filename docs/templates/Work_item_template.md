# 📋 Work Item: [Title]

**Phase:** [e.g., Phase C - Loot Tables]
**Component:** [e.g., Data Pipeline / Core Engine / Simulation]
**Context:** [Reference to activeContext.md or specific file]

## 🎯 Objective
*A concise summary of what we are building, why we are building it, and the expected outcome.*

## 🏗️ Technical Implementation

### 1. Schema Changes
*   **File:** `data/[filename].csv`
*   **New Columns:**
    *   `[column_name]`: [Type] - [Description]
*   **Validation Rules:**
    *   [e.g., Must be positive integer]
    *   [e.g., Must reference existing ID in items.csv]

### 2. Data Model Changes
*   **File:** `src/data/typed_models.py`
*   **New/Modified Class:** `[ClassName]`
*   **Hydration Logic:** [How to map CSV -> Object]

### 3. Core Logic & Architecture
*   **Class/Module:** `[ClassName]`
*   **Responsibilities:**
    *   [Responsibility 1]
    *   [Responsibility 2]
*   **Dependencies (DI):**
    *   [e.g., GameDataProvider (Singleton/Instance)]
    *   [e.g., RNG (Must be injected)]

## 🛡️ Architectural Constraints (Critical)
*   [ ] **Determinism:** Does this feature use RNG? If yes, how is the seed injected?
*   [ ] **State Safety:** Does this mutate `StateManager`? Is it safe during iteration loops?
*   [ ] **Hot-Path:** Does this run per-frame/tick? (Performance budget check)
*   [ ] **Type Safety:** Are strict types and Enums used?

## ✅ Definition of Done (Verification)
*   [ ] **Unit Test:** `tests/test_[feature].py` created and passing.
*   [ ] **Integration:** Validated within `run_simulation.py` or dashboard.
*   [ ] **Data Integrity:** Schema validation passes.
*   [ ] **Clean Code:** Type hints added, linting checks passed.
```
