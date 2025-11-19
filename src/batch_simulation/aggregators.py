"""Statistical aggregators for batch simulation analysis.

Provides DPS and win rate aggregation for analyzing combat simulation results.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import statistics


@dataclass
class DpsAggregator:
    """Aggregates damage events to calculate DPS statistics.
    
    Tracks damage over time to compute min/max/avg DPS per fight
    and batch-level statistics (mean, median, standard deviation).
    """
    
    # Per-fight tracking
    _current_fight_damage: float = 0.0
    _current_fight_duration: float = 0.0
    _current_fight_start: float = 0.0
    
    # Batch-level tracking
    _fight_dps_values: List[float] = field(default_factory=list)
    _fight_damages: List[float] = field(default_factory=list)
    _fight_durations: List[float] = field(default_factory=list)
    
    def start_fight(self, timestamp: float = 0.0) -> None:
        """Start tracking a new fight.
        
        Args:
            timestamp: Starting timestamp for the fight
        """
        self._current_fight_damage = 0.0
        self._current_fight_duration = 0.0
        self._current_fight_start = timestamp
    
    def add_hit(self, damage: float, timestamp: float) -> None:
        """Record a damage event.
        
        Args:
            damage: Amount of damage dealt
            timestamp: When the damage occurred
        """
        self._current_fight_damage += damage
        self._current_fight_duration = timestamp - self._current_fight_start
    
    def end_fight(self) -> float:
        """Complete the current fight and calculate its DPS.
        
        Returns:
            DPS for the completed fight
        """
        if self._current_fight_duration <= 0:
            dps = 0.0
        else:
            dps = self._current_fight_damage / self._current_fight_duration
        
        self._fight_dps_values.append(dps)
        self._fight_damages.append(self._current_fight_damage)
        self._fight_durations.append(self._current_fight_duration)
        
        return dps
    
    def get_mean_dps(self) -> float:
        """Get mean DPS across all fights.
        
        Returns:
            Mean DPS value, or 0.0 if no fights recorded
        """
        if not self._fight_dps_values:
            return 0.0
        return statistics.mean(self._fight_dps_values)
    
    def get_median_dps(self) -> float:
        """Get median DPS across all fights.
        
        Returns:
            Median DPS value, or 0.0 if no fights recorded
        """
        if not self._fight_dps_values:
            return 0.0
        return statistics.median(self._fight_dps_values)
    
    def get_stdev_dps(self) -> float:
        """Get standard deviation of DPS across all fights.
        
        Returns:
            Standard deviation, or 0.0 if insufficient data
        """
        if len(self._fight_dps_values) < 2:
            return 0.0
        return statistics.stdev(self._fight_dps_values)
    
    def get_min_dps(self) -> float:
        """Get minimum DPS across all fights.
        
        Returns:
            Minimum DPS value, or 0.0 if no fights recorded
        """
        if not self._fight_dps_values:
            return 0.0
        return min(self._fight_dps_values)
    
    def get_max_dps(self) -> float:
        """Get maximum DPS across all fights.
        
        Returns:
            Maximum DPS value, or 0.0 if no fights recorded
        """
        if not self._fight_dps_values:
            return 0.0
        return max(self._fight_dps_values)
    
    def get_total_damage(self) -> float:
        """Get total damage across all fights.
        
        Returns:
            Sum of all damage dealt
        """
        return sum(self._fight_damages)
    
    def get_mean_ttk(self) -> float:
        """Get mean time-to-kill across all fights.
        
        Returns:
            Mean fight duration in seconds
        """
        if not self._fight_durations:
            return 0.0
        return statistics.mean(self._fight_durations)
    
    def get_median_ttk(self) -> float:
        """Get median time-to-kill across all fights.
        
        Returns:
            Median fight duration in seconds
        """
        if not self._fight_durations:
            return 0.0
        return statistics.median(self._fight_durations)
    
    def get_fight_count(self) -> int:
        """Get number of fights recorded.
        
        Returns:
            Number of completed fights
        """
        return len(self._fight_dps_values)
    
    def get_summary(self) -> Dict[str, float]:
        """Get comprehensive DPS statistics summary.
        
        Returns:
            Dictionary with all DPS statistics
        """
        return {
            "mean_dps": self.get_mean_dps(),
            "median_dps": self.get_median_dps(),
            "stdev_dps": self.get_stdev_dps(),
            "min_dps": self.get_min_dps(),
            "max_dps": self.get_max_dps(),
            "total_damage": self.get_total_damage(),
            "mean_ttk": self.get_mean_ttk(),
            "median_ttk": self.get_median_ttk(),
            "fight_count": self.get_fight_count(),
        }


@dataclass
class WinRateAggregator:
    """Aggregates combat outcomes to calculate win rate statistics.
    
    Tracks wins, losses, and victory margins for each entity.
    """
    
    # Entity-specific tracking
    _entity_wins: Dict[str, int] = field(default_factory=dict)
    _entity_losses: Dict[str, int] = field(default_factory=dict)
    _victory_margins: List[float] = field(default_factory=list)  # Remaining HP of winner
    
    def record_outcome(self, winner_id: str, loser_id: str, remaining_hp: float) -> None:
        """Record the outcome of a fight.
        
        Args:
            winner_id: ID of the winning entity
            loser_id: ID of the losing entity
            remaining_hp: Winner's remaining health points
        """
        # Track wins
        if winner_id not in self._entity_wins:
            self._entity_wins[winner_id] = 0
        self._entity_wins[winner_id] += 1
        
        # Track losses
        if loser_id not in self._entity_losses:
            self._entity_losses[loser_id] = 0
        self._entity_losses[loser_id] += 1
        
        # Track victory margin
        self._victory_margins.append(remaining_hp)
    
    def get_win_rate(self, entity_id: str) -> float:
        """Get win rate for a specific entity.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Win rate as a fraction (0.0 to 1.0)
        """
        wins = self._entity_wins.get(entity_id, 0)
        losses = self._entity_losses.get(entity_id, 0)
        total = wins + losses
        
        if total == 0:
            return 0.0
        return wins / total
    
    def get_total_fights(self, entity_id: str) -> int:
        """Get total number of fights for an entity.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Total fights (wins + losses)
        """
        wins = self._entity_wins.get(entity_id, 0)
        losses = self._entity_losses.get(entity_id, 0)
        return wins + losses
    
    def get_mean_victory_margin(self) -> float:
        """Get mean remaining HP of winners.
        
        Returns:
            Mean victory margin in HP
        """
        if not self._victory_margins:
            return 0.0
        return statistics.mean(self._victory_margins)
    
    def get_median_victory_margin(self) -> float:
        """Get median remaining HP of winners.
        
        Returns:
            Median victory margin in HP
        """
        if not self._victory_margins:
            return 0.0
        return statistics.median(self._victory_margins)
    
    def get_entity_summary(self, entity_id: str) -> Dict[str, any]:
        """Get comprehensive statistics for an entity.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Dictionary with win/loss statistics
        """
        wins = self._entity_wins.get(entity_id, 0)
        losses = self._entity_losses.get(entity_id, 0)
        total = wins + losses
        
        return {
            "entity_id": entity_id,
            "wins": wins,
            "losses": losses,
            "total_fights": total,
            "win_rate": self.get_win_rate(entity_id),
        }
    
    def get_all_entities(self) -> List[str]:
        """Get list of all entities that participated in fights.
        
        Returns:
            List of entity IDs
        """
        entities = set(self._entity_wins.keys()) | set(self._entity_losses.keys())
        return sorted(list(entities))
    
    def get_summary(self) -> Dict[str, any]:
        """Get comprehensive win rate statistics summary.
        
        Returns:
            Dictionary with all win rate statistics
        """
        entities = self.get_all_entities()
        
        return {
            "entities": {eid: self.get_entity_summary(eid) for eid in entities},
            "mean_victory_margin": self.get_mean_victory_margin(),
            "median_victory_margin": self.get_median_victory_margin(),
            "total_fights": len(self._victory_margins),
        }
