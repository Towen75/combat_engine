"""Effect handlers for combat events - secondary effects like DoTs."""

import random
from abc import ABC, abstractmethod
from .events import EventBus, OnHitEvent
from .state import StateManager


class EffectHandler(ABC):
    """Base class for effect handlers that respond to combat events.

    Provides common functionality for subscribing to events and managing
    effect application logic.
    """

    def __init__(self, event_bus: EventBus, state_manager: StateManager, rng=None):
        """Initialize the effect handler.

        Args:
            event_bus: The event bus to subscribe to
            state_manager: The state manager for applying effects
            rng: Random number generator for deterministic testing. If None,
                 uses random.random() without seeding.
        """
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.rng = rng

    @abstractmethod
    def setup_subscriptions(self):
        """Set up event subscriptions. Must be implemented by subclasses."""
        pass


class BleedHandler(EffectHandler):
    """Handles Bleed DoT application on hit events."""

    def __init__(self, event_bus: EventBus, state_manager: StateManager, proc_rate: float = 0.5, rng=None):
        """Initialize the Bleed handler.

        Args:
            event_bus: The event bus to subscribe to
            state_manager: The state manager for applying debuffs
            proc_rate: Probability of bleed procing on hit (0.0 to 1.0)
            rng: Random number generator for deterministic testing. If None,
                 uses random.random() without seeding.
        """
        super().__init__(event_bus, state_manager, rng)
        self.proc_rate = proc_rate
        self.setup_subscriptions()

    def setup_subscriptions(self):
        """Set up event subscriptions for Bleed effects."""
        self.event_bus.subscribe(OnHitEvent, self.handle_on_hit)

    def handle_on_hit(self, event: OnHitEvent) -> None:
        """Handle an OnHitEvent by potentially applying Bleed.

        Args:
            event: The hit event that occurred
        """
        rng_value = self.rng.random() if self.rng else random.random()
        if rng_value < self.proc_rate:
            print(f"    -> Bleed proc'd on {event.defender.id}!")
            self.state_manager.add_or_refresh_debuff(
                entity_id=event.defender.id,
                debuff_name="Bleed",
                stacks_to_add=1,
                duration=5.0  # Example duration
            )


class PoisonHandler(EffectHandler):
    """Handles Poison DoT application on hit events."""

    def __init__(self, event_bus: EventBus, state_manager: StateManager, proc_rate: float = 0.33, rng=None):
        """Initialize the Poison handler.

        Args:
            event_bus: The event bus to subscribe to
            state_manager: The state manager for applying debuffs
            proc_rate: Probability of poison procing on hit (0.0 to 1.0)
            rng: Random number generator for deterministic testing. If None,
                 uses random.random() without seeding.
        """
        super().__init__(event_bus, state_manager, rng)
        self.proc_rate = proc_rate
        self.setup_subscriptions()

    def setup_subscriptions(self):
        """Set up event subscriptions for Poison effects."""
        self.event_bus.subscribe(OnHitEvent, self.handle_on_hit)

    def handle_on_hit(self, event: OnHitEvent) -> None:
        """Handle an OnHitEvent by potentially applying Poison.

        Args:
            event: The hit event that occurred
        """
        rng_value = self.rng.random() if self.rng else random.random()
        if rng_value < self.proc_rate:
            print(f"    -> Poison proc'd on {event.defender.id}!")
            self.state_manager.add_or_refresh_debuff(
                entity_id=event.defender.id,
                debuff_name="Poison",
                stacks_to_add=1,
                duration=8.0  # Longer duration than Bleed
            )
