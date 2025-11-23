"""Test fixtures and helper functions for Combat Engine tests."""

import pytest
from pathlib import Path
from typing import Optional
from src.core.models import Entity, EntityStats
from src.core.state import StateManager
from src.core.rng import RNG
from src.data.game_data_provider import GameDataProvider


@pytest.fixture(scope="session")
def game_data_provider():
    """Provides GameDataProvider for tests."""
    data_dir = Path(__file__).parent.parent / 'data'
    return GameDataProvider(data_dir)


def make_rng(seed: int = 42) -> RNG:
    """Create a deterministic random number generator for testing.

    Args:
        seed: Random seed for reproducible results

    Returns:
        Configured RNG instance
    """
    return RNG(seed)


def make_entity(
    entity_id: str,
    name: Optional[str] = None,
    base_damage: float = 100.0,
    armor: float = 50.0,
    crit_chance: float = 0.1,
    crit_damage: float = 1.5,
    pierce_ratio: float = 0.1,
    max_health: float = 1000.0,
    evasion_chance: float = 0.0,
    dodge_chance: float = 0.0,
    block_chance: float = 0.0,
    block_amount: float = 0.0,
    rarity: str = "Common"
) -> Entity:
    """Create a test entity with common default values.

    Args:
        entity_id: Unique identifier for the entity
        name: Display name (defaults to entity_id if None)
        base_damage: Base damage stat
        armor: Armor stat
        crit_chance: Critical hit chance (0.0 to 1.0)
        crit_damage: Critical hit damage multiplier
        pierce_ratio: Armor pierce ratio
        max_health: Maximum health
        rarity: Entity rarity tier

    Returns:
        Configured Entity instance
    """
    stats = EntityStats(
        base_damage=base_damage,
        armor=armor,
        crit_chance=crit_chance,
        crit_damage=crit_damage,
        pierce_ratio=pierce_ratio,
        max_health=max_health,
        evasion_chance=evasion_chance,
        dodge_chance=dodge_chance,
        block_chance=block_chance,
        block_amount=block_amount
    )
    return Entity(
        id=entity_id,
        base_stats=stats,
        name=name or entity_id,
        rarity=rarity
    )


def make_attacker(
    base_damage: float = 100.0,
    crit_chance: float = 0.1,
    crit_damage: float = 1.5,
    pierce_ratio: float = 0.1,
    rarity: str = "Common"
) -> Entity:
    """Create a test attacker entity with offensive-focused stats.

    Args:
        base_damage: Attack damage
        crit_chance: Critical hit chance
        crit_damage: Critical hit multiplier
        pierce_ratio: Armor pierce ratio
        rarity: Entity rarity

    Returns:
        Configured attacker Entity
    """
    return make_entity(
        entity_id="attacker",
        name="Test Attacker",
        base_damage=base_damage,
        armor=10.0,  # Low armor for attackers
        crit_chance=crit_chance,
        crit_damage=crit_damage,
        pierce_ratio=pierce_ratio,
        max_health=800.0,
        rarity=rarity
    )


def make_defender(
    armor: float = 50.0,
    max_health: float = 1000.0,
    pierce_ratio: float = 0.05,
    evasion_chance: float = 0.0,
    dodge_chance: float = 0.0,
    block_chance: float = 0.0,
    block_amount: float = 0.0
) -> Entity:
    """Create a test defender entity with defensive-focused stats.

    Args:
        armor: Armor value
        max_health: Health pool
        pierce_ratio: Armor pierce ratio (typically low for defenders)
        evasion_chance: Evasion chance (0.0 to 1.0)
        dodge_chance: Dodge chance (0.0 to 1.0)
        block_chance: Block chance (0.0 to 1.0)
        block_amount: Block damage reduction amount

    Returns:
        Configured defender Entity
    """
    return make_entity(
        entity_id="defender",
        name="Test Defender",
        base_damage=50.0,  # Low damage for defenders
        armor=armor,
        crit_chance=0.05,  # Low crit chance
        crit_damage=1.2,   # Low crit damage
        pierce_ratio=pierce_ratio,
        max_health=max_health,
        evasion_chance=evasion_chance,
        dodge_chance=dodge_chance,
        block_chance=block_chance,
        block_amount=block_amount,
        rarity="Common"
    )


def make_high_armor_defender() -> Entity:
    """Create a defender with very high armor for pierce testing."""
    return make_defender(armor=150.0, max_health=1200.0)


def make_glass_cannon_attacker() -> Entity:
    """Create an attacker with high damage but low survivability."""
    return make_entity(
        entity_id="glass_cannon",
        name="Glass Cannon",
        base_damage=200.0,
        armor=5.0,
        crit_chance=0.3,
        crit_damage=2.5,
        pierce_ratio=0.2,
        max_health=400.0,
        rarity="Rare"
    )


def make_tank_defender() -> Entity:
    """Create a defender with high armor and health."""
    return make_entity(
        entity_id="tank",
        name="Tank Defender",
        base_damage=30.0,
        armor=100.0,
        crit_chance=0.02,
        crit_damage=1.1,
        pierce_ratio=0.02,
        max_health=2000.0,
        rarity="Common"
    )


def make_state_manager(attacker: Optional[Entity] = None, defender: Optional[Entity] = None) -> StateManager:
    """Create a state manager pre-registered with test entities.

    Args:
        attacker: Optional attacker entity to register
        defender: Optional defender entity to register

    Returns:
        Configured StateManager instance
    """
    state_manager = StateManager()

    if attacker:
        state_manager.register_entity(attacker)

    if defender:
        state_manager.register_entity(defender)

    return state_manager
