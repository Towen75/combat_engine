import pytest
import random
from src.utils.item_generator import ItemGenerator
from src.data.typed_models import AffixDefinition

class TestItemGeneratorStrict:
    
    def test_roll_dual_stat_affix(self):
        """Test rolling an affix with two values."""
        # 1. Setup Mock Data using Typed Objects
        gen = ItemGenerator(game_data=None) # Empty init
        
        # Inject a typed definition manually
        gen.affix_defs['test_dual'] = AffixDefinition(
            affix_id='test_dual',
            stat_affected='stat1;stat2',
            mod_type='flat;multiplier',
            base_value='100.0;0.5',
            description='Test Dual',
            affix_pools=['test_pool'],
            dual_stat=True
        )
        
        # 2. Seed RNG
        gen.rng = random.Random(42)
        
        # 3. Execute
        rolled = gen._roll_one_affix('test_dual', 100)
        
        # 4. Verify
        assert rolled.affix_id == 'test_dual'
        # With seed 42: randint(0,100) -> 81, then -> 14
        assert rolled.value == pytest.approx(81.0)    # 100.0 * 0.81
        assert rolled.dual_value == pytest.approx(0.07) # 0.5 * 0.14