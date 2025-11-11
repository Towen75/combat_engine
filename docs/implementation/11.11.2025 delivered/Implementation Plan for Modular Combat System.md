### **Implementation Plan: Core Combat System**

This plan is broken down into phases, starting with the core foundation and progressively adding layers of complexity. The goal is to have a testable module at the end of each phase.

---

### **1. High-Level Strategy & Architecture**

We will adopt a **data-driven** and **event-driven** architecture.

*   **Data-Driven:** All character stats, item affixes, and skill properties will be defined in data files (like JSON or Godot's custom resources) rather than being hard-coded. This makes balancing, testing, and adding new content vastly simpler.
*   **Event-Driven:** The `Event Trigger System` will be the central nervous system of the combat logic. An `EventBus` will dispatch events like `OnHit`, `OnCrit`, etc., and various modules (like DoT applicators or special item effects) will listen and react to them. This decouples effects from the core damage calculation, making the system highly modular.
*   **Engine Agnostic Core:** The core logic will be developed in a standard, engine-agnostic way (initially prototyped in Python for its powerful simulation libraries) with clear separation of concerns, making the final port to GDScript in Godot straightforward.

#### **Core Modules:**
1.  **`DataModels`**: Classes defining the structure of Characters, Skills, Items, and Affixes.
2.  **`CombatEngine`**: A static class or singleton responsible for all damage calculations (`ResolveHit`, `ApplyCritical`, etc.).
3.  **`StateManager`**: Manages the current state of any combat entity (health, resources, active buffs/debuffs).
4.  **`EventBus`**: The central dispatcher for all game events (`OnHit`, `OnCrit`, `OnKill`).
5.  **`EffectHandlers`**: Modules that subscribe to the `EventBus` to apply secondary effects (DoTs, Stuns, Buffs).
6.  **`SimulationFramework`**: A suite of tools for running combat simulations, including a `CombatLogger` and `ReportGenerator`.

---

### **2. Phased Implementation Plan**

#### **Phase 1: The Foundation - Core Damage & State**
This phase creates the absolute minimum required to calculate a single instance of damage.

*   **Task 1: Data Models (`Entity` Class)**
    *   Create a base `Entity` class (or data structure) that holds all core combat stats from your GDD (e.g., `base_damage`, `attack_speed`, `crit_chance`, `crit_damage`, `armor`, `resistances`).
*   **Task 2: State Manager**
    *   Implement a simple `StateManager` that can modify and track an entity's `current_health`.
*   **Task 3: Combat Engine - Basic Damage Formula**
    *   Implement the core damage formula: `Damage Dealt = MAX((Attack Damage - Defences), (Attack Damage * Pierce Ratio))`.
    *   Create a primary function: `CombatEngine.ResolveHit(attacker: Entity, defender: Entity)`. This function will perform the calculation and update the defender's health via the `StateManager`.
*   **Task 4: Unit Testing**
    *   Write a suite of unit tests to verify the damage formula with various inputs (e.g., zero armor, high armor, high pierce).

#### **Phase 2: Adding Layers - Crits & Events**
This phase introduces conditional logic and the event system.

*   **Task 1: Critical Hit Implementation**
    *   Expand `CombatEngine.ResolveHit` to include the `Critical Hit Chance` check.
    *   Implement the "Crit Tier" logic. The `attacker` object should have a `crit_tier` property (derived from rarity/items) that dictates *when* the crit multiplier is applied in the formula (pre-modifier, pre-pierce, post-pierce).
*   **Task 2: EventBus Implementation**
    *   Create a simple `EventBus` with `subscribe()` and `dispatch()` methods.
    *   Define core `Event` data structures (e.g., `OnHitEvent`, `OnCritEvent`), which should contain relevant context (attacker, defender, damage dealt).
    *   Integrate the `EventBus` into the `CombatEngine`. `ResolveHit` should `dispatch` an `OnHit` event for every hit, and an `OnCrit` event if it was a critical.
*   **Task 3: Effect Handlers - DoTs & Stacks**
    *   Create handlers for each DoT type (Bleed, Poison, Burn, Life Drain).
    *   These handlers will `subscribe` to the `OnHit` (or `OnCrit`) event.
    *   Implement the "Combined Refresh Model" logic for applying and refreshing stacks on a target's `StateManager`.
*   **Task 4: Unit & Integration Testing**
    *   Test crit calculations for each tier.
    *   Test that events are dispatched correctly.
    *   Test that DoT handlers apply stacks correctly based on proc rates.

#### **Phase 3: Building the Game Systems - Skills & Items**
This phase connects the core combat logic to the game's progression systems.

*   **Task 1: Item & Affix Data Models**
    *   Create `Item` and `Affix` data structures.
    *   Implement logic for "equipping" items to an `Entity`, which modifies their base stats. This can be a function like `Entity.ApplyEquipment()`.
*   **Task 2: Skill Data Models**
    *   Create a base `Skill` class that defines its properties (hits, targets, damage type, event triggers).
    *   Example: A `Multi-Strike` skill would have `hits: 3` and might contain an `OnHit` trigger with a `proc_rate` for applying `Bleed`.
*   **Task 3: System Integration**
    *   Create a function `Entity.UseSkill(skill, target)`. This function will loop based on the skill's `hits` property, calling `CombatEngine.ResolveHit` for each one.
*   **Task 4: Testing**
    *   Test that equipping items correctly modifies entity stats.
    *   Test that using a skill results in the correct number of hits and event triggers.

#### **Phase 4: Simulation, Reporting & Balancing**
This is where you build the tools to test and balance the entire system.

*   **Task 1: Combat Logger**
    *   Create a `CombatLogger` that subscribes to *all* events on the `EventBus`.
    *   When an event is dispatched, it logs the event type, timestamp, and context to a structured log.
*   **Task 2: Simulation Runner**
    *   Create a `SimulationRunner` class.
    *   It takes an `attacker`, a `defender`, and a `duration` as input.
    *   It runs a simple game loop where the `attacker` uses a specified skill on the `defender` based on their `attack_speed`.
*   **Task 3: Report Generator**
    *   This module processes the data from the `CombatLogger` after a simulation run.
    *   It calculates key metrics: Total Damage, DPS, Damage Breakdown (source of damage), Crit %, DoT Uptime, etc.
*   **Task 4: Initial Simulation & Balancing**
    *   Create sample data objects (see below) and run the first simulations.
    *   Analyze the report to see if the numbers align with your design goals (e.g., "Is Bleed effective?", "Is Burn ramping up too quickly?"). Adjust data values and repeat.

---

### **3. Sample Data Objects (JSON Format)**

Here are example objects for testing, reporting, and simulation, as requested.

#### **A. Test Data: Character & Skill Objects**

```json
{
  "test_character_attacker": {
    "id": "rogue_01",
    "rarity": "Magic",
    "stats": {
      "base_damage": 50,
      "flat_bonus_damage": 10,
      "attack_speed": 1.5,
      "crit_chance": 0.25,
      "crit_damage": 1.75,
      "pierce_ratio": 0.10,
      "health": 1000,
      "armor": 50
    },
    "equipment": [
      {
        "slot": "Hands",
        "name": "Swiftsteel Gauntlets",
        "affixes": [
          {"stat": "attack_speed", "multiplier": 1.1},
          {"stat": "crit_chance", "flat_bonus": 0.05}
        ]
      },
      {
        "slot": "Weapon",
        "name": "Gutting Dagger",
        "affixes": [
          {"stat": "flat_bonus_damage", "flat_bonus": 15},
          {"stat": "pierce_ratio", "flat_bonus": 0.15}
        ]
      }
    ]
  },
  "test_character_defender": {
    "id": "tank_01",
    "rarity": "Normal",
    "stats": {
      "health": 5000,
      "armor": 200,
      "resistances": 20
    }
  },
  "test_skill_multi_hit": {
    "id": "furious_strikes",
    "name": "Furious Strikes",
    "damage_type": "Physical",
    "hits": 3,
    "triggers": [
      {
        "event": "OnHit",
        "check": {"proc_rate": 0.50},
        "result": {"apply_debuff": "Bleed", "stacks": 1}
      }
    ]
  }
}
```

#### **B. Simulation & Reporting Objects**

```json
{
  "simulation_config": {
    "id": "Sim_RogueVsTank_Bleed",
    "description": "Tests the effectiveness of a Bleed build against a high-armor target.",
    "duration_seconds": 60,
    "iterations": 1000,
    "attacker": "rogue_01",
    "defender": "tank_01",
    "skill_to_use": "furious_strikes"
  },
  "simulation_report_output": {
    "simulation_id": "Sim_RogueVsTank_Bleed",
    "total_iterations": 1000,
    "average_duration": 60.0,
    "attacker_stats_snapshot": {
      "final_damage": 82.5,
      "final_attack_speed": 1.65,
      "final_crit_chance": 0.30,
      "final_pierce_ratio": 0.25
    },
    "damage_summary": {
      "average_total_damage": 32450.5,
      "average_dps": 540.8,
      "damage_breakdown": {
        "direct_hits": {"damage": 25100.0, "percentage": 77.3},
        "critical_hits": {"damage": 4350.5, "percentage": 13.4},
        "bleed_dot": {"damage": 3000.0, "percentage": 9.3}
      }
    },
    "performance_metrics": {
      "total_hits": 99000,
      "critical_hit_rate": 0.298,
      "bleed_applications": 24750,
      "average_bleed_uptime": "85.2%"
    }
  }
}
```

This plan provides a clear, step-by-step path to building your combat system with robustness and future expansion in mind. Following these phases will ensure each component is working and tested before you integrate it all together in Godot.