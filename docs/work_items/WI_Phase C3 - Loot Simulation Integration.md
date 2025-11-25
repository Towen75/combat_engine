# 📋 Work Item: Phase C3 - Loot Simulation Integration

**Phase:** Phase C - Deterministic Loot System
**Component:** Handlers & Simulation
**Context:** `docs/feature_plans/FP_Deterministic_Loot_System.md`

## 🎯 Objective
Integrate the Loot System into the main simulation loop. This involves creating a handler that listens for Entity death, triggers the `LootManager`, and dispatches a new `LootDroppedEvent`. The `CombatLogger` will also be updated to record these drops for analysis.

## 🏗️ Technical Implementation

### 1. New Event (`src/core/events.py`)
*   **Class:** `LootDroppedEvent`
*   **Fields:**
    *   `source_id` (str): The entity that dropped the loot.
    *   `items` (List[Item]): The list of generated items.

### 2. Core Logic: Loot Handler (`src/handlers/loot_handler.py`)
*   **Class:** `LootHandler`
*   **Responsibilities:**
    *   Subscribe to `EntityDeathEvent`.
    *   Check if the dying entity has a `loot_table_id` (via `GameDataProvider` lookup of `EntityTemplate` if not stored on runtime Entity, or we need to ensure `Entity` has this field).
        *   *Design Decision:* `Entity` runtime object should have `loot_table_id`. We added this to the CSV in Phase B, ensuring it hydrates into `EntityTemplate`. We need to ensure `EntityFactory` passes it to the `Entity` instance.
    *   Call `LootManager.roll_loot()`.
    *   Dispatch `LootDroppedEvent` containing the generated items.
*   **Dependencies:** `EventBus`, `LootManager`.

### 3. Simulation Integration
*   **File:** `src/simulation/combat_simulation.py`
*   **CombatLogger Update:** Add handling for `LootDroppedEvent`.
    *   New Method: `log_loot_drop(source_id, items)`.
    *   Update `get_simulation_report` to include a `loot_analysis` section.
*   **SimulationRunner Update:**
    *   Instantiate `LootManager` (using the shared RNG).
    *   Instantiate `LootHandler`.

### 4. Model Updates (`src/core/models.py`)
*   **Class:** `Entity`
*   **Change:** Add `loot_table_id: Optional[str] = None` to the class definition so instances carry this data from the Factory.

### 5. Factory Updates (`src/core/factory.py`)
*   **Change:** Ensure `EntityFactory` populates `loot_table_id` from the template when creating an `Entity`.

## 🛡️ Architectural Constraints
*   [x] **Decoupling:** `LootHandler` does not know about `CombatLogger`. Communication happens strictly via `LootDroppedEvent`.
*   [x] **Determinism:** `LootManager` already owns the seeded RNG. The Handler simply invokes it.
*   [x] **State Safety:** Event is fired *after* death logic. Dropping loot is a side effect that does not alter combat math.

## ✅ Definition of Done (Verification)
1.  [ ] **Unit Test:** `tests/test_loot_integration.py`
    *   Mock `EventBus`.
    *   Simulate `EntityDeathEvent`.
    *   Assert `LootDroppedEvent` is dispatched with items.
2.  [ ] **Integration:** Run `run_simulation.py`.
    *   Verify `simulation_report.json` contains a "loot" section listing items dropped during the fight.
3.  [ ] **Data Integrity:** Ensure entities created via Factory actually have their `loot_table_id` set.