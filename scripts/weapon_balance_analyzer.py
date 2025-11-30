#!/usr/bin/env python3
"""Weapon Balance Analysis Tool for Phase 2.3.

Analyzes weapon performance across different scenarios and provides tuning recommendations.
"""

import json
import statistics
from typing import Dict, List, Any
from dataclasses import dataclass
from run_simulation import run_combat_simulation

@dataclass
class WeaponAnalysis:
    """Analysis results for a specific weapon."""
    weapon_name: str
    avg_dps: float
    avg_total_damage: float
    avg_fight_duration: float
    effect_uptime: float
    win_rate: float
    damage_variance: float

class WeaponBalanceAnalyzer:
    """Analyzes weapon balance across multiple simulation runs."""

    def __init__(self):
        self.weapons = [
            "dagger", "greatsword", "axe", "staff", "bow", "sword", "unarmed"
        ]

    def analyze_weapon_balance(self, seed: int = 42, runs_per_weapon: int = 10) -> Dict[str, Any]:
        """Run comprehensive balance analysis.

        Args:
            seed: Base random seed
            runs_per_weapon: Number of simulation runs per weapon type

        Returns:
            Complete balance analysis report
        """
        results = {}

        for weapon in self.weapons:
            weapon_results = []
            print(f"Analyzing {weapon}...")

            for i in range(runs_per_weapon):
                # Run simulation with specific weapon
                report = run_combat_simulation(
                    seed=seed + (i * 100) + hash(weapon) % 1000,
                    duration=30.0
                )

                # Extract relevant metrics
                damage_breakdown = report.get("damage_breakdown", {})
                weapon_results.append({
                    "total_damage": sum(stats.get("total_damage", 0) for stats in damage_breakdown.values()),
                    "duration": report.get("duration", 30.0),
                    "effects": report.get("effect_uptime", {})
                })

            # Calculate averages and statistics
            total_damages = [r["total_damage"] for r in weapon_results]
            durations = [r["duration"] for r in weapon_results]

            results[weapon] = {
                "avg_dps": statistics.mean(total_damages) / statistics.mean(durations),
                "avg_total_damage": statistics.mean(total_damages),
                "avg_duration": statistics.mean(durations),
                "damage_std_dev": statistics.stdev(total_damages) if len(total_damages) > 1 else 0,
                "effect_uptime_avg": self._calculate_avg_effect_uptime(weapon_results)
            }

        # Generate balance recommendations
        recommendations = self._generate_balance_recommendations(results)

        return {
            "analysis_timestamp": __import__("time").time(),
            "weapons_analyzed": self.weapons,
            "balance_results": results,
            "recommendations": recommendations,
            "balance_score": self._calculate_balance_score(results)
        }

    def _calculate_avg_effect_uptime(self, weapon_results: List[Dict]) -> float:
        """Calculate average effect uptime across runs."""
        effect_uptimes = []
        for result in weapon_results:
            effects = result.get("effects", {})
            if effects:
                # Calculate total effect uptime percentage
                total_uptime = sum(
                    sum(effect_stats.get("total_ticks", 0) for effect_stats in entity_effects.values())
                    for entity_effects in effects.values()
                )
                effect_uptimes.append(min(total_uptime / 100.0, 1.0))  # Cap at 100%
            else:
                effect_uptimes.append(0.0)

        return statistics.mean(effect_uptimes) if effect_uptimes else 0.0

    def _generate_balance_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate tuning recommendations based on analysis."""
        recommendations = []

        # Find weapons with outlier DPS
        dps_values = {w: r["avg_dps"] for w, r in results.items()}
        avg_dps = statistics.mean(dps_values.values())

        for weapon, dps in dps_values.items():
            deviation = abs(dps - avg_dps) / avg_dps
            if deviation > 0.15:  # 15% deviation threshold
                if dps > avg_dps:
                    recommendations.append(f"Reduce {weapon} DPS (currently {deviation:.1%} above average)")
                else:
                    recommendations.append(f"Increase {weapon} DPS (currently {deviation:.1%} below average)")

        # Check effect uptime distribution
        effect_weapons = ["axe", "dagger", "staff"]  # Weapons with effects
        effect_uptimes = {w: results[w]["effect_uptime_avg"] for w in effect_weapons}

        if effect_uptimes:
            avg_effect_uptime = statistics.mean(effect_uptimes.values())
            for weapon, uptime in effect_uptimes.items():
                if uptime < avg_effect_uptime * 0.5:
                    recommendations.append(f"Increase {weapon} effect proc rates or frequency")

        return recommendations if recommendations else ["All weapons appear well-balanced"]

    def _calculate_balance_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall balance score (0-100, higher is better)."""
        dps_values = [r["avg_dps"] for r in results.values()]
        avg_dps = statistics.mean(dps_values)

        # Calculate coefficient of variation (lower is better balance)
        if avg_dps > 0:
            cv = statistics.stdev(dps_values) / avg_dps
            # Convert to 0-100 score (lower CV = higher score)
            balance_score = max(0, 100 - (cv * 1000))  # Scale CV appropriately
        else:
            balance_score = 0

        return round(balance_score, 1)

def main():
    """Main entry point."""
    analyzer = WeaponBalanceAnalyzer()
    report = analyzer.analyze_weapon_balance()

    # Save report
    with open("weapon_balance_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("Weapon Balance Analysis Complete")
    print(f"Balance Score: {report['balance_score']}/100")

    if report['recommendations']:
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")

if __name__ == "__main__":
    main()
