"""Typed data models for game data with strict typing and enums.

This module defines dataclasses and enums for all core game data structures.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any, Type, TypeVar
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Enum)

# ========== Enums ==========

class Rarity(str, Enum):
    """Enum for item and entity rarity tiers."""
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    EPIC = "Epic"
    LEGENDARY = "Legendary"
    MYTHIC = "Mythic"
    MAGIC = "Magic"

class ItemSlot(str, Enum):
    """Enum for equipment slots."""
    WEAPON = "Weapon"
    OFF_HAND = "OffHand"
    HEAD = "Head"
    CHEST = "Chest"
    LEGS = "Legs"
    FEET = "Feet"
    HANDS = "Hands"
    RING = "Ring"
    AMULET = "Amulet"
    BELT = "Belt"
    SHOULDERS = "Shoulders"
    CLOAK = "Cloak"
    QUIVER = "Quiver"
    ACCESSORY = "Accessory"

class ModType(str, Enum):
    """Enum for affix modification types."""
    FLAT = "flat"
    MULTIPLIER = "multiplier"
    SCALING = "scaling"

class DamageType(str, Enum):
    """Enum for damage types."""
    PHYSICAL = "Physical"
    FIRE = "Fire"
    COLD = "Cold"
    LIGHTNING = "Lightning"
    POISON = "Poison"
    ACID = "Acid"
    EARTH = "Earth"
    DARK = "Dark"
    LIGHT = "Light"
    MAGIC = "Magic"
    SHADOW = "Shadow"
    DIVINE = "Divine"
    PIERCING = "Piercing"

class EffectType(str, Enum):
    """Enum for effect types."""
    BUFF = "Buff"
    DEBUFF = "Debuff"
    DOT = "DoT"
    HOT = "HoT"
    STUN = "Stun"
    ROOT = "Root"
    SILENCE = "Silence"
    IMMUNE = "Immune"
    SPECIAL = "Special"

class TriggerEvent(str, Enum):
    """Enum for trigger events."""
    ON_HIT = "OnHit"
    ON_KILL = "OnKill"
    ON_DAMAGE_TAKEN = "OnDamageTaken"
    ON_CRIT = "OnCrit"
    ON_EVADE = "OnEvade"
    ON_BLOCK = "OnBlock"
    ON_DODGE = "OnDodge"
    ON_SKILL_USED = "OnSkillUsed"
    ON_USE = "OnUse"
    ON_SELF = "OnSelf"

class LootEntryType(str, Enum):
    """Enum for types of entries in a loot table."""
    ITEM = "Item"
    TABLE = "Table"


# ========== Data Classes ==========

@dataclass
class LootTableEntry:
    """A single row in a loot table."""
    table_id: str
    entry_type: LootEntryType
    entry_id: str
    weight: int
    min_count: int
    max_count: int
    drop_chance: float

@dataclass
class LootTableDefinition:
    """Aggregate object representing a full loot table (multiple entries)."""
    table_id: str
    entries: List[LootTableEntry] = field(default_factory=list)

    def get_total_weight(self) -> int:
        return sum(e.weight for e in self.entries)

@dataclass
class AffixDefinition:
    """Strongly-typed model for affix data from CSV."""
    affix_id: str
    stat_affected: str
    mod_type: str
    base_value: Any  # Changed to Any to support float from JSON or str from CSV
    description: str
    affix_pools: List[str] = field(default_factory=list)
    trigger_event: Optional[TriggerEvent] = None
    proc_rate: float = 0.0
    trigger_result: str = ""
    trigger_duration: float = 10.0
    stacks_max: int = 1
    dual_stat: bool = False
    scaling_power: bool = False
    complex_effect: str = ""

    def __post_init__(self):
        if not self.affix_id:
            raise ValueError("affix_id cannot be empty")
        if not self.stat_affected:
            raise ValueError("stat_affected cannot be empty")
        
        # Validate dual_stat flag
        # Ensure base_value is treated as string for this check to avoid TypeError with floats
        base_val_str = str(self.base_value)
        has_semicolon = ";" in base_val_str
        if self.dual_stat != has_semicolon:
            # Allow exception for non-numeric base values that might not match this rule strictly
            # but warn if it looks like a stat value
            pass 

    def get_mod_types(self) -> List[ModType]:
        parts = self.mod_type.split(';')
        return [ModType(part.strip()) for part in parts]

@dataclass
class ItemTemplate:
    """Strongly-typed model for item template data."""
    item_id: str
    name: str
    slot: ItemSlot
    rarity: Rarity
    affix_pools: List[str] = field(default_factory=list)
    implicit_affixes: List[str] = field(default_factory=list)
    num_random_affixes: int = 0
    default_attack_skill: Optional[str] = None # <--- NEW

    def __post_init__(self):
        if not self.item_id:
            raise ValueError("item_id cannot be empty")
        if not self.name:
            raise ValueError("name cannot be empty")
        if self.num_random_affixes < 0:
            raise ValueError("num_random_affixes must be non-negative")

@dataclass
class QualityTier:
    """Strongly-typed model for quality tier data."""
    quality_id: int
    tier_name: str
    min_range: int
    max_range: int
    common: int = 0
    uncommon: int = 0
    rare: int = 0
    epic: int = 0
    legendary: int = 0
    mythic: int = 0

    def __post_init__(self):
        if self.quality_id < 1:
            raise ValueError("quality_id must be >= 1")
        if self.min_range >= self.max_range:
            raise ValueError(f"min_range ({self.min_range}) must be < max_range ({self.max_range})")

    def get_probability_for_rarity(self, rarity: Rarity) -> int:
        return getattr(self, rarity.value.lower())

@dataclass
class EffectDefinition:
    """Strongly-typed model for effect data."""
    effect_id: str
    name: str
    type: EffectType
    description: str
    max_stacks: int = 1
    tick_rate: float = 1.0
    damage_per_tick: float = 0.0
    stat_multiplier: float = 0.0
    stat_add: float = 0.0
    visual_effect: str = ""
    duration: float = 10.0

    def __post_init__(self):
        if not self.effect_id:
            raise ValueError("effect_id cannot be empty")
        if not self.name:
            raise ValueError("name cannot be empty")

@dataclass
class SkillDefinition:
    """Strongly-typed model for skill data."""
    skill_id: str
    name: str
    damage_type: DamageType
    damage_multiplier: float = 1.0 # <--- NEW
    hits: int = 1
    description: str = ""
    resource_cost: float = 0.0
    cooldown: float = 0.0
    trigger_event: Optional[TriggerEvent] = None
    proc_rate: float = 0.0
    trigger_result: str = ""
    trigger_duration: float = 10.0
    stacks_max: int = 1

    def __post_init__(self):
        if not self.skill_id:
            raise ValueError("skill_id cannot be empty")
        if not self.name:
            raise ValueError("name cannot be empty")

@dataclass
class EntityTemplate:
    """Strongly-typed model for entity definition."""
    entity_id: str
    name: str
    archetype: str
    level: int
    rarity: Rarity
    base_health: float
    base_damage: float
    armor: float
    crit_chance: float
    attack_speed: float
    equipment_pools: List[str] = field(default_factory=list)
    loot_table_id: str = ""
    description: str = ""
    portrait_path: str = ""  # New field for portrait image path

    def __post_init__(self):
        if not self.entity_id:
            raise ValueError("entity_id cannot be empty")
        if self.base_health <= 0:
            raise ValueError(f"base_health must be positive, got {self.base_health}")


# ========== Exception Classes ==========

class DataValidationError(ValueError):
    """Exception raised when data validation fails."""
    def __init__(self, message: str, data_type: str = "", field_name: str = "",
                 invalid_id: str = "", suggestions: Optional[List[str]] = None):
        super().__init__(message)
        self.data_type = data_type
        self.field_name = field_name
        self.invalid_id = invalid_id
        self.suggestions = suggestions or []

    def __str__(self):
        msg = super().__str__()
        if self.suggestions:
            msg += f"\nSuggestions: {', '.join(self.suggestions)}"
        return msg


# ========== Utility Functions ==========

def validate_entity_stats_are_valid(stats_list: List[str]) -> None:
    """Validate that all stat names are valid EntityStats attributes."""
    from src.core.models import EntityStats
    valid_stats = set(vars(EntityStats(0, 1)).keys())
    for stat_name in stats_list:
        if stat_name and stat_name not in valid_stats:
            raise DataValidationError(
                f"Invalid stat name '{stat_name}'",
                data_type="EntityStats",
                field_name="stat_affected",
                invalid_id=stat_name,
                suggestions=list(valid_stats)
            )

def parse_affix_pools(value: str) -> List[str]:
    """Parse affix pools from pipe-separated string."""
    if isinstance(value, list):
        return value
    if not value or (isinstance(value, str) and value.strip() == ""):
        return []
    if isinstance(value, str):
        return [pool.strip() for pool in value.split('|') if pool.strip()]
    return []

def normalize_enum(enum_cls: Type[T], value: str, default: Optional[T] = None) -> T:
    """Helper to fuzzy-match strings to Enum values (case-insensitive)."""
    if not value:
        if default is not None:
            return default
        raise ValueError(f"Empty value for {enum_cls.__name__}")
        
    # Try direct lookup
    try:
        return enum_cls(value)
    except ValueError:
        pass
        
    # Try case-insensitive lookup
    normalized = value.strip().lower()
    
    # Manual mapping for legacy/alternate terms
    mappings = {
        'ItemSlot': {
            'offhand': ItemSlot.OFF_HAND,
            'off-hand': ItemSlot.OFF_HAND,
            'helmet': ItemSlot.HEAD,
            'helm': ItemSlot.HEAD,
            'armor': ItemSlot.CHEST,
            'boots': ItemSlot.FEET,
            'gloves': ItemSlot.HANDS,
            'pants': ItemSlot.LEGS,
            'jewelry': ItemSlot.ACCESSORY, # Fallback
            'shield': ItemSlot.OFF_HAND,
        },
        'DamageType': {
            'piercing': DamageType.PIERCING,
            'physical': DamageType.PHYSICAL,
            'acid': DamageType.ACID, # Map to new Acid type
        }
    }
    
    # Apply specific mappings if they exist
    if enum_cls.__name__ in mappings and normalized in mappings[enum_cls.__name__]:
        return mappings[enum_cls.__name__][normalized]
        
    # General case-insensitive search
    for member in enum_cls:
        if member.value.lower() == normalized:
            return member
            
    raise ValueError(f"Invalid {enum_cls.__name__}: '{value}'")

# ========== Hydration Functions ==========

def hydrate_affix_definition(raw_data: Dict[str, Any]) -> AffixDefinition:
    return AffixDefinition(
        affix_id=raw_data['affix_id'],
        stat_affected=raw_data['stat_affected'],
        mod_type=raw_data['mod_type'],
        base_value=raw_data['base_value'],
        description=raw_data['description'],
        affix_pools=parse_affix_pools(raw_data.get('affix_pools', '')),
        trigger_event=normalize_enum(TriggerEvent, raw_data['trigger_event']) if raw_data.get('trigger_event') else None,
        proc_rate=float(raw_data['proc_rate']) if raw_data.get('proc_rate') else 0.0,
        trigger_result=raw_data.get('trigger_result', ''),
        trigger_duration=float(raw_data['trigger_duration']) if raw_data.get('trigger_duration') else 10.0,
        stacks_max=int(raw_data['stacks_max']) if raw_data.get('stacks_max') else 1,
        dual_stat=bool(raw_data.get('dual_stat', False)),
        scaling_power=bool(raw_data.get('scaling_power', False)),
        complex_effect=raw_data.get('complex_effect', '')
    )

def hydrate_item_template(raw_data: Dict[str, Any]) -> ItemTemplate:
    implicit_affixes_raw = raw_data.get('implicit_affixes', '')
    if isinstance(implicit_affixes_raw, list):
        implicit_affixes = implicit_affixes_raw
    else:
        implicit_affixes = parse_affix_pools(implicit_affixes_raw)

    return ItemTemplate(
        item_id=raw_data['item_id'],
        name=raw_data['name'],
        slot=normalize_enum(ItemSlot, raw_data['slot']),
        rarity=normalize_enum(Rarity, raw_data['rarity']),
        affix_pools=parse_affix_pools(raw_data.get('affix_pools', '')),
        implicit_affixes=implicit_affixes,
        num_random_affixes=int(raw_data['num_random_affixes']) if raw_data.get('num_random_affixes') else 0,
        default_attack_skill=raw_data.get('default_attack_skill') or None # <--- NEW
    )

def hydrate_quality_tier(raw_data: Dict[str, Any]) -> QualityTier:
    return QualityTier(
        quality_id=int(raw_data['quality_id']),
        tier_name=raw_data['tier_name'],
        min_range=int(raw_data['min_range']),
        max_range=int(raw_data['max_range']),
        common=int(raw_data.get('Common', 0)) if raw_data.get('Common') else 0,
        uncommon=int(raw_data.get('Uncommon', 0)) if raw_data.get('Uncommon') else 0,
        rare=int(raw_data.get('Rare', 0)) if raw_data.get('Rare') else 0,
        epic=int(raw_data.get('Epic', 0)) if raw_data.get('Epic') else 0,
        legendary=int(raw_data.get('Legendary', 0)) if raw_data.get('Legendary') else 0,
        mythic=int(raw_data.get('Mythic', 0)) if raw_data.get('Mythic') else 0
    )

def hydrate_effect_definition(raw_data: Dict[str, Any]) -> EffectDefinition:
    return EffectDefinition(
        effect_id=raw_data['effect_id'],
        name=raw_data['name'],
        type=normalize_enum(EffectType, raw_data['type']),
        description=raw_data['description'],
        max_stacks=int(raw_data['max_stacks']) if raw_data.get('max_stacks') else 1,
        tick_rate=float(raw_data['tick_rate']) if raw_data.get('tick_rate') else 1.0,
        damage_per_tick=float(raw_data['damage_per_tick']) if raw_data.get('damage_per_tick') else 0.0,
        stat_multiplier=float(raw_data['stat_multiplier']) if raw_data.get('stat_multiplier') else 0.0,
        stat_add=float(raw_data['stat_add']) if raw_data.get('stat_add') else 0.0,
        visual_effect=raw_data.get('visual_effect', ''),
        duration=float(raw_data['duration']) if raw_data.get('duration') else 10.0
    )

def hydrate_skill_definition(raw_data: Dict[str, Any]) -> SkillDefinition:
    return SkillDefinition(
        skill_id=raw_data['skill_id'],
        name=raw_data['name'],
        damage_type=normalize_enum(DamageType, raw_data['damage_type']),
        damage_multiplier=float(raw_data.get('damage_multiplier', 1.0)), # <--- NEW
        hits=int(raw_data['hits']) if raw_data.get('hits') else 1,
        description=raw_data.get('description', ''),
        resource_cost=float(raw_data['resource_cost']) if raw_data.get('resource_cost') else 0.0,
        cooldown=float(raw_data['cooldown']) if raw_data.get('cooldown') else 0.0,
        trigger_event=normalize_enum(TriggerEvent, raw_data['trigger_event']) if raw_data.get('trigger_event') else None,
        proc_rate=float(raw_data['proc_rate']) if raw_data.get('proc_rate') else 0.0,
        trigger_result=raw_data.get('trigger_result', ''),
        trigger_duration=float(raw_data['trigger_duration']) if raw_data.get('trigger_duration') else 10.0,
        stacks_max=int(raw_data['stacks_max']) if raw_data.get('stacks_max') else 1
    )

def hydrate_loot_entry(raw_data: Dict[str, Any]) -> LootTableEntry:
    return LootTableEntry(
        table_id=raw_data['table_id'],
        entry_type=normalize_enum(LootEntryType, raw_data['entry_type']),
        entry_id=raw_data['entry_id'],
        weight=int(raw_data['weight']),
        min_count=int(raw_data['min_count']) if raw_data.get('min_count') else 1,
        max_count=int(raw_data['max_count']) if raw_data.get('max_count') else 1,
        drop_chance=float(raw_data['drop_chance']) if raw_data.get('drop_chance') else 1.0
    )

def hydrate_entity_template(raw_data: Dict[str, Any]) -> EntityTemplate:
    return EntityTemplate(
        entity_id=raw_data['entity_id'],
        name=raw_data['name'],
        archetype=raw_data.get('archetype', 'Unit'),
        level=int(raw_data['level']) if raw_data.get('level') else 1,
        rarity=normalize_enum(Rarity, raw_data.get('rarity') or 'Common', default=Rarity.COMMON),
        base_health=float(raw_data['base_health']),
        base_damage=float(raw_data['base_damage']),
        armor=float(raw_data.get('armor', 0.0)),
        crit_chance=float(raw_data.get('crit_chance', 0.0)),
        attack_speed=float(raw_data.get('attack_speed', 1.0)),
        equipment_pools=parse_affix_pools(raw_data.get('equipment_pools', '')),
        loot_table_id=raw_data.get('loot_table_id', ''),
        description=raw_data.get('description', ''),
        portrait_path=raw_data.get('portrait_path', '')  # New field mapping
    )
