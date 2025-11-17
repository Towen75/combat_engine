"""Tests for HitContext telemetry dataclass."""

import pytest
from src.engine.hit_context import HitContext
from src import engine as main_engine  # Import the engine module directly
from src.models import Entity, EntityStats
from tests.fixtures import make_attacker, make_defender, make_rng, make_state_manager


class TestHitContextBasics:
    """Test basic HitContext functionality."""

    def test_hitcontext_creation_with_entities(self):
        """Test HitContext can be created with required fields."""
        attacker = make_attacker()
        defender = make_defender()

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
        assert ctx.final_damage == 100  # default value
        assert ctx.was_crit is False
        assert ctx.was_dodged is False
        assert ctx.was_blocked is False
        assert ctx.was_glancing is False

    def test_hitcontext_property_accessors(self):
        """Test derived property accessors work correctly."""
        attacker = make_attacker()
        defender = make_defender()

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

    def test_to_serializable(self):
        """Test JSON-safe representation works correctly."""
        attacker = make_attacker()
        defender = make_defender()

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

        # Set up for guaranteed dodge
        attacker = make_attacker(base_damage=100)
        defender = make_defender(armor=0, evasion_chance=1.0, dodge_chance=1.0)  # 100% dodge

        state_manager = make_state_manager(attacker=attacker, defender=defender)
        engine = main_engine.CombatEngine(rng=make_rng())

        ctx = engine.resolve_hit(attacker, defender, state_manager)

        assert ctx.was_dodged is True
        assert ctx.final_damage == 0.0
        assert ctx.was_crit is False  # Can't crit on dodge
        assert ctx.was_glancing is False

    def test_resolve_hit_populates_phase2_fields_glance(self, make_attacker, make_defender, make_state_manager, make_rng):
        """Test glancing blow scenario."""

        # Set up for guaranteed glance (evade but not dodge)
        attacker = make_attacker(base_damage=100)
        defender = make_defender(armor=0, evasion_chance=1.0, dodge_chance=0.0)  # 100% evade, 0% dodge

        state_manager = make_state_manager(attacker=attacker, defender=defender)
        engine = main_engine.CombatEngine(rng=make_rng())

        ctx = engine.resolve_hit(attacker, defender, state_manager)

        assert ctx.was_dodged is False
        assert ctx.was_glancing is True
        assert ctx.final_damage == 50.0  # 100 * 0.5
        assert ctx.was_crit is False  # Can't crit on glance

    def test_resolve_hit_populates_phase2_fields_block(self, make_attacker, make_defender, make_state_manager, make_rng):
        """Test block scenario with damage reduction."""

        # Set up normal hit that gets blocked
        attacker = make_attacker(base_damage=100, pierce_ratio=0.5)  # Pierce to ensure some damage
        defender = make_defender(armor=0, block_chance=1.0, block_amount=25)  # 100% block, 25 flat reduction

        state_manager = make_state_manager(attacker=attacker, defender=defender)
        engine = main_engine.CombatEngine(rng=make_rng())

        ctx = engine.resolve_hit(attacker, defender, state_manager)

        assert ctx.was_blocked is True
        assert ctx.damage_blocked == 25
        # Calculate expected damage: pierce damage formula max(100-0, 100*0.5) = 100, minus block 25 = 75
        assert ctx.final_damage == 75.0
        assert ctx.was_dodged is False
        assert ctx.was_glancing is False

    def test_resolve_hit_populates_phase2_fields_crit(self, make_attacker, make_defender, make_state_manager, make_rng):
        """Test critical hit scenario."""

        # Set up normal hit that crits
        attacker = make_attacker(base_damage=100, crit_chance=1.0, crit_damage=2.0)  # 100% crit, 2.0x damage
        defender = make_defender(armor=0)

        state_manager = make_state_manager(attacker=attacker, defender=defender)
        engine = main_engine.CombatEngine(rng=make_rng())

        ctx = engine.resolve_hit(attacker, defender, state_manager)

        assert ctx.was_crit is True
        assert ctx.final_damage == 200.0  # 100 * 2.0
        assert ctx.was_dodged is False
        assert ctx.was_glancing is False
        assert ctx.was_blocked is False

    def test_resolve_hit_deterministic_calculation(self, make_attacker, make_defender, make_state_manager):
        """Test that multiple calls with same parameters produce consistent results."""

        attacker = make_attacker(base_damage=100, crit_chance=0.5)
        defender = make_defender(armor=20)

        state_manager = make_state_manager(attacker=attacker, defender=defender)
        rng = make_rng()  # Use same seed for deterministic testing
        engine = main_engine.CombatEngine(rng=rng)

        # Run same calculation multiple times
        ctx1 = engine.resolve_hit(attacker, defender, state_manager)
        ctx2 = engine.resolve_hit(attacker, defender, state_manager)
        ctx3 = engine.resolve_hit(attacker, defender, state_manager)

        # Should be identical results for same inputs
        assert ctx1.final_damage == ctx2.final_damage
        assert ctx1.was_crit == ctx2.was_crit
        assert ctx1.was_dodged == ctx2.was_dodged
        assert ctx1.was_blocked == ctx2.was_blocked
        assert ctx1.was_glancing == ctx2.was_glancing


class TestHitContextSerialization:
    """Test HitContext serialization features."""

    def test_to_serializable_excludes_entities(self, make_attacker, make_defender):
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

        # Should not contain Entity objects
        for value in serialized.values():
            assert not hasattr(value, 'id')  # No Entity-like objects
            assert not hasattr(value, 'final_stats')  # No Entity-like objects

    def test_to_serializable_primitive_types_only(self, make_attacker, make_defender):
        """Ensure serialized data contains only JSON-compatible types."""
        attacker = make_attacker()
        defender = make_defender()

        ctx = HitContext(
            attacker=attacker,
            defender=defender,
            base_raw=100.5,  # float
            base_resolved=101,
            final_damage=75,
            damage_pre_mitigation=125.5
        )

        serialized = ctx.to_serializable()

        # All values should be JSON-serializable
        import json
        try:
            json_str = json.dumps(serialized)
            assert len(json_str) > 0
        except (TypeError, ValueError):
            pytest.fail("Serialization should produce valid JSON")


class TestHitContextBackwardCompatibility:
    """Test that HitContext doesn't break existing consumers."""

    def test_hitcontext_can_be_used_like_old_version(self, make_attacker, make_defender):
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
