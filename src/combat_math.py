"""
Pure, stateless combat math functions.

These functions never:
- store state
- reference CombatEngine
- reference HitContext
- call RNG internally

All randomness must be provided by the caller.
"""

from typing import Tuple


def roll_chance(rng, chance: float) -> bool:
    """Return True if proc occurs. Assumes rng is Random or similar."""
    if chance <= 0:
        return False
    if chance >= 1:
        return True
    return rng.random() < chance


def resolve_crit(rng, crit_chance: float, crit_mult: float) -> Tuple[bool, float]:
    """Returns (is_crit, multiplier).

    Crit multiplier is applied by caller to damage calculations.
    """
    is_crit = roll_chance(rng, crit_chance)
    return is_crit, (crit_mult if is_crit else 1.0)


def evade_dodge_or_normal(rng, dodge_chance: float, evade_chance: float) -> str:
    """Returns 'dodge', 'evade', or 'normal'.

    Dodge and evade are mutually exclusive with priority to full dodges.
    """
    if roll_chance(rng, dodge_chance):
        return 'dodge'
    if roll_chance(rng, evade_chance):
        return 'evade'
    return 'normal'


def apply_block_damage(damage: float, block_amount: float) -> float:
    """Apply damage reduction from blocking. Returns reduced damage."""
    # Never reduce below 1 damage
    return max(1.0, damage - block_amount)


def apply_glancing_damage(damage: float, glancing_multiplier: float) -> float:
    """Apply glancing blow damage reduction."""
    if glancing_multiplier <= 0:
        return 0  # 0% damage on glancing blow means 0 damage total
    return damage * glancing_multiplier


def apply_pierce_to_armor(armor: float, pierce_ratio: float) -> float:
    """Pierce bypasses a portion of armor. Returns effective armor after pierce."""
    # Pierce ratio of 1.0 bypasses all armor (100% pierce)
    # Pierce ratio of 0.0 leaves armor unchanged (0% pierce)
    return max(0.0, armor * (1.0 - pierce_ratio))


def apply_armor_mitigation(damage: float, effective_armor: float) -> float:
    """Apply armor mitigation to damage."""
    # GDD Formula: damage - armor, clamped to 0
    mitigated_damage = max(0.0, damage - effective_armor)

    # Alternative formula could be: damage * (100 / (100 + effective_armor))
    # But current implementation uses the simpler damage - armor approach

    return mitigated_damage


def calculate_pierce_damage_formula(
    pre_pierce_damage: float,
    pierced_damage: float
) -> float:
    """Calculate final damage using pierce formula.

    Current GDD: max(0, max(pre_pierce_damage, pierced_damage))
    This means damage ignores pierce if normal armor reduction gives higher damage.
    """
    return max(0.0, max(pre_pierce_damage, pierced_damage))


def clamp_min_damage(damage: float, min_value: float = 0.0) -> float:
    """Ensure damage never goes below minimum value."""
    return max(min_value, damage)


def calculate_skill_effect_proc(rng, proc_rate: float) -> bool:
    """Determine if a skill effect should proc."""
    return roll_chance(rng, proc_rate)
