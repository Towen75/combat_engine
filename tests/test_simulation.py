"""Unit tests for simulation framework components."""

import pytest
import time
from unittest.mock import Mock, patch
from src.simulation import CombatLogEntry, CombatLogger, SimulationRunner, ReportGenerator
from src.models import Entity, EntityStats
from src.state import StateManager
from src.events import EventBus, OnHitEvent, DamageTickEvent
from src.engine import CombatEngine


class TestCombatLogEntry:
    """Test CombatLogEntry dataclass."""

    def test_combat_log_entry_creation(self):
        """Test creating a CombatLogEntry."""
        timestamp = time.time()
        entry = CombatLogEntry(
            timestamp=timestamp,
            event_type="hit",
            attacker_id="attacker1",
            defender_id="defender1",
            damage_dealt=25.0,
            is_crit=True,
            metadata={"test": "data"}
        )

        assert entry.timestamp == timestamp
        assert entry.event_type == "hit"
        assert entry.attacker_id == "attacker1"
        assert entry.defender_id == "defender1"
        assert entry.damage_dealt == 25.0
        assert entry.is_crit is True
        assert entry.metadata == {"test": "data"}


class TestCombatLogger:
    """Test CombatLogger functionality."""

    def test_logger_initialization(self):
        """Test CombatLogger initialization."""
        logger = CombatLogger()
        assert logger.entries == []
        assert logger.start_time is None
        assert logger.end_time is None

    def test_logging_session(self):
        """Test logging session start/stop."""
        logger = CombatLogger()

        logger.start_logging()
        assert logger.start_time is not None
        assert logger.end_time is None

        time.sleep(0.01)  # Small delay
        logger.stop_logging()
        assert logger.end_time is not None
        assert logger.end_time > logger.start_time

    def test_log_hit(self):
        """Test logging hit events."""
        logger = CombatLogger()
        logger.start_logging()

        logger.log_hit("attacker1", "defender1", 25.0, True)

        assert len(logger.entries) == 1
        entry = logger.entries[0]
        assert entry.event_type == "hit"
        assert entry.attacker_id == "attacker1"
        assert entry.defender_id == "defender1"
        assert entry.damage_dealt == 25.0
        assert entry.is_crit is True

    def test_log_effect_application(self):
        """Test logging effect application events."""
        logger = CombatLogger()
        logger.start_logging()

        logger.log_effect_application("target1", "Bleed", 2)

        assert len(logger.entries) == 1
        entry = logger.entries[0]
        assert entry.event_type == "effect_apply"
        assert entry.defender_id == "target1"
        assert entry.effect_name == "Bleed"
        assert entry.effect_stacks == 2

    def test_log_damage_tick(self):
        """Test logging damage tick events."""
        logger = CombatLogger()
        logger.start_logging()

        logger.log_damage_tick("target1", "Bleed", 10.0)

        assert len(logger.entries) == 1
        entry = logger.entries[0]
        assert entry.event_type == "damage_tick"
        assert entry.defender_id == "target1"
        assert entry.effect_name == "Bleed"
        assert entry.damage_dealt == 10.0

    def test_damage_breakdown(self):
        """Test damage breakdown calculation."""
        logger = CombatLogger()
        logger.start_logging()

        # Add some hit events
        logger.log_hit("attacker1", "defender1", 20.0, False)
        logger.log_hit("attacker1", "defender1", 40.0, True)
        logger.log_hit("attacker2", "defender1", 15.0, False)

        breakdown = logger.get_damage_breakdown()

        assert "attacker1" in breakdown
        assert "attacker2" in breakdown

        attacker1_stats = breakdown["attacker1"]
        assert attacker1_stats["total_damage"] == 60.0
        assert attacker1_stats["hits"] == 2
        assert attacker1_stats["crits"] == 1
        assert attacker1_stats["crit_damage"] == 40.0
        assert attacker1_stats["normal_damage"] == 20.0

    def test_effect_uptime(self):
        """Test effect uptime calculation."""
        logger = CombatLogger()
        logger.start_logging()

        # Add effect events
        logger.log_effect_application("target1", "Bleed", 1)
        logger.log_damage_tick("target1", "Bleed", 5.0)
        logger.log_damage_tick("target1", "Bleed", 5.0)
        logger.log_effect_application("target1", "Poison", 2)
        logger.log_damage_tick("target1", "Poison", 8.0)

        uptime = logger.get_effect_uptime()

        assert "target1" in uptime
        target1_effects = uptime["target1"]

        assert "Bleed" in target1_effects
        assert target1_effects["Bleed"]["applications"] == 1
        assert target1_effects["Bleed"]["total_ticks"] == 2
        assert target1_effects["Bleed"]["total_damage"] == 10.0

        assert "Poison" in target1_effects
        assert target1_effects["Poison"]["applications"] == 1
        assert target1_effects["Poison"]["total_ticks"] == 1
        assert target1_effects["Poison"]["total_damage"] == 8.0

    def test_simulation_duration(self):
        """Test simulation duration calculation."""
        logger = CombatLogger()

        # No timing
        assert logger.get_simulation_duration() == 0.0

        logger.start_logging()
        time.sleep(0.01)
        logger.stop_logging()

        duration = logger.get_simulation_duration()
        assert duration > 0.0
        assert duration < 1.0  # Should be small

    def test_events_per_second(self):
        """Test events per second calculation."""
        logger = CombatLogger()

        # No timing
        assert logger.get_events_per_second() == 0.0

        logger.start_logging()
        logger.log_hit("a", "b", 10.0)
        logger.log_hit("a", "b", 10.0)
        time.sleep(0.01)
        logger.stop_logging()

        eps = logger.get_events_per_second()
        assert eps > 0.0


