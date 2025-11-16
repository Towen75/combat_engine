# Procedural Item Extension Guide v2.0

This comprehensive guide covers extending the **Master Rule Data System** - a complete CSV-driven architecture for adding content to the Combat Engine. This includes advanced affixes, skills, effects, and complex reactive mechanics.

## Overview of CSV Files

The system uses four interconnected CSV files:

| File | Purpose | Main Use Cases |
|------|---------|----------------|
| `data/affixes.csv` | Equipment modifiers and reactive effects | Stats, scaling, triggers, dual-stats |
| `data/skills.csv` | Combat skills and abilities | Damage, resource cost, triggers |
| `data/effects.csv` | Status effects and buffs | DoTs, buffs, debuffs, complex mechanics |
| `data/items.csv` | Equipment templates | Slot definitions, affix pools |

All changes require running `python src/data_loader.py` to regenerate the processed data.

---

## Advanced Affixes System (`data/affixes.csv`)

### Enhanced Format v2.0
```csv
affix_id,stat_affected,mod_type,affix_pools,base_value,description,trigger_event,proc_rate,trigger_result,trigger_duration,stacks_max,dual_stat,scaling_power,complex_effect
```

### Column Details

| Column | Type | Description | Requirements |
|--------|------|-------------|--------------|
| `affix_id` | String | Unique identifier | Must be unique across all affixes |
| `stat_affected` | String | EntityStats attribute(s) | Semicolon-separated for dual-stat (e.g., "crit_chance;crit_damage") |
| `mod_type` | String | Modification type(s) | Semicolon-separated: "flat;multiplier", "scaling;scaling" |
| `affix_pools` | String | Pool membership | Pipe-separated pools (e.g., "weapon_pool|axe_pool") |
| `base_value` | String/Float | Base value(s) | For dual-stat: "0.075;0.375" (semicolon-separated) |
| `description` | String | Tooltip template | Use `{value}` or `{dual_value}` for dual-stat display |
| `trigger_event` | String | When effect activates | e.g., "OnHit", "OnSkillUsed", "OnBlock" |
| `proc_rate` | Float | Chance to trigger (0.0-1.0) | Optional; leave empty for passive effects |
| `trigger_result` | String | Effect to apply | Simple names (e.g., "bleed") or complex "effect:parameter" |
| `trigger_duration` | Float | Effect duration | In seconds |
| `stacks_max` | Int | Maximum stacks | For stacking effects |
| `dual_stat` | String | Second stat name | For dual-stat affixes |
| `scaling_power` | String | Enables power scaling | Set to "true" for scaling affixes |
| `complex_effect` | String | Special effect type | e.g., "special_skill" for advanced triggers |

## Affix Types and Examples

### 1. Basic Stat Affixes
```csv
flat_dmg,base_damage,flat,weapon_pool,50,+{value} Base Damage,,,,,,,,
crit_dmg,crit_damage,flat,jewelry_pool,0.5,+{value}% Crit Damage,,,,,,,,
```

### 2. Dual-Stat Affixes (Affects Multiple Stats Simultaneously)
```csv
devastating_strikes,crit_chance;crit_damage,flat;flat,jewelry_pool,0.075;0.375,{value}% Crit & {dual_value}% Crit Damage,,,,,,,,true,
precision_power,pierce_ratio;max_resource,multiplier;flat,weapon_pool,0.15;25,{value}% Pierce & {dual_value} Max Resource,,,,,,,,true,
```

### 3. Scaling Affixes (Grows Stronger with Character Power)
```csv
berserker_rage,base_damage;crit_chance,scaling;scaling,jewelry_pool,0.5;0.3,{value}% Damage & Crit (scales with power),,,,,,,,,true,true
```

### 4. Reactive Trigger Affixes (Complex Effects)
```csv
thornmail,,,armor_pool,,,,OnBlock,0.5,reflect_damage:0.3,,,true,,
focused_rage,,,jewelry_pool,,,,OnSkillUsed,1.0,apply_crit_bonus:0.25,5.0,3,,true,special_skill
```

