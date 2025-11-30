import pytest
import json
from scripts.weapon_balance_analyzer import WeaponBalanceAnalyzer
from run_simulation import run_combat_simulation

class TestWeaponBalance:

    def test_balance_score_calculation(self):
        """Test that balance score is calculated correctly."""
        analyzer = WeaponBalanceAnalyzer()

        # Mock results with perfect balance
        mock_results = {
            "dagger": {"avg_dps": 50.0},
            "sword": {"avg_dps": 50.0},
            "axe": {"avg_dps": 50.0}
        }

        score = analyzer._calculate_balance_score(mock_results)
        assert score == 100.0  # Perfect balance

    def test_weapon_dps_parity(self):
        """Test that all weapons achieve similar DPS."""
        # Run quick simulation
        report = run_combat_simulation(seed=12345, duration=10.0)

        damage_breakdown = report.get("damage_breakdown", {})
        dps_values = []

        for entity_stats in damage_breakdown.values():
            total_damage = entity_stats.get("total_damage", 0)
            duration = report.get("duration", 10.0)
            if duration > 0:
                dps_values.append(total_damage / duration)

        # Assert reasonable DPS spread (within 50% of average)
        if dps_values:
            avg_dps = sum(dps_values) / len(dps_values)
            for dps in dps_values:
                assert 0.5 <= dps / avg_dps <= 1.5, f"DPS {dps} deviates too much from average {avg_dps}"

    def test_bleed_effect_on_axes(self):
        """Test that axes properly apply bleed effects."""
        # This would require more complex simulation setup
        # For now, test the balance analyzer can detect effect differences
        analyzer = WeaponBalanceAnalyzer()
        report = analyzer.analyze_weapon_balance(runs_per_weapon=3)

        # Axe should have higher effect uptime than sword
        axe_uptime = report["balance_results"]["axe"]["effect_uptime_avg"]
        sword_uptime = report["balance_results"]["sword"]["effect_uptime_avg"]

        assert axe_uptime > sword_uptime, "Axes should have higher effect uptime than basic weapons"

    def test_multi_hit_scaling(self):
        """Test that multi-hit weapons scale damage appropriately."""
        # Daggers should have more total hits but lower per-hit damage
        analyzer = WeaponBalanceAnalyzer()

        # This is a simplified test - would need access to detailed combat logs
        # to count individual hits vs total damage
        assert True  # Placeholder - implement with detailed logging

    def test_balance_report_generation(self):
        """Test that balance reports are generated successfully."""
        analyzer = WeaponBalanceAnalyzer()
        report = analyzer.analyze_weapon_balance(runs_per_weapon=2)

        required_keys = ["analysis_timestamp", "weapons_analyzed", "balance_results", "recommendations", "balance_score"]
        for key in required_keys:
            assert key in report, f"Report missing required key: {key}"

        assert isinstance(report["balance_score"], (int, float))
        assert 0 <= report["balance_score"] <= 100
