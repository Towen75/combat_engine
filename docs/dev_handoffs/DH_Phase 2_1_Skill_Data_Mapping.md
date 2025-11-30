# 🚀 Implementation Hand-off: Phase 2.1 - Skill Data & Mapping

**Related Work Item:** `WI_Phase_2_1.md` (Skill Data & Mapping)

## 📦 File Manifest
| Action | File Path | Description |
| :---: | :--- | :--- |
| ✏️ Modify | `src/data/schemas.py` | Add `damage_multiplier` and `default_attack_skill` to schemas |
| ✏️ Modify | `src/data/typed_models.py` | Update Data Models with new fields |
| ✏️ Modify | `src/data/game_data_provider.py` | Add cross-reference validation (Item -> Skill) |
| ✏️ Modify | `scripts/build_content.py` | Update builder to write `default_attack_skill` to CSV |
| ✏️ Modify | `blueprints/families.yaml` | Map item families to specific attack skills |
| ✏️ Modify | `data/skills.csv` | Add new column and weapon-specific skills |
| 🆕 Create | `tests/test_weapon_data.py` | Verify data integrity and loading |

---

## 1️⃣ Configuration & Dependencies
*No new pip packages required.*

---

## 2️⃣ Code Changes

### A. `src/data/schemas.py`
**Path:** `src/data/schemas.py`
**Context:** Update validation rules for new columns.

```python
# ... inside SKILLS_SCHEMA ...
SKILLS_SCHEMA = {
    "required": ["skill_id", "name", "damage_type"],
    "columns": {
        # ... existing ...
        "damage_multiplier": lambda x: float_validator(x) if x else 1.0, # <--- NEW
        "hits": lambda x: int_validator(x) if x and x.strip() else 1,
        # ... existing ...
    },
}

# ... inside ITEM_SCHEMA ...
ITEM_SCHEMA = {
    "required": ["item_id", "name", "slot", "rarity", "num_random_affixes"],
    "columns": {
        # ... existing ...
        "num_random_affixes": lambda x: int_validator(x) if x and x.strip() else 0,
        "default_attack_skill": str_validator, # <--- NEW
    },
}
```

### B. `src/data/typed_models.py`
**Path:** `src/data/typed_models.py`
**Context:** Update Dataclasses to hold the new data.

```python
@dataclass
class ItemTemplate:
    # ... existing fields ...
    num_random_affixes: int = 0
    default_attack_skill: Optional[str] = None # <--- NEW

    # ... post_init ...

@dataclass
class SkillDefinition:
    # ... existing fields ...
    name: str
    damage_type: DamageType
    damage_multiplier: float = 1.0 # <--- NEW
    hits: int = 1
    # ... rest of fields ...

# ... inside hydrate_item_template ...
def hydrate_item_template(raw_data: Dict[str, Any]) -> ItemTemplate:
    # ... existing parsing ...
    return ItemTemplate(
        # ... existing fields ...
        num_random_affixes=int(raw_data['num_random_affixes']) if raw_data.get('num_random_affixes') else 0,
        default_attack_skill=raw_data.get('default_attack_skill') or None # <--- NEW
    )

# ... inside hydrate_skill_definition ...
def hydrate_skill_definition(raw_data: Dict[str, Any]) -> SkillDefinition:
    return SkillDefinition(
        # ... existing fields ...
        damage_type=normalize_enum(DamageType, raw_data['damage_type']),
        damage_multiplier=float(raw_data.get('damage_multiplier', 1.0)), # <--- NEW
        hits=int(raw_data['hits']) if raw_data.get('hits') else 1,
        # ... existing fields ...
    )
```

### C. `src/data/game_data_provider.py`
**Path:** `src/data/game_data_provider.py`
**Context:** Ensure items don't reference non-existent skills.

```python
    def _validate_cross_references(self) -> None:
        # ... existing validations ...

        # NEW: Validate Item -> Skill reference
        for item_id, item in self.items.items():
            if item.default_attack_skill:
                if item.default_attack_skill not in self.skills:
                    raise DataValidationError(
                        f"Item '{item_id}' references non-existent default_attack_skill '{item.default_attack_skill}'",
                        data_type="ItemTemplate",
                        field_name="default_attack_skill",
                        invalid_id=item.default_attack_skill,
                        suggestions=list(self.skills.keys())
                    )
```

