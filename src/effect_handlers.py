"""Effect handlers for combat events - secondary effects like DoTs."""

import random
import logging
from abc import ABC, abstractmethod
from .events import EventBus, OnHitEvent
from .state import StateManager
from .models import DamageOnHitConfig

logger = logging.getLogger(__name__)


# Effect Configuration Constants - can be moved to data files in future
BLEED_CONFIG = DamageOnHitConfig(
    debuff_name="Bleed",
    proc_rate=0.5,
    duration=5.0,
    damage_per_tick=2.5,  # Example: 2.5 damage per stack per tick
    stacks_to_add=1,
    display_message="Bleed proc'd on {target}!"
)

POISON_CONFIG = DamageOnHitConfig(
    debuff_name="Poison",
    proc_rate=0.33,
    duration=8.0,
    damage_per_tick=1.5,  # Example: 1.5 damage per stack per tick
    stacks_to_add=1,
    display_message="Poison proc'd on {target}!"
)


# Legacy Handler Functions - for backward compatibility during transition
def create_bleed_handler(event_bus, state_manager, rng=None):
    """Create a BleedHandler using the generic DamageOnHitHandler."""
    return DamageOnHitHandler(BLEED_CONFIG, event_bus, state_manager, rng)


def create_poison_handler(event_bus, state_manager, rng=None):
    """Create a PoisonHandler using the generic DamageOnHitHandler."""
    return DamageOnHitHandler(POISON_CONFIG, event_bus, state_manager, rng)


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


class DamageOnHitHandler(EffectHandler):
    """Generic handler for damage-over-time effects applied on hit events.

    Configured via DamageOnHitConfig for data-driven effect creation.
    Enables adding new DoT effects without code changes.
    """

    def __init__(self, config: DamageOnHitConfig, event_bus: EventBus, state_manager: StateManager, rng=None):
        """Initialize the generic damage-on-hit handler.

        Args:
            config: Configuration for this effect (name, proc_rate, duration, etc.)
            event_bus: The event bus to subscribe to
            state_manager: The state manager for applying effects
            rng: Random number generator for deterministic testing. If None,
                 uses random.random() without seeding.
        """
        super().__init__(event_bus, state_manager, rng)
        self.config = config
        self.setup_subscriptions()

    def setup_subscriptions(self):
        """Set up event subscriptions for this effect."""
        self.event_bus.subscribe(OnHitEvent, self.handle_on_hit)

    def handle_on_hit(self, event: OnHitEvent, rng=None) -> None:
        """Handle an OnHitEvent by potentially applying the configured effect.

        Args:
            event: The hit event that occurred
            rng: RNG passed explicitly (per PR6 specification)
        """
        if rng is None:
            rng = self.rng or random
        rng_value = rng.random()
        if rng_value < self.config.proc_rate:
            # Display message if configured
            if self.config.display_message:
                target_name = getattr(event.defender, 'name', event.defender.id)
                message = self.config.display_message.format(target=target_name)
                print("    -> " + message)
                logger.debug("Effect proc: %s", message)
            else:
                # Default message format
                message = f"{self.config.debuff_name} proc'd on {event.defender.id}!"
                print("    -> " + message)
                logger.debug("Effect proc: %s", message)

            self.state_manager.apply_debuff(
                entity_id=event.defender.id,
                debuff_name=self.config.debuff_name,
                stacks_to_add=self.config.stacks_to_add,
                max_duration=self.config.duration
            )


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
            logger.debug("Effect proc: Bleed procd on %s", event.defender.id)
            print("    -> Bleed proc'd on defender!")
            self.state_manager.apply_debuff(
                entity_id=event.defender.id,
                debuff_name="Bleed",
                stacks_to_add=1,
                max_duration=5.0  # Example duration
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
            logger.debug("Effect proc: Poison procd on %s", event.defender.id)
            print("    -> Poison proc'd on defender!")
            self.state_manager.apply_debuff(
                entity_id=event.defender.id,
                debuff_name="Poison",
                stacks_to_add=1,
                max_duration=8.0  # Longer duration than Bleed
            )
