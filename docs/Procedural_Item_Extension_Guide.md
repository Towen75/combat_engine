# Procedural Item Extension Guide

This guide covers how to extend the procedural item generator system by adding new affixes and items through CSV data files.

## Adding New Affixes (`data/affixes.csv`)

### Format
```csv
affix_id,stat_affected,mod_type,affix_pools,base_value,description
```

### Column Details

| Column | Type | Description | Requirements |
|--------|------|-------------|--------------|
| `affix_id` | String | Unique identifier | Must be unique across all affixes |
| `stat_affected` | String | Exact EntityStats attribute name | Must match: `base_damage`, `crit_chance`, `crit_damage`, `pierce_ratio`, `max_health`, `armor`, `resistances`, `attack_speed` |
| `mod_type` | String | Modification type | Must be: `"flat"` (additive) or `"multiplier"` (percentage multiplier) |
| `affix_pools` | String | Pool membership (pipe-separated) | Must reference existing pools; empty string for global affixes |
| `base_value` | Float | Base value at 100% quality | Appropriate scale for the stat (damage ~50, % values ~0.1-0.5) |
| `description` | String | Tooltip template | Must contain `{value}` placeholder for final rolled value |

### Constraints
- **stat_affected**: Must be a valid EntityStats attribute name
- **mod_type**: Limited to `"flat"` or `"multiplier"`
- **base_value**: Should be positive; multipliers use fractional percentages (0.20 = 20%)
- **description**: Template must include `{value}` for value substitution

### Examples
```csv
flat_dmg,base_damage,flat,weapon_pool|axe_pool,50,+{value} Base Damage
crit_chance,crit_chance,flat,jewelry_pool,0.10,{value} Critical Strike Chance
attack_speed,attack_speed,multiplier,weapon_pool,0.20,+{value}% Attack Speed
```

## Adding New Items (`data/items.csv`)

### Format
```csv
item_id,name,slot,rarity,affix_pools,implicit_affixes,num_random_affixes
```

### Column Details

| Column | Type | Description | Requirements |
|--------|------|-------------|--------------|
| `item_id` | String | Unique identifier | Must be unique across all items |
| `name` | String | Display name | Any descriptive string |
| `slot` | String | Equipment slot | Must be valid slot: `Head`, `Chest`, `Hands`, `Feet`, `Weapon`, `OffHand`, `Ring`, `Amulet`, `Belt`, `Shoulders`, `Pants` |
| `rarity` | String | Item rarity tier | Must exist in `quality_tiers.csv`: `Common`, `Uncommon`, `Rare`, `Epic`, `Legendary`, `Mythic`, etc. |
| `affix_pools` | String | Pool membership (pipe-separated) | Must reference existing pools in `affixes.csv` |
| `implicit_affixes` | String | Always-present affixes (pipe-separated) | Must reference valid `affix_id`s from `affixes.csv`; leave empty if none |
| `num_random_affixes` | Integer | Random affixes to roll | Non-negative integer (0 = no random affixes) |

### Constraints
- **slot**: Must match Entity equipment slot definitions
- **rarity**: Must be defined in quality tiers for item quality rolls
- **affix_pools**: Affixes will be selected from these pools only
- **implicit_affixes**: Always applied; count toward total affixes
- **num_random_affixes**: System ensures no duplicate affixes; may select fewer if pools are small

### Examples
```csv
base_iron_axe,Iron Axe,Weapon,Rare,weapon_pool|axe_pool,,2
base_gold_ring,Gold Ring,Ring,Legendary,jewelry_pool,crit_dmg,3
base_iron_helm,Iron Helm,Head,Epic,armor_pool,resistance,2
```

## Updating the System

After editing CSV files, regenerate the processed data:

```bash
python src/data_parser.py
```

This creates `data/game_data.json` with all parsed affix templates and item definitions.

## Validation Rules

The system enforces:
- All referenced affixes must exist
- All rarity tiers must be valid
- Stat names must match EntityStats attributes
- Equipment slots must be predefined
- No duplicate affix_ids or item_ids
- Numeric values must be valid floats/integers

## Testing Changes

Test new content:
```bash
# Run all tests
python -m pytest tests/ -v

# Test item generation
python demo_item.py
```

## System Mechanics

### Item Quality System
Items use a two-step generation process:
1. **Quality Tier Roll**: Rarity determines tier weighting (e.g., Mythic items favor "Masterful" tier)
2. **Quality Percentage**: Within tier, get random percentage (21-25% for "Fine" tier)

### Sub-Quality Variation
Each affix on an item rolls its own quality level (0 to item_quality_max%):
- **High-quality items** (90%+) can have affixes ranging from 0-90% power
- **Low-quality items** (30%) are limited to 0-30% on all affixes
- **Prevents identical items** while maintaining power hierarchy

### Affix Pools
- **Weapon affixes** go in `weapon_pool` for all weapons
- **Armor affixes** go in `armor_pool` for all armor pieces
- **Jewelry affixes** go in `jewelry_pool` for rings/amulets/necklaces
- **Specific pools** like `axe_pool`, `sword_pool` for weapon-specific effects

## Best Practices

- Use descriptive, consistent naming conventions
- Balance base_values appropriately for each stat
- Consider affinity pools carefully (general vs. slot-specific affixes)
- Test edge cases (Mythic items, full armor sets)
- Ensure new content integrates with existing balance
