"""Integration test for PR6 - Combat Math Centralization."""

from random import Random
from src.combat_engine import CombatEngine, HitContext
from src.models import Entity
from src.state import StateManager, EntityState


def test_pr6_resolve_hit_integration():
    """Test that PR6 functions integrate correctly with resolve_hit."""

    # Create test entities
    attacker = Entity(id="test_attacker", name="Test Attacker")
    attacker.final_stats.base_damage = 100
    attacker.final_stats.crit_chance = 0.5
    attacker.final_stats.crit_damage = 2.0
    attacker.final_stats.pierce_ratio = 0.0

    defender = Entity(id="test_defender", name="Test Defender")
    defender.final_stats.armor = 50
    defender.final_stats.evasion_chance = 0.0
    defender.final_stats.dodge_chance = 0.0
    defender.final_stats.block_chance = 0.0
    defender.final_stats.block_amount = 20

    # Create deterministic RNG
    rng = Random(42)
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
    assert ctx.base_damage == 100
    assert ctx.final_damage >= 0

    # Verify with seeded RNG we get deterministic results
    rng2 = Random(42)
    engine2 = CombatEngine(rng=rng2)
    ctx2 = engine2.resolve_hit(attacker, defender, state_manager)

    assert ctx.final_damage == ctx2.final_damage
    assert ctx.is_crit == ctx2.is_crit

    print(f"✅ PR6 Integration Test Passed - Damage: {ctx.final_damage}")


if __name__ == "__main__":
    test_pr6_resolve_hit_integration()
