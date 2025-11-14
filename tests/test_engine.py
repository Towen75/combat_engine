"""Unit tests for CombatEngine - core damage calculations."""

import pytest
from src.models import Entity, EntityStats
from src.engine import CombatEngine, HitContext


class TestCombatEngineResolveHit:
    """Test the core resolve_hit damage calculation."""

    def test_no_armor(self):
        """Test damage calculation with no armor (Unit Test 3.1)."""
        # Attacker: base_damage = 100, pierce_ratio = 0.01 (default)
        attacker_stats = EntityStats(base_damage=100.0)
        attacker = Entity(id="attacker", base_stats=attacker_stats)

        # Defender: armor = 0
        defender_stats = EntityStats(armor=0.0)
        defender = Entity(id="defender", base_stats=defender_stats)

        engine = CombatEngine()
        ctx = engine.resolve_hit(attacker, defender)
        assert ctx.final_damage == 100.0
        assert ctx.is_crit is False  # No crit with default crit_chance

    def test_high_armor_low_pierce(self):
        """Test damage with high armor and low pierce (Unit Test 3.2)."""
        # Attacker: base_damage = 100, pierce_ratio = 0.1
        attacker_stats = EntityStats(base_damage=100.0, pierce_ratio=0.1)
        attacker = Entity(id="attacker", base_stats=attacker_stats)

        # Defender: armor = 120 (higher than attack damage)
        defender_stats = EntityStats(armor=120.0)
        defender = Entity(id="defender", base_stats=defender_stats)

        # PrePierceDamage = 100 - 120 = -20
        # PiercedDamage = 100 * 0.1 = 10
        # Final = max(-20, 10) = 10
        engine = CombatEngine()
        ctx = engine.resolve_hit(attacker, defender)
        assert ctx.final_damage == 10.0

    def test_armor_greater_than_pierced_damage(self):
        """Test when armor reduction is less than pierced damage (Unit Test 3.3)."""
        # Attacker: base_damage = 100, pierce_ratio = 0.3
        attacker_stats = EntityStats(base_damage=100.0, pierce_ratio=0.3)
        attacker = Entity(id="attacker", base_stats=attacker_stats)

        # Defender: armor = 80
        defender_stats = EntityStats(armor=80.0)
        defender = Entity(id="defender", base_stats=defender_stats)

        # PrePierceDamage = 100 - 80 = 20
        # PiercedDamage = 100 * 0.3 = 30
        # Final = max(20, 30) = 30
        engine = CombatEngine()
        ctx = engine.resolve_hit(attacker, defender)
        assert ctx.final_damage == 30.0

    def test_armor_less_than_pierced_damage(self):
        """Test when armor reduction is greater than pierced damage (Unit Test 3.4)."""
        # Attacker: base_damage = 100, pierce_ratio = 0.3
        attacker_stats = EntityStats(base_damage=100.0, pierce_ratio=0.3)
        attacker = Entity(id="attacker", base_stats=attacker_stats)

        # Defender: armor = 60
        defender_stats = EntityStats(armor=60.0)
        defender = Entity(id="defender", base_stats=defender_stats)

        # PrePierceDamage = 100 - 60 = 40
        # PiercedDamage = 100 * 0.3 = 30
        # Final = max(40, 30) = 40
        engine = CombatEngine()
        ctx = engine.resolve_hit(attacker, defender)
        assert ctx.final_damage == 40.0

    def test_zero_damage_prevents_negative(self):
        """Test that damage calculation never returns negative values."""
        # Attacker: base_damage = 50, pierce_ratio = 0.01 (default)
        attacker_stats = EntityStats(base_damage=50.0)
        attacker = Entity(id="attacker", base_stats=attacker_stats)

        # Defender: armor = 100 (much higher than attack)
        defender_stats = EntityStats(armor=100.0)
        defender = Entity(id="defender", base_stats=defender_stats)

        # PrePierceDamage = 50 - 100 = -50
        # PiercedDamage = 50 * 0.01 = 0.5
        # Final = max(-50, 0.5) = 0.5, then max(0, 0.5) = 0.5
        engine = CombatEngine()
        ctx = engine.resolve_hit(attacker, defender)
        assert ctx.final_damage == 0.5

    def test_minimum_pierce_ratio(self):
        """Test damage calculation with minimum pierce ratio."""
        # Attacker: base_damage = 100, pierce_ratio = 0.01 (minimum)
        attacker_stats = EntityStats(base_damage=100.0, pierce_ratio=0.01)
        attacker = Entity(id="attacker", base_stats=attacker_stats)

        # Defender: armor = 50
        defender_stats = EntityStats(armor=50.0)
        defender = Entity(id="defender", base_stats=defender_stats)

        # PrePierceDamage = 100 - 50 = 50
        # PiercedDamage = 100 * 0.01 = 1
        # Final = max(50, 1) = 50
        engine = CombatEngine()
        ctx = engine.resolve_hit(attacker, defender)
        assert ctx.final_damage == 50.0


