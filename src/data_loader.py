"""
Master Rule Data System - CSV-driven data loading for combat mechanics.
Phase 4: Complete data-driven combat system.
"""

import csv
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from .skills import Skill, Trigger
from .models import RolledAffix


@dataclass
class EffectDefinition:
    """Complete definition of an effect loaded from effects.csv"""
    effect_id: str
    name: str
    type: str  # 'buff', 'debuff', 'dot', 'stun', etc.
    description: str
    max_stacks: int = 1
    tick_rate: float = 0.0  # Seconds between ticks
    damage_per_tick: float = 0.0
    stat_multiplier: float = 0.0  # Multiplier to stats
    stat_add: float = 0.0  # Flat add to stats
    visual_effect: str = ""
    duration: float = 0.0

    def __post_init__(self):
        """Validate and convert types from CSV strings"""
        self.max_stacks = int(self.max_stacks)
        self.tick_rate = float(self.tick_rate)
        self.damage_per_tick = float(self.damage_per_tick)
        self.stat_multiplier = float(self.stat_multiplier)
        self.stat_add = float(self.stat_add)
        self.duration = float(self.duration)


@dataclass
class LoadedSkill:
    """Complete skill definition loaded from skills.csv"""
    skill_id: str
    name: str
    damage_type: str = "Physical"
    hits: int = 1
    description: str = ""
    resource_cost: float = 0.0
    cooldown: float = 0.0
    triggers: List[Trigger] = field(default_factory=list)

    def __post_init__(self):
        """Validate and convert types"""
        self.hits = int(self.hits)
        self.resource_cost = float(self.resource_cost)
        self.cooldown = float(self.cooldown)

    def to_skill_object(self) -> Skill:
        """Convert to runtime Skill object"""
        return Skill(
            id=self.skill_id,
            name=self.name,
            damage_type=self.damage_type,
            hits=self.hits,
            triggers=self.triggers
        )


