import pytest
import logging
from unittest.mock import MagicMock
from src.data.game_data_provider import GameDataProvider
from src.data.typed_models import EntityTemplate, Rarity, DataValidationError, LootTableEntry, LootEntryType

class TestEntityDataLoading:

    def test_entity_hydration_defaults(self):
        """Test that defaults are applied correctly."""
        raw_data = {
            "entities": {
                "test_dummy": {
                    "entity_id": "test_dummy",
                    "name": "Test Dummy",
                    "base_health": "100",
                    "base_damage": "0",
                    "rarity": "Common"
                }
            }
        }

        provider = GameDataProvider()
        provider._hydrate_data(raw_data)

        entity = provider.entities["test_dummy"]
        assert entity.level == 1
        assert entity.rarity == Rarity.COMMON
        assert entity.attack_speed == 1.0
        assert entity.armor == 0.0
        assert entity.crit_chance == 0.0
        assert entity.equipment_pools == []
        assert entity.loot_table_id == ""
        assert entity.description == ""

    def test_entity_hydration_with_values(self):
        """Test that provided values override defaults."""
        raw_data = {
            "entities": {
                "orc_chief": {
                    "entity_id": "orc_chief",
                    "name": "Orc Chief",
                    "archetype": "Elite",
                    "level": "5",
                    "rarity": "Rare",
                    "base_health": "500",
                    "base_damage": "25",
                    "armor": "10",
                    "crit_chance": "0.15",
                    "attack_speed": "0.8",
                    "equipment_pools": ["weapon_pool", "armor_pool"],
                    "loot_table_id": "elite_loot",
                    "description": "A mighty orc leader"
                }
            }
        }

        provider = GameDataProvider()
        provider._hydrate_data(raw_data)

        entity = provider.entities["orc_chief"]
        assert entity.entity_id == "orc_chief"
        assert entity.name == "Orc Chief"
        assert entity.archetype == "Elite"
        assert entity.level == 5
        assert entity.rarity == Rarity.RARE
        assert entity.base_health == 500.0
        assert entity.base_damage == 25.0
        assert entity.armor == 10.0
        assert entity.crit_chance == 0.15
        assert entity.attack_speed == 0.8
        assert entity.equipment_pools == ["weapon_pool", "armor_pool"]
        assert entity.loot_table_id == "elite_loot"
        assert entity.description == "A mighty orc leader"

    def test_entity_validation_missing_loot(self):
        """Test validation fails on missing loot table."""
        raw_data = {
            "entities": {
                "bad_goblin": {
                    "entity_id": "bad_goblin",
                    "name": "Goblin",
                    "base_health": "10",
                    "base_damage": "1",
                    "rarity": "Common",
                    "loot_table_id": "missing_table"
                }
            }
        }

        provider = GameDataProvider()
        provider.items = {}
        provider.loot_tables = []  # No loot tables defined
        provider._hydrate_data(raw_data)

        with pytest.raises(DataValidationError) as exc:
            provider._validate_entities()

        assert "missing_table" in str(exc.value)

    def test_entity_validation_valid_loot(self):
        """Test validation passes when loot table exists."""
        raw_data = {
            "entities": {
                "good_goblin": {
                    "entity_id": "good_goblin",
                    "name": "Goblin",
                    "base_health": "10",
                    "base_damage": "1",
                    "rarity": "Common",
                    "loot_table_id": "goblin_loot"
                }
            }
        }

        provider = GameDataProvider()
        provider.items = {}
        provider._hydrate_data(raw_data)

        # Set loot table after hydration (hydration clears it)
        loot_entry = LootTableEntry(
            table_id="goblin_loot",
            entry_type=LootEntryType.ITEM,  # Use proper enum value
            entry_id="gold",
            weight=10,
            min_count=1,
            max_count=5,
            drop_chance=0.8
        )
        provider.loot_tables = [loot_entry]

        # Should not raise an exception
        provider._validate_entities()

    def test_equipment_pool_warning(self, caplog):
        """Test that invalid equipment pool logs a warning (not crash)."""
        raw_data = {
            "entities": {
                "naked_goblin": {
                    "entity_id": "naked_goblin",
                    "name": "Goblin",
                    "base_health": "10",
                    "base_damage": "1",
                    "rarity": "Common",
                    "equipment_pools": ["non_existent_pool"]
                }
            }
        }

        provider = GameDataProvider()
        provider.items = {}  # No items match the pool
        provider.loot_tables = []
        provider._hydrate_data(raw_data)

        with caplog.at_level(logging.WARNING):
            provider._validate_entities()

        assert "non_existent_pool" in caplog.text

    def test_equipment_pool_valid(self, caplog):
        """Test that valid equipment pool (item ID) passes."""
        raw_data = {
            "entities": {
                "equipped_goblin": {
                    "entity_id": "equipped_goblin",
                    "name": "Goblin",
                    "base_health": "10",
                    "base_damage": "1",
                    "rarity": "Common",
                    "equipment_pools": ["rusty_sword"]
                }
            }
        }

        provider = GameDataProvider()

        # Mock item that matches the pool name
        mock_item = MagicMock()
        mock_item.affix_pools = []
        provider.items = {"rusty_sword": mock_item}
        provider.loot_tables = []

        provider._hydrate_data(raw_data)

        # Should not log warnings
        with caplog.at_level(logging.WARNING):
            provider._validate_entities()
            assert len(caplog.records) == 0

    def test_get_entity_template_exists(self):
        """Test getting an entity template that exists."""
        raw_data = {
            "entities": {
                "test_entity": {
                    "entity_id": "test_entity",
                    "name": "Test Entity",
                    "base_health": "100",
                    "base_damage": "10",
                    "rarity": "Common"
                }
            }
        }

        provider = GameDataProvider()
        provider._hydrate_data(raw_data)
        provider._is_initialized = True  # Skip full initialization

        entity = provider.get_entity_template("test_entity")
        assert isinstance(entity, EntityTemplate)
        assert entity.entity_id == "test_entity"
        assert entity.name == "Test Entity"

    def test_get_entity_template_not_found(self):
        """Test getting an entity template that doesn't exist."""
        provider = GameDataProvider()
        provider._is_initialized = True

        with pytest.raises(ValueError) as exc:
            provider.get_entity_template("non_existent")

        assert "non_existent" in str(exc.value)

    def test_get_entity_template_not_initialized(self):
        """Test getting entity template before initialization."""
        provider = GameDataProvider()
        # Don't set _is_initialized

        with pytest.raises(RuntimeError) as exc:
            provider.get_entity_template("any_entity")

        assert "not initialized" in str(exc.value)
