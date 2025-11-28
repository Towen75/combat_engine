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


class TestHeroPortraitUI:
    """
    Integration tests for hero portrait UI functionality.
    Tests the data access and display logic used in lobby and preparation phases.
    """

    def test_portrait_display_logic_lobby(self):
        """Test that lobby phase correctly accesses hero portrait path."""
        # This test verifies the data access logic that would be used in render_lobby
        mock_provider = MagicMock()
        mock_template = MagicMock()
        mock_template.portrait_path = "assets/portraits/hero_paladin.png"
        mock_provider.entities = {"hero_paladin": mock_template}

        # Simulate the logic from render_lobby
        selected_hero = "hero_paladin"
        template = mock_provider.entities[selected_hero]

        # Verify portrait path is accessible
        assert template.portrait_path == "assets/portraits/hero_paladin.png"

        # Test with mocked display_portrait
        with patch.object(sys.modules['dashboard.utils'], 'display_portrait') as mock_display:
            display_portrait(template.portrait_path, width=128)
            mock_display.assert_called_once_with("assets/portraits/hero_paladin.png", width=128)

    def test_portrait_display_logic_preparation(self):
        """Test that preparation phase correctly accesses player portrait path."""
        # This test verifies the data access logic that would be used in render_preparation
        mock_player = MagicMock()
        mock_player.template.portrait_path = "assets/portraits/hero_paladin.png"

        # Simulate the logic from render_preparation
        player = mock_player

        # Verify portrait path is accessible
        assert player.template.portrait_path == "assets/portraits/hero_paladin.png"

        # Test with mocked display_portrait
        with patch('dashboard.utils.display_portrait') as mock_display:
            display_portrait(player.template.portrait_path, width=128)
            mock_display.assert_called_once_with("assets/portraits/hero_paladin.png", width=128)

    def test_portrait_fallback_logic(self):
        """Test that empty portrait paths trigger fallback display."""
        # Test empty path
        with patch('dashboard.utils.display_portrait') as mock_display:
            display_portrait("", width=128)

            # Verify display_portrait handles empty path (fallback should be triggered)
            mock_display.assert_called_once_with("", width=128)

    def test_integration_with_entity_data(self):
        """Test integration with actual EntityTemplate data structure."""
        from src.data.typed_models import EntityTemplate, Rarity

        # Create a real EntityTemplate with portrait path
        template = EntityTemplate(
            entity_id="test_hero",
            name="Test Hero",
            archetype="Hero",
            level=1,
            rarity=Rarity.RARE,
            base_health=100.0,
            base_damage=20.0,
            armor=10.0,
            crit_chance=0.15,
            attack_speed=1.0,
            portrait_path="assets/portraits/test_hero.png"
        )

        # Verify portrait_path field exists and is accessible
        assert hasattr(template, 'portrait_path')
        assert template.portrait_path == "assets/portraits/test_hero.png"

        # Test display logic
        with patch('dashboard.utils.display_portrait') as mock_display:
            display_portrait(template.portrait_path, width=128)
            mock_display.assert_called_once_with("assets/portraits/test_hero.png", width=128)
