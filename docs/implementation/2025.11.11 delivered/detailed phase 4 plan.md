### **Detailed Plan: Phase 4 - Simulation, Reporting & Balancing**

**Objective:** To create a framework for running automated combat simulations and generating detailed reports. This will be the primary tool for testing game balance, verifying system interactions, and understanding the performance of different character builds.

---

#### **Task 1: The Combat Logger - The System's Scribe**

**Objective:** To create a class that listens to all events from the `EventBus` and records them in a structured, chronological log. This log will be the raw data source for our reports.

**Key Components/Classes:**
*   `CombatLogEntry` (Data Class)
*   `CombatLogger` (Listener Class)

**Implementation Steps:**

1.  **Define `CombatLogEntry`:** This standardizes the format of each log message.
    ```python
    # in a new file, e.g., simulation.py
    from dataclasses import dataclass
    from events import Event # From Phase 2

    @dataclass
    class CombatLogEntry:
        timestamp: float
        event: Event
    ```

2.  **Create the `CombatLogger`:** This class subscribes to all relevant events and stores them.
    ```python
    from typing import List

    class CombatLogger:
        def __init__(self, event_bus: EventBus):
            self.log: List[CombatLogEntry] = []
            # Subscribe to all events we want to track
            event_bus.subscribe(OnHitEvent, self.log_event)
            event_bus.subscribe(OnCritEvent, self.log_event)
            # We will also need to dispatch and log events for DoT damage.
            # This requires adding a new event type.
            # event_bus.subscribe(DamageTickEvent, self.log_event)

        def log_event(self, event: Event):
            # In a real simulation, you'd get the timestamp from the simulation loop
            # For now, we can approximate it or pass it in.
            timestamp = 0.0 # This will be updated by the Simulation Runner
            self.log.append(CombatLogEntry(timestamp=timestamp, event=event))

        def get_log(self) -> List[CombatLogEntry]:
            return self.log
        
        def reset(self):
            self.log = []
    ```
3.  **Define a New Event for DoT Ticks:** The `CombatLogger` needs to know when a DoT deals damage.
    ```python
    # in events.py
    @dataclass
    class DamageTickEvent(Event):
        source: str # e.g., "Bleed", "Poison"
        target_id: str
        damage: float
    ```
---

#### **Task 2: The Simulation Runner - The Game Loop**

**Objective:** To create a class that runs a simulated combat encounter for a set duration, advancing time and processing actions and effects.

**Key Components/Classes:**
*   `StateManager` (Refactored to handle time)
*   `SimulationRunner` (The main loop)

**Implementation Steps:**

1.  **Refactor `StateManager` to Process Time:** We need a way to make debuffs tick and expire.
    ```python
    # in state.py
    class StateManager:
        # ... (previous methods) ...

        def update(self, delta_time: float, event_bus: EventBus):
            """Updates all time-based effects for all registered entities."""
            for entity_id, state in self.states.items():
                if not state.is_alive:
                    continue
                
                expired_debuffs = []
                for debuff_name, debuff in state.active_debuffs.items():
                    debuff.time_remaining -= delta_time

                    # This is a simple tick implementation. GDD 4.4.3 mentions an internal cooldown.
                    # This could be handled here by tracking time since last tick.
                    # For now, we'll assume one tick per second.
                    if int(debuff.time_remaining + delta_time) > int(debuff.time_remaining):
                        # Calculate DoT damage (logic will be expanded)
                        dot_damage = self._calculate_dot_damage(debuff)
                        self.apply_damage(entity_id, dot_damage)
                        
                        # Dispatch tick event for the logger
                        event_bus.dispatch(DamageTickEvent(source=debuff.name, target_id=entity_id, damage=dot_damage))

                    if debuff.time_remaining <= 0:
                        expired_debuffs.append(debuff_name)
                
                # Remove expired debuffs
                for name in expired_debuffs:
                    del state.active_debuffs[name]
        
        def _calculate_dot_damage(self, debuff: Debuff) -> float:
            # Placeholder for GDD 4.3 formulas
            if debuff.name == "Bleed":
                return 10 * debuff.stacks # Example: 10 base damage per stack
            return 0
    ```

2.  **Create the `SimulationRunner`:** This class will contain the main simulation loop.
    ```python
    # in simulation.py
    class SimulationRunner:
        def __init__(self, attacker: Entity, defender: Entity, skill: Skill, event_bus: EventBus, state_manager: StateManager, logger: CombatLogger):
            self.attacker = attacker
            self.defender = defender
            self.skill = skill
            self.event_bus = event_bus
            self.state_manager = state_manager
            self.logger = logger

        def run(self, duration: float, delta_time: float = 0.01):
            """Runs the combat simulation for a specified duration."""
            current_time = 0.0
            time_to_next_attack = 0.0

            while current_time < duration and self.state_manager.get_state(self.defender.id).is_alive:
                # Update time-based effects (DoTs, buffs)
                self.state_manager.update(delta_time, self.event_bus)

                # Process attacker's action
                time_to_next_attack -= delta_time
                if time_to_next_attack <= 0:
                    CombatEngine.process_skill_use(self.attacker, self.defender, self.skill, self.event_bus, self.state_manager)
                    
                    # Reset attack cooldown
                    time_to_next_attack += 1.0 / self.attacker.final_stats.attack_speed
                
                # Update timestamps on all newly logged events
                for entry in self.logger.log:
                    if entry.timestamp == 0.0: # Mark un-timestamped events
                        entry.timestamp = current_time

                current_time += delta_time
            
            print(f"Simulation finished at {current_time:.2f} seconds.")
    ```
