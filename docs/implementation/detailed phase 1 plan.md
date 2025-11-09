### **Detailed Plan: Phase 1 - The Foundation**

**Objective:** To create the minimum viable product for the combat system. By the end of this phase, we will have a functional, command-line script that can calculate the damage of a single, non-critical hit between two entities and update the defender's state accordingly.

---

#### **Task 1: Data Models - Defining a Combatant (`Entity`)**

**Objective:** Create the data structures that hold all the static information about a character or enemy.

**Key Components/Classes:**
*   `EntityStats` (Data Class or Dictionary)
*   `Entity` (Main Class)

**Implementation Steps:**

1.  **Create `EntityStats`:** This will be a simple data container. Using a Python `dataclass` is ideal for structure and type safety.
    ```python
    from dataclasses import dataclass

    @dataclass
    class EntityStats:
        # GDD Section 3.0 Dimensions & 5.0 Defenses
        base_damage: float = 10.0
        attack_speed: float = 1.0
        crit_chance: float = 0.05
        crit_damage: float = 1.5
        pierce_ratio: float = 0.01  # GDD 2.1: Min value is 0.01
        
        # Defensive Stats
        max_health: float = 100.0
        armor: float = 10.0
        resistances: float = 0.0
    ```

2.  **Create the `Entity` Class:** This class represents a participant in combat. For now, it will have a unique identifier and its stats.
    ```python
    class Entity:
        def __init__(self, id: str, stats: EntityStats):
            self.id = id
            self.stats = stats
    ```

**Testing Strategy:**
*   **Unit Test 1.1:** Create an instance of `EntityStats` with default values and assert that all properties are correct.
*   **Unit Test 1.2:** Create an instance of `Entity` with a custom `EntityStats` object and verify that the `id` and `stats` are correctly assigned.

---

#### **Task 2: State Management - Tracking What Changes**

**Objective:** Create a system to manage the dynamic state of all entities in combat, primarily their health.

**Key Components/Classes:**
*   `EntityState` (Data Class)
*   `StateManager` (Logic Class)

**Implementation Steps:**

1.  **Create `EntityState`:** This tracks the mutable properties of an entity.
    ```python
    from dataclasses import dataclass

    @dataclass
    class EntityState:
        current_health: float
        is_alive: bool = True
    ```
2.  **Create the `StateManager` Class:** This class will manage the state of all registered entities, indexed by their unique ID.
    ```python
    class StateManager:
        def __init__(self):
            # A dictionary to map entity IDs to their state
            self.states = {}

        def register_entity(self, entity: Entity):
            """Initializes and registers an entity's state."""
            if entity.id not in self.states:
                self.states[entity.id] = EntityState(current_health=entity.stats.max_health)

        def get_state(self, entity_id: str) -> EntityState:
            """Retrieves the current state of an entity."""
            return self.states.get(entity_id)

        def apply_damage(self, entity_id: str, damage: float):
            """Applies damage to an entity and updates its state."""
            state = self.get_state(entity_id)
            if state and state.is_alive:
                state.current_health -= damage
                if state.current_health <= 0:
                    state.current_health = 0
                    state.is_alive = False
    ```

**Testing Strategy:**
*   **Unit Test 2.1:** Test that `register_entity` correctly creates a state with health equal to `max_health`.
*   **Unit Test 2.2:** Test `apply_damage` with a value less than the entity's health. Assert that `current_health` is correctly reduced.
*   **Unit Test 2.3:** Test `apply_damage` with a value greater than the entity's health. Assert that `current_health` is exactly `0` and `is_alive` is `False`.

---

#### **Task 3: Combat Engine - The Core Calculation**

**Objective:** Implement the core damage formula from GDD Section 2.1 as a pure, testable function.

**Key Components/Classes:**
*   `CombatEngine` (Module or Static Class)

**Implementation Steps:**

1.  **Create the `CombatEngine`:** This will be a collection of static methods, as it doesn't need to hold any state.
    ```python
    class CombatEngine:
        @staticmethod
        def resolve_hit(attacker: Entity, defender: Entity) -> float:
            """
            Calculates the damage of a single hit based on GDD formula.
            Returns the final damage value.
            """
            # For Phase 1, Attack Damage is just base_damage.
            # GDD states flat modifiers are applied here, which we will add in Phase 2.
            attack_damage = attacker.stats.base_damage
            defenses = defender.stats.armor  # Assuming physical damage for now

            # GDD 2.1: Damage Formula
            pre_pierce_damage = attack_damage - defenses
            pierced_damage = attack_damage * attacker.stats.pierce_ratio
            
            damage_dealt = max(pre_pierce_damage, pierced_damage)
            
            # Ensure damage is never negative
            return max(0, damage_dealt)
    ```

