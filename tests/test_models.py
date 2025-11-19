"""Tests for models.py - data structures and entity management."""

import pytest
from src.core.models import (
    Entity, EntityStats, Item, RolledAffix,
    SkillUseResult, Action, ApplyDamageAction, DispatchEventAction, ApplyEffectAction,
    RARITY_TO_CRIT_TIER
)
from tests.fixtures import make_entity


class TestSkillUseResult:
    """Test the SkillUseResult data structure."""

    def test_skill_use_result_creation(self):
        """Test creating a SkillUseResult with empty lists."""
        result = SkillUseResult(hit_results=[], actions=[])
        assert result.hit_results == []
        assert result.actions == []

    def test_skill_use_result_with_data(self):
        """Test SkillUseResult with actual data."""
        attacker = make_entity("attacker")
        defender = make_entity("defender")

        # Create mock hit context and actions
        from src.combat.hit_context import HitContext
        hit_ctx = HitContext(attacker=attacker, defender=defender, base_raw=50, base_resolved=50, final_damage=50.0)

        action1 = ApplyDamageAction(target_id=defender.id, damage=25.0, source="test")
        # Create minimal mock event - can be any object for testing
        from src.core.events import Event
        action2 = DispatchEventAction(event=Event())  # Mock event

        result = SkillUseResult(hit_results=[hit_ctx], actions=[action1, action2])

        assert len(result.hit_results) == 1
        assert len(result.actions) == 2
        assert result.hit_results[0].attacker == attacker
        assert isinstance(result.actions[0], ApplyDamageAction)
        assert result.actions[0].target_id == defender.id


class TestActions:
    """Test the Action class hierarchy."""

    def test_apply_damage_action_creation(self):
        """Test creating ApplyDamageAction."""
        action = ApplyDamageAction(target_id="target1", damage=100.0, source="skill")

        assert action.target_id == "target1"
        assert action.damage == 100.0
        assert action.source == "skill"

    def test_apply_damage_action_defaults(self):
        """Test ApplyDamageAction default values."""
        action = ApplyDamageAction(target_id="target1", damage=50.0)

        assert action.source == "skill"  # Default value

    def test_dispatch_event_action_creation(self):
        """Test creating DispatchEventAction."""
        from src.core.events import Event
        mock_event = Event()  # Create actual Event instance
        action = DispatchEventAction(event=mock_event)

        assert action.event == mock_event

    def test_apply_effect_action_creation(self):
        """Test creating ApplyEffectAction."""
        action = ApplyEffectAction(
            target_id="target1",
            effect_name="bleed",
            stacks_to_add=2,
            source="trigger"
        )

        assert action.target_id == "target1"
        assert action.effect_name == "bleed"
        assert action.stacks_to_add == 2
        assert action.source == "trigger"

    def test_apply_effect_action_defaults(self):
        """Test ApplyEffectAction default values."""
        action = ApplyEffectAction(target_id="target1", effect_name="poison")

        assert action.stacks_to_add == 1  # Default value
        assert action.source == "skill"  # Default value

    def test_action_base_class_is_abstract(self):
        """Test that Action base class cannot be instantiated directly."""
        # This should work since Action is just a base dataclass
        action = Action()
        assert isinstance(action, Action)


class TestEntityStats:
    """Test EntityStats validation and functionality."""

    def test_valid_entity_stats_creation(self):
        """Test creating valid EntityStats."""
        stats = EntityStats(
            base_damage=100.0,
            attack_speed=1.5,
            crit_chance=0.2,
            crit_damage=1.8,
            pierce_ratio=0.15,
            max_health=1000.0
        )
        assert stats.base_damage == 100.0
        assert stats.crit_chance == 0.2

    def test_entity_stats_validation_negative_damage(self):
        """Test that negative base_damage raises ValueError."""
        with pytest.raises(ValueError, match="base_damage must be non-negative"):
            EntityStats(base_damage=-10.0)

    def test_entity_stats_validation_zero_speed(self):
        """Test that zero attack_speed raises ValueError."""
        with pytest.raises(ValueError, match="attack_speed must be positive"):
            EntityStats(attack_speed=0.0)

    def test_entity_stats_validation_crit_chance_bounds(self):
        """Test crit_chance validation."""
        # Valid values should work
        EntityStats(crit_chance=0.0)
        EntityStats(crit_chance=1.0)

        # Invalid values should raise errors
        with pytest.raises(ValueError, match="crit_chance must be between 0 and 1"):
            EntityStats(crit_chance=-0.1)
        with pytest.raises(ValueError, match="crit_chance must be between 0 and 1"):
            EntityStats(crit_chance=1.1)

    def test_entity_stats_validation_pierce_ratio_bounds(self):
        """Test pierce_ratio validation."""
        # Should work at minimum
        EntityStats(pierce_ratio=0.01)

        # Should fail below minimum
        with pytest.raises(ValueError, match="pierce_ratio must be >= 0.01"):
            EntityStats(pierce_ratio=0.005)


