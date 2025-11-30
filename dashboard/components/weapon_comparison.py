import streamlit as st
from typing import Dict, List, Any

def render_weapon_comparison(session, provider):
    """Render weapon performance comparison across fights."""

    if not session.combat_log or len(session.combat_log) < 2:
        return

    st.markdown("### ⚖️ Weapon Comparison")

    # Extract weapon performance from recent fights
    fights = session.combat_log[-3:]  # Last 3 fights for comparison
    weapon_stats = []

    for fight in fights:
        stats = extract_weapon_stats_from_fight(fight, session.player, provider)
        weapon_stats.append(stats)

    if weapon_stats:
        col1, col2, col3 = st.columns(3)

        columns = [col1, col2, col3]
        labels = ["Previous", "Recent", "Current"]

        for i, (stats, col, label) in enumerate(zip(weapon_stats, columns, labels)):
            with col:
                st.markdown(f"**{label} Fight**")
                if stats:
                    st.metric("Total Hits", stats.get('total_hits', 0))
                    st.metric("Avg DPS", f"{stats.get('avg_dps', 0):.1f}")
                    st.metric("Effect Uptime", f"{stats.get('effect_uptime', 0):.1f}%")
                else:
                    st.write("No weapon data")

def extract_weapon_stats_from_fight(fight_report, player, provider) -> Dict[str, Any]:
    """Extract weapon performance statistics from a simulation report."""

    if not fight_report or not isinstance(fight_report, dict):
        return {}

    weapon = player.equipment.get("Weapon")
    if not weapon:
        return {}

    # Extract data from simulation report structure
    damage_breakdown = fight_report.get('damage_breakdown', {})
    logger_entries = fight_report.get('logger_entries', [])

    # Get player damage stats
    player_damage = damage_breakdown.get('hero_player', {}).get('total_damage', 0)
    player_hits = damage_breakdown.get('hero_player', {}).get('hits', 0)

    # Calculate fight duration
    fight_duration = fight_report.get('duration', 10.0)  # Default 10s if not available

    # Count effect applications from logger entries
    effect_triggers = 0
    for entry in logger_entries:
        if isinstance(entry, dict) and entry.get('event_type') == 'effect_apply':
            effect_triggers += 1

    return {
        'total_hits': player_hits,
        'total_damage': player_damage,
        'avg_dps': player_damage / fight_duration if fight_duration > 0 else 0,
        'effect_uptime': (effect_triggers / player_hits * 100) if player_hits > 0 else 0
    }