### D. `scripts/build_content.py`
**Path:** `scripts/build_content.py`
**Context:** Update the compiler to read the skill ID from blueprints and write it to CSV.

```python
    # ... inside Item Generation loop ...
    
    # Add new header to item_headers list
    item_headers = [
        "item_id", "name", "slot", "rarity", 
        "affix_pools", "implicit_affixes", "num_random_affixes",
        "default_attack_skill" # <--- NEW HEADER
    ]

    for fam in families:
        base_id = fam["id"]
        fam_implicits = fam.get("implicits", [])
        default_skill = fam.get("default_attack_skill", "") # <--- READ FROM BLUEPRINT
        
        for rarity in rarities:
            # ... existing id generation ...
            
            row = {
                # ... existing fields ...
                "implicit_affixes": "|".join(current_implicits),
                "num_random_affixes": slots[rarity],
                "default_attack_skill": default_skill # <--- WRITE TO ROW
            }
            item_rows.append(row)
```

### E. `blueprints/families.yaml`
**Path:** `blueprints/families.yaml`
**Context:** Map the families to the new skills.

```yaml
families:
  # WARRIOR
  - id: "greatsword"
    name: "Greatsword"
    slot: "Weapon"
    default_attack_skill: "attack_greatsword" # <--- NEW
    implicits: ["melee_damage", "bleed_damage"]
    affix_pools: "warrior_pool|sword_pool|weapon_pool"

  - id: "battle_axe"
    name: "Battle Axe"
    slot: "Weapon"
    default_attack_skill: "attack_axe" # <--- NEW
    implicits: ["pierce_bonus", "threat_generation"]
    affix_pools: "warrior_pool|axe_pool|weapon_pool"

  # ROGUE
  - id: "assassin_dagger"
    name: "Assassin Dagger"
    slot: "Weapon"
    default_attack_skill: "attack_dagger" # <--- NEW
    implicits: ["crit_multiplier", "poison_damage"]
    affix_pools: "rogue_pool|dagger_pool|weapon_pool"

  - id: "recurve_bow"
    name: "Recurve Bow"
    slot: "Weapon"
    default_attack_skill: "attack_bow" # <--- NEW
    implicits: ["movement_speed", "crit_chance"]
    affix_pools: "rogue_pool|bow_pool|weapon_pool"

  # MAGE
  - id: "arcane_staff"
    name: "Arcane Staff"
    slot: "Weapon"
    default_attack_skill: "attack_staff" # <--- NEW
    implicits: ["spell_power", "mana_regeneration"]
    affix_pools: "caster_pool|staff_pool|weapon_pool"

  - id: "spellblade"
    name: "Spellblade"
    slot: "Weapon"
    default_attack_skill: "attack_sword" # <--- NEW
    implicits: ["magic_penetration", "spell_crit_damage"]
    affix_pools: "caster_pool|sword_pool|weapon_pool"

  # Armor remains unchanged (no attack skill)
  - id: "plate_armor"
    name: "Plate Armor"
    slot: "Chest"
    implicits: ["tank_armor", "flat_health"]
    affix_pools: "warrior_pool|armor_pool|plate_pool"
    
  # ... Add remaining armor families ...
```

### F. `data/skills.csv`
**Path:** `data/skills.csv`
**Context:** Add the `damage_multiplier` column and definitions for the new weapon skills.

```csv
skill_id,name,damage_type,damage_multiplier,hits,description,resource_cost,cooldown,trigger_event,proc_rate,trigger_result,trigger_duration,stacks_max
basic_slash,Basic Slash,Physical,1.0,1,Basic attack,0,1.0,,0.0,,0.0,0
attack_unarmed,Unarmed Strike,Physical,1.0,1,Punch,0,1.0,,0.0,,0.0,0
attack_dagger,Dual Slash,Physical,0.6,2,Quick double strike,0,0.8,,0.0,,0.0,0
attack_greatsword,Heavy Swing,Physical,1.4,1,Slow heavy hit,0,1.5,,0.0,,0.0,0
attack_axe,Cleave,Physical,1.2,1,Wide swing,0,1.2,,0.0,,0.0,0
attack_staff,Arcane Bolt,Magic,1.0,1,Magic missile,0,1.0,,0.0,,0.0,0
attack_bow,Quick Shot,Piercing,0.9,1,Ranged shot,0,0.8,,0.0,,0.0,0
attack_sword,Slash,Physical,1.0,1,Standard slash,0,1.0,,0.0,,0.0,0
# ... preserve existing skills ...
```

