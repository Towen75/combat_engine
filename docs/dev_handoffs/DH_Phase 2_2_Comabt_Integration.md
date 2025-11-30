# 🚀 Implementation Hand-off: Phase 2.2 - Combat Integration (Revised v2)

**Related Work Item:** `WI_Phase_2_2.md` (Combat Integration)

## 📦 File Manifest
| Action | File Path | Description |
| :---: | :--- | :--- |
| ✏️ Modify | `src/core/skills.py` | Add `damage_multiplier` to runtime `Skill` class |
| ✏️ Modify | `src/core/models.py` | Add `get_default_attack_skill_id` to `Entity` |
| ✏️ Modify | `src/core/factory.py` | Add `create_runtime_skill` helper with full trigger support |
| ✏️ Modify | `src/combat/engine.py` | Apply multiplier in `calculate_skill_use` |
| ✏️ Modify | `src/simulation/combat_simulation.py` | Update Runner to use skills, Provider, and Logging |
| ✏️ Modify | `src/game/session.py` | Pass provider to SimulationRunner |
| ✏️ Modify | `run_simulation.py` | Pass provider to SimulationRunner |
| 🆕 Create | `tests/test_weapon_mechanics.py` | Unit tests for multiplier logic and fallback |

---

## 1️⃣ Configuration & Dependencies
*No new pip packages required.*

---

## 2️⃣ Code Changes

### A. `src/core/skills.py`
**Path:** `src/core/skills.py`
**Context:** Add the multiplier field.

```python
@dataclass
class Skill:
    """Represents a combat skill with triggers."""
    id: str
    name: str
    damage_type: str = "Physical"
    hits: int = 1
    cooldown: float = 0.0
    resource_cost: float = 0.0
    damage_multiplier: float = 1.0  # <--- NEW FIELD
    triggers: List[Trigger] = field(default_factory=list)
```

### B. `src/core/models.py`
**Path:** `src/core/models.py`
**Context:** Logic to lookup weapon skill ID.

```python
# ... inside Entity class ...

    def get_default_attack_skill_id(self) -> str:
        """
        Determine the skill ID to use for auto-attacks based on equipment.
        
        Returns:
            Skill ID string (e.g., 'attack_dagger', 'attack_unarmed')
        """
        # Note: Ensure ItemSlot.WEAPON value matches dictionary key ("Weapon" usually)
        weapon = self.equipment.get("Weapon") 
        if weapon and hasattr(weapon, "default_attack_skill") and weapon.default_attack_skill:
            return weapon.default_attack_skill
            
        # Fallback
        return "attack_unarmed"
```

### C. `src/core/factory.py`
**Path:** `src/core/factory.py`
**Context:**  **Enhanced** helper to convert definitions into runtime objects, now including full trigger details (duration, stacks) so DoTs work correctly.

```python
# Add imports
from src.data.typed_models import SkillDefinition
from src.core.skills import Skill, Trigger

# ... existing EntityFactory class ...

def create_runtime_skill(definition: SkillDefinition) -> Skill:
    """
    Convert a data SkillDefinition into a runtime Skill object.
    Includes robust trigger hydration.
    """
    triggers = []
    if definition.trigger_event and definition.trigger_result:
        # Construct the result dictionary expected by EffectHandlers
        result_data = {"apply_debuff": definition.trigger_result}
        
        # Add optional fields if present
        if definition.trigger_duration > 0:
            result_data["duration"] = definition.trigger_duration
        
        if definition.stacks_max > 1:
            result_data["stacks"] = 1 # Usually apply 1 stack per hit, capping at stacks_max via logic elsewhere
            result_data["stacks_max"] = definition.stacks_max

        triggers.append(Trigger(
            event=definition.trigger_event.value,
            check={"proc_rate": definition.proc_rate},
            result=result_data
        ))

    return Skill(
        id=definition.skill_id,
        name=definition.name,
        damage_type=definition.damage_type.value,
        hits=definition.hits,
        cooldown=definition.cooldown,
        resource_cost=definition.resource_cost,
        damage_multiplier=definition.damage_multiplier,
        triggers=triggers
    )
```

### D. `src/combat/engine.py`
**Path:** `src/combat/engine.py`
**Context:** Apply the damage multiplier.

```python
    # ... inside calculate_skill_use ...
    def calculate_skill_use(self, attacker: Entity, defender: Entity, skill: Skill, state_manager: StateManager) -> SkillUseResult:
        # ...
        for _ in range(skill.hits):
            # 1. Resolve damage
            hit_context = self.resolve_hit(attacker, defender, state_manager)
            
            # Apply Skill Multiplier
            damage = hit_context.final_damage * skill.damage_multiplier # <--- NEW
            
            hit_results.append(hit_context) 
            
            # 2. Create actions
            actions.append(ApplyDamageAction(
                target_id=defender.id,
                damage=damage, 
                source=f"{skill.name}" # Used for logging
            ))
            
            # Update event with actual damage dealt
            hit_event = OnHitEvent(
                attacker=attacker,
                defender=defender,
                damage_dealt=damage, 
                is_crit=hit_context.was_crit
            )
            # ... rest of function
```

### E. `src/simulation/combat_simulation.py`
**Path:** `src/simulation/combat_simulation.py`
**Context:** Inject Provider, logging integration, and dynamic skill execution.

