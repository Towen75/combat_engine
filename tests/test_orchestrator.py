"""Tests for combat_orchestrator.py - orchestration of calculated actions."""

import pytest
from unittest.mock import MagicMock, patch
from src.core.models import SkillUseResult, ApplyDamageAction, DispatchEventAction, Entity, EntityStats
from src.core.events import OnHitEvent
from src.combat.orchestrator import CombatOrchestrator, execute_skill_use
from tests.fixtures import make_entity


class TestCombatOrchestrator:
    """Test the CombatOrchestrator class functionality."""

    def test_execute_skill_use_with_damage_action(self):
        """Test executing a SkillUseResult with damage actions."""
        # Setup mocks
        state_manager = MagicMock()
        event_bus = MagicMock()

        orchestrator = CombatOrchestrator(state_manager, event_bus)

        # Create a fake SkillUseResult with damage action
        attacker = make_entity("attacker")
        defender = make_entity("defender")

        hit_results = []  # Empty for this test
        actions = [
            ApplyDamageAction(target_id=defender.id, damage=100.0, source="test_skill")
        ]

        result = SkillUseResult(hit_results=hit_results, actions=actions)

        # Execute
        orchestrator.execute_skill_use(result)

        # Verify damage was applied
        state_manager.apply_damage.assert_called_once_with(defender.id, 100.0)

        # Verify no events were dispatched (no DispatchEventAction in actions)
        event_bus.dispatch.assert_not_called()

    def test_execute_skill_use_with_event_action(self):
        """Test executing a SkillUseResult with event actions."""
        # Setup mocks
        state_manager = MagicMock()
        event_bus = MagicMock()

        orchestrator = CombatOrchestrator(state_manager, event_bus)

        # Create a fake SkillUseResult with event action
        attacker = make_entity("attacker")
        defender = make_entity("defender")

        mock_event = OnHitEvent(
            attacker=attacker,
            defender=defender,
            damage_dealt=50.0,
            is_crit=False
        )

        actions = [
            DispatchEventAction(event=mock_event)
        ]

        result = SkillUseResult(hit_results=[], actions=actions)

        # Execute
        orchestrator.execute_skill_use(result)

        # Verify event was dispatched
        event_bus.dispatch.assert_called_once_with(mock_event)

        # Verify no damage was applied
        state_manager.apply_damage.assert_not_called()

    def test_execute_skill_use_with_multiple_actions(self):
        """Test executing multiple actions in sequence."""
        # Setup mocks
        state_manager = MagicMock()
        event_bus = MagicMock()

        orchestrator = CombatOrchestrator(state_manager, event_bus)

        # Create multiple actions
        attacker = make_entity("attacker")
        defender = make_entity("defender")

        damage_action = ApplyDamageAction(target_id=defender.id, damage=75.0, source="multi_action_skill")
        mock_event = OnHitEvent(attacker=attacker, defender=defender, damage_dealt=75.0, is_crit=False)
        event_action = DispatchEventAction(event=mock_event)

        actions = [damage_action, event_action]

        result = SkillUseResult(hit_results=[], actions=actions)

        # Execute
        orchestrator.execute_skill_use(result)

        # Verify both actions were executed in order
        assert state_manager.apply_damage.call_count == 1
        assert event_bus.dispatch.call_count == 1

        state_manager.apply_damage.assert_called_with(defender.id, 75.0)
        event_bus.dispatch.assert_called_with(mock_event)

    def test_execute_skill_use_unknown_action_type(self):
        """Test handling of unknown action types."""
        # Setup mocks
        state_manager = MagicMock()
        event_bus = MagicMock()

        orchestrator = CombatOrchestrator(state_manager, event_bus)

        # Create a custom unknown action
        class UnknownAction:
            pass

        actions = [UnknownAction()]

        result = SkillUseResult(hit_results=[], actions=actions)

        # Execute and expect ValueError
        with pytest.raises(ValueError, match="Unknown action type"):
            orchestrator.execute_skill_use(result)


    def test_execute_skill_use_with_rng_for_triggers(self):
        """Test that actions can be executed with RNG provided."""
        # Test basic execution with RNG for future trigger logic
        state_manager = MagicMock()
        event_bus = MagicMock()
        rng_mock = MagicMock()

        orchestrator = CombatOrchestrator(state_manager, event_bus, rng=rng_mock)

        # Create a known action type
        defender = make_entity("defender")
        actions = [ApplyDamageAction(target_id=defender.id, damage=25.0, source="test_skill")]

        result = SkillUseResult(hit_results=[], actions=actions)

        # Execute - should work with ApplyDamageAction
        orchestrator.execute_skill_use(result)

        # Verify damage was applied
        state_manager.apply_damage.assert_called_once_with(defender.id, 25.0)
        # For now, it just ensures the method runs without error

    def test_execute_skill_use_empty_result(self):
        """Test executing a SkillUseResult with no actions."""
        state_manager = MagicMock()
        event_bus = MagicMock()

        orchestrator = CombatOrchestrator(state_manager, event_bus)

        result = SkillUseResult(hit_results=[], actions=[])

        # Should execute without error
        orchestrator.execute_skill_use(result)

        # No methods should be called
        state_manager.apply_damage.assert_not_called()
        event_bus.dispatch.assert_not_called()


class TestExecuteSkillUseConvenienceFunction:
    """Test the convenience function execute_skill_use."""

    def test_execute_skill_use_convenience_function(self):
        """Test the standalone convenience function."""
        state_manager = MagicMock()
        event_bus = MagicMock()
        rng = MagicMock()

        attacker = make_entity("attacker")
        defender = make_entity("defender")

        # Create a simple result
        damage_action = ApplyDamageAction(target_id=defender.id, damage=25.0, source="convenience_test")
        result = SkillUseResult(hit_results=[], actions=[damage_action])

        # Execute using convenience function
        execute_skill_use(result, state_manager, event_bus, rng)

        # Verify it worked
        state_manager.apply_damage.assert_called_once_with(defender.id, 25.0)
        event_bus.dispatch.assert_not_called()

    def test_execute_skill_use_convenience_function_no_rng(self):
        """Test convenience function without explicit RNG."""
        state_manager = MagicMock()
        event_bus = MagicMock()

        defender = make_entity("defender")
        damage_action = ApplyDamageAction(target_id=defender.id, damage=10.0, source="no_rng_test")
        result = SkillUseResult(hit_results=[], actions=[damage_action])

        # Execute without rng parameter
        execute_skill_use(result, state_manager, event_bus)

        # Should still work (orchestrator will create its own RNG)
        state_manager.apply_damage.assert_called_once_with(defender.id, 10.0)
