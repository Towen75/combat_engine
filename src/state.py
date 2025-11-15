"""State management for combat entities - tracking dynamic properties like health."""

from dataclasses import dataclass, field
from typing import Dict, Optional, TYPE_CHECKING, List

if TYPE_CHECKING:
    from .events import EventBus

from .models import Entity


@dataclass
class Modifier:
    """Represents a temporary modifier that can affect roll chances or other stats."""
    value: float  # Positive for bonus, negative for penalty
    duration: float  # Time remaining in seconds
    source: str = "unknown"  # What applied this modifier


@dataclass
class Debuff:
    """Represents a damage-over-time effect or debuff applied to an entity."""
    name: str
    stacks: int = 1
    max_duration: float = 10.0
    time_remaining: float = 10.0


@dataclass
class EntityState:
    """Tracks the mutable state of a combat entity.

    This represents the current status of an entity during combat,
    separate from their static stats.
    """
    current_health: float
    is_alive: bool = True
    active_debuffs: Dict[str, Debuff] = field(default_factory=dict)

    # New fields for Phase 1 implementation
    current_resource: float = 0.0  # Current resource amount
    max_resource: float = 100.0    # Store max for clamping resource adds
    roll_modifiers: Dict[str, List[Modifier]] = field(default_factory=dict)  # e.g., {'crit_chance': [Modifier], 'evasion_chance': [...]}
    active_cooldowns: Dict[str, float] = field(default_factory=dict)  # skill_name -> remaining cooldown seconds

    def __post_init__(self):
        """Validate state after initialization."""
        if self.current_health < 0:
            raise ValueError("current_health cannot be negative")
        if self.current_health == 0 and self.is_alive:
            # Auto-correct inconsistent state
            self.is_alive = False
        if self.current_resource < 0:
            raise ValueError("current_resource cannot be negative")
        if self.max_resource <= 0:
            raise ValueError("max_resource must be positive")


