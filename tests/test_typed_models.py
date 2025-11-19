import pytest
from src.data.typed_models import normalize_enum, ItemSlot, DamageType

class TestEnumNormalization:
    def test_standard_normalization(self):
        assert normalize_enum(ItemSlot, "weapon") == ItemSlot.WEAPON
        assert normalize_enum(ItemSlot, "WEAPON") == ItemSlot.WEAPON
    
    def test_legacy_mappings(self):
        assert normalize_enum(ItemSlot, "pants") == ItemSlot.LEGS
        assert normalize_enum(ItemSlot, "helmet") == ItemSlot.HEAD
        
    def test_damage_mappings(self):
        assert normalize_enum(DamageType, "physical") == DamageType.PHYSICAL
        assert normalize_enum(DamageType, "acid") == DamageType.ACID
        
    def test_invalid_raises_error(self):
        with pytest.raises(ValueError):
            normalize_enum(ItemSlot, "NotASlot")