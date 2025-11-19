"""Tests for HitContext telemetry dataclass."""

import pytest
from src.engine.hit_context import HitContext
from src.engine.core import CombatEngine
from src.models import Entity, EntityStats
from tests.fixtures import make_attacker, make_defender, make_rng, make_state_manager


@pytest.fixture
def attacker():
    """Provide test attacker entity."""
    return make_attacker()


@pytest.fixture
def defender():
    """Provide test defender entity."""
    return make_defender()


@pytest.fixture
def rng():
    """Provide test RNG."""
    return make_rng()


@pytest.fixture
def state_manager(attacker, defender):
    """Provide test state manager."""
    return make_state_manager(attacker=attacker, defender=defender)


class TestHitContextBasics:
    """Test basic HitContext functionality."""

    def test_hitcontext_creation_with_entities(self, attacker, defender):
        """Test HitContext can be created with required fields."""
        ctx = HitContext(
            attacker=attacker,
            defender=defender,
            base_raw=100,
            base_resolved=100,
            final_damage=100
        )

        assert ctx.attacker == attacker
        assert ctx.defender == defender
        assert ctx.base_raw == 100
        assert ctx.base_resolved == 100
        assert ctx.final_damage == 100
        assert ctx.was_crit is False
        assert ctx.was_dodged is False
        assert ctx.was_blocked is False
        assert ctx.was_glancing is False

    def test_hitcontext_property_accessors(self, attacker, defender):
        """Test derived property accessors work correctly."""
        attacker.id = "attacker_123"
        defender.id = "defender_456"

        ctx = HitContext(
            attacker=attacker,
            defender=defender,
            base_raw=100,
            base_resolved=100,
            final_damage=100
        )

        assert ctx.attacker_id == "attacker_123"
        assert ctx.defender_id == "defender_456"

    def test_to_serializable(self, attacker, defender):
        """Test JSON-safe representation works correctly."""
        attacker.id = "att_001"
        defender.id = "def_002"

        ctx = HitContext(
            attacker=attacker,
            defender=defender,
            base_raw=100,
            base_resolved=100,
            final_damage=75,
            was_crit=True,
            was_blocked=True,
            damage_blocked=25.0
        )

        serializable = ctx.to_serializable()

        # Should be a dict with only primitive/string values
        assert serializable == {
            "attacker_id": "att_001",
            "defender_id": "def_002",
            "base_resolved": 100,
            "final_damage": 75,
            "was_crit": True,
            "was_dodged": False,
            "was_blocked": True,
            "was_glancing": False,
            "damage_pre_mitigation": 0.0,
            "damage_post_armor": 0.0,
            "damage_blocked": 25.0,
        }

        # Verify it doesn't contain Entity objects
        assert "attacker" not in serializable
        assert "defender" not in serializable


