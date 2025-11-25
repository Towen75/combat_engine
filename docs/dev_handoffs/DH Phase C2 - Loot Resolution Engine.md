# 🚀 Implementation Hand-off: Phase C2 - Loot Resolution Engine

**Related Work Item:** Phase C2 - Loot Resolution Engine (Revised)

## 📦 File Manifest
| Action | File Path | Description |
| :--- | :--- | :--- |
| 🆕 Create | `src/core/loot_manager.py` | Core logic for weighted tables and recursion |
| ✏️ Modify | `src/core/__init__.py` | Export LootManager |
| 🆕 Create | `tests/test_loot_manager.py` | Unit tests for determinism and recursion |

---

## 1️⃣ Configuration & Dependencies
*No new pip packages required.*

---

## 2️⃣ Code Changes

### A. `src/core/loot_manager.py`
**Path:** `src/core/loot_manager.py`
**Context:** The core engine for resolving loot tables into Item lists. Implements weighted choice, recursion limits, and RNG injection.

```python
import logging
from typing import List, Optional
from src.core.models import Item
from src.core.rng import RNG
from src.data.game_data_provider import GameDataProvider
from src.data.typed_models import LootEntryType, LootTableEntry
from src.utils.item_generator import ItemGenerator

logger = logging.getLogger(__name__)

class LootManager:
    """
    Manages the generation of loot from weighted tables.
    
    Handles:
    - Weighted probability selection
    - Recursive table traversal
    - Quantity randomization
    - Deterministic RNG usage
    """
    
    MAX_RECURSION_DEPTH = 10
    MAX_TOTAL_ITEMS = 50  # Safety cap to prevent explosive item generation

    def __init__(
        self, 
        provider: GameDataProvider, 
        item_generator: ItemGenerator, 
        rng: RNG
    ):
        """
        Initialize the LootManager.
        
        Args:
            provider: Data provider for LootTableDefinitions.
            item_generator: Generator for creating Item instances.
            rng: Seeded RNG for deterministic drops.
        """
        self.provider = provider
        self.item_gen = item_generator
        self.rng = rng

    def roll_loot(self, table_id: str) -> List[Item]:
        """
        Generate a list of items from the specified loot table.
        
        Args:
            table_id: The ID of the loot table to roll on.
            
        Returns:
            List of generated Item objects.
            
        Raises:
            ValueError: If table_id does not exist.
        """
        results: List[Item] = []
        self._roll_recursive(table_id, results, depth=0)
        return results

    def _roll_recursive(self, table_id: str, results: List[Item], depth: int) -> None:
        """Internal recursive resolver."""
        # 1. Safety Checks
        if depth > self.MAX_RECURSION_DEPTH:
            logger.warning(f"Loot recursion depth limit ({self.MAX_RECURSION_DEPTH}) hit at table '{table_id}'")
            return

        if len(results) >= self.MAX_TOTAL_ITEMS:
            return

        # 2. Validation
        # GameDataProvider.loot_tables is a dict of definitions
        # We need to access the underlying dict directly or via a getter if available
        # Assuming direct access based on C1 implementation
        table_def = self.provider.loot_tables.get(table_id)
        
        if not table_def:
            raise ValueError(f"Loot table '{table_id}' not found in Game Data.")

        # 3. Filter Candidates (Drop Chance)
        candidates = []
        for entry in table_def.entries:
            # Independent probability check: Does this entry enter the pool?
            if entry.drop_chance >= 1.0 or self.rng.roll(entry.drop_chance):
                candidates.append(entry)

        if not candidates:
            return

        # 4. Weighted Selection
        # Logic: Pick ONE entry from the valid candidates based on weight
        weights = [e.weight for e in candidates]
        if sum(weights) == 0:
            return

        selected_entry: LootTableEntry = self.rng.weighted_choice(candidates, weights)

        # 5. Quantity Resolution
        # How many times do we trigger this result?
        count = 1
        if selected_entry.min_count < selected_entry.max_count:
            count = self.rng.randint(selected_entry.min_count, selected_entry.max_count)
        else:
            count = selected_entry.min_count

        # 6. Execution
        for _ in range(count):
            if len(results) >= self.MAX_TOTAL_ITEMS:
                logger.warning(f"Loot item limit ({self.MAX_TOTAL_ITEMS}) hit processing table '{table_id}'")
                break

            if selected_entry.entry_type == LootEntryType.ITEM:
                item = self.item_gen.generate(selected_entry.entry_id)
                results.append(item)
            
            elif selected_entry.entry_type == LootEntryType.TABLE:
                self._roll_recursive(selected_entry.entry_id, results, depth + 1)
```

### B. `src/core/__init__.py`
**Path:** `src/core/__init__.py`
**Context:** Export the new class.

```python
# Append to existing imports
from src.core.loot_manager import LootManager

__all__.append("LootManager")
```

### C. `tests/test_loot_manager.py`
**Path:** `tests/test_loot_manager.py`
**Context:** Verifies determinism, math, and safety features.

