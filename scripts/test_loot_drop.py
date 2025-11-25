from src.data.game_data_provider import GameDataProvider
from src.utils.item_generator import ItemGenerator
from src.core.loot_manager import LootManager
from src.core.rng import RNG

provider = GameDataProvider()
rng = RNG(42)
item_gen = ItemGenerator(provider=provider, rng=rng)
manager = LootManager(provider, item_gen, rng)

# Assuming 'forest_zone_loot' exists from C1
items = manager.roll_loot("forest_zone_loot")
print(f"Dropped {len(items)} items:")
for item in items:
    print(f"- {item.name} ({item.rarity})")
