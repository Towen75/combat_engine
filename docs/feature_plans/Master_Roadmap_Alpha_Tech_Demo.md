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