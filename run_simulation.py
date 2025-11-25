#!/usr/bin/env python3
"""Simulation runner for combat engine testing and balancing.

This script runs automated combat simulations with predefined entities
and generates detailed reports for balance analysis.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(message)s')

from src.core.models import Entity, EntityStats
from src.core.state import StateManager
from src.core.events import EventBus
from src.core.rng import RNG
from src.combat import CombatEngine
from src.handlers.effect_handlers import BleedHandler, PoisonHandler
from src.simulation.combat_simulation import SimulationRunner, ReportGenerator
from src.utils.item_generator import ItemGenerator
from src.data.game_data_provider import GameDataProvider
from src.core.factory import EntityFactory  # Add import for Phase B2


def create_sample_entities(factory: EntityFactory) -> list[Entity]:
    """Create entities using the Data-Driven Factory from Phase B2.

    Note: These IDs must exist in your entities.csv from Phase B1
    If they don't match your CSV, update these strings or add corresponding
    entries to data/entities.csv

    Args:
        factory: EntityFactory for creating data-driven entities

    Returns:
        List of data-driven sample entities
    """
    try:
        return [
            factory.create("goblin_grunt"),
            factory.create("orc_warrior"),
            # factory.create("hero_paladin") # Uncomment if added to CSV
        ]
    except ValueError as e:
        logger.warning(f"Could not create sample entities: {e}. Is data/entities.csv populated?")
        return []


def setup_simulation(rng: RNG):
    """Set up the simulation with all necessary components.

    Args:
        rng: Seeded RNG instance for deterministic simulation

    Returns:
        Tuple of (SimulationRunner instance, EntityFactory instance)
    """
    # Initialize core systems
    state_manager = StateManager()
    event_bus = EventBus()
    combat_engine = CombatEngine(rng=rng)

    # Set up effect handlers
    bleed_handler = BleedHandler(event_bus, state_manager, proc_rate=0.4, rng=rng)
    poison_handler = PoisonHandler(event_bus, state_manager, proc_rate=0.25, rng=rng)

    # Initialize data provider (for Phase B2 EntityFactory)
    provider = GameDataProvider()
    provider.initialize()  # Load all CSV data
    item_gen = ItemGenerator(provider=provider, rng=rng)
    entity_factory = EntityFactory(provider, item_gen, rng)

    # Create simulation runner
    runner = SimulationRunner(combat_engine, state_manager, event_bus, rng)

    return runner, entity_factory


def run_combat_simulation(seed: int = 42, duration: float = 30.0) -> dict:
    """Run a complete combat simulation.

    Args:
        seed: Random seed for reproducible results
        duration: Simulation duration in seconds

    Returns:
        Dictionary containing simulation results and reports
    """
    # Create deterministic RNG for reproducible results
    rng = RNG(seed)

    logger.info(f"Starting combat simulation (seed: {seed}, duration: {duration}s)")

    # Set up simulation
    runner, factory = setup_simulation(rng)

    # Create and add entities
    entities = create_sample_entities(factory)
    for entity in entities:
        runner.add_entity(entity)
        logger.info(f"Added entity: {entity.name} ({entity.id}) - {entity.final_stats}")

    # Run simulation
    logger.info("Running simulation...")
    runner.run_simulation(duration)

    # Generate reports
    logger.info("Generating reports...")
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
    logger.info("\n" + "="*60)
    logger.info("COMBAT SIMULATION SUMMARY")
    logger.info("="*60)

    metadata = report.get("metadata", {})
    logger.info(f"Seed: {metadata.get('seed', 'N/A')}")
    logger.info(f"Duration: {metadata.get('duration', 0):.1f} seconds")
    logger.info(f"Entities: {metadata.get('entity_count', 0)}")

    # Performance summary
    perf = report.get("performance_analysis", {})
    logger.info("\nPerformance:")
    logger.info(f"  Duration: {perf.get('simulation_duration', 0):.2f}s")
    logger.info(f"  Events/second: {perf.get('events_per_second', 0):.1f}")
    logger.info(f"  Rating: {perf.get('performance_rating', 'Unknown')}")

    # Damage summary
    damage = report.get("damage_analysis", {})
    summary = damage.get("summary", {})
    logger.info("\nDamage Summary:")
    logger.info(f"  Total damage: {summary.get('total_damage', 0):.1f}")
    logger.info(f"  Total hits: {summary.get('total_hits', 0)}")
    logger.info(f"  Critical hits: {summary.get('total_crits', 0)}")
    logger.info(f"  Overall crit rate: {summary.get('overall_crit_rate', 0):.1%}")
    logger.info(f"  Avg damage per hit: {summary.get('avg_damage_per_hit', 0):.1f}")

    # Entity breakdown
    entity_breakdown = damage.get("entity_breakdown", {})
    logger.info("\nEntity Performance:")
    for entity_id, stats in entity_breakdown.items():
        logger.info(f"  {entity_id}:")
        logger.info(f"    Damage: {stats.get('total_damage', 0):.1f} ({stats.get('damage_percentage', 0):.1f}%)")
        logger.info(f"    Hits: {stats.get('hits', 0)}, Crits: {stats.get('crits', 0)}")
        logger.info(f"    Crit rate: {stats.get('crit_rate', 0):.1%}")

    # Effect summary
    effect = report.get("effect_analysis", {})
    effect_summary = effect.get("summary", {})
    logger.info("\nEffect Summary:")
    logger.info(f"  Total applications: {effect_summary.get('total_applications', 0)}")
    logger.info(f"  Total DoT ticks: {effect_summary.get('total_ticks', 0)}")
    logger.info(f"  Total DoT damage: {effect_summary.get('total_dot_damage', 0):.1f}")

    # Balance insights
    insights = report.get("balance_insights", {})
    recommendations = insights.get("recommendations", [])
    logger.info("\nBalance Recommendations:")
    for rec in recommendations:
        logger.info(f"  • {rec}")

    logger.info("="*60)


def save_report_to_file(report: dict, filename: str = "simulation_report.json") -> None:
    """Save the simulation report to a JSON file.

    Args:
        filename: Output filename
    """
    try:
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Report saved to {filename}")
    except Exception as e:
        logger.error(f"Error saving report: {e}")


def main():
    """Main entry point for the simulation script."""
    import argparse

    parser = argparse.ArgumentParser(description="Run combat engine simulations")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible results")
    parser.add_argument("--duration", type=float, default=30.0, help="Simulation duration in seconds")
    parser.add_argument("--output", type=str, default="simulation_report.json", help="Output report filename")
    parser.add_argument("--quiet", action="store_true", help="Only show warnings and errors")
    parser.add_argument("--verbose", action="store_true", help="Show debug output")

    args = parser.parse_args()

    # Configure log level based on arguments
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    # Run simulation
    report = run_combat_simulation(seed=args.seed, duration=args.duration)

    # Print summary
    if not args.quiet:
        print_simulation_summary(report)

    # Save report
    save_report_to_file(report, args.output)

    # Item generation demo using provider
    logger.info("\n--- Item Generation Demo ---")
    try:
        # Load data once at startup
        provider = GameDataProvider()
        item_rng = RNG(args.seed + 1000)  # Different seed for items
        item_gen = ItemGenerator(provider=provider, rng=item_rng)

        # Generate a few random items
        for base_id in ['base_iron_axe', 'base_gold_ring', 'base_leather_chest']:
            item = item_gen.generate(base_id)
            logger.info(f"Generated: {item.name} (Quality: {item.quality_tier}, Rarity: {item.rarity})")
            for affix in item.affixes:
                logger.info(f"  - {affix.description.replace('{value}', str(affix.value))}")

    except Exception as e:
        logger.error(f"Item generation demo failed: {e}")

    logger.info(f"\nSimulation complete! Report saved to {args.output}")


if __name__ == "__main__":
    main()
