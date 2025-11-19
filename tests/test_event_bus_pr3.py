"""Production-grade EventBus tests for PR3 enhancements.

Tests the production-ready features added in PR3:
- Exception isolation and safe dispatch
- Unsubscribe support
- Safe iteration with concurrent modifications
- Listener priorities
- Event profiling and monitoring
- Comprehensive edge cases and error handling
"""

import logging
import pytest
from unittest.mock import MagicMock
from src.core.events import EventBus, OnHitEvent, Event


class TestEvent(Event):
    """Simple test event for testing."""
    __test__ = False
    pass


class TestEventTwo(Event):
    """Second test event type."""
    __test__ = False
    pass


def create_mock_entity(name="test"):
    """Create a minimal mock entity for testing."""
    entity = MagicMock()
    entity.id = name
    entity.name = name
    return entity


class TestEventBusExceptionIsolation:
    """Test that exceptions in listeners don't break other listeners."""

    def test_dispatch_isolated_from_listener_errors(self, caplog):
        """Test that failing listeners don't break dispatch to good ones."""
        caplog.set_level(logging.ERROR)
        bus = EventBus()

        calls = []

        def bad_listener(event):
            calls.append("bad_start")
            raise RuntimeError("boom")
            calls.append("bad_end")  # This should not execute

        def good_listener(event):
            calls.append("good")

        bus.subscribe(TestEvent, bad_listener)
        bus.subscribe(TestEvent, good_listener)

        bus.dispatch(TestEvent())

        # First listener started but failed, second listener executed
        assert calls == ["bad_start", "good"]
        # Error was logged
        assert "boom" in caplog.text
        assert "bad_listener" in caplog.text
        assert "TestEvent" in caplog.text

    def test_multiple_listeners_with_mixed_failures(self, caplog):
        """Test multiple listeners where some fail and some succeed."""
        caplog.set_level(logging.ERROR)
        bus = EventBus()

        calls = []

        def listener1(event):
            calls.append("listener1")
            raise ValueError("error1")

        def listener2(event):
            calls.append("listener2")

        def listener3(event):
            calls.append("listener3")
            raise RuntimeError("error3")

        def listener4(event):
            calls.append("listener4")

        bus.subscribe(TestEvent, listener1)
        bus.subscribe(TestEvent, listener2)
        bus.subscribe(TestEvent, listener3)
        bus.subscribe(TestEvent, listener4)

        bus.dispatch(TestEvent())

        # All listeners started executing in order
        assert calls == ["listener1", "listener2", "listener3", "listener4"]
        # Both errors were logged
        assert "error1" in caplog.text
        assert "error3" in caplog.text
        assert caplog.text.count("ERROR") == 2


class TestEventBusUnsubscribe:
    """Test unsubscribe functionality."""

    def test_unsubscribe_removes_listener(self):
        """Test basic unsubscribe removes listener correctly."""
        bus = EventBus()
        calls = []

        def f(event): calls.append(1)

        bus.subscribe(TestEvent, f)
        result = bus.unsubscribe(TestEvent, f)
        bus.dispatch(TestEvent())

        assert result is True
        assert calls == []

    def test_unsubscribe_returns_false_for_nonexistent_listener(self):
        """Test unsubscribe returns False for listener not found."""
        bus = EventBus()

        def f(event): pass

        result = bus.unsubscribe(TestEvent, f)
        assert result is False

    def test_unsubscribe_removes_correct_listener(self):
        """Test unsubscribe only removes specific listener, not others."""
        bus = EventBus()
        calls = []

        def listener1(event): calls.append("listener1")
        def listener2(event): calls.append("listener2")
        def listener3(event): calls.append("listener3")

        bus.subscribe(TestEvent, listener1)
        bus.subscribe(TestEvent, listener2)
        bus.subscribe(TestEvent, listener3)

        bus.unsubscribe(TestEvent, listener2)

        bus.dispatch(TestEvent())

        assert calls == ["listener1", "listener3"]

    def test_unsubscribe_different_event_types(self):
        """Test unsubscribe only affects specific event type."""
        bus = EventBus()
        calls = []

        def f(event): calls.append(event.__class__.__name__)

        bus.subscribe(TestEvent, f)
        bus.subscribe(TestEventTwo, f)

        bus.unsubscribe(TestEvent, f)

        bus.dispatch(TestEvent())
        bus.dispatch(TestEventTwo())

        assert calls == ["TestEventTwo"]


