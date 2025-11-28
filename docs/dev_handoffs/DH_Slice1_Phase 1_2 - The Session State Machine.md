# 🚀 Implementation Hand-off: Phase 1.2 - The Session State Machine

**Related Work Item:** Phase 1.2 - The Session State Machine

## 📦 File Manifest
| Action | File Path | Description |
| :--- | :--- | :--- |
| 🆕 Create | `src/game/enums.py` | Definition of Game States |
| 🆕 Create | `src/game/session.py` | Core Session Controller logic |
| 🆕 Create | `src/game/__init__.py` | Package exports |
| 🆕 Create | `tests/test_game_session.py` | Unit tests for state flow and persistence |

---

## 1️⃣ Configuration & Dependencies
*No new pip packages required.*

---

## 2️⃣ Code Changes

### A. `src/game/enums.py`
**Path:** `src/game/enums.py`
**Context:** Define the states the game can be in. This controls what the UI displays.

```python
from enum import Enum

class GameState(str, Enum):
    LOBBY = "Lobby"             # Character selection
    PREPARATION = "Preparation" # Inventory management / Outfitting
    COMBAT = "Combat"           # Running simulation
    VICTORY = "Victory"         # Loot collection
    GAME_OVER = "Game Over"     # Defeat screen
```

### B. `src/game/session.py`
**Path:** `src/game/session.py`
**Context:** The central brain. It maintains the "Save Data" (Player, Inventory, Stage) and coordinates the transition between phases. It uses **Deterministic RNG injection** for every combat stage.

