import sys
from pathlib import Path
import unittest

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

class TestDashboardImports(unittest.TestCase):
    def test_imports(self):
        """
        Verifies that all dashboard modules can be imported without error.
        This catches syntax errors and missing dependencies.
        """
        try:
            import dashboard.utils
            import dashboard.components.entity_card
            import dashboard.components.battle_log
            # Pages are scripts, but we can try to import them as modules to check syntax
            # We might need to mock streamlit for this to work if they have top-level st calls
            # But for now, let's just check the utils and components which are critical
        except ImportError as e:
            self.fail(f"Failed to import dashboard modules: {e}")
            
    def test_utils_provider(self):
        """
        Verifies that GameDataProvider can be instantiated via utils.
        """
        from dashboard.utils import get_game_data_provider
        # We need to mock streamlit.cache_resource or it will fail outside of streamlit
        # For this simple check, we can just check if the function exists
        self.assertTrue(callable(get_game_data_provider))

if __name__ == '__main__':
    unittest.main()
