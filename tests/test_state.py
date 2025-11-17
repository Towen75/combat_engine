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

    def test_add_entity_success(self):
        """Test successful entity addition."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", base_stats=stats)

        manager.add_entity(entity)

        assert len(manager) == 1
        assert "test_entity" in manager
        assert manager.is_registered("test_entity")

        state = manager.get_state("test_entity")
        assert state is not None
        assert state.current_health == 100.0
        assert state.is_alive is True

    def test_add_entity_duplicate(self):
        """Test that adding the same entity twice raises ValueError."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", base_stats=stats)

        manager.add_entity(entity)

        with pytest.raises(ValueError, match="Entity 'test_entity' is already registered"):
            manager.add_entity(entity)

    def test_remove_entity_success(self):
        """Test successful entity removal."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", base_stats=stats)

        manager.add_entity(entity)
        assert len(manager) == 1

        manager.remove_entity("test_entity")
        assert len(manager) == 0
        assert "test_entity" not in manager
        assert not manager.is_registered("test_entity")

    def test_remove_entity_not_registered(self):
        """Test that removing a non-registered entity raises KeyError."""
        manager = StateManager()

        with pytest.raises(KeyError, match="Entity 'unknown' is not registered"):
            manager.remove_entity("unknown")

    def test_get_state_unregistered_entity(self):
        """Test that getting state of unregistered entity raises KeyError."""
        manager = StateManager()

        with pytest.raises(KeyError, match="Entity 'unknown' not registered - call add_entity\\(\\) first"):
            manager.get_state("unknown")

    def test_apply_damage_normal(self):
        """Test applying damage less than current health."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", base_stats=stats)

        manager.add_entity(entity)
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
        entity = Entity(id="test_entity", base_stats=stats)

        manager.add_entity(entity)
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
        entity = Entity(id="test_entity", base_stats=stats)

        manager.add_entity(entity)
        manager.apply_damage("test_entity", 100.0)  # Kill the entity

        damage_applied = manager.apply_damage("test_entity", 50.0)
        assert damage_applied == 0.0

        state = manager.get_state("test_entity")
        assert state is not None
        assert state.current_health == 0.0
        assert state.is_alive is False

    def test_apply_damage_unregistered_entity(self):
        """Test that damage to unregistered entities returns 0.0."""
        manager = StateManager()

        with pytest.raises(KeyError, match="Entity 'unknown' not registered"):
            manager.apply_damage("unknown", 50.0)

    def test_apply_damage_negative_damage(self):
        """Test that negative damage is ignored (returns 0.0)."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", base_stats=stats)

        manager.add_entity(entity)
        original_health = 100.0

        damage_applied = manager.apply_damage("test_entity", -10.0)
        assert damage_applied == 0.0

        state = manager.get_state("test_entity")
        assert state is not None
        assert state.current_health == original_health  # Health unchanged

    def test_set_health(self):
        """Test setting entity health directly."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", base_stats=stats)

        manager.add_entity(entity)

        # Set health to specific value
        manager.set_health("test_entity", 75.0)
        state = manager.get_state("test_entity")
        assert state.current_health == 75.0
        assert state.is_alive is True

        # Set health to 0 (should mark as dead)
        manager.set_health("test_entity", 0.0)
        state = manager.get_state("test_entity")
        assert state.current_health == 0.0
        assert state.is_alive is False

    def test_set_resource(self):
        """Test setting entity resource directly."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", base_stats=stats)

        manager.add_entity(entity)

        # Set resource to specific value
        manager.set_resource("test_entity", 50.0)
        assert manager.get_current_resource("test_entity") == 50.0

        # Try to set above max (should clamp)
        manager.set_resource("test_entity", 150.0)
        assert manager.get_current_resource("test_entity") == 100.0

        # Try to set below 0 (should clamp)
        manager.set_resource("test_entity", -10.0)
        assert manager.get_current_resource("test_entity") == 0.0

    def test_set_cooldown(self):
        """Test setting skill cooldowns."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", base_stats=stats)

        manager.add_entity(entity)

        # Set cooldown
        manager.set_cooldown("test_entity", "fireball", 3.5)
        assert manager.get_cooldown_remaining("test_entity", "fireball") == 3.5

        # Set another cooldown
        manager.set_cooldown("test_entity", "heal", 1.0)
        assert manager.get_cooldown_remaining("test_entity", "heal") == 1.0
        assert manager.get_cooldown_remaining("test_entity", "fireball") == 3.5

    def test_get_cooldown_remaining(self):
        """Test getting cooldown remaining for skills."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", base_stats=stats)

        manager.add_entity(entity)

        # Test unset cooldown returns 0
        assert manager.get_cooldown_remaining("test_entity", "nonexistent") == 0.0

        # Set and get cooldown
        manager.set_cooldown("test_entity", "skill_1", 5.0)
        assert manager.get_cooldown_remaining("test_entity", "skill_1") == 5.0

    def test_iter_effects(self):
        """Test iterating over active effects."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", base_stats=stats)

        manager.add_entity(entity)

        # Initially should be empty
        assert list(manager.iter_effects("test_entity")) == []

        # Note: Testing effects would require EffectInstance - out of scope for now

    def test_reset_system(self):
        """Test resetting the state manager."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", base_stats=stats)

        manager.add_entity(entity)
        manager.set_health("test_entity", 50.0)
        manager.set_resource("test_entity", 75.0)
        manager.set_cooldown("test_entity", "skill", 2.0)

        assert len(manager) == 1
        assert manager.get_current_health("test_entity") == 50.0

        manager.reset_system()
        assert len(manager) == 0

        # Should not be able to access entity now
        with pytest.raises(KeyError):
            manager.get_state("test_entity")

    def test_len_and_contains(self):
        """Test __len__ and __contains__ methods."""
        manager = StateManager()
        stats = EntityStats(max_health=100.0)
        entity = Entity(id="test_entity", base_stats=stats)

        assert len(manager) == 0
        assert "test_entity" not in manager

        manager.add_entity(entity)

        assert len(manager) == 1
        assert "test_entity" in manager
        assert "unknown" not in manager
