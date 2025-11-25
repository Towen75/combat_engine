# 🚀 Implementation Hand-off: Phase B1 - Entity Data Structure (Revised v2)

**Related Work Item:** Phase B1 - Entity Data Structure
**Fixes:** Adds missing parser registration and tightens schema validation requirements.

## 📦 File Manifest
| Action | File Path | Description |
| :--- | :--- | :--- |
| 🆕 Create | `data/entities.csv` | Sample entity definitions |
| ✏️ Modify | `src/data/schemas.py` | Add `ENTITIES_SCHEMA` (Added `rarity` to required) |
| ✏️ Modify | `src/data/typed_models.py` | Add `EntityTemplate` and hydration |
| ✏️ Modify | `src/data/data_parser.py` | **CRITICAL:** Register `entities.csv` in parser list |
| ✏️ Modify | `src/data/game_data_provider.py` | Add loading, storage, and validation logic |
| 🆕 Create | `tests/test_entity_data.py` | Unit tests for entity loading |

---

## 1️⃣ Configuration & Dependencies
*No new pip packages required.*

---

## 2️⃣ Code Changes

### A. `data/entities.csv`
**Path:** `data/entities.csv`
**Context:** Initial sample data.

```csv
entity_id,name,archetype,level,rarity,base_health,base_damage,armor,crit_chance,attack_speed,equipment_pools,loot_table_id,description
goblin_grunt,Goblin Grunt,Monster,1,Common,50,8,0,0.05,1.2,weapon_pool,goblin_loot,A small, angry goblin.
orc_warrior,Orc Warrior,Monster,3,Uncommon,120,15,10,0.10,0.9,weapon_pool|armor_pool,orc_loot,A tough orc fighter.
hero_paladin,Paladin,Hero,5,Rare,300,25,50,0.15,1.0,sword_pool|armor_pool,,A holy warrior.
```

### B. `src/data/schemas.py`
**Path:** `src/data/schemas.py`
**Context:** Add validation logic. **Update: Added `rarity` to required fields.**

```python
# Add list_split_validator if not present
def list_split_validator(value: str) -> list[str]:
    """Validate pipe-separated lists."""
    if not value or value.strip() == "":
        return []
    return [x.strip() for x in value.split('|') if x.strip()]

# ... existing schemas ...

ENTITIES_SCHEMA = {
    # FIXED: Added 'rarity' to required fields
    "required": ["entity_id", "name", "base_health", "base_damage", "rarity"],
    "columns": {
        "entity_id": str_validator,
        "name": str_validator,
        "archetype": str_validator,
        "level": lambda x: int_validator(x) if x else 1,
        "rarity": str_validator,
        "base_health": positive_float_validator,
        "base_damage": non_negative_float_validator,
        "armor": lambda x: non_negative_float_validator(x) if x and x.strip() else 0.0,
        "crit_chance": lambda x: non_negative_float_validator(x) if x and x.strip() else 0.0,
        "attack_speed": lambda x: positive_float_validator(x) if x and x.strip() else 1.0,
        "equipment_pools": list_split_validator,
        "loot_table_id": str_validator,
        "description": str_validator,
    },
}

# Update get_schema_validator
def get_schema_validator(filepath: str) -> Dict[str, Any]:
    filename = filepath.lower()
    # ... existing checks ...
    if "entities" in filename and filename.endswith(".csv"):
        return ENTITIES_SCHEMA
    # ...
```

### C. `src/data/typed_models.py`
**Path:** `src/data/typed_models.py`
**Context:** Define the strict data model.

```python
# ... existing imports ...

@dataclass
class EntityTemplate:
    """Strongly-typed model for entity definition."""
    entity_id: str
    name: str
    archetype: str
    level: int
    rarity: Rarity
    base_health: float
    base_damage: float
    armor: float
    crit_chance: float
    attack_speed: float
    equipment_pools: List[str] = field(default_factory=list)
    loot_table_id: str = ""
    description: str = ""

    def __post_init__(self):
        if not self.entity_id:
            raise ValueError("entity_id cannot be empty")
        if self.base_health <= 0:
            raise ValueError(f"base_health must be positive, got {self.base_health}")

def hydrate_entity_template(raw_data: Dict[str, Any]) -> EntityTemplate:
    return EntityTemplate(
        entity_id=raw_data['entity_id'],
        name=raw_data['name'],
        archetype=raw_data.get('archetype', 'Unit'),
        level=int(raw_data['level']) if raw_data.get('level') else 1,
        rarity=normalize_enum(Rarity, raw_data.get('rarity'), default=Rarity.COMMON),
        base_health=float(raw_data['base_health']),
        base_damage=float(raw_data['base_damage']),
        armor=float(raw_data.get('armor', 0.0)),
        crit_chance=float(raw_data.get('crit_chance', 0.0)),
        attack_speed=float(raw_data.get('attack_speed', 1.0)),
        equipment_pools=raw_data.get('equipment_pools', []),
        loot_table_id=raw_data.get('loot_table_id', ''),
        description=raw_data.get('description', '')
    )
```