class StateManager:
    """Manages the dynamic state of all combat entities.

    This class tracks the current state (health, alive status, etc.) of all
    entities in the combat system, indexed by their unique entity IDs.
    """

    def __init__(self):
        """Initialize an empty state manager."""
        self.states: Dict[str, EntityState] = {}

    def register_entity(self, entity: Entity) -> None:
        """Register an entity and initialize its state.

        Args:
            entity: The entity to register

        Raises:
            ValueError: If entity is already registered
        """
        if entity.id in self.states:
            raise ValueError(f"Entity '{entity.id}' is already registered")

        self.states[entity.id] = EntityState(
            current_health=entity.final_stats.max_health,
            current_resource=entity.final_stats.max_resource,
            max_resource=entity.final_stats.max_resource
        )

    def unregister_entity(self, entity_id: str) -> None:
        """Remove an entity from state tracking.

        Args:
            entity_id: ID of the entity to remove

        Raises:
            KeyError: If entity is not registered
        """
        if entity_id not in self.states:
            raise KeyError(f"Entity '{entity_id}' is not registered")

        del self.states[entity_id]

    def get_state(self, entity_id: str) -> Optional[EntityState]:
        """Retrieve the current state of an entity.

        Args:
            entity_id: ID of the entity to query

        Returns:
            The entity's current state, or None if not registered
        """
        return self.states.get(entity_id)

    def is_registered(self, entity_id: str) -> bool:
        """Check if an entity is registered.

        Args:
            entity_id: ID of the entity to check

        Returns:
            True if the entity is registered, False otherwise
        """
        return entity_id in self.states

    def apply_damage(self, entity_id: str, damage: float) -> float:
        """Apply damage to an entity and update its state.

        Args:
            entity_id: ID of the entity to damage
            damage: Amount of damage to apply (must be non-negative)

        Returns:
            The actual damage applied (0 if entity not found or dead)

        Raises:
            ValueError: If damage is negative
        """
        if damage < 0:
            raise ValueError("Damage cannot be negative")

        state = self.get_state(entity_id)
        if not state or not state.is_alive:
            return 0.0

        # Apply damage (ensure it doesn't go below 0)
        state.current_health = max(0, state.current_health - damage)

        # Handle death
        if state.current_health <= 0:
            state.current_health = 0
            state.is_alive = False

        return damage

    def heal_entity(self, entity_id: str, healing: float, max_health: float) -> float:
        """Heal an entity up to its maximum health.

        Args:
            entity_id: ID of the entity to heal
            healing: Amount of healing to apply
            max_health: Maximum health cap for the entity

        Returns:
            The actual healing applied (0 if entity not found or dead)

        Raises:
            ValueError: If healing is negative
        """
        if healing < 0:
            raise ValueError("Healing cannot be negative")

        state = self.get_state(entity_id)
        if not state or not state.is_alive:
            return 0.0

        old_health = state.current_health
        state.current_health = min(state.current_health + healing, max_health)

        return state.current_health - old_health

    def add_resource(self, entity_id: str, amount: float) -> float:
        """Add resource to an entity, clamping at max_resource.

        Args:
            entity_id: ID of the entity to add resource to
            amount: Amount of resource to add

        Returns:
            The actual resource added (0 if entity not found or dead)

        Raises:
            ValueError: If amount is negative
        """
        if amount < 0:
            raise ValueError("Amount cannot be negative")

        state = self.get_state(entity_id)
        if not state or not state.is_alive:
            return 0.0

        old_resource = state.current_resource
        state.current_resource = min(state.current_resource + amount, state.max_resource)

        return state.current_resource - old_resource

    def spend_resource(self, entity_id: str, amount: float) -> bool:
        """Spend resource from an entity.

        Args:
            entity_id: ID of the entity to spend resource from
            amount: Amount of resource to spend

        Returns:
            True if enough resource was spent, False if insufficient resource

        Raises:
            ValueError: If amount is negative
        """
        if amount < 0:
            raise ValueError("Amount cannot be negative")

        state = self.get_state(entity_id)
        if not state or not state.is_alive:
            return False

        if state.current_resource >= amount:
            state.current_resource -= amount
            return True
        return False

    def set_cooldown(self, entity_id: str, skill_name: str, cooldown_seconds: float) -> None:
        """Set a cooldown for a skill on an entity.

        Args:
            entity_id: ID of the entity
            skill_name: Name of the skill
            cooldown_seconds: Duration of cooldown

        Raises:
            ValueError: If cooldown is negative or invalid entity
        """
        if cooldown_seconds < 0:
            raise ValueError("Cooldown cannot be negative")

        state = self.get_state(entity_id)
        if not state:
            raise ValueError(f"No state found for entity {entity_id}")

        state.active_cooldowns[skill_name] = cooldown_seconds

    def apply_debuff(self, entity_id: str, debuff_name: str, stacks_to_add: int = 1, max_duration: float = 10.0) -> None:
        """Apply or refresh a debuff on an entity.

        Args:
            entity_id: ID of the target entity
            debuff_name: Name of the debuff to apply
            stacks_to_add: Number of stacks to add (default 1)
            max_duration: Maximum duration for the debuff

        Raises:
            ValueError: If invalid parameters or entity not found
        """
        if stacks_to_add <= 0:
            raise ValueError("stacks_to_add must be positive")

        state = self.get_state(entity_id)
        if not state:
            raise ValueError(f"No state found for entity {entity_id}")

        if debuff_name in state.active_debuffs:
            # Refresh existing debuff
            debuff = state.active_debuffs[debuff_name]
            debuff.stacks = min(debuff.stacks + stacks_to_add, 99)  # Cap at 99 stacks
            debuff.time_remaining = max(debuff.time_remaining, max_duration)
        else:
            # Create new debuff
            debuff = Debuff(
                name=debuff_name,
                stacks=stacks_to_add,
                max_duration=max_duration,
                time_remaining=max_duration
            )
            state.active_debuffs[debuff_name] = debuff

    def get_all_states(self) -> Dict[str, EntityState]:
        """Get a copy of all entity states.

        Returns:
            Dictionary mapping entity IDs to their states
        """
        import copy
        return copy.deepcopy(self.states)

    def reset(self) -> None:
        """Clear all entity states."""
        self.states.clear()

    def __len__(self) -> int:
        """Return the number of registered entities."""
        return len(self.states)

    def __contains__(self, entity_id: str) -> bool:
        """Check if an entity ID is registered."""
        return entity_id in self.states

    def update(self, delta_time: float, event_bus: Optional["EventBus"] = None) -> None:
        """Update temporary effects, cooldowns, and damage-over-time effects for all entities.

        Args:
            delta_time: Time elapsed since last update in seconds
            event_bus: Optional event bus to dispatch DamageTickEvent
        """
        from .events import DamageTickEvent

        entities_to_remove = []

        for entity_id, state in self.states.items():
            if not state.is_alive:
                continue

            # Update active cooldowns
            expired_cooldowns = []
            for skill_name, remaining in state.active_cooldowns.items():
                state.active_cooldowns[skill_name] = max(0, remaining - delta_time)
                if state.active_cooldowns[skill_name] <= 0:
                    expired_cooldowns.append(skill_name)

            for skill_name in expired_cooldowns:
                del state.active_cooldowns[skill_name]

            # Update roll modifiers
            expired_modifiers = []
            for roll_type in list(state.roll_modifiers.keys()):
                new_mods = []
                for mod in state.roll_modifiers[roll_type]:
                    mod.duration = max(0, mod.duration - delta_time)
                    if mod.duration > 0:
                        new_mods.append(mod)
                state.roll_modifiers[roll_type] = new_mods
                if not state.roll_modifiers[roll_type]:
                    expired_modifiers.append(roll_type)

            for roll_type in expired_modifiers:
                del state.roll_modifiers[roll_type]

            # Update DoTs
            debuffs_to_remove = []

            for debuff_name, debuff in state.active_debuffs.items():
                # Decrease time remaining
                debuff.time_remaining -= delta_time

                # Check if it's time to tick (every 1 second for simplicity)
                # In a real implementation, this could be configurable per debuff type
                tick_interval = 1.0  # seconds between ticks
                ticks_this_update = int(delta_time / tick_interval)

                if ticks_this_update > 0:
                    # Calculate damage per tick (example: 5 damage per stack per tick)
                    damage_per_tick = 5.0 * debuff.stacks

                    for _ in range(ticks_this_update):
                        actual_damage = self.apply_damage(entity_id, damage_per_tick)

                        # Dispatch DamageTickEvent if event bus is provided
                        if event_bus and actual_damage > 0:
                            # Get the entity object (this assumes we have access to it)
                            # For now, we'll create a minimal entity representation
                            from .models import Entity, EntityStats
                            target_entity = Entity(
                                id=entity_id,
                                base_stats=EntityStats(),  # Minimal stats for event
                                name=entity_id
                            )

                            tick_event = DamageTickEvent(
                                target=target_entity,
                                effect_name=debuff_name,
                                damage_dealt=actual_damage,
                                stacks=debuff.stacks
                            )
                            event_bus.dispatch(tick_event)

                # Remove expired debuffs
                if debuff.time_remaining <= 0:
                    debuffs_to_remove.append(debuff_name)

            # Remove expired debuffs
            for debuff_name in debuffs_to_remove:
                del state.active_debuffs[debuff_name]

            # Check if entity died from DoT
            if not state.is_alive:
                entities_to_remove.append(entity_id)

        # Note: In a real implementation, you might want to handle entity removal
        # or dispatch death events here, but for simulation purposes we'll keep them
