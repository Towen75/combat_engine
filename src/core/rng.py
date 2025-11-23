"""Deterministic RNG wrapper for all simulation randomness.

This module provides a single, injectable RNG class that replaces all uses
of Python's global random module. All randomness in the combat engine must
flow through this wrapper to ensure deterministic, reproducible simulations.
"""

import random
from typing import Optional, Sequence, TypeVar, List

T = TypeVar('T')


class RNG:
    """Deterministic RNG wrapper for all simulation randomness.
    
    Acts as a facade over Python's random.Random with a cleaner API
    and explicit seeding requirements for deterministic testing.
    
    Examples:
        >>> rng = RNG(seed=42)
        >>> rng.random()  # Deterministic float
        >>> rng.roll(0.5)  # 50% probability check
        >>> rng.choice(['a', 'b', 'c'])  # Random selection
    """

    def __init__(self, seed: Optional[int] = None):
        """Initialize the RNG with an optional seed.
        
        Args:
            seed: Random seed for reproducible results. If None, uses
                  system entropy (non-deterministic).
        """
        self._rng = random.Random(seed)
        self._seed = seed

    def random(self) -> float:
        """Return a random float in the range [0.0, 1.0).
        
        Returns:
            Random float value
        """
        return self._rng.random()

    def randint(self, a: int, b: int) -> int:
        """Return a random integer N such that a <= N <= b.
        
        Args:
            a: Lower bound (inclusive)
            b: Upper bound (inclusive)
            
        Returns:
            Random integer in range [a, b]
        """
        return self._rng.randint(a, b)

    def roll(self, chance: float) -> bool:
        """Roll a probability and return True or False.
        
        Convenience method for probability checks (e.g., crit chance, proc rates).
        
        Args:
            chance: Probability of success (0.0 to 1.0)
            
        Returns:
            True if roll succeeds, False otherwise
            
        Examples:
            >>> rng = RNG(seed=1)
            >>> rng.roll(0.75)  # 75% chance
            True
        """
        return self._rng.random() < chance

    def choice(self, seq: Sequence[T]) -> T:
        """Return a random element from a non-empty sequence.
        
        Args:
            seq: Non-empty sequence to select from
            
        Returns:
            Random element from the sequence
            
        Raises:
            IndexError: If sequence is empty
        """
        return self._rng.choice(seq)

    def shuffle(self, seq: List[T]) -> None:
        """Shuffle a list in-place.
        
        Args:
            seq: List to shuffle (modified in-place)
        """
        self._rng.shuffle(seq)

    def sample(self, population: Sequence[T], k: int) -> List[T]:
        """Return k unique random elements from population.
        
        Args:
            population: Sequence to sample from
            k: Number of elements to select
            
        Returns:
            List of k unique elements
            
        Raises:
            ValueError: If k > len(population)
        """
        return self._rng.sample(population, k)

    def choices(
        self,
        population: Sequence[T],
        weights: Optional[Sequence[float]] = None,
        k: int = 1
    ) -> List[T]:
        """Return k random elements from population with replacement.

        Args:
            population: Sequence to sample from
            weights: Optional weights for each element
            k: Number of elements to select

        Returns:
            List of k elements (may contain duplicates)
        """
        return self._rng.choices(population, weights=weights, k=k)

    def roll_tiered(self, thresholds: list[float]) -> int:
        """
        Rolls against a list of ascending probability thresholds.
        Returns the index of the tier hit.

        Args:
            thresholds: List of ascending probability thresholds (e.g., [0.1, 0.03, 0.01])

        Returns:
            Index of tier hit, or -1 if no tier hit

        Examples:
            >>> rng = RNG(seed=42)
            >>> rng.roll_tiered([0.2, 0.1, 0.02])  # Roll against 20%, 10%, 2% tiers
            0  # Hit first tier
        """
        for idx, threshold in enumerate(thresholds):
            if self.roll(threshold):
                return idx
        return -1

    def weighted_choice(self, items: list[T], weights: list[float]) -> T:
        """
        Return a weighted random choice from items based on weights.

        Args:
            items: List of items to choose from
            weights: Corresponding weights for each item

        Returns:
            Randomly selected item based on weights

        Examples:
            >>> rng = RNG(seed=42)
            >>> rng.weighted_choice(['A', 'B', 'C'], [0.5, 0.3, 0.2])
            'A'  # Will tend to pick 'A' most often
        """
        if len(items) != len(weights):
            raise ValueError("items and weights must have same length")

        total = sum(weights)
        r = self.random() * total

        for item, weight in zip(items, weights):
            if r < weight:
                return item
            r -= weight

        # Fallback (should rarely happen due to floating point precision)
        return items[-1]

    @property
    def seed(self) -> Optional[int]:
        """Get the seed used to initialize this RNG.
        
        Returns:
            The seed value, or None if initialized without a seed
        """
        return self._seed

    def __repr__(self) -> str:
        """Return a string representation of the RNG."""
        return f"RNG(seed={self._seed})"
