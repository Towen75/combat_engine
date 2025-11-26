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