class TestEventBusSafeIteration:
    """Test safe iteration and concurrent modification handling."""

    def test_subscribe_during_dispatch_safe(self):
        """Test subscribing during dispatch doesn't affect current iteration."""
        bus = EventBus()
        calls = []

        def listener_a(event):
            calls.append("A")
            # Subscribe a new listener during dispatch
            bus.subscribe(TestEvent, listener_b)

        def listener_b(event):
            calls.append("B")

        bus.subscribe(TestEvent, listener_a)
        bus.dispatch(TestEvent())

        # Only A executes in this dispatch cycle
        assert calls == ["A"]

        # B should execute in subsequent dispatches
        bus.dispatch(TestEvent())
        assert calls == ["A", "A", "B"]

    def test_unsubscribe_during_dispatch_safe(self):
        """Test unsubscribing during dispatch doesn't break iteration."""
        bus = EventBus()
        calls = []

        def listener_a(event):
            calls.append("A")
            # Unsubscribe self during dispatch (should not affect current dispatch)
            bus.unsubscribe(TestEvent, listener_a)

        def listener_b(event):
            calls.append("B")

        bus.subscribe(TestEvent, listener_a)
        bus.subscribe(TestEvent, listener_b)

        bus.dispatch(TestEvent())
        # Both should execute in first dispatch (safe copy used)
        assert calls == ["A", "B"]

        # Second dispatch only B should execute
        bus.dispatch(TestEvent())
        assert calls == ["A", "B", "B"]

    def test_multiple_subscribe_unsubscribe_during_dispatch(self):
        """Test complex subscribe/unsubscribe operations during dispatch."""
        bus = EventBus()
        calls = []

        def a(event):
            calls.append("A")
            bus.unsubscribe(TestEvent, c)
            bus.subscribe(TestEvent, d)

        def b(event):
            calls.append("B")

        def c(event):
            calls.append("C")

        def d(event):
            calls.append("D")

        bus.subscribe(TestEvent, a)
        bus.subscribe(TestEvent, b)
        bus.subscribe(TestEvent, c)

        # First dispatch: A, B, C execute (safe copy)
        # During A's execution: C is unsubscribed, D is subscribed
        bus.dispatch(TestEvent())
        assert calls == ["A", "B", "C"]

        # Second dispatch: A, B, D execute (D was added, C was removed)
        bus.dispatch(TestEvent())
        assert calls == ["A", "B", "C", "A", "B", "D"]