class TestCombatEngineCalculateEffectiveDamage:
    """Test the detailed damage breakdown calculation."""

    def test_damage_breakdown_no_armor(self):
        """Test detailed breakdown with no armor."""
        attacker_stats = EntityStats(base_damage=100.0, pierce_ratio=0.2)
        attacker = Entity(id="attacker", base_stats=attacker_stats)

        defender_stats = EntityStats(armor=0.0)
        defender = Entity(id="defender", base_stats=defender_stats)

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
        attacker = Entity(id="attacker", base_stats=attacker_stats)

        defender_stats = EntityStats(armor=80.0)
        defender = Entity(id="defender", base_stats=defender_stats)

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
        attacker = Entity(id="attacker", base_stats=attacker_stats)

        defender_stats = EntityStats(armor=120.0)
        defender = Entity(id="defender", base_stats=defender_stats)

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
        attacker = Entity(id="attacker", base_stats=attacker_stats)

        defender_stats = EntityStats(armor=50.0)
        defender = Entity(id="defender", base_stats=defender_stats)

        error = CombatEngine.validate_damage_calculation(attacker, defender)
        assert error is None

    def test_validation_pierce_ratio_above_maximum(self):
        """Test validation of pierce_ratio above maximum (1.0)."""
        attacker_stats = EntityStats(base_damage=100.0, pierce_ratio=1.5)
        attacker = Entity(id="attacker", base_stats=attacker_stats)

        defender_stats = EntityStats(armor=50.0)
        defender = Entity(id="defender", base_stats=defender_stats)

        error = CombatEngine.validate_damage_calculation(attacker, defender)
        assert error == "Attacker pierce_ratio above maximum: 1.5"

    def test_validation_pierce_ratio_at_maximum(self):
        """Test validation accepts pierce_ratio at maximum (1.0)."""
        attacker_stats = EntityStats(base_damage=100.0, pierce_ratio=1.0)
        attacker = Entity(id="attacker", base_stats=attacker_stats)

        defender_stats = EntityStats(armor=50.0)
        defender = Entity(id="defender", base_stats=defender_stats)

        error = CombatEngine.validate_damage_calculation(attacker, defender)
        assert error is None

    def test_validation_edge_cases(self):
        """Test validation of edge cases and boundary conditions."""
        # Test pierce_ratio at minimum
        attacker_stats = EntityStats(base_damage=100.0, pierce_ratio=0.01)
        attacker = Entity(id="attacker", base_stats=attacker_stats)
        defender_stats = EntityStats(armor=50.0)
        defender = Entity(id="defender", base_stats=defender_stats)

        error = CombatEngine.validate_damage_calculation(attacker, defender)
        assert error is None

        # Test zero armor (should be valid)
        defender_stats = EntityStats(armor=0.0)
        defender = Entity(id="defender", base_stats=defender_stats)

        error = CombatEngine.validate_damage_calculation(attacker, defender)
        assert error is None

    # Note: Additional validation tests for negative values removed since EntityStats dataclass
    # already validates these conditions at creation time, making CombatEngine
    # validation redundant for those cases.


