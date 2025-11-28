import pytest
from src.data.typed_models import EntityTemplate, hydrate_entity_template


class TestEntityPortraitData:

    def test_portrait_path_hydration_with_value(self):
        """Test that portrait paths are correctly hydrated from raw data."""
        # Test the hydration function directly
        raw_data = {
            "entity_id": "test_hero",
            "name": "Test Hero",
            "base_health": "100",
            "base_damage": "10",
            "rarity": "Rare",
            "portrait_path": "assets/portraits/hero.png"
        }

        entity = hydrate_entity_template(raw_data)

        assert entity.portrait_path == "assets/portraits/hero.png"
        assert entity.entity_id == "test_hero"
        assert entity.name == "Test Hero"

    def test_portrait_path_hydration_default_empty(self):
        """Test that missing portrait path defaults to empty string."""
        raw_data = {
            "entity_id": "test_mob",
            "name": "Test Mob",
            "base_health": "50",
            "base_damage": "5",
            "rarity": "Common"
            # No portrait_path key
        }

        entity = hydrate_entity_template(raw_data)

        assert entity.portrait_path == ""
        assert entity.entity_id == "test_mob"

    def test_portrait_path_hydration_empty_string(self):
        """Test that empty string portrait path is preserved."""
        raw_data = {
            "entity_id": "test_mob",
            "name": "Test Mob",
            "base_health": "50",
            "base_damage": "5",
            "rarity": "Common",
            "portrait_path": ""  # Explicit empty string
        }

        entity = hydrate_entity_template(raw_data)

        assert entity.portrait_path == ""
        assert entity.entity_id == "test_mob"

    def test_entity_template_has_portrait_path_field(self):
        """Test that EntityTemplate class has portrait_path field."""
        from src.data.typed_models import EntityTemplate, Rarity

        # Create a real EntityTemplate instance
        template = EntityTemplate(
            entity_id="test_entity",
            name="Test Entity",
            archetype="Monster",
            level=1,
            rarity=Rarity.COMMON,
            base_health=100.0,
            base_damage=10.0,
            armor=5.0,
            crit_chance=0.05,
            attack_speed=1.0,
            portrait_path="assets/portraits/test.png"
        )

        # Verify the field exists and is accessible
        assert hasattr(template, 'portrait_path')
        assert template.portrait_path == "assets/portraits/test.png"
