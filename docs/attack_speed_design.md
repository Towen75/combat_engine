# Attack Speed Design Documentation

## Overview

This document clarifies the design and implementation of the `attack_speed` stat in the combat engine, including its interpretation, usage in simulation, and future JSON loading considerations.

## Attack Speed Definition

### Core Concept
- **attack_speed** represents the number of attacks per second an entity can perform
- **Type**: `float` (positive values only)
- **Units**: attacks/second
- **Validation**: Must be > 0.0

### Mathematical Relationship
```
attacks_per_second = attack_speed
time_between_attacks = 1.0 / attack_speed
```

### Example Values
- `attack_speed = 1.0` → 1 attack per second → 1.0 seconds between attacks
- `attack_speed = 2.0` → 2 attacks per second → 0.5 seconds between attacks
- `attack_speed = 0.5` → 0.5 attacks per second → 2.0 seconds between attacks

## Implementation Details

### Simulation Usage
In the `SimulationRunner`, attack timers are initialized as:
```python
self.attack_timers[entity.id] = 1.0 / entity.final_stats.attack_speed
```

This creates a countdown timer that reaches zero when it's time to attack.

### Update Logic
During each simulation update:
1. Decrement attack timer by `delta_time`
2. When timer ≤ 0, perform attack and reset timer
3. Reset value = `1.0 / attack_speed`

### Balance Considerations
- Higher `attack_speed` values = more attacks = more damage potential
- Should be balanced against damage per hit
- Typical range: 0.5 - 3.0 attacks/second for different character types

## JSON Loading Design

### Future Data Structure
When implementing JSON loading for character/item data, the `attack_speed` field should be:

```json
{
  "characters": {
    "warrior": {
      "base_stats": {
        "attack_speed": 0.8,
        "base_damage": 25.0,
        "max_health": 150.0
      }
    },
    "assassin": {
      "base_stats": {
        "attack_speed": 1.5,
        "base_damage": 18.0,
        "max_health": 80.0
      }
    }
  }
}
```

### Validation Rules
- **Type Check**: Must be number (int/float)
- **Range Check**: Must be > 0.0
- **Reasonable Bounds**: Warning if outside 0.1 - 10.0 range

### Loading Process
1. Parse JSON data
2. Validate `attack_speed` field exists and is valid
3. Create `EntityStats` object with validated value
4. Apply equipment modifiers (flat/multiplier) to final attack speed
5. Ensure final attack speed > 0.0 (minimum 0.1)

### Equipment Modification
Attack speed can be modified by equipment affixes:
- **Flat modifiers**: `attack_speed += value`
- **Multiplier modifiers**: `attack_speed *= value`

Example:
```json
{
  "affixes": {
    "haste_boots": {
      "stat": "attack_speed",
      "mod_type": "multiplier",
      "value": 1.2
    }
  }
}
```

## Balance Guidelines

### Character Archetypes
- **Tank**: 0.5 - 0.7 attacks/second (slow, high damage/health)
- **Warrior/Fighter**: 0.8 - 1.0 attacks/second (balanced)
- **Assassin/Rogue**: 1.2 - 1.8 attacks/second (fast, low health)
- **Mage/Caster**: 0.6 - 0.8 attacks/second (slow, high damage)

### Item Balance
- **Weapons**: ±10-20% attack speed modifiers
- **Armor**: Minimal attack speed impact (defensive focus)
- **Accessories**: ±5-15% attack speed modifiers

### Simulation Validation
Use the simulation framework to validate:
- Damage per second calculations: `damage_per_hit * attack_speed`
- Combat pacing feels appropriate
- High attack speed characters aren't overpowered
- Low attack speed characters have compensatory strengths

## Technical Notes

### Floating Point Precision
- Use float64 for calculations to avoid precision issues
- Round display values to 1-2 decimal places
- Validate that `1.0 / attack_speed` doesn't cause division issues

### Performance Impact
- Higher attack speeds = more frequent combat calculations
- Simulation performance scales with total attacks across all entities
- Balance attack speed against server/client performance requirements

### Future Extensions
- **Attack Speed Scaling**: Could scale with level/rarity
- **Dynamic Modifiers**: Temporary attack speed buffs/debuffs
- **Weapon Types**: Different base attack speeds per weapon category
- **Cooldowns**: Separate from attack speed for abilities

## Testing Recommendations

### Unit Tests
- Validate attack timer calculations
- Test attack speed modification application
- Verify minimum/maximum bounds

### Integration Tests
- Run simulations with different attack speeds
- Validate damage per second calculations
- Test equipment modification effects

### Balance Tests
- Compare DPS across different attack speed/damage combinations
- Ensure no degenerate strategies (e.g., 10 attacks/second with 1 damage each)
- Validate against design target DPS values