class TestCombatEngineCriticalHits:
    """Test critical hit functionality."""

    def test_critical_hit_tier_1_common(self):
        """Test that Common rarity entities have crit tier 1 (no special crit effects)."""
        from tests.fixtures import make_rng

        attacker_stats = EntityStats(base_damage=100.0, crit_chance=1.0, crit_damage=2.0)
        attacker = Entity(id="attacker", base_stats=attacker_stats, rarity="Common")

        defender_stats = EntityStats(armor=0.0)
        defender = Entity(id="defender", base_stats=defender_stats)

        engine = CombatEngine(rng=make_rng(42))  # Deterministic crit
        ctx = engine.resolve_hit(attacker, defender)

        assert ctx.is_crit is True
        assert ctx.final_damage == 100.0  # No crit multiplier applied for tier 1
        assert attacker.get_crit_tier() == 1

    def test_critical_hit_tier_2_rare(self):
        """Test that Rare rarity entities have crit tier 2 (pre-pierce multiplier)."""
        from tests.fixtures import make_rng

        attacker_stats = EntityStats(base_damage=100.0, crit_chance=1.0, crit_damage=2.0)
        attacker = Entity(id="attacker", base_stats=attacker_stats, rarity="Rare")

        defender_stats = EntityStats(armor=50.0)
        defender = Entity(id="defender", base_stats=defender_stats)

        engine = CombatEngine(rng=make_rng(42))  # Deterministic crit
        ctx = engine.resolve_hit(attacker, defender)

        assert ctx.is_crit is True
        assert ctx.final_damage == 150.0  # (100 * 2.0 - 50) = 150, max(150, 100 * 0.01) = 150
        assert attacker.get_crit_tier() == 2

    def test_critical_hit_tier_3_legendary(self):
        """Test that Legendary rarity entities have crit tier 3 (post-pierce multiplier)."""
        from tests.fixtures import make_rng

        attacker_stats = EntityStats(base_damage=100.0, crit_chance=1.0, crit_damage=2.0, pierce_ratio=0.2)
        attacker = Entity(id="attacker", base_stats=attacker_stats, rarity="Legendary")

        defender_stats = EntityStats(armor=50.0)
        defender = Entity(id="defender", base_stats=defender_stats)

        engine = CombatEngine(rng=make_rng(42))  # Deterministic crit
        ctx = engine.resolve_hit(attacker, defender)

        assert ctx.is_crit is True
        # Tier 3: Re-calculates with crit damage applied to pierce as well
        # crit_pre_mit = 100 * 2.0 = 200
        # pre_pierce = 200 - 50 = 150
        # pierced = 200 * 0.2 = 40
        # final = max(150, 40) = 150
        assert ctx.final_damage == 150.0
        assert attacker.get_crit_tier() == 3

    def test_no_critical_hit_when_chance_zero(self):
        """Test that no crit occurs when crit_chance is 0."""
        from tests.fixtures import make_rng

        attacker_stats = EntityStats(base_damage=100.0, crit_chance=0.0, crit_damage=2.0)
        attacker = Entity(id="attacker", base_stats=attacker_stats, rarity="Legendary")

        defender_stats = EntityStats(armor=0.0)
        defender = Entity(id="defender", base_stats=defender_stats)

        engine = CombatEngine(rng=make_rng(42))
        ctx = engine.resolve_hit(attacker, defender)

        assert ctx.is_crit is False
        assert ctx.final_damage == 100.0


