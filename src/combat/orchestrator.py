"""Combat Orchestrator - Executes calculated skill actions.

Orchestrator pattern that separates action execution from calculation.
Handles the imperative side effects of combat while keeping the engine pure.
"""

from typing import TYPE_CHECKING
from src.core.rng import RNG

if TYPE_CHECKING:
    from src.core.models import SkillUseResult
    from src.core.state import StateManager
    from src.core.events import EventBus

from src.core.models import ApplyDamageAction, DispatchEventAction, ApplyEffectAction, EffectInstance


class CombatOrchestrator:
    """Orchestrates the execution of calculated combat actions.

    Takes SkillUseResult from CombatEngine and executes the actions
    via StateManager and EventBus. Handles all side effects.
    """

    def __init__(self, state_manager: "StateManager", event_bus: "EventBus", rng: RNG):
        """Initialize the orchestrator with required dependencies.

        Args:
            state_manager: The state manager for applying entity state changes
            event_bus: The event bus for dispatching combat events
            rng: RNG for effect proc rolls and other random behaviors.
                 Must not be None - all randomness must be explicit.
        
        Raises:
            AssertionError: If rng is None
        """
        assert rng is not None, "RNG must be injected into CombatOrchestrator - no global randomness allowed"
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
        # Check proc rate if less than 1.0
        should_apply = True
        if action.proc_rate < 1.0:
            rng_value = self.rng.random()
            should_apply = rng_value < action.proc_rate

        if should_apply:
            # PR8c: Updated to use modern StateManager API instead of legacy compatibility method
            # Create an EffectInstance from the action parameters
            effect = EffectInstance(
                id=f"{action.effect_name}_{action.target_id}",  # Simple unique ID
                definition_id=action.effect_name,
                source_id=action.source,
                time_remaining=10.0,  # Default duration - should be made configurable
                stacks=action.stacks_to_add,
                value=0.0,  # Will be overridden by effect definition
                tick_interval=1.0  # Default tick interval
            )
            self.state_manager.apply_effect(action.target_id, effect)


# Convenience function for executing skill results
def execute_skill_use(skill_result: "SkillUseResult", state_manager: "StateManager", event_bus: "EventBus", rng: RNG) -> None:
    """Convenience function to execute skill use results.

    Args:
        skill_result: The calculated result from CombatEngine.calculate_skill_use()
        state_manager: The state manager for applying entity state changes
        event_bus: The event bus for dispatching combat events
        rng: RNG for effect proc rolls and other random behaviors.
             Must not be None.
    """
    orchestrator = CombatOrchestrator(state_manager, event_bus, rng)
    orchestrator.execute_skill_use(skill_result)
