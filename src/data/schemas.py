"""CSV Schema definitions for data validation.

This module defines validation schemas for all CSV data files.
Each schema specifies required columns and validation functions for their values.
"""

import logging
from typing import Any, Dict, Callable

logger = logging.getLogger(__name__)


def str_validator(value: str) -> str:
    """Validate string values."""
    if value is None:
        return ""
    return str(value).strip()


def int_validator(value: str) -> int:
    """Validate integer values."""
    if not value or value.strip() == "":
        raise ValueError("Value cannot be empty")
    try:
        return int(float(value))  # Handle float strings like "1.0"
    except (ValueError, TypeError):
        raise ValueError(f"Invalid integer value: '{value}'")


def float_validator(value: str) -> float:
    """Validate float values. Can be empty for optional fields."""
    if not value or value.strip() == "":
        # Allow empty values - this should be handled by the lambda wrappers
        raise ValueError("Value cannot be empty")
    try:
        return float(value)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid float value: '{value}'")


def flexible_float_validator(value: str) -> str:
    """Validate float values or semicolon-separated float values for complex affixes."""
    if not value or value.strip() == "":
        return ""  # Allow empty values

    # Check if it's semicolon-separated values
    if ";" in value:
        # Validate each part is a float
        parts = value.split(";")
        try:
            for part in parts:
                part = part.strip()
                if part:  # Allow empty parts
                    float(part)
            return value.strip()
        except ValueError:
            raise ValueError(f"Invalid float values in semicolon-separated list: '{value}'")

    # Single float value
    try:
        float(value.strip())
        return value.strip()
    except ValueError:
        raise ValueError(f"Invalid float value: '{value}'")





def flexible_damage_validator(value: str) -> float:
    """Validate damage values - can be empty (0.0) or any float (including negative for healing)."""
    if not value or value.strip() == "":
        return 0.0  # Empty is default damage
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid damage value: '{value}'")




def positive_float_validator(value: str) -> float:
    """Validate positive float values."""
    val = float_validator(value)
    if val <= 0:
        raise ValueError(f"Value must be > 0, got {val}")
    return val


def non_negative_float_validator(value: str) -> float:
    """Validate non-negative float values."""
    val = float_validator(value)
    if val < 0:
        raise ValueError(f"Value must be >= 0, got {val}")
    return val


def quality_id_validator(value: str) -> int:
    """Validate quality tier IDs."""
    val = int_validator(value)
    if val < 1:
        raise ValueError(f"Quality ID must be >= 1, got {val}")
    return val


def tier_range_validator(min_val: str, max_val: str) -> tuple[int, int]:
    """Validate tier range values and ensure min < max."""
    min_range = int_validator(min_val)
    max_range = int_validator(max_val)
    if min_range >= max_range:
        raise ValueError(f"Min range ({min_range}) must be < max range ({max_range})")
    return min_range, max_range


def affix_pools_validator(value: str) -> list[str]:
    """Validate affix pools - can be empty or pipe-separated string."""
    if not value or value.strip() == "":
        return []
    return [pool.strip() for pool in value.split('|') if pool.strip()]


def tier_probabilities_validator(value: str) -> int:
    """Validate tier probabilities - can be empty (0) or positive integer."""
    if not value or value.strip() == "":
        return 0
    val = int_validator(value)
    if val < 0:
        raise ValueError(f"Tier probability must be >= 0, got {val}")
    return val


# Schema definitions
AFFIX_SCHEMA = {
    "required": ["affix_id", "stat_affected", "mod_type", "base_value", "description"],
    "columns": {
        "affix_id": str_validator,
        "stat_affected": str_validator,
        "mod_type": str_validator,
        "affix_pools": affix_pools_validator,
        "base_value": flexible_float_validator,
        "description": str_validator,
        "trigger_event": str_validator,
        "proc_rate": lambda x: float_validator(x) if x and x.strip() else 0.0,
        "trigger_result": str_validator,
        "trigger_duration": lambda x: non_negative_float_validator(x) if x and x.strip() else 0.0,
        "stacks_max": lambda x: int_validator(x) if x and x.strip() else 1,
        "dual_stat": lambda x: x.upper() == "TRUE" if x and x.strip() else False,
        "scaling_power": lambda x: x.upper() == "TRUE" if x and x.strip() else False,
        "complex_effect": str_validator,
    },
}

ITEM_SCHEMA = {
    "required": ["item_id", "name", "slot", "rarity", "num_random_affixes"],
    "columns": {
        "item_id": str_validator,
        "name": str_validator,
        "slot": str_validator,
        "rarity": str_validator,
        "affix_pools": affix_pools_validator,
        "implicit_affixes": affix_pools_validator,  # Same validation as affix_pools
        "num_random_affixes": lambda x: int_validator(x) if x and x.strip() else 0,
    },
}

