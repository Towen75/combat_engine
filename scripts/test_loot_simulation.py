#!/usr/bin/env python3
"""Test script for Phase C3 Loot Simulation Integration.

Demonstrates that combat simulations now trigger loot drops.
"""

from src.data.game_data_provider import GameDataProvider
from src.utils.item_generator import ItemGenerator
from src.core.models import Entity, EntityStats
from src.core.rng import RNG
from src.core.events import EventBus
from src.core.state import StateManager
from src.core.loot_manager import LootManager
from src.simulation.combat_simulation import SimulationRunner, CombatLogger

def main():
    print("🚀 Phase C3 Loot Simulation Integration Test")
    print("=" * 50)

    # Setup components
    provider = GameDataProvider()
    rng = RNG(seed=42)  # Deterministic for testing

    # Create simulation components
    event_bus = EventBus()
    state_manager = StateManager(event_bus)
    logger = CombatLogger()

    # Create item generator
    item_generator = ItemGenerator(provider=provider, rng=rng)

    # Create loot manager
    loot_manager = LootManager(provider, item_generator, rng)

    # Create simulation runner with loot support
    # Note: In real usage, you'd also pass combat_engine but we're just testing loot here
    runner = SimulationRunner(
        combat_engine=None,  # Not using combat for this demo
        state_manager=state_manager,
        event_bus=event_bus,
        rng=rng,
        logger=logger,
        loot_manager=loot_manager
    )

    print("✅ Simulation Runner created with LootManager")

    # Create test entities with loot tables
    # Use the factory we created
    from src.core.factory import EntityFactory
    factory = EntityFactory()

    # Create warrior (will attack)
    warrior = factory.create(
        "warrior",
        EntityStats(base_damage=30, max_health=120),
        loot_table_id="goblin_loot"  # Should drop item on death
    )

    # Create goblin (won't attack, will die from state manipulation)
    goblin = factory.create(
        "goblin",
        EntityStats(base_damage=10, max_health=40),
        loot_table_id="goblin_loot"
    )

    # Register entities
    state_manager.add_entity(warrior)
    state_manager.add_entity(goblin)

    print(f"✅ Created entities: {warrior.name} ({warrior.loot_table_id}) and {goblin.name} ({goblin.loot_table_id})")

    # Simulate combat by damaging the goblin through state manager (this properly triggers death)
    print(f"💀 Damaging {goblin.name} lethally...")

    # Apply enough damage to kill (proper way - triggers death event automatically)
    damage_applied = state_manager.apply_damage(goblin.id, 100.0)  # More than 40 health
    print(f"   Damage applied: {damage_applied}")
    print(f"   Goblin health now: {state_manager.get_current_health(goblin.id)}")
    print(f"   Goblin is alive: {state_manager.get_is_alive(goblin.id)}")

    print("🔍 Checking loot results...")

    # Get simulation report
    report = runner.get_simulation_report()

    loot_analysis = report.get("loot_analysis", {})
    total_drops = loot_analysis.get("total_drops", 0)
    total_items = loot_analysis.get("total_items", 0)

    print(f"📦 Loot Results:")
    print(f"   - Total drops: {total_drops}")
    print(f"   - Total items: {total_items}")
    print(f"   - Rarity breakdown: {loot_analysis.get('rarity_breakdown', {})}")

    if total_items > 0:
        print("\n🎉 SUCCESS: Loot simulation integration working!")
        print("   Combat deaths now trigger loot drops via LootHandler")

        # Show the logged loot events
        loot_events = [entry for entry in logger.entries if entry.event_type == "loot_drop"]
        print(f"\n📋 Loot Events Logged ({len(loot_events)}):")
        for i, entry in enumerate(loot_events):
            items = entry.metadata.get("items", [])
            print(f"   {i+1}. Source: {entry.attacker_id}")
            for item in items:
                print(f"      └─ {item['name']} ({item['rarity']})")
    else:
        print("❌ No loot generated - check entity loot table setup")

    print("\n🏁 Phase C3 Loot Simulation Integration Test Complete")


if __name__ == "__main__":
    main()
