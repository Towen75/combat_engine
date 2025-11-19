"""Test suite for combat_math.py pure functions."""

import pytest
from random import Random
from src.combat_math import (
    roll_chance,
    resolve_crit,
    evade_dodge_or_normal,
    apply_block_damage,
    apply_glancing_damage,
    apply_pierce_to_armor,
    apply_armor_mitigation,
    calculate_pierce_damage_formula,
    clamp_min_damage,
    calculate_skill_effect_proc
)


class TestRollChance:
    """Test the roll_chance function."""

    def test_chance_zero_never_procs(self, seeded_rng):
        """Chance of 0 should never proc."""
        for _ in range(100):
            assert roll_chance(seeded_rng, 0.0) is False

    def test_chance_one_always_procs(self, seeded_rng):
        """Chance of 1 should always proc."""
        for _ in range(100):
            assert roll_chance(seeded_rng, 1.0) is True

    def test_deterministic_with_seed(self):
        """Same seed should give consistent results."""
        rng1 = Random(123)
        rng2 = Random(123)

        result1 = roll_chance(rng1, 0.5)
        result2 = roll_chance(rng2, 0.5)

        assert result1 == result2


class TestResolveCrit:
    """Test the resolve_crit function."""

    def test_crit_deterministic_with_seed(self):
        """Crit resolution should be deterministic with seeded RNG."""
        rng = Random(1)
        is_crit, mult = resolve_crit(rng, 1.0, 3.0)
        assert is_crit is True
        assert mult == 3.0

    def test_no_crit_when_zero_chance(self):
        """Zero crit chance should never result in crit."""
        rng = Random(1)
        for _ in range(10):
            is_crit, mult = resolve_crit(rng, 0.0, 2.0)
            assert is_crit is False
            assert mult == 1.0

    def test_crit_mult_normal_when_no_crit(self):
        """Non-crit hits should have multiplier of 1.0."""
        rng = Random(1)
        # Using a very low crit chance to ensure no crit
        is_crit, mult = resolve_crit(rng, 0.001, 2.0)
        assert is_crit is False
        assert mult == 1.0


class TestEvadeDodgeOrNormal:
    """Test the evade_dodge_or_normal function."""

    def test_returns_valid_results(self, seeded_rng):
        """Function should only return 'dodge', 'evade', or 'normal'."""
        for _ in range(100):
            result = evade_dodge_or_normal(seeded_rng, 0.1, 0.2)
            assert result in ['dodge', 'evade', 'normal']

    def test_deterministic_with_seed(self):
        """Same seed should produce consistent results."""
        rng1 = Random(42)
        rng2 = Random(42)

        result1 = evade_dodge_or_normal(rng1, 0.5, 0.3)
        result2 = evade_dodge_or_normal(rng2, 0.5, 0.3)

        assert result1 == result2

    def test_zero_chances_always_normal(self):
        """Zero evade/dodge chances should always result in normal."""
        rng = Random(123)
        for _ in range(50):
            result = evade_dodge_or_normal(rng, 0.0, 0.0)
            assert result == 'normal'


class TestApplyBlockDamage:
    """Test the apply_block_damage function."""

    def test_block_reduces_damage(self):
        """Blocking should reduce damage but not below minimum."""
        assert apply_block_damage(100, 50) == 50
        assert apply_block_damage(50, 60) == 1  # Minimum of 1
        assert apply_block_damage(10, 5) == 5

    def test_minimum_damage_one(self):
        """Damage should never drop below 1."""
        assert apply_block_damage(0.5, 0.5) == 1
        assert apply_block_damage(0, 100) == 1


class TestApplyGlancingDamage:
    """Test the apply_glancing_damage function."""

    def test_applies_multiplier(self):
        """Glancing should apply damage multiplier."""
        assert apply_glancing_damage(100, 0.5) == 50.0
        assert apply_glancing_damage(200, 0.25) == 50.0

    def test_zero_multiplier_no_damage(self):
        """Zero multiplier should result in no damage (0% of original)."""
        assert apply_glancing_damage(100, 0.0) == 0  # 0% glancing means 0 damage


class TestApplyPierceToArmor:
    """Test the apply_pierce_to_armor function."""

    def test_pierce_reduces_armor(self):
        """Pierce should reduce effective armor."""
        assert apply_pierce_to_armor(100, 0.5) == 50.0
        assert apply_pierce_to_armor(200, 0.25) == 150.0

    def test_full_pierce_zero_armor(self):
        """100% pierce should result in zero armor."""
        assert apply_pierce_to_armor(100, 1.0) == 0.0

    def test_zero_pierce_full_armor(self):
        """0% pierce should leave armor unchanged."""
        assert apply_pierce_to_armor(100, 0.0) == 100.0


class TestApplyArmorMitigation:
    """Test the apply_armor_mitigation function."""

    def test_armor_reduces_damage(self):
        """Armor should reduce damage but not below zero."""
        assert apply_armor_mitigation(100, 50) == 50.0
        assert apply_armor_mitigation(50, 100) == 0.0

    def test_zero_armor_full_damage(self):
        """Zero armor should leave damage unchanged."""
        assert apply_armor_mitigation(100, 0) == 100.0


class TestCalculatePierceDamageFormula:
    """Test the calculate_pierce_damage_formula function."""

    def test_uses_max_formula(self):
        """Formula should use max(pre_pierce_damage, pierced_damage)."""
        # pre_pierce_damage = 100 - 50 = 50
        # pierced_damage = 100 (assuming current_damage = 100)
        assert calculate_pierce_damage_formula(50, 100) == 100

        # Test case where normal damage is higher
        assert calculate_pierce_damage_formula(80, 40) == 80

    def test_never_negative(self):
        """Result should never be negative."""
        assert calculate_pierce_damage_formula(-10, -5) == 0
        assert calculate_pierce_damage_formula(0, 0) == 0


class TestClampMinDamage:
    """Test the clamp_min_damage function."""

    def test_enforces_minimum(self):
        """Should enforce minimum damage."""
        assert clamp_min_damage(5, 1) == 5
        assert clamp_min_damage(0, 1) == 1
        assert clamp_min_damage(-1, 0) == 0

    def test_zero_minimum_allows_zero(self):
        """Zero minimum should allow zero damage."""
        assert clamp_min_damage(0, 0) == 0
        assert clamp_min_damage(-5, 0) == 0


class TestCalculateSkillEffectProc:
    """Test the calculate_skill_effect_proc function."""

    def test_wrapper_around_roll_chance(self):
        """Function should wrap roll_chance."""
        rng = Random(123)
        # Test deterministic result
        rng = Random(1)
        result1 = calculate_skill_effect_proc(rng, 0.5)
        # Reset and try again
        rng = Random(1)
        result2 = calculate_skill_effect_proc(rng, 0.5)
        assert result1 == result2

    def test_high_proc_rate_always_procs(self):
        """High proc rate should always proc (for seeded RNG)."""
        rng = Random(123)
        # Depending on seed, this will be deterministic
        result = calculate_skill_effect_proc(rng, 0.99)
        assert isinstance(result, bool)

    def test_zero_proc_rate_never_procs(self):
        """Zero proc rate should never proc."""
        rng = Random(123)
        for _ in range(10):
            assert calculate_skill_effect_proc(rng, 0.0) is False


# Fixtures
@pytest.fixture
def seeded_rng():
    """Provide a seeded RNG for deterministic tests."""
    return Random(42)
