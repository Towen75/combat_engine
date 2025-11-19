import unittest
import json
import random
import pytest
from src.utils.item_generator import ItemGenerator
from src.core.models import Item, RolledAffix
from src.data.typed_models import AffixDefinition, QualityTier

class TestItemGenerator(unittest.TestCase):

    def setUp(self):
        with open('data/game_data.json', 'r') as f:
            self.game_data = json.load(f)
        # ItemGenerator now automatically hydrates this JSON into Objects
        self.gen = ItemGenerator(self.game_data)

    def test_init_loads_data(self):
        """Test that the generator loads data correctly as Objects."""
        self.assertIsInstance(self.gen.affix_defs, dict)
        self.assertIsInstance(self.gen.item_templates, dict)
        self.assertIsInstance(self.gen.quality_tiers, list)
        
        # Verify content is present
        self.assertIn('flat_dmg', self.gen.affix_defs)
        self.assertIn('base_iron_axe', self.gen.item_templates)
        
        # Verify conversion to Objects
        first_affix = self.gen.affix_defs['flat_dmg']
        self.assertIsInstance(first_affix, AffixDefinition)
        self.assertTrue(hasattr(first_affix, 'base_value'))

    def test_roll_quality_tier_valid_rarities(self):
        """Test quality tier rolling for different rarities."""
        valid_rarities = ['Common', 'Uncommon', 'Rare', 'Exotic', 'Epic', 'Glorious', 'Exalted', 'Legendary', 'Mythic', 'Godly']
        for rarity in valid_rarities:
            with self.subTest(rarity=rarity):
                # Should return a QualityTier object, not a dict
                tier = self.gen._roll_quality_tier(rarity)
                if tier:
                    self.assertIsInstance(tier, QualityTier)
                    self.assertTrue(hasattr(tier, 'tier_name'))
                    self.assertTrue(hasattr(tier, 'min_range'))
                    self.assertTrue(hasattr(tier, 'max_range'))
                    self.assertTrue(tier.min_range <= tier.max_range)

    def test_roll_quality_tier_rare(self):
        """Test quality tier rolling for Rare specifically."""
        tier = self.gen._roll_quality_tier('Rare')
        self.assertIsInstance(tier, QualityTier)
        self.assertTrue(hasattr(tier, 'tier_name'))
        # Check probability field exists
        self.assertTrue(hasattr(tier, 'rare'))

    def test_get_affix_pool_single_pool(self):
        """Test affix pool gathering for single pool."""
        pool = self.gen._get_affix_pool(['weapon_pool'])
        self.assertIsInstance(pool, list)
        self.assertIn('flat_dmg', pool)

    def test_get_affix_pool_multiple_pools(self):
        """Test affix pool gathering for multiple pools."""
        pool = self.gen._get_affix_pool(['weapon_pool', 'axe_pool'])
        self.assertIsInstance(pool, list)
        self.assertIn('flat_dmg', pool)

    def test_get_affix_pool_empty(self):
        """Test empty pool string."""
        pool = self.gen._get_affix_pool([])
        self.assertEqual(pool, [])

    def test_roll_one_affix_full_quality(self):
        """Test rolling affix with 100% max quality."""
        random.seed(42)
        affix = self.gen._roll_one_affix('flat_dmg', 100)
        
        self.assertIsInstance(affix, RolledAffix)
        self.assertEqual(affix.affix_id, 'flat_dmg')
        self.assertGreaterEqual(affix.value, 0)
        self.assertLessEqual(affix.value, 50.0)
        self.assertEqual(affix.mod_type, 'flat')
        self.assertEqual(affix.stat_affected, 'base_damage')

    def test_roll_one_affix_half_quality(self):
        """Test rolling affix with 50% max quality."""
        random.seed(42)
        affix = self.gen._roll_one_affix('flat_dmg', 50)
        
        self.assertIsInstance(affix, RolledAffix)
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
        
        for affix in item.affixes:
            self.assertIsInstance(affix, RolledAffix)
            self.assertIn(affix.mod_type, ['flat', 'multiplier'])
            self.assertIsInstance(affix.value, float)

    def test_generate_invalid_base_item(self):
        """Test generating with invalid base item ID."""
        with self.assertRaises(KeyError):
            self.gen.generate('nonexistent_item')

    def test_roll_dual_stat_affix(self):
        """Test rolling an affix with two values (primary and dual)."""
        # Create a mocked AffixDefinition object
        mock_affix = AffixDefinition(
            affix_id='test_dual',
            stat_affected='stat1;stat2',
            mod_type='flat;multiplier',
            base_value='100.0;0.5',
            description='Test Dual',
            affix_pools=['test_pool'],
            dual_stat=True
        )
        
        # Inject Object, not Dict
        self.gen.affix_defs['test_dual'] = mock_affix
        
        # Seed RNG
        self.gen.rng = random.Random(42)
        
        # Roll
        rolled = self.gen._roll_one_affix('test_dual', 100)
        
        self.assertEqual(rolled.affix_id, 'test_dual')
        self.assertGreater(rolled.value, 0)
        self.assertIsNotNone(rolled.dual_value)
        self.assertGreater(rolled.dual_value, 0)
        
        # Check deterministic values (Seed 42: rolls 81% then 14%)
        # Primary: 100 * 0.81 = 81.0
        # Secondary: 0.5 * 0.14 = 0.07
        self.assertAlmostEqual(rolled.value, 81.0)
        self.assertAlmostEqual(rolled.dual_value, 0.07)

if __name__ == '__main__':
    unittest.main()