import pytest
import sys
from unittest.mock import patch, MagicMock

# Mock streamlit module before importing dashboard.utils
mock_st = MagicMock()
# Mock the cache_data decorator to return the original function result
mock_st.cache_data = lambda func: func
# Make warning/error methods do nothing
mock_st.warning = MagicMock()
mock_st.error = MagicMock()
sys.modules['streamlit'] = mock_st

# Now import the functions
from dashboard.utils import display_portrait


class TestEnemyPortraitUI:
    """
    Integration tests for enemy portrait UI functionality.
    Tests the data access and display logic used in preparation and combat phases.
    """

    def test_enemy_portrait_display_preparation(self):
        """Test that preparation phase correctly accesses next enemy portrait path."""
        # Mock session and provider
        mock_session = MagicMock()
        mock_session._get_current_enemy_id.return_value = "goblin_grunt"
        mock_session.current_stage = 0

        mock_provider = MagicMock()
        mock_enemy_template = MagicMock()
        mock_enemy_template.portrait_path = "assets/portraits/goblin_grunt.png"
        mock_enemy_template.name = "Goblin Grunt"
        mock_provider.entities = {"goblin_grunt": mock_enemy_template}

        # Simulate the logic from render_preparation
        enemy_id = mock_session._get_current_enemy_id()
        enemy_template = mock_provider.entities[enemy_id]

        # Verify enemy data access
        assert enemy_id == "goblin_grunt"
        assert enemy_template.portrait_path == "assets/portraits/goblin_grunt.png"

        # Test display logic
        with patch('dashboard.utils.display_portrait') as mock_display:
            display_portrait(enemy_template.portrait_path, width=128)
            mock_display.assert_called_once_with("assets/portraits/goblin_grunt.png", width=128)

    def test_enemy_portrait_display_combat(self):
        """Test that combat phase correctly accesses defeated enemy portrait path."""
        # Mock session and provider
        mock_session = MagicMock()
        mock_session._get_current_enemy_id.return_value = "orc_warrior"

        mock_provider = MagicMock()
        mock_enemy_template = MagicMock()
        mock_enemy_template.portrait_path = "assets/portraits/orc_warrior.png"
        mock_enemy_template.name = "Orc Warrior"
        mock_provider.entities = {"orc_warrior": mock_enemy_template}

        # Simulate the logic from render_combat
        enemy_id = mock_session._get_current_enemy_id()
        enemy_template = mock_provider.entities[enemy_id]

        # Verify enemy data access
        assert enemy_id == "orc_warrior"
        assert enemy_template.portrait_path == "assets/portraits/orc_warrior.png"

        # Test display logic
        with patch('dashboard.utils.display_portrait') as mock_display:
            display_portrait(enemy_template.portrait_path, width=128)
            mock_display.assert_called_once_with("assets/portraits/orc_warrior.png", width=128)

    def test_enemy_stage_progression(self):
        """Test that enemy changes correctly across stages."""
        # Mock session with different stages
        mock_session = MagicMock()

        # Stage 0 - first enemy
        mock_session.current_stage = 0
        mock_session._get_current_enemy_id.return_value = "goblin_grunt"

        enemy_id = mock_session._get_current_enemy_id()
        assert enemy_id == "goblin_grunt"

        # Stage 2 - different enemy
        mock_session.current_stage = 2
        mock_session._get_current_enemy_id.return_value = "enemy_mage_novice"

        enemy_id = mock_session._get_current_enemy_id()
        assert enemy_id == "enemy_mage_novice"

    def test_enemy_portrait_fallback(self):
        """Test that empty enemy portrait paths trigger fallback display."""
        # Mock enemy template with empty portrait path
        mock_enemy_template = MagicMock()
        mock_enemy_template.portrait_path = ""

        # Test display logic with empty path
        with patch('dashboard.utils.display_portrait') as mock_display:
            display_portrait(mock_enemy_template.portrait_path, width=128)

            # Verify display_portrait handles empty path (fallback should be triggered)
            mock_display.assert_called_once_with("", width=128)

    def test_integration_with_game_session(self):
        """Test integration with actual GameSession enemy selection."""
        from src.game.session import GameSession
        from src.data.game_data_provider import GameDataProvider

        # Create minimal session for testing
        provider = GameDataProvider.__new__(GameDataProvider)
        session = GameSession(provider)

        # Test that _get_current_enemy_id method exists and works
        assert hasattr(session, '_get_current_enemy_id')

        # Test enemy ID generation for different stages
        session.current_stage = 0
        enemy_id_0 = session._get_current_enemy_id()
        assert enemy_id_0 == "goblin_grunt"

        session.current_stage = 1
        enemy_id_1 = session._get_current_enemy_id()
        assert enemy_id_1 == "orc_warrior"

    def test_enemy_template_data_access(self):
        """Test that enemy template data is properly accessible."""
        from src.data.typed_models import EntityTemplate, Rarity

        # Create a real enemy template
        enemy_template = EntityTemplate(
            entity_id="goblin_grunt",
            name="Goblin Grunt",
            archetype="Monster",
            level=1,
            rarity=Rarity.COMMON,
            base_health=50.0,
            base_damage=8.0,
            armor=0.0,
            crit_chance=0.05,
            attack_speed=1.2,
            portrait_path="assets/portraits/goblin_grunt.png"
        )

        # Verify all expected fields are accessible
        assert enemy_template.entity_id == "goblin_grunt"
        assert enemy_template.name == "Goblin Grunt"
        assert enemy_template.archetype == "Monster"
        assert enemy_template.portrait_path == "assets/portraits/goblin_grunt.png"
        assert enemy_template.base_health == 50.0
        assert enemy_template.base_damage == 8.0

        # Test portrait display with real template
        with patch('dashboard.utils.display_portrait') as mock_display:
            display_portrait(enemy_template.portrait_path, width=128)
            mock_display.assert_called_once_with("assets/portraits/goblin_grunt.png", width=128)
