"""
Tests for rarity-gated affix pools, tiered weighted rolls, and auto-generation.

Tests the new affix pool functionality including:
- Weighted selection mechanics
- Rarity fallback logic
- Builder auto-generation
- Schema validation
"""

import csv
import pytest
from pathlib import Path
from src.core.rng import RNG
from src.data.game_data_provider import GameDataProvider
from src.utils.item_generator import ItemGenerator
from scripts.build_content import main as build_content_main

def test_weighted_choice_deterministic():
    """Test that RNG weighted_choice is deterministic."""
    rng = RNG(seed=42)
    items = ["a", "b", "c"]
    weights = [70, 20, 10]
    picks = [rng.weighted_choice(items, [float(w) for w in weights]) for _ in range(5)]
    assert picks == ['a', 'a', 'a', 'a', 'b']  # exact sequence depends on RNG implementation

def test_item_generator_with_affix_pools():
    """Test ItemGenerator can load and use affix pools."""
    provider = GameDataProvider()
    generator = ItemGenerator(provider=provider, rng=RNG(seed=123))

    # Should have affix pools loaded
    assert len(generator.affix_pools) > 0

    # Test the new _pick_affix_for_item method (rarity fallback)
    # Use a test item that has pools
    test_affix = generator._pick_affix_for_item('longsword_rare')  # should fallback to Common if no Rare pools
    assert test_affix is not None
    assert isinstance(test_affix, str)

def test_rarity_fallback_logic():
    """Test that the RARITY_ORDER is correctly defined."""
    from src.utils.item_generator import RARITY_ORDER

    # Test that RARITY_ORDER contains expected rarities
    assert 'Common' in RARITY_ORDER
    assert 'Rare' in RARITY_ORDER
    assert 'Epic' in RARITY_ORDER

    # Test order makes sense (lower index should be more common)
    assert RARITY_ORDER.index('Common') < RARITY_ORDER.index('Epic')

def test_builder_generates_valid_affix_pools(tmp_path):
    """
    Tests that the build_content script generates an affix_pools.csv
    with expected, valid data.
    """
    output_dir = tmp_path

    # Run the builder script, directing its output to the temp directory.
    # This may need adjustment based on how the script handles output paths.
    build_content_main()

    affix_pools_file = Path("data/affix_pools.csv")
    assert affix_pools_file.exists(), "affix_pools.csv was not created"

    with open(affix_pools_file, 'r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))

    assert len(reader) > 0, "affix_pools.csv is empty"

    # Example assertion: Find a predictable row to validate the logic.
    # The specifics depend on your blueprint data.
    expected_pool_ids = ['weapon_pool', 'sword_pool', 'armor_pool', 'jewelry_pool']
    found_pool_ids = set(row['pool_id'] for row in reader)
    assert found_pool_ids == set(expected_pool_ids), f"Expected pools {expected_pool_ids}, got {found_pool_ids}"

    # Check that all entries have required fields
    for row in reader:
        assert 'pool_id' in row
        assert 'rarity' in row
        assert 'tier' in row
        assert 'affix_id' in row
        assert 'weight' in row
        assert int(row['tier']) > 0
        assert int(row['weight']) > 0

def test_affix_pools_schema_validation():
    """Test that affix_pools.csv validates against schema."""
    # The parse_all_csvs function should validate with schema
    provider = GameDataProvider()
    pools = provider.get_affix_pools()

    # Should have nested structure
    assert isinstance(pools, dict)
    for pool_id, rarities in pools.items():
        assert isinstance(rarities, dict)
        for rarity, tiers in rarities.items():
            assert isinstance(tiers, dict)
            for tier, entries in tiers.items():
                assert isinstance(entries, list)
                assert len(entries) > 0
                for entry in entries:
                    assert 'affix_id' in entry
                    assert 'weight' in entry
                    assert isinstance(entry['weight'], int)
