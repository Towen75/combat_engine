"""Tests for data_parser module with CSV schema validation."""

import pytest
import tempfile
import os
from pathlib import Path
import csv

from src.data.data_parser import parse_csv, parse_all_csvs
from src.data.schemas import (
    AFFIX_SCHEMA,
    ITEM_SCHEMA,
    QUALITY_TIERS_SCHEMA,
    EFFECTS_SCHEMA,
    SKILLS_SCHEMA
)


class TestCSVParseSchema:

    def test_parse_csv_missing_required_column(self):
        """Test CSV parse fails when required columns are missing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name,value\n")
            f.write("Test Item,10\n")
            temp_file = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                parse_csv(temp_file, ITEM_SCHEMA)
            assert "Missing required columns" in str(exc_info.value)
            assert "item_id" in str(exc_info.value)
        finally:
            os.unlink(temp_file)

    def test_parse_csv_bad_float_value(self):
        """Test CSV parse fails with invalid float."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(["item_id", "name", "slot", "rarity", "num_random_affixes"])
            writer.writerow(["test_item", "Test Item", "Weapon", "Common", "not-a-number"])
            temp_file = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                parse_csv(temp_file, ITEM_SCHEMA)
            assert "Invalid integer value" in str(exc_info.value)
        finally:
            os.unlink(temp_file)

    def test_parse_csv_invalid_positive_float(self):
        """Test CSV parse fails with non-positive float."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(["effect_id", "name", "type", "description", "tick_rate"])
            writer.writerow(["bleed", "Bleed", "DoT", "Deals damage", "-1.0"])
            temp_file = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                parse_csv(temp_file, EFFECTS_SCHEMA)
            assert "Value must be >= 0" in str(exc_info.value)
        finally:
            os.unlink(temp_file)

    def test_parse_csv_valid_data(self):
        """Test CSV parse succeeds with valid data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(["item_id", "name", "slot", "rarity", "num_random_affixes"])
            writer.writerow(["iron_sword", "Iron Sword", "Weapon", "Common", "2"])
            writer.writerow(["leather_armor", "Leather Armor", "Chest", "Common", "0"])
            temp_file = f.name

        try:
            rows = parse_csv(temp_file, ITEM_SCHEMA)
            assert len(rows) == 2
            assert rows[0]["item_id"] == "iron_sword"
            assert rows[0]["name"] == "Iron Sword"
            assert rows[0]["num_random_affixes"] == 2
            assert rows[1]["item_id"] == "leather_armor"
            assert rows[1]["num_random_affixes"] == 0
        finally:
            os.unlink(temp_file)

    def test_parse_csv_with_empty_optional_fields(self):
        """Test CSV parse handles empty optional fields."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(["affix_id", "stat_affected", "mod_type", "base_value", "description"])
            writer.writerow(["sharp", "damage", "flat", "15.5", "+{value} Damage"])
            temp_file = f.name

        try:
            rows = parse_csv(temp_file, AFFIX_SCHEMA)
            assert len(rows) == 1
            assert rows[0]["affix_id"] == "sharp"
            assert rows[0]["affix_pools"] == []  # Empty field defaults to empty list
            assert rows[0]["stacks_max"] == 1  # Default value
        finally:
            os.unlink(temp_file)

    def test_parse_csv_affix_pools_validator(self):
        """Test affix pools validator parses pipe-separated values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(["item_id", "name", "slot", "rarity", "affix_pools", "num_random_affixes"])
            writer.writerow(["magic_sword", "Magic Sword", "Weapon", "Rare", "weapon_pool|magic_pool|rare_pool", "3"])
            temp_file = f.name

        try:
            rows = parse_csv(temp_file, ITEM_SCHEMA)
            assert rows[0]["affix_pools"] == ["weapon_pool", "magic_pool", "rare_pool"]
        finally:
            os.unlink(temp_file)

    def test_parse_csv_duplicate_id_detection(self):
        """Test that duplicate IDs are not handled automatically (this would require additional logic)."""
        # This test documents current behavior - duplicate IDs would just overwrite
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(["item_id", "name", "slot", "rarity", "num_random_affixes"])
            writer.writerow(["sword", "Iron Sword", "Weapon", "Common", "2"])
            writer.writerow(["sword", "Steel Sword", "Weapon", "Common", "1"])  # Duplicate ID
            temp_file = f.name

        try:
            rows = parse_csv(temp_file, ITEM_SCHEMA)
            # Currently allows duplicates, last one wins
            assert len(rows) == 2
            assert rows[0]["name"] == "Iron Sword"
            assert rows[1]["name"] == "Steel Sword"
        finally:
            os.unlink(temp_file)

    def test_parse_all_csvs_quality_tier_range_validation(self):
        """Test that parse_all_csvs validates quality tier min_range < max_range."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create a valid quality tiers CSV with invalid range
            csv_file = os.path.join(tmp_dir, "quality_tiers.csv")
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["quality_id", "tier_name", "min_range", "max_range"])
                writer.writerow(["1", "Low", "5", "3"])  # Invalid range: min > max

            with pytest.raises(ValueError) as exc_info:
                parse_all_csvs(tmp_dir)
            error_msg = str(exc_info.value)
            # Should catch the min >= max validation error in parse_all_csvs
            assert "min_range" in error_msg.lower() or "max_range" in error_msg.lower()


class TestParseAllCSVs:

    def test_parse_all_csvs_with_project_data(self, tmp_path):
        """Test parsing all CSVs in a directory structure similar to the project."""
        # Copy project CSV files to temp dir
        import os
        src_data_dir = Path(__file__).parent.parent / "data"
        if not src_data_dir.exists():
            pytest.skip("Project data directory not found")

        for csv_file in src_data_dir.glob("*.csv"):
            # Create minimal test CSVs with required columns
            if "affixes" in csv_file.name:
                self._create_test_affix_csv(tmp_path / csv_file.name)
            elif "items" in csv_file.name:
                self._create_test_item_csv(tmp_path / csv_file.name)
            elif "effects" in csv_file.name:
                self._create_test_effect_csv(tmp_path / csv_file.name)
            elif "skills" in csv_file.name:
                self._create_test_skill_csv(tmp_path / csv_file.name)
            elif "quality_tiers" in csv_file.name:
                self._create_test_quality_tiers_csv(tmp_path / csv_file.name)

        # Parse all CSVs
        result = parse_all_csvs(str(tmp_path))

        # Verify structure
        assert "affixes" in result
        assert "items" in result
        assert "effects" in result
        assert "skills" in result
        assert "quality_tiers" in result

        # Verify data types
        assert isinstance(result["affixes"], dict)
        assert isinstance(result["items"], dict)
        assert isinstance(result["effects"], dict)
        assert isinstance(result["skills"], dict)
        assert isinstance(result["quality_tiers"], list)

    def _create_test_affix_csv(self, filepath):
        """Create a test affixes CSV."""
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["affix_id", "stat_affected", "mod_type", "base_value", "description"])
            writer.writerow(["test_affix", "damage", "flat", "10", "Test affix"])
            writer.writerow(["fire_affix", "fire_damage", "percent", "25", "Fire damage"])

    def _create_test_item_csv(self, filepath):
        """Create a test items CSV."""
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["item_id", "name", "slot", "rarity", "num_random_affixes"])
            writer.writerow(["sword1", "Iron Sword", "Weapon", "Common", "2"])
            writer.writerow(["armor1", "Leather Armor", "Chest", "Common", "1"])

    def _create_test_effect_csv(self, filepath):
        """Create a test effects CSV."""
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["effect_id", "name", "type", "description"])
            writer.writerow(["bleeding", "Bleed", "DoT", "Deals damage over time"])

    def _create_test_skill_csv(self, filepath):
        """Create a test skills CSV."""
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["skill_id", "name", "damage_type"])
            writer.writerow(["fireball", "Fireball", "Fire"])

    def _create_test_quality_tiers_csv(self, filepath):
        """Create a test quality tiers CSV."""
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["quality_id", "tier_name", "min_range", "max_range"])
            writer.writerow(["1", "Poor", "0", "10"])


class TestSchemasValidators:

    def test_str_validator_handles_various_inputs(self):
        """Test string validator handles various input types."""
        from src.data.schemas import str_validator

        assert str_validator("hello") == "hello"
        assert str_validator(str(123)) == "123"  # Convert to str for typing
        # These won't actually be passed None or int directly in the CSV parser
        assert str_validator("") == ""

    def test_int_validator_rejects_invalid_values(self):
        """Test integer validator rejects invalid inputs."""
        from src.data.schemas import int_validator

        assert int_validator("123") == 123
        assert int_validator("1.0") == 1  # Handles float strings

        with pytest.raises(ValueError):
            int_validator("not-a-number")
        with pytest.raises(ValueError):
            int_validator("")

    def test_float_validator_range(self):
        """Test float validator accepts various numeric formats."""
        from src.data.schemas import float_validator

        assert float_validator("1.5") == 1.5
        assert float_validator("2") == 2.0
        assert float_validator("-5.0") == -5.0

        with pytest.raises(ValueError):
            float_validator("not-a-float")


class TestComprehensiveSchemaValidators:
    """Comprehensive tests for all schema validators."""

    def test_affix_pools_validator_edge_cases(self):
        """Test affix_pools_validator handles various edge cases."""
        from src.data.schemas import affix_pools_validator

        # Empty string
        assert affix_pools_validator("") == []
        assert affix_pools_validator("   ") == []

        # Single pool
        assert affix_pools_validator("weapon_pool") == ["weapon_pool"]

        # Multiple pools with spaces
        assert affix_pools_validator("weapon_pool | armor_pool") == ["weapon_pool", "armor_pool"]
        assert affix_pools_validator("  weapon_pool  |  armor_pool  ") == ["weapon_pool", "armor_pool"]

        # Empty segments
        assert affix_pools_validator("weapon_pool||armor_pool") == ["weapon_pool", "armor_pool"]
        assert affix_pools_validator("|weapon_pool|") == ["weapon_pool"]

    def test_tier_probabilities_validator_edge_cases(self):
        """Test tier_probabilities_validator edge cases."""
        from src.data.schemas import tier_probabilities_validator

        # Empty values become 0
        assert tier_probabilities_validator("") == 0
        assert tier_probabilities_validator("0") == 0
        # Note: None would cause a TypeError in actual CSV parsing, but this documents fallback behavior

        # Valid positive integers
        assert tier_probabilities_validator("42") == 42

        # Invalid negative values
        with pytest.raises(ValueError):
            tier_probabilities_validator("-1")

    def test_tier_range_validator(self):
        """Test tier_range_validator functionality."""
        from src.data.schemas import tier_range_validator

        # Valid ranges
        assert tier_range_validator("1", "10") == (1, 10)
        assert tier_range_validator("50", "100") == (50, 100)

        # Invalid ranges (min >= max)
        with pytest.raises(ValueError):
            tier_range_validator("10", "10")  # equal
        with pytest.raises(ValueError):
            tier_range_validator("20", "10")  # min > max

        # Invalid integer values
        with pytest.raises(ValueError):
            tier_range_validator("not-a-number", "10")
        with pytest.raises(ValueError):
            tier_range_validator("1", "not-a-number")

    def test_quality_id_validator(self):
        """Test quality_id_validator ensures >= 1."""
        from src.data.schemas import quality_id_validator

        assert quality_id_validator("1") == 1
        assert quality_id_validator("100") == 100

        # Invalid values
        with pytest.raises(ValueError):
            quality_id_validator("0")
        with pytest.raises(ValueError):
            quality_id_validator("-1")
        with pytest.raises(ValueError):
            quality_id_validator("not-a-number")


class TestSchemaValidationIntegration:
    """Test schema validation in complete parsing scenarios."""

    def test_affix_schema_complex_values(self):
        """Test affix schema with complex values like dual stats."""
        from src.data.schemas import AFFIX_SCHEMA

        # Test case similar to actual data: dual stat affix
        row_data = {
"affix_id": "swiftslayer",
"stat_affected": "attack_speed;cooldown_reduction",
"mod_type": "multiplier;flat",
"affix_pools": "weapon_pool",
"base_value": "0.25;0.08",
"description": "{value}% Attack Speed & {dual_value}% CD Reduction",
"dual_stat": "TRUE",
"stacks_max": "",
"proc_rate": "",
"trigger_duration": "",
"scaling_power": "",
"trigger_event": "",
"trigger_result": "",
"complex_effect": ""
        }

        # Validate all columns
        validated = {}
        for col, validator in AFFIX_SCHEMA["columns"].items():
            raw_value = row_data.get(col, "")
            validated[col] = validator(raw_value)

        # Check results
        assert validated["affix_id"] == "swiftslayer"
        assert validated["stat_affected"] == "attack_speed;cooldown_reduction"
        assert validated["dual_stat"] == True  # "TRUE" in CSV becomes boolean True
        assert validated["stacks_max"] == 1  # Default value
        assert validated["proc_rate"] == 0.0  # Default value
        assert validated["scaling_power"] == 0.0  # Default value

    def test_effects_schema_tick_rate_defaults(self):
        """Test effects schema with tick_rate defaulting."""
        from src.data.schemas import EFFECTS_SCHEMA

        # Effect without tick_rate specified should default to 1.0
        row_data = {
            "effect_id": "quick_effect",
            "name": "Quick Effect",
            "type": "buff",
            "description": "A quick effect",
            "max_stacks": "",
            "tick_rate": "",
            "damage_per_tick": "",
            "stat_multiplier": "",
            "stat_add": "",
            "visual_effect": "",
            "duration": ""
        }

        validated = {}
        for col, validator in EFFECTS_SCHEMA["columns"].items():
            raw_value = row_data.get(col, "")
            validated[col] = validator(raw_value)

        # Check defaults
        assert validated["max_stacks"] == 1
        assert validated["tick_rate"] == 1.0
        assert validated["duration"] == 10.0  # Explicit default in schema

    def test_skills_schema_defaults(self):
        """Test skills schema default values."""
        from src.data.schemas import SKILLS_SCHEMA

        row_data = {
            "skill_id": "basic_attack",
            "name": "Basic Attack",
            "damage_type": "",
            "hits": "",
            "description": "",
            "resource_cost": "",
            "cooldown": "",
            "trigger_event": "",
            "proc_rate": "",
            "trigger_result": "",
            "trigger_duration": "",
            "stacks_max": ""
        }

        validated = {}
        for col, validator in SKILLS_SCHEMA["columns"].items():
            raw_value = row_data.get(col, "")
            validated[col] = validator(raw_value)

        # Check defaults
        assert validated["hits"] == 1
        assert validated["resource_cost"] == 0.0
        assert validated["cooldown"] == 0.0
        assert validated["proc_rate"] == 0.0


class TestSchemaValidatorFactory:
    """Test the get_schema_validator function."""

    def test_get_schema_validator_affixes(self):
        """Test schema detection for affixes.csv."""
        from src.data.schemas import get_schema_validator

        schema = get_schema_validator("/path/to/affixes.csv")
        assert "required" in schema
        assert "affix_id" in schema["required"]

    def test_get_schema_validator_items(self):
        """Test schema detection for items.csv."""
        from src.data.schemas import get_schema_validator

        schema = get_schema_validator("items.csv")
        assert "required" in schema
        assert "item_id" in schema["required"]

    def test_get_schema_validator_unknown(self):
        """Test schema detection fails for unknown CSV files."""
        from src.data.schemas import get_schema_validator

        with pytest.raises(ValueError) as exc_info:
            get_schema_validator("unknown.csv")
        assert "No schema found" in str(exc_info.value)

    def test_get_schema_validator_quality_tiers(self):
        """Test schema detection for quality_tiers.csv."""
        from src.data.schemas import get_schema_validator

        schema = get_schema_validator("my_quality_tiers.csv")
        assert "required" in schema
        assert "quality_id" in schema["required"]

    def test_get_schema_validator_effects(self):
        """Test schema detection for effects.csv."""
        from src.data.schemas import get_schema_validator

        schema = get_schema_validator("effects.csv")
        assert "required" in schema
        assert "effect_id" in schema["required"]

    def test_get_schema_validator_skills(self):
        """Test schema detection for skills.csv."""
        from src.data.schemas import get_schema_validator

        schema = get_schema_validator("skills.csv")
        assert "required" in schema
        assert "skill_id" in schema["required"]


class TestErrorHandlingAndMessages:
    """Test detailed error handling and messages."""

    def test_parse_csv_error_details(self):
        """Test that parse_csv provides detailed error information."""
        from src.data.data_parser import parse_csv
        from src.data.schemas import ITEM_SCHEMA

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("item_id,name,slot,rarity,num_random_affixes\n")
            f.write("test_item,Test Item,Weapon,Rare,invalid_number\n")
            temp_file = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                parse_csv(temp_file, ITEM_SCHEMA)
            error_msg = str(exc_info.value)
            assert "line 2" in error_msg  # Should mention line number
            assert "num_random_affixes" in error_msg  # Should mention column
            assert "invalid_number" in error_msg  # Should mention problematic value
        finally:
            os.unlink(temp_file)

    def test_schema_missing_column_details(self):
        """Test that missing column errors are detailed."""
        from src.data.data_parser import parse_csv
        from src.data.schemas import ITEM_SCHEMA

        # Create CSV missing a required column
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("item_id,name,slot,num_random_affixes\n")  # Missing 'rarity'
            f.write("test_item,Test Item,Weapon,2\n")
            temp_file = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                parse_csv(temp_file, ITEM_SCHEMA)
            error_msg = str(exc_info.value)
            assert "rarity" in error_msg  # Should mention missing column
            assert "required columns" in error_msg.casefold()
        finally:
            os.unlink(temp_file)


class TestDataParserIntegration:
    """Test integration between parser and real data files."""

    def test_parse_all_csvs_file_missing_warning(self, tmp_path, caplog):
        """Test that missing files are logged as warnings and don't break parsing."""
        import logging

        # Create only effects.csv, leave others missing
        effects_csv = tmp_path / "effects.csv"
        with open(effects_csv, 'w', newline='') as f:
            import csv
            writer = csv.writer(f)
            writer.writerow(["effect_id", "name", "type", "description"])
            writer.writerow(["bleed", "Bleed", "DoT", "Damage over time"])

        with caplog.at_level(logging.WARNING):
            result = parse_all_csvs(str(tmp_path))

        # Should have warnings for missing files
        warning_messages = [record.message for record in caplog.records if record.levelname == "WARNING"]
        assert any("affixes.csv" in msg for msg in warning_messages)
        assert any("items.csv" in msg for msg in warning_messages)
        assert any("quality_tiers.csv" in msg for msg in warning_messages)
        assert any("skills.csv" in msg for msg in warning_messages)

        # Should still have effects data
        assert "effects" in result
        assert "bleed" in result["effects"]

    @pytest.mark.parametrize("data_key,expected_empty", [
        ("affixes", {}),
        ("items", {}),
        ("quality_tiers", []),
        ("effects", {}),
        ("skills", {})
    ])
    def test_parse_all_csvs_handles_missing_files(self, tmp_path, data_key, expected_empty):
        """Test that parse_all_csvs handles missing files appropriately."""
        # Create only one CSV file, others will be missing
        if data_key == "effects":
            csv_file = tmp_path / "effects.csv"
            with open(csv_file, 'w', newline='') as f:
                import csv
                writer = csv.writer(f)
                writer.writerow(["effect_id", "name", "type", "description"])
                writer.writerow(["test_effect", "Test Effect", "buff", "Test buff"])

        result = parse_all_csvs(str(tmp_path))

        # Non-created data should be empty
        assert result[data_key] == expected_empty if data_key != "effects" else {"test_effect": result[data_key]["test_effect"]}

        # The created effects data should be populated
        if data_key == "effects":
            assert len(result[data_key]) == 1
            assert result[data_key]["test_effect"]["effect_id"] == "test_effect"