class TestEventBusListenerPriorities:
    """Test listener priority system."""

    def test_priority_ordering(self):
        """Test listeners execute in priority order (highest first)."""
        bus = EventBus()
        calls = []

        def low_priority(event): calls.append("low")
        def med_priority(event): calls.append("med")
        def high_priority(event): calls.append("high")

        bus.subscribe(TestEvent, low_priority, priority=0)  # Default priority
        bus.subscribe(TestEvent, med_priority, priority=5)
        bus.subscribe(TestEvent, high_priority, priority=10)

        bus.dispatch(TestEvent())

        assert calls == ["high", "med", "low"]

    def test_priority_negative_values(self):
        """Test negative priority values work correctly."""
        bus = EventBus()
        calls = []

        def p_neg1(event): calls.append("-1")
        def p_zero(event): calls.append("0")
        def p_pos1(event): calls.append("1")

        bus.subscribe(TestEvent, p_neg1, priority=-1)
        bus.subscribe(TestEvent, p_zero, priority=0)
        bus.subscribe(TestEvent, p_pos1, priority=1)

        bus.dispatch(TestEvent())

        assert calls == ["1", "0", "-1"]

    def test_priority_sorting_after_subscribe(self):
        """Test that priority sorting works when subscribing in wrong order."""
        bus = EventBus()
        calls = []

        def first(event): calls.append("first")
        def second(event): calls.append("second")
        def third(event): calls.append("third")

        # Subscribe in "wrong" order
        bus.subscribe(TestEvent, first, priority=1)
        bus.subscribe(TestEvent, second, priority=5)
        bus.subscribe(TestEvent, third, priority=10)

        # Should still execute in correct priority order
        bus.dispatch(TestEvent())

        assert calls == ["third", "second", "first"]

    def test_unsubscribe_preserves_priority_ordering(self):
        """Test that unsubscribing maintains priority ordering for remaining listeners."""
        bus = EventBus()
        calls = []

        def low(event): calls.append("low")
        def med(event): calls.append("med")
        def high(event): calls.append("high")

        bus.subscribe(TestEvent, low, priority=1)
        bus.subscribe(TestEvent, med, priority=5)
        bus.subscribe(TestEvent, high, priority=10)

        # Remove medium priority
        bus.unsubscribe(TestEvent, med)

        bus.dispatch(TestEvent())

        assert calls == ["high", "low"]


class TestEventBusProfiling:
    """Test event dispatch profiling and monitoring features."""

    def test_profiling_disabled_by_default(self):
        """Test profiling is disabled by default and doesn't collect data."""
        bus = EventBus()

        def listener(event): pass

        bus.subscribe(TestEvent, listener)
        bus.dispatch(TestEvent())

        stats = bus.get_profiling_stats()

        # Stats should be mostly empty since profiling is disabled
        assert stats == {'_failures': {}, '_total_events_dispatched': 0}

    def test_profiling_enabled_collects_basic_stats(self):
        """Test enabling profiling collects dispatch counts."""
        bus = EventBus()
        bus.enable_profiling(True)

        def listener(event): pass

        bus.subscribe(TestEvent, listener)
        bus.dispatch(TestEvent())
        bus.dispatch(TestEvent())

        stats = bus.get_profiling_stats()

        event_stats = stats.get('TestEvent')
        assert event_stats is not None
        assert event_stats['total_dispatches'] == 2
        assert event_stats['listeners_count'] == 1
        assert isinstance(event_stats['avg_dispatch_time_ms'], float)
        assert isinstance(event_stats['max_dispatch_time_ms'], float)
        assert stats['_total_events_dispatched'] == 2

    def test_profiling_collects_failure_stats(self):
        """Test profiling collects failure counts."""
        bus = EventBus()
        bus.enable_profiling(True)

        def good_listener(event): pass
        def bad_listener(event): raise RuntimeError("test")

        bus.subscribe(TestEvent, good_listener)
        bus.subscribe(TestEvent, bad_listener)
        bus.subscribe(TestEventTwo, bad_listener)

        bus.dispatch(TestEvent())
        bus.dispatch(TestEvent())
        bus.dispatch(TestEventTwo())

        stats = bus.get_profiling_stats()

        # Should have failure count for bad_listener
        failures = stats.get('_failures', {})
        bad_listener_name = bad_listener.__name__ if hasattr(bad_listener, '__name__') else str(bad_listener)
        assert failures[bad_listener_name] == 3  # Failed on 2 TestEvent + 1 TestEventTwo

        # Should have dispatch stats for both event types
        assert 'TestEvent' in stats
        assert 'TestEventTwo' in stats
        assert stats['TestEvent']['total_dispatches'] == 2
        assert stats['TestEventTwo']['total_dispatches'] == 1

    def test_profiling_reset_clears_data(self):
        """Test profiling reset clears all metrics."""
        bus = EventBus()
        bus.enable_profiling(True)

        def listener(event): pass

        bus.subscribe(TestEvent, listener)
        bus.dispatch(TestEvent())

        # Stats should exist
        stats_before = bus.get_profiling_stats()
        assert stats_before['_total_events_dispatched'] == 1

        # Reset and check stats are cleared
        bus.reset_profiling()
        stats_after = bus.get_profiling_stats()
        assert stats_after == {'_failures': {}, '_total_events_dispatched': 0}

    def test_enable_disable_profiling(self):
        """Test enabling/disabling profiling works correctly."""
        bus = EventBus()

        def listener(event): pass

        bus.subscribe(TestEvent, listener)

        # Disabled by default
        bus.dispatch(TestEvent())
        stats_disabled = bus.get_profiling_stats()
        assert stats_disabled['_total_events_dispatched'] == 0

        # Enable profiling
        bus.enable_profiling(True)
        bus.dispatch(TestEvent())
        stats_enabled = bus.get_profiling_stats()
        assert stats_enabled['_total_events_dispatched'] == 1

        # Disable profiling (should stop collecting new data)
        bus.enable_profiling(False)
        bus.dispatch(TestEvent())
        stats_disabled_again = bus.get_profiling_stats()
        # Should still have the previous dispatch count
        assert stats_disabled_again['_total_events_dispatched'] == 1

        # Re-enable should work
        bus.enable_profiling(True)
        bus.dispatch(TestEvent())
        final_stats = bus.get_profiling_stats()
        assert final_stats['_total_events_dispatched'] == 2