### 5. Pure Reactive Affixes (No Stat Bonuses)
```csv
blinding_rebuke,,,jewelry_pool,,,,OnBlock,0.8,reduced_evasion:0.15,3.0,1,,true,,
```

## Complex Trigger Effects

### Format: `"effect_name:parameter"`
The trigger_result column supports complex effects using `"effect_name:parameter"` format.

### Available Effect Types:
- **Standard Effects**: `"bleed"`, `"freeze"`, `"burn"`, `"stun"`, etc.
- **Damage Reflection**: `"reflect_damage:0.3"` (reflects 30% of blocked damage)
- **Stat Modification**: `"apply_crit_bonus:0.25"` (+25% crit chance)  
- **Healing Effects**: `"heal_self:0.2"` (heal 20% of damage dealt)
- **Chain Effects**: `"chain_damage:0.6"` (60% damage to adjacent targets)
- **Life Drain**: `"drain_life:0.05"` (drain 5% of target health per tick)
- **Divine Effects**: `"bless_allies:0.3"` (heal nearby allies)
- **Self Damage**: `"self_damage:0.5"` (take damage when triggering)
- **Resource Effects**: Various resource manipulation effects

### Trigger Events:
- `"OnHit"` - When the attack hits (any damage)
- `"OnCrit"` - When the attack crits
- `"OnBlock"` - When the attack is blocked
- `"OnDodge"` - When the attack is dodged
- `"OnSkillUsed"` - When any skill is used (requires complex_effect match)

---

## Skills and Abilities (`data/skills.csv`)

Add combat skills using the CSV-driven skill system.

### Enhanced Format v2.0
```csv
skill_id,name,damage_type,hits,description,resource_cost,cooldown,trigger_event,proc_rate,trigger_result,trigger_duration,stacks_max
```

### Column Details

| Column | Type | Description | Requirements |
|--------|------|-------------|--------------|
| `skill_id` | String | Unique identifier | Must be unique across all skills |
| `name` | String | Display name | Any descriptive string |
| `damage_type` | String | Damage category | `Physical`, `Magic`, `Fire`, `Shadow`, etc. |
| `hits` | Int | Multi-hit attacks | Number of attacks in sequence |
| `description` | String | Flavor text | Human-readable description |
| `resource_cost` | Float | Resource required | Optional; leave as 0.0 for basic attacks |
| `cooldown` | Float | Cooldown duration (seconds) | Optional; leave as 0.0 for simple skills |
| `trigger_event` | String | When skill effects activate | e.g., "OnHit", "OnCrit", "OnSkillUsed" |
| `proc_rate` | Float | Chance to trigger (0.0-1.0) | Required for triggers |
| `trigger_result` | String | Effect to apply | Simple or "effect:parameter" format |
| `trigger_duration` | Float | Effect duration | In seconds |
| `stacks_max` | Int | Maximum effect stacks | For stacking triggered effects |

### Skill Examples

```csv
# Basic skills
basic_slash,Basic Slash,Physical,1,Basic physical attack that deals moderate damage.,0,1.0,,,,,

# Resource-costing skills with triggers
bleed_strike,Bleed Strike,Physical,1,Slash that causes bleeding DoT on critical hits.,15,3.0,OnCrit,0.8,apply_bleed,8.0,3
flame_burst,Flame Burst,Fire,1,Explosive fire damage that burns enemies.,25,4.0,OnHit,0.8,apply_burn_dot,6.0,3

# Special skills with complex effects
holy_shield,Holy Shield,Divine,1,Divine protection that blocks all damage for 3 seconds.,50,12.0,OnSkillUsed,1.0,apply_divine_shield,3.0,1
berserker_rage,Berserker Rage,Physical,1,Powerful rage-fueled attack with lifesteal.,40,7.0,OnHit,1.0,heal_self:0.2,0,0
teleport_strike,Teleport Strike,Physical,1,Teleport behind enemy for guaranteed hit.,30,5.0,OnHit,1.0,stun_target,2.0,1
```

---

## Status Effects and DoTs (`data/effects.csv`)

