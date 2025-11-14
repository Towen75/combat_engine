"""Core combat engine - damage calculation and hit resolution."""

import random
from dataclasses import dataclass
from typing import Optional, List
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

    def resolve_hit(self, attacker: Entity, defender: Entity) -> HitContext:
        """Calculate the damage of a single hit with critical hit support.

        Implements the core damage formula with crit tier progression:
        Damage Dealt = MAX((Attack Damage - Defences), (Attack Damage * Pierce Ratio))

        Args:
            attacker: The entity performing the attack
            defender: The entity receiving the attack

        Returns:
            HitContext with complete damage calculation results
        """
        # --- 1. Initial Setup ---
        ctx = HitContext(attacker=attacker, defender=defender, base_damage=attacker.final_stats.base_damage)

        # --- 2. Critical Hit Check ---
        # Use injected RNG for deterministic testing, fallback to random.random()
        rng_value = self.rng.random() if self.rng else random.random()
        if rng_value < attacker.final_stats.crit_chance:
            ctx.is_crit = True

        # --- 3. Pre-Mitigation Damage Calculation ---
        # For now, this is just base damage. Phase 3 will add flat bonuses here.
        ctx.pre_mitigation_damage = ctx.base_damage

        # Apply Tier 1/2 crits (Base/Pre-Pierce)
        if ctx.is_crit:
            CombatEngine._apply_pre_pierce_crit(ctx)

        # --- 4. Mitigation Calculation (The GDD formula) ---
        pre_pierce_damage = ctx.pre_mitigation_damage - defender.final_stats.armor
        pierced_damage = ctx.pre_mitigation_damage * attacker.final_stats.pierce_ratio
        ctx.mitigated_damage = max(0, max(pre_pierce_damage, pierced_damage))

        # --- 5. Final Damage & Post-Mitigation Crits ---
        # Phase 3 will add final multipliers here.
        ctx.final_damage = ctx.mitigated_damage

        # Apply Tier 3 crits (Post-Pierce)
        if ctx.is_crit:
            CombatEngine._apply_post_pierce_crit(ctx)

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

    def calculate_skill_use(self, attacker: Entity, defender: Entity, skill: Skill) -> SkillUseResult:
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
            hit_context = self.resolve_hit(attacker, defender)
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

    def process_skill_use(self, attacker: Entity, defender: Entity, skill: Skill, event_bus: EventBus, state_manager: StateManager):
        """Process a full skill use, including all hits and triggers.

        Args:
            attacker: The entity using the skill
            defender: The target of the skill
            skill: The skill being used
            event_bus: The event bus for dispatching events
            state_manager: The state manager for applying effects
        """
        for _ in range(skill.hits):
            # 1. Resolve the damage for a single hit
            hit_context = self.resolve_hit(attacker, defender)
            damage = hit_context.final_damage
            state_manager.apply_damage(defender.id, damage)

            # 2. Dispatch core events (OnHit, OnCrit)
            hit_event = OnHitEvent(
                attacker=attacker,
                defender=defender,
                damage_dealt=damage,
                is_crit=hit_context.is_crit
            )
            event_bus.dispatch(hit_event)

            if hit_context.is_crit:
                crit_event = OnCritEvent(hit_event=hit_event)
                event_bus.dispatch(crit_event)

            # 3. Process Skill-Specific Triggers
            for trigger in skill.triggers:
                if trigger.event == "OnHit":
                    # Perform the check (e.g., proc rate)
                    rng_value = self.rng.random() if self.rng else random.random()
                    if rng_value < trigger.check.get("proc_rate", 1.0):
                        # Execute the result
                        if "apply_debuff" in trigger.result:
                            state_manager.add_or_refresh_debuff(
                                entity_id=defender.id,
                                debuff_name=trigger.result["apply_debuff"],
                                stacks_to_add=trigger.result.get("stacks", 1)
                            )
