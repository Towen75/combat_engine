"""
Unit tests for StateManager strict mode and legacy compatibility.
Converted from test_strict_mode.py to standard pytest format.
"""

import pytest
from src.models import Entity, EntityStats
from src.state import StateManager


def test_strict_mode_keyerror_unregistered_access():
    """Test that strict mode raises KeyError for unregistered entities."""
    manager = StateManager(strict_mode=True)

    # Test apply_damage to unregistered entity
    with pytest.raises(KeyError, match="not registered"):
        manager.apply_damage("unknown", 50.0)

    # Test get_state on unregistered entity
    with pytest.raises(KeyError, match="not registered"):
        manager.get_state("unknown")

    # Test set_health on unregistered entity
    with pytest.raises(KeyError, match="not registered"):
        manager.set_health("unknown", 50.0)


def test_strict_mode_disabled_behavior():
    """Test behavior when strict mode is disabled."""
    manager = StateManager(strict_mode=False)

    # Even in non-strict mode, operations that rely on entity state 
    # (like apply_damage) must raise KeyError if the entity doesn't exist
    # to prevent silent failures or data corruption.
    with pytest.raises(KeyError, match="not registered"):
        manager.apply_damage("unknown", 50.0)


def test_legacy_compatibility_methods():
    """Test that legacy compatibility methods work through new API."""
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


def test_legacy_methods_with_strict_mode():
    """Test legacy methods work correctly in strict mode."""
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


def test_state_management_edge_cases():
    """Test edge cases in state management."""
    manager = StateManager()

    # Create entity
    stats = EntityStats(max_health=100.0)
    entity = Entity(id="test_entity", base_stats=stats)
    manager.add_entity(entity)

    # Test setting health to negative (should clamp to 0)
    manager.set_health("test_entity", -10.0)
    assert manager.get_current_health("test_entity") == 0.0
    assert not manager.get_is_alive("test_entity")

    # Reset for next test
    manager.set_health("test_entity", 100.0)
    assert manager.get_is_alive("test_entity")

    # Test resource clamping
    manager.set_resource("test_entity", 150.0)  # Above max (100)
    assert manager.get_current_resource("test_entity") == 100.0

    manager.set_resource("test_entity", -10.0)  # Below 0
    assert manager.get_current_resource("test_entity") == 0.0


def test_manager_creation_and_len():
    """Test basic StateManager creation and length tracking."""
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