import pytest
from src.data.game_data_provider import GameDataProvider
from src.data.typed_models import DataValidationError

class TestWeaponData:

    def test_skills_load_multiplier(self):
        """Test that skills.csv loads the new damage_multiplier field."""
        # Setup mock data for skill
        raw_data = {
            "skills": {
                "test_dagger_attack": {
                    "skill_id": "test_dagger_attack",
                    "name": "Dagger",
                    "damage_type": "Physical",
                    "damage_multiplier": "0.5",
                    "hits": "2"
                }
            }
        }

        provider = GameDataProvider.__new__(GameDataProvider)
        # Initialize required attributes
        provider.skills = {}
        provider.affixes = {}
        provider.affix_pools = {}
        provider.items = {}
        provider.quality_tiers = []
        provider.effects = {}
        provider.loot_tables = []
        provider.entities = {}

        provider._hydrate_data(raw_data)

        skill = provider.skills["test_dagger_attack"]
        assert skill.damage_multiplier == 0.5
        assert skill.hits == 2

    def test_item_loads_default_skill(self):
        """Test that items load the default_attack_skill."""
        raw_data = {
            "items": {
                "dagger_common": {
                    "item_id": "dagger_common",
                    "name": "Dagger",
                    "slot": "Weapon",
                    "rarity": "Common",
                    "default_attack_skill": "attack_dagger"
                }
            }
        }

        provider = GameDataProvider.__new__(GameDataProvider)
        # Initialize required attributes
        provider.skills = {}
        provider.affixes = {}
        provider.affix_pools = {}
        provider.items = {}
        provider.quality_tiers = []
        provider.effects = {}
        provider.loot_tables = []
        provider.entities = {}

        provider._hydrate_data(raw_data)

        item = provider.items["dagger_common"]
        assert item.default_attack_skill == "attack_dagger"

    def test_validation_fails_on_missing_skill(self):
        """Test validation catches items pointing to missing skills."""
        raw_data = {
            "items": {
                "broken_sword": {
                    "item_id": "broken_sword",
                    "name": "Broken",
                    "slot": "Weapon",
                    "rarity": "Common",
                    "default_attack_skill": "missing_skill"
                }
            },
            "skills": {} # Empty skills
        }

        provider = GameDataProvider.__new__(GameDataProvider)
        # Initialize required attributes
        provider.skills = {}
        provider.affixes = {}
        provider.affix_pools = {}
        provider.items = {}
        provider.quality_tiers = []
        provider.effects = {}
        provider.loot_tables = []
        provider.entities = {}

        provider._hydrate_data(raw_data)

        with pytest.raises(DataValidationError) as exc:
            provider._validate_cross_references()

        assert "missing_skill" in str(exc.value)
        assert "broken_sword" in str(exc.value)
