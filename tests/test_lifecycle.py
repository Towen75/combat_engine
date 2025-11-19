"""Unit tests for Entity Lifecycle Management."""

import pytest
from unittest.mock import MagicMock
from src.core.models import Entity, EntityStats
from src.core.state import StateManager
from src.core.events import EventBus, EntitySpawnEvent, EntityDeathEvent, EntityDespawnEvent, EntityActivateEvent

class TestEntityLifecycle:
    
    @pytest.fixture
    def event_bus(self):
        return EventBus()
        
    @pytest.fixture
    def state_manager(self, event_bus):
        return StateManager(event_bus=event_bus)
        
    @pytest.fixture
    def entity(self):
        return Entity("hero", EntityStats(max_health=100.0))

    def test_spawn_event_on_add(self, state_manager, event_bus, entity):
        """Test that adding an entity fires EntitySpawnEvent."""
        received = []
        event_bus.subscribe(EntitySpawnEvent, lambda e: received.append(e))
        
        state_manager.add_entity(entity)
        
        assert len(received) == 1
        assert received[0].entity == entity
        
    def test_activate_event(self, state_manager, event_bus, entity):
        """Test that activating an entity fires EntityActivateEvent."""
        state_manager.add_entity(entity)
        
        received = []
        event_bus.subscribe(EntityActivateEvent, lambda e: received.append(e))
        
        state_manager.activate_entity(entity.id)
        
        assert len(received) == 1
        assert received[0].entity == entity

    def test_death_event_on_lethal_damage(self, state_manager, event_bus, entity):
        """Test that lethal damage fires EntityDeathEvent exactly once."""
        state_manager.add_entity(entity)
        
        received = []
        event_bus.subscribe(EntityDeathEvent, lambda e: received.append(e))
        
        # Non-lethal damage
        state_manager.apply_damage(entity.id, 50.0)
        assert len(received) == 0
        assert state_manager.get_is_alive(entity.id) is True
        
        # Lethal damage
        state_manager.apply_damage(entity.id, 60.0)
        assert len(received) == 1
        assert received[0].entity_id == entity.id
        assert state_manager.get_is_alive(entity.id) is False
        
        # Overkill damage (should not fire death event again)
        state_manager.apply_damage(entity.id, 10.0)
        assert len(received) == 1

    def test_despawn_event_on_remove(self, state_manager, event_bus, entity):
        """Test that removing an entity fires EntityDespawnEvent."""
        state_manager.add_entity(entity)
        
        received = []
        event_bus.subscribe(EntityDespawnEvent, lambda e: received.append(e))
        
        state_manager.remove_entity(entity.id)
        
        assert len(received) == 1
        assert received[0].entity_id == entity.id