### D. `src/data/data_parser.py`
**Path:** `src/data/data_parser.py`
**Context:** **CRITICAL FIX:** Register the new file in `csv_files` list.

```python
def parse_all_csvs(base_path: str = "data") -> Dict[str, Any]:
    # ... inside csv_files ...
    csv_files = [
        ("affixes.csv", "affixes"),
        ("items.csv", "items"),
        ("quality_tiers.csv", "quality_tiers"),
        ("effects.csv", "effects"),
        ("skills.csv", "skills"),
        ("loot_tables.csv", "loot_tables"),
        ("entities.csv", "entities") # <--- NEW: Ensure this line is present
    ]
    
    game_data = {
        "affixes": {},
        "items": {},
        "quality_tiers": [],
        "effects": {},
        "skills": {},
        "loot_tables": [],
        "entities": {} # <--- NEW: Ensure this key is initialized
    }
    # ... rest of function
```

### E. `src/data/game_data_provider.py`
**Path:** `src/data/game_data_provider.py`
**Context:** Add storage, loading, and specific validation logic.

```python
# Import EntityTemplate, hydrate_entity_template
from .typed_models import (
    # ... existing ...
    EntityTemplate, hydrate_entity_template
)

class GameDataProvider:
    # ... type hints ...
    entities: Dict[str, EntityTemplate]

    def _hydrate_data(self, raw_data: Dict[str, Any]) -> None:
        # ... existing hydration ...
        
        # Hydrate Entities
        self.entities = {}
        for ent_id, raw_ent in raw_data.get('entities', {}).items():
            self.entities[ent_id] = hydrate_entity_template(raw_ent)

    def _validate_cross_references(self) -> None:
        # ... existing validation ...
        self._validate_entities()

    def _validate_entities(self) -> None:
        """Validate entity references (Equipment Pools and Loot Tables)."""
        logger.info("GameDataProvider: Validating entities...")
        
        # Pre-calculate valid equipment targets
        # Valid targets are: 1. Actual Item IDs, 2. Affix Pools used by items
        valid_equipment_targets = set(self.items.keys())
        for item in self.items.values():
            valid_equipment_targets.update(item.affix_pools)

        for ent_id, entity in self.entities.items():
            # 1. Validate Loot Table
            if entity.loot_table_id:
                # Check if loot_tables exist
                if hasattr(self, 'loot_tables') and self.loot_tables:
                    if entity.loot_table_id not in self.loot_tables:
                        raise DataValidationError(
                            f"Entity '{ent_id}' references non-existent loot table '{entity.loot_table_id}'",
                            data_type="EntityTemplate", field_name="loot_table_id", invalid_id=entity.loot_table_id
                        )

            # 2. Validate Equipment Pools
            for pool in entity.equipment_pools:
                if pool not in valid_equipment_targets:
                    # Warning only
                    logger.warning(
                        f"Entity '{ent_id}' references equipment pool '{pool}' which matches no Item ID or Item Affix Pool."
                    )

    def get_entity_template(self, entity_id: str) -> EntityTemplate:
        if not self._is_initialized:
            raise RuntimeError("GameDataProvider not initialized")
        if entity_id not in self.entities:
            raise ValueError(f"Entity template '{entity_id}' not found")
        return self.entities[entity_id]
```

### F. `tests/test_entity_data.py`
**Path:** `tests/test_entity_data.py`
**Context:** Verify loading and validation.

```python
import pytest
from unittest.mock import MagicMock
from src.data.game_data_provider import GameDataProvider
from src.data.typed_models import EntityTemplate, Rarity, DataValidationError

class TestEntityDataLoading:
    
    def test_entity_hydration_defaults(self):
        """Test that defaults are applied correctly."""
        raw_data = {
            "entities": {
                "test_dummy": {
                    "entity_id": "test_dummy",
                    "name": "Dummy",
                    "base_health": "100",
                    "base_damage": "0",
                    "rarity": "Common" # Now required
                }
            }
        }
        
        provider = GameDataProvider.__new__(GameDataProvider)
        provider._hydrate_data(raw_data)
        
        entity = provider.entities["test_dummy"]
        assert entity.level == 1
        assert entity.rarity == Rarity.COMMON
        assert entity.attack_speed == 1.0
        assert entity.equipment_pools == []

    def test_entity_validation_missing_loot(self):
        """Test validation fails on missing loot table."""
        raw_data = {
            "entities": {
                "bad_goblin": {
                    "entity_id": "bad_goblin", "name": "Goblin", "base_health": "10", "base_damage": "1", "rarity": "Common",
                    "loot_table_id": "missing_table"
                }
            }
        }
        
        provider = GameDataProvider.__new__(GameDataProvider)
        provider.items = {}
        provider.loot_tables = {}
        provider._hydrate_data(raw_data)
        
        with pytest.raises(DataValidationError) as exc:
            provider._validate_entities()
            
        assert "missing_table" in str(exc.value)
```

---

## 🧪 Verification Steps

1.  **Run Unit Test:**
    ```bash
    python -m pytest tests/test_entity_data.py
    ```
2.  **Integration Check:**
    Ensure `data/entities.csv` exists and `run_simulation.py` runs without error.