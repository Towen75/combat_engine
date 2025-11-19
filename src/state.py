"""State management for combat entities - tracking dynamic properties like health."""

from dataclasses import dataclass, field
from typing import Dict, Optional, TYPE_CHECKING, List
import uuid

from .models import Entity, EffectInstance
from .events import (
    EventBus, 
    EntitySpawnEvent, 
    EntityDeathEvent, 
    EntityDespawnEvent, 
    EntityActivateEvent,
    EffectApplied,
    EffectTick,
    EffectExpired
)

@dataclass
class Modifier:
    """Represents a temporary modifier that can affect roll chances or other stats."""
    value: float
    duration: float
    source: str = "unknown"


@dataclass
class Debuff:
    """Represents a damage-over-time effect or debuff applied to an entity."""
    name: str
    stacks: int = 1
    max_duration: float = 10.0
    time_remaining: float = 10.0
    accumulator: float = 0.0
    tick_interval: float = 1.0
    damage_per_tick: float = 5.0


@dataclass
class EntityState:
    """Tracks the mutable state of a combat entity."""
    entity: Entity
    current_health: float
    is_alive: bool = True
    active_debuffs: Dict[str, Debuff] = field(default_factory=dict)
    current_resource: float = 0.0
    max_resource: float = 100.0
    roll_modifiers: Dict[str, List[Modifier]] = field(default_factory=dict)
    active_cooldowns: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        """Validate state after initialization."""
        if self.current_health < 0:
            raise ValueError("current_health cannot be negative")
        if self.current_health == 0 and self.is_alive:
            self.is_alive = False
        if self.current_resource < 0:
            raise ValueError("current_resource cannot be negative")
        if self.max_resource <= 0:
            raise ValueError("max_resource must be positive")


