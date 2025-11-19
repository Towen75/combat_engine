"""Tests for data exporters.

Validates JSON and CSV export functionality.
"""

import pytest
import json
import csv
from pathlib import Path
from src.core.models import Entity, EntityStats
from src.simulation.batch_runner import SimulationBatchRunner, BatchResult
from src.simulation.exporters import export_to_json, export_to_csv, export_summary_to_csv


@pytest.fixture
def sample_batch_result():
    """Create a sample batch result for testing."""
    result = BatchResult(
        batch_id="test_batch",
        iterations=5,
        base_seed=42
    )
    result.winners = ["warrior", "warrior", "mage", "warrior", "mage"]
    result.remaining_hps = [50.0, 60.0, 40.0, 55.0, 45.0]
    result.durations = [10.0, 10.0, 10.0, 10.0, 10.0]
    result.dps_stats = {
        "mean_dps": 150.0,
        "median_dps": 150.0,
        "min_dps": 100.0,
        "max_dps": 200.0,
        "total_damage": 750.0,
        "fight_count": 5
    }
    result.win_rate_stats = {
        "entities": {
            "warrior": {"wins": 3, "losses": 2, "total_fights": 5, "win_rate": 0.6},
            "mage": {"wins": 2, "losses": 3, "total_fights": 5, "win_rate": 0.4}
        },
        "mean_victory_margin": 50.0,
        "median_victory_margin": 50.0,
        "total_fights": 5
    }
    return result


class TestJsonExport:
    """Test JSON export functionality."""
    
    def test_export_to_json(self, sample_batch_result, tmp_path):
        """Test exporting batch results to JSON."""
        output_file = tmp_path / "test_export.json"
        
        export_to_json(sample_batch_result, str(output_file))
        
        # Verify file was created
        assert output_file.exists()
        
        # Verify content
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        assert data['batch_id'] == "test_batch"
        assert data['iterations'] == 5
        assert data['base_seed'] == 42
        assert len(data['winners']) == 5
        assert 'dps_stats' in data
        assert 'win_rate_stats' in data
    
    def test_json_structure(self, sample_batch_result, tmp_path):
        """Test JSON structure matches expected format."""
        output_file = tmp_path / "test_structure.json"
        
        export_to_json(sample_batch_result, str(output_file))
        
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        # Check DPS stats
        assert data['dps_stats']['mean_dps'] == 150.0
        assert data['dps_stats']['median_dps'] == 150.0
        
        # Check win rate stats
        assert 'warrior' in data['win_rate_stats']['entities']
        assert 'mage' in data['win_rate_stats']['entities']


class TestCsvExport:
    """Test CSV export functionality."""
    
    def test_export_to_csv(self, sample_batch_result, tmp_path):
        """Test exporting batch results to CSV."""
        output_file = tmp_path / "test_export.csv"
        
        export_to_csv(sample_batch_result, str(output_file))
        
        # Verify file was created
        assert output_file.exists()
        
        # Verify content
        with open(output_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 5
        assert rows[0]['batch_id'] == "test_batch"
        assert rows[0]['winner'] == "warrior"
    
    def test_csv_columns(self, sample_batch_result, tmp_path):
        """Test CSV has correct columns."""
        output_file = tmp_path / "test_columns.csv"
        
        export_to_csv(sample_batch_result, str(output_file))
        
        with open(output_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
        
        expected_columns = ['batch_id', 'simulation_id', 'base_seed', 'winner', 'remaining_hp', 'duration']
        assert fieldnames == expected_columns
    
    def test_export_summary_to_csv(self, sample_batch_result, tmp_path):
        """Test exporting summary statistics to CSV."""
        output_file = tmp_path / "test_summary.csv"
        
        export_summary_to_csv(sample_batch_result, str(output_file))
        
        # Verify file was created
        assert output_file.exists()
        
        # Verify content includes statistics
        with open(output_file, 'r', newline='') as f:
            content = f.read()
        
        assert "Batch Summary" in content
        assert "DPS Statistics" in content
        assert "Win Rate Statistics" in content
        assert "test_batch" in content


class TestExportIntegration:
    """Test export integration with real batch results."""
    
    def test_export_real_batch(self, tmp_path):
        """Test exporting results from an actual batch run."""
        # Create simple entities
        warrior_stats = EntityStats(
            base_damage=25.0,
            attack_speed=1.0,
            crit_chance=0.1,
            crit_damage=1.5,
            pierce_ratio=0.05,
            max_health=150.0,
            armor=15.0,
            resistances=0.0
        )
        warrior = Entity("warrior", warrior_stats, "Warrior", "Rare")
        
        mage_stats = EntityStats(
            base_damage=30.0,
            attack_speed=0.8,
            crit_chance=0.15,
            crit_damage=1.5,
            pierce_ratio=0.02,
            max_health=80.0,
            armor=5.0,
            resistances=0.2
        )
        mage = Entity("mage", mage_stats, "Mage", "Epic")
        
        # Run small batch
        runner = SimulationBatchRunner(batch_id="export_test")
        result = runner.run_batch(warrior, mage, iterations=3, base_seed=42, max_duration=5.0)
        
        # Export to both formats
        json_file = tmp_path / "batch_result.json"
        csv_file = tmp_path / "batch_result.csv"
        summary_file = tmp_path / "batch_summary.csv"
        
        export_to_json(result, str(json_file))
        export_to_csv(result, str(csv_file))
        export_summary_to_csv(result, str(summary_file))
        
        # Verify all files created
        assert json_file.exists()
        assert csv_file.exists()
        assert summary_file.exists()
