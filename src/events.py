"""Event system for combat engine.

Provides the EventBus and event classes for decoupling combat logic from effects.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import Entity
    from engine import HitContext


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


class EventBus:
    """Central dispatcher for combat events using the Observer pattern.

    Maintains a registry of listeners for different event types and dispatches
    events to all registered listeners.
    """

    def __init__(self):
        """Initialize the event bus with empty listener registry."""
        from collections import defaultdict
        self.listeners = defaultdict(list)

    def subscribe(self, event_type: type, listener):
        """Add a listener function for a specific event type.

        Args:
            event_type: The event class to listen for
            listener: Function to call when event is dispatched
        """
        self.listeners[event_type].append(listener)

    def dispatch(self, event: Event):
        """Dispatch an event to all registered listeners.

        Args:
            event: The event instance to dispatch
        """
        for listener in self.listeners[event.__class__]:
            listener(event)
