# Game Design & Implementation: Procedural Item Generator

**Version:** 1.0
**Date:** November 10, 2025

## 1.0 Overview

This document outlines the design and implementation plan for a procedural item generation service. The goal is to create a robust, data-driven system capable of generating randomized loot with variable stats, based on a set of predefined rules and templates. This system replaces a static item database, promoting replayability and creating an exciting loot-driven player experience.

The generation process is a two-step random roll:
1.  **Quality Tier Roll:** Based on the item's Rarity (e.g., Common, Rare, Legendary), a "Quality Tier" (e.g., Awful, Good, Perfect) is selected from a weighted table.
2.  **Quality Value Roll:** Within the selected Quality Tier, a specific percentage (e.g., 0-100) is rolled. This percentage acts as a master multiplier for all affixes on the item.

## 2.0 Data Schema Design

The system relies on a set of CSV (Comma-Separated Values) files that are easy to edit in any spreadsheet software. These files define the rules, templates, and pools for generation. A parser will convert these into a structured JSON file (`game_data.json`) for efficient use by the game engine.

### 2.1 `affixes.csv` - The Affix Definition File

This file defines every possible magical property an item can have.

**Columns:**

| Column Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `affix_id` | String | **Primary Key.** A unique, human-readable ID. | `flat_dmg` |
| `stat_affected` | String | The exact name of the stat this affix modifies. Must match the `EntityStats` model. | `base_damage` |
| `mod_type` | String | The type of modification: `flat` or `multiplier`. | `flat` |
| `affix_pools` | String | Pipe-delimited `|` list of pools this affix belongs to. | `weapon_pool|axe_pool` |
| `base_value` | Float | The 100% "Perfect" roll value for this affix. | `50` |
| `description` | String | A template for the item's tooltip. `{value}` will be replaced by the final rolled value. | `+{value} Base Damage` |

**Example `affixes.csv`:**
```csv
affix_id,stat_affected,mod_type,affix_pools,base_value,description
flat_dmg,base_damage,flat,weapon_pool|axe_pool,50,+{value} Base Damage
crit_dmg,crit_damage,flat,weapon_pool|jewelry_pool,0.50,+{value}% Crit Damage
bleed_chance,proc_rate_bleed,flat,axe_pool|sword_pool,0.25,{value}% chance to Bleed
flat_armor,armor,flat,armor_pool,150,+{value} Armor
```

### 2.2 `items.csv` - The Base Item Template File

This file defines the base templates for each item type, including which affix pools they draw from.

**Columns:**

| Column Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `item_id` | String | **Primary Key.** A unique ID for the base item. | `base_iron_axe` |
| `name` | String | The base display name of the item. | `Iron Axe` |
| `slot` | String | The equipment slot this item occupies (e.g., `Weapon`, `Chest`). | `Weapon` |
| `rarity` | String | The rarity of the item, used to determine the Quality Tier roll column. | `Rare` |
| `affix_pools` | String | Pipe-delimited `|` list of pools to draw random affixes from. | `weapon_pool|axe_pool` |
| `implicit_affixes` | String | Pipe-delimited `|` list of `affix_id`s that *always* appear on this item type. | `flat_dmg` |
| `num_random_affixes` | Integer | The number of *additional* random affixes to roll for this item. | `2` |

**Example `items.csv`:**
```csv
item_id,name,slot,rarity,affix_pools,implicit_affixes,num_random_affixes
base_iron_axe,Iron Axe,Weapon,Rare,weapon_pool|axe_pool,,2
base_gold_ring,Gold Ring,Ring,Legendary,jewelry_pool,crit_dmg,3```

### 2.3 `quality_tiers.csv` - The Quality Roll Definition File

This file is a direct representation of the provided spreadsheet and drives the two-step roll mechanism.

**Columns:**

| Column Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `quality_id` | Integer | **Primary Key.** A unique ID for the quality tier. | `7` |
| `tier_name` | String | The display name for this quality (e.g., Awful, Fine, Perfect). | `Fine` |
| `min_range` | Integer | The minimum percentage value for this tier's quality roll (inclusive). | `34` |
| `max_range` | Integer | The maximum percentage value for this tier's quality roll (inclusive). | `40` |
| `Common` | Integer | The weighted chance for a "Common" item to roll this tier. Empty means 0. | `35` |
| `Uncommon`...`Mythic` | Integer | Weighted chances for each subsequent rarity. | `30` |

**Example `quality_tiers.csv`:**
```csv
quality_id,tier_name,min_range,max_range,Normal,Common,Unusual,Uncommon,Rare,Exotic,Epic,Glorious,Exalted,Legendary,Mythic,Godly
1,Awful,0,5,35,15,5,,,
2,Dull,6,10,30,20,10,5,,
3,Mundane,11,15,40,30,20,10,5,
...
17,Perfect,99,100,,,,,5
```

## 3.0 Implementation Plan: The Item Generator Service

The generator will be a service class (`ItemGenerator`) that consumes the parsed data definitions and exposes a single public method: `generate()`.

