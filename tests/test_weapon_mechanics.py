import pytest
from unittest.mock import MagicMock
from src.core.models import Entity
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

        # Check that we have an ApplyDamageAction
        from src.core.models import ApplyDamageAction
        assert isinstance(result.actions[0], ApplyDamageAction)

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
