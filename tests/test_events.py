"""Unit tests for the event system."""

import pytest
from src.core.events import Event, OnHitEvent, OnCritEvent, EventBus
from src.core.models import Entity, EntityStats


class TestEventClasses:
    """Test the event data classes."""

    def test_on_hit_event_creation(self):
        """Test OnHitEvent can be created with required fields."""
        attacker_stats = EntityStats()
        defender_stats = EntityStats()
        attacker = Entity("attacker", attacker_stats)
        defender = Entity("defender", defender_stats)

        event = OnHitEvent(
            attacker=attacker,
            defender=defender,
            damage_dealt=50.0,
            is_crit=False
        )

        assert event.attacker == attacker
        assert event.defender == defender
        assert event.damage_dealt == 50.0
        assert event.is_crit is False

    def test_on_crit_event_creation(self):
        """Test OnCritEvent can be created with OnHitEvent."""
        attacker_stats = EntityStats()
        defender_stats = EntityStats()
        attacker = Entity("attacker", attacker_stats)
        defender = Entity("defender", defender_stats)

        hit_event = OnHitEvent(
            attacker=attacker,
            defender=defender,
            damage_dealt=75.0,
            is_crit=True
        )

        crit_event = OnCritEvent(hit_event=hit_event)

        assert crit_event.hit_event == hit_event
        assert crit_event.hit_event.is_crit is True


class TestEventBus:
    """Test the EventBus functionality."""

    def test_event_bus_initialization(self):
        """Test EventBus initializes with empty listeners."""
        bus = EventBus()
        assert len(bus.listeners) == 0

    def test_subscribe_adds_listener(self):
        """Test that subscribe adds a listener for an event type."""
        bus = EventBus()
        mock_listener = lambda event: None

        bus.subscribe(OnHitEvent, mock_listener)

        assert OnHitEvent in bus.listeners
        # With PR3, listeners are now ListenerEntry objects
        listener_entries = bus.listeners[OnHitEvent]
        assert len(listener_entries) == 1
        assert listener_entries[0].listener == mock_listener

    def test_dispatch_calls_listener(self):
        """Test that dispatch calls the subscribed listener with the event."""
        bus = EventBus()
        events_received = []

        def mock_listener(event):
            events_received.append(event)

        bus.subscribe(OnHitEvent, mock_listener)

        attacker_stats = EntityStats()
        defender_stats = EntityStats()
        attacker = Entity("attacker", attacker_stats)
        defender = Entity("defender", defender_stats)

        event = OnHitEvent(
            attacker=attacker,
            defender=defender,
            damage_dealt=25.0
        )

        bus.dispatch(event)

        assert len(events_received) == 1
        assert events_received[0] == event

    def test_dispatch_does_not_call_wrong_event_type(self):
        """Test that listeners only receive events of their subscribed type."""
        bus = EventBus()
        hit_events_received = []
        crit_events_received = []

        def hit_listener(event):
            hit_events_received.append(event)

        def crit_listener(event):
            crit_events_received.append(event)

        bus.subscribe(OnHitEvent, hit_listener)
        bus.subscribe(OnCritEvent, crit_listener)

        attacker_stats = EntityStats()
        defender_stats = EntityStats()
        attacker = Entity("attacker", attacker_stats)
        defender = Entity("defender", defender_stats)

        hit_event = OnHitEvent(
            attacker=attacker,
            defender=defender,
            damage_dealt=25.0
        )

        bus.dispatch(hit_event)

        assert len(hit_events_received) == 1
        assert len(crit_events_received) == 0

    def test_multiple_listeners_same_event(self):
        """Test that multiple listeners for the same event type all get called."""
        bus = EventBus()
        listener1_calls = []
        listener2_calls = []

        def listener1(event):
            listener1_calls.append(event)

        def listener2(event):
            listener2_calls.append(event)

        bus.subscribe(OnHitEvent, listener1)
        bus.subscribe(OnHitEvent, listener2)

        attacker_stats = EntityStats()
        defender_stats = EntityStats()
        attacker = Entity("attacker", attacker_stats)
        defender = Entity("defender", defender_stats)

        event = OnHitEvent(
            attacker=attacker,
            defender=defender,
            damage_dealt=30.0
        )

        bus.dispatch(event)

        assert len(listener1_calls) == 1
        assert len(listener2_calls) == 1
        assert listener1_calls[0] == event
        assert listener2_calls[0] == event

    def test_dispatch_with_no_listeners(self):
        """Test that dispatching an event with no listeners doesn't cause errors."""
        bus = EventBus()

        attacker_stats = EntityStats()
        defender_stats = EntityStats()
        attacker = Entity("attacker", attacker_stats)
        defender = Entity("defender", defender_stats)

        event = OnHitEvent(
            attacker=attacker,
            defender=defender,
            damage_dealt=20.0
        )

        # Should not raise any exceptions
        bus.dispatch(event)