class MasterRuleData:
    """Central repository for all CSV-driven combat data.
    Phase 4: Complete data-driven combat system."""

    def __init__(self, data_directory: str = "data"):
        self.data_dir = data_directory
        self.affixes: Dict[str, RolledAffix] = {}
        self.skills: Dict[str, LoadedSkill] = {}
        self.effects: Dict[str, EffectDefinition] = {}

        # Load all data on initialization
        self._load_all_data()

    def _load_all_data(self):
        """Load all CSV data files"""
        self._load_affixes()
        self._load_skills()
        self._load_effects()

    def _load_affixes(self):
        """Load affixes.csv into RolledAffix objects"""
        path = os.path.join(self.data_dir, "affixes.csv")
        if not os.path.exists(path):
            print(f"Warning: affixes.csv not found at {path}")
            return

        with open(path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    # Skip comments and invalid rows
                    if not row.get('affix_id') or row['affix_id'].startswith('#'):
                        continue

                    # Safe type conversions with fallbacks
                    try:
                        value = float(row.get('value', '0'))
                    except ValueError:
                        value = 0.0

                    try:
                        proc_rate_str = row.get('proc_rate', '0').strip()
                        proc_rate = float(proc_rate_str) if proc_rate_str else None
                    except (ValueError, TypeError):
                        proc_rate = None

                    try:
                        trigger_duration_str = row.get('trigger_duration', '0').strip()
                        trigger_duration = float(trigger_duration_str) if trigger_duration_str else None
                    except (ValueError, TypeError):
                        trigger_duration = None

                    try:
                        stacks_max_str = row.get('stacks_max', '1').strip()
                        stacks_max = int(stacks_max_str) if stacks_max_str else None
                    except (ValueError, TypeError):
                        stacks_max = None

                    try:
                        scaling_power_str = row.get('scaling_power', '').strip().lower()
                        scaling_power = scaling_power_str == 'true'
                    except:
                        scaling_power = False

                    affix = RolledAffix(
                        affix_id=row['affix_id'],
                        stat_affected=row['stat_affected'],
                        mod_type=row['mod_type'],
                        affix_pools=row.get('affix_pools', ''),
                        description=row['description'],
                        base_value=row.get('base_value', ''),
                        value=value,
                        trigger_event=row.get('trigger_event', '').strip() or None,
                        proc_rate=proc_rate,
                        trigger_result=row.get('trigger_result', '').strip() or None,
                        trigger_duration=trigger_duration,
                        stacks_max=stacks_max,
                        dual_stat=row.get('dual_stat', '').strip() or None,
                        scaling_power=scaling_power,
                        complex_effect=row.get('complex_effect', '').strip() or None
                    )
                    self.affixes[affix.affix_id] = affix

                except Exception as e:
                    print(f"Error loading affix {row.get('affix_id', 'unknown')}: {e}")

    def _load_skills(self):
        """Load skills.csv into LoadedSkill objects"""
        path = os.path.join(self.data_dir, "skills.csv")
        if not os.path.exists(path):
            print(f"Warning: skills.csv not found at {path}")
            return

        with open(path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    # Parse triggers for this skill
                    triggers = []
                    if row.get('trigger_event') and row.get('proc_rate') and row.get('trigger_result'):
                        result_dict = {}

                        # Parse trigger result (same logic as affixes)
                        if ':' in row['trigger_result']:
                            effect_name, effect_value = row['trigger_result'].split(':', 1)
                            try:
                                result_dict[effect_name] = float(effect_value)
                            except ValueError:
                                result_dict[effect_name] = effect_value
                        else:
                            result_dict["apply_debuff"] = row['trigger_result']

                        # Add metadata
                        result_dict["duration"] = float(row.get('trigger_duration', '10.0'))
                        result_dict["stacks_max"] = int(row.get('stacks_max', '1'))

                        trigger = Trigger(
                            event=row['trigger_event'],
                            check={"proc_rate": float(row['proc_rate'])},
                            result=result_dict
                        )
                        triggers.append(trigger)

                    # Create LoadedSkill
                    skill = LoadedSkill(
                        skill_id=row['skill_id'],
                        name=row['name'],
                        damage_type=row.get('damage_type', 'Physical'),
                        hits=int(row.get('hits', '1')),
                        description=row.get('description', ''),
                        resource_cost=float(row.get('resource_cost', '0')),
                        cooldown=float(row.get('cooldown', '0')),
                        triggers=triggers
                    )
                    self.skills[skill.skill_id] = skill

                except Exception as e:
                    print(f"Error loading skill {row.get('skill_id', 'unknown')}: {e}")

    def _load_effects(self):
        """Load effects.csv into EffectDefinition objects"""
        path = os.path.join(self.data_dir, "effects.csv")
        if not os.path.exists(path):
            print(f"Warning: effects.csv not found at {path}")
            return

        with open(path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    effect = EffectDefinition(
                        effect_id=row['effect_id'],
                        name=row['name'],
                        type=row['type'],
                        description=row['description'],
                        max_stacks=int(row.get('max_stacks', '1')),
                        tick_rate=float(row.get('tick_rate', '0')),
                        damage_per_tick=float(row.get('damage_per_tick', '0')),
                        stat_multiplier=float(row.get('stat_multiplier', '0')),
                        stat_add=float(row.get('stat_add', '0')),
                        visual_effect=row.get('visual_effect', ''),
                        duration=float(row.get('duration', '0'))
                    )
                    self.effects[effect.effect_id] = effect

                except Exception as e:
                    print(f"Error loading effect {row.get('effect_id', 'unknown')}: {e}")

    # Query methods
    def get_affix(self, affix_id: str) -> Optional[RolledAffix]:
        """Get affix by ID"""
        return self.affixes.get(affix_id)

    def get_skill(self, skill_id: str) -> Optional[LoadedSkill]:
        """Get skill by ID"""
        return self.skills.get(skill_id)

    def get_effect(self, effect_id: str) -> Optional[EffectDefinition]:
        """Get effect by ID"""
        return self.effects.get(effect_id)

    def get_all_affixes(self) -> List[RolledAffix]:
        """Get all loaded affixes"""
        return list(self.affixes.values())

    def get_all_skills(self) -> List[LoadedSkill]:
        """Get all loaded skills"""
        return list(self.skills.values())

    def get_all_effects(self) -> List[EffectDefinition]:
        """Get all loaded effects"""
        return list(self.effects.values())

    def find_affixes_by_pool(self, pool_name: str) -> List[RolledAffix]:
        """Find affixes that can appear in a given affix pool"""
        return [affix for affix in self.affixes.values()
                if pool_name in affix.affix_pools]

    def find_skills_by_type(self, skill_type: str) -> List[LoadedSkill]:
        """Find skills by damage type (Physical, Magic, etc.)"""
        return [skill for skill in self.skills.values()
                if skill.damage_type == skill_type]

    # Statistics methods
    def get_data_stats(self) -> Dict[str, int]:
        """Get statistics about loaded data"""
        return {
            'affixes': len(self.affixes),
            'skills': len(self.skills),
            'effects': len(self.effects)
        }

    def validate_data_consistency(self) -> List[str]:
        """Validate that all referenced effects and triggers exist"""
        issues = []

        # Check if skill trigger results reference valid effects
        for skill_id, skill in self.skills.items():
            for trigger in skill.triggers:
                if "apply_debuff" in trigger.result:
                    debuff_name = trigger.result["apply_debuff"]
                    if debuff_name not in self.effects:
                        issues.append(f"Skill {skill_id} references unknown debuff '{debuff_name}'")

        # Check if affix trigger results reference valid effects
        for affix_id, affix in self.affixes.items():
            if affix.trigger_result and affix.trigger_result not in self.effects:
                # Skip if it's a complex effect (contains colon)
                if ':' not in affix.trigger_result:
                    issues.append(f"Affix {affix_id} references unknown debuff '{affix.trigger_result}'")

        return issues


# Global instance for easy access
_global_data_loader = None

def get_data_loader() -> MasterRuleData:
    """Get the global data loader instance"""
    global _global_data_loader
    if _global_data_loader is None:
        _global_data_loader = MasterRuleData()
    return _global_data_loader

def reload_data() -> MasterRuleData:
    """Reload all CSV data (useful for development)"""
    global _global_data_loader
    _global_data_loader = MasterRuleData()
    return _global_data_loader
