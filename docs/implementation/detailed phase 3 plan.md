### **Detailed Plan: Phase 3 - Building the Game Systems**

**Objective:** To integrate the item and skill systems from the GDD into the combat engine. By the end of this phase, we will have a system where a character's stats are dynamically calculated based on their equipment, and they can use multi-hit skills with unique event triggers to deal damage.

---

#### **Task 1: Item and Affix Data Models**

**Objective:** Create data structures for items and their magical properties (affixes), based on GDD Sections 7.3 and 7.5.

**Key Components/Classes:**
*   `Affix` (Data Class)
*   `Item` (Data Class)

**Implementation Steps:**

1.  **Create the `Affix` Class:** This will define a single bonus on an item. We need to distinguish between flat bonuses and multipliers as specified in your GDD.
    ```python
    # in models.py
    from dataclasses import dataclass
    from typing import Literal

    @dataclass
    class Affix:
        stat: str  # e.g., "base_damage", "crit_chance", "armor"
        mod_type: Literal["flat", "multiplier"]
        value: float
    ```

2.  **Create the `Item` Class:** This class represents a piece of equipment. It will have a slot and a list of affixes.
    ```python
    # in models.py
    from typing import List

    @dataclass
    class Item:
        id: str
        name: str
        slot: Literal["Head", "Chest", "Hands", "Weapon", ...] # From GDD 7.1
        affixes: List[Affix]
    ```

**Testing Strategy:**
*   **Unit Test 1.1:** Create an `Item` instance (e.g., a sword) with a list of `Affix` objects (e.g., a flat damage bonus and an attack speed multiplier). Verify that all data is stored correctly.

---

#### **Task 2: Equipment System & Dynamic Stat Calculation**

**Objective:** Refactor the `Entity` class to allow for equipping items and to calculate a "final stats" object that the `CombatEngine` will use.

**Key Components/Classes:**
*   `Entity` (Refactored)

**Implementation Steps:**

1.  **Update the `Entity` Class:** Add an equipment dictionary and change the `stats` property to `base_stats`.
    ```python
    # in models.py
    class Entity:
        def __init__(self, id: str, base_stats: EntityStats, rarity: str = "Common"):
            self.id = id
            self.base_stats = base_stats
            self.rarity = rarity
            # Equipment will be stored in a dictionary mapping slot to Item
            self.equipment = {} 
            # This will hold the dynamically calculated stats
            self.final_stats = self.calculate_final_stats()

        def equip_item(self, item: Item):
            """Equips an item to its designated slot and recalculates stats."""
            self.equipment[item.slot] = item
            self.recalculate_stats()

        def recalculate_stats(self):
            """Public method to trigger stat recalculation."""
            self.final_stats = self.calculate_final_stats()

        def get_crit_tier(self) -> int:
            # ... (from Phase 2) ...

        def calculate_final_stats(self) -> EntityStats:
            """
            Calculates the final stats of the entity by applying item affixes.
            Follows GDD 2.1: Flats first, then multipliers.
            """
            # Start with a copy of the base stats
            # IMPORTANT: Convert the dataclass to a dictionary for easy modification
            final_stats_dict = self.base_stats.__dict__.copy()

            # 1. Apply all FLAT affixes first
            for item in self.equipment.values():
                for affix in item.affixes:
                    if affix.mod_type == "flat":
                        final_stats_dict[affix.stat] += affix.value

            # 2. Apply all MULTIPLIER affixes second
            for item in self.equipment.values():
                for affix in item.affixes:
                    if affix.mod_type == "multiplier":
                        final_stats_dict[affix.stat] *= affix.value
            
            # Create a new EntityStats object from the modified dictionary
            return EntityStats(**final_stats_dict)
    ```
2.  **Update `CombatEngine` and `process_attack`:** Modify all functions to use `entity.final_stats` instead of `entity.stats` or `entity.base_stats`.
    ```python
    # in engine.py
    # Example change:
    def resolve_hit(attacker: Entity, defender: Entity) -> HitContext:
        # Use final_stats, which includes equipment bonuses
        ctx = HitContext(attacker=attacker, defender=defender, base_damage=attacker.final_stats.base_damage)
        # ... rest of the function remains the same but uses ctx.attacker.final_stats
    ```

**Testing Strategy:**
*   **Unit Test 2.1:** Create an `Entity`. Equip an item with a flat `+20 base_damage` affix. Call `recalculate_stats()` and assert that `final_stats.base_damage` is `base_stats.base_damage + 20`.
*   **Unit Test 2.2:** Equip an item with a `1.5` multiplier to `base_damage`. Assert `final_stats.base_damage` is `base_stats.base_damage * 1.5`.
*   **Integration Test 2.3:** Equip both items from the tests above. If base damage is 100, the result should be `(100 + 20) * 1.5 = 180`, not `(100 * 1.5) + 20 = 170`. This verifies the order of operations.

---

#### **Task 3: Skill Data Models & Combat Engine Integration**

**Objective:** Define skills as data objects and create the logic to execute them, including handling multi-hits and skill-specific event triggers.

**Key Components/Classes:**
*   `Trigger` (Data Class)
*   `Skill` (Data Class)
*   `CombatEngine` (New Method)

**Implementation Steps:**

