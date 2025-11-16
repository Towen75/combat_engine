"""
Event-driven handlers for conditional affixes.
Phase 3: Simulation & Balancing implementation.
"""

import logging
from .events import EventBus, OnSkillUsedEvent, OnBlockEvent
from .state import Modifier
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .state import StateManager

logger = logging.getLogger(__name__)


class FocusedRageHandler:
    """Handler for Focused Rage affix.
    Applies crit chance bonus when special skills are used.
    """

    def __init__(self, event_bus: EventBus, state_manager: "StateManager"):
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.event_bus.subscribe(OnSkillUsedEvent, self.handle_skill_used)

    def handle_skill_used(self, event: OnSkillUsedEvent):
        """Apply crit chance modifier when special skills are used."""
        # TODO: Check if it's a special skill (based on skill data)
        # For now, all skills qualify
        bonus_value = 0.25  # +25% crit chance
        duration = 5.0      # 5 seconds

        modifier = Modifier(
            value=bonus_value,
            duration=duration,
            source="focused_rage"
        )

        entity_state = self.state_manager.get_state(event.entity.id)
        if entity_state:
            if 'crit_chance' not in entity_state.roll_modifiers:
                entity_state.roll_modifiers['crit_chance'] = []
            entity_state.roll_modifiers['crit_chance'].append(modifier)

            # Optional: Dispatch event for UI feedback
            # self.event_bus.dispatch(BuffAppliedEvent(event.entity, modifier))


class BlindingRebukeHandler:
    """Handler for Blinding Rebuke affix.
    Applies evasion penalty to attacker when defender blocks.
    """

    def __init__(self, event_bus: EventBus, state_manager: "StateManager"):
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.event_bus.subscribe(OnBlockEvent, self.handle_block)

    def handle_block(self, event: OnBlockEvent):
        """Apply evasion penalty to the attacker when they get blocked."""
        penalty_value = -0.15  # -15% evasion chance
        duration = 3.0         # 3 seconds

        modifier = Modifier(
            value=penalty_value,
            duration=duration,
            source="blinding_rebuke"
        )

        # Apply to attacker's evasion modifiers
        attacker_state = self.state_manager.get_state(event.attacker.id)
        if attacker_state:
            if 'evasion_chance' not in attacker_state.roll_modifiers:
                attacker_state.roll_modifiers['evasion_chance'] = []
            attacker_state.roll_modifiers['evasion_chance'].append(modifier)

            # Optional: Dispatch event for UI feedback
            # self.event_bus.dispatch(DebuffAppliedEvent(event.attacker, modifier))


def setup_conditional_affix_handlers(event_bus: EventBus, state_manager: "StateManager"):
    """Initialize all conditional affix handlers.

    Args:
        event_bus: The game's event bus
        state_manager: The game's state manager
    """
    # Create and register handlers
    FocusedRageHandler(event_bus, state_manager)
    BlindingRebukeHandler(event_bus, state_manager)

    logger.info("Conditional affix handlers initialized")
    logger.info("  ✅ Focused Rage: Crit bonus on special skill use")
    logger.info("  ✅ Blinding Rebuke: Evasion penalty on attacker when blocked")