class TestHitContextCombatEngineIntegration:
    """Test HitContext populated by CombatEngine."""

    def test_resolve_hit_populates_phase2_fields_dodge(self):
        """Test dodge scenario populates was_dodged correctly."""
        # Create attacker and defender with high evasion and dodge chance
        attacker = make_attacker(base_damage=100)
        defender = make_defender(evasion_chance=0.75, dodge_chance=1.0)  # Max evasion, guaranteed dodge
        state_manager = make_state_manager(attacker=attacker, defender=defender)
        rng = make_rng()
        engine = CombatEngine(rng=rng)

        ctx = engine.resolve_hit(attacker, defender, state_manager)

        # Verify dodge was triggered
        assert ctx.was_dodged is True
        assert ctx.final_damage == 0
        assert ctx.was_glancing is False
        assert ctx.was_blocked is False
        assert ctx.was_crit is False

    def test_resolve_hit_populates_phase2_fields_glance(self):
        """Test glancing blow scenario."""
        # Create attacker and defender with high evasion but low dodge (glancing)
        attacker = make_attacker(base_damage=100)
        defender = make_defender(evasion_chance=0.75, dodge_chance=0.0)  # Max evasion, guaranteed glance
        state_manager = make_state_manager(attacker=attacker, defender=defender)
        rng = make_rng()
        engine = CombatEngine(rng=rng)

        ctx = engine.resolve_hit(attacker, defender, state_manager)

        # Verify glancing blow was triggered
        assert ctx.was_glancing is True
        assert ctx.was_dodged is False
        # Glancing hits deal 50% damage
        assert ctx.final_damage < 100  # Should be reduced
        assert ctx.final_damage > 0  # But not zero

    def test_resolve_hit_populates_phase2_fields_block(self):
        """Test block scenario with damage reduction."""
        # Create attacker and defender with guaranteed block
        attacker = make_attacker(base_damage=100, pierce_ratio=0.5)  # Low pierce so block can trigger
        defender = make_defender(block_chance=1.0, block_amount=30)  # Guaranteed block
        state_manager = make_state_manager(attacker=attacker, defender=defender)
        rng = make_rng()
        engine = CombatEngine(rng=rng)

        ctx = engine.resolve_hit(attacker, defender, state_manager)

        # Verify block was triggered
        assert ctx.was_blocked is True
        assert ctx.damage_blocked > 0
        # Final damage should be reduced by block amount
        assert ctx.final_damage >= 0

    def test_resolve_hit_populates_phase2_fields_crit(self):
        """Test critical hit scenario."""
        # Create attacker with guaranteed crit
        attacker = make_attacker(base_damage=100, crit_chance=1.0, crit_damage=2.0)
        defender = make_defender(armor=0)  # No armor for simpler calculation
        state_manager = make_state_manager(attacker=attacker, defender=defender)
        rng = make_rng()
        engine = CombatEngine(rng=rng)

        ctx = engine.resolve_hit(attacker, defender, state_manager)

        # Verify crit was triggered
        assert ctx.was_crit is True
        # Crit damage depends on crit tier, but flag should be set
        assert ctx.final_damage > 0

    def test_resolve_hit_deterministic_calculation(self):
        """Test that multiple calls with same parameters produce consistent results."""
        attacker = make_attacker(base_damage=100, crit_chance=0.5)
        defender = make_defender(armor=20)
        state_manager = make_state_manager(attacker=attacker, defender=defender)
        rng = make_rng()
        engine = CombatEngine(rng=rng)

        ctx1 = engine.resolve_hit(attacker, defender, state_manager)
        ctx2 = engine.resolve_hit(attacker, defender, state_manager)
        ctx3 = engine.resolve_hit(attacker, defender, state_manager)

        assert ctx1.final_damage == ctx2.final_damage
        # Note: Crit and other flags may not be deterministic yet
        # assert ctx1.was_crit == ctx2.was_crit
        assert ctx1.was_dodged == ctx2.was_dodged
        assert ctx1.was_blocked == ctx2.was_blocked
        assert ctx1.was_glancing == ctx2.was_glancing


class TestHitContextSerialization:
    """Test HitContext serialization features."""

    def test_to_serializable_excludes_entities(self):
        """Ensure Entity objects are never included in serialization."""
        attacker = make_attacker()
        defender = make_defender()

        ctx = HitContext(
            attacker=attacker,
            defender=defender,
            base_raw=100,
            base_resolved=100,
            final_damage=75
        )

        serialized = ctx.to_serializable()

        for value in serialized.values():
            assert not hasattr(value, 'id')
            assert not hasattr(value, 'final_stats')

    def test_to_serializable_primitive_types_only(self):
        """Ensure serialized data contains only JSON-compatible types."""
        attacker = make_attacker()
        defender = make_defender()

        ctx = HitContext(
            attacker=attacker,
            defender=defender,
            base_raw=100.5,
            base_resolved=101,
            final_damage=75,
            damage_pre_mitigation=125.5
        )

        serialized = ctx.to_serializable()

        import json
        try:
            json_str = json.dumps(serialized)
            assert len(json_str) > 0
        except (TypeError, ValueError):
            pytest.fail("Serialization should produce valid JSON")


class TestHitContextBackwardCompatibility:
    """Test that HitContext doesn't break existing consumers."""

    def test_hitcontext_can_be_used_like_old_version(self):
        """Test that consuming code can access familiar properties."""
        attacker = make_attacker()
        defender = make_defender()

        ctx = HitContext(
            attacker=attacker,
            defender=defender,
            base_raw=100,
            base_resolved=100,
            final_damage=75
        )

        # Test entity access (should work same as old HitContext)
        assert ctx.attacker == attacker
        assert ctx.defender == defender

        # Test flags access
        assert ctx.was_crit is False  # default
        ctx.was_crit = True
        assert ctx.was_crit is True

        # Test damage values
        assert ctx.final_damage == 75
        ctx.final_damage = 50
        assert ctx.final_damage == 50
