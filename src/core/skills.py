"""Skill system for combat - triggers and skill definitions."""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Trigger:
    """Represents a trigger condition and effect for a skill.

    Based on GDD Section 4.1.
    """
    event: str  # e.g., "OnHit", "OnCrit"
    check: Dict[str, Any]  # e.g., {"proc_rate": 0.5}
    result: Dict[str, Any]  # e.g., {"apply_debuff": "Bleed", "stacks": 1}


@dataclass
class Skill:
    """Represents a combat skill with triggers.

    Based on GDD Sections 3.0 and 4.1.
    """
    id: str
    name: str
    damage_type: str = "Physical"
    hits: int = 1
    cooldown: float = 0.0  # Cooldown in seconds
    resource_cost: float = 0.0  # Resource cost to use skill
    triggers: List[Trigger] = field(default_factory=list)
