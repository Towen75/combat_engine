"""Combat integration layer - ties together engine, events, and state management."""

from .engine import CombatEngine, HitContext
from .events import EventBus, OnHitEvent, OnCritEvent
from .state import StateManager


def process_attack(attacker, defender, event_bus: EventBus, state_manager: StateManager) -> HitContext:
    """Process a complete attack from hit calculation through event dispatching.

    Args:
        attacker: The entity performing the attack
        defender: The entity receiving the attack
        event_bus: The event bus for dispatching combat events
        state_manager: The state manager for applying damage

    Returns:
        HitContext containing the complete damage calculation results
    """
    # Calculate the hit using the combat engine
    hit_context = CombatEngine.resolve_hit(attacker, defender)

    # Apply damage to the defender
    damage = hit_context.final_damage
    state_manager.apply_damage(defender.id, damage)

    # Dispatch the hit event
    hit_event = OnHitEvent(
        attacker=attacker,
        defender=defender,
        damage_dealt=damage,
        is_crit=hit_context.is_crit
    )
    event_bus.dispatch(hit_event)

    # Dispatch crit event if it was a critical hit
    if hit_context.is_crit:
        crit_event = OnCritEvent(hit_event=hit_event)
        event_bus.dispatch(crit_event)

    return hit_context
