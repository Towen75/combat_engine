"""Event system for combat engine.

Provides the EventBus and event classes for decoupling combat logic from effects.

Enhanced with PR3: Production-grade event system with unsubscribe support,
exception isolation, safe iteration, and listener priority support.
"""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from models import Entity, EffectInstance
    from engine import HitContext

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Base class for all combat events."""
    pass


@dataclass
class OnHitEvent(Event):
    """Event fired when an attack hits a target."""
    attacker: "Entity"
    defender: "Entity"
    damage_dealt: float
    is_crit: bool = False


@dataclass
class OnCritEvent(Event):
    """Event fired when a critical hit occurs."""
    hit_event: OnHitEvent


@dataclass
class DamageTickEvent(Event):
    """Event fired when a damage-over-time effect ticks."""
    target: "Entity"
    effect_name: str
    damage_dealt: float
    stacks: int


@dataclass
class OnDodgeEvent(Event):
    """Fired when an attack is fully dodged."""
    attacker: "Entity"
    defender: "Entity"


@dataclass
class OnBlockEvent(Event):
    """Fired when a hit is successfully blocked."""
    attacker: "Entity"
    defender: "Entity"
    damage_before_block: float
    damage_blocked: float
    hit_context: "HitContext"


@dataclass
class OnGlancingBlowEvent(Event):
    """Fired when a hit is downgraded to a Glancing Blow."""
    hit_event: OnHitEvent


@dataclass
class OnSkillUsedEvent(Event):
    """Fired when an entity successfully uses a skill (after cost/cooldown checks)."""
    entity: "Entity"
    skill_id: str
    skill_type: str


@dataclass
class EffectApplied(Event):
    """Fired when a status effect is applied to an entity."""
    entity_id: str
    effect: "EffectInstance"


@dataclass
class EffectExpired(Event):
    """Fired when a status effect expires from an entity."""
    entity_id: str
    effect: "EffectInstance"


@dataclass
class EffectTick(Event):
    """Fired when a periodic effect applies its tick damage/healing."""
    entity_id: str
    effect: "EffectInstance"
    damage_applied: float
    stacks: int = 1


@dataclass
class ListenerEntry:
    """Represents a listener with metadata for priority and management."""
    listener: Callable
    priority: int = 0  # Higher priority = executed first
    name: str = ""     # Optional name for debugging


class EventBus:
    """Production-grade EventBus with PR3 enhancements.

    Features:
    - Exception isolation: One failing listener cannot break others
    - Unsubscribe support: Proper resource management
    - Safe iteration: No concurrent modification issues
    - Listener priorities: Critical listeners run first
    - Event profiling: Optional monitoring and metrics
    """

    def __init__(self):
        """Initialize the enhanced event bus."""
        # Listener registry: event_type -> list of ListenerEntry (sorted by priority)
        self.listeners: Dict[type, List[ListenerEntry]] = defaultdict(list)

        # Optional profiling/metrics
        self._profiling_enabled = False
        self._profiling_initialized = False  # Track if profiling has been enabled at least once
        self._dispatch_counts: Dict[type, int] = defaultdict(int)
        self._dispatch_times: Dict[type, List[float]] = defaultdict(list)
        self._failure_counts: Dict[Callable, int] = defaultdict(int)

    def subscribe(self, event_type: type, listener: Callable, priority: int = 0, name: str = ""):
        """Register a listener for the given event type.

        Args:
            event_type: The event class to listen for
            listener: Function to call when event is dispatched
            priority: Higher values executed first (default: 0)
            name: Optional name for debugging (default: "")
        """
        entry = ListenerEntry(listener=listener, priority=priority, name=name)
        self.listeners[event_type].append(entry)

        # Keep listeners sorted by priority (highest first)
        self.listeners[event_type].sort(key=lambda e: e.priority, reverse=True)

        logger.debug("Subscribed listener %s for %s (priority: %d)",
                    name or str(listener), event_type.__name__, priority)

    def unsubscribe(self, event_type: type, listener: Callable):
        """Remove a listener from the event type.

        Args:
            event_type: The event class to unsubscribe from
            listener: The listener function to remove

        Returns:
            True if listener was found and removed, False otherwise
        """
        listeners = self.listeners.get(event_type, [])
        for i, entry in enumerate(listeners):
            if entry.listener is listener:
                removed = listeners.pop(i)
                logger.debug("Unsubscribed listener %s from %s",
                           removed.name or str(listener), event_type.__name__)
                return True

        logger.debug("Listener %s not found for %s", str(listener), event_type.__name__)
        return False

    def dispatch(self, event: Event):
        """Dispatch an event to all registered listeners safely.

        Features:
        - Exception isolation: Listener failures don't stop dispatch
        - Safe iteration: Copy list to prevent concurrent modification
        - Logging: Failed listeners logged as errors
        - Profiling: Optional dispatch metrics

        Args:
            event: The event instance to dispatch
        """
        event_type = event.__class__
        event_listeners = self.listeners.get(event_type, [])

        if not event_listeners:
            return

        # Create safe copy for iteration (prevents modification during dispatch)
        safe_listeners = list(event_listeners)

        dispatch_start = time.perf_counter() if self._profiling_enabled else 0
        failed_count = 0

        logger.debug("Dispatching %s to %d listeners", event_type.__name__, len(safe_listeners))

        for entry in safe_listeners:
            try:
                entry.listener(event)
            except Exception as e:
                failed_count += 1
                self._failure_counts[entry.listener] += 1

                listener_name = entry.name or str(entry.listener)
                logger.error(
                    "Listener %s failed while handling %s: %s",
                    listener_name, event_type.__name__, e,
                    exc_info=True
                )
                # Continue dispatching to other listeners

        # Collect profiling data
        if self._profiling_enabled:
            dispatch_time = time.perf_counter() - dispatch_start
            self._dispatch_counts[event_type] += 1
            self._dispatch_times[event_type].append(dispatch_time)

            logger.debug(
                "Dispatched %s in %.3fms (%d listeners, %d failed)",
                event_type.__name__, dispatch_time * 1000, len(safe_listeners), failed_count
            )

    # === Profiling and Monitoring Features ===

    def enable_profiling(self, enabled: bool = True):
        """Enable or disable event dispatch profiling.

        Args:
            enabled: Whether to collect dispatch performance metrics
        """
        previously_enabled = self._profiling_enabled
        self._profiling_enabled = enabled

        # Reset only when first enabling profiling
        if enabled and not self._profiling_initialized:
            self.reset_profiling()
            self._profiling_initialized = True

    def reset_profiling(self):
        """Reset all profiling data."""
        self._dispatch_counts.clear()
        self._dispatch_times.clear()
        self._failure_counts.clear()

    def get_profiling_stats(self) -> Dict:
        """Get comprehensive profiling statistics.

        Returns:
            Dictionary containing dispatch counts, average times, and failure rates
        """
        stats = {}

        for event_type, times in self._dispatch_times.items():
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                total_dispatches = self._dispatch_counts[event_type]

                stats[event_type.__name__] = {
                    'total_dispatches': total_dispatches,
                    'avg_dispatch_time_ms': avg_time * 1000,
                    'max_dispatch_time_ms': max_time * 1000,
                    'listeners_count': len(self.listeners[event_type])
                }

        # Include failure stats
        failure_summary = {}
        for listener, count in self._failure_counts.items():
            listener_name = getattr(listener, '__name__', str(listener))
            failure_summary[listener_name] = count

        stats['_failures'] = failure_summary
        stats['_total_events_dispatched'] = sum(self._dispatch_counts.values())

        return stats

    # === Utility and Management Methods ===

    def get_listener_count(self, event_type: Optional[type] = None) -> int:
        """Get the total number of listeners.

        Args:
            event_type: If specified, count only for this event type

        Returns:
            Number of registered listeners
        """
        if event_type:
            return len(self.listeners.get(event_type, []))
        return sum(len(listeners) for listeners in self.listeners.values())

    def clear(self):
        """Remove all listeners from the event bus.

        Useful for cleanup or testing.
        """
        total_removed = sum(len(listeners) for listeners in self.listeners.values())
        self.listeners.clear()
        self.reset_profiling()
        logger.debug("Cleared all listeners (%d removed)", total_removed)
