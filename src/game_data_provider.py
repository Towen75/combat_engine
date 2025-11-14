"""Game Data Provider - Centralized access to game data files.

Provides a singleton interface for accessing game data loaded from JSON files.
Centralizes data loading and provides consistent access patterns across the application.
"""

import json
import os
from typing import Dict, Any, Optional


class GameDataProvider:
    """Singleton provider for game data loaded from JSON files.

    Manages loading and access to game data files like game_data.json.
    Uses singleton pattern to ensure data is loaded once and shared across the application.
    """

    _instance: Optional["GameDataProvider"] = None
    _data: Optional[Dict[str, Any]] = None

    def __new__(cls) -> "GameDataProvider":
        """Singleton pattern - return existing instance or create new one."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the provider. Only loads data on first instantiation due to singleton."""
        if self._data is None:
            self._load_game_data()

    def _load_game_data(self) -> None:
        """Load game data from data/game_data.json file."""
        data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'game_data.json')

        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
            print(f"GameDataProvider: Successfully loaded data from {data_file}")

        except FileNotFoundError:
            print(f"ERROR: GameDataProvider: Data file not found: {data_file}")
            print("Please run src/data_parser.py to generate game_data.json")
            self._data = {}
        except json.JSONDecodeError as e:
            print(f"ERROR: GameDataProvider: Invalid JSON in {data_file}: {e}")
            self._data = {}
        except Exception as e:
            print(f"ERROR: GameDataProvider: Unexpected error loading data: {e}")
            self._data = {}

    def get_data(self) -> Dict[str, Any]:
        """Get the complete game data dictionary.

        Returns:
            Dictionary containing all game data loaded from game_data.json
        """
        if self._data is None:
            self._load_game_data()
        return self._data or {}

    def get_affixes(self) -> Dict[str, Any]:
        """Get the affixes data section.

        Returns:
            Dictionary of affix definitions
        """
        return self.get_data().get('affixes', {})

    def get_items(self) -> Dict[str, Any]:
        """Get the items data section.

        Returns:
            Dictionary of item templates
        """
        return self.get_data().get('items', {})

    def get_quality_tiers(self) -> Dict[str, Any]:
        """Get the quality tiers data section.

        Returns:
            Dictionary of quality tier definitions
        """
        return self.get_data().get('quality_tiers', {})

    def get_effects(self) -> Dict[str, Any]:
        """Get the effects data section.

        Returns:
            Dictionary of effect configurations (future extension)
        """
        return self.get_data().get('effects', {})

    def reload_data(self) -> bool:
        """Reload game data from disk.

        Useful during development when data files change.

        Returns:
            True if data was successfully reloaded, False if there were errors
        """
        old_data = self._data
        self._data = None
        try:
            self._load_game_data()
            success = self._data is not None and len(self._data) > 0
            if not success:
                print("GameDataProvider: Reload failed, reverting to previous data")
                self._data = old_data
            return success
        except Exception:
            print("GameDataProvider: Reload failed, reverting to previous data")
            self._data = old_data
            return False

    def is_data_loaded(self) -> bool:
        """Check if game data has been successfully loaded.

        Returns:
            True if data is loaded and not empty, False otherwise
        """
        return self._data is not None and len(self._data) > 0


# Convenience functions for easy access
def get_game_data() -> Dict[str, Any]:
    """Convenience function to get complete game data.

    Returns:
        Dictionary containing all game data
    """
    return GameDataProvider().get_data()


def get_affixes() -> Dict[str, Any]:
    """Convenience function to get affixes data.

    Returns:
        Dictionary of affix definitions
    """
    return GameDataProvider().get_affixes()


def get_items() -> Dict[str, Any]:
    """Convenience function to get items data.

    Returns:
        Dictionary of item templates
    """
    return GameDataProvider().get_items()


def get_quality_tiers() -> Dict[str, Any]:
    """Convenience function to get quality tiers data.

    Returns:
        Dictionary of quality tier definitions
    """
    return GameDataProvider().get_quality_tiers()
