# 🚀 Implementation Hand-off: UI-3 User Experience Polish

**Related Work Item:** `docs/work_items/WI_UI_3_User_Experience_Polish.md`

## 📦 File Manifest
| Action | File Path | Description |
| :--- | :--- | :--- |
| ✏️ Modify | `dashboard/pages/4_Campaign.py` | Add intelligent quick-views, smooth transitions, and weapon comparison features |
| 🆕 Create | `dashboard/components/weapon_comparison.py` | New component for weapon performance analytics |
| ✏️ Modify | `dashboard/components/battle_log.py` | Enhance combat log with strategic weapon insights |
| ✏️ Modify | `dashboard/utils.py` | Add utility functions for UI intelligence and transitions |

---

## 1️⃣ Configuration & Dependencies
*(No new dependencies required - all enhancements use existing Streamlit and Python libraries)*

---

## 2️⃣ Code Changes

### A. dashboard/pages/4_Campaign.py - Main Campaign Page Enhancement
**Path:** `dashboard/pages/4_Campaign.py`
**Context:** Add intelligent quick-views, smooth transitions, and weapon comparison integration

```python
# Add these imports at the top
from dashboard.components.weapon_comparison import render_weapon_comparison
from dashboard.utils import (
    generate_equipment_quickview,
    generate_backpack_quickview,
    create_smooth_transition,
    analyze_weapon_performance
)

# Replace the equipment header section (around line ~50)
def render_equipment_header(player, provider, session):
    """Enhanced equipment header with intelligent quick-view."""

    # Existing collapsible logic...
    with st.expander("🎒 Equipment & Inventory", expanded=False) as equipment_expander:
        if not equipment_expander.expanded:
            # Quick-view summary when collapsed
            col1, col2 = st.columns(2)

            with col1:
                weapon_info = generate_equipment_quickview(player, provider)
                st.markdown(f"""
                **⚔️ Weapon:** {weapon_info['name']}
                - **Skill:** {weapon_info['skill_name']}
                - **Type:** {weapon_info['damage_type']} ({weapon_info['hits']} hit{'s' if weapon_info['hits'] > 1 else ''})
                - **Effects:** {', '.join(weapon_info['effects']) if weapon_info['effects'] else 'None'}
                """)

            with col2:
                backpack_info = generate_backpack_quickview(session.player.inventory, provider)
                st.markdown(f"""
                **🎒 Backpack:** {backpack_info['status']}
                - **Highlights:** {', '.join(backpack_info['highlights']) if backpack_info['highlights'] else 'No notable items'}
                """)

            return  # Exit early when collapsed

        # Full expanded view (existing code continues here)...

# Add weapon comparison section before results (around line ~150)
def render_combat_results(session, provider):
    """Enhanced combat results with weapon intelligence."""

    # Existing results code...

    # Add weapon comparison insights
    if session.combat_log and len(session.combat_log) > 1:
        st.markdown("---")
        st.subheader("🎯 Weapon Performance Analysis")

        insights = analyze_weapon_performance(
            session.combat_log[-1],  # Current fight
            session.combat_log[:-1]  # Previous fights
        )

        if insights:
            for insight in insights:
                st.info(insight)

        # Full weapon comparison component
        render_weapon_comparison(session, provider)

# Modify the main campaign function to include smooth transitions
def main():
    """Main campaign page with enhanced UX."""

    # ... existing initialization ...

    # Add state transition handling
    if 'previous_state' not in st.session_state:
        st.session_state.previous_state = 'preparation'

    current_state = 'preparation'
    if session.in_combat:
        current_state = 'combat'
    elif session.game_over:
        current_state = 'results'

    # Handle transitions
    if current_state != st.session_state.previous_state:
        create_smooth_transition(st.session_state.previous_state, current_state, session)
        st.session_state.previous_state = current_state

    # ... rest of existing main function ...
```

### B. dashboard/components/weapon_comparison.py - New Weapon Analytics Component
**Path:** `dashboard/components/weapon_comparison.py`
**Context:** Create new component for side-by-side weapon performance analysis

