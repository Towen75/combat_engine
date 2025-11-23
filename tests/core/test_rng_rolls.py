"""Tests for RNG probability rolls and combat-specific randomness.

Verifies that roll() method works correctly for crit chances,
proc rates, and other probability-based mechanics.
"""

import pytest
from src.core.rng import RNG


def test_roll_always_true():
    """Test that roll(1.0) always returns True."""
    rng = RNG(seed=1)
    results = [rng.roll(1.0) for _ in range(100)]
    assert all(results), "roll(1.0) must always return True"


def test_roll_always_false():
    """Test that roll(0.0) always returns False."""
    rng = RNG(seed=1)
    results = [rng.roll(0.0) for _ in range(100)]
    assert not any(results), "roll(0.0) must always return False"


def test_roll_deterministic():
    """Test that roll() is deterministic with seeding."""
    rng1 = RNG(seed=42)
    rng2 = RNG(seed=42)
    
    rolls1 = [rng1.roll(0.5) for _ in range(50)]
    rolls2 = [rng2.roll(0.5) for _ in range(50)]
    
    assert rolls1 == rolls2, "Seeded roll() must produce identical sequences"


    """Test that roll() produces expected distribution over many samples.
    
    With a large sample size, the proportion of True results should
    approximate the given probability.
    """
    rng = RNG(seed=12345)
    chance = 0.3
    num_trials = 10000
    
    successes = sum(rng.roll(chance) for _ in range(num_trials))
    success_rate = successes / num_trials
    
    # Allow 5% deviation from expected probability
    assert abs(success_rate - chance) < 0.05, \
        f"roll({chance}) success rate {success_rate} too far from expected"


def test_roll_crit_chance_scenario():
    """Test roll() for crit chance calculation (realistic scenario)."""
    rng = RNG(seed=999)
    crit_chance = 0.15  # 15% crit chance
    
    # Simulate 100 attacks
    crits = [rng.roll(crit_chance) for _ in range(100)]
    crit_count = sum(crits)
    
    # Should be roughly 15 crits, allow reasonable variance
    assert 5 <= crit_count <= 25, \
        f"Expected ~15 crits out of 100, got {crit_count}"


def test_roll_proc_rate_scenario():
    """Test roll() for proc rate calculation (realistic scenario)."""
    rng = RNG(seed=777)
    proc_rate = 0.33  # 33% proc chance
    
    # Simulate 100 hits
    procs = [rng.roll(proc_rate) for _ in range(100)]
    proc_count = sum(procs)
    
    # Should be roughly 33 procs, allow reasonable variance
    assert 20 <= proc_count <= 46, \
        f"Expected ~33 procs out of 100, got {proc_count}"


def test_roll_edge_cases():
    """Test roll() with edge case probabilities."""
    rng = RNG(seed=5)
    
    # Very low probability
    very_low = [rng.roll(0.001) for _ in range(100)]
    assert sum(very_low) <= 5, "Very low probability should rarely succeed"
    
    # Very high probability
    rng = RNG(seed=5)  # Reset seed
    very_high = [rng.roll(0.999) for _ in range(100)]
    assert sum(very_high) >= 95, "Very high probability should almost always succeed"


def test_roll_negative_chance_raises():
    """Test that negative probability raises appropriate error."""
    rng = RNG(seed=1)
    
    # Note: Currently roll() doesn't validate, but this documents expected behavior
    # This test may need updating if validation is added
    result = rng.roll(-0.1)
    # Negative chance effectively same as 0.0
    assert result is False


def test_roll_greater_than_one():
    """Test roll() with probability > 1.0."""
    rng = RNG(seed=1)
    
    # Probability > 1.0 should always succeed
    results = [rng.roll(1.5) for _ in range(10)]
    assert all(results), "roll(>1.0) should always return True"


def test_multiple_roll_types_in_sequence():
    """Test that different roll probabilities work correctly in sequence."""
    rng = RNG(seed=444)
    
    # Simulate a combat sequence: crit check, dodge check, proc check
    crit = rng.roll(0.20)      # 20% crit
    dodge = rng.roll(0.10)     # 10% dodge
    bleed_proc = rng.roll(0.50)  # 50% bleed proc
    
    # With seed=444, verify deterministic results
    assert isinstance(crit, bool)
    assert isinstance(dodge, bool)
    assert isinstance(bleed_proc, bool)
    
    # Verify repeatability
    rng2 = RNG(seed=444)
    assert rng2.roll(0.20) == crit
    assert rng2.roll(0.10) == dodge
    assert rng2.roll(0.50) == bleed_proc
