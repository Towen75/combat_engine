"""Unit tests for StateManager."""

import pytest
from unittest.mock import MagicMock
from src.models import Entity, EntityStats, EffectInstance
from src.state import StateManager, EntityState


@pytest.fixture
def state_manager():
    return StateManager()

@pytest.fixture
def entity():
    stats = EntityStats(max_health=100.0, max_resource=50.0)
    return Entity(id="test_entity", base_stats=stats)


class TestEntityState:
    def test_initialization(self, entity):
        """Test valid initialization."""
        state = EntityState(entity=entity, current_health=100.0)
        assert state.current_health == 100.0
        assert state.is_alive is True
        
    def test_validation_negative_health(self, entity):
        """Test that negative health is rejected."""
        with pytest.raises(ValueError):
            EntityState(entity=entity,current_health=-1.0)

    def test_auto_death_on_zero_health(self, entity):
        """Test that 0 health sets is_alive to False."""
        state = EntityState(entity=entity,current_health=0.0, is_alive=True)
        assert state.is_alive is False


class TestStateManager:
    
    def test_add_entity(self, state_manager, entity):
        """Test adding an entity initializes state correctly."""
        state_manager.add_entity(entity)
        assert "test_entity" in state_manager
        
        state = state_manager.get_state("test_entity")
        assert state.current_health == 100.0
        assert state.current_resource == 50.0

    def test_add_duplicate_entity_raises_error(self, state_manager, entity):
        """Test that adding duplicate entity raises ValueError."""
        state_manager.add_entity(entity)
        with pytest.raises(ValueError, match="already registered"):
            state_manager.add_entity(entity)

    def test_remove_entity(self, state_manager, entity):
        """Test removing entity clears state."""
        state_manager.add_entity(entity)
        state_manager.remove_entity(entity.id)
        assert "test_entity" not in state_manager
        
        with pytest.raises(KeyError):
            state_manager.get_state(entity.id)

    def test_remove_unknown_entity_raises_error(self, state_manager):
        """Test removing unknown entity raises KeyError."""
        with pytest.raises(KeyError, match="not registered"):
            state_manager.remove_entity("unknown")

    def test_apply_damage(self, state_manager, entity):
        """Test damage application logic."""
        state_manager.add_entity(entity)
        
        # Normal damage
        actual = state_manager.apply_damage(entity.id, 30.0)
        assert actual == 30.0
        assert state_manager.get_state(entity.id).current_health == 70.0
        
        # Lethal damage
        actual = state_manager.apply_damage(entity.id, 100.0)
        assert actual == 70.0 # Only dealt remaining health
        state = state_manager.get_state(entity.id)
        assert state.current_health == 0.0
        assert state.is_alive is False

    def test_apply_damage_unregistered(self, state_manager):
        """Test apply_damage on unregistered entity raises KeyError."""
        with pytest.raises(KeyError, match="not registered"):
            state_manager.apply_damage("unknown", 10.0)

    def test_apply_effect(self, state_manager, entity):
        """Test applying an EffectInstance."""
        state_manager.add_entity(entity)
        
        effect = EffectInstance(
            id="eff1", definition_id="poison", source_id="src",
            time_remaining=10.0, tick_interval=1.0, stacks=1
        )
        
        result = state_manager.apply_effect(entity.id, effect)
        assert result["success"] is True
        assert result["action"] == "applied"
        
        effects = state_manager.iter_effects(entity.id)
        assert len(effects) == 1
        assert effects[0].definition_id == "poison"

    def test_update_processes_ticks(self, state_manager, entity):
        """Test that update() triggers effect ticks."""
        state_manager.add_entity(entity)
        
        # Apply a damaging effect
        effect = EffectInstance(
            id="eff1", definition_id="poison", source_id="src",
            time_remaining=5.0, tick_interval=1.0, stacks=1, value=10.0
        )
        state_manager.apply_effect(entity.id, effect)
        
        # Simulate 1.0 second (should trigger 1 tick of 10 damage)
        state_manager.update(1.0)
        
        state = state_manager.get_state(entity.id)
        assert state.current_health == 90.0 # 100 - 10
        assert state.active_debuffs == {} # Ensure old debuff dict is ignored if using new system

    def test_reset_system(self, state_manager, entity):
        """Test that reset clears everything."""
        state_manager.add_entity(entity)
        state_manager.reset_system()
        
        assert len(state_manager) == 0
        with pytest.raises(KeyError):
            state_manager.get_state(entity.id)