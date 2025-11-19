#!/usr/bin/env python3
"""Phase 3 Integration Test - Items, Skills, and Equipment."""

import random
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

from src.models import Entity, EntityStats, RolledAffix, Item
from src.skills import Skill, Trigger
from src.events import EventBus
from src.state import StateManager
from src.engine import CombatEngine
from src.effect_handlers import BleedHandler, PoisonHandler


def main():
    """Run the Phase 3 integration test."""
    print("=== Phase 3: Items, Skills & Equipment Test ===")

    # Set up seeded random for reproducible results
    random.seed(42)

    # Create EventBus and StateManager
    event_bus = EventBus()
    state_manager = StateManager()

    # Create effect handlers
    bleed_handler = BleedHandler(event_bus, state_manager, proc_rate=0.6)
    poison_handler = PoisonHandler(event_bus, state_manager, proc_rate=0.33)

    # Create player with base stats
    player_base_stats = EntityStats(
        base_damage=50.0,
        crit_chance=0.1,
        crit_damage=2.0,
        pierce_ratio=0.1,
        max_health=1000.0
    )
    player = Entity(id="player_1", base_stats=player_base_stats, rarity="Rare")

    # Create enemy
    enemy_base_stats = EntityStats(
        max_health=1500.0,
        armor=50.0
    )
    enemy = Entity(id="enemy_1", base_stats=enemy_base_stats)

    # Register entities
    state_manager.register_entity(player)
    state_manager.register_entity(enemy)

    # Create equipment
    vicious_axe = Item(
        id="axe_01",
        name="Vicious Axe",
        slot="Weapon",
        affixes=[
            Affix(stat="base_damage", mod_type="flat", value=20.0),
            Affix(stat="crit_chance", mod_type="flat", value=0.15),
            Affix(stat="pierce_ratio", mod_type="multiplier", value=1.5)
        ]
    )

    enchanted_helm = Item(
        id="helm_01",
        name="Enchanted Helm",
        slot="Head",
        affixes=[
            Affix(stat="max_health", mod_type="flat", value=200.0),
            Affix(stat="armor", mod_type="multiplier", value=1.25)
        ]
    )

    # Create skill
    multi_slash = Skill(
        id="skill_01",
        name="Multi-Slash",
        hits=3,
        triggers=[
            Trigger(
                event="OnHit",
                check={"proc_rate": 0.4},
                result={"apply_debuff": "Poison", "stacks": 1}
            )
        ]
    )

    # Show initial stats
    print("--- Initial Player Stats ---")
    print(f"Base Damage: {player.base_stats.base_damage}")
    print(f"Crit Chance: {player.base_stats.crit_chance}")
    print(f"Max Health: {player.base_stats.max_health}")
    print(f"Armor: {player.base_stats.armor}")
    print(f"Pierce Ratio: {player.base_stats.pierce_ratio}")
    print()

    # Equip items
    print("--- Equipping Items ---")
    player.equip_item(vicious_axe)
    print(f"Equipped: {vicious_axe.name}")

    player.equip_item(enchanted_helm)
    print(f"Equipped: {enchanted_helm.name}")
    print()

    # Show final stats after equipment
    print("--- Player Stats After Equipment ---")
    print(f"Final Damage: {player.final_stats.base_damage}")
    print(f"Final Crit Chance: {player.final_stats.crit_chance}")
    print(f"Final Max Health: {player.final_stats.max_health}")
    print(f"Final Armor: {player.final_stats.armor}")
    print(f"Final Pierce Ratio: {player.final_stats.pierce_ratio}")
    print()

    # Use skill
    print(f"--- {player.name} uses {multi_slash.name} on {enemy.name} ---")
    CombatEngine.process_skill_use(player, enemy, multi_slash, event_bus, state_manager)

    # Show results
    print()
    print("--- Final Results ---")
    enemy_state = state_manager.get_state(enemy.id)
    if enemy_state:
        print(f"Enemy Health: {enemy_state.current_health:.1f} / {enemy.final_stats.max_health}")
        if enemy_state.active_debuffs:
            print("Active Debuffs:")
            for debuff_name, debuff in enemy_state.active_debuffs.items():
                print(f"  - {debuff_name}: {debuff.stacks} stacks, {debuff.time_remaining:.1f}s remaining")
        else:
            print("No debuffs applied.")

    print("\n=== Phase 3 Test Complete ===")


if __name__ == "__main__":
    main()