class TestPerformanceAndEdgeCases:
    """Test performance and edge cases."""

    def test_parse_csv_large_file(self, tmp_path):
        """Test parsing a relatively large CSV file."""
        # Create a CSV with ~1000 rows
        large_csv = tmp_path / "large_items.csv"

        with open(large_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["item_id", "name", "slot", "rarity", "num_random_affixes"])

            for i in range(1000):
                writer.writerow([f"item_{i}", f"Item {i}", "Weapon", "Common", "1"])

        result = parse_csv(str(large_csv), ITEM_SCHEMA)
        assert len(result) == 1000
        assert result[0]["item_id"] == "item_0"
        assert result[-1]["item_id"] == "item_999"

    def test_parse_csv_unicode_support(self):
        """Test CSV parsing with Unicode characters."""
        from src.data.data_parser import parse_csv
        from src.data.schemas import AFFIX_SCHEMA

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', encoding='utf-8', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(["affix_id", "stat_affected", "mod_type", "base_value", "description"])
            writer.writerow(["fire_sword", "damage", "flat", "45", "🔥 Огненный Меч 🔥"])  # Russian + emoji
            writer.writerow(["pepe_ring", "health", "flat", "100", "🐸 Pepe Ring 🐸"])  # Emoji
            temp_file = f.name

        try:
            result = parse_csv(temp_file, AFFIX_SCHEMA)
            assert len(result) == 2
            # Note: This test documents current behavior - unicode is preserved
            assert "🔥" in result[0]["description"]
            assert "Огненный" in result[0]["description"]
            assert result[1]["base_value"] == "100"
        finally:
            os.unlink(temp_file)

    def test_parse_csv_duplicate_headers_allowed(self):
        """Test behavior with duplicate column headers."""
        # This documents current behavior - last column wins
        from src.data.data_parser import parse_csv
        from src.data.schemas import AFFIX_SCHEMA

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            # Duplicate column names - should parse but with undefined behavior
            writer.writerow(["affix_id", "stat_affected", "mod_type", "base_value", "description", "description"])
            writer.writerow(["double_desc", "damage", "flat", "25", "+25 Damage", "Actually +50 Damage"])
            temp_file = f.name

        try:
            result = parse_csv(temp_file, AFFIX_SCHEMA)
            assert len(result) == 1
            # Behavior is undefined for duplicate headers, but shouldn't crash
            assert result[0]["affix_id"] == "double_desc"
            assert result[0]["base_value"] == "25"
        finally:
            os.unlink(temp_file)

