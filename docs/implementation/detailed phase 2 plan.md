### **Detailed Plan: Phase 2 - Adding Layers: Crits & Events**

**Objective:** To expand the core damage calculation to include the multi-tiered critical hit system and implement the `EventBus`, which will allow secondary effects (like Damage over Time) to be triggered from combat actions.

---

#### **Task 1: The EventBus - The System's Nervous System**

**Objective:** Create a central dispatcher to broadcast game events. This decouples the cause of an event (like a hit) from its consequences (applying a debuff), making the system incredibly modular.

**Key Components/Classes:**
*   `Event` (Base Class)
*   `OnHitEvent`, `OnCritEvent` (Specific Event Classes)
*   `EventBus` (The Dispatcher)

**Implementation Steps:**

1.  **Define the `Event` Classes:** These are simple data containers that hold information about what just happened.
    ```python
    # in a new file, e.g., events.py
    from dataclasses import dataclass
    from models import Entity # Import from Phase 1

    @dataclass
    class Event:
        pass # Base class for all events

    @dataclass
    class OnHitEvent(Event):
        attacker: Entity
        defender: Entity
        damage_dealt: float
        is_crit: bool = False
    
    @dataclass
    class OnCritEvent(Event):
        hit_event: OnHitEvent # Contains all the context of the original hit
    ```

2.  **Create the `EventBus`:** This class uses the Observer pattern. It maintains a list of "listeners" (subscribers) for each event type.
    ```python
    from collections import defaultdict

    class EventBus:
        def __init__(self):
            # A dictionary mapping event types to a list of listener functions
            self.listeners = defaultdict(list)

        def subscribe(self, event_type: type, listener):
            """Adds a listener function for a specific event type."""
            self.listeners[event_type].append(listener)

        def dispatch(self, event: Event):
            """Calls all listener functions for the given event."""
            for listener in self.listeners[event.__class__]:
                listener(event)
    ```

**Testing Strategy:**
*   **Unit Test 1.1:** Test that a listener function is correctly added via `subscribe`.
*   **Unit Test 1.2:** `dispatch` an `OnHitEvent` and assert that the subscribed listener function was called with the correct event data.
*   **Unit Test 1.3:** Test that a listener subscribed to `OnHitEvent` does *not* get called when an `OnCritEvent` is dispatched.

---

#### **Task 2: Refactoring the Combat Engine for Crit Tiers**

**Objective:** Modify the `CombatEngine` to support injecting the critical hit multiplier at different stages of the calculation, as defined in your GDD. This requires breaking the single `resolve_hit` function into a pipeline.

**Key Components/Classes:**
*   `HitContext` (Data Class for the pipeline)
*   `CombatEngine` (Refactored)

**Implementation Steps:**

1.  **Create `HitContext`:** This object will be passed through the damage calculation pipeline, accumulating values at each step.
    ```python
    # in engine.py
    @dataclass
    class HitContext:
        attacker: Entity
        defender: Entity
        base_damage: float
        pre_mitigation_damage: float = 0.0
        mitigated_damage: float = 0.0
        final_damage: float = 0.0
        is_crit: bool = False
    ```

2.  **Refactor `CombatEngine` into a Pipeline:**
    ```python
    # in engine.py
    import random
    from models import Entity

    class CombatEngine:
        @staticmethod
        def resolve_hit(attacker: Entity, defender: Entity) -> HitContext:
            """
            Orchestrates the full damage calculation pipeline.
            Returns a HitContext object with the final results.
            """
            # --- 1. Initial Setup ---
            ctx = HitContext(attacker=attacker, defender=defender, base_damage=attacker.stats.base_damage)
            
            # --- 2. Critical Hit Check ---
            if random.random() < attacker.stats.crit_chance:
                ctx.is_crit = True

            # --- 3. Pre-Mitigation Damage Calculation ---
            # For now, this is just base damage. Phase 3 will add flat bonuses here.
            ctx.pre_mitigation_damage = ctx.base_damage
            
            # Apply Tier 1/2 crits (Base/Pre-Pierce)
            if ctx.is_crit:
                CombatEngine._apply_pre_pierce_crit(ctx)

            # --- 4. Mitigation Calculation (The GDD formula) ---
            pre_pierce_damage = ctx.pre_mitigation_damage - defender.stats.armor
            pierced_damage = ctx.pre_mitigation_damage * attacker.stats.pierce_ratio
            ctx.mitigated_damage = max(0, max(pre_pierce_damage, pierced_damage))

            # --- 5. Final Damage & Post-Mitigation Crits ---
            # Phase 3 will add final multipliers here.
            ctx.final_damage = ctx.mitigated_damage
            
            # Apply Tier 3 crits (Post-Pierce)
            if ctx.is_crit:
                CombatEngine._apply_post_pierce_crit(ctx)
            
            return ctx

        @staticmethod
        def _apply_pre_pierce_crit(ctx: HitContext):
            # TIER 1 (Base Crit) only affects base_damage, not yet implemented here. This is a simplification for now.
            # TIER 2 (Enhanced Crit) affects all pre-mitigation damage.
            if ctx.attacker.get_crit_tier() == 2: # get_crit_tier() will be added to Entity
                ctx.pre_mitigation_damage *= ctx.attacker.stats.crit_damage

        @staticmethod
        def _apply_post_pierce_crit(ctx: HitContext):
            # TIER 3 (True Crit) affects post-mitigation damage.
            if ctx.attacker.get_crit_tier() == 3:
                # We need to re-calculate mitigated damage using the crit-boosted pre_mitigation_damage
                crit_pre_mit_damage = ctx.base_damage * ctx.attacker.stats.crit_damage
                pre_pierce_damage = crit_pre_mit_damage - ctx.defender.stats.armor
                pierced_damage = crit_pre_mit_damage * ctx.attacker.stats.pierce_ratio
                
                # Update final damage directly based on new calculation
                ctx.final_damage = max(0, max(pre_pierce_damage, pierced_damage))
    ```

