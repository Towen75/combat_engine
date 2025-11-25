# 📋 Work Item: Phase B2 - The Entity Factory

**Phase:** Phase B - Data-Driven Entities
**Component:** Core Systems (`src/core/`)
**Context:** `docs/feature_plans/FP_Data_Driven_Entities.md`

## 🎯 Objective
Implement the `EntityFactory` class. This component is responsible for hydrating `EntityTemplate` definitions into runtime `Entity` objects. It orchestrates the selection of equipment from defined pools, ensuring that entity generation is fully deterministic and data-driven.

## 🏗️ Technical Implementation

### 1. Core Logic: The Factory Class
*   **File:** `src/core/factory.py` (Replace existing placeholder)
*   **Class:** `EntityFactory`
*   **Dependencies (Injected):**
    *   `GameDataProvider`: To retrieve `EntityTemplate` and `ItemTemplate` data.
    *   `ItemGenerator`: To create actual item instances.
    *   `RNG`: To randomly select items from pools.

### 2. Key Algorithms

#### A. Entity Hydration (`create`)
1.  Look up `EntityTemplate` by `entity_id`.
2.  Create `EntityStats` mapping template fields (`base_health`, `armor`, etc.) to stats.
3.  Instantiate `Entity` with a unique instance ID.
4.  Call internal `_equip_entity` method.
5.  Return the initialized entity.

#### B. Equipment Resolution (`_equip_entity`)
The template provides a list of strings in `equipment_pools` (e.g., `["common_melee", "cloth_armor"]`).
For **each** pool string:
1.  **Strategy 1 (Direct ID):** Check if the string matches a specific `item_id` in `GameDataProvider.items`. If yes, generate it.
2.  **Strategy 2 (Pool Lookup):** If not an ID, scan all `ItemTemplate`s. Collect all items where `pool_string` exists in `ItemTemplate.affix_pools`.
3.  **Selection:**
    *   If candidates found: Use `rng.choice(candidates)` to pick one `item_id`.
    *   Call `ItemGenerator.generate(selected_item_id)`.
    *   Equip to Entity.
    *   *Fallback:* If no candidates found, log warning and skip.

### 3. Integration Updates
*   **File:** `src/utils/item_generator.py`
    *   Ensure `ItemGenerator` exposes `generate(item_id)` publicly (it already does).
*   **File:** `run_simulation.py`
    *   Update to use `EntityFactory` instead of manual `Entity(...)` instantiation.

## 🛡️ Architectural Constraints
*   [x] **Determinism:**
    *   The selection of which item to pick from a pool MUST use the injected `RNG`.
    *   The generation of the item itself (affix rolling) MUST use the injected `RNG` (via `ItemGenerator`).
*   [x] **Separation of Concerns:**
    *   The Factory builds the object graph.
    *   The `ItemGenerator` handles item specifics.
    *   The `Entity` handles runtime stat calculations.

## ✅ Definition of Done (Verification)
1.  [ ] **Unit Test:** `tests/test_entity_factory.py`
    *   **Direct Item:** Template requests "iron_sword" -> Entity has Iron Sword.
    *   **Pool Item:** Template requests "weapon_pool" -> Entity has *some* item from that pool.
    *   **Determinism:** Seed X always results in the same item selection from a pool.
    *   **Stats:** Entity base stats match CSV values.
2.  [ ] **Integration:** `run_simulation.py` spawns entities defined in `entities.csv`.
