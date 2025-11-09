"""Unit tests for state management (EntityState and StateManager)."""

import pytest
from src.models import Entity, EntityStats
from src.state import EntityState, StateManager


class TestEntityState:
    """Test the EntityState dataclass."""

    def test_entity_state_creation_alive(self):
        """Test creating an EntityState for a living entity."""
        state = EntityState(current_health=100.0, is_alive=True)
        assert state.current_health == 100.0
        assert state.is_alive is True

    def test_entity_state_creation_dead(self):
        """Test creating an EntityState for a dead entity."""
        state = EntityState(current_health=0.0, is_alive=False)
        assert state.current_health == 0.0
        assert state.is_alive is False

    def test_entity_state_validation_negative_health(self):
        """Test that negative current_health raises ValueError."""
        with pytest.raises(ValueError, match="current_health cannot be negative"):
            EntityState(current_health=-10.0)

    def test_entity_state_auto_correct_dead(self):
        """Test that zero health automatically sets is_alive to False."""
        state = EntityState(current_health=0.0, is_alive=True)
        assert state.current_health == 0.0
        assert state.is_alive is False


class TestStateManager:
    """Test the StateManager class."""

    def test_state_manager_initialization(self):
        """Test that StateManager starts empty."""
        manager = StateManager()
        assert len(manager) == 0
        assert manager.get_all_states() == {}

    def test_register_entity_success(self):
        """Test successful entity registration."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", stats=stats)

        manager.register_entity(entity)

        assert len(manager) == 1
        assert "test_entity" in manager
        assert manager.is_registered("test_entity")

        state = manager.get_state("test_entity")
        assert state is not None
        assert state.current_health == 100.0
        assert state.is_alive is True

    def test_register_entity_duplicate(self):
        """Test that registering the same entity twice raises ValueError."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", stats=stats)

        manager.register_entity(entity)

        with pytest.raises(ValueError, match="Entity 'test_entity' is already registered"):
            manager.register_entity(entity)

    def test_unregister_entity_success(self):
        """Test successful entity unregistration."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", stats=stats)

        manager.register_entity(entity)
        assert len(manager) == 1

        manager.unregister_entity("test_entity")
        assert len(manager) == 0
        assert "test_entity" not in manager
        assert not manager.is_registered("test_entity")

    def test_unregister_entity_not_registered(self):
        """Test that unregistering a non-registered entity raises KeyError."""
        manager = StateManager()

        with pytest.raises(KeyError, match="Entity 'unknown' is not registered"):
            manager.unregister_entity("unknown")

    def test_get_state_unregistered_entity(self):
        """Test that getting state of unregistered entity returns None."""
        manager = StateManager()

        state = manager.get_state("unknown")
        assert state is None

    def test_apply_damage_normal(self):
        """Test applying damage less than current health."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", stats=stats)

        manager.register_entity(entity)
        damage_applied = manager.apply_damage("test_entity", 30.0)

        assert damage_applied == 30.0
        state = manager.get_state("test_entity")
        assert state is not None
        assert state.current_health == 70.0
        assert state.is_alive is True

    def test_apply_damage_exact_death(self):
        """Test applying damage exactly equal to current health."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", stats=stats)

        manager.register_entity(entity)
        damage_applied = manager.apply_damage("test_entity", 100.0)

        assert damage_applied == 100.0
        state = manager.get_state("test_entity")
        assert state is not None
        assert state.current_health == 0.0
        assert state.is_alive is False

    def test_apply_damage_to_dead_entity(self):
        """Test that damage to dead entities does nothing."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", stats=stats)

        manager.register_entity(entity)
        manager.apply_damage("test_entity", 100.0)  # Kill the entity

        damage_applied = manager.apply_damage("test_entity", 50.0)
        assert damage_applied == 0.0

        state = manager.get_state("test_entity")
        assert state is not None
        assert state.current_health == 0.0
        assert state.is_alive is False

    def test_apply_damage_unregistered_entity(self):
        """Test that damage to unregistered entities does nothing."""
        manager = StateManager()

        damage_applied = manager.apply_damage("unknown", 50.0)
        assert damage_applied == 0.0

    def test_apply_damage_negative_damage(self):
        """Test that negative damage raises ValueError."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", stats=stats)

        manager.register_entity(entity)

        with pytest.raises(ValueError, match="Damage cannot be negative"):
            manager.apply_damage("test_entity", -10.0)

    def test_heal_entity_normal(self):
        """Test healing an entity."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", stats=stats)

        manager.register_entity(entity)
        manager.apply_damage("test_entity", 50.0)  # Health now 50

        healing_applied = manager.heal_entity("test_entity", 25.0, 100.0)

        assert healing_applied == 25.0
        state = manager.get_state("test_entity")
        assert state is not None
        assert state.current_health == 75.0
        assert state.is_alive is True

    def test_heal_entity_over_max(self):
        """Test healing beyond max health caps at max."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", stats=stats)

        manager.register_entity(entity)
        manager.apply_damage("test_entity", 20.0)  # Health now 80

        healing_applied = manager.heal_entity("test_entity", 50.0, 100.0)

        assert healing_applied == 20.0  # Only healed to max
        state = manager.get_state("test_entity")
        assert state is not None
        assert state.current_health == 100.0
        assert state.is_alive is True

    def test_heal_entity_dead(self):
        """Test that healing dead entities does nothing."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", stats=stats)

        manager.register_entity(entity)
        manager.apply_damage("test_entity", 100.0)  # Kill the entity

        healing_applied = manager.heal_entity("test_entity", 50.0, 100.0)
        assert healing_applied == 0.0

    def test_heal_entity_unregistered(self):
        """Test that healing unregistered entities does nothing."""
        manager = StateManager()

        healing_applied = manager.heal_entity("unknown", 50.0, 100.0)
        assert healing_applied == 0.0

    def test_heal_entity_negative_healing(self):
        """Test that negative healing raises ValueError."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", stats=stats)

        manager.register_entity(entity)

        with pytest.raises(ValueError, match="Healing cannot be negative"):
            manager.heal_entity("test_entity", -10.0, 100.0)

    def test_get_all_states(self):
        """Test getting all states returns a copy."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)

        entity1 = Entity(id="entity1", stats=stats)
        entity2 = Entity(id="entity2", stats=stats)

        manager.register_entity(entity1)
        manager.register_entity(entity2)

        all_states = manager.get_all_states()
        assert len(all_states) == 2
        assert "entity1" in all_states
        assert "entity2" in all_states

        # Verify it's a copy (modifying it doesn't affect original)
        all_states["entity1"].current_health = 50.0
        original_state = manager.get_state("entity1")
        assert original_state is not None
        assert original_state.current_health == 100.0

    def test_reset(self):
        """Test resetting the state manager."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", stats=stats)

        manager.register_entity(entity)
        assert len(manager) == 1

        manager.reset()
        assert len(manager) == 0
        assert not manager.is_registered("test_entity")

    def test_len_and_contains(self):
        """Test __len__ and __contains__ methods."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", stats=stats)

        assert len(manager) == 0
        assert "test_entity" not in manager

        manager.register_entity(entity)

        assert len(manager) == 1
        assert "test_entity" in manager
        assert "unknown" not in manager
