"""Tests for telemetry configuration and formatters.

Validates logging modes and custom formatters.
"""

import pytest
import logging
from src.simulation.telemetry import (
    configure_telemetry_mode,
    DeveloperFormatter,
    DesignerFormatter,
    PlayerFormatter,
    SimulationFilter
)


class TestTelemetryConfiguration:
    """Test telemetry mode configuration."""
    
    def test_developer_mode_configuration(self):
        """Test Developer mode sets DEBUG level."""
        logger = configure_telemetry_mode('developer', logger_name='test_dev')
        
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, DeveloperFormatter)
    
    def test_designer_mode_configuration(self):
        """Test Designer mode sets INFO level."""
        logger = configure_telemetry_mode('designer', logger_name='test_designer')
        
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, DesignerFormatter)
    
    def test_player_mode_configuration(self):
        """Test Player mode sets INFO level with custom formatter."""
        logger = configure_telemetry_mode('player', logger_name='test_player')
        
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, PlayerFormatter)
    
    def test_invalid_mode_raises_error(self):
        """Test that invalid mode raises ValueError."""
        with pytest.raises(ValueError, match="Unknown telemetry mode"):
            configure_telemetry_mode('invalid_mode', logger_name='test_invalid')
    
    def test_filter_by_simulation_id(self):
        """Test filtering by simulation ID."""
        logger = configure_telemetry_mode(
            'developer',
            logger_name='test_filter_sim',
            simulation_id=42
        )
        
        # Check that filter is applied
        assert len(logger.handlers) == 1
        handler = logger.handlers[0]
        assert len(handler.filters) == 1
        assert isinstance(handler.filters[0], SimulationFilter)


class TestSimulationFilter:
    """Test simulation filter functionality."""
    
    def test_filter_passes_all_when_no_criteria(self):
        """Test filter passes all records when no criteria set."""
        sim_filter = SimulationFilter()
        
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='test message',
            args=(),
            exc_info=None
        )
        
        assert sim_filter.filter(record) is True
    
    def test_filter_by_simulation_id(self):
        """Test filtering by simulation ID."""
        sim_filter = SimulationFilter(simulation_id=42)
        
        # Record with matching simulation_id
        record_match = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg='test', args=(), exc_info=None
        )
        record_match.simulation_id = 42
        
        # Record with non-matching simulation_id
        record_no_match = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg='test', args=(), exc_info=None
        )
        record_no_match.simulation_id = 99
        
        assert sim_filter.filter(record_match) is True
        assert sim_filter.filter(record_no_match) is False
    
    def test_filter_by_batch_id(self):
        """Test filtering by batch ID."""
        sim_filter = SimulationFilter(batch_id="test_batch")
        
        record_match = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg='test', args=(), exc_info=None
        )
        record_match.batch_id = "test_batch"
        
        record_no_match = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg='test', args=(), exc_info=None
        )
        record_no_match.batch_id = "other_batch"
        
        assert sim_filter.filter(record_match) is True
        assert sim_filter.filter(record_no_match) is False


class TestPlayerFormatter:
    """Test Player mode narrative formatter."""
    
    def test_format_critical_hit(self):
        """Test formatting of critical hit events."""
        formatter = PlayerFormatter()
        
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg='test', args=(), exc_info=None
        )
        record.event_type = 'hit'
        record.attacker_name = 'Gork'
        record.defender_name = 'Mork'
        record.damage = 50.0
        record.is_crit = True
        
        formatted = formatter.format(record)
        
        assert "Critical Hit!" in formatted
        assert "Gork" in formatted
        assert "Mork" in formatted
        assert "50" in formatted
    
    def test_format_normal_hit(self):
        """Test formatting of normal hit events."""
        formatter = PlayerFormatter()
        
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg='test', args=(), exc_info=None
        )
        record.event_type = 'hit'
        record.attacker_name = 'Warrior'
        record.defender_name = 'Mage'
        record.damage = 25.0
        record.is_crit = False
        
        formatted = formatter.format(record)
        
        assert "Warrior" in formatted
        assert "Mage" in formatted
        assert "25" in formatted
        assert "Critical" not in formatted
    
    def test_format_death_event(self):
        """Test formatting of death events."""
        formatter = PlayerFormatter()
        
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg='test', args=(), exc_info=None
        )
        record.event_type = 'death'
        record.entity_name = 'Goblin'
        
        formatted = formatter.format(record)
        
        assert "Goblin" in formatted
        assert "defeated" in formatted
