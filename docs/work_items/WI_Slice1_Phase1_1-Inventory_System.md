# 🚀 Implementation Hand-off: Phase 1.1 - The Inventory System

**Related Work Item:** Phase 1.1 - The Inventory System

## 📦 File Manifest
| Action | File Path | Description |
| :--- | :--- | :--- |
| 🆕 Create | `src/core/inventory.py` | Core Inventory class with atomic equip/unequip logic |
| ✏️ Modify | `src/core/__init__.py` | Export Inventory class |
| 🆕 Create | `tests/test_inventory.py` | Unit tests for capacity, swapping, and persistence |

---

## 1️⃣ Configuration & Dependencies
*No new pip packages required.*

---

## 2️⃣ Code Changes

### A. `src/core/inventory.py`
**Path:** `src/core/inventory.py`
**Context:** New core system. Manages a list of Items and handles the logic of moving them to/from an Entity. Includes serialization logic.

```python
import logging
from typing import List, Optional, Dict, Any
from dataclasses import asdict

from src.core.models import Item, Entity, RolledAffix
from src.data.typed_models import ItemSlot

logger = logging.getLogger(__name__)

class Inventory:
    """
    Manages a collection of Items (backpack) and handles equipment operations.
    
    Features:
    - Capacity enforcement
    - Atomic equipment swapping
    - Serialization support
    """

    def __init__(self, capacity: int = 20):
        self.capacity = capacity
        self._items: List[Item] = []

    @property
    def items(self) -> List[Item]:
        """Return a copy of the item list."""
        return list(self._items)

    @property
    def count(self) -> int:
        """Current number of items in inventory."""
        return len(self._items)

    @property
    def is_full(self) -> bool:
        return self.count >= self.capacity

    def add_item(self, item: Item) -> bool:
        """
        Add an item to the inventory.
        
        Returns:
            True if added, False if inventory is full.
        """
        if self.is_full:
            logger.warning(f"Inventory full. Cannot add item: {item.name}")
            return False
        
        self._items.append(item)
        return True

    def remove_item(self, item_instance_id: str) -> Optional[Item]:
        """Remove and return an item by its instance ID."""
        for i, item in enumerate(self._items):
            if item.instance_id == item_instance_id:
                return self._items.pop(i)
        return None

    def get_item(self, item_instance_id: str) -> Optional[Item]:
        """Find an item by instance ID without removing it."""
        for item in self._items:
            if item.instance_id == item_instance_id:
                return item
        return None

    def get_items_by_slot(self, slot: ItemSlot) -> List[Item]:
        """Filter items by equipment slot (useful for UI)."""
        # Handle both Enum and String comparison since Item.slot is a string
        slot_val = slot.value if hasattr(slot, 'value') else str(slot)
        return [i for i in self._items if i.slot == slot_val]

    def equip_item(self, entity: Entity, item_instance_id: str) -> bool:
        """
        Equip an item from the inventory onto an entity.
        
        Handles the 'Swap' logic atomically:
        1. Removes new item from inventory.
        2. Unequips old item from entity (if any) into inventory.
        3. Equips new item to entity.
        
        Returns:
            True if successful, False if item not found.
        """
        # 1. Find the item in the bag
        item_to_equip = self.get_item(item_instance_id)
        if not item_to_equip:
            logger.error(f"Cannot equip: Item {item_instance_id} not found in inventory.")
            return False

        # 2. Determine the slot
        slot_key = item_to_equip.slot
        
        # 3. Check if slot is occupied on entity
        currently_equipped = entity.equipment.get(slot_key)

        # 4. Execute Swap
        # Remove new item FIRST to make space (if we were at capacity)
        self.remove_item(item_instance_id)

        if currently_equipped:
            # Move old item to bag
            # Since we just removed one, we guarantee space for the swap
            self._items.append(currently_equipped)
            # Remove from entity (strictly speaking not needed as equip_item overwrites, 
            # but good for clarity)
            pass 

        # Equip new item
        entity.equip_item(item_to_equip)
        
        logger.info(f"Equipped {item_to_equip.name} to {entity.name} (Swapped: {currently_equipped.name if currently_equipped else 'None'})")
        return True

    def unequip_item(self, entity: Entity, slot: str) -> bool:
        """
        Unequip an item from the entity into the inventory.
        
        Args:
            slot: The slot string (e.g. 'Weapon', 'Chest') matches Item.slot
        """
        if self.is_full:
            logger.warning("Cannot unequip: Inventory is full.")
            return False

        item = entity.equipment.get(slot)
        if not item:
            return False

        # Remove from entity
        del entity.equipment[slot]
        entity.recalculate_stats()

        # Add to inventory
        self._items.append(item)
        logger.info(f"Unequipped {item.name} from {entity.name}")
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize inventory state."""
        return {
            "capacity": self.capacity,
            "items": [asdict(item) for item in self._items]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Inventory":
        """Reconstruct inventory from dictionary."""
        inv = cls(capacity=data.get("capacity", 20))
        
        # Hydrate Items manually since Item is a dataclass without a from_dict
        raw_items = data.get("items", [])
        for raw_item in raw_items:
            # Reconstruct Affixes
            affixes = []
            for raw_affix in raw_item.get("affixes", []):
                affixes.append(RolledAffix(**raw_affix))
            
            # Reconstruct Item
            # We need to filter out 'affixes' from raw_item before passing to constructor
            # to avoid double-passing or type errors, then re-attach
            item_kwargs = {k: v for k, v in raw_item.items() if k != "affixes"}
            item = Item(affixes=affixes, **item_kwargs)
            inv._items.append(item)
            
        return inv
```

