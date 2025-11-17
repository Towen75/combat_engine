"""HitContext - telemetry dataclass for combat hit resolution."""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from ..models import Entity


@dataclass
class HitContext:
    """Telemetry object capturing combat hit resolution results.

    Provides structured data about each combat hit for debugging,
    testing, and analytics while maintaining Entity references
    for backward compatibility.
    """
    attacker: Entity
    defender: Entity

    # Core damage values
    base_raw: Any        # Original damage input (int, tuple, etc.)
    base_resolved: int   # Final resolved base damage value
    final_damage: int    # Final damage after all calculations

    # Combat outcome flags (Phase 2 mechanics)
    was_crit: bool = False
    was_dodged: bool = False
    was_blocked: bool = False
    was_glancing: bool = False

    # Partial damage accounting
    damage_pre_mitigation: float = 0.0  # Damage before armor mitigation
    damage_post_armor: float = 0.0      # Damage after pierce/armor calculation
    damage_blocked: float = 0.0         # Amount reduced by blocking

    # Optional RNG debugging (disabled by default for performance)
    rng_seed: Optional[int] = None

    @property
    def attacker_id(self) -> str:
        """Get attacker entity ID for serialization."""
        return self.attacker.id

    @property
    def defender_id(self) -> str:
        """Get defender entity ID for serialization."""
        return self.defender.id

    def to_serializable(self) -> Dict[str, Any]:
        """Return JSON-safe representation for telemetry/logging.

        Returns:
            Dict with string IDs and primitive values only (no Entity objects)
        """
        return {
            "attacker_id": self.attacker_id,
            "defender_id": self.defender_id,
            "base_resolved": self.base_resolved,
            "final_damage": self.final_damage,
            "was_crit": self.was_crit,
            "was_dodged": self.was_dodged,
            "was_blocked": self.was_blocked,
            "was_glancing": self.was_glancing,
            "damage_pre_mitigation": self.damage_pre_mitigation,
            "damage_post_armor": self.damage_post_armor,
            "damage_blocked": self.damage_blocked,
        }
