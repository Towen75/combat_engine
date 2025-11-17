#!/usr/bin/env python3
"""
Test strict mode enforcement and legacy compatibility for PR8c migration.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models import Entity, EntityStats
from state import StateManager


def test_strict_mode_keyerror_unregistered_access():
    """Test that strict mode raises KeyError for unregistered entities."""
    print("Testing strict mode KeyError behavior...")

    manager = StateManager(strict_mode=True)

    # Test apply_damage to unregistered entity
    try:
        manager.apply_damage("unknown", 50.0)
        assert False, "Should have raised KeyError for unregistered entity"
    except KeyError as e:
        assert "not registered" in str(e)

    # Test apply_effect to unregistered entity - this requires mocking to avoid imports
    # We'll test the core strict_mode check

    # Test get_state on unregistered entity
    try:
        manager.get_state("unknown")
        assert False, "Should have raised KeyError for unregistered entity"
    except KeyError as e:
        assert "not registered" in str(e)

    # Test set_health on unregistered entity
    try:
        manager.set_health("unknown", 50.0)
        assert False, "Should have raised KeyError for unregistered entity"
    except KeyError as e:
        assert "not registered" in str(e)

    print("✅ Strict mode enforcement verified")


def test_strict_mode_disabled_behavior():
    """Test behavior when strict mode is disabled."""
    print("Testing non-strict mode behavior...")

    manager = StateManager(strict_mode=False)

    # In non-strict mode, get_state still requires registration
    # because all methods call get_state()
    try:
        manager.apply_damage("unknown", 50.0)
        assert False, "Should have raised KeyError even in non-strict mode"
    except KeyError as e:
        assert "not registered" in str(e)

    print("✅ Non-strict mode behaves correctly (all modes require registration)")


def test_legacy_compatibility_methods():
    """Test that legacy compatibility methods work through new API."""
    print("Testing legacy compatibility methods...")

    manager = StateManager()

    # Create a test entity
    stats = EntityStats(max_health=100.0)
    entity = Entity(id="test_entity", base_stats=stats)

    # Test register_entity (legacy method)
    manager.register_entity(entity)
    assert manager.is_registered("test_entity")
    assert manager.get_current_health("test_entity") == 100.0

    # Test legacy tick method (delegates to update)
    initial_health = manager.get_current_health("test_entity")
    manager.tick(1.0)  # Should work without error
    assert manager.get_current_health("test_entity") == initial_health  # Health unchanged

    # Test unregister_entity (legacy method)
    manager.unregister_entity("test_entity")
    assert not manager.is_registered("test_entity")

    # Test get_all_states (legacy method)
    all_states = manager.get_all_states()
    assert isinstance(all_states, dict)
    assert len(all_states) == 0  # No entities

    print("✅ Legacy compatibility methods working")


def test_legacy_methods_with_strict_mode():
    """Test legacy methods work correctly in strict mode."""
    print("Testing legacy methods with strict mode enabled...")

    manager = StateManager(strict_mode=True)

    stats = EntityStats(max_health=100.0)
    entity = Entity(id="test_entity", base_stats=stats)

    # Legacy register method should work
    manager.register_entity(entity)
    assert manager.is_registered("test_entity")

    # Legacy tick method should work
    manager.tick(0.5)

    # Legacy unregister should work
    manager.unregister_entity("test_entity")
    assert not manager.is_registered("test_entity")

    print("✅ Legacy methods work with strict mode")


def test_state_management_edge_cases():
    """Test edge cases in state management."""
    print("Testing state management edge cases...")

    manager = StateManager()

    # Create entity
    stats = EntityStats(max_health=100.0)
    entity = Entity(id="test_entity", base_stats=stats)
    manager.add_entity(entity)

    # Test setting health to negative (should clamp to 0)
    manager.set_health("test_entity", -10.0)
    assert manager.get_current_health("test_entity") == 0.0
    assert not manager.get_is_alive("test_entity")

    # Recreate entity for next test
    manager.add_entity(entity)

    # Test resource clamping
    manager.set_resource("test_entity", 150.0)  # Above max
    assert manager.get_current_resource("test_entity") == 100.0

    manager.set_resource("test_entity", -10.0)  # Below 0
    assert manager.get_current_resource("test_entity") == 0.0

    print("✅ Edge case handling verified")


def test_manager_creation_and_len():
    """Test basic StateManager creation and length tracking."""
    print("Testing StateManager creation and length...")

    manager = StateManager()
    assert len(manager) == 0
    assert "unknown" not in manager

    # Add entity and verify length
    stats = EntityStats(max_health=100.0)
    entity = Entity(id="test_entity", base_stats=stats)
    manager.add_entity(entity)

    assert len(manager) == 1
    assert "test_entity" in manager
    assert "unknown" not in manager

    print("✅ StateManager basics verified")


if __name__ == "__main__":
    print("=== PR8c Strict Mode Verification Tests ===\n")

    test_strict_mode_keyerror_unregistered_access()
    test_strict_mode_disabled_behavior()
    test_legacy_compatibility_methods()
    test_legacy_methods_with_strict_mode()
    test_state_management_edge_cases()
    test_manager_creation_and_len()

    print("\n🎉 All PR8c verification tests passed!")