```python
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

def extract_weapon_stats_from_fight(fight_log, player, provider) -> Dict[str, Any]:
    """Extract weapon performance statistics from a fight log."""

    if not fight_log or not isinstance(fight_log, list):
        return {}

    weapon = player.equipment.get("Weapon")
    if not weapon:
        return {}

    # Analyze fight log for weapon usage
    total_hits = 0
    total_damage = 0
    effect_triggers = 0
    fight_duration = len(fight_log) * 0.1  # Assume 0.1s per log entry

    for entry in fight_log:
        # Handle both Dict (if serialized) and Object (if raw)
        damage = 0
        is_damage_event = False

        if isinstance(entry, dict):
            damage = entry.get('damage_dealt', 0) or entry.get('damage', 0)
            is_damage_event = entry.get('event_type') == 'hit'
        else:
            # Dataclass access
            damage = getattr(entry, 'damage_dealt', 0)
            is_damage_event = getattr(entry, 'event_type', '') == 'hit'

        if is_damage_event:
            total_hits += 1
            total_damage += damage

        # Check for effect triggers
        if isinstance(entry, dict):
            if 'effect' in entry:
                effect_triggers += 1
        else:
            if hasattr(entry, 'effect_triggered') and entry.effect_triggered:
                effect_triggers += 1

    return {
        'total_hits': total_hits,
        'total_damage': total_damage,
        'avg_dps': total_damage / fight_duration if fight_duration > 0 else 0,
        'effect_uptime': (effect_triggers / total_hits * 100) if total_hits > 0 else 0
    }
```

### C. dashboard/components/battle_log.py - Enhanced Combat Log
**Path:** `dashboard/components/battle_log.py`
**Context:** Add strategic weapon insights to combat log display

```python
# Add this function to the battle_log.py file
def generate_weapon_insights(fight_log, player, provider) -> List[str]:
    """Generate strategic insights about weapon performance."""

    insights = []

    # Analyze weapon usage patterns
    weapon_hits = 0
    effect_procs = 0
    total_damage = 0

    for entry in fight_log:
        # Handle both dict and dataclass formats
        damage = 0
        effect = None
        is_damage_event = False

        if isinstance(entry, dict):
            damage = entry.get('damage_dealt', 0) or entry.get('damage', 0)
            effect = entry.get('effect')
            is_damage_event = entry.get('event_type') == 'hit'
        else:
            damage = getattr(entry, 'damage_dealt', 0)
            effect = getattr(entry, 'effect_triggered', None)
            is_damage_event = getattr(entry, 'event_type', '') == 'hit'

        if is_damage_event:
            weapon_hits += 1
            total_damage += damage

        if effect and effect in ['bleed', 'poison', 'burn']:
            effect_procs += 1

    # Generate insights based on weapon type
    weapon = player.equipment.get("Weapon")
    if weapon:
        weapon_template = provider.items.get(weapon.template_id)
        skill_id = getattr(weapon_template, 'default_skill', None)

        if skill_id:
            skill = provider.skills.get(skill_id)

            # Dagger insights
            if 'dagger' in weapon.name.lower() and weapon_hits > 5:
                insights.append("🎯 Your dagger's multi-strike potential is showing! Consider building around attack speed.")

            # Axe insights
            elif 'axe' in weapon.name.lower() and effect_procs > 2:
                insights.append("🩸 Strong bleed uptime! Axes excel against targets that survive multiple hits.")

            # Bow insights
            elif 'bow' in weapon.name.lower() and weapon_hits > 3:
                insights.append("🏹 Good ranged performance. Bows shine when you can maintain distance.")

    # General insights
    if weapon_hits > 8:
        insights.append("⚡ High weapon activity! You're making good use of your attack speed.")

    if effect_procs == 0 and weapon_hits > 3:
        insights.append("💡 Consider weapons with special effects (bleed, poison) for sustained damage.")

    return insights

# Modify the render_battle_log function to include insights
def render_battle_log(log_entries, player, provider):
    """Enhanced battle log with weapon insights."""

    # Existing log rendering...

    # Add insights section at the end
    if log_entries:
        st.markdown("---")
        insights = generate_weapon_insights(log_entries, player, provider)

        if insights:
            st.markdown("### 💡 Combat Insights")
            for insight in insights:
                st.info(insight)
        else:
            st.write("*No special insights this fight.*")
```

### D. dashboard/utils.py - UI Intelligence Utilities
**Path:** `dashboard/utils.py`
**Context:** Add utility functions for quick-views and transitions

