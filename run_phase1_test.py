#!/usr/bin/env python3
"""
Phase 1 Integration Test: "First Hit" Demo

This script demonstrates the complete Phase 1 combat system by simulating
a single attack from one entity to another, combining all Phase 1 components:
- Entity creation with stats
- State management
- Damage calculation
- Health tracking

Expected output for the test scenario:
- Attacker: base_damage=120, pierce_ratio=0.1
- Defender: max_health=1000, armor=150
- Damage calculation: max(120-150, 120*0.1) = max(-30, 12) = 12
- Defender health: 1000 → 988
"""

import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

from src.models import Entity, EntityStats
from src.state import StateManager
from src.engine import CombatEngine


def main():
    """Run the Phase 1 integration test."""
    print("=== Phase 1: First Hit Test ===")
    print("Testing complete combat system integration")
    print()

    # Create test entities
    print("1. Creating test entities...")

    # Attacker: Strong but low pierce
    attacker_stats = EntityStats(base_damage=120.0, pierce_ratio=0.1)
    attacker = Entity(id="player_1", base_stats=attacker_stats, name="Hero")

    # Defender: Heavily armored
    defender_stats = EntityStats(max_health=1000.0, armor=150.0)
    defender = Entity(id="enemy_1", base_stats=defender_stats, name="Armored Knight")

    print(f"   Attacker: {attacker} (Damage: {attacker.stats.base_damage}, Pierce: {attacker.stats.pierce_ratio})")
    print(f"   Defender: {defender} (Health: {defender.stats.max_health}, Armor: {defender.stats.armor})")
    print()

    # Set up state management
    print("2. Initializing combat state...")
    state_manager = StateManager()
    state_manager.register_entity(attacker)
    state_manager.register_entity(defender)

    defender_state = state_manager.get_state(defender.id)
    assert defender_state is not None, f"Defender {defender.id} not registered"
    initial_hp = defender_state.current_health
    print(f"   {defender} initial health: {initial_hp}")
    print()

    # Execute the attack
    print("3. Executing attack...")

    # Calculate damage
    engine = CombatEngine()
    damage_context = engine.resolve_hit(attacker, defender, state_manager)
    damage = damage_context.final_damage
    print(f"   {attacker} attacks {defender} for {damage:.2f} damage")

    # Show damage breakdown for analysis
    breakdown = CombatEngine.calculate_effective_damage(attacker, defender)
    print("   Damage breakdown:")
    print(f"     Attack damage: {breakdown['attack_damage']}")
    print(f"     Pre-pierce damage: {breakdown['pre_pierce_damage']}")
    print(f"     Pierced damage: {breakdown['pierced_damage']}")
    print(f"     Armor reduction: {breakdown['armor_reduction']}")
    print(f"     Final damage: {breakdown['final_damage']}")
    print()

    # Apply damage to defender
    print("4. Applying damage...")
    state_manager.apply_damage(defender.id, damage)

    final_defender_state = state_manager.get_state(defender.id)
    assert final_defender_state is not None, f"Defender {defender.id} state lost"
    final_hp = final_defender_state.current_health
    is_alive = final_defender_state.is_alive

    print(f"   {defender} final health: {final_hp}")
    print(f"   {defender} is alive: {is_alive}")
    print()

    # Verify expected results
    print("5. Verification...")
    expected_damage = 12.0  # max(120-150, 120*0.1) = max(-30, 12) = 12
    expected_final_hp = 988.0  # 1000 - 12

    if abs(damage - expected_damage) < 0.01:
        print("   ✅ Damage calculation correct")
    else:
        print(f"   ❌ Damage calculation incorrect. Expected: {expected_damage}, Got: {damage}")

    if abs(final_hp - expected_final_hp) < 0.01:
        print("   ✅ Health tracking correct")
    else:
        print(f"   ❌ Health tracking incorrect. Expected: {expected_final_hp}, Got: {final_hp}")

    if is_alive:
        print("   ✅ Alive status correct")
    else:
        print("   ❌ Alive status incorrect")

    print()
    print("=== Test Complete ===")

    # Return success/failure for automated testing
    success = (abs(damage - expected_damage) < 0.01 and
               abs(final_hp - expected_final_hp) < 0.01 and
               is_alive)
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
