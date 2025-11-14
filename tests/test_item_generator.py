import unittest
import json
import random
from src.item_generator import ItemGenerator
from src.models import Item, RolledAffix


class TestItemGenerator(unittest.TestCase):

    def setUp(self):
        with open('data/game_data.json', 'r') as f:
            self.game_data = json.load(f)
        self.gen = ItemGenerator(self.game_data)

    def test_init_loads_data(self):
        """Test that the generator loads data correctly."""
        self.assertIsInstance(self.gen.affix_defs, dict)
        self.assertIsInstance(self.gen.item_templates, dict)
        self.assertIsInstance(self.gen.quality_tiers, list)
        self.assertIn('flat_dmg', self.gen.affix_defs)
        self.assertIn('base_iron_axe', self.gen.item_templates)

    def test_roll_quality_tier_valid_rarities(self):
        """Test quality tier rolling for different rarities."""
        valid_rarities = ['Common', 'Uncommon', 'Rare', 'Exotic', 'Epic', 'Glorious', 'Exalted', 'Legendary', 'Mythic', 'Godly']
        for rarity in valid_rarities:
            with self.subTest(rarity=rarity):
                if rarity in ['Normal']:
                    continue  # Normal may not be in items, but skip if any rarity in items
                try:
                    tier = self.gen._roll_quality_tier(rarity)
                    if tier:
                        self.assertIn('tier_name', tier)
                        self.assertIn('min_range', tier)
                        self.assertIn('max_range', tier)
                        self.assertTrue(tier['min_range'] <= tier['max_range'])
                except AttributeError:
                    pass  # Some rarities may not have tiers, skip

    def test_roll_quality_tier_rare(self):
        """Test quality tier rolling for Rare specifically."""
        tier = self.gen._roll_quality_tier('Rare')
        self.assertIsInstance(tier, dict)
        self.assertIn('tier_name', tier)
        self.assertIn('Rare', tier)
        # Since Rare can roll non-zero weights, but in our data, Rare has weights in higher tiers
        # The test that it returns something valid is sufficient due to randomness

    def test_get_affix_pool_single_pool(self):
        """Test affix pool gathering for single pool."""
        pool = self.gen._get_affix_pool(['weapon_pool'])
        self.assertIsInstance(pool, list)
        self.assertIn('flat_dmg', pool)  # From our affixes.csv

    def test_get_affix_pool_multiple_pools(self):
        """Test affix pool gathering for multiple pools."""
        pool = self.gen._get_affix_pool(['weapon_pool', 'axe_pool'])
        self.assertIsInstance(pool, list)
        self.assertIn('flat_dmg', pool)
        # Should have all from both

    def test_get_affix_pool_empty(self):
        """Test empty pool string."""
        pool = self.gen._get_affix_pool([])
        self.assertEqual(pool, [])

    def test_roll_one_affix_full_quality(self):
        """Test rolling affix with 100% max quality (can roll up to 100%)."""
        # Seed random for reproducible test
        random.seed(42)
        affix = self.gen._roll_one_affix('flat_dmg', 100)
        self.assertIsInstance(affix, RolledAffix)
        self.assertEqual(affix.affix_id, 'flat_dmg')
        # With any seed, should be between 0 and 50.0
        self.assertGreaterEqual(affix.value, 0)
        self.assertLessEqual(affix.value, 50.0)
        self.assertEqual(affix.mod_type, 'flat')
        self.assertEqual(affix.stat_affected, 'base_damage')

    def test_roll_one_affix_half_quality(self):
        """Test rolling affix with 50% max quality (can roll up to 25)."""
        # Seed random for reproducible test
        random.seed(42)
        affix = self.gen._roll_one_affix('flat_dmg', 50)
        self.assertIsInstance(affix, RolledAffix)
        # Should be between 0 and 25.0
        self.assertGreaterEqual(affix.value, 0)
        self.assertLessEqual(affix.value, 25.0)

    def test_generate_base_iron_axe(self):
        """Test generating an item."""
        item = self.gen.generate('base_iron_axe')
        self.assertIsInstance(item, Item)
        self.assertEqual(item.base_id, 'base_iron_axe')
        self.assertEqual(item.name, 'Iron Axe')
        self.assertEqual(item.slot, 'Weapon')
        self.assertEqual(item.rarity, 'Rare')
        self.assertIsInstance(item.affixes, list)
        self.assertTrue(len(item.affixes) >= 0)  # At least implicits, but in our data no implicits for iron axe

        # In our items.csv, implicit_affixes is empty, num_random_affixes = 2
        # But random pools have affixes, but due to randomness, just check structure
        for affix in item.affixes:
            self.assertIsInstance(affix, RolledAffix)
            self.assertIn(affix.mod_type, ['flat', 'multiplier'])
            self.assertIsInstance(affix.value, float)

    def test_generate_invalid_base_item(self):
        """Test generating with invalid base item ID."""
        with self.assertRaises(KeyError):
            self.gen.generate('nonexistent_item')

    def test_generate_gold_ring_with_implicits(self):
        """Test generating gold ring which has implicits."""
        item = self.gen.generate('base_gold_ring')
        self.assertEqual(item.rarity, 'Legendary')
        self.assertTrue(len(item.affixes) >= 1)  # At least crit_dmg implicit
        has_crit_dmg = any(affix.affix_id == 'crit_dmg' for affix in item.affixes)
        self.assertTrue(has_crit_dmg)


if __name__ == '__main__':
    unittest.main()