class TestHitContext:
    """Test the HitContext data structure."""

    def test_hit_context_creation(self):
        """Test HitContext can be created with required fields."""
        attacker_stats = EntityStats()
        defender_stats = EntityStats()
        attacker = Entity("attacker", base_stats=attacker_stats)
        defender = Entity("defender", base_stats=defender_stats)

        ctx = HitContext(
            attacker=attacker,
            defender=defender,
            base_damage=100.0
        )

        assert ctx.attacker == attacker
        assert ctx.defender == defender
        assert ctx.base_damage == 100.0
        assert ctx.pre_mitigation_damage == 0.0
        assert ctx.mitigated_damage == 0.0
        assert ctx.final_damage == 0.0
        assert ctx.is_crit is False

    def test_final_damage_always_assigned(self):
        """Test that ctx.final_damage is always assigned in all code paths."""
        from tests.fixtures import make_rng

        attacker_stats = EntityStats(base_damage=100.0, crit_chance=1.0, crit_damage=2.0)
        defender_stats = EntityStats(armor=50.0)

        # Test all rarity tiers with guaranteed crits
        for rarity in ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]:
            attacker = Entity(id="attacker", base_stats=attacker_stats, rarity=rarity)
            defender = Entity(id="defender", base_stats=defender_stats)

            engine = CombatEngine(rng=make_rng(42))  # Deterministic crit
            ctx = engine.resolve_hit(attacker, defender)

            # final_damage should always be set and non-negative
            assert ctx.final_damage is not None
            assert ctx.final_damage >= 0.0
            assert isinstance(ctx.final_damage, float)

    def test_tier_3_post_pierce_crit_recalculation(self):
        """Test that Tier 3 crits properly recalculate damage with pierce."""
        from tests.fixtures import make_rng

        # Legendary = Tier 3 crit
        attacker_stats = EntityStats(
            base_damage=100.0,
            crit_chance=1.0,
            crit_damage=2.0,
            pierce_ratio=0.2
        )
        attacker = Entity(id="attacker", base_stats=attacker_stats, rarity="Legendary")

        defender_stats = EntityStats(armor=50.0)
        defender = Entity(id="defender", base_stats=defender_stats)

        engine = CombatEngine(rng=make_rng(42))  # Deterministic crit
        ctx = engine.resolve_hit(attacker, defender)

        assert ctx.is_crit is True
        assert attacker.get_crit_tier() == 3

        # Tier 3 calculation:
        # crit_pre_mit = 100 * 2.0 = 200
        # pre_pierce = 200 - 50 = 150
        # pierced = 200 * 0.2 = 40
        # final = max(150, 40) = 150
        assert ctx.final_damage == 150.0

    def test_non_crit_damage_assignment(self):
        """Test that non-crit hits properly assign mitigated_damage to final_damage."""
        from tests.fixtures import make_rng

        attacker_stats = EntityStats(base_damage=100.0, crit_chance=0.0)  # No crit chance
        attacker = Entity(id="attacker", base_stats=attacker_stats, rarity="Common")

        defender_stats = EntityStats(armor=30.0)
        defender = Entity(id="defender", base_stats=defender_stats)

        engine = CombatEngine(rng=make_rng(42))
        ctx = engine.resolve_hit(attacker, defender)

        assert ctx.is_crit is False
        # Should be: max(100-30, 100*0.01) = max(70, 1) = 70
        assert ctx.final_damage == 70.0


