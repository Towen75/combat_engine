import pytest
from unittest.mock import MagicMock
from src.core.rng import RNG
from src.core.loot_manager import LootManager
from src.data.typed_models import LootTableDefinition, LootTableEntry, LootEntryType
from src.core.models import Item

class TestLootManager:

    @pytest.fixture
    def mock_provider(self):
        provider = MagicMock()
        provider.loot_tables = {}
        return provider

    @pytest.fixture
    def mock_item_gen(self):
        gen = MagicMock()
        # When generate is called, return a dummy Item with the ID as name
        gen.generate.side_effect = lambda item_id: Item(
            instance_id="inst", base_id=item_id, name=item_id,
            slot="weapon", rarity="Common", quality_tier="Normal", quality_roll=1
        )
        return gen

    @pytest.fixture
    def rng(self):
        return RNG(seed=42)

    def test_missing_table_raises_error(self, mock_provider, mock_item_gen, rng):
        manager = LootManager(mock_provider, mock_item_gen, rng)
        with pytest.raises(ValueError, match="not found"):
            manager.roll_loot("missing_table")

    def test_weighted_selection_determinism(self, mock_provider, mock_item_gen, rng):
        """Test that seeds produce consistent item picks."""
        # Setup: Table with two items, 50/50 weight
        entry_a = LootTableEntry("t1", LootEntryType.ITEM, "item_a", 50, 1, 1, 1.0)
        entry_b = LootTableEntry("t1", LootEntryType.ITEM, "item_b", 50, 1, 1, 1.0)

        table = LootTableDefinition("t1", entries=[entry_a, entry_b])
        mock_provider.loot_tables = {"t1": table}

        manager = LootManager(mock_provider, mock_item_gen, rng)

        # Run 1: Seed 42
        result_1 = manager.roll_loot("t1")[0].name

        # Run 2: Reset Seed 42
        rng_2 = RNG(seed=42)
        manager_2 = LootManager(mock_provider, mock_item_gen, rng_2)
        result_2 = manager_2.roll_loot("t1")[0].name

        assert result_1 == result_2

    def test_recursive_table_resolution(self, mock_provider, mock_item_gen, rng):
        """Test Table A -> Table B -> Item logic."""
        # Table B drops Item X
        entry_x = LootTableEntry("table_b", LootEntryType.ITEM, "item_x", 1, 1, 1, 1.0)
        table_b = LootTableDefinition("table_b", entries=[entry_x])

        # Table A drops Table B
        entry_b = LootTableEntry("table_a", LootEntryType.TABLE, "table_b", 1, 1, 1, 1.0)
        table_a = LootTableDefinition("table_a", entries=[entry_b])

        mock_provider.loot_tables = {"table_a": table_a, "table_b": table_b}

        manager = LootManager(mock_provider, mock_item_gen, rng)
        results = manager.roll_loot("table_a")

        assert len(results) == 1
        assert results[0].name == "item_x"

    def test_quantity_resolution(self, mock_provider, mock_item_gen, rng):
        """Test min_count and max_count."""
        # Entry drops 3-3 times (Fixed)
        entry = LootTableEntry("t1", LootEntryType.ITEM, "item_x", 1, 3, 3, 1.0)
        table = LootTableDefinition("t1", entries=[entry])
        mock_provider.loot_tables = {"t1": table}

        manager = LootManager(mock_provider, mock_item_gen, rng)
        results = manager.roll_loot("t1")

        assert len(results) == 3
        assert all(i.name == "item_x" for i in results)

    def test_drop_chance_filtering(self, mock_provider, mock_item_gen, rng):
        """Test that 0.0 drop chance prevents item from appearing."""
        # Entry A: 0% chance, Weight 1000
        # Entry B: 100% chance, Weight 1
        entry_a = LootTableEntry("t1", LootEntryType.ITEM, "item_a", 1000, 1, 1, 0.0)
        entry_b = LootTableEntry("t1", LootEntryType.ITEM, "item_b", 1, 1, 1, 1.0)

        table = LootTableDefinition("t1", entries=[entry_a, entry_b])
        mock_provider.loot_tables = {"t1": table}

        manager = LootManager(mock_provider, mock_item_gen, rng)
        results = manager.roll_loot("t1")

        # Despite high weight, A should never drop
        assert len(results) == 1
        assert results[0].name == "item_b"

    def test_safety_item_limit(self, mock_provider, mock_item_gen, rng):
        """Test MAX_TOTAL_ITEMS cap."""
        # Entry drops 100 items
        entry = LootTableEntry("t1", LootEntryType.ITEM, "item_x", 1, 100, 100, 1.0)
        table = LootTableDefinition("t1", entries=[entry])
        mock_provider.loot_tables = {"t1": table}

        manager = LootManager(mock_provider, mock_item_gen, rng)
        results = manager.roll_loot("t1")

        assert len(results) == 50  # Capped at default MAX_TOTAL_ITEMS