class TestEventBusUtilityMethods:
    """Test utility and management methods."""

    def test_get_listener_count(self):
        """Test listener count methods."""
        bus = EventBus()

        def listener1(event): pass
        def listener2(event): pass
        def listener3(event): pass

        # Empty bus
        assert bus.get_listener_count() == 0
        assert bus.get_listener_count(TestEvent) == 0

        # Add listeners
        bus.subscribe(TestEvent, listener1)
        bus.subscribe(TestEvent, listener2)
        bus.subscribe(TestEventTwo, listener3)

        assert bus.get_listener_count() == 3
        assert bus.get_listener_count(TestEvent) == 2
        assert bus.get_listener_count(TestEventTwo) == 1

        # Remove one
        bus.unsubscribe(TestEvent, listener1)

        assert bus.get_listener_count() == 2
        assert bus.get_listener_count(TestEvent) == 1

    def test_clear_all_listeners(self):
        """Test clearing all listeners."""
        bus = EventBus()

        def listener1(event): pass
        def listener2(event): pass

        bus.subscribe(TestEvent, listener1, priority=5, name="test1")
        bus.subscribe(TestEvent, listener2, priority=10, name="test2")
        bus.enable_profiling(True)
        bus.dispatch(TestEvent())  # Generate some profiling data

        # Verify listeners exist and profiling data exists
        initial_count = bus.get_listener_count()
        initial_stats = bus.get_profiling_stats()

        assert initial_count == 2
        assert initial_stats['_total_events_dispatched'] == 1

        # Clear everything
        bus.clear()

        # Verify everything is cleared
        assert bus.get_listener_count() == 0
        cleared_stats = bus.get_profiling_stats()
        assert cleared_stats == {'_failures': {}, '_total_events_dispatched': 0}

    def test_multiple_event_types_independence(self):
        """Test that operations on one event type don't affect others."""
        bus = EventBus()

        def test_event1_listener(event): pass
        def test_event2_listener(event): pass

        bus.subscribe(TestEvent, test_event1_listener)
        bus.subscribe(TestEventTwo, test_event2_listener)

        # Unsubscribe from wrong event type
        result = bus.unsubscribe(TestEvent, test_event2_listener)
        assert result is False
        assert bus.get_listener_count(TestEvent) == 1
        assert bus.get_listener_count(TestEventTwo) == 1

        # Correct unsubscribe
        result = bus.unsubscribe(TestEventTwo, test_event2_listener)
        assert result is True
        assert bus.get_listener_count(TestEvent) == 1
        assert bus.get_listener_count(TestEventTwo) == 0


