"""Unit tests for skill system - multi-hit skills and triggers."""

import pytest
from src.core.models import Entity, EntityStats
from src.core.skills import Skill, Trigger
from src.core.events import EventBus
from src.core.state import StateManager
from src.combat.engine import CombatEngine
from src.handlers.effect_handlers import BleedHandler
from tests.fixtures import make_rng, make_attacker, make_defender


class TestSkillSystem:
    """Test skill system functionality."""

    def test_multi_hit_skill_basic(self):
        """Test that multi-hit skills execute the correct number of hits."""
        from tests.fixtures import make_rng

        # Create entities
        attacker = make_attacker(base_damage=50.0)
        defender = make_defender(armor=0.0, max_health=1000.0)

        # Create event bus and state manager
        event_bus = EventBus()
        state_manager = StateManager()
        state_manager.register_entity(attacker)
        state_manager.register_entity(defender)

        # Create engine with deterministic RNG (no crits)
        engine = CombatEngine(rng=make_rng(1))  # Seed that won't trigger crits

        # Create 3-hit skill with no triggers
        skill = Skill(
            id="test_skill",
            name="Test Multi-Hit",
            hits=3,
            triggers=[]
        )

        # Execute skill
        engine.process_skill_use(attacker, defender, skill, event_bus, state_manager)

        # Check that 3 hits were applied (50 damage * 3 = 150 total)
        defender_state = state_manager.get_state(defender.id)
        assert defender_state.current_health == 1000.0 - 150.0  # 850.0

    def test_multi_hit_skill_with_triggers_deterministic(self):
        """Test multi-hit skill with triggers using deterministic RNG."""
        # Create entities
        attacker = make_attacker(base_damage=50.0)
        defender = make_defender(armor=0.0, max_health=1000.0)

        # Create event bus and state manager
        event_bus = EventBus()
        state_manager = StateManager()
        state_manager.register_entity(attacker)
        state_manager.register_entity(defender)

        # Create Bleed handler with deterministic RNG
        rng = make_rng(42)
        bleed_handler = BleedHandler(event_bus, state_manager, proc_rate=1.0, rng=rng)  # 100% proc for testing

        # Create engine with RNG that will trigger procs on specific hits
        # We need to control the RNG sequence for proc checks
        rng = make_rng(42)  # This will give us predictable proc outcomes
        engine = CombatEngine(rng=rng)

        # Create skill with trigger that has 50% proc rate
        skill = Skill(
            id="bleed_skill",
            name="Bleed Strike",
            hits=4,  # Test with 4 hits
            triggers=[
                Trigger(
                    event="OnHit",
                    check={"proc_rate": 0.5},  # 50% chance
                    result={"apply_debuff": "Bleed", "stacks": 1}
                )
            ]
        )

        # Execute skill
        engine.process_skill_use(attacker, defender, skill, event_bus, state_manager)

        # Check damage (4 hits * 50 damage = 200 total)
        defender_state = state_manager.get_state(defender.id)
        assert defender_state.current_health == 1000.0 - 200.0  # 800.0

        # Check that some bleeds were applied (with deterministic RNG, we expect specific outcomes)
        # The exact number depends on the RNG sequence, but we should have at least some bleeds
        # Check that some bleeds were applied (with deterministic RNG, we expect specific outcomes)
        # The exact number depends on the RNG sequence, but we should have at least some bleeds
        effects = state_manager.get_active_effects(defender.id)
        assert len(effects) > 0
        assert any(e.definition_id == "Bleed" for e in effects)

    def test_multi_hit_skill_per_hit_independence(self):
        """Test that each hit in a multi-hit skill is independent."""
        # Create entities
        attacker = make_attacker(base_damage=100.0, crit_chance=0.0)  # No crits
        defender = make_defender(armor=0.0, max_health=1000.0)

        # Create event bus and state manager
        event_bus = EventBus()
        state_manager = StateManager()
        state_manager.register_entity(attacker)
        state_manager.register_entity(defender)

        # Create engine
        from tests.fixtures import make_rng
        engine = CombatEngine(rng=make_rng(42))

        # Create 2-hit skill
        skill = Skill(
            id="double_hit",
            name="Double Hit",
            hits=2,
            triggers=[]
        )

        # Execute skill
        engine.process_skill_use(attacker, defender, skill, event_bus, state_manager)

        # Check that exactly 2 hits were applied (100 * 2 = 200 damage)
        defender_state = state_manager.get_state(defender.id)
        assert defender_state.current_health == 1000.0 - 200.0  # 800.0

    def test_skill_trigger_proc_rates_with_deterministic_rng(self):
        """Test skill trigger proc rates with deterministic RNG for predictable outcomes."""
        # Create entities
        attacker = make_attacker(base_damage=50.0)
        defender = make_defender(armor=0.0, max_health=1000.0)

        # Create event bus and state manager
        event_bus = EventBus()
        state_manager = StateManager()
        state_manager.register_entity(attacker)
        state_manager.register_entity(defender)

        # NOTE: Not creating BleedHandler to avoid double application

        # Create engine with RNG that gives predictable proc outcomes
        rng = make_rng(123)  # Specific seed for predictable results
        engine = CombatEngine(rng=rng)

        # Create skill with guaranteed proc trigger
        skill = Skill(
            id="guaranteed_bleed",
            name="Guaranteed Bleed",
            hits=1,
            triggers=[
                Trigger(
                    event="OnHit",
                    check={"proc_rate": 1.0},  # 100% proc
                    result={"apply_debuff": "Bleed", "stacks": 2}
                )
            ]
        )

        # Execute skill
        engine.process_skill_use(attacker, defender, skill, event_bus, state_manager)

        # Check damage (1 hit * 50 damage = 50 total)
        defender_state = state_manager.get_state(defender.id)
        assert defender_state.current_health == 1000.0 - 50.0  # 950.0

        # Check that bleed was applied with correct stacks
        # Check that bleed was applied with correct stacks
        assert state_manager.get_effect_stacks(defender.id, "Bleed") == 2

    def test_multi_hit_skill_state_accumulation(self):
        """Test that multi-hit skills properly accumulate state changes."""
        # Create entities
        attacker = make_attacker(base_damage=25.0)
        defender = make_defender(armor=0.0, max_health=1000.0)

        # Create event bus and state manager
        event_bus = EventBus()
        state_manager = StateManager()
        state_manager.register_entity(attacker)
        state_manager.register_entity(defender)

        # NOTE: Not creating BleedHandler to avoid double application

        # Create engine
        from tests.fixtures import make_rng
        engine = CombatEngine(rng=make_rng(42))

        # Create 4-hit skill where each hit applies 1 stack of bleed
        skill = Skill(
            id="stacking_bleed",
            name="Stacking Bleed",
            hits=4,
            triggers=[
                Trigger(
                    event="OnHit",
                    check={"proc_rate": 1.0},  # Guaranteed proc
                    result={"apply_debuff": "Bleed", "stacks": 1}
                )
            ]
        )

        # Execute skill
        engine.process_skill_use(attacker, defender, skill, event_bus, state_manager)

        # Check damage accumulation (4 hits * 25 damage = 100 total)
        defender_state = state_manager.get_state(defender.id)
        assert defender_state.current_health == 1000.0 - 100.0  # 900.0

        # Check stack accumulation (4 procs * 1 stack each = 4 total stacks)
        # Check stack accumulation (4 procs * 1 stack each = 4 total stacks)
        assert state_manager.get_effect_stacks(defender.id, "Bleed") == 4
