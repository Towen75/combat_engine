# 🗺️ Master Roadmap: Project "Ludus" (Gladiator Manager)

**Vision:** A deterministic, data-driven Auto-Battler where player agency comes from strategic preparation (Drafting, Crafting, Outfitting), not twitch reflexes.

## 🧱 Milestone 1: The Core Loop (Persistence)
*Goal: Connect the disparate systems (Factory, Loot, Combat) into a continuous session.*

### **Phase 1: The Game Loop** (Immediate Focus)
*   **Objective:** Create a persistent "Session" wrapper. Fight -> Loot -> Inventory -> Equip -> Fight Next.
*   **Key Systems:** `GameSession`, `InventoryManager`.
*   **Deliverable:** A Streamlit page where you can play a sequence of 5 fights, collecting loot along the way.

## ⚔️ Milestone 2: Strategic Depth
*Goal: Make "Setup" the primary mechanic. Weapons and Stats must feel distinct.*

### **Phase 2: Weapon Mechanics**
*   **Objective:** Daggers feel different from Hammers.
*   **Key Systems:** Content Compiler updates (implicit affixes), Simulation logic for Attack Speed.
*   **Adjustment:** No AI. Skills fire on cooldown. The strategy is purely mathematical (e.g., "I need fast hits to proc Bleed" vs "I need big hits to penetrate Armor").

## ⚒️ Milestone 3: The Economy & Progression
*Goal: Validate the scaling curves and "Risk vs Reward" loops.*

### **Phase 3: Crafting & Leveling**
*   **Objective:** Implement the "Natural vs Upgraded" rarity math.
*   **Key Systems:** `The Forge` (Upgrade/Salvage logic), XP tracking, Entity Stat Scaling curves.

## 🔬 Milestone 4: Observability & Tooling
*Goal: Professional-grade debugging and analysis tools.*

### **Phase 4: Testing Polish**
*   **Objective:** Refactor test suite structure. Use tests not just for bugs, but for **Balance Assertions** (e.g., "A Level 10 Warrior MUST beat a Level 10 Goblin 90% of the time").

### **Phase 5: RNG Transparency (The "Black Box" Recorder)**
*   **Objective:** Log every single RNG roll with context.
*   **Deliverable:** A readable log: `RNG[0042]: Roll 0.15 -> False (Context: Crit Check, Tier 1)`.

### **Phase 6: Deterministic Replay System**
*   **Objective:** Export a JSON file representing a battle.
*   **Deliverable:** A "Replay Viewer" that loads the JSON and re-simulates the fight exactly, allowing developers to debug specific edge cases sent by users.

## 🧬 Milestone 5: The "Super Entity"
*Goal: Complex character building.*

### **Phase 7: Traits & Kits**
*   **Objective:** Entities become "Super Items."
*   **Key Systems:**
    *   **Traits:** Passive skills (Affixes) attached to the Actor, not the Item.
    *   **Kits:** Starting bundles of Traits/Skills that can evolve during the game randomly from a pool of kits specific skills.
    *   **Cross-Class:** Special hard to find Items granting Traits (e.g., "Gauntlets of Duality" granting Dual Wield) to "break the game".

---

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

---

**Decision:**
Do you approve the **Master Roadmap** and the **Feature Plan for Slice 1**?
If yes, I will generate the **Work Item** for **Phase 1.1: The Inventory System**.