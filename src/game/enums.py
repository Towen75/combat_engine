from enum import Enum

class GameState(str, Enum):
    LOBBY = "Lobby"             # Character selection
    PREPARATION = "Preparation" # Inventory management / Outfitting
    COMBAT = "Combat"           # Running simulation
    VICTORY = "Victory"         # Loot collection
    GAME_OVER = "Game Over"     # Defeat screen
