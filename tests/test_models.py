"""Unit tests for data models (Entity, EntityStats, Affix, Item)."""

import pytest
from src.models import Entity, EntityStats, Affix, Item


class TestEntityStats:
    """Test the EntityStats dataclass."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        stats = EntityStats()
        assert stats.base_damage == 10.0
        assert stats.attack_speed == 1.0
        assert stats.crit_chance == 0.05
        assert stats.crit_damage == 1.5
        assert stats.pierce_ratio == 0.01
        assert stats.max_health == 100.0
        assert stats.armor == 10.0
        assert stats.resistances == 0.0

    def test_custom_values(self):
        """Test that custom values are set correctly."""
        stats = EntityStats(
            base_damage=50.0,
            attack_speed=1.5,
            crit_chance=0.25,
            crit_damage=2.0,
            pierce_ratio=0.2,
            max_health=500.0,
            armor=25.0,
            resistances=10.0
        )
        assert stats.base_damage == 50.0
        assert stats.attack_speed == 1.5
        assert stats.crit_chance == 0.25
        assert stats.crit_damage == 2.0
        assert stats.pierce_ratio == 0.2
        assert stats.max_health == 500.0
        assert stats.armor == 25.0
        assert stats.resistances == 10.0

    def test_validation_negative_base_damage(self):
        """Test that negative base_damage raises ValueError."""
        with pytest.raises(ValueError, match="base_damage must be non-negative"):
            EntityStats(base_damage=-10.0)

    def test_validation_zero_attack_speed(self):
        """Test that zero attack_speed raises ValueError."""
        with pytest.raises(ValueError, match="attack_speed must be positive"):
            EntityStats(attack_speed=0)

    def test_validation_negative_attack_speed(self):
        """Test that negative attack_speed raises ValueError."""
        with pytest.raises(ValueError, match="attack_speed must be positive"):
            EntityStats(attack_speed=-1.0)

    def test_validation_crit_chance_below_zero(self):
        """Test that crit_chance below 0 raises ValueError."""
        with pytest.raises(ValueError, match="crit_chance must be between 0 and 1"):
            EntityStats(crit_chance=-0.1)

    def test_validation_crit_chance_above_one(self):
        """Test that crit_chance above 1 raises ValueError."""
        with pytest.raises(ValueError, match="crit_chance must be between 0 and 1"):
            EntityStats(crit_chance=1.5)

    def test_validation_crit_damage_below_one(self):
        """Test that crit_damage below 1 raises ValueError."""
        with pytest.raises(ValueError, match="crit_damage must be >= 1"):
            EntityStats(crit_damage=0.8)

    def test_validation_pierce_ratio_below_minimum(self):
        """Test that pierce_ratio below 0.01 raises ValueError."""
        with pytest.raises(ValueError, match="pierce_ratio must be >= 0.01"):
            EntityStats(pierce_ratio=0.005)

    def test_validation_zero_max_health(self):
        """Test that zero max_health raises ValueError."""
        with pytest.raises(ValueError, match="max_health must be positive"):
            EntityStats(max_health=0)

    def test_validation_negative_max_health(self):
        """Test that negative max_health raises ValueError."""
        with pytest.raises(ValueError, match="max_health must be positive"):
            EntityStats(max_health=-100.0)

    def test_validation_negative_armor(self):
        """Test that negative armor raises ValueError."""
        with pytest.raises(ValueError, match="armor must be non-negative"):
            EntityStats(armor=-5.0)

    def test_validation_negative_resistances(self):
        """Test that negative resistances raises ValueError."""
        with pytest.raises(ValueError, match="resistances must be non-negative"):
            EntityStats(resistances=-10.0)


class TestEntity:
    """Test the Entity class."""

    def test_entity_creation_with_defaults(self):
        """Test creating an Entity with default EntityStats."""
        stats = EntityStats()
        entity = Entity(id="test_entity", base_stats=stats)

        assert entity.id == "test_entity"
        assert entity.name == "test_entity"
        assert entity.base_stats == stats

    def test_entity_creation_with_custom_name(self):
        """Test creating an Entity with a custom name."""
        stats = EntityStats()
        entity = Entity(id="test_entity", base_stats=stats, name="Test Entity")

        assert entity.id == "test_entity"
        assert entity.name == "Test Entity"
        assert entity.base_stats == stats

    def test_entity_creation_with_custom_stats(self):
        """Test creating an Entity with custom EntityStats."""
        stats = EntityStats(base_damage=100.0, max_health=200.0)
        entity = Entity(id="strong_entity", base_stats=stats)

        assert entity.id == "strong_entity"
        assert entity.base_stats.base_damage == 100.0
        assert entity.base_stats.max_health == 200.0

    def test_entity_empty_id_raises_error(self):
        """Test that empty id raises ValueError."""
        stats = EntityStats()
        with pytest.raises(ValueError, match="Entity id cannot be empty"):
            Entity(id="", base_stats=stats)

    def test_entity_repr(self):
        """Test Entity string representation."""
        stats = EntityStats()
        entity = Entity(id="test_entity", base_stats=stats, name="Test Entity")

        expected = "Entity(id='test_entity', name='Test Entity')"
        assert repr(entity) == expected

    def test_entity_str(self):
        """Test Entity string conversion."""
        stats = EntityStats()
        entity = Entity(id="test_entity", base_stats=stats, name="Test Entity")

        assert str(entity) == "Test Entity"

    def test_entity_str_defaults_to_id(self):
        """Test that str() defaults to id when no name is provided."""
        stats = EntityStats()
        entity = Entity(id="test_entity", base_stats=stats)

        assert str(entity) == "test_entity"


class TestAffix:
    """Test the Affix dataclass."""

    def test_affix_creation_flat(self):
        """Test creating a flat affix."""
        affix = Affix(stat="base_damage", mod_type="flat", value=20.0)

        assert affix.stat == "base_damage"
        assert affix.mod_type == "flat"
        assert affix.value == 20.0

    def test_affix_creation_multiplier(self):
        """Test creating a multiplier affix."""
        affix = Affix(stat="crit_chance", mod_type="multiplier", value=1.25)

        assert affix.stat == "crit_chance"
        assert affix.mod_type == "multiplier"
        assert affix.value == 1.25


class TestItem:
    """Test the Item dataclass."""

    def test_item_creation_with_affixes(self):
        """Test creating an item with multiple affixes."""
        affixes = [
            Affix(stat="base_damage", mod_type="flat", value=15.0),
            Affix(stat="crit_chance", mod_type="flat", value=0.1),
            Affix(stat="armor", mod_type="multiplier", value=1.2)
        ]

        item = Item(id="sword_01", name="Vicious Sword", slot="Weapon", affixes=affixes)

        assert item.id == "sword_01"
        assert item.name == "Vicious Sword"
        assert item.slot == "Weapon"
        assert len(item.affixes) == 3
        assert item.affixes[0].stat == "base_damage"
        assert item.affixes[0].mod_type == "flat"
        assert item.affixes[0].value == 15.0

    def test_item_creation_empty_affixes(self):
        """Test creating an item with no affixes."""
        item = Item(id="plain_sword", name="Plain Sword", slot="Weapon", affixes=[])

        assert item.id == "plain_sword"
        assert item.name == "Plain Sword"
        assert item.slot == "Weapon"
        assert len(item.affixes) == 0