### G. `tests/test_weapon_data.py`
**Path:** `tests/test_weapon_data.py`
**Context:** Verify the pipeline works.

```python
import pytest
from src.data.game_data_provider import GameDataProvider
from src.data.typed_models import DataValidationError

class TestWeaponData:
    
    def test_skills_load_multiplier(self):
        """Test that skills.csv loads the new damage_multiplier field."""
        # Setup mock data for skill
        raw_data = {
            "skills": {
                "test_dagger_attack": {
                    "skill_id": "test_dagger_attack",
                    "name": "Dagger",
                    "damage_type": "Physical",
                    "damage_multiplier": "0.5",
                    "hits": "2"
                }
            }
        }
        
        provider = GameDataProvider.__new__(GameDataProvider)
        provider._hydrate_data(raw_data)
        
        skill = provider.skills["test_dagger_attack"]
        assert skill.damage_multiplier == 0.5
        assert skill.hits == 2

    def test_item_loads_default_skill(self):
        """Test that items load the default_attack_skill."""
        raw_data = {
            "items": {
                "dagger_common": {
                    "item_id": "dagger_common",
                    "name": "Dagger",
                    "slot": "Weapon",
                    "rarity": "Common",
                    "default_attack_skill": "attack_dagger"
                }
            }
        }
        
        provider = GameDataProvider.__new__(GameDataProvider)
        provider._hydrate_data(raw_data)
        
        item = provider.items["dagger_common"]
        assert item.default_attack_skill == "attack_dagger"

    def test_validation_fails_on_missing_skill(self):
        """Test validation catches items pointing to missing skills."""
        raw_data = {
            "items": {
                "broken_sword": {
                    "item_id": "broken_sword",
                    "name": "Broken",
                    "slot": "Weapon",
                    "rarity": "Common",
                    "default_attack_skill": "missing_skill"
                }
            },
            "skills": {} # Empty skills
        }
        
        provider = GameDataProvider.__new__(GameDataProvider)
        provider.skills = {}
        provider._hydrate_data(raw_data)
        
        with pytest.raises(DataValidationError) as exc:
            provider._validate_cross_references()
            
        assert "missing_skill" in str(exc.value)
        assert "broken_sword" in str(exc.value)
```

---

## 🧪 Verification Steps

**1. Run Content Builder**
Regenerate your items CSV to include the new column.
```bash
python scripts/build_content.py --validate
```
*Expected:* `✅ Data Load Successful!` (Ensure `data/skills.csv` was updated first).

**2. Run Unit Tests**
```bash
python -m pytest tests/test_weapon_data.py
```

## 📋 Migration Notes
**Existing Skills:** When updating `data/skills.csv`, ensure all existing skill entries receive `damage_multiplier: 1.0` to maintain current balance. The schema defaults to 1.0, but explicit values prevent confusion.

**Example Migration:**
```csv
# BEFORE
skill_id,name,damage_type,hits,description
basic_slash,Basic Slash,Physical,1,Basic attack

# AFTER
skill_id,name,damage_type,damage_multiplier,hits,description
basic_slash,Basic Slash,Physical,1.0,1,Basic attack
```

## 📖 Documentation Updates Required
**File:** `docs/data_pipeline.md`
**Action:** Document the new `damage_multiplier` field in `SkillDefinition` and `default_attack_skill` field in `ItemTemplate`. Update the data flow diagrams to show the Item→Skill relationship validation.

## ⚠️ Rollback Plan
If this causes failures:
1.  Revert `src/data/schemas.py`, `src/data/typed_models.py`, `src/data/game_data_provider.py`.
2.  Revert `scripts/build_content.py`.
3.  Restore backup of `data/skills.csv` and `blueprints/families.yaml`.
4.  Run `python scripts/build_content.py` to restore old `items.csv`.
