import pytest
import logging
from unittest.mock import MagicMock
from src.core.factory import EntityFactory
from src.core.models import Entity, Item
from src.core.rng import RNG
from src.data.typed_models import EntityTemplate, ItemTemplate, Rarity, ItemSlot

class TestEntityFactory:

    @pytest.fixture
    def mock_components(self):
        provider = MagicMock()
        item_gen = MagicMock()
        rng = RNG(42)

        # Mock Item Generation
        def mock_generate(item_id):
            return Item("inst", item_id, f"Name {item_id}", "Weapon", "Common", "Normal", 1)
        item_gen.generate.side_effect = mock_generate

        return provider, item_gen, rng

    def test_create_basic_entity(self, mock_components):
        """Test simple entity creation from template."""
        provider, item_gen, rng = mock_components
        factory = EntityFactory(provider, item_gen, rng)

        # Setup Template
        template = EntityTemplate(
            entity_id="goblin", name="Goblin", archetype="Monster", level=1, rarity=Rarity.COMMON,
            base_health=100.0, base_damage=10.0, armor=5.0, crit_chance=0.05, attack_speed=1.0
        )
        provider.get_entity_template.return_value = template

        # Execute
        entity = factory.create("goblin")

        # Verify
        assert entity.name == "Goblin"
        assert entity.base_stats.max_health == 100.0
        assert entity.base_stats.armor == 5.0
        assert "goblin" in entity.id

    def test_create_with_custom_instance_id(self, mock_components):
        """Test entity creation with custom instance ID."""
        provider, item_gen, rng = mock_components
        factory = EntityFactory(provider, item_gen, rng)

        # Setup Template
        template = EntityTemplate(
            entity_id="orc", name="Orc", archetype="Monster", level=1, rarity=Rarity.COMMON,
            base_health=100.0, base_damage=10.0, armor=0.0, crit_chance=0.0, attack_speed=1.0
        )
        provider.get_entity_template.return_value = template

        # Execute with custom ID
        entity = factory.create("orc", instance_id="special_orc_001")

        # Verify custom ID is used
        assert entity.id == "special_orc_001"

    def test_equip_direct_item_id(self, mock_components):
        """Test equipping an item referenced directly by ID."""
        provider, item_gen, rng = mock_components
        factory = EntityFactory(provider, item_gen, rng)

        # Setup Template with direct item ID
        template = EntityTemplate(
            entity_id="guard", name="Guard", archetype="NPC", level=1, rarity=Rarity.COMMON,
            base_health=100, base_damage=10, armor=0, crit_chance=0, attack_speed=1,
            equipment_pools=["iron_sword"]
        )
        provider.get_entity_template.return_value = template

        # Setup Provider to verify ID exists
        provider.items = {"iron_sword": MagicMock(item_id="iron_sword")}

        # Execute
        entity = factory.create("guard")

        # Verify
        item_gen.generate.assert_called_with("iron_sword")
        assert len(entity.equipment) == 1

    def test_equip_from_pool_deterministic(self, mock_components):
        """Test selecting an item from a pool is deterministic."""
        provider, item_gen, rng = mock_components
        factory = EntityFactory(provider, item_gen, rng)

        # Setup Template with pool
        template = EntityTemplate(
            entity_id="bandit", name="Bandit", archetype="Monster", level=1, rarity=Rarity.COMMON,
            base_health=100, base_damage=10, armor=0, crit_chance=0, attack_speed=1,
            equipment_pools=["melee_pool"]
        )
        provider.get_entity_template.return_value = template

        # Setup Items in Provider
        item1 = ItemTemplate("dagger", "Dagger", ItemSlot.WEAPON, Rarity.COMMON, affix_pools=["melee_pool"])
        item2 = ItemTemplate("axe", "Axe", ItemSlot.WEAPON, Rarity.COMMON, affix_pools=["melee_pool"])
        provider.items = {"dagger": item1, "axe": item2}

        # Execute 1 (Seed 42)
        entity1 = factory.create("bandit")

        # Reset RNG to same seed
        rng2 = RNG(42)
        factory2 = EntityFactory(provider, item_gen, rng2)

        # Execute 2 (Seed 42)
        entity2 = factory2.create("bandit")

        # Verify selections are identical
        # We check the calls to item_gen to see what ID was resolved
        call_args1 = item_gen.generate.call_args_list[-2][0][0]  # item for entity1
        call_args2 = item_gen.generate.call_args_list[-1][0][0]  # item for entity2

        assert call_args1 == call_args2

    def test_resolve_failure_logs_warning(self, mock_components, caplog):
        """Test that invalid pools log warnings but don't crash."""
        provider, item_gen, rng = mock_components
        factory = EntityFactory(provider, item_gen, rng)

        template = EntityTemplate(
            entity_id="ghost", name="Ghost", archetype="Monster", level=1, rarity=Rarity.COMMON,
            base_health=100, base_damage=10, armor=0, crit_chance=0, attack_speed=1,
            equipment_pools=["missing_pool"]
        )
        provider.get_entity_template.return_value = template
        provider.items = {}  # No items

        # Execute
        entity = factory.create("ghost")

        # Verify warning
        assert "Could not resolve item" in caplog.text
        assert "missing_pool" in caplog.text

    def test_multiple_equipment_pools(self, mock_components):
        """Test attempting to equip multiple items from different pools."""
        provider, item_gen, rng = mock_components
        factory = EntityFactory(provider, item_gen, rng)

        template = EntityTemplate(
            entity_id="warrior", name="Warrior", archetype="Hero", level=1, rarity=Rarity.RARE,
            base_health=150, base_damage=20, armor=0, crit_chance=0, attack_speed=1,
            equipment_pools=["sword", "shield", "armor"]
        )
        provider.get_entity_template.return_value = template

        # All pools resolve directly to items (all weapons, so last one wins slot)
        provider.items = {
            "sword": MagicMock(item_id="sword"),
            "shield": MagicMock(item_id="shield"),
            "armor": MagicMock(item_id="armor")
        }

        # Execute
        entity = factory.create("warrior")

        # Verify all three items were attempted (Entity can only equip one per slot)
        assert item_gen.generate.call_count == 3
        # Only one item equipped since all are same slot - last one wins
        assert len(entity.equipment) == 1

    def test_missing_template_raises_error(self, mock_components):
        """Test that missing template raises ValueError."""
        provider, item_gen, rng = mock_components
        factory = EntityFactory(provider, item_gen, rng)

        # Provider raises ValueError for missing template
        provider.get_entity_template.side_effect = ValueError("Template not found")

        # Execute and verify
        with pytest.raises(ValueError, match="Template not found"):
            factory.create("missing_template")

    def test_resolve_direct_item_priority(self, mock_components):
        """Test that direct item IDs take priority over pool lookup."""
        provider, item_gen, rng = mock_components
        factory = EntityFactory(provider, item_gen, rng)

        # Setup: item "sword" exists both as direct item AND in pool "sword_pool"
        direct_item = MagicMock(item_id="sword")
        pool_item = ItemTemplate("sword2", "Sword 2", ItemSlot.WEAPON, Rarity.COMMON, affix_pools=["sword"])
        provider.items = {"sword": direct_item, "sword2": pool_item}

        # Resolve "sword" - should return direct match, not do pool lookup
        result = factory._resolve_item_id("sword")

        # Should return the direct item, not check pools
        assert result == "sword"

    def test_resolve_empty_pool_returns_none(self, mock_components):
        """Test that pool with no matching items returns None."""
        provider, item_gen, rng = mock_components
        factory = EntityFactory(provider, item_gen, rng)

        # Setup empty provider
        provider.items = {}

        # Resolve non-existent pool
        result = factory._resolve_item_id("empty_pool")

        # Should return None
        assert result is None