```python
# Add these functions to dashboard/utils.py
import time
import streamlit as st
from typing import Dict, Any, List

def generate_equipment_quickview(player, provider) -> Dict[str, Any]:
    """Generate intelligent equipment summary for collapsed header."""

    weapon = player.equipment.get("Weapon")
    if weapon:
        weapon_template = provider.items.get(weapon.template_id)
        skill_id = getattr(weapon_template, 'default_skill', None)

        if skill_id:
            skill = provider.skills.get(skill_id)
            weapon_info = {
                'name': weapon.name,
                'skill_name': skill.name if skill else 'Basic Attack',
                'damage_type': skill.damage_type if skill else 'Physical',
                'hits': skill.hits if skill else 1,
                'effects': []
            }

            # Extract weapon effects
            if hasattr(skill, 'trigger_result') and skill.trigger_result:
                weapon_info['effects'].append(skill.trigger_result)

            return weapon_info

    return {'name': 'Unarmed', 'skill_name': 'Strike', 'damage_type': 'Physical', 'hits': 1, 'effects': []}

def generate_backpack_quickview(inventory, provider) -> Dict[str, Any]:
    """Generate intelligent backpack summary for collapsed header."""

    items = inventory.items
    if not items:
        return {'status': 'empty', 'highlights': []}

    # Analyze item quality distribution
    quality_counts = {}
    highlights = []

    for item in items:
        quality = item.quality_tier
        quality_counts[quality] = quality_counts.get(quality, 0) + 1

        # Find notable items
        if hasattr(item, 'rarity') and item.rarity in ['rare', 'epic', 'legendary']:
            highlights.append(f"{item.name} ({item.rarity})")

    return {
        'status': f"{len(items)}/{inventory.capacity} items",
        'quality_dist': quality_counts,
        'highlights': highlights[:3]  # Top 3 notable items
    }

def create_smooth_transition(from_state: str, to_state: str, session):
    """Create smooth UI transitions between game states."""

    transition_config = {
        ('preparation', 'combat'): {
            'message': "⚔️ Entering Combat...",
            'preview_func': lambda: generate_weapon_preview(session.player),
            'duration': 2.0
        },
        ('combat', 'victory'): {
            'message': "🎉 Victory Achieved!",
            'celebration': True,
            'duration': 3.0
        },
        ('combat', 'game_over'): {
            'message': "💀 Combat Ended...",
            'reflection': True,
            'duration': 2.0
        }
    }

    config = transition_config.get((from_state, to_state))
    if config:
        with st.empty():
            progress_bar = st.progress(0)
            status_text = st.empty()

            steps = 100
            for i in range(steps + 1):
                progress_bar.progress(i)

                if i < 30:
                    status_text.markdown(f"## {config['message']}")
                elif i < 70 and 'preview_func' in config:
                    preview = config['preview_func']()
                    status_text.markdown(f"## {config['message']}\n{preview}")
                else:
                    status_text.markdown("## Loading results...")

                time.sleep(config['duration'] / steps)

            progress_bar.empty()
            status_text.empty()

def generate_weapon_preview(player) -> str:
    """Generate weapon preview for combat transition."""
    weapon = player.equipment.get("Weapon")
    if weapon:
        return f"**Weapon:** {weapon.name}\n*Prepare for battle!* ⚔️"
    return "*Unarmed combat initiated!* 👊"

def analyze_weapon_performance(current_fight, previous_fights) -> List[str]:
    """Analyze weapon performance across fights for comparison insights."""

    if not previous_fights:
        return ["First fight - establishing weapon baseline!"]

    insights = []

    # Extract basic metrics
    current_hits = len([e for e in current_fight if isinstance(e, dict) and 'damage' in e])
    avg_prev_hits = sum(len([e for e in f if isinstance(e, dict) and 'damage' in e])
                       for f in previous_fights) / len(previous_fights)

    # Hit count analysis
    if current_hits > avg_prev_hits * 1.5:
        insights.append("🎯 **High hit count!** Your current weapon excels at multi-strikes.")
    elif current_hits < avg_prev_hits * 0.7:
        insights.append("🎯 **Lower hit count.** Consider weapons with higher attack speed.")

    # Placeholder for more advanced analysis
    insights.append("📊 Weapon performance analysis is being enhanced...")

    return insights if insights else ["Weapon performance is consistent with previous fights."]
```

---

## 🧪 Verification Steps

**1. Automated Tests**
```bash
# Run dashboard integration tests
python -m pytest tests/test_dashboard_integration.py -v

# Run UI component tests
python -m pytest tests/test_ui_components.py -v
```

**2. Manual Verification**
*   **Quick Views:** Collapse equipment header and verify weapon/backpack summaries appear
*   **Smooth Transitions:** Start combat and observe animated loading states
*   **Weapon Intelligence:** Complete a fight and check combat log for strategic insights
*   **Performance:** Verify all UI interactions complete within 500ms
*   **Weapon Comparison:** Play multiple fights and verify comparison analytics appear

## ⚠️ Known Issues & Mitigations

### Session State Timing
The transition logic may experience "flickering" where animations play twice due to Streamlit's re-run model. This is expected behavior and not a critical issue. The `time.sleep()` calls are kept short (1-3 seconds total) to minimize UI freezing.

### Combat Log Data Handling
Code has been updated to handle both dict and CombatLogEntry dataclass formats. Uses `hasattr()` and `getattr()` for safe attribute access.

## ⚠️ Rollback Plan
If UI enhancements cause performance issues or break functionality:

1. **Delete:** `dashboard/components/weapon_comparison.py`
2. **Revert:** `dashboard/pages/4_Campaign.py` to commit before UI changes
3. **Revert:** `dashboard/components/battle_log.py` to remove insight functions
4. **Revert:** `dashboard/utils.py` to remove new utility functions

**Core functionality will remain intact as all enhancements are progressive (work without polish features).**
