import logging
import sys
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

# Ensure logging goes to stdout for Streamlit visibility
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Hardcoded campaign for Slice 1
CAMPAIGN_STAGES = [
    "goblin_grunt",       # Stage 1.1
    "enemy_warrior_grunt",       # Stage 1.2
    "enemy_rogue_thief",       # Stage 1.3
    "enemy_mage_novice",       # Stage 1.4
    "orc_warrior",        # Stage 2.1
    "enemy_warrior_guard",       # Stage 2.2
    "enemy_rogue_assassin",  # Stage 2.3
    "enemy_mage_sorcerer",  # Stage 2.4
    "enemy_warrior_boss",  # Stage 3.1
    "enemy_rouge_boss",  # Stage 3.2
    "enemy_mage_boss"  # Stage 3.3
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
        self.last_report: Dict[str, Any] = {}
        self.combat_log: List[Dict[str, Any]] = []  # History of combat reports

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
        factory = EntityFactory(provider=self.provider, item_generator=item_gen, rng=rng)

        # Spawn Player
        try:
            self.player = factory.create(archetype_id, instance_id="hero_player")
        except ValueError as e:
            logger.error(f"Failed to spawn player: {e}")
            self.state = GameState.LOBBY

    def execute_combat_turn(self) -> bool:
        """
        Run the combat simulation for the current stage.
        Returns True if player won, False if died.
        """
        if self.state != GameState.PREPARATION:
            logger.error(f"Invalid state for combat: {self.state}")
            return False

        self.state = GameState.COMBAT
        try:
            # 1. Deterministic RNG for this specific stage
            # Logic: Master Seed + Stage Index ensures Stage 3 is always Stage 3
            stage_seed = self.master_seed + self.current_stage
            rng = RNG(stage_seed)

            # 2. Setup Systems
            event_bus = EventBus()
            state_manager = StateManager(event_bus)  # ✅ Pass event_bus to StateManager
            combat_engine = CombatEngine(rng)

            # Reset state manager to ensure clean slate
            state_manager.reset_system()

            # 3. Setup Loot
            item_gen = self._get_item_generator(rng)
            loot_manager = LootManager(self.provider, item_gen, rng)

            # 4. Spawn Enemy
            factory = EntityFactory(provider=self.provider, item_generator=item_gen, rng=rng)
            enemy_id = self._get_current_enemy_id()
            enemy = factory.create(enemy_id, instance_id=f"enemy_stage_{self.current_stage}")

        except Exception as e:
            self.state = GameState.PREPARATION
            return False

        try:
            # 5. Register Entities
            if self.player is None:
                self.state = GameState.LOBBY
                return False

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

            runner = SimulationRunner(combat_engine, state_manager, event_bus, rng, provider=self.provider)

            # Add entities to runner (Vital for attack timers)
            runner.entities.append(self.player)
            runner.entities.append(enemy)

            # Initialize attack timers manually
            runner.attack_timers[self.player.id] = 1.0 / max(0.1, self.player.final_stats.attack_speed)
            runner.attack_timers[enemy.id] = 1.0 / max(0.1, enemy.final_stats.attack_speed)

            # Run for max 60 seconds or until death
            runner.run_simulation(duration=60.0)

            # Store report for UI
            self.last_report = runner.get_simulation_report()
            # Add to combat history for weapon comparison analytics
            self.combat_log.append(self.last_report)
            # Keep only last 10 combats to avoid memory issues
            if len(self.combat_log) > 10:
                self.combat_log.pop(0)

        except Exception as e:
            self.state = GameState.PREPARATION
            return False

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
            return True
        elif not player_state.is_alive:
            self.state = GameState.GAME_OVER
            return False
        else:
            # Both alive = Timeout
            self.state = GameState.GAME_OVER
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
        return ItemGenerator(provider=self.provider, rng=rng)
