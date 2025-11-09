"""State management for combat entities - tracking dynamic properties like health."""

from dataclasses import dataclass
from typing import Dict, Optional
from .models import Entity


@dataclass
class EntityState:
    """Tracks the mutable state of a combat entity.

    This represents the current status of an entity during combat,
    separate from their static stats.
    """
    current_health: float
    is_alive: bool = True

    def __post_init__(self):
        """Validate state after initialization."""
        if self.current_health < 0:
            raise ValueError("current_health cannot be negative")
        if self.current_health == 0 and self.is_alive:
            # Auto-correct inconsistent state
            self.is_alive = False


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

        self.states[entity.id] = EntityState(current_health=entity.stats.max_health)

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

        # Apply damage
        state.current_health -= damage

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
