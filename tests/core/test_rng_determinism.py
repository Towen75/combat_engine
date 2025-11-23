"""Tests for RNG determinism and repeatability.

Verifies that seeded RNG instances produce identical sequences
for reproducible simulations and debugging.
"""

import pytest
from src.core.rng import RNG


def test_rng_seeded_repeatability():
    """Test that same seed produces identical random sequences."""
    rng1 = RNG(seed=123)
    rng2 = RNG(seed=123)
    
    # Generate sequences
    sequence1 = [rng1.random() for _ in range(10)]
    sequence2 = [rng2.random() for _ in range(10)]
    
    assert sequence1 == sequence2, "Seeded RNG instances must produce identical sequences"


def test_rng_golden_values():
    """Test against golden values for regression detection.
    
    These specific values are the expected output from seed=123.
    Any change indicates RNG behavior has changed.
    """
    rng = RNG(seed=123)
    values = [rng.random() for _ in range(5)]
    
    # Golden values - DO NOT CHANGE unless RNG implementation changes
    expected = [
        0.052363598850944326,
        0.08718667752263232,
        0.4072417636703983,
        0.10770023493843905,
        0.9011988779516946,
    ]
    
    assert values == expected, "RNG golden values must not change"


def test_rng_different_seeds_produce_different_sequences():
    """Test that different seeds produce different sequences."""
    rng1 = RNG(seed=1)
    rng2 = RNG(seed=2)
    
    sequence1 = [rng1.random() for _ in range(10)]
    sequence2 = [rng2.random() for _ in range(10)]
    
    assert sequence1 != sequence2, "Different seeds must produce different sequences"


def test_rng_randint_determinism():
    """Test that randint is deterministic with seeding."""
    rng1 = RNG(seed=42)
    rng2 = RNG(seed=42)
    
    values1 = [rng1.randint(1, 100) for _ in range(20)]
    values2 = [rng2.randint(1, 100) for _ in range(20)]
    
    assert values1 == values2, "Seeded randint must produce identical sequences"


def test_rng_choice_determinism():
    """Test that choice is deterministic with seeding."""
    items = ['a', 'b', 'c', 'd', 'e']
    
    rng1 = RNG(seed=99)
    rng2 = RNG(seed=99)
    
    choices1 = [rng1.choice(items) for _ in range(20)]
    choices2 = [rng2.choice(items) for _ in range(20)]
    
    assert choices1 == choices2, "Seeded choice must produce identical sequences"


def test_rng_shuffle_determinism():
    """Test that shuffle is deterministic with seeding."""
    rng1 = RNG(seed=77)
    rng2 = RNG(seed=77)
    
    list1 = list(range(10))
    list2 = list(range(10))
    
    rng1.shuffle(list1)
    rng2.shuffle(list2)
    
    assert list1 == list2, "Seeded shuffle must produce identical results"


def test_rng_sample_determinism():
    """Test that sample is deterministic with seeding."""
    population = list(range(100))
    
    rng1 = RNG(seed=55)
    rng2 = RNG(seed=55)
    
    sample1 = rng1.sample(population, 10)
    sample2 = rng2.sample(population, 10)
    
    assert sample1 == sample2, "Seeded sample must produce identical results"


def test_rng_choices_determinism():
    """Test that weighted choices is deterministic with seeding."""
    population = ['a', 'b', 'c']
    weights = [0.5, 0.3, 0.2]
    
    rng1 = RNG(seed=33)
    rng2 = RNG(seed=33)
    
    choices1 = rng1.choices(population, weights=weights, k=20)
    choices2 = rng2.choices(population, weights=weights, k=20)
    
    assert choices1 == choices2, "Seeded weighted choices must produce identical results"


def test_rng_seed_property():
    """Test that seed property returns the initialization seed."""
    rng1 = RNG(seed=12345)
    assert rng1.seed == 12345
    
    rng2 = RNG()
    assert rng2.seed is None


def test_rng_repr():
    """Test RNG string representation."""
    rng = RNG(seed=999)
    assert repr(rng) == "RNG(seed=999)"
    
    rng_unseeded = RNG()
    assert repr(rng_unseeded) == "RNG(seed=None)"