class TestSimulationRunner:
    """Test SimulationRunner functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.combat_engine = Mock(spec=CombatEngine)
        self.state_manager = Mock(spec=StateManager)
        self.event_bus = Mock(spec=EventBus)
        self.logger = CombatLogger()

        self.runner = SimulationRunner(
            self.combat_engine,
            self.state_manager,
            self.event_bus,
            self.logger
        )

    def test_initialization(self):
        """Test SimulationRunner initialization."""
        assert self.runner.combat_engine == self.combat_engine
        assert self.runner.state_manager == self.state_manager
        assert self.runner.event_bus == self.event_bus
        assert self.runner.logger == self.logger
        assert self.runner.entities == []
        assert self.runner.attack_timers == {}
        assert self.runner.simulation_time == 0.0
        assert self.runner.is_running is False

    def test_add_entity(self):
        """Test adding entities to simulation."""
        entity = Mock(spec=Entity)
        entity.id = "test_entity"
        entity.final_stats = Mock()
        entity.final_stats.attack_speed = 1.0

        self.state_manager.register_entity = Mock()

        self.runner.add_entity(entity)

        assert entity in self.runner.entities
        assert "test_entity" in self.runner.attack_timers
        assert self.runner.attack_timers["test_entity"] == 1.0
        self.state_manager.register_entity.assert_called_once_with(entity)

    def test_get_random_target(self):
        """Test random target selection."""
        # Create mock entities
        entity1 = Mock(spec=Entity)
        entity1.id = "entity1"
        entity2 = Mock(spec=Entity)
        entity2.id = "entity2"
        entity3 = Mock(spec=Entity)
        entity3.id = "entity3"

        # Set up state manager mock
        self.state_manager.get_state.side_effect = lambda eid: Mock(is_alive=eid != "entity2")

        self.runner.entities = [entity1, entity2, entity3]

        # Test with attacker that has living targets
        target = self.runner.get_random_target("entity1")
        assert target is not None
        assert target.id in ["entity2", "entity3"]  # entity2 is dead, so only entity3

        # Test with no living targets
        self.state_manager.get_state.side_effect = lambda eid: Mock(is_alive=False)
        target = self.runner.get_random_target("entity1")
        assert target is None

    @patch('random.choice')
    def test_update_attack_logic(self, mock_choice):
        """Test attack logic during update."""
        # Create mock entities
        attacker = Mock(spec=Entity)
        attacker.id = "attacker"
        attacker.final_stats = Mock()
        attacker.final_stats.attack_speed = 1.0
        target = Mock(spec=Entity)
        target.id = "target"

        self.runner.entities = [attacker, target]
        self.runner.attack_timers = {"attacker": 0.5}  # Only attacker has timer

        # Set up mocks - attacker is alive, target is alive
        self.state_manager.get_state.side_effect = lambda eid: Mock(is_alive=True)
        mock_choice.return_value = target
        self.combat_engine.resolve_hit = Mock()

        # Update with delta time that triggers attack (force_update=True to bypass is_running check)
        self.runner.update(0.6, force_update=True)  # Timer goes from 0.5 to -0.1, triggering attack

        # Verify attack was attempted
        self.combat_engine.resolve_hit.assert_called_once_with(attacker, target)

        # Verify timer was reset
        assert self.runner.attack_timers["attacker"] == 1.0  # Reset to 1.0 / attack_speed

    def test_update_dot_effects(self):
        """Test DoT effect updates."""
        self.state_manager.update_dot_effects = Mock()

        self.runner.update(0.1, force_update=True)

        self.state_manager.update_dot_effects.assert_called_once_with(0.1, self.event_bus)

    def test_run_simulation(self):
        """Test running a complete simulation."""
        # Mock the update method but preserve simulation time tracking
        original_update = self.runner.update
        call_count = 0

        def mock_update(delta_time, force_update=False):
            nonlocal call_count
            call_count += 1
            # Simulate what the real update does for simulation time
            if self.runner.is_running:
                self.runner.simulation_time += delta_time

        self.runner.update = mock_update

        # Run simulation
        self.runner.run_simulation(1.0, 0.1)

        # Verify logging was started and stopped
        assert self.runner.logger.start_time is not None
        assert self.runner.logger.end_time is not None

        # Verify update was called multiple times (should be called ~10 times for 1.0 duration with 0.1 steps)
        assert call_count >= 10  # At least 10 calls for 1 second with 0.1 step

        # Verify simulation time was tracked
        assert self.runner.simulation_time >= 1.0

    def test_get_simulation_report(self):
        """Test simulation report generation."""
        # Mock logger methods
        self.logger.get_simulation_duration = Mock(return_value=10.0)
        self.logger.get_total_events = Mock(return_value=100)
        self.logger.get_events_per_second = Mock(return_value=10.0)
        self.logger.get_damage_breakdown = Mock(return_value={"test": "data"})
        self.logger.get_effect_uptime = Mock(return_value={"test": "effects"})

        # Mock state manager
        self.state_manager.get_all_states = Mock(return_value={
            "entity1": Mock(current_health=50.0, is_alive=True, active_debuffs={})
        })

        report = self.runner.get_simulation_report()

        assert report["duration"] == 10.0
        assert report["total_events"] == 100
        assert report["events_per_second"] == 10.0
        assert "damage_breakdown" in report
        assert "effect_uptime" in report
        assert "final_entity_states" in report


class TestReportGenerator:
    """Test ReportGenerator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.logger = Mock(spec=CombatLogger)
        self.generator = ReportGenerator(self.logger)

    def test_generate_damage_report(self):
        """Test damage report generation."""
        # Mock logger damage breakdown
        self.logger.get_damage_breakdown.return_value = {
            "attacker1": {"total_damage": 100.0, "hits": 10, "crits": 2, "crit_damage": 40.0, "normal_damage": 60.0},
            "attacker2": {"total_damage": 50.0, "hits": 5, "crits": 0, "crit_damage": 0.0, "normal_damage": 50.0}
        }

        report = self.generator.generate_damage_report()

        assert "summary" in report
        assert "entity_breakdown" in report

        summary = report["summary"]
        assert summary["total_damage"] == 150.0
        assert summary["total_hits"] == 15
        assert summary["total_crits"] == 2
        assert summary["overall_crit_rate"] == 2/15
        assert summary["avg_damage_per_hit"] == 150.0/15

    def test_generate_effect_report(self):
        """Test effect report generation."""
        # Mock logger effect uptime
        self.logger.get_effect_uptime.return_value = {
            "target1": {
                "Bleed": {"applications": 2, "total_ticks": 10, "total_damage": 50.0},
                "Poison": {"applications": 1, "total_ticks": 5, "total_damage": 25.0}
            }
        }

        report = self.generator.generate_effect_report()

        assert "summary" in report
        assert "entity_breakdown" in report

        summary = report["summary"]
        assert summary["total_applications"] == 3
        assert summary["total_ticks"] == 15
        assert summary["total_dot_damage"] == 75.0

    def test_generate_performance_report(self):
        """Test performance report generation."""
        self.logger.get_simulation_duration.return_value = 30.0
        self.logger.get_total_events.return_value = 1500
        self.logger.get_events_per_second.return_value = 50.0

        report = self.generator.generate_performance_report()

        assert report["simulation_duration"] == 30.0
        assert report["total_events"] == 1500
        assert report["events_per_second"] == 50.0
        assert report["performance_rating"] == "Poor"  # 50 EPS is poor performance

    def test_generate_balance_insights(self):
        """Test balance insights generation."""
        # Mock damage report with unbalanced distribution
        damage_report = {
            "summary": {"total_damage": 100.0},
            "entity_breakdown": {
                "entity1": {"damage_percentage": 90.0},
                "entity2": {"damage_percentage": 10.0}
            }
        }

        effect_report = {
            "entity_breakdown": {"entity1": {}, "entity2": {}}
        }

        # Mock the internal methods
        self.generator.generate_damage_report = Mock(return_value=damage_report)
        self.generator.generate_effect_report = Mock(return_value=effect_report)
        self.generator.generate_performance_report = Mock(return_value={"performance_rating": "Good"})

        insights = self.generator.generate_balance_insights()

        assert "damage_distribution" in insights
        assert "effect_balance" in insights
        assert "recommendations" in insights
        assert len(insights["recommendations"]) > 0

    def test_generate_full_report(self):
        """Test full report generation."""
        # Mock all the individual report methods
        self.generator.generate_damage_report = Mock(return_value={"damage": "data"})
        self.generator.generate_effect_report = Mock(return_value={"effect": "data"})
        self.generator.generate_performance_report = Mock(return_value={"performance": "data"})
        self.generator.generate_balance_insights = Mock(return_value={"insights": "data"})

        report = self.generator.generate_full_report()

        assert "damage_analysis" in report
        assert "effect_analysis" in report
        assert "performance_analysis" in report
        assert "balance_insights" in report
        assert "generated_at" in report
