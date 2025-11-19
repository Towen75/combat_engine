"""Telemetry configuration and custom formatters for simulation logging.

Provides three telemetry modes:
- Developer: DEBUG level with detailed variable changes and RNG rolls
- Designer: INFO level with aggregate statistics per fight
- Player: Custom formatter producing narrative combat text
"""

import logging
from typing import Optional


class DeveloperFormatter(logging.Formatter):
    """Formatter for Developer mode - structured logging with full context.
    
    Logs every variable change, RNG roll, and state update with timestamps.
    """
    
    def __init__(self):
        super().__init__(
            fmt='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S.%f'
        )


class DesignerFormatter(logging.Formatter):
    """Formatter for Designer mode - aggregate statistics formatting.
    
    Focuses on summary statistics per fight for balance analysis.
    """
    
    def __init__(self):
        super().__init__(
            fmt='[%(levelname)s] %(message)s'
        )


class PlayerFormatter(logging.Formatter):
    """Formatter for Player mode - natural language combat narrative.
    
    Transforms structured logs into readable text like:
    "Critical Hit! Gork deals 50 damage to Mork."
    """
    
    def __init__(self):
        super().__init__(
            fmt='%(message)s'
        )
    
    def format(self, record):
        """Transform log record into narrative text.
        
        Args:
            record: LogRecord to format
            
        Returns:
            Formatted narrative string
        """
        # Extract combat event details if present
        if hasattr(record, 'event_type'):
            if record.event_type == 'hit':
                attacker = getattr(record, 'attacker_name', 'Unknown')
                defender = getattr(record, 'defender_name', 'Unknown')
                damage = getattr(record, 'damage', 0)
                is_crit = getattr(record, 'is_crit', False)
                
                if is_crit:
                    return f"Critical Hit! {attacker} deals {damage:.1f} damage to {defender}."
                else:
                    return f"{attacker} hits {defender} for {damage:.1f} damage."
            
            elif record.event_type == 'death':
                entity_name = getattr(record, 'entity_name', 'Unknown')
                return f"{entity_name} has been defeated!"
            
            elif record.event_type == 'effect':
                target = getattr(record, 'target_name', 'Unknown')
                effect = getattr(record, 'effect_name', 'Unknown')
                return f"{target} is affected by {effect}."
        
        # Default formatting
        return super().format(record)


class SimulationFilter(logging.Filter):
    """Filter logs by simulation_id, batch_id, or entity_id.
    
    Allows focusing on specific simulations or entities during analysis.
    """
    
    def __init__(
        self,
        simulation_id: Optional[int] = None,
        batch_id: Optional[str] = None,
        entity_id: Optional[str] = None
    ):
        """Initialize the filter.
        
        Args:
            simulation_id: Only pass logs from this simulation
            batch_id: Only pass logs from this batch
            entity_id: Only pass logs involving this entity
        """
        super().__init__()
        self.simulation_id = simulation_id
        self.batch_id = batch_id
        self.entity_id = entity_id
    
    def filter(self, record):
        """Determine if record should be logged.
        
        Args:
            record: LogRecord to filter
            
        Returns:
            True if record should be logged, False otherwise
        """
        # If no filters set, pass everything
        if self.simulation_id is None and self.batch_id is None and self.entity_id is None:
            return True
        
        # Check simulation_id
        if self.simulation_id is not None:
            if not hasattr(record, 'simulation_id') or record.simulation_id != self.simulation_id:
                return False
        
        # Check batch_id
        if self.batch_id is not None:
            if not hasattr(record, 'batch_id') or record.batch_id != self.batch_id:
                return False
        
        # Check entity_id
        if self.entity_id is not None:
            attacker_id = getattr(record, 'attacker_id', None)
            defender_id = getattr(record, 'defender_id', None)
            if attacker_id != self.entity_id and defender_id != self.entity_id:
                return False
        
        return True


def configure_telemetry_mode(
    mode: str,
    logger_name: str = 'combat_simulation',
    simulation_id: Optional[int] = None,
    batch_id: Optional[str] = None,
    entity_id: Optional[str] = None
) -> logging.Logger:
    """Configure logging for a specific telemetry mode.
    
    Args:
        mode: Telemetry mode - 'developer', 'designer', or 'player'
        logger_name: Name of the logger to configure
        simulation_id: Optional filter by simulation ID
        batch_id: Optional filter by batch ID
        entity_id: Optional filter by entity ID
        
    Returns:
        Configured logger instance
        
    Raises:
        ValueError: If mode is not recognized
    """
    # Get or create logger
    logger = logging.getLogger(logger_name)
    logger.handlers.clear()  # Clear existing handlers
    logger.propagate = False  # Don't propagate to root logger
    
    # Create console handler
    handler = logging.StreamHandler()
    
    # Configure based on mode
    mode = mode.lower()
    
    if mode == 'developer':
        logger.setLevel(logging.DEBUG)
        handler.setFormatter(DeveloperFormatter())
    
    elif mode == 'designer':
        logger.setLevel(logging.INFO)
        handler.setFormatter(DesignerFormatter())
    
    elif mode == 'player':
        logger.setLevel(logging.INFO)
        handler.setFormatter(PlayerFormatter())
    
    else:
        raise ValueError(f"Unknown telemetry mode: {mode}. Use 'developer', 'designer', or 'player'.")
    
    # Add filter if specified
    if simulation_id is not None or batch_id is not None or entity_id is not None:
        sim_filter = SimulationFilter(simulation_id, batch_id, entity_id)
        handler.addFilter(sim_filter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


def log_hit_event(
    logger: logging.Logger,
    attacker_name: str,
    defender_name: str,
    damage: float,
    is_crit: bool = False,
    simulation_id: Optional[int] = None,
    batch_id: Optional[str] = None,
    attacker_id: Optional[str] = None,
    defender_id: Optional[str] = None
) -> None:
    """Log a hit event with appropriate context.
    
    Args:
        logger: Logger instance to use
        attacker_name: Name of attacking entity
        defender_name: Name of defending entity
        damage: Amount of damage dealt
        is_crit: Whether this was a critical hit
        simulation_id: Optional simulation ID
        batch_id: Optional batch ID
        attacker_id: Optional attacker entity ID
        defender_id: Optional defender entity ID
    """
    extra = {
        'event_type': 'hit',
        'attacker_name': attacker_name,
        'defender_name': defender_name,
        'damage': damage,
        'is_crit': is_crit,
        'simulation_id': simulation_id,
        'batch_id': batch_id,
        'attacker_id': attacker_id,
        'defender_id': defender_id,
    }
    
    if is_crit:
        logger.info(f"Critical hit: {attacker_name} -> {defender_name} ({damage:.1f} damage)", extra=extra)
    else:
        logger.debug(f"Hit: {attacker_name} -> {defender_name} ({damage:.1f} damage)", extra=extra)


def log_fight_summary(
    logger: logging.Logger,
    fight_number: int,
    winner: str,
    duration: float,
    dps: float,
    simulation_id: Optional[int] = None,
    batch_id: Optional[str] = None
) -> None:
    """Log a fight summary for Designer mode.
    
    Args:
        logger: Logger instance to use
        fight_number: Fight number in the batch
        winner: Name of the winning entity
        duration: Fight duration in seconds
        dps: Average DPS for the fight
        simulation_id: Optional simulation ID
        batch_id: Optional batch ID
    """
    extra = {
        'simulation_id': simulation_id,
        'batch_id': batch_id,
    }
    
    logger.info(
        f"Fight {fight_number}: {winner} wins in {duration:.1f}s, {dps:.1f} DPS",
        extra=extra
    )
