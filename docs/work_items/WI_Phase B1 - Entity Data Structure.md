# 📋 Work Item: Phase B1 - Entity Data Structure (Revised)

**Phase:** Phase B - Data-Driven Entities
**Component:** Data Pipeline (`src/data/`)
**Context:** `docs/feature_plans/FP_DATA_DRIVEN_ENTITIES.md`

## 🎯 Objective
Establish the data foundation for spawning entities. This involves defining the CSV schema for `entities.csv`, creating the `EntityTemplate` data model, and updating the `GameDataProvider` to load and validate these templates.

## 🏗️ Technical Implementation

### 1. Schema Changes
*   **File:** `data/entities.csv`
*   **Columns:**
    *   `entity_id` (str): Unique key (e.g., `goblin_grunt`).
    *   `name` (str): Display name.
    *   `archetype` (str): Logical grouping (Monster, NPC).
    *   `level` (int): Base level. **Default: 1**.
    *   `rarity` (str): Rarity Enum (Common, Rare, etc.). **Validated against `Rarity` Enum**.
    *   `base_health` (float): Maps to `EntityStats.max_health`.
    *   `base_damage` (float): Maps to `EntityStats.base_damage`.
    *   `armor` (float): Maps to `EntityStats.armor`.
    *   `crit_chance` (float): Maps to `EntityStats.crit_chance`.
    *   `attack_speed` (float): Maps to `EntityStats.attack_speed`. (Used by `SimulationRunner`).
    *   `equipment_pools` (str): Pipe-separated list (e.g., `common_melee|leather_armor`).
    *   `loot_table_id` (str): Reference to `loot_tables.csv`.
    *   `description` (str): Flavor text.

*   **Validation Logic (`ENTITIES_SCHEMA`):**
    *   `entity_id`: Required, String.
    *   `base_health`: > 0.
    *   `equipment_pools`: Split by `|`.
    *   `rarity`: String (Enum validation happens during Hydration).

### 2. Data Model Changes (`src/data/typed_models.py`)
*   **New Dataclass:** `EntityTemplate`
    *   Field types match `EntityStats` requirements.
*   **Hydration:** `hydrate_entity_template(raw_data)`
    *   Uses `normalize_enum(Rarity, ...)` for the rarity field.
    *   Parses `equipment_pools` string into `List[str]`.

### 3. Core Logic: Data Loading & Validation
*   **Class:** `GameDataProvider`
*   **Cross-Reference Validation Strategy:**
    *   **Equipment Pools:** For each pool string in `equipment_pools`:
        1.  Check if it matches a known `item_id` in `self.items`.
        2.  **IF NOT**: Check if it matches any `affix_pool` defined inside `self.affixes` (Wait, strictly speaking, `ItemGenerator` matches items based on the item's `affix_pools` list).
        *   *Correction:* The `ItemGenerator` (as currently written in Phase 5) usually picks items by `item_id` directly or filters items that *contain* specific tags.
        *   *Decision:* For Phase B1, we will validate that the pool string **appears in at least one Item's `affix_pools` list OR matches an `item_id`.** This ensures the generator has *something* to find.

## 🛡️ Architectural Constraints
*   [x] **Type Safety:** Rarity is strictly typed to the Enum.
*   [x] **Determinism:** Loading is deterministic.
*   [x] **Backward Compatibility:** The schema includes default values for `attack_speed` (1.0) and `crit_chance` (0.0) to match `EntityStats` defaults.

## ✅ Definition of Done (Verification)
1.  [ ] **Unit Test:** `tests/test_entity_data.py`
    *   Verify `entities.csv` parses correctly.
    *   Verify hydration converts "common" -> `Rarity.COMMON`.
    *   Verify cross-reference validation catches an equipment pool that matches *nothing*.
2.  [ ] **Integration:** `GameDataProvider` loads the file without error.