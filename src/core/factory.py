"""Entity Factory for creating entities from templates."""

from typing import Optional
from src.core.models import Entity, EntityStats


class EntityFactory:
    """Factory for creating Entity instances with consistent configuration."""

    def __init__(self):
        """Initialize the entity factory."""
        # In Phase B, this would load from entity templates CSV
        # For now, placeholder for future template support
        pass

    def create(self, entity_id: str, base_stats: Optional[EntityStats] = None, instance_id: Optional[str] = None, loot_table_id: Optional[str] = None) -> Entity:
        """Create an entity with the specified configuration.

        Args:
            entity_id: The template/entity identifier
            base_stats: Stats for the entity (defaults to basic stats)
            instance_id: Optional unique instance identifier
            loot_table_id: Optional loot table this entity drops from

        Returns:
            Configured Entity instance
        """
        if base_stats is None:
            base_stats = EntityStats()

        # In Phase B, template lookup would happen here
        # For now, direct entity creation with provided loot_table_id
        real_id = instance_id or f"{entity_id}_instance"

        return Entity(
            id=real_id,
            base_stats=base_stats,
            name=entity_id.title(),  # Simple name derivation
            loot_table_id=loot_table_id
        )