Define the actual effect mechanics that skills and affixes trigger.

### Format v2.0
```csv
effect_id,name,type,description,max_stacks,tick_rate,damage_per_tick,stat_multiplier,stat_add,visual_effect,duration
```

### Column Details

| Column | Type | Description | Requirements |
|--------|------|-------------|--------------|
| `effect_id` | String | Unique identifier | Must match skill/affix trigger_result references |
| `name` | String | Display name | Human-readable effect name |
| `type` | String | Effect category | `buff`, `debuff`, `dot`, `stun`, etc. |
| `description` | String | Flavor text | Human-readable description |
| `max_stacks` | Int | Maximum stack count | Non-negative integer |
| `tick_rate` | Float | Seconds between ticks | 0.0 for instant effects |
| `damage_per_tick` | Float | Damage per tick (negative = healing) | 0.0 for non-damage effects |
| `stat_multiplier` | Float | Multiplicative stat bonus | 1.0 = no change, 1.2 = +20% |
| `stat_add` | Float | Additive stat bonus | Direct stat addition |
| `visual_effect` | String | Visual effect asset | VFX name for rendering |
| `duration` | Float | Effect duration | In seconds |

### Effect Examples

```csv
# Damage over time effects
bleed,Bleeding DoT,debuff,Bleeding wound that deals physical damage over time.,10,1.0,8.0,0.0,0.0,"red_blood_particles",10.0
burn,Burning DoT,debuff,Flaming burn that deals fire damage over time.,8,2.0,4.0,0.0,0.0,"flame_particles",8.0
poison,Venom DoT,debuff,Venomous poison that deals nature damage over time.,12,1.5,6.0,0.0,0.0,"green_gas_cloud",12.0

# Stun effects
freeze,Frozen,stun,Frozen solid, preventing all movement and actions.,1,0.0,0.0,0.0,0.0,"ice_crystals",4.0
stun,Stunned,stun,Stunned and incapacitated, unable to act.,1,0.0,0.0,0.0,0.0,"yellow_stun_stars",3.0

# Stat modification effects
crit_bonus_drain,Focused Rage,buff,Increased critical strike chance.,1,0.0,0.0,0.0,25.0,"golden_buff_particles",5.0
divine_shield,Divine Protection,buff,Invulnerable to all damage.,1,0.0,0.0,1.0,0.0,"golden_shield",5.0
damage_amp_buff,Berserker Rage,buff,Increased damage output.,1,0.0,0.0,0.2,0.0,"red_aura",10.0

# Healing effects
heal_over_time_buff,Divine Blessing,buff,Heal over time.,5,2.0,-15.0,0.0,0.0,"healing_particles",10.0
lifesteal_buff,Vampiric Touch,buff,Life steal on attacks.,1,0.0,0.0,0.0,0.0,"blood_trail",8.0
```

---

## Loading and Integration

### Data Loading Process

After editing any CSV files, regenerate the master data:

```bash
python src/data_loader.py
```

This loads and validates all CSV data, caching it for runtime access.

### Runtime Integration

Use the MasterRuleData singleton for all content access:

```python
from src.data_loader import get_data_loader

loader = get_data_loader()

# Load content by ID
skill = loader.get_skill('berserker_rage')
affix = loader.get_affix('thornmail')
effect = loader.get_effect('bleed')

# Query by criteria
magic_skills = loader.find_skills_by_type('Magic')
weapon_affixes = loader.find_affixes_by_pool('weapon_pool')

# Get all content
all_skills = loader.get_all_skills()
all_effects = loader.get_all_effects()
```

### Equipment Integration

Items automatically use CSV-defined affixes when equipped:

```python
from src.models import Item

# Create item with CSV-defined affixes
item = Item(instance_id='sword1', base_id='berserker_sword',
           name='Berserker Sword', slot='weapon',
           rarity='Epic', quality_tier='Perfect',
           quality_roll=9,
           affixes=[loader.get_affix('berserker_rage')])

attacker.equip_item(item)
```

## Content Creation Workflow