---

#### **Task 3: The Report Generator - The Analyst**

**Objective:** To process the raw data from the `CombatLogger` and generate a concise, human-readable summary that matches your requested format.

**Key Components/Classes:**
*   `ReportGenerator`

**Implementation Steps:**

1.  **Create the `ReportGenerator` Class:**
    ```python
    # in simulation.py
    from collections import Counter

    class ReportGenerator:
        def generate(self, log: List[CombatLogEntry], duration: float) -> dict:
            """Processes a combat log and returns a structured report."""
            report = {
                "total_damage": 0.0,
                "dps": 0.0,
                "damage_breakdown": Counter(),
                "performance_metrics": Counter()
            }
            
            for entry in log:
                event = entry.event
                if isinstance(event, OnHitEvent):
                    report["performance_metrics"]["total_hits"] += 1
                    source = "critical_hits" if event.is_crit else "direct_hits"
                    report["damage_breakdown"][source] += event.damage_dealt
                    report["total_damage"] += event.damage_dealt

                if isinstance(event, OnCritEvent):
                    report["performance_metrics"]["crit_count"] += 1

                if isinstance(event, DamageTickEvent):
                    source = f"{event.source.lower()}_dot"
                    report["damage_breakdown"][source] += event.damage
                    report["total_damage"] += event.damage

            # Calculate derived stats
            if duration > 0:
                report["dps"] = report["total_damage"] / duration
            
            if report["performance_metrics"]["total_hits"] > 0:
                report["performance_metrics"]["critical_hit_rate"] = \
                    report["performance_metrics"]["crit_count"] / report["performance_metrics"]["total_hits"]
            
            # Convert Counters to plain dicts for clean output
            report["damage_breakdown"] = dict(report["damage_breakdown"])
            report["performance_metrics"] = dict(report["performance_metrics"])

            return report
    ```

---

#### **Task 4: The Full Simulation & Balancing Loop**

**Objective:** To create the final script that ties all modules together, runs a simulation based on a configuration, and prints the final report. This script is the entry point for all balancing work.

**Implementation Steps:**

1.  **Create `run_simulation.py`:**
    ```python
    # run_simulation.py
    # 1. Imports from all your modules (models, engine, state, events, simulation, etc.)

    # 2. Define Simulation Configuration
    SIM_CONFIG = {
        "duration": 30.0, # seconds
        "attacker_id": "player_1",
        "defender_id": "enemy_1",
        "skill_id": "multi_slash"
    }

    # 3. Define Game Data (This would eventually be loaded from JSON/Godot resources)
    ENTITIES = {
        "player_1": Entity("player_1", EntityStats(base_damage=50, attack_speed=1.2, crit_chance=0.2), rarity="Rare"),
        "enemy_1": Entity("enemy_1", EntityStats(max_health=5000, armor=100))
    }
    SKILLS = {
        "multi_slash": Skill("multi_slash", "Multi-Slash", hits=2, triggers=[
            Trigger("OnHit", {"proc_rate": 0.5}, {"apply_debuff": "Bleed"})
        ])
    }

    # 4. Main Execution Block
    if __name__ == "__main__":
        # --- Setup ---
        event_bus = EventBus()
        state_manager = StateManager()
        logger = CombatLogger(event_bus)

        attacker = ENTITIES[SIM_CONFIG["attacker_id"]]
        defender = ENTITIES[SIM_CONFIG["defender_id"]]
        skill = SKILLS[SIM_CONFIG["skill_id"]]

        state_manager.register_entity(attacker)
        state_manager.register_entity(defender)

        # The BleedHandler now needs to be instantiated to listen to the bus
        bleed_handler = BleedHandler(event_bus, state_manager)
        
        # --- Run ---
        runner = SimulationRunner(attacker, defender, skill, event_bus, state_manager, logger)
        runner.run(duration=SIM_CONFIG["duration"])

        # --- Report ---
        log = logger.get_log()
        reporter = ReportGenerator()
        report_data = reporter.generate(log, SIM_CONFIG["duration"])
        
        # --- Output ---
        import json
        print("\n--- SIMULATION REPORT ---")
        print(json.dumps(report_data, indent=2))

        # --- Balancing Loop ---
        # Now, you would analyze the report. If DPS is too high, you could:
        # 1. Lower player_1's base_damage in the ENTITIES dictionary.
        # 2. Lower the proc_rate of Bleed in the SKILLS dictionary.
        # 3. Re-run the script to see the new results.
    ```

**Expected Outcome:**
Running `run_simulation.py` will:
1.  Set up the combat scenario.
2.  Run a 30-second simulation, printing log messages for procs as it goes.
3.  Finish by printing a clean, structured JSON report detailing DPS, damage breakdown by source (direct hits, crits, Bleed), and other key performance indicators. This provides immediate, actionable feedback for balancing.

---

### **End of Phase 4 Deliverables**

1.  **`events.py` (Updated):** With the new `DamageTickEvent`.
2.  **`state.py` (Updated):** Refactored `StateManager` with the `update` method to handle time.
3.  **`simulation.py` (New):** Contains `CombatLogEntry`, `CombatLogger`, `SimulationRunner`, and `ReportGenerator`.
4.  **`run_simulation.py` (New):** The main entry point script for running simulations and demonstrating the entire system.
5.  **A complete, modular, and testable combat system core,** ready to be ported to GDScript and integrated into your game.