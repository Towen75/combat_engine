"""Core combat engine - damage calculation and hit resolution."""

from typing import Optional
from .models import Entity


class CombatEngine:
    """Static class containing core combat calculation methods.

    This engine implements the damage formulas from the Game Design Document,
    providing pure functions for hit resolution and damage calculation.
    """

    @staticmethod
    def resolve_hit(attacker: Entity, defender: Entity) -> float:
        """Calculate the damage of a single hit based on GDD Section 2.1.

        Implements the core damage formula:
        Damage Dealt = MAX((Attack Damage - Defences), (Attack Damage * Pierce Ratio))

        Args:
            attacker: The entity performing the attack
            defender: The entity receiving the attack

        Returns:
            The final damage value (never negative)

        Note:
            For Phase 1, Attack Damage equals base_damage only.
            Flat modifiers will be added in Phase 2.
        """
        # Phase 1: Attack Damage is just base_damage
        attack_damage = attacker.stats.base_damage

        # Defenses are armor for physical attacks (GDD 5.0)
        defenses = defender.stats.armor

        # GDD 2.1: Core Damage Formula
        pre_pierce_damage = attack_damage - defenses
        pierced_damage = attack_damage * attacker.stats.pierce_ratio

        # Take the maximum of pre-pierce and pierced damage
        damage_dealt = max(pre_pierce_damage, pierced_damage)

        # Ensure damage is never negative
        return max(0, damage_dealt)

    @staticmethod
    def calculate_effective_damage(attacker: Entity, defender: Entity) -> dict:
        """Calculate detailed damage breakdown for analysis.

        Args:
            attacker: The entity performing the attack
            defender: The entity receiving the attack

        Returns:
            Dictionary with damage calculation details:
            {
                'final_damage': float,
                'attack_damage': float,
                'pre_pierce_damage': float,
                'pierced_damage': float,
                'armor_reduction': float,
                'pierce_ratio': float
            }
        """
        attack_damage = attacker.stats.base_damage
        defenses = defender.stats.armor
        pierce_ratio = attacker.stats.pierce_ratio

        pre_pierce_damage = attack_damage - defenses
        pierced_damage = attack_damage * pierce_ratio
        final_damage = max(pre_pierce_damage, pierced_damage)
        final_damage = max(0, final_damage)

        return {
            'final_damage': final_damage,
            'attack_damage': attack_damage,
            'pre_pierce_damage': pre_pierce_damage,
            'pierced_damage': pierced_damage,
            'armor_reduction': defenses,
            'pierce_ratio': pierce_ratio
        }

    @staticmethod
    def validate_damage_calculation(attacker: Entity, defender: Entity) -> Optional[str]:
        """Validate that a damage calculation would be valid.

        Args:
            attacker: The entity performing the attack
            defender: The entity receiving the attack

        Returns:
            None if valid, error message string if invalid
        """
        if attacker.stats.base_damage < 0:
            return f"Attacker base_damage cannot be negative: {attacker.stats.base_damage}"

        if attacker.stats.pierce_ratio < 0.01:
            return f"Attacker pierce_ratio below minimum: {attacker.stats.pierce_ratio}"

        if defender.stats.armor < 0:
            return f"Defender armor cannot be negative: {defender.stats.armor}"

        return None