1.  **Define `Trigger` and `Skill` Classes:** These will be data containers based on GDD Sections 3.0 and 4.1.
    ```python
    # in a new file, skills.py
    from dataclasses import dataclass, field
    from typing import List, Dict, Any

    @dataclass
    class Trigger:
        event: str  # "OnHit", "OnCrit", etc.
        check: Dict[str, Any]  # e.g., {"proc_rate": 0.5}
        result: Dict[str, Any] # e.g., {"apply_debuff": "Bleed", "stacks": 1}

    @dataclass
    class Skill:
        id: str
        name: str
        damage_type: str = "Physical"
        hits: int = 1
        triggers: List[Trigger] = field(default_factory=list)
    ```

2.  **Add `process_skill_use` to `CombatEngine`:** This new orchestrator function handles a complete skill action.
    ```python
    # in engine.py
    class CombatEngine:
        # ... (resolve_hit from before) ...

        @staticmethod
        def process_skill_use(attacker: Entity, defender: Entity, skill: Skill, event_bus: EventBus, state_manager: StateManager):
            """Processes a full skill use, including all hits and triggers."""
            for _ in range(skill.hits):
                # 1. Resolve the damage for a single hit
                hit_context = CombatEngine.resolve_hit(attacker, defender)
                damage = hit_context.final_damage
                state_manager.apply_damage(defender.id, damage)

                # 2. Dispatch core events (OnHit, OnCrit)
                hit_event = OnHitEvent(...)
                event_bus.dispatch(hit_event)
                if hit_context.is_crit:
                    event_bus.dispatch(OnCritEvent(hit_event))
                
                # 3. Process Skill-Specific Triggers
                for trigger in skill.triggers:
                    if trigger.event == "OnHit":
                        # Perform the check (e.g., proc rate)
                        if random.random() < trigger.check.get("proc_rate", 1.0):
                            # Execute the result
                            if "apply_debuff" in trigger.result:
                                state_manager.add_or_refresh_debuff(
                                    defender.id,
                                    trigger.result["apply_debuff"],
                                    trigger.result.get("stacks", 1)
                                )
    ```

---

#### **Task 4: Full Integration Test**

**Objective:** Combine all components from Phases 1, 2, and 3 into a single, comprehensive test script.

**Implementation Steps:**

1.  **Create all necessary objects:**
    *   `EventBus` and `StateManager`.
    *   A `BleedHandler` (from Phase 2, modified to be a class instance).
    *   An attacker `Entity` with base stats.
    *   A defender `Entity` with base stats.
    *   An `Item` with a flat damage affix and a crit chance affix.
    *   A `Skill` with `hits: 3` and an `OnHit` trigger to apply a "Poison" debuff (you will need to create a simple `PoisonHandler` like the `BleedHandler`).

2.  **Write the test script `run_phase3_test.py`:**
    ```python
    # in run_phase3_test.py
    # 1. Imports and Class Instantiations...
    # ... (event_bus, state_manager, handlers for Bleed and Poison)

    # 2. Define Game Data
    player = Entity(id="player_1", base_stats=EntityStats(base_damage=50, crit_chance=0.1))
    enemy = Entity(id="enemy_1", base_stats=EntityStats(max_health=1500, armor=50))
    
    axe = Item(id="axe_01", name="Vicious Axe", slot="Weapon", affixes=[
        Affix(stat="base_damage", mod_type="flat", value=20),
        Affix(stat="crit_chance", mod_type="flat", value=0.15)
    ])
    
    multi_slash = Skill(id="skill_01", name="Multi-Slash", hits=3, triggers=[
        Trigger(event="OnHit", check={"proc_rate": 0.33}, result={"apply_debuff": "Poison"})
    ])

    # 3. Setup
    state_manager.register_entity(player)
    state_manager.register_entity(enemy)
    
    print("--- Initial Player Stats ---")
    print(player.final_stats) # Should show base stats

    player.equip_item(axe)
    print("\n--- Player Stats After Equipping Axe ---")
    print(player.final_stats) # Should show updated stats (damage 70, crit 0.25)
    
    # 4. Simulation
    print(f"\n--- {player.id} uses {multi_slash.name} on {enemy.id} ---")
    CombatEngine.process_skill_use(player, enemy, multi_slash, event_bus, state_manager)

    # 5. Report Results
    final_state = state_manager.get_state(enemy.id)
    print("\n--- Final Enemy State ---")
    print(f"Health: {final_state.current_health} / {enemy.base_stats.max_health}")
    print(f"Debuffs: {final_state.active_debuffs}")
    ```

**Expected Outcome:**
The script will run, showing the player's stats increasing after equipping the axe. It will then simulate the 3-hit skill. The output will detail each hit, some of which may be criticals, and some of which will apply Poison. The final report will show the enemy's remaining health and any debuffs applied, confirming that items, stats, skills, and events are all working together correctly.

---

### **End of Phase 3 Deliverables**

1.  **`models.py` (Updated):** Now includes `Affix` and `Item` classes, and the refactored `Entity` class with the equipment system.
2.  **`skills.py` (New):** Contains the `Trigger` and `Skill` data classes.
3.  **`engine.py` (Updated):** Heavily refactored to use `final_stats` and includes the new `process_skill_use` orchestrator.
4.  **`tests/` (Updated):** New unit tests for the equipment system and skill execution logic.
5.  **`run_phase3_test.py` (New):** A comprehensive integration test script that serves as a living document and a test case for the entire system so far.