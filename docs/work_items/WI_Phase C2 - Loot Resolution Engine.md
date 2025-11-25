# 📋 Work Item: Phase C2 - Loot Resolution Engine (Revised)

**Phase:** Phase C - Deterministic Loot System
**Component:** Core Systems (`src/core/`)
**Context:** `docs/feature_plans/FP_Deterministic_Loot_System.md`

## 🎯 Objective
Implement the `LootManager` class responsible for converting a `loot_table_id` into a list of actual `Item` objects. This engine handles the mathematical resolution of weighted probability tables, stack size randomization, and recursive table traversal.

## 🏗️ Technical Implementation

### 1. Schema Changes
*None. (Data structure defined in Phase C1).*

### 2. Data Model Changes
*None. (Uses `LootTableDefinition` and `LootTableEntry` from Phase C1).*

### 3. Core Logic & Architecture
*   **Class:** `src/core/loot_manager.py` -> `LootManager`
*   **Responsibilities:**
    *   **Weighted Selection:** Select one entry from a table based on relative `weight` using `RNG.weighted_choice`.
    *   **Filtering:** Apply `drop_chance` checks before weight calculation.
    *   **Quantity Resolution:**
        *   **Algorithm:** Uniform Integer Distribution (`rng.randint(min, max)`).
        *   This determines how many *times* we roll the inner content, or how many copies of an item are created.
    *   **Recursion:** If the selected entry is a `TABLE`, call `roll_loot()` recursively.
    *   **Item Generation:** If the selected entry is an `ITEM`, delegate to `ItemGenerator`.
*   **Dependencies (DI):**
    *   `GameDataProvider`: To look up `LootTableDefinition`.
    *   `ItemGenerator`: To create actual item instances.
    *   `RNG`: **Crucial.** Must be injected.

## 🛡️ Architectural Constraints (Critical)
*   [x] **Error Handling:** If a `loot_table_id` is not found:
    *   **Decision:** Raise `ValueError`. "No loot" is a valid valid game state (empty list), but "Missing Table" is a bug. Silent failure would make debugging configuration errors impossible.
*   [x] **Determinism:** `LootManager` must accept an `RNG` instance. `min_count` to `max_count` must use `rng.randint`.
*   [x] **Performance & Safety:**
    *   **Recursion:** Enforce `MAX_DEPTH = 10` (failsafe).
    *   **Explosion Protection:** Enforce `MAX_TOTAL_ITEMS = 50` per call. Deeply nested tables with multipliers (e.g., Drop 10 of Table B, which drops 10 of Table C) create exponential object generation. We must cap this to prevent frame drops.

## ✅ Definition of Done (Verification)
1.  [ ] **Unit Test:** `tests/test_loot_manager.py`.
    *   **Weighted Weights:** Run 1000 rolls, verify statistical distribution.
    *   **Quantity:** Verify `min=2, max=5` produces integers 2, 3, 4, 5 roughly evenly.
    *   **Error Handling:** Verify calling a non-existent table ID raises `ValueError`.
    *   **Safety Limits:** Create a test table that tries to drop 1000 items; verify it clamps to the limit or raises a warning.
2.  [ ] **Integration:** Can be instantiated in a script and produce items from the sample `forest_zone_loot`.
3.  [ ] **Clean Code:** Fully typed `roll_loot(table_id: str) -> List[Item]`.
