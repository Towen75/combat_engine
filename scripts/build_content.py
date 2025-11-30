import yaml
import csv
import os
import argparse
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
BLUEPRINT_DIR = BASE_DIR / "blueprints"
DATA_DIR = BASE_DIR / "data"

def load_yaml(filename):
    with open(BLUEPRINT_DIR / filename, 'r') as f:
        return yaml.safe_load(f)

def validate_content():
    """Attempt to load all data via GameDataProvider to ensure integrity."""
    print("🔍 Validating Generated Content...")
    try:
        import sys
        # Add the src root to path to import engine modules
        sys.path.append(str(BASE_DIR))

        from src.data.game_data_provider import GameDataProvider

        # Force a reload/fresh load
        provider = GameDataProvider(data_dir=str(DATA_DIR))
        # If the singleton was already initialized in memory, force re-init logic isn't exposed easily
        # but instantiating it triggers _load_and_validate_data if not initialized.
        # Better: rely on the fact that this script runs in a fresh process usually.

        print(f"   ✅ Data Load Successful!")
        print(f"      - Items: {len(provider.items)}")
        print(f"      - Affixes: {len(provider.affixes)}")
        print(f"      - Entities: {len(provider.entities)}")
        print(f"      - Loot Tables: {len(provider.loot_tables)}")
        return True
    except Exception as e:
        print(f"   ❌ Validation Failed: {e}")
        return False