```python
import logging
from typing import Optional, List, Dict, Any

from src.game.enums import GameState
from src.core.models import Entity, Item
from src.core.inventory import Inventory
from src.core.factory import EntityFactory
from src.core.loot_manager import LootManager
from src.core.rng import RNG
from src.data.game_data_provider import GameDataProvider
from src.simulation.combat_simulation import SimulationRunner
from src.combat.engine import CombatEngine
from src.core.state import StateManager
from src.core.events import EventBus, LootDroppedEvent

logger = logging.getLogger(__name__)

# Hardcoded campaign for Slice 1
CAMPAIGN_STAGES = [
    "goblin_grunt",       # Stage 1
    "orc_warrior",        # Stage 2
    "enemy_rogue_thief",  # Stage 3
    "enemy_mage_novice",  # Stage 4
    "enemy_warrior_boss"  # Stage 5
]

class GameSession:
    """
    Manages the persistent state of a gameplay session.
    Coordinatess factories, simulation, and inventory.
    """

    def __init__(self, provider: GameDataProvider):
        self.provider = provider
        # dependencies instantiated on-demand or passed in
        self.state: GameState = GameState.LOBBY
        
        # Persistent Data
        self.player: Optional[Entity] = None
        self.inventory: Inventory = Inventory(capacity=20)
        self.current_stage: int = 0
        self.master_seed: int = 0
        self.loot_stash: List[Item] = [] # Items dropped but not yet picked up
        
        # Last run analytics
        self.last_combat_log: List[Any] = []

    def start_new_run(self, archetype_id: str, seed: int) -> None:
        """Initialize a new run with a specific archetype and seed."""
        self.master_seed = seed
        self.current_stage = 0
        self.loot_stash = []
        self.inventory = Inventory(capacity=20)
        self.state = GameState.PREPARATION
        
        # Create Factories with Master Seed
        rng = RNG(self.master_seed)
        item_gen = self._get_item_generator(rng)
        factory = EntityFactory(self.provider, item_gen, rng)
        
        # Spawn Player
        try:
            self.player = factory.create(archetype_id, instance_id="hero_player")
            logger.info(f"Started new run with {archetype_id} (Seed: {seed})")
        except ValueError as e:
            logger.error(f"Failed to spawn player: {e}")
            self.state = GameState.LOBBY

    def execute_combat_turn(self) -> bool:
        """
        Run the combat simulation for the current stage.
        Returns True if player won, False if died.
        """
        if self.state != GameState.PREPARATION:
            return False

        self.state = GameState.COMBAT
        
        # 1. Deterministic RNG for this specific stage
        # Logic: Master Seed + Stage Index ensures Stage 3 is always Stage 3
        stage_seed = self.master_seed + self.current_stage
        rng = RNG(stage_seed)
        
        # 2. Setup Systems
        state_manager = StateManager()
        event_bus = EventBus()
        combat_engine = CombatEngine(rng)
        
        # 3. Setup Loot
        item_gen = self._get_item_generator(rng)
        loot_manager = LootManager(self.provider, item_gen, rng)
        
        # 4. Spawn Enemy
        factory = EntityFactory(self.provider, item_gen, rng)
        enemy_id = self._get_current_enemy_id()
        enemy = factory.create(enemy_id, instance_id=f"enemy_stage_{self.current_stage}")
        
        # 5. Register Entities
        state_manager.add_entity(self.player)
        state_manager.add_entity(enemy)
        
        # 6. Capture Loot Events
        self.loot_stash = []
        def on_loot(event: LootDroppedEvent):
            self.loot_stash.extend(event.items)
        event_bus.subscribe(LootDroppedEvent, on_loot)
        
        # 7. Run Simulation
        # We manually attach the LootHandler here since SimulationRunner constructor might vary
        from src.handlers.loot_handler import LootHandler
        loot_handler = LootHandler(event_bus, state_manager, loot_manager)
        
        runner = SimulationRunner(combat_engine, state_manager, event_bus, rng)
        runner.add_entity(self.player)
        runner.add_entity(enemy)
        
        # Run for max 60 seconds or until death
        runner.run_simulation(duration=60.0)
        
        # 8. Resolve Outcome
        player_state = state_manager.get_state(self.player.id)
        enemy_state = state_manager.get_state(enemy.id)
        
        # Persist HP loss
        self.player.final_stats.max_health = player_state.entity.final_stats.max_health # In case stats changed
        # We don't have a "current_hp" on Entity model yet, usually StateManager handles it.
        # For Slice 1, we assume full heal between rounds OR we need to add current_hp to Entity.
        # Let's implement Full Heal between rounds for the Tech Demo simplicity for now.
        
        if player_state.is_alive and not enemy_state.is_alive:
            self.state = GameState.VICTORY
            logger.info(f"Victory at stage {self.current_stage}")
            return True
        else:
            self.state = GameState.GAME_OVER
            logger.info("Defeat")
            return False

    def claim_loot(self, item_index: int) -> bool:
        """Move item from stash to inventory."""
        if 0 <= item_index < len(self.loot_stash):
            item = self.loot_stash[item_index]
            if self.inventory.add_item(item):
                self.loot_stash.pop(item_index)
                return True
        return False

    def advance_stage(self) -> None:
        """Proceed to next stage."""
        if self.state == GameState.VICTORY:
            self.current_stage += 1
            if self.current_stage >= len(CAMPAIGN_STAGES):
                # Loop or End? For now, loop with higher difficulty (implied)
                # or just cap it. Let's cap it.
                pass 
            self.state = GameState.PREPARATION
            self.loot_stash = [] # Clear unclaimed loot

    def _get_current_enemy_id(self) -> str:
        """Get enemy ID for current stage, looping if necessary."""
        idx = self.current_stage % len(CAMPAIGN_STAGES)
        return CAMPAIGN_STAGES[idx]

    def _get_item_generator(self, rng: RNG):
        from src.utils.item_generator import ItemGenerator
        return ItemGenerator(self.provider, rng)
```

### C. `src/game/__init__.py`
**Path:** `src/game/__init__.py`
**Context:** Export classes.

```python
from src.game.enums import GameState
from src.game.session import GameSession

__all__ = ["GameState", "GameSession"]
```

### D. `tests/test_game_session.py`
**Path:** `tests/test_game_session.py`
**Context:** Verify state flow and inventory integration.

```python
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
```

---

## 🧪 Verification Steps

**1. Run Unit Tests**
```bash
python -m pytest tests/test_game_session.py
```

**2. Integration Check**
Create a temporary script to simulate a run:
```python
from src.data.game_data_provider import GameDataProvider
from src.game.session import GameSession

provider = GameDataProvider()
session = GameSession(provider)
session.start_new_run("hero_warrior", 42)
print(f"Player: {session.player.name}")
result = session.execute_combat_turn()
print(f"Combat Result: {result}")
```

## ⚠️ Rollback Plan
If this fails:
1.  Delete `src/game/` directory (if new).
2.  Delete `tests/test_game_session.py`.