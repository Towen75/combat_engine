# 🚀 Implementation Hand-off: Stock Entities - Phase 3

**Related Work Item:** `WI_Stock_Entities.md` (Enemy Types & Encounters)

## 📦 File Manifest
| Action | File Path | Description |
| :---: | :--- | :--- |
| ✏️ Modify | `data/entities.csv` | Add 9 enemy archetypes (Counter-play focused) |
| ✏️ Modify | `data/loot_tables.csv` | Define loot drops for new enemies |
| 🆕 Create | `tests/test_stock_content.py` | Verify stock entities load and equip correctly |

---

## 1️⃣ Configuration & Dependencies
*No new pip packages required.*
*Ensure Phase 2 (Items) has been run (`python scripts/build_content.py`) so the item IDs referenced below exist.*

---

## 2️⃣ Code Changes

### A. `data/entities.csv`
**Path:** `data/entities.csv`
**Context:** Defines the enemy roster.
*   **Design Logic:**
    *   **Warriors:** High HP/Armor, use Plate/Axes. Weak to Magic.
    *   **Rogues:** High Speed/Crit, use Leather/Daggers. Weak to Burst.
    *   **Mages:** High Dmg/Pierce, use Cloth/Staffs. Weak to Physical.
*   **Equipment:** Uses `_common` or `_uncommon` variants generated in Phase 2.

```csv
entity_id,name,archetype,level,rarity,base_health,base_damage,armor,crit_chance,attack_speed,equipment_pools,loot_table_id,description
enemy_warrior_grunt,Iron Recruit,Warrior,1,Common,120,10,15,0.05,0.8,greatsword_common|plate_armor_common,loot_warrior_grunt,A sturdy recruit in basic plate.
enemy_warrior_guard,Citadel Guard,Warrior,5,Uncommon,300,25,40,0.05,0.9,battle_axe_uncommon|tower_shield_uncommon|plate_armor_uncommon,loot_warrior_elite,Heavily armored defender.
enemy_warrior_boss,Warlord Ghom,Warrior,10,Rare,800,60,100,0.10,0.8,greatsword_rare|great_helm_rare|plate_armor_rare,loot_warrior_boss,A mountain of steel and rage.
enemy_rogue_thief,Street Rat,Rogue,1,Common,60,12,5,0.15,1.2,assassin_dagger_common|leather_tunic_common,loot_rogue_grunt,Quick but fragile thief.
enemy_rogue_assassin,Shadow Blade,Rogue,5,Uncommon,180,35,15,0.25,1.4,assassin_dagger_uncommon|leather_hood_uncommon|leather_tunic_uncommon,loot_rogue_elite,Strikes from the shadows.
enemy_rogue_boss,Nightmaster,Rogue,10,Rare,550,80,30,0.40,1.5,recurve_bow_rare|shadow_cloak_rare|leather_tunic_rare,loot_rogue_boss,You wont see him coming.
enemy_mage_novice,Apprentice,Mage,1,Common,50,18,0,0.05,1.0,arcane_staff_common|silk_robes_common,loot_mage_grunt,Learning to control the arcane.
enemy_mage_sorcerer,Void Caller,Mage,5,Uncommon,140,45,5,0.15,1.0,spellblade_uncommon|mystic_orb_uncommon|silk_robes_uncommon,loot_mage_elite,Wields dangerous chaotic energies.
enemy_mage_boss,Grand Magus,Mage,10,Rare,450,120,10,0.25,1.1,arcane_staff_rare|circlet_rare|silk_robes_rare,loot_mage_boss,Master of the arcane arts.
```

### B. `data/loot_tables.csv`
**Path:** `data/loot_tables.csv`
**Context:** Defines what these enemies drop.
*   **Structure:** Enemies drop items from their own family (e.g., Warriors drop Plate/Weapons).
*   **Progression:**
    *   Grunts drop **Common** items.
    *   Elites drop **Uncommon** items (with chance for Rare).
    *   Bosses drop **Rare** items (with chance for Epic).

