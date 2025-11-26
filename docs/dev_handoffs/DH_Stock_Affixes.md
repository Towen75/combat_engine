# 🚀 Implementation Hand-off: Stock Affixes - Phase 1

**Related Work Item:** WI_Stock_Affixes.md

## 📦 File Manifest
| Action | File Path | Description |
| :---: | :--- | :--- |
| ✏️ Modify | `blueprints/affixes.yaml` | Add archetype-defining vanilla affixes (12 new definitions) |
| ✏️ Modify | `scripts/build_content.py` | Add --generate-affixes command for selective generation |

---

## 1️⃣ Configuration & Dependencies
*No new pip packages required.*

---

## 2️⃣ Code Changes

### A. `blueprints/affixes.yaml`
**Path:** `blueprints/affixes.yaml`
**Context:** Extend existing yaml with archetype-specific vanilla affixes. Focus on simple stat modifiers that define each archetype's playstyle. **CRITICAL: Uses only valid EntityStats field names to prevent crashes.**

```yaml
definitions:
  # Existing affixes (unchanged)...

  # ========== SPELLCASTER AFFIXES ==========
  - id: "spell_power"
    stat: "base_damage"
    type: "multiplier"
    base_val: 0.12
    name: "Spell Power"
    pools: ["caster_pool", "staff_pool", "magic_pool"]

  - id: "mana_regeneration"
    stat: "resource_on_hit"
    type: "flat"
    base_val: 5
    name: "Mana Regeneration"
    pools: ["caster_pool", "magic_pool"]

  - id: "magic_penetration"
    stat: "pierce_ratio"
    type: "flat"
    base_val: 0.08
    name: "Magic Penetration"
    pools: ["caster_pool", "staff_pool", "magic_pool"]

  - id: "spell_crit_damage"
    stat: "crit_damage"
    type: "flat"
    base_val: 0.25
    name: "Spell Critical Damage"
    pools: ["caster_pool", "staff_pool", "jewelry_pool"]

  # ========== WARRIOR AFFIXES ==========
  - id: "tank_armor"
    stat: "armor"
    type: "multiplier"
    base_val: 0.15
    name: "Tank Armor"
    pools: ["tank_pool", "armor_pool", "plate_pool"]

  - id: "melee_damage"
    stat: "base_damage"
    type: "multiplier"
    base_val: 0.18
    name: "Melee Damage"
    pools: ["warrior_pool", "sword_pool", "axe_pool"]

  - id: "threat_generation"
    stat: "damage_multiplier" # Proxied as damage for now
    type: "flat"
    base_val: 0.05
    name: "Threat Generation"
    pools: ["tank_pool", "shield_pool"]

  - id: "bleed_damage"
    stat: "damage_over_time"
    type: "multiplier"
    base_val: 0.25
    name: "Bleed Damage"
    pools: ["warrior_pool", "axe_pool"]

  # ========== ROGUE AFFIXES ==========
  - id: "movement_speed"
    stat: "movement_speed"
    type: "multiplier"
    base_val: 0.10
    name: "Movement Speed"
    pools: ["rogue_pool", "leather_pool", "jewelry_pool"]

  - id: "crit_multiplier"
    stat: "crit_damage"  # FIXED: Was crit_multiplier
    type: "flat"
    base_val: 0.3
    name: "Critical Multiplier"
    pools: ["rogue_pool", "dagger_pool", "bow_pool"]

  - id: "stealth_value"
    stat: "evasion_chance"
    type: "flat"
    base_val: 0.08
    name: "Stealth"
    pools: ["rogue_pool", "leather_pool", "cloak_pool"]

  - id: "poison_damage"
    stat: "damage_over_time" # FIXED: Was poison_damage
    type: "multiplier"
    base_val: 0.20
    name: "Poison Damage"
    pools: ["rogue_pool", "dagger_pool", "poison_pool"]
```

### B. `scripts/build_content.py`
**Path:** `scripts/build_content.py`
**Context:** Add command-line argument for selective affix generation during development. **FIXED: Proper scope - main() defined at top level, not nested.**

```python
import argparse
# ... imports ...

# 1. Refactor main to accept arguments at the top level
def main(generate_affixes_only=False):
    print("🔨 Starting Content Build...")

    # Load Yaml...
    # ...

    # 2. Generate Affixes (affixes.csv)
    # ... (Affine generation logic) ...

    if generate_affixes_only:
        print(f"✅ Partial Build Complete: {len(affix_rows)} affixes generated.")
        # Only write affixes.csv
        with open(DATA_DIR / "affixes.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=affix_fieldnames)
            writer.writeheader()
            writer.writerows(affix_rows)
        return

    # 3. Generate Items (Only runs if generate_affixes_only is False)
    # ... (Item generation logic) ...

    # 4. Write Files (Both)
    # ...

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Build game content from blueprints')
    parser.add_argument('--generate-affixes', action='store_true', help='Generate affixes CSV only')
    args = parser.parse_args()

    main(generate_affixes_only=args.generate_affixes)
```

---

## 🧪 Verification Steps

1.  **Extend Blueprints:**
    ```bash
    # Manually add the 12 new affix definitions to blueprints/affixes.yaml
    code blueprints/affixes.yaml
    ```

2.  **Generate Affix Data:**
    ```bash
    python scripts/build_content.py --generate-affixes
    ```

3.  **Validate Generated Files:**
    ```bash
    # Check affixes.csv for new entries
    head -20 data/base_affixes.csv
    grep "spell_power\|tank_armor\|movement_speed" data/base_affixes.csv
    
    # Check pools
    grep "caster_pool\|tank_pool\|rogue_pool" data/affix_pools.csv
    ```

4.  **Schema Validation:**
    ```bash
    python -c "from src.data.schemas import validate_affix_definitions; print('Schema validation passed')"
    ```

5.  **Integration Test:**
    ```bash
    python scripts/build_content.py  # Full generation
    python run_simulation.py        # Verify no import/data errors
    ```

## ⚠️ Rollback Plan
If this fails:
1.  Revert `blueprints/affixes.yaml` to backup copy
2.  Delete generated CSV files, run `python scripts/build_content.py` to regenerate from original blueprints
3.  Remove the --generate-affixes argument code changes
