Acting as **Senior Developer**, here is the **Developer Hand-off** for Phase C1.

This package implements the data structure and the critical **Cycle Detection Algorithm** to prevent infinite recursion in loot tables.

***

# 🚀 Implementation Hand-off: Phase C1 - Loot Data & Validation

**Related Work Item:** Phase C1 - Loot Data Structure & Cycle Validation

## 📦 File Manifest
| Action | File Path | Description |
| :--- | :--- | :--- |
| 🆕 Create | `data/loot_tables.csv` | New data file for loot definitions |
| ✏️ Modify | `src/data/typed_models.py` | Add `LootEntryType` Enum and models |
| ✏️ Modify | `src/data/schemas.py` | Add CSV validation schema |
| ✏️ Modify | `src/data/data_parser.py` | Register new CSV in parser logic |
| ✏️ Modify | `src/data/game_data_provider.py` | Implement hydration and **DFS Cycle Validation** |
| 🆕 Create | `tests/test_loot_validation.py` | Unit tests for DAG enforcement |

---

## 1️⃣ Configuration & Dependencies
*No new pip packages required.*

---

## 2️⃣ Code Changes

### A. `data/loot_tables.csv`
**Path:** `data/loot_tables.csv`
**Context:** Initial sample data to verify loading works.

```csv
table_id,entry_type,entry_id,weight,min_count,max_count,drop_chance
forest_zone_loot,Table,goblin_loot,100,1,1,1.0
goblin_loot,Item,dagger_common,50,1,1,0.5
goblin_loot,Item,small_potion,50,1,2,0.3
```

### B. `src/data/typed_models.py`
**Path:** `src/data/typed_models.py`
**Context:** Add Enums and Data Classes for loot.

```python
# Add to Enums
class LootEntryType(str, Enum):
    """Enum for types of entries in a loot table."""
    ITEM = "Item"
    TABLE = "Table"

# Add to Data Classes
@dataclass
class LootTableEntry:
    """A single row in a loot table."""
    table_id: str
    entry_type: LootEntryType
    entry_id: str
    weight: int
    min_count: int
    max_count: int
    drop_chance: float

@dataclass
class LootTableDefinition:
    """Aggregate object representing a full loot table (multiple entries)."""
    table_id: str
    entries: List[LootTableEntry] = field(default_factory=list)

    def get_total_weight(self) -> int:
        return sum(e.weight for e in self.entries)

# Add Hydration Function
def hydrate_loot_entry(raw_data: Dict[str, Any]) -> LootTableEntry:
    return LootTableEntry(
        table_id=raw_data['table_id'],
        entry_type=normalize_enum(LootEntryType, raw_data['entry_type']),
        entry_id=raw_data['entry_id'],
        weight=int(raw_data['weight']),
        min_count=int(raw_data['min_count']),
        max_count=int(raw_data['max_count']),
        drop_chance=float(raw_data['drop_chance'])
    )
```

### C. `src/data/schemas.py`
**Path:** `src/data/schemas.py`
**Context:** Input validation for the CSV parser.

```python
# Add to Schema definitions
LOOT_TABLES_SCHEMA = {
    "required": ["table_id", "entry_type", "entry_id", "weight"],
    "columns": {
        "table_id": str_validator,
        "entry_type": str_validator,
        "entry_id": str_validator,
        "weight": lambda x: int_validator(x) if x else 0,
        "min_count": lambda x: int_validator(x) if x else 1,
        "max_count": lambda x: int_validator(x) if x else 1,
        "drop_chance": lambda x: float_validator(x) if x else 1.0,
    },
}

# Update get_schema_validator factory
def get_schema_validator(filepath: str) -> Dict[str, Any]:
    filename = filepath.lower()
    # ... existing checks ...
    if "loot_tables" in filename and filename.endswith(".csv"):
        return LOOT_TABLES_SCHEMA
    # ...
```

### D. `src/data/data_parser.py`
**Path:** `src/data/data_parser.py`
**Context:** Register the new file in `parse_all_csvs`.

```python
def parse_all_csvs(base_path: str = "data") -> Dict[str, Any]:
    # ... inside the csv_files list ...
    csv_files = [
        # ... existing ...
        ("entities.csv", "entities"),
        ("loot_tables.csv", "loot_tables") # <--- NEW
    ]
    
    game_data = {
        # ... existing ...
        "entities": {},
        "loot_tables": [] # <--- NEW (List because rows share IDs)
    }
    # ... rest of function ...
```

### E. `src/data/game_data_provider.py`
**Path:** `src/data/game_data_provider.py`
**Context:** Core logic for hydration and **DFS Cycle Detection**.

