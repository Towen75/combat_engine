"""Data models for combat entities and their statistics."""

from dataclasses import dataclass, field
from typing import Optional, List, Literal, Dict

# Rarity to critical hit tier mapping
RARITY_TO_CRIT_TIER = {
    "Common": 1,
    "Uncommon": 1,
    "Rare": 2,
    "Epic": 2,
    "Legendary": 3,
    "Mythic": 3
}


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

    An Entity has base stats, equipment that modifies final stats, and a unique identifier.
    Dynamic state (health, buffs, etc.) is managed separately.
    """

    def __init__(self, id: str, base_stats: EntityStats, name: Optional[str] = None, rarity: str = "Common"):
        """Initialize an Entity.

        Args:
            id: Unique identifier for this entity
            base_stats: Base statistics for this entity (before equipment modifiers)
            name: Optional display name (defaults to id)
            rarity: Character rarity tier (Common, Uncommon, Rare, Epic, Legendary, Mythic)
        """
        if not id:
            raise ValueError("Entity id cannot be empty")

        if rarity not in RARITY_TO_CRIT_TIER:
            raise ValueError(f"Invalid rarity: {rarity}. Must be one of {list(RARITY_TO_CRIT_TIER.keys())}")

        self.id = id
        self.base_stats = base_stats
        self.name = name or id
        self.rarity = rarity
        self.equipment: Dict[str, Item] = {}
        self.final_stats = self.calculate_final_stats()

    def __repr__(self) -> str:
        return f"Entity(id='{self.id}', name='{self.name}')"

    def __str__(self) -> str:
        return self.name

    def get_crit_tier(self) -> int:
        """Get the critical hit tier based on entity rarity.

        Returns:
            Critical hit tier (1, 2, or 3)
        """
        return RARITY_TO_CRIT_TIER.get(self.rarity, 1)

    def equip_item(self, item: "Item") -> None:
        """Equip an item to its designated slot and recalculate stats.

        Args:
            item: The item to equip
        """
        self.equipment[item.slot] = item
        self.recalculate_stats()

    def recalculate_stats(self) -> None:
        """Public method to trigger stat recalculation."""
        self.final_stats = self.calculate_final_stats()

    def calculate_final_stats(self) -> EntityStats:
        """Calculate the final stats by applying equipment modifiers.

        Order of operations: Multipliers first, then flats (revised from GDD 2.1).
        Validates that final stats meet minimum requirements.

        Returns:
            EntityStats with final calculated values
        """
        # Start with a copy of the base stats
        final_stats_dict = self.base_stats.__dict__.copy()

        # 1. Apply all MULTIPLIER affixes first
        for item in self.equipment.values():
            for affix in item.affixes:
                if affix.mod_type == "multiplier":
                    # Assumes value is percentage (e.g., 0.2 for 20% increase)
                    final_stats_dict[affix.stat_affected] *= (1 + affix.value)

        # 2. Apply all FLAT affixes second
        for item in self.equipment.values():
            for affix in item.affixes:
                if affix.mod_type == "flat":
                    final_stats_dict[affix.stat_affected] += affix.value

        # Create new EntityStats object from modified dictionary
        final_stats = EntityStats(**final_stats_dict)

        # Additional validation to ensure final stats are valid
        if final_stats.base_damage < 0:
            final_stats.base_damage = 0
        if final_stats.attack_speed <= 0:
            final_stats.attack_speed = 0.1  # Minimum speed
        if final_stats.crit_chance < 0:
            final_stats.crit_chance = 0
        if final_stats.crit_chance > 1:
            final_stats.crit_chance = 1
        if final_stats.crit_damage < 1:
            final_stats.crit_damage = 1
        if final_stats.pierce_ratio < 0.01:
            final_stats.pierce_ratio = 0.01
        if final_stats.max_health <= 0:
            final_stats.max_health = 1
        if final_stats.armor < 0:
            final_stats.armor = 0
        if final_stats.resistances < 0:
            final_stats.resistances = 0

        return final_stats


@dataclass
class RolledAffix:
    affix_id: str
    stat_affected: str
    mod_type: Literal['flat', 'multiplier']
    description: str
    base_value: float
    value: float


@dataclass
class Item:
    instance_id: str
    base_id: str
    name: str
    slot: str
    rarity: str
    quality_tier: str
    quality_roll: int
    affixes: List[RolledAffix] = field(default_factory=list)
