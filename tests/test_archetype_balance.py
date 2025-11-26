import pytest
from src.core.factory import EntityFactory
from src.data.game_data_provider import GameDataProvider
from src.core.rng import RNG
from src.combat.engine import CombatEngine
from src.core.state import StateManager
from src.core.events import EventBus

class TestArchetypeBalance:

    @pytest.fixture
    def setup_combat(self):
        provider = GameDataProvider()
        provider.initialize("data")
        rng = RNG(42) # Fixed seed for consistent balance checks
        factory = EntityFactory(provider, None, rng)
        engine = CombatEngine(rng)
        return factory, engine

    def _run_duel(self, factory, engine, hero_id, enemy_id):
        """Run a fight until death."""
        hero = factory.create(hero_id)
        enemy = factory.create(enemy_id)

        state_manager = StateManager()
        event_bus = EventBus()

        state_manager.add_entity(hero)
        state_manager.add_entity(enemy)

        rounds = 0
        max_rounds = 100 # Prevent infinite loops

        # Simple turn-based loop
        while state_manager.get_is_alive(hero.id) and state_manager.get_is_alive(enemy.id) and rounds < max_rounds:
            # Hero attacks
            engine.process_attack(hero, enemy, event_bus, state_manager)

            if state_manager.get_is_alive(enemy.id):
                # Enemy attacks back
                engine.process_attack(enemy, hero, event_bus, state_manager)

            rounds += 1

        return hero, enemy, state_manager

    def test_warrior_viability(self, setup_combat):
        """Test that Hero Warrior can beat a Rogue Grunt."""
        factory, engine = setup_combat
        hero, enemy, state = self._run_duel(factory, engine, "hero_warrior", "enemy_rogue_thief")

        assert state.get_is_alive(hero.id), "Warrior should defeat Rogue Grunt"
        # Warrior relies on Armor. Check if he took damage but survived.
        hero_hp = state.get_current_health(hero.id)
        assert hero_hp < hero.final_stats.max_health, "Warrior should have taken some damage"

    def test_rogue_viability(self, setup_combat):
        """Test that Hero Rogue can beat a Mage Novice."""
        factory, engine = setup_combat
        hero, enemy, state = self._run_duel(factory, engine, "hero_rogue", "enemy_mage_novice")

        assert state.get_is_alive(hero.id), "Rogue should defeat Mage Novice"

    def test_mage_viability(self, setup_combat):
        """Test that Hero Mage can beat a Warrior Grunt."""
        factory, engine = setup_combat
        hero, enemy, state = self._run_duel(factory, engine, "hero_mage", "enemy_warrior_grunt")

        assert state.get_is_alive(hero.id), "Mage should defeat Warrior Grunt"

    def test_archetype_equipment_check(self, setup_combat):
        """Verify Heroes spawn with correct family items."""
        factory, _ = setup_combat

        warrior = factory.create("hero_warrior")
        assert "Greatsword" in warrior.equipment["Weapon"].name
        assert "Plate" in warrior.equipment["Chest"].name

        mage = factory.create("hero_mage")
        assert "Staff" in mage.equipment["Weapon"].name
        assert "Robes" in mage.equipment["Chest"].name
