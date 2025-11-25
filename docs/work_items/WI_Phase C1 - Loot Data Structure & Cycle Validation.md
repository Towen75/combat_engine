# 📋 Work Item: Phase C1 - Loot Data Structure & Cycle Validation

**Phase:** Phase C - Deterministic Loot System
**Component:** Data Pipeline (`src/data/`)
**Context:** `docs/feature_plans/FP_Deterministic_Loot_System.md`

## 🎯 Objective
Establish the data foundation for the Loot System. This includes defining the CSV schema, strict typed models, and implementing a **Depth-First Search (DFS)** validation algorithm to reject circular table references (e.g., A -> B -> A) at load time.

## 🏗️ Technical Implementation

### 1. Schema Changes
*   **File:** `data/loot_tables.csv`
*   **Columns:**
    *   `table_id`: String - Group identifier (Multiple rows can share this ID).
    *   `entry_type`: String - Enum [`Item`, `Table`].
    *   `entry_id`: String - Reference to `items.csv` OR another `table_id`.
    *   `weight`: Integer - Relative probability weight (for weighted random choice).
    *   `min_count`: Integer - Minimum quantity to drop (default 1).
    *   `max_count`: Integer - Maximum quantity to drop (default 1).
    *   `drop_chance`: Float - Independent probability (0.0-1.0) for this entry to roll at all.

*   **Validation Rules:**
    *   `weight` must be >= 0.
    *   `min_count` <= `max_count`.
    *   If `entry_type` is `Item`, `entry_id` must exist in `items`.
    *   If `entry_type` is `Table`, `entry_id` must exist in `loot_tables` (Self-reference checked via DAG algo).

### 2. Data Model Changes (`src/data/typed_models.py`)
*   **New Enum:** `LootEntryType` (`Item`, `Table`)
*   **New Dataclass:** `LootTableEntry`
    *   Represents a single row in the CSV.
*   **New Dataclass:** `LootTableDefinition`
    *   Represents the aggregated table (List of `LootTableEntry` sharing the same `table_id`).
    *   Helper methods: `get_total_weight()`.

### 3. Core Logic: Cycle Detection
*   **Location:** `src/data/game_data_provider.py` -> `_validate_loot_tables()`
*   **Algorithm:** **Recursive Depth-First Search (DFS) with Path Tracking**.
    1.  Construct an adjacency graph where Nodes = `table_id` and Edges = references to other Tables.
    2.  Maintain two sets: `visited` (globally processed) and `recursion_stack` (current traversal path).
    3.  Iterate through every known `table_id`. If not in `visited`, call `dfs(table_id)`.
    4.  **DFS Function:**
        *   Add current ID to `visited` and `recursion_stack`.
        *   For each entry in the table:
            *   If type is `Table`:
                *   If `entry_id` in `recursion_stack`: **Raise DataValidationError (Cycle Detected)**.
                *   If `entry_id` not in `visited`: Recurse `dfs(entry_id)`.
        *   Remove current ID from `recursion_stack`.

## 🛡️ Architectural Constraints
*   [x] **Determinism:** Data loading is deterministic. The validation logic does not require RNG.
*   [x] **State Safety:** Validation occurs during initialization (Startup), guaranteeing no runtime recursion crashes.
*   [x] **Type Safety:** Use `LootEntryType` Enum for strict checks.

## ✅ Definition of Done (Verification)
1.  [ ] **Unit Test:** `tests/test_loot_validation.py`.
    *   Test Case A: Valid nested tables (A -> B -> C) pass.
    *   Test Case B: Direct cycle (A -> A) raises `DataValidationError`.
    *   Test Case C: Indirect cycle (A -> B -> A) raises `DataValidationError`.
    *   Test Case D: Invalid Item Reference raises `DataValidationError`.
2.  [ ] **Integration:** `GameDataProvider` loads `data/loot_tables.csv` successfully without errors.
3.  [ ] **Data:** A sample `loot_tables.csv` is added to the repository.

***