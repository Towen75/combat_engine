"""Unit tests for simulation and time-based systems (DoT ticks, etc.)."""

import pytest
from src.models import Entity, EntityStats
from src.events import EventBus
from src.state import StateManager
from tests.fixtures import make_defender


class TestDoTSystem:
    """Test damage-over-time effects and time-based simulation."""

    def test_dot_ticks_over_time(self):
        """Test that DoT effects tick correctly over time and accumulate damage."""
        # Create entity with DoT applied
        defender = make_defender(armor=0.0, max_health=1000.0)

        # Create event bus and state manager
        event_bus = EventBus()
        state_manager = StateManager()
        state_manager.register_entity(defender)

        # Apply Bleed debuff with 5 stacks
        state_manager.add_or_refresh_debuff(
            entity_id=defender.id,
            debuff_name="Bleed",
            stacks_to_add=5,
            duration=10.0  # 10 seconds
        )

        # Verify initial state
        defender_state = state_manager.get_state(defender.id)
        assert defender_state.current_health == 1000.0
        assert "Bleed" in defender_state.active_debuffs
        assert defender_state.active_debuffs["Bleed"].stacks == 5

        # Simulate 3 seconds of time (should trigger 3 ticks at 5 damage per stack = 25 damage per tick)
        state_manager.update_dot_effects(delta_time=3.0, event_bus=event_bus)

        # Check damage accumulation: 3 ticks * 5 stacks * 5 damage = 75 damage
        defender_state = state_manager.get_state(defender.id)
        assert defender_state.current_health == 1000.0 - 75.0  # 925.0

        # Check that duration decreased
        assert defender_state.active_debuffs["Bleed"].time_remaining == 7.0  # 10.0 - 3.0

    def test_dot_damage_accumulation_multiple_effects(self):
        """Test DoT damage accumulation with multiple different effects."""
        defender = make_defender(armor=0.0, max_health=1000.0)

        event_bus = EventBus()
        state_manager = StateManager()
        state_manager.register_entity(defender)

        # Apply Bleed (5 stacks) and Poison (3 stacks)
        state_manager.add_or_refresh_debuff(
            entity_id=defender.id,
            debuff_name="Bleed",
            stacks_to_add=5,
            duration=10.0
        )
        state_manager.add_or_refresh_debuff(
            entity_id=defender.id,
            debuff_name="Poison",
            stacks_to_add=3,
            duration=8.0
        )

        # Simulate 2 seconds (2 ticks)
        # Bleed: 2 * 5 * 5 = 50 damage
        # Poison: 2 * 3 * 5 = 30 damage (assuming same 5 damage per stack)
        # Total: 80 damage
        state_manager.update_dot_effects(delta_time=2.0, event_bus=event_bus)

        defender_state = state_manager.get_state(defender.id)
        assert defender_state.current_health == 1000.0 - 80.0  # 920.0

        # Check both effects are present with correct remaining durations
        assert "Bleed" in defender_state.active_debuffs
        assert "Poison" in defender_state.active_debuffs
        assert defender_state.active_debuffs["Bleed"].time_remaining == 8.0  # 10.0 - 2.0
        assert defender_state.active_debuffs["Poison"].time_remaining == 6.0  # 8.0 - 2.0

    def test_dot_effect_expiration(self):
        """Test that DoT effects expire correctly after their duration."""
        defender = make_defender(armor=0.0, max_health=1000.0)

        event_bus = EventBus()
        state_manager = StateManager()
        state_manager.register_entity(defender)

        # Apply short-duration Bleed (2 seconds)
        state_manager.add_or_refresh_debuff(
            entity_id=defender.id,
            debuff_name="Bleed",
            stacks_to_add=2,
            duration=2.0
        )

        # Verify initial state
        defender_state = state_manager.get_state(defender.id)
        assert "Bleed" in defender_state.active_debuffs
        assert defender_state.active_debuffs["Bleed"].time_remaining == 2.0

        # Simulate 1.5 seconds (1 tick, duration becomes 0.5)
        state_manager.update_dot_effects(delta_time=1.5, event_bus=event_bus)
        defender_state = state_manager.get_state(defender.id)
        assert defender_state.current_health == 1000.0 - 10.0  # 1 tick * 2 stacks * 5 damage
        assert defender_state.active_debuffs["Bleed"].time_remaining == 0.5

        # Simulate another 1 second (should tick once more, then expire)
        state_manager.update_dot_effects(delta_time=1.0, event_bus=event_bus)
        defender_state = state_manager.get_state(defender.id)
        assert defender_state.current_health == 1000.0 - 20.0  # 2 ticks * 2 stacks * 5 damage
        assert "Bleed" not in defender_state.active_debuffs  # Should be expired

    def test_dot_partial_ticks(self):
        """Test DoT ticking with partial time intervals."""
        defender = make_defender(armor=0.0, max_health=1000.0)

        event_bus = EventBus()
        state_manager = StateManager()
        state_manager.register_entity(defender)

        # Apply Bleed with 1 stack
        state_manager.add_or_refresh_debuff(
            entity_id=defender.id,
            debuff_name="Bleed",
            stacks_to_add=1,
            duration=5.0
        )

        # Simulate 0.5 seconds (no tick yet - tick_interval = 1.0)
        state_manager.update_dot_effects(delta_time=0.5, event_bus=event_bus)
        defender_state = state_manager.get_state(defender.id)
        assert defender_state.current_health == 1000.0  # No damage yet
        assert defender_state.active_debuffs["Bleed"].time_remaining == 4.5

        # Simulate 1.1 seconds in one update (should trigger 1 tick)
        state_manager.update_dot_effects(delta_time=1.1, event_bus=event_bus)
        defender_state = state_manager.get_state(defender.id)
        assert defender_state.current_health == 1000.0 - 5.0  # 1 tick * 1 stack * 5 damage
        assert defender_state.active_debuffs["Bleed"].time_remaining == 3.4  # 4.5 - 1.1

    def test_dot_stacking_behavior(self):
        """Test DoT stacking and refresh behavior over time."""
        defender = make_defender(armor=0.0, max_health=1000.0)

        event_bus = EventBus()
        state_manager = StateManager()
        state_manager.register_entity(defender)

        # Apply initial Bleed with 2 stacks
        state_manager.add_or_refresh_debuff(
            entity_id=defender.id,
            debuff_name="Bleed",
            stacks_to_add=2,
            duration=5.0
        )

        # Simulate 2 seconds (2 ticks)
        state_manager.update_dot_effects(delta_time=2.0, event_bus=event_bus)
        defender_state = state_manager.get_state(defender.id)
        assert defender_state.current_health == 1000.0 - 20.0  # 2 ticks * 2 stacks * 5 damage
        assert defender_state.active_debuffs["Bleed"].stacks == 2
        assert defender_state.active_debuffs["Bleed"].time_remaining == 3.0

        # Refresh with 3 more stacks (total should be 5)
        state_manager.add_or_refresh_debuff(
            entity_id=defender.id,
            debuff_name="Bleed",
            stacks_to_add=3,
            duration=5.0  # Reset duration
        )

        defender_state = state_manager.get_state(defender.id)
        assert defender_state.active_debuffs["Bleed"].stacks == 5  # 2 + 3
        assert defender_state.active_debuffs["Bleed"].time_remaining == 5.0  # Refreshed

        # Simulate 1 more second (1 tick with 5 stacks)
        state_manager.update_dot_effects(delta_time=1.0, event_bus=event_bus)
        defender_state = state_manager.get_state(defender.id)
        assert defender_state.current_health == 1000.0 - 45.0  # Previous 20 + 25 new damage
        assert defender_state.active_debuffs["Bleed"].stacks == 5
        assert defender_state.active_debuffs["Bleed"].time_remaining == 4.0

    def test_dot_no_damage_to_dead_entities(self):
        """Test that DoT effects don't damage already dead entities."""
        defender = make_defender(armor=0.0, max_health=1000.0)

        event_bus = EventBus()
        state_manager = StateManager()
        state_manager.register_entity(defender)

        # Apply Bleed
        state_manager.add_or_refresh_debuff(
            entity_id=defender.id,
            debuff_name="Bleed",
            stacks_to_add=1,
            duration=10.0
        )

        # Kill the entity directly
        state_manager.apply_damage(defender.id, 1000.0)
        defender_state = state_manager.get_state(defender.id)
        assert defender_state.current_health == 0.0
        assert not defender_state.is_alive

        # Simulate time - should not apply more damage
        state_manager.update_dot_effects(delta_time=2.0, event_bus=event_bus)
        defender_state = state_manager.get_state(defender.id)
        assert defender_state.current_health == 0.0  # Still 0, no additional damage

    def test_dot_event_dispatching(self):
        """Test that DoT ticks dispatch DamageTickEvent when event_bus is provided."""
        defender = make_defender(armor=0.0, max_health=1000.0)

        event_bus = EventBus()
        state_manager = StateManager()
        state_manager.register_entity(defender)

        # Track events
        received_events = []
        def event_handler(event):
            received_events.append(event)
        from src.events import DamageTickEvent
        event_bus.subscribe(DamageTickEvent, event_handler)

        # Apply Bleed
        state_manager.add_or_refresh_debuff(
            entity_id=defender.id,
            debuff_name="Bleed",
            stacks_to_add=2,
            duration=10.0
        )

        # Simulate 1 second (1 tick)
        state_manager.update_dot_effects(delta_time=1.0, event_bus=event_bus)

        # Should have received 1 DamageTickEvent
        assert len(received_events) == 1
        event = received_events[0]
        assert event.target.id == defender.id
        assert event.effect_name == "Bleed"
        assert event.damage_dealt == 10.0  # 2 stacks * 5 damage
        assert event.stacks == 2
