"""Tests for effect_handlers.py - event-driven effect systems."""

import pytest
from unittest.mock import MagicMock, patch
from src.models import DamageOnHitConfig
from src.effect_handlers import DamageOnHitHandler, BleedHandler, PoisonHandler
from src.events import EventBus, OnHitEvent
from src.state import StateManager
from tests.fixtures import make_entity, make_rng


class TestDamageOnHitConfig:
    """Test the DamageOnHitConfig data structure."""

    def test_config_creation(self):
        """Test creating a DamageOnHitConfig."""
        config = DamageOnHitConfig(
            debuff_name="Burn",
            proc_rate=0.25,
            duration=6.0,
            damage_per_tick=3.0,
            stacks_to_add=1,
            display_message="Burn proc'd on {target}!"
        )

        assert config.debuff_name == "Burn"
        assert config.proc_rate == 0.25
        assert config.duration == 6.0
        assert config.damage_per_tick == 3.0
        assert config.stacks_to_add == 1
        assert config.display_message == "Burn proc'd on {target}!"

    def test_config_defaults(self):
        """Test DamageOnHitConfig default values."""
        config = DamageOnHitConfig(
            debuff_name="Frost",
            proc_rate=0.4,
            duration=10.0,
            damage_per_tick=2.0
        )

        assert config.stacks_to_add == 1  # Default value
        assert config.display_message == ""  # Default value


class TestDamageOnHitHandler:
    """Test the generic DamageOnHitHandler class."""

    def test_handler_creation(self):
        """Test creating a DamageOnHitHandler with config."""
        config = DamageOnHitConfig(
            debuff_name="Burn",
            proc_rate=0.5,
            duration=6.0,
            damage_per_tick=5.0
        )

        event_bus = MagicMock()
        state_manager = MagicMock()

        handler = DamageOnHitHandler(config, event_bus, state_manager)

        assert handler.config == config
        assert handler.event_bus == event_bus
        assert handler.state_manager == state_manager

    def test_handler_subscribes_to_on_hit(self):
        """Test that the handler subscribes to OnHitEvent."""
        config = DamageOnHitConfig(
            debuff_name="Test",
            proc_rate=1.0,  # Guarantee proc for testing
            duration=5.0,
            damage_per_tick=1.0
        )

        event_bus = MagicMock()
        state_manager = MagicMock()

        handler = DamageOnHitHandler(config, event_bus, state_manager)

        # Verify subscription was called
        event_bus.subscribe.assert_called_once()
        args = event_bus.subscribe.call_args
        assert args[0][0] == OnHitEvent  # Event type
        assert args[0][1] == handler.handle_on_hit  # Handler method

    def test_handle_on_hit_guaranteed_proc(self):
        """Test handle_on_hit with guaranteed proc."""
        config = DamageOnHitConfig(
            debuff_name="TestEffect",
            proc_rate=1.0,  # Guaranteed proc
            duration=5.0,
            damage_per_tick=1.0,
            display_message="Custom message for {target}!"
        )

        event_bus = MagicMock()
        state_manager = MagicMock()

        handler = DamageOnHitHandler(config, event_bus, state_manager, rng=make_rng(42))

        attacker = make_entity("attacker")
        defender = make_entity("defender", name="TestDefender")

        event = OnHitEvent(
            attacker=attacker,
            defender=defender,
            damage_dealt=10.0,
            is_crit=False
        )

        # Capture print output for display message
        with patch('builtins.print') as mock_print:
            handler.handle_on_hit(event)

        # Verify custom message was printed
        mock_print.assert_called_once_with("    -> Custom message for TestDefender!")

        # Verify debuff was applied to state manager
        state_manager.apply_debuff.assert_called_once_with(
            entity_id=defender.id,
            debuff_name="TestEffect",
            stacks_to_add=1,
            max_duration=5.0
        )

    def test_handle_on_hit_no_proc(self):
        """Test handle_on_hit with no proc (proc_rate = 0)."""
        config = DamageOnHitConfig(
            debuff_name="NoProcEffect",
            proc_rate=0.0,  # Never procs
            duration=5.0,
            damage_per_tick=1.0
        )

        event_bus = MagicMock()
        state_manager = MagicMock()

        handler = DamageOnHitHandler(config, event_bus, state_manager, rng=make_rng(42))

        attacker = make_entity("attacker")
        defender = make_entity("defender")

        event = OnHitEvent(
            attacker=attacker,
            defender=defender,
            damage_dealt=10.0,
            is_crit=False
        )

        handler.handle_on_hit(event)

        # Verify nothing was applied
        state_manager.apply_debuff.assert_not_called()

    def test_handle_on_hit_default_message(self):
        """Test handle_on_hit with default message when no custom message configured."""
        config = DamageOnHitConfig(
            debuff_name="DefaultEffect",
            proc_rate=1.0,
            duration=3.0,
            damage_per_tick=2.0
            # No display_message - should use default
        )

        event_bus = MagicMock()
        state_manager = MagicMock()

        handler = DamageOnHitHandler(config, event_bus, state_manager, rng=make_rng(42))

        attacker = make_entity("attacker")
        defender = make_entity("defender")

        event = OnHitEvent(
            attacker=attacker,
            defender=defender,
            damage_dealt=15.0,
            is_crit=False
        )

        # Test that proc occurred and debuff was applied (without testing print output)
        # Import capture to redirect stdout for testing
        import io
        import sys
        from contextlib import redirect_stdout

        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            handler.handle_on_hit(event)

        output = captured_output.getvalue()
        assert "DefaultEffect proc'd on defender!" in output

        # Verify debuff was applied
        state_manager.apply_debuff.assert_called_once_with(
            entity_id=defender.id,
            debuff_name="DefaultEffect",
            stacks_to_add=1,
            max_duration=3.0
        )