**Testing Strategy:**
*   **Unit Test 3.1 (No Armor):** Attacker `base_damage` = 100, Defender `armor` = 0. Assert result is `100`.
*   **Unit Test 3.2 (High Armor, Low Pierce):** Attacker `base_damage` = 100, `pierce_ratio` = 0.1, Defender `armor` = 120. `PrePierceDamage` is negative, `PiercedDamage` is 10. Assert result is `10`.
*   **Unit Test 3.3 (Armor > Pierced Damage):** Attacker `base_damage` = 100, `pierce_ratio` = 0.3, Defender `armor` = 80. `PrePierceDamage` is 20, `PiercedDamage` is 30. Assert result is `30`.
*   **Unit Test 3.4 (Armor < Pierced Damage):** Attacker `base_damage` = 100, `pierce_ratio` = 0.3, Defender `armor` = 60. `PrePierceDamage` is 40, `PiercedDamage` is 30. Assert result is `40`.

---

#### **Task 4: Integration - The "First Hit" Test**

**Objective:** Combine all the above components into a single script to simulate one entity hitting another.

**Key Components/Classes:**
*   A single script file (e.g., `run_phase1_test.py`)

**Implementation Steps:**

1.  **Instantiate Test Data:** Create two `Entity` objects, one attacker and one defender, using `EntityStats`.
    ```python
    # Attacker: Strong but low pierce
    attacker_stats = EntityStats(base_damage=120, pierce_ratio=0.1)
    attacker = Entity(id="player_1", stats=attacker_stats)

    # Defender: Heavily armored
    defender_stats = EntityStats(max_health=1000, armor=150)
    defender = Entity(id="enemy_1", stats=defender_stats)
    ```
2.  **Set up the State:** Create a `StateManager` and register both entities.
    ```python
    state_manager = StateManager()
    state_manager.register_entity(attacker)
    state_manager.register_entity(defender)
    ```
3.  **Run the Logic:**
    *   Print the defender's initial health from the `StateManager`.
    *   Call `CombatEngine.resolve_hit()` to calculate the damage.
    *   Call `StateManager.apply_damage()` to apply the damage.
    *   Print the damage dealt and the defender's final health.
    ```python
    # --- The Simulation ---
    print(f"--- Phase 1: First Hit Test ---")
    initial_hp = state_manager.get_state(defender.id).current_health
    print(f"{defender.id} initial health: {initial_hp}")

    damage = CombatEngine.resolve_hit(attacker, defender)
    print(f"{attacker.id} attacks {defender.id} for {damage:.2f} damage.")

    state_manager.apply_damage(defender.id, damage)
    final_hp = state_manager.get_state(defender.id).current_health
    print(f"{defender.id} final health: {final_hp}")
    print(f"--- Test Complete ---")
    ```

**Testing Strategy:**
*   Run the script and manually verify the output. For the example data above:
    *   `attack_damage` = 120, `armor` = 150, `pierce_ratio` = 0.1
    *   `PrePierceDamage` = 120 - 150 = -30
    *   `PiercedDamage` = 120 * 0.1 = 12
    *   `DamageDealt` = `max(-30, 12)` = 12
    *   The script should output `12.00` damage, and the defender's health should drop from `1000` to `988`.

---

### **End of Phase 1 Deliverables**

Upon completion of this phase, you will have:
1.  **`models.py`**: A file containing the `Entity` and `EntityStats` classes.
2.  **`state.py`**: A file containing the `EntityState` and `StateManager` classes.
3.  **`engine.py`**: A file containing the `CombatEngine` static class.
4.  **`tests/`**: A folder with unit tests for each of the above modules, ensuring they work correctly in isolation.
5.  **`run_phase1_test.py`**: An executable script that demonstrates the integrated functionality of all Phase 1 components.

This modular structure provides a solid, verifiable foundation to build upon in Phase 2, where you will introduce critical hits and the EventBus.