```csv
table_id,entry_type,entry_id,weight,min_count,max_count,drop_chance
loot_warrior_grunt,Item,greatsword_common,10,1,1,0.3
loot_warrior_grunt,Item,plate_armor_common,10,1,1,0.3
loot_warrior_grunt,Item,battle_axe_common,10,1,1,0.2
loot_warrior_elite,Item,battle_axe_uncommon,10,1,1,0.5
loot_warrior_elite,Item,plate_armor_uncommon,10,1,1,0.5
loot_warrior_elite,Item,great_helm_uncommon,5,1,1,0.3
loot_warrior_boss,Item,greatsword_rare,10,1,1,1.0
loot_warrior_boss,Item,plate_armor_rare,10,1,1,1.0
loot_warrior_boss,Item,iron_amulet_epic,1,1,1,0.1
loot_rogue_grunt,Item,assassin_dagger_common,10,1,1,0.3
loot_rogue_grunt,Item,leather_tunic_common,10,1,1,0.3
loot_rogue_elite,Item,recurve_bow_uncommon,10,1,1,0.5
loot_rogue_elite,Item,leather_hood_uncommon,10,1,1,0.5
loot_rogue_boss,Item,assassin_dagger_rare,10,1,1,1.0
loot_rogue_boss,Item,shadow_cloak_rare,5,1,1,0.5
loot_mage_grunt,Item,arcane_staff_common,10,1,1,0.3
loot_mage_grunt,Item,silk_robes_common,10,1,1,0.3
loot_mage_elite,Item,spellblade_uncommon,10,1,1,0.5
loot_mage_elite,Item,mystic_orb_uncommon,10,1,1,0.5
loot_mage_boss,Item,arcane_staff_rare,10,1,1,1.0
loot_mage_boss,Item,circlet_rare,10,1,1,1.0
loot_mage_boss,Item,mystic_talisman_epic,1,1,1,0.1
```

### C. `tests/test_stock_content.py`
**Path:** `tests/test_stock_content.py`
**Context:** A specific test to ensure the "Stock Content" package is cohesive (Entities reference valid Items).

```python
import pytest
from src.core.factory import EntityFactory
from src.data.game_data_provider import GameDataProvider
from src.core.rng import RNG

class TestStockContent:
    
    @pytest.fixture
    def factory(self):
        provider = GameDataProvider()
        rng = RNG(123)
        return EntityFactory(provider, None, rng) # ItemGen created internally if None

    def test_all_stock_entities_spawn_correctly(self, factory):
        """Verify every entity in the stock CSV can be instantiated with equipment."""
        stock_ids = [
            "enemy_warrior_grunt", "enemy_warrior_guard", "enemy_warrior_boss",
            "enemy_rogue_thief", "enemy_rogue_assassin", "enemy_rogue_boss",
            "enemy_mage_novice", "enemy_mage_sorcerer", "enemy_mage_boss"
        ]
        
        for eid in stock_ids:
            entity = factory.create(eid)
            assert entity is not None
            assert entity.name != ""
            # Verify equipment was actually equipped
            assert len(entity.equipment) > 0, f"{eid} failed to equip items"
            
    def test_boss_power_scaling(self, factory):
        """Verify Bosses are stronger than Grunts (sanity check)."""
        grunt = factory.create("enemy_warrior_grunt")
        boss = factory.create("enemy_warrior_boss")
        
        # Check Health
        assert boss.final_stats.max_health > grunt.final_stats.max_health
        
        # Check Damage (should be significantly higher due to Rare items vs Common)
        assert boss.final_stats.base_damage > grunt.final_stats.base_damage

    def test_loot_table_linkage(self, factory):
        """Verify entities have valid loot tables."""
        grunt = factory.create("enemy_mage_novice")
        assert grunt.loot_table_id == "loot_mage_grunt"
        
        # Verify table exists in provider
        provider = factory.provider
        assert "loot_mage_grunt" in provider.loot_tables
```

---

## 🧪 Verification Steps

**1. Run the Stock Content Test**
```bash
python -m pytest tests/test_stock_content.py
```

**2. Manual Simulation Check**
Modify `run_simulation.py` locally to spawn a "Warlord Ghom" (`enemy_warrior_boss`) and verify he is tough to kill.

## ⚠️ Rollback Plan
If this causes data loading errors:
1.  Delete lines added to `data/entities.csv`.
2.  Delete lines added to `data/loot_tables.csv`.
3.  Delete `tests/test_stock_content.py`.