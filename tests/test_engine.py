"""Unit tests for CombatEngine - core damage calculations."""

import pytest
from src.models import Entity, EntityStats
from src.engine import CombatEngine


class TestCombatEngineResolveHit:
    """Test the core resolve_hit damage calculation."""

    def test_no_armor(self):
        """Test damage calculation with no armor (Unit Test 3.1)."""
        # Attacker: base_damage = 100, pierce_ratio = 0.01 (default)
        attacker_stats = EntityStats(base_damage=100.0)
        attacker = Entity(id="attacker", stats=attacker_stats)

        # Defender: armor = 0
        defender_stats = EntityStats(armor=0.0)
        defender = Entity(id="defender", stats=defender_stats)

        damage = CombatEngine.resolve_hit(attacker, defender)
        assert damage == 100.0

    def test_high_armor_low_pierce(self):
        """Test damage with high armor and low pierce (Unit Test 3.2)."""
        # Attacker: base_damage = 100, pierce_ratio = 0.1
        attacker_stats = EntityStats(base_damage=100.0, pierce_ratio=0.1)
        attacker = Entity(id="attacker", stats=attacker_stats)

        # Defender: armor = 120 (higher than attack damage)
        defender_stats = EntityStats(armor=120.0)
        defender = Entity(id="defender", stats=defender_stats)

        # PrePierceDamage = 100 - 120 = -20
        # PiercedDamage = 100 * 0.1 = 10
        # Final = max(-20, 10) = 10
        damage = CombatEngine.resolve_hit(attacker, defender)
        assert damage == 10.0

    def test_armor_greater_than_pierced_damage(self):
        """Test when armor reduction is less than pierced damage (Unit Test 3.3)."""
        # Attacker: base_damage = 100, pierce_ratio = 0.3
        attacker_stats = EntityStats(base_damage=100.0, pierce_ratio=0.3)
        attacker = Entity(id="attacker", stats=attacker_stats)

        # Defender: armor = 80
        defender_stats = EntityStats(armor=80.0)
        defender = Entity(id="defender", stats=defender_stats)

        # PrePierceDamage = 100 - 80 = 20
        # PiercedDamage = 100 * 0.3 = 30
        # Final = max(20, 30) = 30
        damage = CombatEngine.resolve_hit(attacker, defender)
        assert damage == 30.0

    def test_armor_less_than_pierced_damage(self):
        """Test when armor reduction is greater than pierced damage (Unit Test 3.4)."""
        # Attacker: base_damage = 100, pierce_ratio = 0.3
        attacker_stats = EntityStats(base_damage=100.0, pierce_ratio=0.3)
        attacker = Entity(id="attacker", stats=attacker_stats)

        # Defender: armor = 60
        defender_stats = EntityStats(armor=60.0)
        defender = Entity(id="defender", stats=defender_stats)

        # PrePierceDamage = 100 - 60 = 40
        # PiercedDamage = 100 * 0.3 = 30
        # Final = max(40, 30) = 40
        damage = CombatEngine.resolve_hit(attacker, defender)
        assert damage == 40.0

    def test_zero_damage_prevents_negative(self):
        """Test that damage calculation never returns negative values."""
        # Attacker: base_damage = 50, pierce_ratio = 0.01 (default)
        attacker_stats = EntityStats(base_damage=50.0)
        attacker = Entity(id="attacker", stats=attacker_stats)

        # Defender: armor = 100 (much higher than attack)
        defender_stats = EntityStats(armor=100.0)
        defender = Entity(id="defender", stats=defender_stats)

        # PrePierceDamage = 50 - 100 = -50
        # PiercedDamage = 50 * 0.01 = 0.5
        # Final = max(-50, 0.5) = 0.5, then max(0, 0.5) = 0.5
        damage = CombatEngine.resolve_hit(attacker, defender)
        assert damage == 0.5

    def test_minimum_pierce_ratio(self):
        """Test damage calculation with minimum pierce ratio."""
        # Attacker: base_damage = 100, pierce_ratio = 0.01 (minimum)
        attacker_stats = EntityStats(base_damage=100.0, pierce_ratio=0.01)
        attacker = Entity(id="attacker", stats=attacker_stats)

        # Defender: armor = 50
        defender_stats = EntityStats(armor=50.0)
        defender = Entity(id="defender", stats=defender_stats)

        # PrePierceDamage = 100 - 50 = 50
        # PiercedDamage = 100 * 0.01 = 1
        # Final = max(50, 1) = 50
        damage = CombatEngine.resolve_hit(attacker, defender)
        assert damage == 50.0


class TestCombatEngineCalculateEffectiveDamage:
    """Test the detailed damage breakdown calculation."""

    def test_damage_breakdown_no_armor(self):
        """Test detailed breakdown with no armor."""
        attacker_stats = EntityStats(base_damage=100.0, pierce_ratio=0.2)
        attacker = Entity(id="attacker", stats=attacker_stats)

        defender_stats = EntityStats(armor=0.0)
        defender = Entity(id="defender", stats=defender_stats)

        breakdown = CombatEngine.calculate_effective_damage(attacker, defender)

        expected = {
            'final_damage': 100.0,
            'attack_damage': 100.0,
            'pre_pierce_damage': 100.0,
            'pierced_damage': 20.0,
            'armor_reduction': 0.0,
            'pierce_ratio': 0.2
        }
        assert breakdown == expected

    def test_damage_breakdown_with_armor(self):
        """Test detailed breakdown with armor."""
        attacker_stats = EntityStats(base_damage=100.0, pierce_ratio=0.3)
        attacker = Entity(id="attacker", stats=attacker_stats)

        defender_stats = EntityStats(armor=80.0)
        defender = Entity(id="defender", stats=defender_stats)

        breakdown = CombatEngine.calculate_effective_damage(attacker, defender)

        expected = {
            'final_damage': 30.0,
            'attack_damage': 100.0,
            'pre_pierce_damage': 20.0,
            'pierced_damage': 30.0,
            'armor_reduction': 80.0,
            'pierce_ratio': 0.3
        }
        assert breakdown == expected

    def test_damage_breakdown_negative_pre_pierce(self):
        """Test detailed breakdown when pre-pierce damage is negative."""
        attacker_stats = EntityStats(base_damage=100.0, pierce_ratio=0.1)
        attacker = Entity(id="attacker", stats=attacker_stats)

        defender_stats = EntityStats(armor=120.0)
        defender = Entity(id="defender", stats=defender_stats)

        breakdown = CombatEngine.calculate_effective_damage(attacker, defender)

        expected = {
            'final_damage': 10.0,
            'attack_damage': 100.0,
            'pre_pierce_damage': -20.0,
            'pierced_damage': 10.0,
            'armor_reduction': 120.0,
            'pierce_ratio': 0.1
        }
        assert breakdown == expected


class TestCombatEngineValidateDamageCalculation:
    """Test damage calculation validation."""

    def test_valid_calculation(self):
        """Test validation of a valid damage calculation."""
        attacker_stats = EntityStats(base_damage=100.0, pierce_ratio=0.2)
        attacker = Entity(id="attacker", stats=attacker_stats)

        defender_stats = EntityStats(armor=50.0)
        defender = Entity(id="defender", stats=defender_stats)

        error = CombatEngine.validate_damage_calculation(attacker, defender)
        assert error is None

    # Note: Additional validation tests removed since EntityStats dataclass
    # already validates these conditions at creation time, making CombatEngine
    # validation redundant for these cases.