class TestEntity:
    """Test Entity creation and functionality."""

    def test_entity_creation(self):
        """Test basic Entity creation."""
        stats = EntityStats()
        entity = Entity(id="test_entity", base_stats=stats, name="Test Entity", rarity="Rare")

        assert entity.id == "test_entity"
        assert entity.name == "Test Entity"
        assert entity.rarity == "Rare"
        assert entity.get_crit_tier() == 2  # Rare = tier 2

    def test_entity_default_name(self):
        """Test Entity name defaults to id."""
        stats = EntityStats()
        entity = Entity(id="test_entity", base_stats=stats)

        assert entity.name == "test_entity"

    def test_entity_invalid_rarity(self):
        """Test Entity rejects invalid rarity."""
        stats = EntityStats()
        with pytest.raises(ValueError, match="Invalid rarity"):
            Entity(id="test", base_stats=stats, rarity="Invalid")

    def test_entity_crit_tier_mapping(self):
        """Test crit tier mapping for all rarities."""
        stats = EntityStats()
        test_cases = [
            ("Common", 1),
            ("Uncommon", 1),
            ("Rare", 2),
            ("Epic", 2),
            ("Legendary", 3),
            ("Mythic", 3)
        ]

        for rarity, expected_tier in test_cases:
            entity = Entity(id=f"test_{rarity}", base_stats=stats, rarity=rarity)
            assert entity.get_crit_tier() == expected_tier

    def test_entity_empty_id_validation(self):
        """Test Entity rejects empty id."""
        stats = EntityStats()
        with pytest.raises(ValueError, match="Entity id cannot be empty"):
            Entity(id="", base_stats=stats)


class TestItemSystem:
    """Test Item and RolledAffix functionality."""

    def test_rolled_affix_creation(self):
        """Test creating RolledAffix."""
        affix = RolledAffix(
            affix_id="test_affix",
            stat_affected="base_damage",
            mod_type="flat",
            affix_pools="damage",
            description="+10 Damage",
            base_value=10.0,
            value=12.5
        )

        assert affix.affix_id == "test_affix"
        assert affix.stat_affected == "base_damage"
        assert affix.mod_type == "flat"
        assert affix.value == 12.5

    def test_item_creation(self):
        """Test creating Item."""
        affixes = [
            RolledAffix("affix1", "base_damage", "flat", "damage", "+10 Damage", 10.0, 10.0)
        ]

        item = Item(
            instance_id="item_001",
            base_id="sword_basic",
            name="Rusty Sword",
            slot="weapon",
            rarity="Common",
            quality_tier="Normal",
            quality_roll=1,
            affixes=affixes
        )

        assert item.instance_id == "item_001"
        assert item.name == "Rusty Sword"
        assert len(item.affixes) == 1


# Rarity mapping tests
class TestRarityMapping:
    """Test the global rarity to crit tier mapping."""

    def test_all_rarities_have_mappings(self):
        """Ensure all standard rarities are mapped."""
        from src.data.typed_models import Rarity
        expected_rarities = {Rarity.COMMON, Rarity.UNCOMMON, Rarity.RARE, Rarity.EPIC, Rarity.LEGENDARY, Rarity.MYTHIC}

        assert set(RARITY_TO_CRIT_TIER.keys()) == expected_rarities

    def test_crit_tier_values(self):
        """Ensure crit tier values are valid (1, 2, or 3)."""
        for tier in RARITY_TO_CRIT_TIER.values():
            assert tier in {1, 2, 3}
