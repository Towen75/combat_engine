#!/usr/bin/env python3
"""Simulation runner for combat engine testing and balancing.

This script runs automated combat simulations with predefined entities
and generates detailed reports for balance analysis.
"""

import random
import json
from src.models import Entity, EntityStats
from src.state import StateManager
from src.events import EventBus
from src.engine import CombatEngine
from src.effect_handlers import BleedHandler, PoisonHandler
from src.simulation import SimulationRunner, ReportGenerator
from src.item_generator import ItemGenerator


def create_sample_entities() -> list[Entity]:
    """Create sample entities for simulation testing.

    Returns:
        List of sample entities with different stats
    """
    # Warrior - High damage, low speed, tanky
    warrior_stats = EntityStats(
        base_damage=25.0,
        attack_speed=0.8,  # attacks per second
        crit_chance=0.1,
        crit_damage=1.8,
        pierce_ratio=0.05,
        max_health=150.0,
        armor=15.0,
        resistances=0.0
    )
    warrior = Entity("warrior", warrior_stats, "Warrior", "Rare")

    # Assassin - High speed, moderate damage, low health
    assassin_stats = EntityStats(
        base_damage=18.0,
        attack_speed=1.5,  # attacks per second
        crit_chance=0.25,
        crit_damage=2.0,
        pierce_ratio=0.1,
        max_health=80.0,
        armor=5.0,
        resistances=0.0
    )
    assassin = Entity("assassin", assassin_stats, "Assassin", "Epic")

    # Mage - Moderate damage, low speed, squishy
    mage_stats = EntityStats(
        base_damage=30.0,
        attack_speed=0.6,  # attacks per second
        crit_chance=0.15,
        crit_damage=1.5,
        pierce_ratio=0.02,
        max_health=70.0,
        armor=0.0,
        resistances=0.2
    )
    mage = Entity("mage", mage_stats, "Mage", "Legendary")

    # Tank - Low damage, very tanky, slow
    tank_stats = EntityStats(
        base_damage=12.0,
        attack_speed=0.5,  # attacks per second
        crit_chance=0.05,
        crit_damage=1.3,
        pierce_ratio=0.01,
        max_health=200.0,
        armor=25.0,
        resistances=0.1
    )
    tank = Entity("tank", tank_stats, "Tank", "Uncommon")

    return [warrior, assassin, mage, tank]


def setup_simulation() -> SimulationRunner:
    """Set up the simulation with all necessary components.

    Returns:
        Configured SimulationRunner instance
    """
    # Initialize core systems
    state_manager = StateManager()
    event_bus = EventBus()
    combat_engine = CombatEngine()

    # Set up effect handlers
    bleed_handler = BleedHandler(event_bus, state_manager, proc_rate=0.4)
    poison_handler = PoisonHandler(event_bus, state_manager, proc_rate=0.25)

    # Create simulation runner
    runner = SimulationRunner(combat_engine, state_manager, event_bus)

    return runner


def run_combat_simulation(seed: int = 42, duration: float = 30.0) -> dict:
    """Run a complete combat simulation.

    Args:
        seed: Random seed for reproducible results
        duration: Simulation duration in seconds

    Returns:
        Dictionary containing simulation results and reports
    """
    # Set random seed for reproducible results
    random.seed(seed)

    print(f"Starting combat simulation (seed: {seed}, duration: {duration}s)")

    # Set up simulation
    runner = setup_simulation()

    # Create and add entities
    entities = create_sample_entities()
    for entity in entities:
        runner.add_entity(entity)
        print(f"Added entity: {entity.name} ({entity.id}) - {entity.final_stats}")

    # Run simulation
    print("Running simulation...")
    runner.run_simulation(duration)

    # Generate reports
    print("Generating reports...")
    report_generator = ReportGenerator(runner.logger)
    full_report = report_generator.generate_full_report()

    # Add simulation metadata
    full_report["metadata"] = {
        "seed": seed,
        "duration": duration,
        "entity_count": len(entities),
        "entities": [
            {
                "id": e.id,
                "name": e.name,
                "rarity": e.rarity,
                "stats": {
                    "damage": e.final_stats.base_damage,
                    "attack_speed": e.final_stats.attack_speed,
                    "health": e.final_stats.max_health,
                    "armor": e.final_stats.armor
                }
            }
            for e in entities
        ]
    }

    return full_report


