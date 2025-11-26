import pytest
from src.core.factory import EntityFactory
from src.data.game_data_provider import GameDataProvider
from src.core.rng import RNG
from src.combat.engine import CombatEngine
from src.core.state import StateManager
from src.core.events import EventBus

class TestStockContent:

    @pytest.fixture
    def setup_combat(self):
        provider = GameDataProvider()
        provider.initialize("data")  # Initialize the provider with data
        rng = RNG(42) # Fixed seed for consistent balance checks
        factory = EntityFactory(provider, None, rng)
        engine = CombatEngine(rng)
        return factory, engine

    def test_all_stock_entities_spawn_correctly(self, setup_combat):
        """Verify every enemy in the stock CSV can be instantiated with equipment."""
        factory, _ = setup_combat
        stock_ids = [
            "enemy_warrior_grunt", "enemy_warrior_guard", "enemy_warrior_boss",
            "enemy_rogue_thief", "enemy_rogue_assassin", "enemy_rogue_boss",
            "enemy_mage_novice", "enemy_mage_sorcerer", "enemy_mage_boss"
        ]

        for eid in stock_ids:
            entity = factory.create(eid)
            assert entity is not None
            assert entity.name != ""
            # Verify equipment was actually equipped
            assert len(entity.equipment) > 0, f"{eid} failed to equip items"

    def test_boss_power_scaling(self, setup_combat):
        """Verify Bosses are stronger than Grunts (sanity check)."""
        factory, _ = setup_combat

        # Test Warrior progression
        grunt = factory.create("enemy_warrior_grunt")
        boss = factory.create("enemy_warrior_boss")

        # Check Health
        assert boss.final_stats.max_health > grunt.final_stats.max_health

        # Check Damage (should be significantly higher due to Rare vs Common items)
        assert boss.final_stats.base_damage > grunt.final_stats.base_damage

    def test_loot_table_linkage(self, setup_combat):
        """Verify entities have valid loot tables."""
        factory, _ = setup_combat

        grunt = factory.create("enemy_mage_novice")
        assert grunt.loot_table_id == "loot_mage_grunt"

        # Verify table exists in provider (check table_ids of loot entries)
        provider = factory.provider
        assert "loot_mage_grunt" in [lt.table_id for lt in provider.loot_tables]
