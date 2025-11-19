"""Tests for aggregator functionality.

Validates DPS and win rate aggregation with known data.
"""

import pytest
from src.simulation.aggregators import DpsAggregator, WinRateAggregator


class TestDpsAggregator:
    """Test DPS aggregation functionality."""
    
    def test_single_fight_dps(self):
        """Test DPS calculation for a single fight."""
        aggregator = DpsAggregator()
        
        aggregator.start_fight(timestamp=0.0)
        aggregator.add_hit(damage=100, timestamp=0.5)
        aggregator.add_hit(damage=150, timestamp=1.0)
        aggregator.add_hit(damage=200, timestamp=2.0)
        dps = aggregator.end_fight()
        
        # Total damage: 450, duration: 2.0s, DPS: 225
        assert dps == 225.0
        assert aggregator.get_total_damage() == 450.0
    
    def test_multiple_fights_statistics(self):
        """Test statistics across multiple fights."""
        aggregator = DpsAggregator()
        
        # Fight 1: 100 damage in 1s = 100 DPS
        aggregator.start_fight(0.0)
        aggregator.add_hit(100, 1.0)
        aggregator.end_fight()
        
        # Fight 2: 200 damage in 1s = 200 DPS
        aggregator.start_fight(0.0)
        aggregator.add_hit(200, 1.0)
        aggregator.end_fight()
        
        # Fight 3: 150 damage in 1s = 150 DPS
        aggregator.start_fight(0.0)
        aggregator.add_hit(150, 1.0)
        aggregator.end_fight()
        
        # Mean: (100 + 200 + 150) / 3 = 150
        assert aggregator.get_mean_dps() == 150.0
        
        # Median: 150
        assert aggregator.get_median_dps() == 150.0
        
        # Min/Max
        assert aggregator.get_min_dps() == 100.0
        assert aggregator.get_max_dps() == 200.0
        
        # Fight count
        assert aggregator.get_fight_count() == 3
    
    def test_ttk_calculation(self):
        """Test time-to-kill calculation."""
        aggregator = DpsAggregator()
        
        # Fight 1: 2 seconds
        aggregator.start_fight(0.0)
        aggregator.add_hit(100, 2.0)
        aggregator.end_fight()
        
        # Fight 2: 3 seconds
        aggregator.start_fight(0.0)
        aggregator.add_hit(100, 3.0)
        aggregator.end_fight()
        
        # Fight 3: 4 seconds
        aggregator.start_fight(0.0)
        aggregator.add_hit(100, 4.0)
        aggregator.end_fight()
        
        # Mean TTK: (2 + 3 + 4) / 3 = 3
        assert aggregator.get_mean_ttk() == 3.0
        
        # Median TTK: 3
        assert aggregator.get_median_ttk() == 3.0
    
    def test_empty_aggregator(self):
        """Test aggregator with no data."""
        aggregator = DpsAggregator()
        
        assert aggregator.get_mean_dps() == 0.0
        assert aggregator.get_median_dps() == 0.0
        assert aggregator.get_min_dps() == 0.0
        assert aggregator.get_max_dps() == 0.0
        assert aggregator.get_total_damage() == 0.0
        assert aggregator.get_fight_count() == 0
    
    def test_summary_format(self):
        """Test summary dictionary format."""
        aggregator = DpsAggregator()
        
        aggregator.start_fight(0.0)
        aggregator.add_hit(100, 1.0)
        aggregator.end_fight()
        
        summary = aggregator.get_summary()
        
        assert 'mean_dps' in summary
        assert 'median_dps' in summary
        assert 'stdev_dps' in summary
        assert 'min_dps' in summary
        assert 'max_dps' in summary
        assert 'total_damage' in summary
        assert 'mean_ttk' in summary
        assert 'median_ttk' in summary
        assert 'fight_count' in summary


class TestWinRateAggregator:
    """Test win rate aggregation functionality."""
    
    def test_single_outcome(self):
        """Test recording a single outcome."""
        aggregator = WinRateAggregator()
        
        aggregator.record_outcome("warrior", "mage", remaining_hp=50.0)
        
        assert aggregator.get_win_rate("warrior") == 1.0
        assert aggregator.get_win_rate("mage") == 0.0
        assert aggregator.get_total_fights("warrior") == 1
        assert aggregator.get_total_fights("mage") == 1
    
    def test_multiple_outcomes(self):
        """Test win rate calculation across multiple fights."""
        aggregator = WinRateAggregator()
        
        # Warrior wins 3 times
        aggregator.record_outcome("warrior", "mage", 50.0)
        aggregator.record_outcome("warrior", "mage", 60.0)
        aggregator.record_outcome("warrior", "mage", 40.0)
        
        # Mage wins 2 times
        aggregator.record_outcome("mage", "warrior", 30.0)
        aggregator.record_outcome("mage", "warrior", 20.0)
        
        # Warrior: 3 wins, 2 losses = 60% win rate
        assert aggregator.get_win_rate("warrior") == 0.6
        
        # Mage: 2 wins, 3 losses = 40% win rate
        assert aggregator.get_win_rate("mage") == 0.4
        
        # Total fights
        assert aggregator.get_total_fights("warrior") == 5
        assert aggregator.get_total_fights("mage") == 5
    
    def test_victory_margins(self):
        """Test victory margin statistics."""
        aggregator = WinRateAggregator()
        
        aggregator.record_outcome("warrior", "mage", 50.0)
        aggregator.record_outcome("warrior", "mage", 60.0)
        aggregator.record_outcome("mage", "warrior", 40.0)
        
        # Mean: (50 + 60 + 40) / 3 = 50
        assert aggregator.get_mean_victory_margin() == 50.0
        
        # Median: 50
        assert aggregator.get_median_victory_margin() == 50.0
    
    def test_entity_summary(self):
        """Test entity summary format."""
        aggregator = WinRateAggregator()
        
        aggregator.record_outcome("warrior", "mage", 50.0)
        aggregator.record_outcome("mage", "warrior", 30.0)
        
        summary = aggregator.get_entity_summary("warrior")
        
        assert summary['entity_id'] == "warrior"
        assert summary['wins'] == 1
        assert summary['losses'] == 1
        assert summary['total_fights'] == 2
        assert summary['win_rate'] == 0.5
    
    def test_get_all_entities(self):
        """Test retrieving all participating entities."""
        aggregator = WinRateAggregator()
        
        aggregator.record_outcome("warrior", "mage", 50.0)
        aggregator.record_outcome("mage", "assassin", 30.0)
        
        entities = aggregator.get_all_entities()
        
        assert set(entities) == {"warrior", "mage", "assassin"}
    
    def test_empty_aggregator(self):
        """Test aggregator with no data."""
        aggregator = WinRateAggregator()
        
        assert aggregator.get_win_rate("unknown") == 0.0
        assert aggregator.get_total_fights("unknown") == 0
        assert aggregator.get_mean_victory_margin() == 0.0
        assert aggregator.get_all_entities() == []
