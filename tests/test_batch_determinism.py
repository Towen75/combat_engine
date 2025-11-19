"""Tests for batch simulation determinism.

Validates that batch simulations produce identical results when run with the same seed.
"""

import pytest
from src.core.models import Entity, EntityStats
from src.simulation.batch_runner import SimulationBatchRunner


@pytest.fixture
def warrior():
    """Create a warrior entity for testing."""
    stats = EntityStats(
        base_damage=25.0,
        attack_speed=1.0,
        crit_chance=0.1,
        crit_damage=1.5,
        pierce_ratio=0.05,
        max_health=150.0,
        armor=15.0,
        resistances=0.0
    )
    return Entity("warrior", stats, "Warrior", "Rare")


@pytest.fixture
def mage():
    """Create a mage entity for testing."""
    stats = EntityStats(
        base_damage=30.0,
        attack_speed=0.8,
        crit_chance=0.15,
        crit_damage=1.5,
        pierce_ratio=0.02,
        max_health=80.0,
        armor=5.0,
        resistances=0.2
    )
    return Entity("mage", stats, "Mage", "Epic")


class TestBatchDeterminism:
    """Test deterministic behavior of batch simulations."""
    
    def test_batch_determinism_small(self, warrior, mage):
        """Test that small batches produce identical results with same seed."""
        runner = SimulationBatchRunner(batch_id="test_batch")
        
        # Run batch with seed=42, 10 iterations
        result1 = runner.run_batch(warrior, mage, iterations=10, base_seed=42, max_duration=10.0)
        
        # Run again with same seed
        result2 = runner.run_batch(warrior, mage, iterations=10, base_seed=42, max_duration=10.0)
        
        # Assert bit-identical results
        assert result1.winners == result2.winners, "Winners should be identical"
        assert result1.remaining_hps == result2.remaining_hps, "Remaining HPs should be identical"
        assert result1.durations == result2.durations, "Durations should be identical"
    
    def test_batch_determinism_large(self, warrior, mage):
        """Test that larger batches produce identical results with same seed."""
        runner = SimulationBatchRunner(batch_id="test_batch_large")
        
        # Run batch with seed=42, 100 iterations
        result1 = runner.run_batch(warrior, mage, iterations=100, base_seed=42, max_duration=10.0)
        
        # Run again with same seed
        result2 = runner.run_batch(warrior, mage, iterations=100, base_seed=42, max_duration=10.0)
        
        # Assert bit-identical results
        assert result1.winners == result2.winners, "Winners should be identical"
        assert result1.remaining_hps == result2.remaining_hps, "Remaining HPs should be identical"
        assert len(result1.winners) == 100, "Should have 100 results"
    
    def test_different_seeds_produce_different_results(self, warrior, mage):
        """Test that different seeds produce different results."""
        runner = SimulationBatchRunner(batch_id="test_batch_diff")
        
        # Run with seed=42
        result1 = runner.run_batch(warrior, mage, iterations=50, base_seed=42, max_duration=10.0)
        
        # Run with seed=123
        result2 = runner.run_batch(warrior, mage, iterations=50, base_seed=123, max_duration=10.0)
        
        # Results should be different (with very high probability)
        # At least some winners or HPs should differ
        assert (result1.winners != result2.winners or 
                result1.remaining_hps != result2.remaining_hps), \
            "Different seeds should produce different results"
    
    def test_batch_result_structure(self, warrior, mage):
        """Test that batch results have correct structure."""
        runner = SimulationBatchRunner(batch_id="test_structure")
        
        result = runner.run_batch(warrior, mage, iterations=5, base_seed=42, max_duration=10.0)
        
        # Check basic structure
        assert result.batch_id == "test_structure"
        assert result.iterations == 5
        assert result.base_seed == 42
        assert len(result.winners) == 5
        assert len(result.remaining_hps) == 5
        assert len(result.durations) == 5
        
        # Check statistics are present
        assert 'mean_dps' in result.dps_stats
        assert 'median_dps' in result.dps_stats
        assert 'entities' in result.win_rate_stats
    
    def test_batch_statistics_consistency(self, warrior, mage):
        """Test that batch statistics are consistent across runs."""
        runner = SimulationBatchRunner(batch_id="test_stats")
        
        result1 = runner.run_batch(warrior, mage, iterations=20, base_seed=42, max_duration=10.0)
        result2 = runner.run_batch(warrior, mage, iterations=20, base_seed=42, max_duration=10.0)
        
        # DPS stats should be identical
        assert result1.dps_stats['mean_dps'] == result2.dps_stats['mean_dps']
        assert result1.dps_stats['median_dps'] == result2.dps_stats['median_dps']
        
        # Win rate stats should be identical
        entities1 = set(result1.win_rate_stats['entities'].keys())
        entities2 = set(result2.win_rate_stats['entities'].keys())
        assert entities1 == entities2
        
        for entity_id in entities1:
            assert result1.win_rate_stats['entities'][entity_id]['wins'] == \
                   result2.win_rate_stats['entities'][entity_id]['wins']
