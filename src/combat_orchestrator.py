"""Combat Orchestrator - Executes calculated skill actions.

Orchestrator pattern that separates action execution from calculation.
Handles the imperative side effects of combat while keeping the engine pure.
"""

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import SkillUseResult
    from .state import StateManager
    from .events import EventBus

from .models import ApplyDamageAction, DispatchEventAction, ApplyEffectAction


class CombatOrchestrator:
    """Orchestrates the execution of calculated combat actions.

    Takes SkillUseResult from CombatEngine and executes the actions
    via StateManager and EventBus. Handles all side effects.
    """

    def __init__(self, state_manager: "StateManager", event_bus: "EventBus", rng=None):
        """Initialize the orchestrator with required dependencies.

        Args:
            state_manager: The state manager for applying entity state changes
            event_bus: The event bus for dispatching combat events
            rng: Optional RNG for effect proc rolls and other random behaviors
        """
        self.state_manager = state_manager
        self.event_bus = event_bus
        self.rng = rng

    def execute_skill_use(self, skill_result: "SkillUseResult") -> None:
        """Execute all actions from a calculated skill use.

        Args:
            skill_result: The calculated result from CombatEngine.calculate_skill_use()
        """
        for action in skill_result.actions:
            if isinstance(action, ApplyDamageAction):
                self._execute_damage_action(action)
            elif isinstance(action, DispatchEventAction):
                self._execute_event_action(action)
            elif isinstance(action, ApplyEffectAction):
                self._execute_effect_action(action)
            else:
                raise ValueError(f"Unknown action type: {type(action)}")

    def _execute_damage_action(self, action: ApplyDamageAction) -> None:
        """Execute a damage application action.

        Args:
            action: The ApplyDamageAction to execute
        """
        self.state_manager.apply_damage(action.target_id, action.damage)

    def _execute_event_action(self, action: DispatchEventAction) -> None:
        """Execute an event dispatching action.

        Args:
            action: The DispatchEventAction to execute
        """
        self.event_bus.dispatch(action.event)

    def _execute_effect_action(self, action: ApplyEffectAction) -> None:
        """Execute an effect application action.

        Handles random proc checks for triggered effects.

        Args:
            action: The ApplyEffectAction to execute
        """
        # For effects that have proc rates (like skill triggers), check randomness here
        # This is where we handle the stochastic aspects of triggers
        should_apply = True

        # If the action has a proc rate, check it
        # TODO: This logic needs to be made more generic - currently assumes skill triggers
        # For now, assume the source contains "_trigger" to indicate probabilistic effects
        if "_trigger" in action.source:
            # This is a skill trigger effect - check if it procs
            # For now, we assume a default proc rate - this should be made configurable
            rng_value = self.rng.random() if self.rng else random.random()
            # Default proc rate - should be made configurable per trigger
            proc_rate = 0.5  # TODO: Make this configurable
            should_apply = rng_value < proc_rate

        if should_apply:
            self.state_manager.add_or_refresh_debuff(
                entity_id=action.target_id,
                debuff_name=action.effect_name,
                stacks_to_add=action.stacks_to_add
            )


# Convenience function for executing skill results
def execute_skill_use(skill_result: "SkillUseResult", state_manager: "StateManager", event_bus: "EventBus", rng=None) -> None:
    """Convenience function to execute skill use results.

    Args:
        skill_result: The calculated result from CombatEngine.calculate_skill_use()
        state_manager: The state manager for applying entity state changes
        event_bus: The event bus for dispatching combat events
        rng: Optional RNG for effect proc rolls and other random behaviors
    """
    orchestrator = CombatOrchestrator(state_manager, event_bus, rng)
    orchestrator.execute_skill_use(skill_result)
