import csv
import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Union
from .schemas import get_schema_validator

logger = logging.getLogger(__name__)


def parse_csv(filepath: str, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse CSV with schema validation.

    Args:
        filepath: Path to CSV file
        schema: Dict specifying required columns and validators

    Returns:
        List of validated row dictionaries

    Raises:
        ValueError: If validation fails
        FileNotFoundError: If file doesn't exist
    """
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Validate columns
        missing = [c for c in schema["required"] if c not in reader.fieldnames]
        if missing:
            raise ValueError(
                f"CSV Schema Error in {filepath}: Missing required columns: {missing}"
            )

        rows = []
        for i, row in enumerate(reader, start=2):  # header is line 1
            validated = {}
            for col, validator in schema["columns"].items():
                raw_value = row.get(col, "")
                try:
                    validated[col] = validator(raw_value)
                except Exception as e:
                    raise ValueError(
                        f"CSV Parse Error in {filepath} at line {i}: "
                        f"Column '{col}', value '{raw_value}': {e}"
                    )
            rows.append(validated)
        return rows


def parse_all_csvs(base_path: Union[str, Path] = "data") -> Dict[str, Any]:
    """Parse all CSV files in the data directory using schema validation.

    Args:
        base_path: Path to the data directory (string or Path object)

    Returns:
        Dictionary with all parsed CSV data organized by type
    """
    # Convert to Path object and resolve to absolute path
    data_dir = Path(base_path)
    if not data_dir.is_absolute():
        # If relative, resolve relative to project root (not this file)
        project_root = Path(__file__).resolve().parent.parent.parent
        data_dir = project_root / data_dir

    csv_files = [
        ("affixes.csv", "affixes"),
        ("affix_pools.csv", "affix_pools"),  # NEW: optional affix pools data
        ("items.csv", "items"),
        ("quality_tiers.csv", "quality_tiers"),
        ("effects.csv", "effects"),
        ("skills.csv", "skills"),
        ("loot_tables.csv", "loot_tables")  # NEW: loot tables data
    ]

    game_data = {
        "affixes": {},
        "affix_pools": {},  # NEW: nested structure {pool_id: {rarity: {tier: [{affix_id, weight}]}}}
        "items": {},
        "quality_tiers": [],
        "effects": {},
        "skills": {},
        "loot_tables": []  # NEW: list of loot table entries
    }

    for filename, data_key in csv_files:
        filepath = data_dir / filename
        filepath_str = str(filepath)
        if not os.path.exists(filepath_str):
            logger.warning(f"CSV file not found: {filepath_str}, skipping")
            continue

        try:
            schema = get_schema_validator(filepath_str)
            rows = parse_csv(filepath_str, schema)

            if data_key == "quality_tiers":
                # Special validation for quality tiers: min_range < max_range
                game_data[data_key] = rows
                for row in rows:
                    if row["min_range"] >= row["max_range"]:
                        raise ValueError(
                            f"Quality tier validation error in {filename}: "
                            f"min_range ({row['min_range']}) must be < max_range ({row['max_range']})"
                        )
            elif data_key in ["affixes", "items", "effects", "skills"]:
                # These are keyed by ID
                id_key = list(schema["required"])[0]  # First required column is usually the ID
                for row in rows:
                    game_data[data_key][row[id_key]] = row
            elif data_key == "affix_pools":
                # NEW: Special nested structure for affix pools
                pools = {}
                for row in rows:
                    pool = row['pool_id']
                    rarity = row['rarity']
                    tier = row['tier']
                    affixes = {
                        "affix_id": row['affix_id'],
                        "weight": row['weight']
                    }
                    pools.setdefault(pool, {}).setdefault(rarity, {}).setdefault(tier, []).append(affixes)
                game_data[data_key] = pools
            else:
                # quality_tiers is a list
                game_data[data_key] = rows

            logger.info(f"Successfully parsed {filename} ({len(rows)} rows)")

        except Exception as e:
            logger.error(f"Failed to parse {filename}: {e}")
            raise

    # Cross-validation: Ensure affix IDs in affix_pools exist in affixes
    if game_data.get('affix_pools'):
        missing_affixes = []
        for pool_id, rarities in game_data['affix_pools'].items():
            for rarity, tiers in rarities.items():
                for tier, entries in tiers.items():
                    for entry in entries:
                        affix_id = entry['affix_id']
                        if affix_id not in game_data['affixes']:
                            missing_affixes.append((pool_id, rarity, tier, affix_id))

        if missing_affixes:
            raise ValueError(f"affix_pools.csv references unknown affix IDs: {missing_affixes}")

    return game_data


def parse_csv_data():
    """
    Parses the CSV files into a structured game_data dictionary and saves as JSON.
    """
    data_dir = "data"
    
    # Initialize empty structures
    game_data = {
        "affixes": {},
        "items": {},
        "quality_tiers": []
    }
    
    # Parse affixes.csv
    affixes_path = os.path.join(data_dir, "affixes.csv")
    with open(affixes_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            affix_id = row['affix_id']
            game_data["affixes"][affix_id] = {
                "affix_id": affix_id,
                "stat_affected": row["stat_affected"],
                "mod_type": row["mod_type"],
                "affix_pools": row["affix_pools"].split('|') if row["affix_pools"] else [],
                "base_value": float(row["base_value"]),
                "description": row["description"]
            }
    
    # Parse items.csv
    items_path = os.path.join(data_dir, "items.csv")
    with open(items_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            item_id = row['item_id']
            game_data["items"][item_id] = {
                "item_id": item_id,
                "name": row["name"],
                "slot": row["slot"],
                "rarity": row["rarity"],
                "affix_pools": row["affix_pools"].split('|') if row["affix_pools"] else [],
                "implicit_affixes": row["implicit_affixes"].split('|') if row["implicit_affixes"] else [],
                "num_random_affixes": int(row["num_random_affixes"])
            }
    
    # Parse quality_tiers.csv
    tiers_path = os.path.join(data_dir, "quality_tiers.csv")
    with open(tiers_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            game_data["quality_tiers"].append({
                "quality_id": int(row["quality_id"]),
                "tier_name": row["tier_name"],
                "min_range": int(row["min_range"]),
                "max_range": int(row["max_range"]),
                "Normal": int(row["Normal"]) if row["Normal"] else 0,
                "Common": int(row["Common"]) if row["Common"] else 0,
                "Unusual": int(row["Unusual"]) if row["Unusual"] else 0,
                "Uncommon": int(row["Uncommon"]) if row["Uncommon"] else 0,
                "Rare": int(row["Rare"]) if row["Rare"] else 0,
                "Exotic": int(row["Exotic"]) if row["Exotic"] else 0,
                "Epic": int(row["Epic"]) if row["Epic"] else 0,
                "Glorious": int(row["Glorious"]) if row["Glorious"] else 0,
                "Exalted": int(row["Exalted"]) if row["Exalted"] else 0,
                "Legendary": int(row["Legendary"]) if row["Legendary"] else 0,
                "Mythic": int(row["Mythic"]) if row["Mythic"] else 0,
                "Godly": int(row["Godly"]) if row["Godly"] else 0
            })
    
    # Save to JSON
    output_path = os.path.join(data_dir, "game_data.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(game_data, f, indent=2)
    
    return game_data


if __name__ == "__main__":
    parse_csv_data()
    logger.info("Data parsed and game_data.json created successfully.")
