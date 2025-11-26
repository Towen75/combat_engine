## 📅 Feature Plan: Slice 1 - The Game Loop

**Status:** Proposed
**Target Version:** v2.7.0
**Owner:** System Architect

### 1. Executive Summary
Currently, the engine can run a single fight, but it has no memory. We cannot "keep" the loot we find. This phase introduces the **Persistence Layer**. We will build a Session Manager that tracks the player's state across multiple Streamlit re-runs, allowing for a multi-stage "Run."

### 2. Goals & Success Criteria
*   **Goal 1:** **Persistence.** A player character retains HP, XP (placeholder), and Equipment between fights.
*   **Goal 2:** **Inventory.** A runtime container for `Item` objects. Players can move items from "Bag" to "Slot."
*   **Goal 3:** **Progression.** A defined "Campaign" (List of Stages) that the player proceeds through.
*   **Metric:** A player can complete a 3-stage run (Goblin -> Orc -> Boss), looting an item in Stage 1 and using it in Stage 3.

### 3. Scope Boundaries
### ✅ In Scope
*   **`Inventory` Class:** logic for `add`, `remove`, `equip`, `unequip`. Capacity limits (e.g., 20 slots).
*   **`GameSession` Class:** A state machine (`Lobby`, `Combat`, `Looting`, `Rest`).
*   **Dashboard UI:** A new "Campaign" page that visualizes the Session.

### ⛔ Out of Scope
*   **Saving to Disk:** Session lives in RAM (Streamlit Session State) only for now.
*   **Shop/Trading:** Loot only drops from enemies.
*   **Complex XP:** Leveling is Phase 3.

### 4. Implementation Strategy

#### 🔹 Phase 1.1: The Inventory System
*   **Focus:** Data Structure.
*   **Task:** Create `src/core/inventory.py`. Needs to handle `Item` objects, track capacity, and handle swapping items between "Backpack" and "Entity Equipment Slots."
*   **Output:** `WORK_ITEM-1.1`

#### 🔹 Phase 1.2: The Session State Machine
*   **Focus:** Logic Flow.
*   **Task:** Create `src/game/session.py`. This coordinates the `EntityFactory` (to spawn the player), the `LootManager` (to generate rewards), and the `SimulationRunner` (to resolve combat).
*   **Output:** `WORK_ITEM-1.2`

#### 🔹 Phase 1.3: UI Integration
*   **Focus:** User Experience.
*   **Task:** Build `pages/4_Campaign.py`. Needs an "Inventory View" (Grid of items) and a "Stage View" (Next enemy stats).
*   **Output:** `WORK_ITEM-1.3`

### 5. Risk Assessment
*   **Risk:** **Streamlit State Management.** Streamlit re-runs the script on every click.
    *   *Mitigation:* The `GameSession` object must be robustly cached in `st.session_state` and must handle serialization/deserialization if we move to disk later.
*   **Risk:** **Equipment Sync.**
    *   *Mitigation:* When an item is equipped, it must effectively move from `Inventory` list to `Entity.equipment` dict, and `Entity.calculate_final_stats()` must trigger immediately.