"""Unit tests for typed models and normalization logic."""

import pytest
from src.data.typed_models import (
    normalize_enum, 
    ItemSlot, 
    DamageType, 
    Rarity, 
    EffectType, 
    DataValidationError,
    validate_entity_stats_are_valid
)
from src.models import EntityStats

class TestEnumNormalization:
    """Test the enum normalization and mapping logic."""

    def test_standard_normalization(self):
        """Test case-insensitive matching."""
        assert normalize_enum(ItemSlot, "weapon") == ItemSlot.WEAPON
        assert normalize_enum(ItemSlot, "WEAPON") == ItemSlot.WEAPON
        assert normalize_enum(ItemSlot, "  Weapon  ") == ItemSlot.WEAPON

    def test_legacy_mappings_item_slots(self):
        """Test legacy mappings for ItemSlots."""
        # Specific mappings defined in typed_models.py
        assert normalize_enum(ItemSlot, "pants") == ItemSlot.LEGS
        assert normalize_enum(ItemSlot, "helmet") == ItemSlot.HEAD
        assert normalize_enum(ItemSlot, "helm") == ItemSlot.HEAD
        assert normalize_enum(ItemSlot, "off-hand") == ItemSlot.OFF_HAND
        assert normalize_enum(ItemSlot, "shield") == ItemSlot.OFF_HAND
        assert normalize_enum(ItemSlot, "jewelry") == ItemSlot.ACCESSORY
        assert normalize_enum(ItemSlot, "boots") == ItemSlot.FEET
        assert normalize_enum(ItemSlot, "gloves") == ItemSlot.HANDS
        assert normalize_enum(ItemSlot, "armor") == ItemSlot.CHEST

    def test_damage_type_mappings(self):
        """Test damage type normalization."""
        assert normalize_enum(DamageType, "physical") == DamageType.PHYSICAL
        assert normalize_enum(DamageType, "fire") == DamageType.FIRE
        assert normalize_enum(DamageType, "acid") == DamageType.ACID

    def test_effect_type_normalization(self):
        """Test effect type normalization."""
        assert normalize_enum(EffectType, "buff") == EffectType.BUFF
        assert normalize_enum(EffectType, "DoT") == EffectType.DOT
        assert normalize_enum(EffectType, "stun") == EffectType.STUN

    def test_rarity_normalization(self):
        """Test rarity normalization."""
        assert normalize_enum(Rarity, "common") == Rarity.COMMON
        assert normalize_enum(Rarity, "Legendary") == Rarity.LEGENDARY

    def test_invalid_enum_raises_error(self):
        """Test that invalid values raise ValueError."""
        with pytest.raises(ValueError, match="Invalid ItemSlot"):
            normalize_enum(ItemSlot, "NotASlot")
            
    def test_empty_value_raises_error(self):
        """Test empty values raise ValueError."""
        with pytest.raises(ValueError):
            normalize_enum(ItemSlot, "")
        with pytest.raises(ValueError):
            normalize_enum(ItemSlot, None)
            
    def test_default_value_fallback(self):
        """Test that default value is returned if provided for invalid/empty input."""
        # Note: The implementation throws ValueError on empty even with default, 
        # but handles invalid values if default provided? 
        # Actually, looking at code: `if not value: if default... return default`
        assert normalize_enum(ItemSlot, "", default=ItemSlot.WEAPON) == ItemSlot.WEAPON
        assert normalize_enum(ItemSlot, None, default=ItemSlot.WEAPON) == ItemSlot.WEAPON


class TestValidationHelpers:
    """Test validation helper functions."""
    
    def test_validate_entity_stats_valid(self):
        """Test validation with valid stats."""
        valid_stats = ["base_damage", "max_health", "crit_chance"]
        # Should not raise exception
        validate_entity_stats_are_valid(valid_stats)
        
    def test_validate_entity_stats_invalid(self):
        """Test validation with invalid stats."""
        invalid_stats = ["base_damage", "fake_stat"]
        
        with pytest.raises(DataValidationError) as excinfo:
            validate_entity_stats_are_valid(invalid_stats)
        
        assert "Invalid stat name 'fake_stat'" in str(excinfo.value)
        assert excinfo.value.data_type == "EntityStats"