QUALITY_TIERS_SCHEMA = {
    "required": ["quality_id", "tier_name", "min_range", "max_range"],
    "columns": {
        "quality_id": quality_id_validator,
        "tier_name": str_validator,
        "min_range": int_validator,
        "max_range": int_validator,
        # Rarity probability columns (can be empty for 0)
        "Normal": tier_probabilities_validator,
        "Common": tier_probabilities_validator,
        "Unusual": tier_probabilities_validator,
        "Uncommon": tier_probabilities_validator,
        "Rare": tier_probabilities_validator,
        "Exotic": tier_probabilities_validator,
        "Epic": tier_probabilities_validator,
        "Glorious": tier_probabilities_validator,
        "Exalted": tier_probabilities_validator,
        "Legendary": tier_probabilities_validator,
        "Mythic": tier_probabilities_validator,
        "Godly": tier_probabilities_validator,
    },
}

EFFECTS_SCHEMA = {
    "required": ["effect_id", "name", "type", "description"],
    "columns": {
        "effect_id": str_validator,
        "name": str_validator,
        "type": str_validator,
        "description": str_validator,
        "max_stacks": lambda x: int_validator(x) if x and x.strip() else 1,
        "tick_rate": lambda x: non_negative_float_validator(x) if x and x.strip() else 1.0,
        "damage_per_tick": flexible_damage_validator,
        "stat_multiplier": lambda x: float_validator(x) if x and x.strip() else 0.0,
        "stat_add": lambda x: float_validator(x) if x and x.strip() else 0.0,
        "visual_effect": str_validator,
        "duration": lambda x: non_negative_float_validator(x) if x and x.strip() else 10.0,  # Default to 10 if empty
    },
}

SKILLS_SCHEMA = {
    "required": ["skill_id", "name", "damage_type"],
    "columns": {
        "skill_id": str_validator,
        "name": str_validator,
        "damage_type": str_validator,
        "hits": lambda x: int_validator(x) if x and x.strip() else 1,
        "description": str_validator,
        "resource_cost": lambda x: non_negative_float_validator(x) if x and x.strip() else 0.0,
        "cooldown": lambda x: non_negative_float_validator(x) if x and x.strip() else 0.0,
        "trigger_event": str_validator,
        "proc_rate": lambda x: float_validator(x) if x and x.strip() else 0.0,
        "trigger_result": str_validator,
        "trigger_duration": lambda x: non_negative_float_validator(x) if x and x.strip() else 0.0,
        "stacks_max": lambda x: int_validator(x) if x and x.strip() else 1,
    },
}

AFFIX_POOLS_SCHEMA = {
    "required": ["pool_id", "rarity", "tier", "affix_id"],
    "columns": {
        "pool_id": str_validator,
        "rarity": str_validator,
        "tier": int_validator,
        "affix_id": str_validator,
        "weight": lambda v: int_validator(v) if v and v.strip() else 1
    },
}

LOOT_TABLES_SCHEMA = {
    "required": ["table_id", "entry_type", "entry_id", "weight"],
    "columns": {
        "table_id": str_validator,
        "entry_type": str_validator,
        "entry_id": str_validator,
        "weight": lambda x: int_validator(x) if x else 0,
        "min_count": lambda x: int_validator(x) if x else 1,
        "max_count": lambda x: int_validator(x) if x else 1,
        "drop_chance": lambda x: float_validator(x) if x else 1.0,
    },
}

ENTITIES_SCHEMA = {
    "required": ["entity_id", "name", "base_health", "base_damage", "rarity"],
    "columns": {
        "entity_id": str_validator,
        "name": str_validator,
        "archetype": str_validator,
        "level": lambda x: int_validator(x) if x else 1,
        "rarity": str_validator,
        "base_health": positive_float_validator,
        "base_damage": non_negative_float_validator,
        "armor": lambda x: non_negative_float_validator(x) if x and x.strip() else 0.0,
        "crit_chance": lambda x: non_negative_float_validator(x) if x and x.strip() else 0.0,
        "attack_speed": lambda x: positive_float_validator(x) if x and x.strip() else 1.0,
        "equipment_pools": affix_pools_validator,  # Reuse the same validator
        "loot_table_id": str_validator,
        "description": str_validator,
    },
}


def get_schema_validator(filepath: str) -> Dict[str, Any]:
    """Get the appropriate schema validator for a CSV file based on its path.

    Args:
        filepath: Path to the CSV file

    Returns:
        Schema dictionary with validation rules

    Raises:
        ValueError: If no schema matches the file
    """
    filename = filepath.lower()

    if "affixes" in filename and filename.endswith(".csv"):
        return AFFIX_SCHEMA
    elif "affix_pools" in filename and filename.endswith(".csv"):
        return AFFIX_POOLS_SCHEMA
    elif "items" in filename and filename.endswith(".csv"):
        return ITEM_SCHEMA
    elif "quality_tiers" in filename and filename.endswith(".csv"):
        return QUALITY_TIERS_SCHEMA
    elif "effects" in filename and filename.endswith(".csv"):
        return EFFECTS_SCHEMA
    elif "skills" in filename and filename.endswith(".csv"):
        return SKILLS_SCHEMA
    elif "loot_tables" in filename and filename.endswith(".csv"):
        return LOOT_TABLES_SCHEMA
    elif "entities" in filename and filename.endswith(".csv"):
        return ENTITIES_SCHEMA
    else:
        raise ValueError(f"No schema found for CSV file: {filepath}")
