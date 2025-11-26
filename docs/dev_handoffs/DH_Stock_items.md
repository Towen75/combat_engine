# 🚀 Implementation Hand-off: Stock Items - Phase 2 (Expanded)

**Related Work Item:** `WI_Stock_Items.md` (Archetype Weapon & Armor Families)
**Update:** Now includes item families for **every equipment slot** defined in the engine.

## 📦 File Manifest
| Action | File Path | Description |
| :---: | :--- | :--- |
| ✏️ Modify | `blueprints/families.yaml` | Define complete item sets (Weapons, Armor, Jewelry) for Warrior, Rogue, and Spellcaster |
| 🧪 Verify | `data/items.csv` | Generated output validation |

---

## 1️⃣ Configuration & Dependencies
*No new pip packages required.*

---

## 2️⃣ Code Changes

### A. `blueprints/families.yaml`
**Path:** `blueprints/families.yaml`
**Context:** Defines base item families.
*   **Implicits:** Primary applies to all rarities. Secondary applies at Legendary.
*   **Pools:** Ensures random rolls match the archetype (e.g., Plate armor gets Tank affixes).

```yaml
families:
  # =================================================================
  # WARRIOR ARCHETYPE (Heavy / Tank / Bleed)
  # Slots: Weapon, OffHand, Head, Chest, Hands, Legs, Feet, Shoulders, Belt, Ring, Amulet
  # =================================================================
  - id: "greatsword"
    name: "Greatsword"
    slot: "Weapon"
    implicits: ["melee_damage", "bleed_damage"]
    affix_pools: "warrior_pool|sword_pool|weapon_pool"

  - id: "battle_axe"
    name: "Battle Axe"
    slot: "Weapon"
    implicits: ["pierce_bonus", "threat_generation"]
    affix_pools: "warrior_pool|axe_pool|weapon_pool"

  - id: "tower_shield"
    name: "Tower Shield"
    slot: "OffHand"
    implicits: ["tank_armor", "flat_health"]
    affix_pools: "warrior_pool|shield_pool|armor_pool"

  - id: "great_helm"
    name: "Great Helm"
    slot: "Head"
    implicits: ["flat_health", "tank_armor"]
    affix_pools: "warrior_pool|armor_pool|plate_pool"

  - id: "plate_armor"
    name: "Plate Armor"
    slot: "Chest"
    implicits: ["tank_armor", "flat_health"]
    affix_pools: "warrior_pool|armor_pool|plate_pool"

  - id: "plate_gauntlets"
    name: "Plate Gauntlets"
    slot: "Hands"
    implicits: ["melee_damage", "attack_speed"]
    affix_pools: "warrior_pool|armor_pool|plate_pool"

  - id: "plate_greaves"
    name: "Plate Greaves"
    slot: "Legs"
    implicits: ["flat_health", "tank_armor"]
    affix_pools: "warrior_pool|armor_pool|plate_pool"

  - id: "plate_boots"
    name: "Sabatons"
    slot: "Feet"
    implicits: ["tank_armor", "movement_speed"]
    affix_pools: "warrior_pool|armor_pool|plate_pool"

  - id: "steel_pauldrons"
    name: "Steel Pauldrons"
    slot: "Shoulders"
    implicits: ["threat_generation", "tank_armor"]
    affix_pools: "warrior_pool|armor_pool|plate_pool"

  - id: "war_belt"
    name: "War Belt"
    slot: "Belt"
    implicits: ["flat_health", "melee_damage"]
    affix_pools: "warrior_pool|armor_pool"

  - id: "soldier_ring"
    name: "Soldier's Ring"
    slot: "Ring"
    implicits: ["melee_damage", "crit_chance"]
    affix_pools: "warrior_pool|jewelry_pool"

  - id: "iron_amulet"
    name: "Iron Amulet"
    slot: "Amulet"
    implicits: ["flat_health", "tank_armor"]
    affix_pools: "warrior_pool|jewelry_pool"


  # =================================================================
  # ROGUE ARCHETYPE (Medium / Crit / Poison)
  # Slots: Weapon, Quiver, Head, Chest, Hands, Legs, Feet, Shoulders, Belt, Ring, Amulet, Cloak
  # =================================================================
  - id: "assassin_dagger"
    name: "Assassin Dagger"
    slot: "Weapon"
    implicits: ["crit_multiplier", "poison_damage"]
    affix_pools: "rogue_pool|dagger_pool|weapon_pool"

  - id: "recurve_bow"
    name: "Recurve Bow"
    slot: "Weapon"
    implicits: ["movement_speed", "crit_chance"]
    affix_pools: "rogue_pool|bow_pool|weapon_pool"

  - id: "hunter_quiver"
    name: "Hunter Quiver"
    slot: "Quiver"
    implicits: ["attack_speed", "crit_chance"]
    affix_pools: "rogue_pool|weapon_pool"

  - id: "leather_hood"
    name: "Leather Hood"
    slot: "Head"
    implicits: ["crit_chance", "stealth_value"]
    affix_pools: "rogue_pool|armor_pool|leather_pool"

  - id: "leather_tunic"
    name: "Leather Tunic"
    slot: "Chest"
    implicits: ["movement_speed", "stealth_value"]
    affix_pools: "rogue_pool|armor_pool|leather_pool"

  - id: "leather_gloves"
    name: "Leather Gloves"
    slot: "Hands"
    implicits: ["attack_speed", "crit_multiplier"]
    affix_pools: "rogue_pool|armor_pool|leather_pool"

  - id: "leather_pants"
    name: "Leather Pants"
    slot: "Legs"
    implicits: ["movement_speed", "evasion_chance"] # Using core affix
    affix_pools: "rogue_pool|armor_pool|leather_pool"

  - id: "light_boots"
    name: "Light Boots"
    slot: "Feet"
    implicits: ["movement_speed", "stealth_value"]
    affix_pools: "rogue_pool|armor_pool|leather_pool"

  - id: "rogue_shoulders"
    name: "Leather Pads"
    slot: "Shoulders"
    implicits: ["evasion_chance", "stealth_value"]
    affix_pools: "rogue_pool|armor_pool"

  - id: "utility_belt"
    name: "Utility Belt"
    slot: "Belt"
    implicits: ["crit_chance", "poison_damage"]
    affix_pools: "rogue_pool|armor_pool"

  - id: "shadow_cloak"
    name: "Shadow Cloak"
    slot: "Cloak"
    implicits: ["stealth_value", "movement_speed"]
    affix_pools: "rogue_pool|armor_pool"

  - id: "thief_ring"
    name: "Thief's Ring"
    slot: "Ring"
    implicits: ["crit_chance", "crit_multiplier"]
    affix_pools: "rogue_pool|jewelry_pool"

  - id: "agility_amulet"
    name: "Agility Amulet"
    slot: "Amulet"
    implicits: ["movement_speed", "attack_speed"]
    affix_pools: "rogue_pool|jewelry_pool"


  # =================================================================
  # SPELLCASTER ARCHETYPE (Light / Magic / Mana)
  # Slots: Weapon, OffHand, Head, Chest, Hands, Legs, Feet, Shoulders, Belt, Ring, Amulet
  # =================================================================
  - id: "arcane_staff"
    name: "Arcane Staff"
    slot: "Weapon"
    implicits: ["spell_power", "mana_regeneration"]
    affix_pools: "caster_pool|staff_pool|weapon_pool"

  - id: "spellblade"
    name: "Spellblade"
    slot: "Weapon"
    implicits: ["magic_penetration", "spell_crit_damage"]
    affix_pools: "caster_pool|sword_pool|weapon_pool"

  - id: "mystic_orb"
    name: "Mystic Orb"
    slot: "OffHand"
    implicits: ["spell_power", "spell_crit_damage"]
    affix_pools: "caster_pool|weapon_pool"

  - id: "circlet"
    name: "Circlet"
    slot: "Head"
    implicits: ["mana_regeneration", "spell_power"]
    affix_pools: "caster_pool|armor_pool|cloth_pool"

  - id: "silk_robes"
    name: "Silk Robes"
    slot: "Chest"
    implicits: ["mana_regeneration", "spell_power"]
    affix_pools: "caster_pool|armor_pool|cloth_pool"

  - id: "silk_gloves"
    name: "Silk Gloves"
    slot: "Hands"
    implicits: ["attack_speed", "spell_crit_damage"] # Attack Speed maps to cast speed concept
    affix_pools: "caster_pool|armor_pool|cloth_pool"

  - id: "silk_skirt"
    name: "Silk Skirt"
    slot: "Legs"
    implicits: ["mana_regeneration", "flat_health"]
    affix_pools: "caster_pool|armor_pool|cloth_pool"

  - id: "sandals"
    name: "Sandals"
    slot: "Feet"
    implicits: ["movement_speed", "mana_regeneration"]
    affix_pools: "caster_pool|armor_pool|cloth_pool"

  - id: "mantle"
    name: "Mantle"
    slot: "Shoulders"
    implicits: ["mana_regeneration", "spell_power"]
    affix_pools: "caster_pool|armor_pool"

  - id: "sash"
    name: "Sash"
    slot: "Belt"
    implicits: ["flat_health", "mana_regeneration"]
    affix_pools: "caster_pool|armor_pool"

  - id: "arcane_ring"
    name: "Arcane Ring"
    slot: "Ring"
    implicits: ["spell_power", "magic_penetration"]
    affix_pools: "caster_pool|jewelry_pool"

  - id: "mystic_talisman"
    name: "Mystic Talisman"
    slot: "Amulet"
    implicits: ["spell_crit_damage", "mana_regeneration"]
    affix_pools: "caster_pool|jewelry_pool"
```

---

## 🧪 Verification Steps

**1. Generate Content**
Run the builder script to regenerate everything.
```bash
python scripts/build_content.py
```

**2. Validate CSV Output**
Check that specific slot items were generated.

```bash
# Check for Warrior Helmet
grep "great_helm_common" data/items.csv

# Check for Rogue Cloak
grep "shadow_cloak_rare" data/items.csv

# Check for Mage Offhand
grep "mystic_orb_legendary" data/items.csv
```

**3. Simulation Smoke Test**
Run the simulation.
```bash
python run_simulation.py --quiet
```

## ⚠️ Rollback Plan
If this corrupts the item database or causes crashes:
1.  Revert `blueprints/families.yaml` to the previous version.
2.  Run `python scripts/build_content.py` to restore `data/items.csv` to the known good state.