def print_simulation_summary(report: dict) -> None:
    """Print a human-readable summary of the simulation results.

    Args:
        report: The full simulation report
    """
    print("\n" + "="*60)
    print("COMBAT SIMULATION SUMMARY")
    print("="*60)

    metadata = report.get("metadata", {})
    print(f"Seed: {metadata.get('seed', 'N/A')}")
    print(f"Duration: {metadata.get('duration', 0):.1f} seconds")
    print(f"Entities: {metadata.get('entity_count', 0)}")

    # Performance summary
    perf = report.get("performance_analysis", {})
    print("\nPerformance:")
    print(f"  Duration: {perf.get('simulation_duration', 0):.2f}s")
    print(f"  Events/second: {perf.get('events_per_second', 0):.1f}")
    print(f"  Rating: {perf.get('performance_rating', 'Unknown')}")

    # Damage summary
    damage = report.get("damage_analysis", {})
    summary = damage.get("summary", {})
    print("\nDamage Summary:")
    print(f"  Total damage: {summary.get('total_damage', 0):.1f}")
    print(f"  Total hits: {summary.get('total_hits', 0)}")
    print(f"  Critical hits: {summary.get('total_crits', 0)}")
    print(f"  Overall crit rate: {summary.get('overall_crit_rate', 0):.1%}")
    print(f"  Avg damage per hit: {summary.get('avg_damage_per_hit', 0):.1f}")

    # Entity breakdown
    entity_breakdown = damage.get("entity_breakdown", {})
    print("\nEntity Performance:")
    for entity_id, stats in entity_breakdown.items():
        print(f"  {entity_id}:")
        print(f"    Damage: {stats.get('total_damage', 0):.1f} ({stats.get('damage_percentage', 0):.1f}%)")
        print(f"    Hits: {stats.get('hits', 0)}, Crits: {stats.get('crits', 0)}")
        print(f"    Crit rate: {stats.get('crit_rate', 0):.1%}")

    # Effect summary
    effect = report.get("effect_analysis", {})
    effect_summary = effect.get("summary", {})
    print("\nEffect Summary:")
    print(f"  Total applications: {effect_summary.get('total_applications', 0)}")
    print(f"  Total DoT ticks: {effect_summary.get('total_ticks', 0)}")
    print(f"  Total DoT damage: {effect_summary.get('total_dot_damage', 0):.1f}")

    # Balance insights
    insights = report.get("balance_insights", {})
    recommendations = insights.get("recommendations", [])
    print("\nBalance Recommendations:")
    for rec in recommendations:
        print(f"  • {rec}")

    print("="*60)


def save_report_to_file(report: dict, filename: str = "simulation_report.json") -> None:
    """Save the simulation report to a JSON file.

    Args:
        filename: Output filename
    """
    try:
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"Report saved to {filename}")
    except Exception as e:
        print(f"Error saving report: {e}")


def main():
    """Main entry point for the simulation script."""
    import argparse

    parser = argparse.ArgumentParser(description="Run combat engine simulations")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible results")
    parser.add_argument("--duration", type=float, default=30.0, help="Simulation duration in seconds")
    parser.add_argument("--output", type=str, default="simulation_report.json", help="Output report filename")
    parser.add_argument("--quiet", action="store_true", help="Suppress detailed output")

    args = parser.parse_args()

    # Run simulation
    report = run_combat_simulation(seed=args.seed, duration=args.duration)

    # Print summary
    if not args.quiet:
        print_simulation_summary(report)

    # Save report
    save_report_to_file(report, args.output)

    # Item generation demo
    print("\n--- Item Generation Demo ---")
    try:
        with open('data/game_data.json', 'r') as f:
            game_data = json.load(f)
        item_gen = ItemGenerator(game_data)

        # Generate a few random items
        for base_id in ['base_iron_axe', 'base_gold_ring', 'base_leather_chest']:
            item = item_gen.generate(base_id)
            print(f"Generated: {item.name} (Quality: {item.quality_tier}, Rarity: {item.rarity})")
            for affix in item.affixes:
                print(f"  - {affix.description.replace('{value}', str(affix.value))}")

    except Exception as e:
        print(f"Item generation demo failed: {e}")

    print(f"\nSimulation complete! Report saved to {args.output}")


if __name__ == "__main__":
    main()
