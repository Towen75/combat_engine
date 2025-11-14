import csv
import json
import os

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
    print("Data parsed and game_data.json created successfully.")