---

#### **Task 3: Integrating Crits and Events**

**Objective:** Update the `Entity` class and the main logic flow to handle crits and dispatch events.

**Implementation Steps:**

1.  **Update `Entity` and `EntityStats`:**
    *   Add `rarity: str = "Common"` to `Entity`.
    *   Add `crit_tier` mapping and a helper method to the `Entity` class.
    ```python
    # in models.py
    RARITY_TO_CRIT_TIER = {"Common": 1, "Uncommon": 1, "Rare": 2, "Epic": 2, "Legendary": 3, "Mythic": 3}

    class Entity:
        def __init__(self, id: str, stats: EntityStats, rarity: str = "Common"):
            self.id = id
            self.stats = stats
            self.rarity = rarity

        def get_crit_tier(self) -> int:
            return RARITY_TO_CRIT_TIER.get(self.rarity, 1)
    ```

2.  **Update Main Logic to Dispatch Events:** Create a new function that takes the `EventBus` and `StateManager` to tie everything together.
    ```python
    # in a new main script, e.g., run_phase2_test.py
    def process_attack(attacker: Entity, defender: Entity, event_bus: EventBus, state_manager: StateManager):
        hit_context = CombatEngine.resolve_hit(attacker, defender)
        damage = hit_context.final_damage
        
        state_manager.apply_damage(defender.id, damage)
        
        # Dispatch events
        hit_event = OnHitEvent(
            attacker=attacker, 
            defender=defender, 
            damage_dealt=damage,
            is_crit=hit_context.is_crit
        )
        event_bus.dispatch(hit_event)
        
        if hit_context.is_crit:
            crit_event = OnCritEvent(hit_event=hit_event)
            event_bus.dispatch(crit_event)
    ```

---

#### **Task 4: Implementing Effect Handlers (DoTs)**

**Objective:** Extend the `StateManager` to track debuffs and create the first `EffectHandler` for Bleed.

**Implementation Steps:**

1.  **Create a `Debuff` Class and Extend `EntityState`:**
    ```python
    # in state.py
    @dataclass
    class Debuff:
        name: str
        stacks: int = 1
        max_duration: float = 10.0
        time_remaining: float = 10.0
    
    @dataclass
    class EntityState:
        current_health: float
        is_alive: bool = True
        active_debuffs: dict[str, Debuff] = field(default_factory=dict) # Maps debuff name to Debuff object
    ```

2.  **Extend `StateManager` for Debuffs:** Add logic for the "Combined Refresh Model".
    ```python
    # in state.py
    class StateManager:
        # ... (previous methods) ...
        def add_or_refresh_debuff(self, entity_id: str, debuff_name: str, stacks_to_add: int = 1, duration: float = 10.0):
            state = self.get_state(entity_id)
            if not state or not state.is_alive:
                return

            if debuff_name in state.active_debuffs:
                # Refresh duration and add stacks
                debuff = state.active_debuffs[debuff_name]
                debuff.stacks += stacks_to_add
                debuff.time_remaining = duration
            else:
                # Apply new debuff
                state.active_debuffs[debuff_name] = Debuff(name=debuff_name, stacks=stacks_to_add, max_duration=duration, time_remaining=duration)
    ```

3.  **Create the `BleedHandler`:** This is our first "listener".
    ```python
    # in a new file, effect_handlers.py
    import random

    class BleedHandler:
        def __init__(self, event_bus: EventBus, state_manager: StateManager, proc_rate: float = 0.5):
            self.state_manager = state_manager
            self.proc_rate = proc_rate
            event_bus.subscribe(OnHitEvent, self.handle_on_hit)

        def handle_on_hit(self, event: OnHitEvent):
            """Checks proc rate and applies Bleed if successful."""
            if random.random() < self.proc_rate:
                print(f"    -> Bleed proc'd on {event.defender.id}!")
                self.state_manager.add_or_refresh_debuff(
                    entity_id=event.defender.id,
                    debuff_name="Bleed",
                    stacks_to_add=1,
                    duration=5.0 # Example duration
                )
    ```

---

#### **Task 5: Integration Test**

**Objective:** Create a script to simulate a series of attacks and verify that crits and DoT applications are working.

```python
# in run_phase2_test.py

# --- Setup ---
event_bus = EventBus()
state_manager = StateManager()

# Create entities
attacker_stats = EntityStats(crit_chance=0.50, crit_damage=2.0)
attacker = Entity(id="player_1