### Step 1: Define Effect Mechanics
Start with effects.csv to define the actual mechanics:
```csv
reflect_buff,Thornmail Reflection,buff,Reflect percentage of blocked damage,1,0.0,0.0,0.0,0.0,"spike_aura",999.0
crit_buff,Focused Rage Bonus,buff,Temporary critical strike bonus,1,0.0,0.0,0.0,25.0,"golden_buff_particles",5.0
```

### Step 2: Create Affixes with Triggers
Define affixes that reference the effects:
```csv
thornmail,,,armor_pool,,,,OnBlock,0.5,reflect_buff,,,true,,
focused_rage,,,jewelry_pool,,,,OnSkillUsed,1.0,crit_buff,5.0,3,,true,special_skill
```

### Step 3: Design Skills (Optional)
Create skills that reference the effects:
```csv
focus_skill,Focus Strike,Physical,1,Charge up for special effects,20,0.0,OnSkillUsed,1.0,special_skill,0.0,1
```

### Step 4: Configure Equipment
Set up items that use the affixes:
```csv
base_thorn_armor,Thornmail Armor,Chest,Epic,armor_pool,thornmail,2
base_rage_amulet,Rage Amulet,Amulet,Rare,jewelry_pool,focused_rage,1
```

### Step 5: Regenerate and Test
```bash
python src/data_loader.py
python test_phase4.py
```

## Advanced Mechanics

### Scaling Power System
Scaling affixes grow stronger based on character power level:

```csv
# Character power = base_damage + health/10 + armor*2 + crit_chance*100 + pierce*1000
# Scaling multiplier = 1.0 + log(power_level + 1) * 0.1
berserker_rage,base_damage;crit_chance,scaling;scaling,jewelry_pool,0.5;0.3,{value}% Damage & Crit (scales with power),,,,,,,,,true,true
```

### Complex Trigger Effects
Advanced trigger parsing supports parameterized effects:

```csv
# Format: "effect_name:parameter"
reflect_damage:0.3      # Reflect 30% of blocked damage
apply_crit_bonus:0.25   # +25% crit chance bonus
heal_self:0.2          # Heal 20% of damage dealt
chain_damage:0.6       # 60% damage to adjacent targets
drain_life:0.05        # Drain 5% of target health per tick
bless_allies:0.3       # Heal nearby allies 30% of damage
stun_target            # Apply stun debuff
```

### Dual-Stat Affixes
Single affixes that modify multiple stats simultaneously:

```csv
# "stat1;stat2" with "value1;value2" and display {value}/{dual_value}
devastating_strikes,crit_chance;crit_damage,flat;flat,jewelry_pool,0.075;0.375,{value}% Crit & {dual_value}% Crit Damage,,,,,,,,true,
```

## Validation and Debugging

### Validation Checks
The system automatically validates:
- All trigger results reference valid effects
- All stat names match EntityStats attributes
- Numeric values are properly formatted
- Required columns are present

### Troubleshooting
```bash
# Check for data consistency issues
python -c "from src.data_loader import get_data_loader; loader = get_data_loader(); print(loader.validate_data_consistency())"

# Reload data after changes
python -c "from src.data_loader import reload_data; reload_data()"
```

### Testing Framework
```bash
# Test specific functionality
python test_trigger_parsing.py    # Test trigger parsing
python test_phase4.py            # Test master data system
python run_full_test.py          # Full integration test
```

## Data Flow Diagram

```
CSV Files ──→ Data Loader ──→ Validation ──→ Runtime Objects
    ↓              ↓              ↓                ↓
affixes.csv    AffixDefinition   Affix Objects     Entity.active_triggers
skills.csv     LoadedSkill       Skill Objects     Attack Calculations
effects.csv    EffectDefinition  Debuff Objects    Applied Effects
items.csv      Item Templates    Item Objects      Equipment Stats

Complex Effects: "effect:parameter" → Parsed → Applied to Target
Scaling Affixes: power_level → multiplier → enhanced values
Dual-Stat: "stat1;stat2" → simultaneous modifications
```

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
