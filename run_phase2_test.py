#!/usr/bin/env python3
"""Phase 2 Integration Test - Critical Hits, Events, and DoTs."""

import random
from src.models import Entity, EntityStats
from src.events import EventBus
from src.state import StateManager
from src.combat import process_attack
from src.effect_handlers import BleedHandler


def main():
    """Run the Phase 2 integration test."""
    print("=== Phase 2: Crit & Event Test ===")

    # Set up seeded random for reproducible results
    random.seed(42)

    # Create EventBus and StateManager
    event_bus = EventBus()
    state_manager = StateManager()

    # Create attacker (Rare - Tier 2 crits)
    attacker_stats = EntityStats(
        base_damage=100.0,
        crit_chance=0.8,  # High crit chance for testing
        crit_damage=2.0,
        pierce_ratio=0.1
    )
    attacker = Entity(id="player_1", stats=attacker_stats, rarity="Rare")

    # Create defender
    defender_stats = EntityStats(max_health=2000.0, armor=100.0)
    defender = Entity(id="enemy_1", stats=defender_stats)

    # Register entities
    state_manager.register_entity(attacker)
    state_manager.register_entity(defender)

    # Register effect handler
    bleed_handler = BleedHandler(event_bus, state_manager, proc_rate=0.6)  # 60% proc rate

    print(f"Attacker is '{attacker.rarity}', using Crit Tier {attacker.get_crit_tier()}.")
    print(f"Defender starts with {defender.stats.max_health} health.")
    print()

    # Simulate 5 attacks
    for i in range(5):
        print(f"Attack #{i+1}:")
        hit_context = process_attack(attacker, defender, event_bus, state_manager)

        is_crit_str = "CRITICAL HIT!" if hit_context.is_crit else "Normal Hit."
        print(f"  > {is_crit_str} Damage: {hit_context.final_damage:.2f}")

        # Show current defender state
        defender_state = state_manager.get_state(defender.id)
        assert defender_state is not None, "Defender state should not be None"
        print(f"  > Defender Health: {defender_state.current_health:.2f}")

        if defender_state.active_debuffs:
            for debuff_name, debuff in defender_state.active_debuffs.items():
                print(f"  > Debuff: {debuff_name}, Stacks: {debuff.stacks}, Time: {debuff.time_remaining:.1f}s")
        else:
            print("  > No debuffs applied.")

        print()

    # Final state summary
    print("--- Final State ---")
    defender_state = state_manager.get_state(defender.id)
    assert defender_state is not None, "Defender state should not be None"
    print(f"Defender Health: {defender_state.current_health:.2f} / {defender.stats.max_health}")
    if defender_state.active_debuffs:
        print("Active Debuffs:")
        for debuff_name, debuff in defender_state.active_debuffs.items():
            print(f"  - {debuff_name}: {debuff.stacks} stacks, {debuff.time_remaining:.1f}s remaining")
    else:
        print("No debuffs applied.")

    print("\n=== Phase 2 Test Complete ===")


if __name__ == "__main__":
    main()