```python
# Imports
from .typed_models import (
    LootTableDefinition, LootEntryType, hydrate_loot_entry
)

class GameDataProvider:
    # ... type hints ...
    loot_tables: Dict[str, LootTableDefinition]

    # Update _hydrate_data
    def _hydrate_data(self, raw_data: Dict[str, Any]) -> None:
        # ... existing hydration ...
        
        # Hydrate Loot Tables (Aggregate rows into Definitions)
        self.loot_tables = {}
        raw_loot_list = raw_data.get('loot_tables', [])
        
        for row in raw_loot_list:
            entry = hydrate_loot_entry(row)
            if entry.table_id not in self.loot_tables:
                self.loot_tables[entry.table_id] = LootTableDefinition(table_id=entry.table_id)
            self.loot_tables[entry.table_id].entries.append(entry)

    # Update _validate_cross_references
    def _validate_cross_references(self) -> None:
        # ... existing validation ...
        self._validate_loot_tables()

    # NEW: Cycle Detection Logic
    def _validate_loot_tables(self) -> None:
        """Validate Loot Tables: Check references and enforce DAG structure."""
        logger.info("GameDataProvider: Validating loot tables...")
        
        visited = set()
        recursion_stack = set()

        def dfs_check_cycles(table_id: str):
            visited.add(table_id)
            recursion_stack.add(table_id)
            
            definition = self.loot_tables[table_id]
            
            for entry in definition.entries:
                # 1. Check Reference Validity
                if entry.entry_type == LootEntryType.ITEM:
                    if entry.entry_id not in self.items:
                        raise DataValidationError(
                            f"Loot table '{table_id}' references non-existent Item '{entry.entry_id}'",
                            data_type="LootTable", field_name="entry_id", invalid_id=entry.entry_id
                        )
                elif entry.entry_type == LootEntryType.TABLE:
                    if entry.entry_id not in self.loot_tables:
                        raise DataValidationError(
                            f"Loot table '{table_id}' references non-existent Table '{entry.entry_id}'",
                            data_type="LootTable", field_name="entry_id", invalid_id=entry.entry_id
                        )
                    
                    # 2. Check Cycle (DFS)
                    if entry.entry_id in recursion_stack:
                        raise DataValidationError(
                            f"Circular dependency detected in loot tables: {table_id} -> {entry.entry_id}",
                            data_type="LootTable", field_name="entry_id", invalid_id=entry.entry_id
                        )
                    
                    if entry.entry_id not in visited:
                        dfs_check_cycles(entry.entry_id)
            
            recursion_stack.remove(table_id)

        # Run DFS on all tables
        for tid in self.loot_tables:
            if tid not in visited:
                dfs_check_cycles(tid)

    # Accessor
    def get_loot_table(self, table_id: str) -> LootTableDefinition:
        if not self._is_initialized:
            raise RuntimeError("GameDataProvider not initialized")
        return self.loot_tables.get(table_id)
```

### F. `tests/test_loot_validation.py`
**Path:** `tests/test_loot_validation.py`
**Context:** Verify the DAG algorithm catches cycles.

```python
import pytest
from unittest.mock import MagicMock
from src.data.game_data_provider import GameDataProvider
from src.data.typed_models import DataValidationError

class TestLootValidation:
    def test_circular_dependency_detection(self):
        """Test that A->B->A cycle raises ValidationError."""
        # Mock Data
        raw_data = {
            "items": {"dagger": {"item_id": "dagger"}}, 
            "loot_tables": [
                # Table A points to Table B
                {"table_id": "table_A", "entry_type": "Table", "entry_id": "table_B", "weight": "1", "min_count": "1", "max_count": "1", "drop_chance": "1"},
                # Table B points to Table A (CYCLE)
                {"table_id": "table_B", "entry_type": "Table", "entry_id": "table_A", "weight": "1", "min_count": "1", "max_count": "1", "drop_chance": "1"},
            ]
        }
        
        provider = GameDataProvider.__new__(GameDataProvider)
        provider._is_initialized = False
        
        # Manual injection to bypass file loading
        provider.items = {"dagger": MagicMock()} 
        provider._hydrate_data(raw_data)
        
        with pytest.raises(DataValidationError) as exc:
            provider._validate_loot_tables()
            
        assert "Circular dependency" in str(exc.value)
        assert "table_A" in str(exc.value)

    def test_valid_nested_structure(self):
        """Test that A->B->Item is valid."""
        raw_data = {
            "loot_tables": [
                {"table_id": "parent", "entry_type": "Table", "entry_id": "child", "weight": "1", "min_count": "1", "max_count": "1", "drop_chance": "1"},
                {"table_id": "child", "entry_type": "Item", "entry_id": "dagger", "weight": "1", "min_count": "1", "max_count": "1", "drop_chance": "1"},
            ]
        }

        provider = GameDataProvider.__new__(GameDataProvider)
        provider._is_initialized = False
        
        # Mock items
        provider.items = {"dagger": MagicMock()}
        
        # Hydrate & Validate
        provider._hydrate_data(raw_data)
        try:
            provider._validate_loot_tables()
        except DataValidationError:
            pytest.fail("Valid nested structure raised DataValidationError unexpectedly")

    def test_invalid_item_reference(self):
        """Test that referencing a non-existent item raises ValidationError."""
        raw_data = {
            "loot_tables": [
                {"table_id": "broken_table", "entry_type": "Item", "entry_id": "fake_sword", "weight": "1", "min_count": "1", "max_count": "1", "drop_chance": "1"},
            ]
        }

        provider = GameDataProvider.__new__(GameDataProvider)
        provider._is_initialized = False
        provider.items = {} # Empty items dict
        
        provider._hydrate_data(raw_data)
        
        with pytest.raises(DataValidationError) as exc:
            provider._validate_loot_tables()
            
        assert "references non-existent Item" in str(exc.value)
        assert "fake_sword" in str(exc.value)
```

---

## 🧪 Verification Steps

**1. Automated Tests**
Run the new validation test suite to ensure the Cycle Detection Algorithm works as expected:
```bash
python -m pytest tests/test_loot_validation.py
```

**2. Integration Check**
Run the dashboard or main simulation script. Because `GameDataProvider` validates on load, if the application starts without crashing, the empty `loot_tables.csv` (or the sample provided) was successfully parsed and validated.
```bash
# If this runs without error, validation passed
python run_simulation.py --quiet
```

## ⚠️ Rollback Plan
If this implementation causes critical failures:
1.  Delete: `data/loot_tables.csv`
2.  Delete: `tests/test_loot_validation.py`
3.  Revert changes in: `src/data/game_data_provider.py` (Remove `_validate_loot_tables` call and method)
4.  Revert changes in: `src/data/data_parser.py` (Remove `loot_tables` from file list)