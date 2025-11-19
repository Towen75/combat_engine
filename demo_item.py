#!/usr/bin/env python3
"""Demo script to generate and display a random procedural item."""

import json
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

from src.item_generator import ItemGenerator


def main():
    """Generate and display a random item."""
    try:
        # Load game data
        with open('data/game_data.json', 'r', encoding='utf-8') as f:
            game_data = json.load(f)

        # Initialize generator
        item_gen = ItemGenerator(game_data)

        # Get available base items
        base_items = list(game_data['items'].keys())

        # Pick a random base item
        base_id = random.choice(base_items)

        # Generate the item
        item = item_gen.generate(base_id)

        # Print item details
        print("=" * 50)
        print(f"🎲 RANDOM ITEM GENERATED 🎲")
        print("=" * 50)
        print(f"Name: {item.name}")
        print(f"Rarity: {item.rarity}")
        print(f"Quality: {item.quality_tier}")
        print(f"Quality Roll: {item.quality_roll}")
        print(f"Slot: {item.slot}")
        print(f"Instance ID: {item.instance_id}")
        print(f"Base ID: {item.base_id}")
        print()
        print("Affixes:")
        for i, affix in enumerate(item.affixes, 1):
            # Format percentage values for display (stats that are multipliers shown as %)
            display_value = affix.value
            percentage_stats = {'crit_damage', 'resistances', 'pierce_ratio', 'crit_chance'}
            if affix.stat_affected in percentage_stats and '%' in affix.description:
                display_value = affix.value * 100  # 0.315 → 31.5

            description = affix.description.replace('{value}', str(display_value))
            print(f"  {i}. {description}")
            print(f"     (Base: {affix.base_value}, Rolled: {affix.value}, Type: {affix.mod_type})")
        print("=" * 50)
        print(f"Total affixes: {len(item.affixes)}")

    except FileNotFoundError:
        print("Error: data/game_data.json not found. Run src/data_parser.py first.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