def main(generate_affixes_only=False, run_validation=False):
    print("🔨 Starting Content Build...")

    # 1. Load Blueprints
    scaling = load_yaml("scaling.yaml")
    affix_defs = load_yaml("affixes.yaml")["definitions"]

    rarities = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
    curve = scaling["rarity_curve"]
    slots = scaling["random_affix_slots"]

    # 2. Generate Affixes (affixes.csv)
    print(f"   - Generating Affixes from {len(affix_defs)} definitions...")

    affix_rows = []
    # Headers based on your strict schema
    affix_headers = [
        "affix_id", "stat_affected", "mod_type",  "affix_pools",
        "base_value","description", "trigger_event", "proc_rate",
        "trigger_result", "trigger_duration", "stacks_max",
        "dual_stat", "scaling_power", "complex_effect"
    ]

    generated_affix_ids = set() # Track for item linking

    for definition in affix_defs:
        base_id = definition["id"]
        base_val = definition["base_val"]

        for rarity in rarities:
            multiplier = curve[rarity]
            final_val = base_val * multiplier

            # Generate ID: flat_dmg_common
            new_id = f"{base_id}_{rarity.lower()}"
            generated_affix_ids.add(new_id)

            # Description formatting
            desc = f"+{{value}} {definition['name']} ({rarity})"

            row = {
                "affix_id": new_id,
                "stat_affected": definition["stat"],
                "mod_type": definition["type"],
                "affix_pools": "|".join(definition.get("pools", [])),
                "base_value": final_val,
                "description": desc,
                # Defaults for optional fields
                "trigger_event": "", "proc_rate": "", "trigger_result": "",
                "trigger_duration": "", "stacks_max": "", "dual_stat": "",
                "scaling_power": "", "complex_effect": ""
            }
            affix_rows.append(row)

    # Write affixes.csv and affix_pools.csv
    with open(DATA_DIR / "affixes.csv", 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=affix_headers)
        writer.writeheader()
        writer.writerows(affix_rows)

    # 2.5 Generate Affix Pools (affix_pools.csv)
    print(f"   - Generating Affix Pools from {len(affix_rows)} affixes...")

    # Tier and Weight configuration (from PR)
    rarity_tier_defaults = {"Common": [1], "Uncommon": [1], "Rare": [1, 2], "Epic": [1, 2, 3], "Legendary": [1, 2, 3, 4]}
    rarity_weight_base = {"Common": 100, "Uncommon": 60, "Rare": 30, "Epic": 15, "Legendary": 6}

    affix_pool_rows = []

    for row in affix_rows:
        affix_id = row['affix_id']

        # Extract rarity from ID suffix (e.g., "flat_dmg_common" -> "Common")
        id_parts = affix_id.split('_')
        if len(id_parts) >= 2:
            rarity_suffix = id_parts[-1].title()  # "common" -> "Common"
            if rarity_suffix in rarity_tier_defaults:
                rarity = rarity_suffix
            else:
                continue  # Skip invalid rarities
        else:
            continue  # Skip malformed IDs

        pools_field = row.get("affix_pools") or ""
        pools = [p.strip() for p in pools_field.split("|") if p.strip()]

        possible_tiers = rarity_tier_defaults.get(rarity, [1])
        chosen_tier = possible_tiers[-1]  # Default to highest tier for that rarity

        base_weight = rarity_weight_base.get(rarity, 10)

        try:
            val = float(row.get('base_value') or 1.0)
            weight = max(1, int(base_weight / (1 + (val / max(1.0, base_weight/2)))))
        except (ValueError, TypeError):
            weight = max(1, int(base_weight))

        for pool in pools:
            affix_pool_rows.append({
                "pool_id": pool,
                "rarity": rarity,
                "tier": chosen_tier,
                "affix_id": affix_id,
                "weight": weight
            })

    # Write affix_pools.csv
    affix_pools_headers = ["pool_id", "rarity", "tier", "affix_id", "weight"]
    with open(DATA_DIR / "affix_pools.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=affix_pools_headers)
        writer.writeheader()
        writer.writerows(affix_pool_rows)

    print(f"   - Generated {len(affix_pool_rows)} affix pool entries.")

    if generate_affixes_only:
        print(f"✅ Partial Build Complete: {len(affix_rows)} affixes generated.")
        return

    # 3. Generate Items (Only runs if generate_affixes_only is False)
    families = load_yaml("families.yaml")["families"]
    print(f"   - Generating Items from {len(families)} families...")

    item_rows = []
    item_headers = [
        "item_id", "name", "slot", "rarity",
        "affix_pools", "implicit_affixes", "num_random_affixes",
        "default_attack_skill" # <--- NEW HEADER
    ]

    for fam in families:
        base_id = fam["id"]
        implicits = fam.get("implicits", [])
        default_skill = fam.get("default_attack_skill", "") # <--- READ FROM BLUEPRINT

        for rarity in rarities:
            # item_id: longsword_rare
            item_id = f"{base_id}_{rarity.lower()}"

            # Resolve Implicit Affixes
            item_implicits = []

            if rarity == "Legendary":
                # Special Rule: Legendary gets 2 implicits at EPIC strength
                # Primary Implicit (Epic version)
                if len(implicits) > 0:
                    item_implicits.append(f"{implicits[0]}_epic")
                # Secondary Implicit (Epic version)
                if len(implicits) > 1:
                    item_implicits.append(f"{implicits[1]}_epic")
            else:
                # Normal Rule: 1 implicit matching current rarity
                if len(implicits) > 0:
                    item_implicits.append(f"{implicits[0]}_{rarity.lower()}")

            row = {
                "item_id": item_id,
                "name": f"{rarity} {fam['name']}",
                "slot": fam["slot"],
                "rarity": rarity,
                "affix_pools": fam["affix_pools"],
                "implicit_affixes": "|".join(item_implicits),
                "num_random_affixes": slots[rarity],
                "default_attack_skill": default_skill # <--- WRITE TO ROW
            }
            item_rows.append(row)

    # Write items.csv
    with open(DATA_DIR / "items.csv", 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=item_headers)
        writer.writeheader()
        writer.writerows(item_rows)

    print(f"✅ Build Complete.")
    print(f"   Generated {len(affix_rows)} affixes.")
    print(f"   Generated {len(item_rows)} items.")

    if run_validation:
        success = validate_content()
        if not success:
            import sys
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Build game content from blueprints')
    parser.add_argument('--generate-affixes', action='store_true', help='Generate affixes CSV only')
    parser.add_argument('--validate', action='store_true', help='Run data validation after generation') # New Flag
    args = parser.parse_args()

    main(generate_affixes_only=args.generate_affixes, run_validation=args.validate)
