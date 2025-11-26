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
            # Reconstruct Affixes (filter out auto-generated fields that start with underscore)
            affixes = []
            for raw_affix in raw_item.get("affixes", []):
                affix_kwargs = {k: v for k, v in raw_affix.items() if not k.startswith('_')}
                affixes.append(RolledAffix(**affix_kwargs))

            # Reconstruct Item
            # We need to filter out 'affixes' from raw_item before passing to constructor
            # to avoid double-passing or type errors, then re-attach
            item_kwargs = {k: v for k, v in raw_item.items() if k != "affixes"}
            item = Item(affixes=affixes, **item_kwargs)
            inv._items.append(item)

        return inv
