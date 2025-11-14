# Implementation Plan: Procedural Item Generator

This document outlines the step-by-step plan to implement the procedural item generator service into the existing codebase, including data schema, required code changes, and a testing strategy.

### **Part 1: Analysis of Existing Code**

To integrate the `ItemGenerator` service, several existing modules will need to be aware of the new data structures and potentially be modified to use the generated items.

1.  **`src/models.py`**: This is the most critical file.
    *   The `affixes.csv` file's `stat_affected` column must correspond to attributes in an entity's statistics. We will need to inspect the `EntityStats` class (or equivalent) to ensure the example CSVs are valid.
    *   The output of the `ItemGenerator` is a dictionary representing an item. We should create a new `Item` data class in `models.py` to provide a clear and type-safe structure for these generated items. This class will replace the simple dictionary structure.

2.  **`src/engine.py` / `src/combat.py`**: These files likely contain the core combat logic.
    *   The functions that calculate combat outcomes (e.g., damage dealt, effects applied) will need to be modified to read stat modifiers from the new `Item` objects equipped by an entity. Currently, stats are likely read directly from a character's base stats. The new system will require iterating through an entity's equipped items and applying the `affixes` from each.

3.  **`src/simulation.py` / `run_simulation.py`**: These files manage the high-level simulation flow.
    *   This is the logical place to integrate the item generation. For example, after a combat encounter, the simulation could call the `ItemGenerator` to create loot drops. This will involve initializing the `ItemGenerator` with the parsed game data and calling its `generate()` method.

### **Part 2: Step-by-Step Implementation Plan**

**Step 1: Create Data Directory and CSV Files**

1.  Create a new directory: `data/`.
2.  Inside `data/`, create the three required CSV files with the example content provided in Part 3 of this plan.
    *   `data/affixes.csv`
    *   `data/items.csv`
    *   `data/quality_tiers.csv`

**Step 2: Implement the Data Parser**

1.  Create a new script: `src/data_parser.py`.
2.  This script will contain a function `parse_csv_data()` that:
    *   Reads `data/affixes.csv`, `data/items.csv`, and `data/quality_tiers.csv`.
    *   Processes the data into dictionaries and lists as described in the design document.
    *   Handles converting pipe-delimited strings into lists.
    *   Merges all the data into a single dictionary.
    *   Saves the final dictionary as `data/game_data.json`.
3.  Create a corresponding test file `tests/test_data_parser.py` to verify the parser works correctly and the resulting JSON is structured as expected.

**Step 3: Update Data Models**

1.  In `src/models.py`, create new data classes to represent the generated items and their affixes, matching the structure from the design document.

    ```python
    # In src/models.py

    from dataclasses import dataclass, field
    from typing import List, Literal

    @dataclass
    class RolledAffix:
        affix_id: str
        stat_affected: str
        mod_type: Literal['flat', 'multiplier']
        description: str
        base_value: float
        value: float

    @dataclass
    class Item:
        instance_id: str
        base_id: str
        name: str
        rarity: str
        quality_tier: str
        quality_roll: int
        affixes: List[RolledAffix] = field(default_factory=list)
    ```

**Step 4: Implement the ItemGenerator Service**

1.  Create a new file: `src/item_generator.py`.
2.  Implement the `ItemGenerator` class as detailed in the design document's pseudocode.
3.  The constructor `__init__` will take the loaded `game_data` (from `game_data.json`) as an argument.
4.  The `generate()` method will return an instance of the new `Item` data class from `src/models.py`, not a raw dictionary.

**Step 5: Create Unit Tests for the ItemGenerator**

1.  Create a new test file: `tests/test_item_generator.py`.
2.  The tests should:
    *   Load the `game_data.json` created by the data parser.
    *   Instantiate the `ItemGenerator`.
    *   Test the `_roll_quality_tier` method to ensure it returns a valid tier based on weighted probabilities for a given rarity.
    *   Test the `_get_affix_pool` method to ensure it correctly collects all affixes from multiple pools.
    *   Test the `_roll_one_affix` method to verify the value calculation is correct.
    *   Test the main `generate()` method comprehensively:
        *   Call it for a base item (`base_iron_axe`).
        *   Assert that the returned object is an instance of `models.Item`.
        *   Assert that the number of affixes matches the `implicit_affixes` plus `num_random_affixes` defined in `items.csv`.
        *   Assert that the final values of the affixes are correctly calculated based on a known `quality_roll` (this may require mocking `random.randint`).

**Step 6: Integrate into the Simulation**

1.  Modify `run_simulation.py` (or the appropriate high-level script).
2.  At the start of the simulation, load `data/game_data.json` and initialize the `ItemGenerator`.
    ```python
    # In run_simulation.py
    import json
    from src.item_generator import ItemGenerator

    with open('data/game_data.json', 'r') as f:
        game_data = json.load(f)

    item_generator = ItemGenerator(game_data)

    # ... later in the simulation ...
    # When loot needs to be generated:
    new_axe = item_generator.generate('base_iron_axe')
    print(f"Generated Item: {new_axe.name} ({new_axe.quality_tier})")
    ```
3.  Modify the combat logic in `src/engine.py` or `src/combat.py` to apply the stats from equipped items. This involves changing functions that access character stats to first check for equipped items and apply their `RolledAffix` modifiers.

### **Part 3: Example CSV Files for Testing**

These files are ready to be created and used for the implementation and unit testing.

**`affixes.csv`**

```csv
affix_id,stat_affected,mod_type,affix_pools,base_value,description
flat_dmg,base_damage,flat,weapon_pool|axe_pool,50,+{value} Base Damage
crit_dmg,crit_damage,flat,weapon_pool|jewelry_pool,0.50,+{value}% Crit Damage
bleed_chance,proc_rate_bleed,flat,axe_pool|sword_pool,0.25,{value}% chance to Bleed
flat_armor,armor,flat,armor_pool,150,+{value} Armor
attack_speed,attack_speed,multiplier,weapon_pool,0.20,+{value}% Attack Speed
health,max_health,flat,armor_pool|jewelry_pool,100,+{value} Health
```

**`items.csv`**

```csv
item_id,name,slot,rarity,affix_pools,implicit_affixes,num_random_affixes
base_iron_axe,Iron Axe,Weapon,Rare,"weapon_pool|axe_pool",flat_dmg,2
base_gold_ring,Gold Ring,Ring,Legendary,jewelry_pool,crit_dmg,3
base_leather_chest,Leather Tunic,Chest,Common,armor_pool,,1
base_steel_sword,Steel Sword,Weapon,Uncommon,"weapon_pool|sword_pool",,2
```

**`quality_tiers.csv`**

```csv
quality_id,tier_name,min_range,max_range,Common,Uncommon,Rare,Legendary
1,Awful,0,10,40,20,10,5
2,Poor,11,25,35,25,15,10
3,Good,26,50,20,30,30,20
4,Great,51,75,5,20,30,30
5,Flawless,76,90,,5,10,25
6,Perfect,91,100,,,,10
```