class TestBleedHandlerLegacy:
    """Test the legacy BleedHandler for backward compatibility."""

    def test_bleed_handler_creation(self):
        """Test creating a BleedHandler."""
        event_bus = MagicMock()
        state_manager = MagicMock()

        handler = BleedHandler(event_bus, state_manager, proc_rate=0.6, rng=make_rng(42))

        assert handler.proc_rate == 0.6
        event_bus.subscribe.assert_called_once_with(OnHitEvent, handler.handle_on_hit)

    def test_bleed_handler_proc(self):
        """Test BleedHandler applying bleed effect."""
        event_bus = MagicMock()
        state_manager = MagicMock()

        handler = BleedHandler(event_bus, state_manager, proc_rate=1.0, rng=make_rng(42))

        attacker = make_entity("attacker")
        defender = make_entity("defender")

        event = OnHitEvent(attacker=attacker, defender=defender, damage_dealt=10.0, is_crit=False)

        with patch('builtins.print') as mock_print:
            handler.handle_on_hit(event)

        mock_print.assert_called_once_with("    -> Bleed proc'd on defender!")

        state_manager.apply_debuff.assert_called_once_with(
            entity_id=defender.id,
            debuff_name="Bleed",
            stacks_to_add=1,
            max_duration=5.0
        )


class TestPoisonHandlerLegacy:
    """Test the legacy PoisonHandler for backward compatibility."""

    def test_poison_handler_creation(self):
        """Test creating a PoisonHandler."""
        event_bus = MagicMock()
        state_manager = MagicMock()

        handler = PoisonHandler(event_bus, state_manager, proc_rate=0.4, rng=make_rng(42))

        assert handler.proc_rate == 0.4
        event_bus.subscribe.assert_called_once_with(OnHitEvent, handler.handle_on_hit)

    def test_poison_handler_proc(self):
        """Test PoisonHandler applying poison effect."""
        event_bus = MagicMock()
        state_manager = MagicMock()

        handler = PoisonHandler(event_bus, state_manager, proc_rate=1.0, rng=make_rng(42))

        attacker = make_entity("attacker")
        defender = make_entity("defender")

        event = OnHitEvent(attacker=attacker, defender=defender, damage_dealt=10.0, is_crit=False)

        with patch('builtins.print') as mock_print:
            handler.handle_on_hit(event)

        mock_print.assert_called_once_with("    -> Poison proc'd on defender!")

        state_manager.apply_debuff.assert_called_once_with(
            entity_id=defender.id,
            debuff_name="Poison",
            stacks_to_add=1,
            max_duration=8.0
        )
