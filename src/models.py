"""Data models for combat entities and their statistics."""

from dataclasses import dataclass, field
from typing import Optional, List, Literal, Dict, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .engine import HitContext
    from .events import Event, EffectApplied, EffectExpired
    from .skills import Trigger

from .data.typed_models import Rarity

# Rarity to critical hit tier mapping
RARITY_TO_CRIT_TIER = {
    Rarity.COMMON: 1,
    Rarity.UNCOMMON: 1,
    Rarity.RARE: 2,
    Rarity.EPIC: 2,
    Rarity.LEGENDARY: 3,
    Rarity.MYTHIC: 3
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
    damage_multiplier: float = 1.0  # Global damage multiplier

    # Defensive Stats (GDD 5.0)
    max_health: float = 100.0
    armor: float = 10.0
    resistances: float = 0.0
    
    # Utility / Sustain Stats
    life_steal: float = 0.0
    movement_speed: float = 1.0
    damage_over_time: float = 1.0  # Multiplier for DoT damage

    # New Evasion System Stats (IP 2.1)
    evasion_chance: float = 0.0  # Max 0.75
    dodge_chance: float = 0.0

    # New Block System Stats (IP 2.1)
    block_chance: float = 0.0
    block_amount: float = 0.0

    # Active Resource System Stats (IP 2.3)
    max_resource: float = 100.0
    resource_on_hit: float = 2.0
    resource_on_kill: float = 10.0

    # Cooldown Reduction Stat (IP 2.3)
    cooldown_reduction: float = 0.0

    def __post_init__(self) -> None:
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
        if not (0 <= self.evasion_chance <= 0.75):
            raise ValueError("evasion_chance must be between 0 and 0.75")
        if not (0 <= self.dodge_chance <= 1):
            raise ValueError("dodge_chance must be between 0 and 1")
        if not (0 <= self.block_chance <= 1):
            raise ValueError("block_chance must be between 0 and 1")
        if self.block_amount < 0:
            raise ValueError("block_amount must be non-negative")
        if self.max_resource <= 0:
            raise ValueError("max_resource must be positive")
        if self.resource_on_hit < 0:
            raise ValueError("resource_on_hit must be non-negative")
        if self.resource_on_kill < 0:
            raise ValueError("resource_on_kill must be non-negative")
        if self.cooldown_reduction < 0:
            raise ValueError("cooldown_reduction must be non-negative")


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

        try:
            self.rarity = Rarity(rarity)
        except ValueError:
            valid_rarities = [r.value for r in Rarity]
            raise ValueError(f"Invalid rarity: {rarity}. Must be one of {valid_rarities}")

        self.id = id
        self.base_stats = base_stats
        self.name = name or id
        self.equipment: Dict[str, Item] = {}
        self.active_triggers: List["Trigger"] = []  # For affix reactive effects
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

        Phase 3 Enhanced: Supports dual-stat, scaling, and complex effect affixes.
        Order of operations: Multipliers first, then flats (revised from GDD 2.1).
        Also aggregates reactive triggers from affixes.
        Validates that final stats meet minimum requirements and validates affix stat names.

        Returns:
            EntityStats with final calculated values
        """
        from .skills import Trigger
        import math

        # Start with a copy of the base stats
        final_stats_dict = self.base_stats.__dict__.copy()

        # Get valid stat names for validation
        valid_stat_names = set(final_stats_dict.keys())

        # Clear existing triggers for recalculation
        self.active_triggers.clear()

        # Calculate character power level for scaling affixes (simple sum of offensive/defensive stats)
        power_level = (
            self.base_stats.base_damage +
            self.base_stats.max_health * 0.1 +
            self.base_stats.armor * 2 +
            (self.base_stats.crit_chance * 100) +
            (self.base_stats.pierce_ratio * 1000)
        ) / 100.0  # Normalize to reasonable scale

        # 1. Apply all MULTIPLIER affixes first
        for item in self.equipment.values():
            for affix in item.affixes:
                # Handle dual-stat affixes (applies to multiple stats)
                stats_affected = affix.stat_affected.split(';') if affix.dual_stat else [affix.stat_affected]
                mod_types = affix.mod_type.split(';') if affix.dual_stat else [affix.mod_type]
                values = [affix.value]

                # For dual-stat, get the second value from the dual_value field
                if affix.dual_stat and affix.dual_value is not None:
                    values.append(affix.dual_value)

                # Apply scaling power multiplier if this is a scaling affix
                scaling_multiplier = 1.0
                if affix.scaling_power:
                    scaling_multiplier = 1.0 + math.log(power_level + 1) * 0.1  # Gentle scaling curve

                for i, stat_name in enumerate(stats_affected):
                    if not stat_name or stat_name not in valid_stat_names:
                        continue

                    mod_type = mod_types[min(i, len(mod_types)-1)]
                    value = values[min(i, len(values)-1)]

                    if mod_type == "multiplier":
                        # Apply value and scaling
                        final_value = value * scaling_multiplier
                        final_stats_dict[stat_name] *= (1 + final_value)

                # Aggregate reactive triggers from affixes
                if affix.trigger_event and affix.proc_rate and affix.trigger_result:
                    # Parse trigger_result - supports both simple debuff names and complex effects like "reflect_damage:0.3"
                    result_dict = {}

                    # Check if it's a complex effect with colon separator (e.g., "reflect_damage:0.3")
                    if ':' in affix.trigger_result:
                        effect_name, effect_value = affix.trigger_result.split(':', 1)
                        try:
                            # Try to parse as float for numerical values
                            result_dict[effect_name] = float(effect_value)
                        except ValueError:
                            # If not a number, store as string
                            result_dict[effect_name] = effect_value
                    else:
                        # Simple debuff name - use legacy format for backward compatibility
                        result_dict["apply_debuff"] = affix.trigger_result

                    # Add common trigger metadata
                    result_dict["duration"] = float(affix.trigger_duration or 10.0)
                    result_dict["stacks_max"] = int(affix.stacks_max or 99)

                    trigger = Trigger(
                        event=affix.trigger_event,
                        check={"proc_rate": affix.proc_rate},
                        result=result_dict
                    )
                    self.active_triggers.append(trigger)

        # 2. Apply all FLAT affixes second
        for item in self.equipment.values():
            for affix in item.affixes:
                # Handle dual-stat affixes for flat bonuses
                stats_affected = affix.stat_affected.split(';') if affix.dual_stat else [affix.stat_affected]
                values = [affix.value]

                if affix.dual_stat and affix.dual_value is not None:
                    values.append(affix.dual_value)

                # Apply scaling power multiplier if this is a scaling affix
                scaling_multiplier = 1.0
                if affix.scaling_power:
                    scaling_multiplier = 1.0 + math.log(power_level + 1) * 0.1

                for i, stat_name in enumerate(stats_affected):
                    if not stat_name or stat_name not in valid_stat_names:
                        continue

                    value = values[min(i, len(values)-1)]
                    # Apply value and scaling
                    final_value = value * scaling_multiplier
                    final_stats_dict[stat_name] += final_value

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
    mod_type: str
    affix_pools: str                          # Comma-separated list of valid pools
    description: str
    base_value: Any  # Can be float or string for dual values like "0.5;0.3"
    value: float
    dual_value: Optional[float] = None        # Second stat value for dual-stat affixes
    trigger_event: Optional[str] = None        # e.g., "OnHit"
    proc_rate: Optional[float] = None          # e.g., 0.25
    trigger_result: Optional[str] = None       # e.g., "apply_bleed"
    trigger_duration: Optional[float] = None   # e.g., 10.0
    stacks_max: Optional[int] = None           # e.g., 5
    # Phase 3: Advanced affix features
    dual_stat: Optional[str] = None            # e.g., "crit_damage"
    scaling_power: bool = False                # True for scaling affixes
    complex_effect: Optional[str] = None       # e.g., "special_skill"

    def get_dual_mod_type(self) -> str:
        """Get the modification type for the dual stat if applicable."""
        if not self.dual_stat:
            return ""
        # Extract the second type from the dual mod_type string (e.g., "flat;flat" -> "flat")
        return self.mod_type.split(';')[1] if ';' in self.mod_type else self.mod_type

    def get_dual_value(self) -> float:
        """Get the rolled value for the dual stat."""
        if not self.dual_stat:
            return 0.0
        # Parse dual values from base_value string format "primary;dual"
        base_val_str = str(self.base_value)
        if ';' in base_val_str:
            try:
                return float(base_val_str.split(';')[1])
            except (IndexError, ValueError):
                return 0.0
        return 0.0

    def get_primary_value(self) -> float:
        """Get the primary stat value (handles dual-stat format)."""
        base_val_str = str(self.base_value)
        if ';' in base_val_str:
            try:
                return float(base_val_str.split(';')[0])
            except (IndexError, ValueError):
                return float(self.value)  # Fallback to value
        try:
            return float(self.base_value)
        except (ValueError, TypeError):
            return float(self.value)  # Fallback


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


# Effect Configuration and Handler Data

@dataclass
class DamageOnHitConfig:
    """Configuration for damage-over-time effects applied on hit.

    Supports future data-driven configuration from effects.csv file.
    Enables adding new DoT effects without code changes.
    """
    debuff_name: str
    proc_rate: float
    duration: float
    damage_per_tick: float
    stacks_to_add: int = 1
    display_message: str = ""  # e.g., "Bleed proc'd on {target}!"


# Combat Engine Result Objects

@dataclass
class SkillUseResult:
    """Result container for skill use calculations.

    Separates damage calculations from action execution for architectural purity.
    Godot-friendly structure that translates well to signal/event systems.
    """
    hit_results: List["HitContext"]  # Calculated hits from multi-hit skills
    actions: List["Action"]         # Actions to execute (damage, events, effects)


# Action Classes for Decoupled Execution

@dataclass
class Action:
    """Base class for executable actions after skill calculation."""
    pass


@dataclass
class ApplyDamageAction(Action):
    """Action to apply calculated damage to a target."""
    target_id: str
    damage: float
    source: str = "skill"  # For tracking damage source


@dataclass
class DispatchEventAction(Action):
    """Action to dispatch an event via the EventBus."""
    event: "Event"  # The event instance to dispatch


@dataclass
class ApplyEffectAction(Action):
    """Action to apply a status effect to a target."""
    target_id: str
    effect_name: str
    stacks_to_add: int = 1
    source: str = "skill"  # For tracking effect source
    proc_rate: float = 1.0  # Probability of this effect applying (0.0 to 1.0)


@dataclass
class EffectInstance:
    """Runtime instance of a status effect applied to an entity.

    PR8a: New normalized effect data structure.
    Supports DoTs, buffs, debuffs, and complex reactive mechanics.
    """
    id: str                    # unique instance ID
    definition_id: str         # reference to effect definition
    source_id: str            # who applied this effect
    time_remaining: float
    tick_interval: float      # seconds between ticks (0 for no ticks)
    accumulator: float = 0.0  # time accumulator for ticking
    stacks: int = 1
    value: float = 0.0        # damage per tick, stat modifier, etc.
    expires_on_zero: bool = True

    def __repr__(self) -> str:
        return f"EffectInstance(id='{self.id}', definition='{self.definition_id}', stacks={self.stacks})"


# Forward reference for Action subclasses
# This will be resolved when imported in the engine
ApplyDamageAction.__annotations__["target_id"] = str
ApplyDamageAction.__annotations__["damage"] = float
ApplyDamageAction.__annotations__["source"] = str

DispatchEventAction.__annotations__["event"] = str  # Simplified for forward reference

ApplyEffectAction.__annotations__["target_id"] = str
ApplyEffectAction.__annotations__["effect_name"] = str
ApplyEffectAction.__annotations__["stacks_to_add"] = int
ApplyEffectAction.__annotations__["source"] = str
