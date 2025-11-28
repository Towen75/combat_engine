import pytest
from unittest.mock import MagicMock
from src.game.session import GameSession, GameState
from src.data.game_data_provider import GameDataProvider
from src.core.models import Item, Entity, EntityStats

class TestGameSession:

    @pytest.fixture
    def mock_provider(self):
        provider = MagicMock()
        # Mock template lookup
        mock_template = MagicMock()
        mock_template.base_health = 100
        mock_template.base_damage = 10
        mock_template.armor = 5
        mock_template.crit_chance = 0.1
        mock_template.attack_speed = 1.0
        mock_template.name = "Test Hero"
        mock_template.rarity = MagicMock()
        mock_template.rarity.value = "Common"
        mock_template.loot_table_id = "hero_loot"
        mock_template.equipment_pools = []
        provider.get_entity_template.return_value = mock_template
        return provider

    def test_initialization(self, mock_provider):
        session = GameSession(mock_provider)
        assert session.state == GameState.LOBBY
        assert session.current_stage == 0

    def test_start_new_run(self, mock_provider):
        session = GameSession(mock_provider)

        # Should switch to PREPARATION and spawn player
        session.start_new_run("hero_warrior", seed=123)

        assert session.state == GameState.PREPARATION
        assert session.player is not None
        assert session.master_seed == 123
        assert session.inventory.capacity == 20

    def test_claim_loot(self, mock_provider):
        session = GameSession(mock_provider)

        # Inject loot into stash manually
        sword = Item("i1", "b1", "Sword", "Weapon", "C", "N", 1)
        session.loot_stash = [sword]

        # Claim
        success = session.claim_loot(0)

        assert success is True
        assert len(session.loot_stash) == 0
        assert session.inventory.count == 1
        assert session.inventory.get_item("i1") == sword

    def test_advance_stage(self, mock_provider):
        session = GameSession(mock_provider)
        session.state = GameState.VICTORY
        session.current_stage = 0

        session.advance_stage()

        assert session.state == GameState.PREPARATION
        assert session.current_stage == 1
        assert len(session.loot_stash) == 0 # Should clear stash
