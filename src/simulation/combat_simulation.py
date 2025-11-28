"""Simulation framework for combat testing and balancing.

Provides automated combat simulation, logging, and reporting tools for
validating balance and performance.
"""

import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from collections import defaultdict
from src.core.rng import RNG

if TYPE_CHECKING:
    from src.core.models import Entity
    from src.core.events import OnHitEvent, DamageTickEvent, Item

# Import for runtime use
from src.core.events import OnHitEvent, DamageTickEvent
from src.core.loot_manager import LootManager
from src.handlers.loot_handler import LootHandler
from src.core.events import LootDroppedEvent # Add to imports


@dataclass
class CombatLogEntry:
    """Represents a single event in the combat log.

    Used to track all combat events for analysis and reporting.
    """
    timestamp: float
    event_type: str
    attacker_id: Optional[str] = None
    defender_id: Optional[str] = None
    damage_dealt: Optional[float] = None
    is_crit: bool = False
    effect_name: Optional[str] = None
    effect_stacks: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CombatLogger:
    """Logs and analyzes combat events for simulation and balancing.

    Records all combat events and provides methods for analysis and reporting.
    """

    def __init__(self):
        """Initialize the combat logger."""
        self.entries: List[CombatLogEntry] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def start_logging(self) -> None:
        """Start the logging session."""
        self.start_time = time.time()
        self.entries.clear()

    def stop_logging(self) -> None:
        """Stop the logging session."""
        self.end_time = time.time()

    def log_hit(self, attacker_id: str, defender_id: str, damage: float, is_crit: bool = False) -> None:
        """Log a hit event.

        Args:
            attacker_id: ID of the attacking entity
            defender_id: ID of the defending entity
            damage: Amount of damage dealt
            is_crit: Whether this was a critical hit
        """
        entry = CombatLogEntry(
            timestamp=time.time(),
            event_type="hit",
            attacker_id=attacker_id,
            defender_id=defender_id,
            damage_dealt=damage,
            is_crit=is_crit
        )
        self.entries.append(entry)

    def log_effect_application(self, target_id: str, effect_name: str, stacks: int) -> None:
        """Log an effect application event.

        Args:
            target_id: ID of the entity affected
            effect_name: Name of the effect applied
            stacks: Number of stacks applied
        """
        entry = CombatLogEntry(
            timestamp=time.time(),
            event_type="effect_apply",
            defender_id=target_id,
            effect_name=effect_name,
            effect_stacks=stacks
        )
        self.entries.append(entry)

    def log_damage_tick(self, target_id: str, effect_name: str, damage: float) -> None:
        """Log a damage-over-time tick event.

        Args:
            target_id: ID of the entity taking damage
            effect_name: Name of the DoT effect
            damage: Amount of damage dealt by the tick
        """
        entry = CombatLogEntry(
            timestamp=time.time(),
            event_type="damage_tick",
            defender_id=target_id,
            effect_name=effect_name,
            damage_dealt=damage
        )
        self.entries.append(entry)

    def log_loot_drop(self, source_id: str, items: List[Any]) -> None:
        """Log a loot drop event.

        Args:
            source_id: ID of the entity that dropped loot
            items: List of Item instances dropped
        """
        # Extract item names for cleaner logs
        item_summary = [{"name": i.name, "rarity": i.rarity} for i in items]
        entry = CombatLogEntry(
            timestamp=time.time(),
            event_type="loot_drop",
            attacker_id=source_id,  # Reusing field for source
            metadata={"items": item_summary}
        )
        self.entries.append(entry)

    def log_death(self, entity_id: str) -> None:
        """Log an entity death event.

        Args:
            entity_id: ID of the entity that died
        """
        entry = CombatLogEntry(
            timestamp=time.time(),
            event_type="death",
            defender_id=entity_id
        )
        self.entries.append(entry)

    def get_damage_breakdown(self) -> Dict[str, Dict[str, float]]:
        """Get a breakdown of damage dealt by each attacker.

        Returns:
            Dictionary mapping attacker IDs to damage statistics
        """
        breakdown = defaultdict(lambda: {"total_damage": 0.0, "crit_damage": 0.0, "normal_damage": 0.0, "hits": 0, "crits": 0})

        for entry in self.entries:
            if entry.event_type == "hit" and entry.attacker_id and entry.damage_dealt is not None:
                attacker_stats = breakdown[entry.attacker_id]
                attacker_stats["total_damage"] += entry.damage_dealt
                attacker_stats["hits"] += 1

                if entry.is_crit:
                    attacker_stats["crit_damage"] += entry.damage_dealt
                    attacker_stats["crits"] += 1
                else:
                    attacker_stats["normal_damage"] += entry.damage_dealt

        return dict(breakdown)

    def get_effect_uptime(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Get effect uptime statistics.

        Returns:
            Dictionary mapping entity IDs to effect statistics
        """
        effect_stats = defaultdict(lambda: defaultdict(lambda: {"applications": 0, "total_ticks": 0, "total_damage": 0.0}))

        for entry in self.entries:
            if entry.event_type == "effect_apply" and entry.defender_id and entry.effect_name:
                effect_stats[entry.defender_id][entry.effect_name]["applications"] += 1
            elif entry.event_type == "damage_tick" and entry.defender_id and entry.effect_name and entry.damage_dealt:
                effect_stats[entry.defender_id][entry.effect_name]["total_ticks"] += 1
                effect_stats[entry.defender_id][entry.effect_name]["total_damage"] += entry.damage_dealt

        return dict(effect_stats)

    def get_loot_report(self) -> Dict[str, Any]:
        """Generate summary of dropped loot."""
        total_drops = 0
        total_items = 0
        rarity_counts = defaultdict(int)

        for entry in self.entries:
            if entry.event_type == "loot_drop":
                total_drops += 1
                items = entry.metadata.get("items", [])
                total_items += len(items)
                for item in items:
                    rarity_counts[item['rarity']] += 1

        return {
            "total_drops": total_drops,
            "total_items": total_items,
            "rarity_breakdown": dict(rarity_counts)
        }

    def get_simulation_duration(self) -> float:
        """Get the total duration of the logged simulation.

        Returns:
            Duration in seconds, or 0 if logging not properly started/stopped
        """
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

    def get_total_events(self) -> int:
        """Get the total number of logged events.

        Returns:
            Number of events in the log
        """
        return len(self.entries)

    def get_events_per_second(self) -> float:
        """Get the average events per second during simulation.

        Returns:
            Events per second, or 0 if no duration
        """
        duration = self.get_simulation_duration()
        if duration > 0:
            return len(self.entries) / duration
        return 0.0

    def clear(self) -> None:
        """Clear all logged entries."""
        self.entries.clear()
        self.start_time = None
        self.end_time = None


class SimulationRunner:
    """Runs automated combat simulations with time-based progression.

    Manages the simulation loop, entity attacks, and effect processing.
    """

    def __init__(self, combat_engine, state_manager, event_bus, rng: RNG, logger: Optional[CombatLogger] = None, loot_manager: Optional[LootManager] = None):
        """Initialize the simulation runner.

        Args:
            combat_engine: The combat engine for damage calculations
            state_manager: The state manager for entity states
            event_bus: The event bus for dispatching events
            rng: RNG for random target selection and other behaviors.
                 Must not be None - all randomness must be explicit.
            logger: Optional combat logger for recording events
            loot_manager: Optional loot manager for handling loot drops

        Raises:
            AssertionError: If rng is None
        """
        assert rng is not None, "RNG must be injected into SimulationRunner - no global randomness allowed"
        self.combat_engine = combat_engine
        self.state_manager = state_manager
        self.event_bus = event_bus
        self.rng = rng
        self.logger = logger or CombatLogger()
        self.loot_manager = loot_manager

        # Simulation state
        self.entities: List["Entity"] = []
        self.attack_timers: Dict[str, float] = {}
        self.simulation_time: float = 0.0
        self.is_running: bool = False

        # Initialize Loot Handler if manager is provided
        if self.loot_manager:
            self.loot_handler = LootHandler(self.event_bus, self.state_manager, self.loot_manager)

        # Set up event subscriptions for logging
        self._setup_event_subscriptions()

    def _setup_event_subscriptions(self) -> None:
        """Set up event subscriptions for logging combat events."""
        if self.logger:
            self.event_bus.subscribe(OnHitEvent, self._log_hit_event)
            self.event_bus.subscribe(DamageTickEvent, self._log_damage_tick_event)
            if hasattr(self.logger, 'log_loot_drop'):
                self.event_bus.subscribe(LootDroppedEvent, self._log_loot_event)

    def _log_hit_event(self, event) -> None:
        """Log a hit event."""
        self.logger.log_hit(
            attacker_id=event.attacker.id,
            defender_id=event.defender.id,
            damage=event.damage_dealt,
            is_crit=event.is_crit
        )

    def _log_damage_tick_event(self, event) -> None:
        """Log a damage tick event."""
        self.logger.log_damage_tick(
            target_id=event.target.id,
            effect_name=event.effect_name,
            damage=event.damage_dealt
        )

    def _log_loot_event(self, event) -> None:
        """Log a loot drop event."""
        self.logger.log_loot_drop(event.source_id, event.items)

    def add_entity(self, entity: "Entity") -> None:
        """Add an entity to the simulation."""
        if entity not in self.entities:
            self.entities.append(entity)
            
            # --- THIS CHECK IS REQUIRED ---
            # Check if already registered to prevent "Entity already registered" crash
            if not self.state_manager.is_registered(entity.id):
                self.state_manager.register_entity(entity)
            # ------------------------------
                
            # Initialize attack timer
            speed = max(0.1, entity.final_stats.attack_speed)
            self.attack_timers[entity.id] = 1.0 / speed

    def remove_entity(self, entity_id: str) -> None:
        """Remove an entity from the simulation.

        Args:
            entity_id: ID of the entity to remove
        """
        self.entities = [e for e in self.entities if e.id != entity_id]
        self.state_manager.unregister_entity(entity_id)
        if entity_id in self.attack_timers:
            del self.attack_timers[entity_id]

    def get_random_target(self, attacker_id: str) -> Optional["Entity"]:
        """Get a random living target for an attacker.

        Args:
            attacker_id: ID of the attacking entity

        Returns:
            A random living target, or None if no valid targets
        """
        living_entities = [
            entity for entity in self.entities
            if entity.id != attacker_id and self.state_manager.get_state(entity.id).is_alive
        ]
        return self.rng.choice(living_entities) if living_entities else None

    def update(self, delta_time: float, force_update: bool = False) -> None:
        """Update the simulation by the given time delta.

        Args:
            delta_time: Time elapsed since last update in seconds
            force_update: If True, update even when simulation is not running (for testing)
        """
        if not self.is_running and not force_update:
            return

        if self.is_running:  # Only update simulation time during actual runs
            self.simulation_time += delta_time

        # Update attack timers and process attacks
        for entity in self.entities[:]:  # Copy list to avoid modification during iteration
            if not self.state_manager.get_state(entity.id).is_alive:
                continue

            # Only update attack timers for entities that have them (i.e., can attack)
            if entity.id in self.attack_timers:
                self.attack_timers[entity.id] -= delta_time

                # Check if it's time to attack
                if self.attack_timers[entity.id] <= 0:
                    target = self.get_random_target(entity.id)
                    if target:
                        # Perform attack using the combat engine
                        hit_context = self.combat_engine.resolve_hit(entity, target, self.state_manager)

                        # Apply damage
                        damage = hit_context.final_damage
                        self.state_manager.apply_damage(target.id, damage)

                        # Dispatch events
                        from src.core.events import OnHitEvent, OnCritEvent
                        hit_event = OnHitEvent(
                            attacker=entity,
                            defender=target,
                            damage_dealt=damage,
                            is_crit=hit_context.was_crit
                        )
                        self.event_bus.dispatch(hit_event)

                        if hit_context.was_crit:
                            crit_event = OnCritEvent(hit_event=hit_event)
                            self.event_bus.dispatch(crit_event)

                        # Reset attack timer
                        self.attack_timers[entity.id] = 1.0 / entity.final_stats.attack_speed

        # Update DoT effects (PR4: centralized tick processing)
        self.state_manager.tick(delta_time, self.event_bus)

    def run_simulation(self, duration: float, time_step: float = 0.1) -> None:
        """Run a simulation for the specified duration.

        Args:
            duration: Total simulation time in seconds
            time_step: Time step for each update in seconds
        """
        self.logger.start_logging()
        self.is_running = True
        self.simulation_time = 0.0

        try:
            while self.simulation_time < duration:
                step_time = min(time_step, duration - self.simulation_time)
                self.update(step_time)
        finally:
            self.is_running = False
            self.logger.stop_logging()

    def get_simulation_report(self) -> Dict[str, Any]:
        """Get a comprehensive report of the simulation results.

        Returns:
            Dictionary containing simulation statistics and analysis
        """
        return {
            "duration": self.logger.get_simulation_duration(),
            "total_events": self.logger.get_total_events(),
            "events_per_second": self.logger.get_events_per_second(),
            "damage_breakdown": self.logger.get_damage_breakdown(),
            "effect_uptime": self.logger.get_effect_uptime(),
            "loot_analysis": self.logger.get_loot_report(),
            "final_entity_states": {
                entity_id: {
                    "health": state.current_health,
                    "is_alive": state.is_alive,
                    "active_debuffs": list(state.active_debuffs.keys())
                }
                for entity_id, state in self.state_manager.get_all_states().items()
            }
        }

    def reset(self) -> None:
        """Reset the simulation state."""
        self.entities.clear()
        self.attack_timers.clear()
        self.simulation_time = 0.0
        self.is_running = False
        self.state_manager.reset()
        self.logger.clear()


class ReportGenerator:
    """Generates detailed reports and analysis from simulation data.

    Provides balance analysis, performance metrics, and actionable insights.
    """

    def __init__(self, logger: CombatLogger):
        """Initialize the report generator.

        Args:
            logger: The combat logger containing simulation data
        """
        self.logger = logger

    def generate_damage_report(self) -> Dict[str, Any]:
        """Generate a comprehensive damage analysis report.

        Returns:
            Dictionary containing damage statistics and analysis
        """
        damage_breakdown = self.logger.get_damage_breakdown()

        # Calculate aggregate statistics
        total_damage = sum(stats["total_damage"] for stats in damage_breakdown.values())
        total_hits = sum(stats["hits"] for stats in damage_breakdown.values())
        total_crits = sum(stats["crits"] for stats in damage_breakdown.values())

        # Calculate averages
        avg_damage_per_hit = total_damage / total_hits if total_hits > 0 else 0
        crit_rate = total_crits / total_hits if total_hits > 0 else 0

        # Per-entity analysis
        entity_analysis = {}
        for entity_id, stats in damage_breakdown.items():
            entity_analysis[entity_id] = {
                "total_damage": stats["total_damage"],
                "damage_percentage": (stats["total_damage"] / total_damage * 100) if total_damage > 0 else 0,
                "hits": stats["hits"],
                "crits": stats["crits"],
                "crit_rate": stats["crits"] / stats["hits"] if stats["hits"] > 0 else 0,
                "avg_damage_per_hit": stats["total_damage"] / stats["hits"] if stats["hits"] > 0 else 0,
                "avg_crit_damage": stats["crit_damage"] / stats["crits"] if stats["crits"] > 0 else 0,
                "avg_normal_damage": stats["normal_damage"] / (stats["hits"] - stats["crits"]) if (stats["hits"] - stats["crits"]) > 0 else 0
            }

        return {
            "summary": {
                "total_damage": total_damage,
                "total_hits": total_hits,
                "total_crits": total_crits,
                "overall_crit_rate": crit_rate,
                "avg_damage_per_hit": avg_damage_per_hit
            },
            "entity_breakdown": entity_analysis
        }

    def generate_effect_report(self) -> Dict[str, Any]:
        """Generate a comprehensive effect analysis report.

        Returns:
            Dictionary containing effect statistics and analysis
        """
        effect_uptime = self.logger.get_effect_uptime()

        # Calculate aggregate statistics
        total_applications = 0
        total_ticks = 0
        total_dot_damage = 0.0

        effect_analysis = {}
        for entity_id, effects in effect_uptime.items():
            entity_effects = {}
            for effect_name, stats in effects.items():
                total_applications += stats["applications"]
                total_ticks += stats["total_ticks"]
                total_dot_damage += stats["total_damage"]

                entity_effects[effect_name] = {
                    "applications": stats["applications"],
                    "total_ticks": stats["total_ticks"],
                    "total_damage": stats["total_damage"],
                    "avg_damage_per_tick": stats["total_damage"] / stats["total_ticks"] if stats["total_ticks"] > 0 else 0
                }

            effect_analysis[entity_id] = entity_effects

        return {
            "summary": {
                "total_applications": total_applications,
                "total_ticks": total_ticks,
                "total_dot_damage": total_dot_damage,
                "avg_damage_per_tick": total_dot_damage / total_ticks if total_ticks > 0 else 0
            },
            "entity_breakdown": effect_analysis
        }

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate a performance analysis report.

        Returns:
            Dictionary containing performance metrics
        """
        duration = self.logger.get_simulation_duration()
        total_events = self.logger.get_total_events()
        events_per_second = self.logger.get_events_per_second()

        return {
            "simulation_duration": duration,
            "total_events": total_events,
            "events_per_second": events_per_second,
            "performance_rating": self._calculate_performance_rating(events_per_second)
        }

    def _calculate_performance_rating(self, events_per_second: float) -> str:
        """Calculate a performance rating based on events per second.

        Args:
            events_per_second: Average events per second

        Returns:
            Performance rating string
        """
        if events_per_second >= 1000:
            return "Excellent"
        elif events_per_second >= 500:
            return "Good"
        elif events_per_second >= 100:
            return "Fair"
        else:
            return "Poor"

    def generate_balance_insights(self) -> Dict[str, Any]:
        """Generate balance analysis insights.

        Returns:
            Dictionary containing balance analysis and recommendations
        """
        damage_report = self.generate_damage_report()
        effect_report = self.generate_effect_report()

        insights = {
            "damage_distribution": self._analyze_damage_distribution(damage_report),
            "effect_balance": self._analyze_effect_balance(effect_report),
            "recommendations": self._generate_recommendations(damage_report, effect_report)
        }

        return insights

    def _analyze_damage_distribution(self, damage_report: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze damage distribution for balance insights.

        Args:
            damage_report: The damage report data

        Returns:
            Analysis of damage distribution
        """
        entity_breakdown = damage_report["entity_breakdown"]
        damage_percentages = [stats["damage_percentage"] for stats in entity_breakdown.values()]

        if not damage_percentages:
            return {"distribution": "insufficient_data"}

        max_damage_pct = max(damage_percentages)
        min_damage_pct = min(damage_percentages)
        avg_damage_pct = sum(damage_percentages) / len(damage_percentages)

        # Calculate variance
        variance = sum((pct - avg_damage_pct) ** 2 for pct in damage_percentages) / len(damage_percentages)

        return {
            "distribution_type": "balanced" if variance < 100 else "unbalanced",
            "max_damage_percentage": max_damage_pct,
            "min_damage_percentage": min_damage_pct,
            "variance": variance,
            "range": max_damage_pct - min_damage_pct
        }

    def _analyze_effect_balance(self, effect_report: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze effect balance for insights.

        Args:
            effect_report: The effect report data

        Returns:
            Analysis of effect balance
        """
        entity_breakdown = effect_report["entity_breakdown"]

        # Count entities with effects vs without
        entities_with_effects = len([e for e in entity_breakdown.values() if e])
        total_entities = len(entity_breakdown)

        return {
            "entities_with_effects": entities_with_effects,
            "total_entities": total_entities,
            "effect_coverage": entities_with_effects / total_entities if total_entities > 0 else 0
        }

    def _generate_recommendations(self, damage_report: Dict[str, Any], effect_report: Dict[str, Any]) -> List[str]:
        """Generate balance recommendations based on analysis.

        Args:
            damage_report: The damage report data
            effect_report: The effect report data

        Returns:
            List of recommendations
        """
        recommendations = []

        # Damage distribution recommendations
        damage_dist = self._analyze_damage_distribution(damage_report)
        if damage_dist.get("distribution_type") == "unbalanced":
            recommendations.append("Consider balancing damage output - high variance detected in damage distribution")

        # Effect recommendations
        effect_balance = self._analyze_effect_balance(effect_report)
        if effect_balance.get("effect_coverage", 0) < 0.5:
            recommendations.append("Effects are underutilized - consider increasing proc rates or effect triggers")

        # Performance recommendations
        perf_report = self.generate_performance_report()
        if perf_report.get("performance_rating") == "Poor":
            recommendations.append("Simulation performance is poor - consider optimizing event handling")

        return recommendations if recommendations else ["Simulation appears well-balanced"]

    def generate_full_report(self) -> Dict[str, Any]:
        """Generate a complete simulation analysis report.

        Returns:
            Comprehensive report with all analysis sections
        """
        return {
            "damage_analysis": self.generate_damage_report(),
            "effect_analysis": self.generate_effect_report(),
            "performance_analysis": self.generate_performance_report(),
            "balance_insights": self.generate_balance_insights(),
            "generated_at": time.time()
        }
