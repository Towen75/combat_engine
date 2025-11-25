import pytest
from unittest.mock import MagicMock
from src.data.game_data_provider import GameDataProvider
from src.data.typed_models import DataValidationError

class TestLootValidation:
    def test_circular_dependency_detection(self):
        """Test that A->B->A cycle raises ValidationError."""
        # Mock Data - only loot_tables for this test
        raw_data = {
            "loot_tables": [
                # Table A points to Table B
                {"table_id": "table_A", "entry_type": "Table", "entry_id": "table_B", "weight": "1", "min_count": "1", "max_count": "1", "drop_chance": "1"},
                # Table B points to Table A (CYCLE)
                {"table_id": "table_B", "entry_type": "Table", "entry_id": "table_A", "weight": "1", "min_count": "1", "max_count": "1", "drop_chance": "1"},
            ]
        }

        provider = GameDataProvider.__new__(GameDataProvider)
        provider._is_initialized = False

        # Set up provider state
        provider.affixes = {}
        provider.quality_tiers = []
        provider.effects = {}
        provider.skills = {}
        provider.affix_pools = {}

        # Mock items dict to have references (not going through hydration to avoid extra fields)
        provider.items = {"dagger": MagicMock()}
        provider._hydrate_data(raw_data)  # This will add loot_tables, but not override items

        with pytest.raises(DataValidationError) as exc:
            provider._validate_loot_tables()

        assert "Circular dependency" in str(exc.value)
        assert "table_A" in str(exc.value)

    def test_valid_nested_structure(self):
        """Test that A->B->Item is valid."""
        raw_data = {
            "items": {"dagger": {"item_id": "dagger", "name": "Dagger", "slot": "Weapon", "rarity": "Common"}},
            "loot_tables": [
                {"table_id": "parent", "entry_type": "Table", "entry_id": "child", "weight": "1", "min_count": "1", "max_count": "1", "drop_chance": "1"},
                {"table_id": "child", "entry_type": "Item", "entry_id": "dagger", "weight": "1", "min_count": "1", "max_count": "1", "drop_chance": "1"},
            ]
        }

        provider = GameDataProvider.__new__(GameDataProvider)
        provider._is_initialized = False

        # Set up provider state
        provider.affixes = {}
        provider.quality_tiers = []
        provider.effects = {}
        provider.skills = {}
        provider.affix_pools = {}

        # Hydrate & Validate - this will set items correctly
        provider._hydrate_data(raw_data)
        try:
            provider._validate_loot_tables()
        except DataValidationError:
            pytest.fail("Valid nested structure raised DataValidationError unexpectedly")

    def test_invalid_item_reference(self):
        """Test that referencing a non-existent item raises ValidationError."""
        raw_data = {
            "loot_tables": [
                {"table_id": "broken_table", "entry_type": "Item", "entry_id": "fake_sword", "weight": "1", "min_count": "1", "max_count": "1", "drop_chance": "1"},
            ]
        }

        provider = GameDataProvider.__new__(GameDataProvider)
        provider._is_initialized = False

        # Set up provider state
        provider.affixes = {}
        provider.quality_tiers = []
        provider.effects = {}
        provider.skills = {}
        provider.affix_pools = {}

        provider.items = {} # Empty items dict

        provider._hydrate_data(raw_data)

        with pytest.raises(DataValidationError) as exc:
            provider._validate_loot_tables()

        assert "references non-existent Item" in str(exc.value)
        assert "fake_sword" in str(exc.value)