```python
import pytest
from unittest.mock import MagicMock
from src.core.rng import RNG
from src.core.loot_manager import LootManager
from src.data.typed_models import LootTableDefinition, LootTableEntry, LootEntryType
from src.core.models import Item

class TestLootManager:
    
    @pytest.fixture
    def mock_provider(self):
        provider = MagicMock()
        provider.loot_tables = {}
        return provider

    @pytest.fixture
    def mock_item_gen(self):
        gen = MagicMock()
        # When generate is called, return a dummy Item with the ID as name
        gen.generate.side_effect = lambda item_id: Item(
            instance_id="inst", base_id=item_id, name=item_id, 
            slot="weapon", rarity="Common", quality_tier="Normal", quality_roll=1
        )
        return gen

    @pytest.fixture
    def rng(self):
        return RNG(seed=42)

    def test_missing_table_raises_error(self, mock_provider, mock_item_gen, rng):
        manager = LootManager(mock_provider, mock_item_gen, rng)
        with pytest.raises(ValueError, match="not found"):
            manager.roll_loot("missing_table")

    def test_weighted_selection_determinism(self, mock_provider, mock_item_gen, rng):
        """Test that seeds produce consistent item picks."""
        # Setup: Table with two items, 50/50 weight
        entry_a = LootTableEntry("t1", LootEntryType.ITEM, "item_a", 50, 1, 1, 1.0)
        entry_b = LootTableEntry("t1", LootEntryType.ITEM, "item_b", 50, 1, 1, 1.0)
        
        table = LootTableDefinition("t1", entries=[entry_a, entry_b])
        mock_provider.loot_tables = {"t1": table}
        
        manager = LootManager(mock_provider, mock_item_gen, rng)
        
        # Run 1: Seed 42
        result_1 = manager.roll_loot("t1")[0].name
        
        # Run 2: Reset Seed 42
        rng_2 = RNG(seed=42)
        manager_2 = LootManager(mock_provider, mock_item_gen, rng_2)
        result_2 = manager_2.roll_loot("t1")[0].name
        
        assert result_1 == result_2

    def test_recursive_table_resolution(self, mock_provider, mock_item_gen, rng):
        """Test Table A -> Table B -> Item logic."""
        # Table B drops Item X
        entry_x = LootTableEntry("table_b", LootEntryType.ITEM, "item_x", 1, 1, 1, 1.0)
        table_b = LootTableDefinition("table_b", entries=[entry_x])
        
        # Table A drops Table B
        entry_b = LootTableEntry("table_a", LootEntryType.TABLE, "table_b", 1, 1, 1, 1.0)
        table_a = LootTableDefinition("table_a", entries=[entry_b])
        
        mock_provider.loot_tables = {"table_a": table_a, "table_b": table_b}
        
        manager = LootManager(mock_provider, mock_item_gen, rng)
        results = manager.roll_loot("table_a")
        
        assert len(results) == 1
        assert results[0].name == "item_x"

    def test_quantity_resolution(self, mock_provider, mock_item_gen, rng):
        """Test min_count and max_count."""
        # Entry drops 3-3 times (Fixed)
        entry = LootTableEntry("t1", LootEntryType.ITEM, "item_x", 1, 3, 3, 1.0)
        table = LootTableDefinition("t1", entries=[entry])
        mock_provider.loot_tables = {"t1": table}
        
        manager = LootManager(mock_provider, mock_item_gen, rng)
        results = manager.roll_loot("t1")
        
        assert len(results) == 3
        assert all(i.name == "item_x" for i in results)

    def test_drop_chance_filtering(self, mock_provider, mock_item_gen, rng):
        """Test that 0.0 drop chance prevents item from appearing."""
        # Entry A: 0% chance, Weight 1000
        # Entry B: 100% chance, Weight 1
        entry_a = LootTableEntry("t1", LootEntryType.ITEM, "item_a", 1000, 1, 1, 0.0)
        entry_b = LootTableEntry("t1", LootEntryType.ITEM, "item_b", 1, 1, 1, 1.0)
        
        table = LootTableDefinition("t1", entries=[entry_a, entry_b])
        mock_provider.loot_tables = {"t1": table}
        
        manager = LootManager(mock_provider, mock_item_gen, rng)
        results = manager.roll_loot("t1")
        
        # Despite high weight, A should never drop
        assert len(results) == 1
        assert results[0].name == "item_b"

    def test_safety_item_limit(self, mock_provider, mock_item_gen, rng):
        """Test MAX_TOTAL_ITEMS cap."""
        # Entry drops 100 items
        entry = LootTableEntry("t1", LootEntryType.ITEM, "item_x", 1, 100, 100, 1.0)
        table = LootTableDefinition("t1", entries=[entry])
        mock_provider.loot_tables = {"t1": table}
        
        manager = LootManager(mock_provider, mock_item_gen, rng)
        results = manager.roll_loot("t1")
        
        assert len(results) == 50  # Capped at default MAX_TOTAL_ITEMS
```

---

## 🧪 Verification Steps

**1. Automated Tests**
Run the new unit tests to verify logic and safety constraints:
```bash
python -m pytest tests/test_loot_manager.py
```

**2. Manual Verification**
You can create a temporary script `scripts/test_loot_drop.py`:
```python
from src.data.game_data_provider import GameDataProvider
from src.utils.item_generator import ItemGenerator
from src.core.loot_manager import LootManager
from src.core.rng import RNG

provider = GameDataProvider()
rng = RNG(42)
item_gen = ItemGenerator(provider, rng)
manager = LootManager(provider, item_gen, rng)

# Assuming 'forest_zone_loot' exists from C1
items = manager.roll_loot("forest_zone_loot")
print(f"Dropped {len(items)} items:")
for item in items:
    print(f"- {item.name} ({item.rarity})")
```

## ⚠️ Rollback Plan
If this implementation causes critical failures:
1.  Delete: `src/core/loot_manager.py`
2.  Delete: `tests/test_loot_manager.py`
3.  Revert: `src/core/__init__.py`