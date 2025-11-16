"""Core combat engine - damage calculation and hit resolution."""

import random
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from .models import Entity, SkillUseResult, ApplyDamageAction, DispatchEventAction, ApplyEffectAction, Action
from .skills import Skill
from .events import EventBus, OnHitEvent, OnCritEvent
from .state import StateManager


@dataclass
class HitContext:
    """Data container for damage calculation pipeline.

    Accumulates values through the damage resolution stages.
    """
    attacker: Entity
    defender: Entity
    base_damage: float
    pre_mitigation_damage: float = 0.0
    mitigated_damage: float = 0.0
    final_damage: float = 0.0
    is_crit: bool = False
    # New fields for Phase 2 evasion/block pipeline
    is_glancing: bool = False
    was_dodged: bool = False
    was_blocked: bool = False
    damage_blocked: float = 0.0


class CombatEngine:
    """Static class containing core combat calculation methods.

    This engine implements the damage formulas from the Game Design Document,
    providing pure functions for hit resolution and damage calculation.
    """

    def __init__(self, rng=None):
        """Initialize CombatEngine with optional RNG for deterministic testing.

        Args:
            rng: Random number generator for reproducible results. If None,
                 uses random.random() without seeding.
        """
        self.rng = rng

    def _get_modified_chance(self, entity: Entity, state_manager: StateManager, base_chance: float, roll_type: str) -> float:
        """Calculate the final chance after applying bonus/penalty modifiers.

        Args:
            entity: The entity whose modifiers to check
            state_manager: StateManager to get entity state
            base_chance: The base percentage chance (e.g., 0.5 for 50%)
            roll_type: The type of roll (e.g., 'crit_chance', 'evasion_chance')

        Returns:
            Final modified chance, clamped to 0-1
        """
        state = state_manager.get_state(entity.id)
        if not state or not state.roll_modifiers.get(roll_type):
            return base_chance

        total_modifier = 0.0
        for mod in state.roll_modifiers[roll_type]:
            total_modifier += mod.value

        final_chance = base_chance + total_modifier
        return max(0.0, min(1.0, final_chance))  # Clamp to 0-1

    def _perform_evasion_check(self, defender: Entity, state_manager: StateManager) -> tuple[bool, bool]:
        """Perform evasion check with glancing/dodge mechanics.

        Args:
            defender: The defending entity
            state_manager: StateManager for modifiers

        Returns:
            Tuple of (was_dodged, was_glanced)
        """
        # Roll against modified evasion chance
        evasion_chance = self._get_modified_chance(defender, state_manager, defender.final_stats.evasion_chance, 'evasion_chance')
        rng_value = self.rng.random() if self.rng else random.random()

        if rng_value >= evasion_chance:
            return False, False  # Normal hit

        # If evaded, roll for dodge vs glance
        dodge_chance = self._get_modified_chance(defender, state_manager, defender.final_stats.dodge_chance, 'dodge_chance')
        rng_value = self.rng.random() if self.rng else random.random()

        # Actual dodge chance is the modified dodge chance
        # If dodge roll < modified dodge chance, it's a full dodge
        if rng_value < dodge_chance:
            return True, False  # Dodged

        return False, True  # Glanced

    def _perform_block_check(self, defender: Entity, state_manager: StateManager) -> bool:
        """Perform block check for potential damage reduction.

        Args:
            defender: The defending entity
            state_manager: StateManager for modifiers

        Returns:
            True if the attack was blocked
        """
        block_chance = self._get_modified_chance(defender, state_manager, defender.final_stats.block_chance, 'block_chance')
        rng_value = self.rng.random() if self.rng else random.random()
        return rng_value < block_chance

    def resolve_hit(self, attacker: Entity, defender: Entity, state_manager: "StateManager") -> "HitContext":
        """Calculate the damage of a single hit following the 9-step GDD pipeline.

        Args:
            attacker: The entity performing the attack
            defender: The entity receiving the attack
            state_manager: StateManager for accessing entity modifiers

        Returns:
            HitContext with complete damage calculation results and outcome flags
        """
        if state_manager is None:
            raise ValueError(
                "CombatEngine.resolve_hit() requires state_manager parameter. "
                "Hit resolution needs entity state for crit/evasion/block modifiers. "
                "Example: engine.resolve_hit(attacker, defender, state_manager)"
            )
        # Step 1: Initial Setup
        ctx = HitContext(attacker=attacker, defender=defender, base_damage=attacker.final_stats.base_damage)

        # Step 2: Evasion Check
        was_dodged, was_glanced = self._perform_evasion_check(defender, state_manager)
        if was_dodged:
            ctx.was_dodged = True
            ctx.final_damage = 0.0
            return ctx  # Early exit for dodges

        if was_glanced:
            ctx.is_glancing = True

        # Step 3: Critical Hit Check
        if not ctx.is_glancing:  # Glancing blows cannot crit
            crit_chance = self._get_modified_chance(attacker, state_manager, attacker.final_stats.crit_chance, 'crit_chance')
            rng_value = self.rng.random() if self.rng else random.random()
            if rng_value < crit_chance:
                ctx.is_crit = True

        # Step 4: Pre-Mitigation Damage Calculation
        ctx.pre_mitigation_damage = ctx.base_damage

        # Apply Tier 2 crits (Enhanced) - affects pre-mitigation
        if ctx.is_crit and attacker.get_crit_tier() == 2:
            ctx.pre_mitigation_damage *= attacker.final_stats.crit_damage

        # Step 5: Defense Mitigation (GDD formula)
        pre_pierce_damage = ctx.pre_mitigation_damage - defender.final_stats.armor
        pierced_damage = ctx.pre_mitigation_damage * attacker.final_stats.pierce_ratio
        ctx.mitigated_damage = max(0, max(pre_pierce_damage, pierced_damage))

        # Step 6: Post-Mitigation Modifiers
        ctx.final_damage = ctx.mitigated_damage

        # Apply Tier 3 crits (True) - full recalculation
        if ctx.is_crit and attacker.get_crit_tier() == 3:
            CombatEngine._apply_post_pierce_crit(ctx)

        # Step 7: Glancing Penalty
        if ctx.is_glancing:
            ctx.final_damage *= 0.5  # 50% reduction for glancing blows

        # Step 8: Block Check
        block_damage_before = ctx.final_damage
        was_blocked = self._perform_block_check(defender, state_manager)
        if was_blocked:
            ctx.was_blocked = True
            ctx.damage_blocked = min(ctx.final_damage, defender.final_stats.block_amount)
            ctx.final_damage = max(1, ctx.final_damage - ctx.damage_blocked)  # Cannot block below 1

        # Step 9: Finalization - damage ready
        return ctx

    @staticmethod
    def calculate_effective_damage(attacker: Entity, defender: Entity) -> dict:
        """Calculate detailed damage breakdown for analysis.

        Args:
            attacker: The entity performing the attack
            defender: The entity receiving the attack

        Returns:
            Dictionary with damage calculation details:
            {
                'final_damage': float,
                'attack_damage': float,
                'pre_pierce_damage': float,
                'pierced_damage': float,
                'armor_reduction': float,
                'pierce_ratio': float
            }
        """
        attack_damage = attacker.final_stats.base_damage
        defenses = defender.final_stats.armor
        pierce_ratio = attacker.final_stats.pierce_ratio

        pre_pierce_damage = attack_damage - defenses
        pierced_damage = attack_damage * pierce_ratio
        final_damage = max(pre_pierce_damage, pierced_damage)
        final_damage = max(0, final_damage)

        return {
            'final_damage': final_damage,
            'attack_damage': attack_damage,
            'pre_pierce_damage': pre_pierce_damage,
            'pierced_damage': pierced_damage,
            'armor_reduction': defenses,
            'pierce_ratio': pierce_ratio
        }

    @staticmethod
    def validate_damage_calculation(attacker: Entity, defender: Entity) -> Optional[str]:
        """Validate that a damage calculation would be valid.

        Args:
            attacker: The entity performing the attack
            defender: The entity receiving the attack

        Returns:
            None if valid, error message string if invalid
        """
        if attacker.final_stats.base_damage < 0:
            return f"Attacker base_damage cannot be negative: {attacker.final_stats.base_damage}"

        if attacker.final_stats.pierce_ratio < 0.01:
            return f"Attacker pierce_ratio below minimum: {attacker.final_stats.pierce_ratio}"

        if attacker.final_stats.pierce_ratio > 1.0:
            return f"Attacker pierce_ratio above maximum: {attacker.final_stats.pierce_ratio}"

        if defender.final_stats.armor < 0:
            return f"Defender armor cannot be negative: {defender.final_stats.armor}"

        return None

    @staticmethod
    def _apply_pre_pierce_crit(ctx: HitContext):
        """Apply pre-pierce critical hit multipliers based on crit tier.

        Tier 1 (Base Crit): Only affects base_damage (not yet implemented)
        Tier 2 (Enhanced Crit): Affects all pre-mitigation damage
        """
        crit_tier = ctx.attacker.get_crit_tier()

        if crit_tier == 2:  # Enhanced Crit
            ctx.pre_mitigation_damage *= ctx.attacker.final_stats.crit_damage

    @staticmethod
    def _apply_post_pierce_crit(ctx: HitContext):
        """Apply post-pierce critical hit multipliers based on crit tier.

        Tier 3 (True Crit): Affects post-mitigation damage
        """
        crit_tier = ctx.attacker.get_crit_tier()

        if crit_tier == 3:  # True Crit
            # Re-calculate mitigated damage using crit-boosted pre_mitigation_damage
            crit_pre_mit_damage = ctx.base_damage * ctx.attacker.final_stats.crit_damage
            pre_pierce_damage = crit_pre_mit_damage - ctx.defender.final_stats.armor
            pierced_damage = crit_pre_mit_damage * ctx.attacker.final_stats.pierce_ratio

            # Update final damage directly based on new calculation
            ctx.final_damage = max(0, max(pre_pierce_damage, pierced_damage))

    def calculate_skill_use(self, attacker: Entity, defender: Entity, skill: Skill, state_manager: StateManager) -> SkillUseResult:
        """Calculate the results of a skill use without executing actions.

        Pure function that computes all hit contexts and intended actions.
        Separates calculation from execution for architectural purity.

        Args:
            attacker: The entity using the skill
            defender: The target of the skill
            skill: The skill being used

        Returns:
            SkillUseResult containing calculated hit contexts and actions to execute
        """
        hit_results: List[HitContext] = []
        actions: List[Action] = []

        for _ in range(skill.hits):
            # 1. Resolve the damage for a single hit
            hit_context = self.resolve_hit(attacker, defender, state_manager)
            hit_results.append(hit_context)
            damage = hit_context.final_damage

            # 2. Create actions for damage application and event dispatching
            actions.append(ApplyDamageAction(
                target_id=defender.id,
                damage=damage,
                source=f"{skill.name}"
            ))

            hit_event = OnHitEvent(
                attacker=attacker,
                defender=defender,
                damage_dealt=damage,
                is_crit=hit_context.is_crit
            )
            actions.append(DispatchEventAction(event=hit_event))

            if hit_context.is_crit:
                crit_event = OnCritEvent(hit_event=hit_event)
                actions.append(DispatchEventAction(event=crit_event))

            # 3. Process Skill-Specific Triggers (create effect actions)
            for trigger in skill.triggers:
                if trigger.event == "OnHit":
                    # Calculate if trigger would proc (but don't execute randomness yet)
                    # For now, we create the action assuming it will proc - execution will check RNG
                    # TODO: Pre-calculate proc results for true determinism if needed
                    if "apply_debuff" in trigger.result:
                        actions.append(ApplyEffectAction(
                            target_id=defender.id,
                            effect_name=trigger.result["apply_debuff"],
                            stacks_to_add=trigger.result.get("stacks", 1),
                            source=f"{skill.name}_trigger"
                        ))

        return SkillUseResult(hit_results=hit_results, actions=actions)

    def process_skill_use(self, attacker: Entity, defender: Entity, skill: Skill, event_bus: EventBus, state_manager: StateManager) -> bool:
        """Process a full skill use with resource checks, executing hits and dispatching all events.

        Primary skill execution method that handles resource consumption, cooldowns,
        damage application, and comprehensive event dispatching for the full pipeline.

        Args:
            attacker: The entity using the skill
            defender: The target of the skill
            skill: The skill being used
            event_bus: The event bus for dispatching events
            state_manager: The state manager for damage/effects/resources

        Returns:
            True if skill was successfully used, False if unable (cooldown/resource issues)
        """
        from .events import OnDodgeEvent, OnBlockEvent, OnGlancingBlowEvent, OnSkillUsedEvent

        # 0. Check resource availability
        attacker_state = state_manager.get_state(attacker.id)
        if not attacker_state:
            return False  # Invalid attacker state

        # Assume skill has resource_cost (will be added to skill model)
        skill_cost = getattr(skill, 'resource_cost', 0.0)
        if attacker_state.current_resource < skill_cost:
            return False  # Insufficient resource

        # Check cooldown
        skill_name = getattr(skill, 'name', str(skill))
        if attacker_state.active_cooldowns.get(skill_name, 0) > 0:
            return False  # On cooldown

        # 1. Consume resource and set cooldown
        if skill_cost > 0:
            state_manager.spend_resource(attacker.id, skill_cost)
        if hasattr(skill, 'cooldown') and skill.cooldown > 0:
            cooldown_duration = skill.cooldown * (1.0 - attacker.final_stats.cooldown_reduction)
            state_manager.set_cooldown(attacker.id, skill_name, cooldown_duration)

        # 2. Process all hits
        for hit_num in range(skill.hits):
            # Resolve the damage for a single hit
            hit_context = self.resolve_hit(attacker, defender, state_manager)

            # Dispatch outcome-specific events first
            if hit_context.was_dodged:
                dodge_event = OnDodgeEvent(attacker=attacker, defender=defender)
                event_bus.dispatch(dodge_event)
                # Award evasion resource if applicable
                state_manager.add_resource(attacker.id, attacker.final_stats.resource_on_kill)  # Attacker evaded, treat as "kill"?
                continue  # No damage/debuffs on dodge

            # Create the hit event first
            hit_event = OnHitEvent(
                attacker=attacker,
                defender=defender,
                damage_dealt=hit_context.final_damage,
                is_crit=hit_context.is_crit
            )

            if hit_context.is_glancing:
                # OnGlancingBlowEvent for glancing hits
                event_bus.dispatch(hit_event)
                glancing_event = OnGlancingBlowEvent(hit_event=hit_event)
                event_bus.dispatch(glancing_event)

            elif hit_context.was_blocked:
                # Normal hit with block event
                event_bus.dispatch(hit_event)
                block_event = OnBlockEvent(
                    attacker=attacker,
                    defender=defender,
                    damage_before_block=hit_context.mitigated_damage + (hit_context.final_damage * 2 if hit_context.is_glancing else hit_context.final_damage),  # Pre-block damage
                    damage_blocked=hit_context.damage_blocked,
                    hit_context=hit_context
                )
                event_bus.dispatch(block_event)

            else:
                # Normal hit event only
                event_bus.dispatch(hit_event)

            # Apply damage and award resource
            if hit_context.final_damage > 0:
                state_manager.apply_damage(defender.id, hit_context.final_damage)
                state_manager.add_resource(attacker.id, attacker.final_stats.resource_on_hit)

                # OnKill resource bonus (check if defender died)
                defender_state = state_manager.get_state(defender.id)
                if defender_state and not defender_state.is_alive:
                    state_manager.add_resource(attacker.id, attacker.final_stats.resource_on_kill)

            # Dispatch crit event if critical
            if hit_context.is_crit:
                crit_event = OnCritEvent(hit_event=hit_event)
                event_bus.dispatch(crit_event)

            # Process skill triggers and active triggers
            self._process_skill_triggers(attacker, defender, skill, hit_context, event_bus, state_manager)

        # 3. Dispatch OnSkillUsed event (after execution)
        skill_used_event = OnSkillUsedEvent(entity=attacker, skill_id=str(skill), skill_type="damage")
        event_bus.dispatch(skill_used_event)

        return True  # Successfully used

    def _process_skill_triggers(self, attacker: Entity, defender: Entity, skill: Skill, hit_context: HitContext,
                               event_bus: EventBus, state_manager: StateManager):
        """Process skill triggers and active triggers for a hit context."""

        # Process skill-specific triggers
        for trigger in skill.triggers:
            if trigger.event == "OnHit" and hit_context.final_damage > 0:
                rng_value = self.rng.random() if self.rng else random.random()
                if rng_value < trigger.check.get("proc_rate", 1.0):
                    self._execute_trigger_result(trigger.result, attacker, defender, hit_context, event_bus, state_manager)

        # Process active triggers from attacker affixes
        for trigger in attacker.active_triggers:
            if trigger.event == "OnHit" and hit_context.final_damage > 0:
                rng_value = self.rng.random() if self.rng else random.random()
                if rng_value < trigger.check.get("proc_rate", 1.0):
                    self._execute_trigger_result(trigger.result, attacker, defender, hit_context, event_bus, state_manager)

            elif trigger.event == "OnSkillUsed":
                # Special case for OnSkillUsed triggers (like Focused Rage)
                rng_value = self.rng.random() if self.rng else random.random()
                if rng_value < trigger.check.get("proc_rate", 1.0):
                    self._execute_trigger_result(trigger.result, attacker, defender, hit_context, event_bus, state_manager)

        # Process defender active triggers (block/dodge effects)
        defender_state = state_manager.get_state(defender.id)
        if defender_state and defender_state.is_alive:
            for trigger in defender.active_triggers:
                if trigger.event == "OnBlock" and hit_context.was_blocked:
                    rng_value = self.rng.random() if self.rng else random.random()
                    if rng_value < trigger.check.get("proc_rate", 1.0):
                        self._execute_trigger_result(trigger.result, defender, attacker, hit_context, event_bus, state_manager)

                elif trigger.event == "OnDodge" and hit_context.was_dodged:
                    # Defender reactive effects on dodge
                    pass

    def _execute_trigger_result(self, result: Dict[str, any], source: Entity, target: Entity, hit_context: HitContext,
                              event_bus: EventBus, state_manager: StateManager):
        """Execute the result of a trigger with support for complex effects.

        Args:
            result: The trigger result dictionary
            source: Entity that triggered the effect
            target: Entity that receives the effect
            hit_context: Current hit context for damage calculations
            event_bus: Event bus for dispatching events
            state_manager: State manager for applying effects
        """
        # Standard debuff application
        if "apply_debuff" in result:
            state_manager.apply_debuff(
                entity_id=target.id,
                debuff_name=result["apply_debuff"],
                stacks_to_add=result.get("stacks", 1),
                max_duration=result.get("duration", 10.0)
            )

        # Complex effects - Phase 3
        if "apply_crit_bonus" in result:
            # Focused Rage effect - apply crit chance bonus to source
            bonus_value = result["apply_crit_bonus"]
            duration = result.get("duration", 5.0)

            # Create a crit chance modifier
            from .state import Modifier
            modifier = Modifier(
                value=bonus_value,
                duration=duration,
                source="focused_rage"
            )

            source_state = state_manager.get_state(source.id)
            if source_state:
                if 'crit_chance' not in source_state.roll_modifiers:
                    source_state.roll_modifiers['crit_chance'] = []
                source_state.roll_modifiers['crit_chance'].append(modifier)

        if "reflect_damage" in result:
            # Thornmail effect - reflect damage back to attacker
            reflect_ratio = result["reflect_damage"]
            reflected_damage = hit_context.final_damage * reflect_ratio

            if reflected_damage > 0:
                state_manager.apply_damage(source.id, reflected_damage)

                # Create reflect damage event
                from .events import OnHitEvent
                reflect_event = OnHitEvent(
                    attacker=target,  # Defender is now attacker
                    defender=source, # Attacker becomes defender
                    damage_dealt=int(reflected_damage),
                    is_crit=False
                )
                event_bus.dispatch(reflect_event)
