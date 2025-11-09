"""Data models for combat entities and their statistics."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class EntityStats:
    """Static statistics for a combat entity.

    Based on GDD Section 3.0 Dimensions & 5.0 Defenses.
    All values are non-negative and validated on creation.
    """
    # Offensive Stats (GDD 3.0)
    base_damage: float = 10.0
    attack_speed: float = 1.0
    crit_chance: float = 0.05
    crit_damage: float = 1.5
    pierce_ratio: float = 0.01  # GDD 2.1: Min value is 0.01

    # Defensive Stats (GDD 5.0)
    max_health: float = 100.0
    armor: float = 10.0
    resistances: float = 0.0

    def __post_init__(self):
        """Validate stats after initialization."""
        if self.base_damage < 0:
            raise ValueError("base_damage must be non-negative")
        if self.attack_speed <= 0:
            raise ValueError("attack_speed must be positive")
        if not (0 <= self.crit_chance <= 1):
            raise ValueError("crit_chance must be between 0 and 1")
        if self.crit_damage < 1:
            raise ValueError("crit_damage must be >= 1")
        if self.pierce_ratio < 0.01:
            raise ValueError("pierce_ratio must be >= 0.01")
        if self.max_health <= 0:
            raise ValueError("max_health must be positive")
        if self.armor < 0:
            raise ValueError("armor must be non-negative")
        if self.resistances < 0:
            raise ValueError("resistances must be non-negative")


class Entity:
    """Represents a participant in combat.

    An Entity has static stats and a unique identifier.
    Dynamic state (health, buffs, etc.) is managed separately.
    """

    def __init__(self, id: str, stats: EntityStats, name: Optional[str] = None):
        """Initialize an Entity.

        Args:
            id: Unique identifier for this entity
            stats: Static statistics for this entity
            name: Optional display name (defaults to id)
        """
        if not id:
            raise ValueError("Entity id cannot be empty")

        self.id = id
        self.stats = stats
        self.name = name or id

    def __repr__(self) -> str:
        return f"Entity(id='{self.id}', name='{self.name}')"

    def __str__(self) -> str:
        return self.name