### B. `src/core/__init__.py`
**Path:** `src/core/__init__.py`
**Context:** Export the new class.

```python
# ... existing imports ...
from src.core.inventory import Inventory

# ... existing __all__ or just leave imports
__all__ = [
    # ... existing ...
    "Inventory"
]
```

### C. `tests/test_inventory.py`
**Path:** `tests/test_inventory.py`
**Context:** Unit tests verifying capacity, swapping logic, and persistence.

```python
import pytest
from src.core.inventory import Inventory
from src.core.models import Item, Entity, EntityStats, RolledAffix
from src.data.typed_models import ItemSlot

class TestInventory:
    
    @pytest.fixture
    def sword(self):
        return Item(
            instance_id="sword_1", base_id="base_sword", name="Iron Sword", 
            slot="Weapon", rarity="Common", quality_tier="Normal", quality_roll=1, 
            affixes=[]
        )

    @pytest.fixture
    def axe(self):
        return Item(
            instance_id="axe_1", base_id="base_axe", name="Iron Axe", 
            slot="Weapon", rarity="Common", quality_tier="Normal", quality_roll=1, 
            affixes=[]
        )

    @pytest.fixture
    def entity(self):
        return Entity("hero", EntityStats())

    def test_add_remove_item(self, sword):
        inv = Inventory(capacity=5)
        assert inv.count == 0
        
        # Add
        assert inv.add_item(sword) is True
        assert inv.count == 1
        assert inv.get_item("sword_1") == sword
        
        # Remove
        removed = inv.remove_item("sword_1")
        assert removed == sword
        assert inv.count == 0

    def test_capacity_limit(self, sword):
        inv = Inventory(capacity=1)
        inv.add_item(sword)
        
        # Try adding another
        axe = Item("axe", "base", "Axe", "Weapon", "Common", "Normal", 1)
        assert inv.add_item(axe) is False
        assert inv.count == 1

    def test_equip_empty_slot(self, inv=None, entity=None, sword=None):
        inv = Inventory()
        entity = Entity("hero", EntityStats())
        sword = Item("s1", "b1", "Sword", "Weapon", "C", "N", 1)
        
        inv.add_item(sword)
        
        success = inv.equip_item(entity, "s1")
        
        assert success is True
        assert inv.count == 0
        assert entity.equipment["Weapon"] == sword

    def test_equip_swap_logic(self):
        """Test swapping items, especially when inventory is full."""
        inv = Inventory(capacity=1)
        entity = Entity("hero", EntityStats())
        
        sword = Item("sword", "b", "Sword", "Weapon", "C", "N", 1)
        axe = Item("axe", "b", "Axe", "Weapon", "C", "N", 1)
        
        # Setup: Entity has Sword, Inventory has Axe (Full)
        entity.equip_item(sword)
        inv.add_item(axe)
        assert inv.is_full is True
        
        # Execute Swap: Equip Axe from bag
        success = inv.equip_item(entity, "axe")
        
        assert success is True
        
        # Verify Entity has Axe
        assert entity.equipment["Weapon"] == axe
        
        # Verify Inventory has Sword
        assert inv.count == 1
        assert inv.get_item("sword") is not None
        assert inv.get_item("axe") is None

    def test_unequip_item(self):
        inv = Inventory()
        entity = Entity("hero", EntityStats())
        sword = Item("sword", "b", "Sword", "Weapon", "C", "N", 1)
        
        entity.equip_item(sword)
        
        success = inv.unequip_item(entity, "Weapon")
        
        assert success is True
        assert "Weapon" not in entity.equipment
        assert inv.count == 1
        assert inv.get_item("sword") == sword

    def test_unequip_full_inventory_fails(self):
        inv = Inventory(capacity=0) # Full
        entity = Entity("hero", EntityStats())
        sword = Item("sword", "b", "Sword", "Weapon", "C", "N", 1)
        entity.equip_item(sword)
        
        success = inv.unequip_item(entity, "Weapon")
        
        assert success is False
        assert entity.equipment["Weapon"] == sword # Still equipped

    def test_serialization(self):
        inv = Inventory(capacity=10)
        affix = RolledAffix("dmg", "damage", "flat", "pool", "desc", 10, 10)
        item = Item("i1", "b1", "Name", "Weapon", "C", "N", 1, [affix])
        inv.add_item(item)
        
        data = inv.to_dict()
        
        # Reconstruct
        new_inv = Inventory.from_dict(data)
        
        assert new_inv.capacity == 10
        assert new_inv.count == 1
        loaded_item = new_inv.get_item("i1")
        assert loaded_item.name == "Name"
        assert len(loaded_item.affixes) == 1
        assert loaded_item.affixes[0].affix_id == "dmg"
```

---

## 🧪 Verification Steps

1.  **Run Unit Tests:**
    ```bash
    python -m pytest tests/test_inventory.py
    ```
2.  **Manual Verification:**
    This is a foundational system. It will be visually verifiable once we build the UI in Phase 1.3. For now, the atomic swap logic passing the test case `test_equip_swap_logic` is the critical success metric.

## ⚠️ Rollback Plan
If this fails:
1.  Delete `src/core/inventory.py`
2.  Delete `tests/test_inventory.py`