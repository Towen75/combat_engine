"""Batch simulation runner for high-volume deterministic combat testing.

Provides SimulationBatchRunner for running thousands of combat simulations
with deterministic seeding and comprehensive result collection.
"""

import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from src.core.models import Entity
from src.core.state import StateManager
from src.core.events import EventBus, OnHitEvent
from src.combat.engine import CombatEngine
from .. import simulation as sim_module
from .aggregators import DpsAggregator, WinRateAggregator


@dataclass
class BatchResult:
    """Results from a batch of combat simulations.
    
    Contains aggregated statistics and per-fight details.
    """
    batch_id: str
    iterations: int
    base_seed: int
    
    # Per-fight results
    winners: List[str] = field(default_factory=list)
    remaining_hps: List[float] = field(default_factory=list)
    durations: List[float] = field(default_factory=list)
    
    # Aggregated statistics
    dps_stats: Dict[str, float] = field(default_factory=dict)
    win_rate_stats: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization.
        
        Returns:
            Dictionary representation of batch results
        """
        return {
            "batch_id": self.batch_id,
            "iterations": self.iterations,
            "base_seed": self.base_seed,
            "winners": self.winners,
            "remaining_hps": self.remaining_hps,
            "durations": self.durations,
            "dps_stats": self.dps_stats,
            "win_rate_stats": self.win_rate_stats,
        }


class SimulationBatchRunner:
    """Runs batches of deterministic combat simulations.
    
    Implements PR-P2S5 requirements for high-volume testing with:
    - Deterministic seeding (base_seed + iteration)
    - RNG injection into all components
    - Mandatory cleanup via StateManager.reset_system()
    - Statistical aggregation
    """
    
    def __init__(self, batch_id: Optional[str] = None):
        """Initialize the batch runner.
        
        Args:
            batch_id: Optional identifier for this batch
        """
        self.batch_id = batch_id or "default_batch"
    
    def run_batch(
        self,
        attacker_template: Entity,
        defender_template: Entity,
        iterations: int,
        base_seed: int,
        max_duration: float = 30.0
    ) -> BatchResult:
        """Run a batch of combat simulations with deterministic seeding.
        
        Each iteration uses seed = base_seed + i for reproducibility.
        
        Args:
            attacker_template: Template entity for the attacker
            defender_template: Template entity for the defender
            iterations: Number of simulations to run
            base_seed: Base random seed for deterministic results
            max_duration: Maximum duration per simulation in seconds
            
        Returns:
            BatchResult with aggregated statistics and per-fight details
        """
        # Initialize aggregators
        dps_aggregator = DpsAggregator()
        win_rate_aggregator = WinRateAggregator()
        
        # Result tracking
        result = BatchResult(
            batch_id=self.batch_id,
            iterations=iterations,
            base_seed=base_seed
        )
        
        for i in range(iterations):
            # 1. Create deterministic seed for this specific run
            run_seed = base_seed + i
            rng = random.Random(run_seed)
            
            # 2. Inject RNG into all components (PR-P1S2 compliance)
            combat_engine = CombatEngine(rng=rng)
            state_manager = StateManager()
            event_bus = EventBus()
            
            # 3. Create fresh entity instances for this simulation
            # Use the template's base_stats to create new entity objects
            attacker = Entity(
                id=f"{attacker_template.id}_sim{i}",
                base_stats=attacker_template.base_stats,
                name=attacker_template.name,
                rarity=attacker_template.rarity.value if hasattr(attacker_template.rarity, 'value') else str(attacker_template.rarity)
            )
            defender = Entity(
                id=f"{defender_template.id}_sim{i}",
                base_stats=defender_template.base_stats,
                name=defender_template.name,
                rarity=defender_template.rarity.value if hasattr(defender_template.rarity, 'value') else str(defender_template.rarity)
            )
            
            # Copy equipment if present
            if hasattr(attacker_template, 'equipment') and attacker_template.equipment:
                attacker.equipment = attacker_template.equipment.copy()
            if hasattr(defender_template, 'equipment') and defender_template.equipment:
                defender.equipment = defender_template.equipment.copy()
            
            # 4. Run simulation
            runner = sim_module.SimulationRunner(combat_engine, state_manager, event_bus)
            runner.add_entity(attacker)
            runner.add_entity(defender)
            
            # Track DPS for this fight
            dps_aggregator.start_fight(timestamp=0.0)
            
            # Run the simulation
            runner.run_simulation(max_duration)
            
            # End DPS tracking
            fight_dps = dps_aggregator.end_fight()
            
            # 5. Collect results
            # Determine winner (entity with health > 0)
            attacker_alive = state_manager.get_is_alive(attacker.id)
            defender_alive = state_manager.get_is_alive(defender.id)
            
            if attacker_alive and not defender_alive:
                winner_id = attacker_template.id  # Use template ID for aggregation
                loser_id = defender_template.id
                remaining_hp = state_manager.get_current_health(attacker.id)
            elif defender_alive and not attacker_alive:
                winner_id = defender_template.id
                loser_id = attacker_template.id
                remaining_hp = state_manager.get_current_health(defender.id)
            elif attacker_alive and defender_alive:
                # Both alive - timeout, pick one with more HP
                attacker_hp = state_manager.get_current_health(attacker.id)
                defender_hp = state_manager.get_current_health(defender.id)
                if attacker_hp >= defender_hp:
                    winner_id = attacker_template.id
                    loser_id = defender_template.id
                    remaining_hp = attacker_hp
                else:
                    winner_id = defender_template.id
                    loser_id = attacker_template.id
                    remaining_hp = defender_hp
            else:
                # Both dead - draw, pick attacker arbitrarily
                winner_id = attacker_template.id
                loser_id = defender_template.id
                remaining_hp = 0.0
            
            # Record outcome
            result.winners.append(winner_id)
            result.remaining_hps.append(remaining_hp)
            result.durations.append(max_duration)  # Use actual duration if available
            
            win_rate_aggregator.record_outcome(winner_id, loser_id, remaining_hp)
            
            # 6. Mandatory cleanup (PR #9 compliance)
            state_manager.reset_system()
        
        # Compile aggregated statistics
        result.dps_stats = dps_aggregator.get_summary()
        result.win_rate_stats = win_rate_aggregator.get_summary()
        
        return result