class TestCombatEngineCalculateSkillUse:
    """Test the new calculate_skill_use method that returns SkillUseResult."""

    def test_calculate_skill_use_basic_skill(self):
        """Test calculate_skill_use with a basic single-hit skill."""
        from tests.fixtures import make_entity, make_rng
        from src.models import SkillUseResult

        attacker = make_entity("attacker")
        defender = make_entity("defender")

        # Create a simple skill with 1 hit and no triggers
        skill = type('Skill', (), {
            'hits': 1,
            'name': 'basic_attack',
            'triggers': []
        })()

        engine = CombatEngine(rng=make_rng(42))  # Deterministic for testing
        result = engine.calculate_skill_use(attacker, defender, skill)

        # Should return a SkillUseResult with 1 hit and 3 actions (damage + hit event + possible crit event)
        assert isinstance(result, SkillUseResult)
        assert len(result.hit_results) == 1

        # Actions: ApplyDamageAction + DispatchEventAction (OnHitEvent)
        # Since this is not a crit (default crit_chance=0.05), no crit event
        assert len(result.actions) == 2

        # First action should be damage application
        from src.models import ApplyDamageAction, DispatchEventAction
        damage_action = result.actions[0]
        assert isinstance(damage_action, ApplyDamageAction)
        assert damage_action.target_id == defender.id
        assert damage_action.damage == 50.0  # Default base_damage from fixtures
        assert damage_action.source == "basic_attack"

        # Second action should be OnHit event dispatch
        event_action = result.actions[1]
        assert isinstance(event_action, DispatchEventAction)
        assert hasattr(event_action, 'event')
        assert event_action.event.attacker == attacker
        assert event_action.event.defender == defender

    def test_calculate_skill_use_multi_hit_skill(self):
        """Test calculate_skill_use with a multi-hit skill."""
        from tests.fixtures import make_entity, make_rng

        attacker = make_entity("attacker")
        defender = make_entity("defender")

        # Create a skill with 3 hits
        skill = type('Skill', (), {
            'hits': 3,
            'name': 'triple_slash',
            'triggers': []
        })()

        engine = CombatEngine(rng=make_rng(42))
        result = engine.calculate_skill_use(attacker, defender, skill)

        assert len(result.hit_results) == 3
        # Each hit: 1 damage action + 1-2 event actions = 6-9 total actions
        assert len(result.actions) >= 6  # Minimum without crits

        # Verify hit contexts
        for hit_ctx in result.hit_results:
            assert hit_ctx.attacker == attacker
            assert hit_ctx.defender == defender
            assert hit_ctx.base_damage == 100.0  # Default base_damage from fixtures

    def test_calculate_skill_use_with_crit(self):
        """Test calculate_skill_use with guaranteed critical hit."""
        from tests.fixtures import make_entity, make_rng

        # Create attacker with guaranteed crit (Rare for tier 2 crits)
        attacker = make_entity("attacker", base_damage=50.0, crit_chance=1.0, crit_damage=2.0, rarity="Rare")
        defender = make_entity("defender")

        skill = type('Skill', (), {
            'hits': 1,
            'name': 'crit_attack',
            'triggers': []
        })()

        engine = CombatEngine(rng=make_rng(42))  # Deterministic crit
        result = engine.calculate_skill_use(attacker, defender, skill)

        assert len(result.hit_results) == 1
        hit_ctx = result.hit_results[0]
        assert hit_ctx.is_crit is True
        # Rare = tier 2 crit: pre-pierce multiplier
        # Base damage: 50 * crit(2.0) = 100, minus defender armor(50) = 50, max with pierced(1)
        assert hit_ctx.final_damage == 50.0

        # Actions: 1 damage + 2 events (OnHit + OnCrit)
        assert len(result.actions) == 3

    def test_calculate_skill_use_with_trigger(self):
        """Test calculate_skill_use with a skill trigger."""
        from tests.fixtures import make_entity, make_rng
        from src.models import ApplyEffectAction

        attacker = make_entity("attacker")
        defender = make_entity("defender")

        # Create a skill with 1 hit and 1 trigger (OnHit apply bleed)
        # The engine expects triggers to be objects with attributes, not dicts
        trigger_obj = type('Trigger', (), {
            'event': 'OnHit',
            'check': {'proc_rate': 1.0},  # Guaranteed to trigger for testing
            'result': {'apply_debuff': 'bleed', 'stacks': 2}  # This matches what engine expects
        })()

        skill = type('Skill', (), {
            'hits': 1,
            'name': 'bleed_attack',
            'triggers': [trigger_obj]
        })()

        engine = CombatEngine(rng=make_rng(42))
        result = engine.calculate_skill_use(attacker, defender, skill)

        assert len(result.hit_results) == 1
        # Actions: 1 damage + 1 OnHit event + 1 ApplyEffect
        assert len(result.actions) == 3

        # Last action should be the effect application
        effect_action = result.actions[2]
        assert isinstance(effect_action, ApplyEffectAction)
        assert effect_action.target_id == defender.id
        assert effect_action.effect_name == "bleed"
        assert effect_action.stacks_to_add == 2
        assert effect_action.source == "bleed_attack_trigger"

    def test_calculate_skill_use_detached_from_execution(self):
        """Test that calculate_skill_use performs no side effects."""
        from tests.fixtures import make_entity, make_rng
        from unittest.mock import patch, MagicMock

        attacker = make_entity("attacker")
        defender = make_entity("defender")

        skill = type('Skill', (), {
            'hits': 1,
            'name': 'test_skill',
            'triggers': []
        })()

        # Mock StateManager and EventBus to ensure they're not called
        with patch('src.engine.StateManager') as mock_state_manager, \
             patch('src.engine.EventBus') as mock_event_bus:

            engine = CombatEngine(rng=make_rng(42))
            result = engine.calculate_skill_use(attacker, defender, skill)

            # Verify no methods were called on the mocks during calculation
            mock_state_manager.assert_not_called()
            mock_event_bus.assert_not_called()

        # Verify result is still valid (don't perform isinstance check on mock objects)
        assert hasattr(result, 'hit_results') and hasattr(result, 'actions')
        assert len(result.hit_results) == 1
        assert len(result.actions) >= 2  # At least damage and event actions
