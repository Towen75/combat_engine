"""Integration test for PR6 - Combat Math Centralization."""

from src.core.rng import RNG
from src.combat.engine import CombatEngine, HitContext
from src.core.models import Entity, EntityStats
from src.core.state import StateManager, EntityState


def test_pr6_resolve_hit_integration():
    """Test that PR6 functions integrate correctly with resolve_hit."""

    # Create test entities with base stats
    attacker_stats = EntityStats(
        base_damage=100,
        crit_chance=0.5,
        crit_damage=2.0,
        pierce_ratio=0.01  # Minimum valid value
    )
    attacker = Entity(id="test_attacker", base_stats=attacker_stats, name="Test Attacker")

    defender_stats = EntityStats(
        base_damage=50,
        armor=50,
        evasion_chance=0.0,
        dodge_chance=0.0,
        block_chance=0.0,
        block_amount=20
    )
    defender = Entity(id="test_defender", base_stats=defender_stats, name="Test Defender")

    # Create deterministic RNG
    rng = RNG(42)
    engine = CombatEngine(rng=rng)

    # Create state manager
    state_manager = StateManager()
    state_manager.add_entity(attacker)
    state_manager.add_entity(defender)

    # Resolve hit
    ctx = engine.resolve_hit(attacker, defender, state_manager)

    # Verify it's a HitContext
    assert isinstance(ctx, HitContext)

    # Verify basic properties
    assert ctx.attacker == attacker
    assert ctx.defender == defender
    assert ctx.final_damage >= 0

    # Verify with seeded RNG we get deterministic results
    rng2 = RNG(42)
    engine2 = CombatEngine(rng=rng2)
    ctx2 = engine2.resolve_hit(attacker, defender, state_manager)

    assert ctx.final_damage == ctx2.final_damage
    assert ctx.was_crit == ctx2.was_crit


if __name__ == "__main__":
    test_pr6_resolve_hit_integration()