# Run comprehensive validation of actual project data if available
class TestProjectDataValidation:
    """Test validation using actual project data files."""

    def test_validate_actual_project_data(self):
        """Test that actual project data validates correctly."""
        # This test is skipped in normal CI since it requires project data
        # But provides validation when running locally with full data set
        import os.path

        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

        if not os.path.exists(os.path.join(data_dir, "affixes.csv")):
            pytest.skip("Project data files not available - skipping comprehensive validation")

        # If data exists, try to parse it all
        try:
            from src.data.data_parser import parse_all_csvs
            game_data = parse_all_csvs(data_dir)

            # Basic structure validation
            assert "affixes" in game_data
            assert "items" in game_data
            assert "quality_tiers" in game_data
            assert "effects" in game_data
            assert "skills" in game_data

            # Basic data type validation
            assert isinstance(game_data["affixes"], dict)
            assert isinstance(game_data["items"], dict)
            assert isinstance(game_data["quality_tiers"], list)
            assert isinstance(game_data["effects"], dict)
            assert isinstance(game_data["skills"], dict)

            # Validate that quality tiers have valid ranges
            for tier in game_data["quality_tiers"]:
                assert tier["min_range"] < tier["max_range"], f"Invalid tier range for {tier['tier_name']}"

        except Exception as e:
            pytest.fail(f"Project data validation failed: {e}")