```python
# Imports
from src.data.game_data_provider import GameDataProvider
from src.core.factory import create_runtime_skill
from src.core.events import OnSkillUsedEvent

# 1. Update CombatLogger
class CombatLogger:
    # ... existing methods ...
    def log_skill_use(self, entity_id: str, skill_name: str) -> None:
        """Log when a skill is used."""
        entry = CombatLogEntry(
            timestamp=time.time(),
            event_type="skill",
            attacker_id=entity_id,
            metadata={"skill": skill_name}
        )
        self.entries.append(entry)

# 2. Update SimulationRunner
class SimulationRunner:
    def __init__(self, combat_engine, state_manager, event_bus, rng: RNG, provider: GameDataProvider, logger: Optional[CombatLogger] = None, loot_manager: Optional[LootManager] = None):
        # Added provider argument ^^^
        # ... existing assignments ...
        self.provider = provider
        # ...

    def _setup_event_subscriptions(self) -> None:
        # ... existing ...
        if self.logger:
            self.event_bus.subscribe(OnSkillUsedEvent, self._log_skill_event)

    def _log_skill_event(self, event: OnSkillUsedEvent) -> None:
        self.logger.log_skill_use(event.entity.id, event.skill_id)

    def update(self, delta_time: float, force_update: bool = False) -> None:
        # ... existing checks ...
        if self.is_running:
            self.simulation_time += delta_time

        # Update attack timers and process attacks
        for entity in self.entities[:]:
            if not self.state_manager.get_state(entity.id).is_alive:
                continue

            if entity.id in self.attack_timers:
                self.attack_timers[entity.id] -= delta_time

                if self.attack_timers[entity.id] <= 0:
                    target = self.get_random_target(entity.id)
                    if target:
                        # --- DYNAMIC SKILL LOGIC ---
                        # 1. Determine Skill ID from Weapon
                        skill_id = entity.get_default_attack_skill_id()
                        
                        # 2. Look up definition
                        skill_def = self.provider.skills.get(skill_id)
                        
                        # 3. Fallback Logic
                        if not skill_def:
                            # Try generic unarmed
                            skill_def = self.provider.skills.get("attack_unarmed")
                            
                        # 4. Create Runtime Skill
                        if skill_def:
                            runtime_skill = create_runtime_skill(skill_def)
                        else:
                            # Emergency fallback if data is totally missing
                            from src.core.skills import Skill
                            runtime_skill = Skill(id="fallback", name="Basic Attack")

                        # 5. Execute Skill via Engine
                        self.combat_engine.process_skill_use(entity, target, runtime_skill, self.event_bus, self.state_manager)
                        # ---------------------------

                        # Reset attack timer
                        speed = max(0.1, entity.final_stats.attack_speed)
                        self.attack_timers[entity.id] = 1.0 / speed
        
        # ... existing tick ...
```

### F. `src/game/session.py`
**Path:** `src/game/session.py`
**Context:** Pass `self.provider` to `SimulationRunner`.

```python
    def execute_combat_turn(self) -> bool:
        # ...
        
        # 7. Run Simulation
        from src.handlers.loot_handler import LootHandler
        loot_handler = LootHandler(event_bus, state_manager, loot_manager)
        
        # PASS PROVIDER HERE
        runner = SimulationRunner(combat_engine, state_manager, event_bus, rng, provider=self.provider)
        
        # ...
```

### G. `run_simulation.py`
**Path:** `run_simulation.py`
**Context:** Pass `provider` to `SimulationRunner`.

```python
def setup_simulation(rng: RNG) -> tuple:
    # ...
    provider = GameDataProvider() # Ensure this exists
    
    # ...
    
    # PASS PROVIDER HERE
    runner = SimulationRunner(combat_engine, state_manager, event_bus, rng, provider=provider)

    return runner, entity_factory
```

### H. `tests/test_weapon_mechanics.py`
**Path:** `tests/test_weapon_mechanics.py`
**Context:** Verification tests.

```python
import pytest
from unittest.mock import MagicMock
from src.core.models import Entity, Item
from src.core.skills import Skill
from src.combat.engine import CombatEngine
from src.core.state import StateManager
from tests.fixtures import make_rng, make_entity

class TestWeaponMechanics:
    
    def test_damage_multiplier_application(self):
        """Test that skill damage multiplier is applied."""
        attacker = make_entity("att", base_damage=100)
        defender = make_entity("def", armor=0)
        
        skill = Skill("test", "Test", damage_multiplier=0.5, hits=1)
        
        engine = CombatEngine(make_rng())
        state_manager = StateManager()
        state_manager.add_entity(attacker)
        state_manager.add_entity(defender)
        
        result = engine.calculate_skill_use(attacker, defender, skill, state_manager)
        
        # Base 100 * 0.5 = 50
        assert result.actions[0].damage == 50.0

    def test_get_default_attack_skill(self):
        """Test entity retrieves skill ID from weapon."""
        entity = make_entity("hero")
        
        # No weapon -> unarmed
        assert entity.get_default_attack_skill_id() == "attack_unarmed"
        
        # Weapon with skill
        weapon = MagicMock()
        weapon.default_attack_skill = "attack_dagger"
        entity.equipment["Weapon"] = weapon
        
        assert entity.get_default_attack_skill_id() == "attack_dagger"
```

---

## 🧪 Verification Steps

1.  **Run Unit Tests:**
    ```bash
    python -m pytest tests/test_weapon_mechanics.py
    ```
2.  **Run Dashboard (The Arena or Campaign):**
    *   Equip a **Dagger** (or ensure the hero has one).
    *   Look at the Combat Log. It should say "Dual Slash" (or whatever name was defined in CSV) instead of generic text.
    *   Equip a **Greatsword**. It should say "Heavy Swing".

## ⚠️ Rollback Plan
If this breaks the simulation:
1.  Revert `src/simulation/combat_simulation.py`.
2.  Revert `src/combat/engine.py`.
3.  Revert `src/core/models.py`.