### 3.1 Data Loading and Parsing

A prerequisite script will parse the three CSV files into a single, structured `game_data.json` file. This process "hydrates" the data, making it easy for the generator to access.

**Parser Responsibilities:**
*   Read `quality_tiers.csv` into a list of tier objects.
*   Read `affixes.csv` into a dictionary, keyed by `affix_id`.
*   Read `items.csv` into a dictionary, keyed by `item_id`.
*   Combine these into one JSON object.

### 3.2 `ItemGenerator` Service

This class will be initialized with the loaded `game_data`.

**Python Pseudocode:**

```python
import random
import uuid

class ItemGenerator:
    def __init__(self, game_data):
        self.affix_defs = game_data['affixes']
        self.item_templates = game_data['items']
        self.quality_tiers = game_data['quality_tiers']

    def generate(self, base_item_id: str):
        """Generates a fully rolled item instance from a base item ID."""
        template = self.item_templates[base_item_id]
        item_rarity = template['rarity']

        # --- Step 1 & 2: Perform the two-step quality roll ---
        quality_tier_obj = self._roll_quality_tier(item_rarity)
        quality_roll = random.randint(quality_tier_obj['min_range'], quality_tier_obj['max_range'])

        # --- Step 3: Initialize the item instance ---
        new_item = {
            "instance_id": str(uuid.uuid4()),
            "base_id": base_item_id,
            "name": template['name'],
            "rarity": item_rarity,
            "quality_tier": quality_tier_obj['tier_name'],
            "quality_roll": quality_roll,
            "affixes": []
        }

        # --- Step 4: Roll and append affixes ---
        all_affix_ids_to_roll = []
        
        # Add implicits
        implicits = template['implicit_affixes'].split('|') if template['implicit_affixes'] else []
        all_affix_ids_to_roll.extend(implicits)
        
        # Determine and add random explicits
        possible_random_affixes = self._get_affix_pool(template['affix_pools'])
        num_random = template['num_random_affixes']
        
        # Ensure we don't try to roll more affixes than exist in the pool or add duplicates
        possible_random_affixes = [aff for aff in possible_random_affixes if aff not in all_affix_ids_to_roll]
        num_to_roll = min(num_random, len(possible_random_affixes))
        
        if num_to_roll > 0:
            all_affix_ids_to_roll.extend(random.sample(possible_random_affixes, k=num_to_roll))
            
        # --- Step 5: Calculate final value for each affix ---
        for affix_id in all_affix_ids_to_roll:
            rolled_affix = self._roll_one_affix(affix_id, quality_roll)
            new_item['affixes'].append(rolled_affix)
            
        return new_item

    def _roll_quality_tier(self, rarity: str) -> dict:
        """Performs a weighted roll to select a quality tier based on item rarity."""
        rarity_column = rarity.capitalize()
        possible_tiers = [tier for tier in self.quality_tiers if tier[rarity_column]]
        weights = [float(tier[rarity_column]) for tier in possible_tiers]
        
        if not possible_tiers:
            return None # Or handle error appropriately

        return random.choices(possible_tiers, weights=weights, k=1)[0]

    def _get_affix_pool(self, pools_str: str) -> list:
        """Gathers all affix IDs that belong to the specified pools."""
        target_pools = set(pools_str.split('|'))
        return [
            affix_id for affix_id, affix_def in self.affix_defs.items()
            if target_pools.intersection(affix_def['affix_pools'].split('|'))
        ]

    def _roll_one_affix(self, affix_id: str, quality_roll: int) -> dict:
        """Calculates the final value of an affix based on its base value and the quality roll."""
        affix_def = self.affix_defs[affix_id]
        base_value = affix_def['base_value']
        final_value = base_value * (quality_roll / 100.0)

        # Return a dictionary representing the final, rolled affix instance
        return {
            "affix_id": affix_id,
            "stat_affected": affix_def['stat_affected'],
            "mod_type": affix_def['mod_type'],
            "description": affix_def['description'],
            "base_value": base_value,
            "value": round(final_value, 4) # Round to a reasonable number of decimal places
        }

```

## 4.0 Example Output

A call to `ItemGenerator.generate('base_iron_axe')` would result in a unique item object like the one below, which contains all the static and dynamically rolled data needed by the game engine.

```json
{
  "instance_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "base_id": "base_iron_axe",
  "name": "Iron Axe",
  "rarity": "Rare",
  "quality_tier": "Good",
  "quality_roll": 30,
  "affixes": [
    {
      "affix_id": "flat_dmg",
      "stat_affected": "base_damage",
      "mod_type": "flat",
      "description": "+{value} Base Damage",
      "base_value": 50,
      "value": 15.0
    },
    {
      "affix_id": "bleed_chance",
      "stat_affected": "proc_rate_bleed",
      "mod_type": "flat",
      "description": "{value}% chance to Bleed",
      "base_value": 0.25,
      "value": 0.075
    }
  ]
}
```

This system provides a powerful and flexible foundation for creating a compelling loot system that can be easily balanced and expanded upon by editing simple spreadsheet files.