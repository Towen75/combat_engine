import pytest
from unittest.mock import MagicMock
from src.core.events import EventBus, EntityDeathEvent, LootDroppedEvent
from src.core.state import StateManager
from src.core.models import Entity, EntityStats, Item
from src.handlers.loot_handler import LootHandler

class TestLootIntegration:

    @pytest.fixture
    def components(self):
        event_bus = EventBus()
        state_manager = StateManager(event_bus)
        loot_manager = MagicMock()

        # Setup mock items
        mock_item = Item("inst", "base", "Test Sword", "Weapon", "Common", "Normal", 1)
        loot_manager.roll_loot.return_value = [mock_item]

        handler = LootHandler(event_bus, state_manager, loot_manager)

        return event_bus, state_manager, loot_manager, handler

    def test_death_triggers_loot_drop(self, components):
        event_bus, state_manager, loot_manager, handler = components

        # 1. Register dying entity
        entity = Entity("goblin", EntityStats(), loot_table_id="goblin_loot")
        state_manager.add_entity(entity)

        # 2. Subscribe to LootDroppedEvent to verify dispatch
        caught_events = []
        event_bus.subscribe(LootDroppedEvent, lambda e: caught_events.append(e))

        # 3. Simulate Death Event
        death_event = EntityDeathEvent(entity_id="goblin")
        event_bus.dispatch(death_event)

        # 4. Verify
        # Manager called?
        loot_manager.roll_loot.assert_called_with("goblin_loot")

        # Event dispatched?
        assert len(caught_events) == 1
        assert caught_events[0].source_id == "goblin"
        assert len(caught_events[0].items) == 1
        assert caught_events[0].items[0].name == "Test Sword"

    def test_no_loot_table_ignored(self, components):
        event_bus, state_manager, loot_manager, handler = components

        # Entity with NO loot table
        entity = Entity("dummy", EntityStats(), loot_table_id=None)
        state_manager.add_entity(entity)

        event_bus.dispatch(EntityDeathEvent(entity_id="dummy"))

        # Should not call roll_loot
        loot_manager.roll_loot.assert_not_called()

    def test_empty_drop_ignored(self, components):
        event_bus, state_manager, loot_manager, handler = components

        # Manager returns empty list
        loot_manager.roll_loot.return_value = []

        entity = Entity("ghost", EntityStats(), loot_table_id="empty_table")
        state_manager.add_entity(entity)

        caught_events = []
        event_bus.subscribe(LootDroppedEvent, lambda e: caught_events.append(e))

        event_bus.dispatch(EntityDeathEvent(entity_id="ghost"))

        # Should NOT dispatch event for empty drop
        assert len(caught_events) == 0