class TestEventBusEdgeCases:
    """Test edge cases and complex scenarios."""

    def test_subscribe_with_names(self):
        """Test listener names for better debugging."""
        bus = EventBus()

        def listener(event): pass

        bus.subscribe(TestEvent, listener, name="my_special_listener")

        # Check that the listener entry has the correct name
        event_listeners = bus.listeners[TestEvent]
        assert len(event_listeners) == 1
        assert event_listeners[0].name == "my_special_listener"

    def test_exception_in_exception_handler_does_not_crash(self):
        """Test that even if exception logging fails, dispatch continues."""
        bus = EventBus()

        # Patch logger.exception to fail
        original_exception = logging.Logger.exception
        logging.Logger.exception = MagicMock(side_effect=Exception("Logger failed"))

        calls = []

        def bad_listener(event):
            raise RuntimeError("Listener error")

        def good_listener(event):
            calls.append("good")

        bus.subscribe(TestEvent, bad_listener)
        bus.subscribe(TestEvent, good_listener)

        # This should not raise - even though logger.exception fails,
        # the dispatch should continue to good listeners
        bus.dispatch(TestEvent())

        assert calls == ["good"]

        # Restore logger
        logging.Logger.exception = original_exception

    def test_performance_with_many_listeners(self):
        """Basic performance test with many listeners."""
        bus = EventBus()

        listeners = []

        # Create 100 listeners
        for i in range(100):
            def make_listener(idx):
                def listener(event):
                    pass
                return listener
            listeners.append(make_listener(i))

        # Subscribe all
        for idx, listener in enumerate(listeners):
            bus.subscribe(TestEvent, listener, priority=idx, name=f"listener_{idx}")

        # Dispatch should handle all listeners
        bus.dispatch(TestEvent())

        assert bus.get_listener_count(TestEvent) == 100

    def test_complex_priority_and_error_scenario(self):
        """Test complex scenario with priorities and mixed failures."""
        bus = EventBus()
        bus.enable_profiling(True)
        calls = []

        def high_fail(event):
            calls.append("high_failed")
            raise RuntimeError("High priority failure")

        def med_success(event):
            calls.append("med_success")

        def low_fail(event):
            calls.append("low_failed")
            raise ValueError("Low priority failure")

        def low_success(event):
            calls.append("low_success")

        # Subscribe with various priorities and reliability
        bus.subscribe(TestEvent, high_fail, priority=10, name="high_fail")
        bus.subscribe(TestEvent, med_success, priority=5, name="med_success")
        bus.subscribe(TestEvent, low_fail, priority=0, name="low_fail")
        bus.subscribe(TestEvent, low_success, priority=0, name="low_success")

        # Dispatch should execute in priority order and continue despite failures
        bus.dispatch(TestEvent())

        # Priority order: high fail, med success, then low priority group
        # Within same priority (0), order of subscription
        assert calls == ["high_failed", "med_success", "low_failed", "low_success"]

        # Profiling should track failures
        stats = bus.get_profiling_stats()
        failures = stats['_failures']

        # Both failing listeners should be tracked
        assert failures['high_fail'] == 1
        assert failures['low_fail'] == 1


class TestBackwardsCompatibility:
    """Test that existing EventBus API still works."""

    def test_old_api_still_works(self):
        """Test the old subscribe() API (without priority/name) still works."""
        bus = EventBus()
        calls = []

        def listener1(event): calls.append("listener1")
        def listener2(event): calls.append("listener2")

        # Old API without priority/name
        bus.subscribe(TestEvent, listener1)
        bus.subscribe(TestEvent, listener2)

        bus.dispatch(TestEvent())

        # Both listeners called (priority defaults to 0, so subscription order)
        assert calls == ["listener1", "listener2"]

        # Unsubscribe still works
        bus.unsubscribe(TestEvent, listener1)
        calls.clear()
        bus.dispatch(TestEvent())

        assert calls == ["listener2"]
