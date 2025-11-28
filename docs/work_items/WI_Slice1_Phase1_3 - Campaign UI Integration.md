# 📋 Work Item: Phase 1.3 - Campaign UI Integration

**Phase:** Phase 1.3 - Game Loop Foundations
**Component:** Dashboard / UI
**Context:** Tech Demo Slice 1. Visualizes the `GameSession` state machine, allowing users to play the Roguelite loop.

## 🎯 Objective
Create the **Campaign Dashboard** (`pages/4_Campaign.py`). This interface must handle the full game lifecycle: selecting a hero, managing inventory between rounds, initiating combat, and collecting loot. It serves as the primary "Playable" demo.

## 🏗️ Technical Implementation

### 1. New Page
*   **File:** `dashboard/pages/4_Campaign.py`
*   **State Management:**
    *   Initialize `st.session_state.game_session` using a singleton pattern helper.
    *   Persist the `GameSession` object across reruns.

### 2. UI Layouts (By GameState)
The page renders differently based on `session.state`:

#### A. `LOBBY`
*   **Input:** "Hero Archetype" (Selectbox from `entities.csv` where archetype=Hero).
*   **Input:** "Master Seed" (Number input).
*   **Action:** "Start Run" button -> Calls `session.start_new_run()`.

#### B. `PREPARATION` (The Hub)
*   **Layout:** Two Columns.
    *   **Left (Hero):** Entity Card (Stats), Equipment Slots.
        *   *Interaction:* "Unequip" buttons next to slots.
    *   **Right (Inventory):** Grid of Item Cards in the backpack.
        *   *Interaction:* "Equip" button on each item card.
*   **Action:** "Enter Arena" (Start Combat) button.

#### C. `COMBAT`
*   **Display:** Combat Log (reusing existing component).
*   **Logic:** Auto-run the simulation logic once, then display result.
*   **Transition:** Automatically show "Continue" button to move to VICTORY or GAME_OVER based on result.

#### D. `VICTORY`
*   **Display:** "Victory!" Banner.
*   **Loot:** Section showing items in `session.loot_stash`.
    *   *Interaction:* "Take" button per item -> Calls `session.claim_loot()`.
*   **Action:** "Next Stage" button -> Calls `session.advance_stage()`.

#### E. `GAME_OVER`
*   **Display:** "Defeat" Banner.
*   **Action:** "Return to Lobby" button.

### 3. Shared Components
*   **Refactor:** Ensure `render_item_card` (dashboard/components/item_card.py) can support an "Action Button" callback (e.g., "Equip").

## 🛡️ Architectural Constraints
*   [x] **State Persistence:** The `GameSession` instance **must not** be recreated on every button click. Use `st.session_state` checks.
*   [x] **Latency:** Combat simulation happens in Python backend (fast), but Streamlit rerenders the whole page. Ensure logs aren't too massive to crash the browser.
*   [x] **Input Validation:** Ensure hero selection only shows valid "Hero" entities, not monsters.

## ✅ Definition of Done (Verification)
1.  [ ] **Playthrough:** Can start a run with "Hero Warrior", fight Stage 1 (Goblin), win, see loot, equip loot, and start Stage 2.
2.  **Inventory Sync:** Clicking "Equip" on a sword in the UI immediately updates the Player's Attack Damage stat on the screen.
3.  **Determinism:** Entering Seed `123` twice results in the exact same enemy and loot drops.