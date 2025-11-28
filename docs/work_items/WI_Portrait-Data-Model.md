# 📋 Work Item: Portrait Data Model Extension

**Phase:** Phase 1 - Data Structure Extension
**Component:** Data Pipeline / Entity System
**Context:** `docs/feature_plans/FP_Character_Portraits.md`

## 🎯 Objective
Extend the entity data model to support portrait file paths, enabling the campaign UI to display character portraits for heroes and enemies. This creates the foundational data structure needed for visual character representation throughout the campaign phases.

## 🏗️ Technical Implementation

### 1. Schema Changes
*   **File:** `data/entities.csv`
*   **New Columns:**
    *   `portrait_path`: str - Path to PNG portrait file relative to assets directory
*   **Validation Rules:**
    *   Optional field (can be empty)
    *   Must be valid relative path string if provided
    *   Should reference PNG files in assets/portraits/ directory

### 2. Data Model Changes
*   **File:** `src/data/typed_models.py`
*   **New/Modified Class:** `EntityTemplate`
*   **Fields to Add:**
    *   `portrait_path: str = ""` - Path to portrait image file
*   **Hydration Logic:** Update `hydrate_entity_template()` to include portrait_path mapping

### 3. Core Logic & Architecture
*   **Class/Module:** `src/data/schemas.py`
*   **Schema Updates:**
    *   Add `portrait_path` to `ENTITIES_SCHEMA` columns
    *   Use `str_validator` for optional string validation
*   **Responsibilities:**
    *   Validate portrait path format during data loading
    *   Ensure portrait paths are accessible at runtime
    *   Support fallback to default portraits when path is missing

## 🛡️ Architectural Constraints (Critical)
*   [ ] **Determinism:** No RNG usage - pure data structure extension
*   [ ] **State Safety:** No state mutations - data loading only
*   [ ] **Hot-Path:** Not applicable - data loaded at startup
*   [ ] **Type Safety:** Strict string typing for portrait paths

## ✅ Definition of Done (Verification)
*   [ ] **Unit Test:** `tests/test_entity_portrait_data.py` created and passing
*   [ ] **Integration:** Portrait paths load correctly in `run_simulation.py`
*   [ ] **Data Integrity:** Schema validation passes for entities.csv with portrait_path column
*   [ ] **Clean Code:** Type hints added, mypy validation passes
*   [ ] **Documentation:** EntityTemplate docstring updated to describe portrait_path field
