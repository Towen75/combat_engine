# 🚀 Implementation Hand-off: Phase 1 - Portrait Data Model

**Related Work Item:** `docs/work_items/WI_Portrait-Data-Model.md`

## 📦 File Manifest
| Action | File Path | Description |
| :--- | :--- | :--- |
| ⚙️ Config | `assets/portraits/` | confirm directory structure for images exist |
| ✏️ Modify | `data/entities.csv` | Add `portrait_path` column to entity data |
| ✏️ Modify | `src/data/schemas.py` | Update `ENTITIES_SCHEMA` with validation |
| ✏️ Modify | `src/data/typed_models.py` | Add field to `EntityTemplate` and update hydration |
| 🆕 Create | `tests/test_entity_portrait_data.py` | Unit tests verifying the schema extension |

---

## 1️⃣ Configuration & Dependencies
Run these commands to set up the asset directory structure:

```bash
# Create a dummy placeholder file so tests don't fail on missing files (optional but good practice)
touch assets/portraits/placeholder.png
```

---

## 2️⃣ Code Changes

### A. `data/entities.csv`
**Path:** `data/entities.csv`
**Context:** Add the `portrait_path` column.
*Note: Ensure you handle commas in descriptions correctly (CSV parsers usually require quotes if the text contains commas).*

```csv
entity_id,name,archetype,level,rarity,base_health,base_damage,armor,crit_chance,attack_speed,equipment_pools,loot_table_id,description,portrait_path
goblin_grunt,Goblin Grunt,Monster,1,Common,50,8,0,0.05,1.2,weapon_pool,loot_warrior_grunt,"A small, angry goblin.",assets/portraits/goblin_grunt.png
orc_warrior,Orc Warrior,Monster,3,Uncommon,120,15,10,0.10,0.9,weapon_pool|armor_pool,loot_warrior_elite,"A tough orc fighter.",assets/portraits/orc_warrior.png
hero_paladin,Paladin,Hero,5,Rare,300,25,50,0.15,1.0,sword_pool|armor_pool,,"A holy warrior.",assets/portraits/hero_paladin.png
```

### B. `src/data/schemas.py`
**Path:** `src/data/schemas.py`
**Context:** Add `portrait_path` to the schema validation.

```python
# ... inside ENTITIES_SCHEMA ...
ENTITIES_SCHEMA = {
    "required": ["entity_id", "name", "base_health", "base_damage", "rarity"],
    "columns": {
        # ... existing columns ...
        "description": str_validator,
        "portrait_path": str_validator,  # <--- NEW FIELD
    },
}
```

### C. `src/data/typed_models.py`
**Path:** `src/data/typed_models.py`
**Context:** Update the Dataclass and Hydration logic.

```python
@dataclass
class EntityTemplate:
    # ... existing fields ...
    description: str = ""
    portrait_path: str = ""  # <--- NEW FIELD (Default empty)

    def __post_init__(self):
        # ... existing validation ...
        pass

def hydrate_entity_template(raw_data: Dict[str, Any]) -> EntityTemplate:
    return EntityTemplate(
        entity_id=raw_data['entity_id'],
        name=raw_data['name'],
        archetype=raw_data.get('archetype', 'Unit'),
        level=int(raw_data['level']) if raw_data.get('level') else 1,
        rarity=normalize_enum(Rarity, raw_data.get('rarity') or 'Common', default=Rarity.COMMON),
        base_health=float(raw_data['base_health']),
        base_damage=float(raw_data['base_damage']),
        armor=float(raw_data.get('armor', 0.0)),
        crit_chance=float(raw_data.get('crit_chance', 0.0)),
        attack_speed=float(raw_data.get('attack_speed', 1.0)),
        # Note: equipment_pools is already a list from the schema validator
        equipment_pools=raw_data.get('equipment_pools', []),
        loot_table_id=raw_data.get('loot_table_id', ''),
        description=raw_data.get('description', ''),
        portrait_path=raw_data.get('portrait_path', ''),  # <--- NEW MAPPING
    )
```

### D. `tests/test_entity_portrait_data.py`
**Path:** `tests/test_entity_portrait_data.py`
**Context:** Verify the data flows correctly from CSV to Model.

```python
import pytest
from src.data.game_data_provider import GameDataProvider
from src.data.typed_models import EntityTemplate

class TestEntityPortraitData:
    
    def test_portrait_path_loading(self):
        """Test that portrait paths are correctly loaded from data."""
        # Mock raw data injection
        raw_data = {
            "entities": {
                "test_hero": {
                    "entity_id": "test_hero",
                    "name": "Test Hero",
                    "base_health": "100",
                    "base_damage": "10",
                    "rarity": "Rare",
                    "portrait_path": "assets/portraits/hero.png"
                }
            }
        }
        
        provider = GameDataProvider.__new__(GameDataProvider)
        provider._hydrate_data(raw_data)
        
        entity = provider.entities["test_hero"]
        assert entity.portrait_path == "assets/portraits/hero.png"

    def test_portrait_path_default_empty(self):
        """Test that missing portrait path defaults to empty string."""
        raw_data = {
            "entities": {
                "test_mob": {
                    "entity_id": "test_mob",
                    "name": "Test Mob",
                    "base_health": "50",
                    "base_damage": "5",
                    "rarity": "Common"
                    # No portrait_path
                }
            }
        }
        
        provider = GameDataProvider.__new__(GameDataProvider)
        provider._hydrate_data(raw_data)
        
        entity = provider.entities["test_mob"]
        assert entity.portrait_path == ""
```

---

## 🧪 Verification Steps

**1. Automated Tests**
```bash
python -m pytest tests/test_entity_portrait_data.py
```

**2. Manual Check**
Ensure the CSV parser doesn't crash on the new column.
```bash
python run_simulation.py --quiet
```

## ⚠️ Rollback Plan
If this implementation causes critical failures:
1.  Remove `portrait_path` column from `data/entities.csv`.
2.  Revert `src/data/typed_models.py` (remove field and hydration line).
3.  Revert `src/data/schemas.py`.
4.  Delete `tests/test_entity_portrait_data.py`.