class StateManager:
    """Centralized manager for entity state and lifecycle.

    Features:
    - Enforces strict entity registration (KeyError on unknown IDs).
    - Manages health, resources, cooldowns, and effects.
    - Dispatches lifecycle events (Spawn, Death, Despawn) via EventBus.
    """

    def __init__(self, event_bus: Optional["EventBus"] = None):
        """Initialize the state manager.

        Args:
            event_bus: Optional EventBus for dispatching lifecycle events.
        """
        self.event_bus = event_bus
        self.states: Dict[str, EntityState] = {}
        # Track active EffectInstances (normalized effect system)
        self._active_effects: Dict[str, Dict[str, "EffectInstance"]] = {}

    # ============================================================================
    # Entity Lifecycle Management
    # ============================================================================

    def add_entity(self, entity: Entity) -> None:
        """Register an entity for state management."""
        if entity.id in self.states:
            raise ValueError(f"Entity '{entity.id}' is already registered")

        self.states[entity.id] = EntityState(
            entity=entity,  # <--- Store the reference
            current_health=entity.final_stats.max_health,
            current_resource=entity.final_stats.max_resource,
            max_resource=entity.final_stats.max_resource
        )

        if self.event_bus:
            self.event_bus.dispatch(EntitySpawnEvent(entity=entity))

    def activate_entity(self, entity_id: str) -> None:
        """Activate an entity, signaling it is ready for combat.
        
        Triggers EntityActivateEvent.
        """
        state = self.get_state(entity_id)
        
        if self.event_bus:
            self.event_bus.dispatch(EntityActivateEvent(entity=state.entity))

    def remove_entity(self, entity_id: str) -> None:
        """Remove an entity and its state from the system.
        
        Triggers EntityDespawnEvent if EventBus is available.
        """
        if entity_id not in self.states:
            raise KeyError(f"Entity '{entity_id}' is not registered")
        
        del self.states[entity_id]
        
        if entity_id in self._active_effects:
            del self._active_effects[entity_id]

        if self.event_bus:
            self.event_bus.dispatch(EntityDespawnEvent(entity_id=entity_id))

    def get_state(self, entity_id: str) -> EntityState:
        """Get entity state directly."""
        state = self.states.get(entity_id)
        if state is None:
            raise KeyError(f"Entity '{entity_id}' not registered - call add_entity() first")
        return state

    def is_registered(self, entity_id: str) -> bool:
        """Check if entity is registered."""
        return entity_id in self.states

    def reset_system(self) -> None:
        """Clear all states and effects. Used for simulation resets."""
        self.states.clear()
        self._active_effects.clear()

    # ============================================================================
    # Core State Operations
    # ============================================================================

    def apply_damage(self, entity_id: str, damage: float) -> float:
        """Apply damage to an entity and return actual damage applied.
        
        Automatically triggers EntityDeathEvent if health reaches 0.
        """
        if damage < 0:
            return 0.0

        state = self.get_state(entity_id)
        
        # Don't damage dead entities
        if not state.is_alive:
            return 0.0

        old_health = state.current_health
        state.current_health = max(0, state.current_health - damage)
        actual_damage = old_health - state.current_health

        # Handle Death
        if state.current_health <= 0:
            state.current_health = 0
            was_alive = state.is_alive
            state.is_alive = False
            
            if was_alive and self.event_bus:
                self.event_bus.dispatch(EntityDeathEvent(entity_id=entity_id))

        return actual_damage

    def set_health(self, entity_id: str, health: float) -> None:
        """Directly set entity health (useful for testing or specific mechanics)."""
        state = self.get_state(entity_id)
        if health < 0:
            health = 0
        state.current_health = health
        state.is_alive = health > 0

    def set_resource(self, entity_id: str, amount: float) -> None:
        """Directly set entity resource."""
        state = self.get_state(entity_id)
        state.current_resource = max(0, min(amount, state.max_resource))
    
    def spend_resource(self, entity_id: str, amount: float) -> bool:
        """Try to spend resource. Returns True if successful."""
        state = self.get_state(entity_id)
        if state.current_resource >= amount:
            state.current_resource -= amount
            return True
        return False
        
    def add_resource(self, entity_id: str, amount: float) -> None:
        """Add resource, clamped to max."""
        state = self.get_state(entity_id)
        state.current_resource = min(state.current_resource + amount, state.max_resource)

    def set_cooldown(self, entity_id: str, skill_name: str, cooldown_seconds: float) -> None:
        """Set a skill cooldown."""
        state = self.get_state(entity_id)
        state.active_cooldowns[skill_name] = cooldown_seconds

    def get_current_health(self, entity_id: str) -> float:
        state = self.get_state(entity_id)
        return state.current_health

    def get_current_resource(self, entity_id: str) -> float:
        state = self.get_state(entity_id)
        return state.current_resource

    def get_is_alive(self, entity_id: str) -> bool:
        state = self.get_state(entity_id)
        return state.is_alive

    def get_cooldown_remaining(self, entity_id: str, skill_id: str) -> float:
        state = self.get_state(entity_id)
        return state.active_cooldowns.get(skill_id, 0.0)

    # ============================================================================
    # Effect Management
    # ============================================================================

    def apply_effect(self, entity_id: str, effect: "EffectInstance") -> Dict[str, any]:
        """Apply an EffectInstance to an entity."""
        # Ensure entity exists (will raise KeyError if not)
        _ = self.get_state(entity_id)

        if entity_id not in self._active_effects:
            self._active_effects[entity_id] = {}

        # Check for existing effect and stack/refresh
        existing = self._active_effects[entity_id].get(effect.definition_id)

        if existing:
            existing.stacks += effect.stacks
            existing.time_remaining = max(existing.time_remaining, effect.time_remaining)
            result = {"success": True, "action": "refreshed", "new_stacks": existing.stacks}
        else:
            self._active_effects[entity_id][effect.definition_id] = effect
            result = {"success": True, "action": "applied", "new_stacks": effect.stacks}

        if self.event_bus:
            self.event_bus.dispatch(EffectApplied(entity_id=entity_id, effect=effect))

        return result

    def update(self, delta_time: float, event_bus: Optional["EventBus"] = None) -> None:
        """Advance simulation time: process cooldowns and active effects."""
        bus = self.event_bus or event_bus

        # 1. Update Entities (Cooldowns)
        for state in self.states.values():
            if not state.is_alive:
                continue
            
            # Decrement cooldowns
            for skill_name in list(state.active_cooldowns.keys()):
                state.active_cooldowns[skill_name] -= delta_time
                if state.active_cooldowns[skill_name] <= 0:
                    del state.active_cooldowns[skill_name]

        # 2. Update Effects (Duration & Ticks)
        for entity_id, effects in list(self._active_effects.items()):
            if entity_id not in self.states:
                continue

            state = self.states[entity_id]
            if not state.is_alive:
                continue

            effects_to_remove = []

            for effect_id, effect in effects.items():
                # Decrement duration
                effect.time_remaining = max(0, effect.time_remaining - delta_time)

                # Process ticks
                if effect.tick_interval > 0 and effect.value > 0:
                    effect.accumulator += delta_time
                    
                    while effect.accumulator >= effect.tick_interval:
                        effect.accumulator -= effect.tick_interval
                        
                        # Calculate tick damage
                        damage = effect.value * effect.stacks
                        if damage > 0:
                            actual_damage = self.apply_damage(entity_id, damage)
                            
                            if bus and actual_damage > 0:
                                bus.dispatch(EffectTick(
                                    entity_id=entity_id, 
                                    effect=effect, 
                                    damage_applied=actual_damage,
                                    stacks=effect.stacks
                                ))

                # Check Expiration
                if effect.time_remaining <= 0 and effect.expires_on_zero:
                    effects_to_remove.append(effect_id)
                    if bus:
                        bus.dispatch(EffectExpired(entity_id=entity_id, effect=effect))

            # Remove expired effects
            for effect_id in effects_to_remove:
                del effects[effect_id]

        # Cleanup empty dictionaries
        empty_keys = [k for k, v in self._active_effects.items() if not v]
        for k in empty_keys:
            del self._active_effects[k]

    def remove_effect(self, entity_id: str, effect_id: str) -> bool:
        """Remove a specific effect instance."""
        if entity_id in self._active_effects and effect_id in self._active_effects[entity_id]:
            del self._active_effects[entity_id][effect_id]
            return True
        return False
    
    def iter_effects(self, entity_id: str) -> List["EffectInstance"]:
        """Iterator for entity's active effects."""
        if entity_id not in self.states:
             raise KeyError(f"Entity '{entity_id}' not registered")
        return list(self._active_effects.get(entity_id, {}).values())

    def get_active_effects(self, entity_id: str) -> List["EffectInstance"]:
        """Return list of active effects (alias for iter_effects)."""
        return self.iter_effects(entity_id)
    
    def get_effect_stacks(self, entity_id: str, effect_id: str) -> int:
        """Get current stacks of a specific effect."""
        if entity_id in self._active_effects and effect_id in self._active_effects[entity_id]:
            return self._active_effects[entity_id][effect_id].stacks
        return 0
        
    def clear_all_effects(self, entity_id: str) -> int:
        """Clear all effects from an entity."""
        if entity_id in self._active_effects:
            count = len(self._active_effects[entity_id])
            del self._active_effects[entity_id]
            return count
        return 0

    # ============================================================================
    # Aliases / Helpers
    # ============================================================================

    def apply_debuff(self, entity_id: str, debuff_name: str, stacks_to_add: int = 1, max_duration: float = 10.0) -> None:
        """Convenience wrapper to apply a basic debuff as an EffectInstance."""
        effect = EffectInstance(
            id=str(uuid.uuid4()),
            definition_id=debuff_name,
            source_id="helper",
            time_remaining=max_duration,
            tick_interval=1.0,
            stacks=stacks_to_add,
            value=5.0 # Default base damage for helper usage
        )
        self.apply_effect(entity_id, effect)

    # Aliases for API compatibility
    register_entity = add_entity
    unregister_entity = remove_entity
    tick = update
    add_or_refresh_debuff = apply_debuff
    
    def get_all_states(self) -> Dict[str, EntityState]:
        return self.states

    def __len__(self) -> int:
        return len(self.states)

    def __contains__(self, entity_id: str) -> bool:
        return entity_id in self.states