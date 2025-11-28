# 📋 Work Item: Phase 1.2 - The Session State Machine

**Phase:** Phase 1.2 - Game Loop Foundations
**Component:** Game Logic (`src/game/`)
**Context:** Tech Demo Slice 1. Connects `EntityFactory`, `Inventory`, and `SimulationRunner` into a persistent state machine compatible with Streamlit.

## 🎯 Objective
Implement the `GameSession` class. This object acts as the central controller for a gameplay session. It manages the player's persistent state (Health, Inventory), tracks progression through a "Campaign" (sequence of stages), and handles the flow between Game States (Lobby -> Combat -> Loot -> Next Stage).

## 🏗️ Technical Implementation

### 1. Schema Changes
*   *None required.* (Campaign stages will be defined as a constant list of Entity IDs for Slice 1).

### 2. Data Model Changes
*   **File:** `src/game/enums.py` (New file)
*   **Enum:** `GameState`
    *   `LOBBY`: Character selection / Initial setup.
    *   `PREPARATION`: Managing inventory before a fight.
    *   `COMBAT`: Simulation running/displaying results.
    *   `VICTORY`: Combat won, looting phase.
    *   `GAME_OVER`: Player died.

### 3. Core Logic & Architecture
*   **Class:** `src/game/session.py` -> `GameSession`
*   **State:**
    *   `state`: GameState
    *   `player`: Entity (Runtime object)
    *   `inventory`: Inventory (Runtime object)
    *   `current_stage`: int (Index of current enemy)
    *   `campaign_seed`: int (Master seed for the run)
    *   `loot_stash`: List[Item] (Items dropped but not yet picked up)
*   **Methods:**
    *   `initialize_run(archetype_id: str, seed: int)`: Spawns player, sets seed, resets stage.
    *   `start_combat()`: Uses `EntityFactory` to spawn the current stage's Enemy. Runs `SimulationRunner`.
    *   `resolve_combat(result: SimulationResult)`: Updates Player HP. If Win -> State=VICTORY, Gen Loot. If Loss -> State=GAME_OVER.
    *   `loot_item(item_index: int)`: Moves item from `loot_stash` to `inventory`.
    *   `next_stage()`: Increments stage index, State=PREPARATION.
*   **Dependencies (DI):**
    *   `EntityFactory` (for spawning Player and Enemies).
    *   `LootManager` (for generating rewards).
    *   `RNG` (Managed internally per run).

## 🛡️ Architectural Constraints
*   [x] **Determinism:** The Session takes a `master_seed` at initialization.
    *   Stage 1 RNG = `master_seed + 1`
    *   Stage 2 RNG = `master_seed + 2`
    *   This ensures re-running the same campaign yields the same enemies and drops.
*   [x] **Persistence:** The `GameSession` object must be self-contained so it can be stored in `st.session_state` and survive page reloads.
*   [x] **State Safety:** Transitions must be strict (cannot go from LOBBY to VICTORY).

## ✅ Definition of Done (Verification)
1.  [ ] **Unit Test:** `tests/test_game_session.py`
    *   Verify state transitions (Init -> Prep -> Combat -> Victory -> Prep).
    *   Verify HP persistence (Player takes damage in Stage 1, starts Stage 2 with partial HP).
    *   Verify Loot pickup (Stash -> Inventory).
2.  **Integration:** Can be instantiated in a script, run a mock combat, and advance the stage.