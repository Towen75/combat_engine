import streamlit as st

def render_battle_log(events, provider=None, hero_name=None):
    """
    Renders the battle log with styled events.

    Args:
        events (list): A list of CombatLogEntry objects from the combat engine.
        provider (GameDataProvider, optional): Provider for entity name lookups.
        hero_name (str, optional): Name of the hero entity for display.
    """
    st.markdown("### 📜 Battle Log")

    with st.container(border=True, height=300):
        if not events:
            st.info("⚔️ No combat events yet. Start a fight!")
            return

        for i, event in enumerate(events):
            # Handle both dict and CombatLogEntry formats
            if hasattr(event, 'event_type'):
                # CombatLogEntry object
                e_type = event.event_type
                # Generate message from CombatLogEntry attributes
                message = generate_message_from_log_entry(event, provider, hero_name)
            else:
                # Fallback for dict format
                e_type = event.get("type", "info")
                message = event.get("message", str(event))

            # Color coding with emoji icons (matching spec)
            if e_type == "damage" or e_type == "hit":
                st.markdown(f"🔴 **DAMAGE** › {message}")
            elif e_type == "heal":
                st.markdown(f"🟢 **HEAL** › {message}")
            elif e_type == "block":
                st.markdown(f"🛡️ **BLOCK** › {message}")
            elif e_type == "crit":
                st.markdown(f"🟡 **CRITICAL HIT!** › {message}")
            elif e_type == "dodge":
                st.markdown(f"💨 **DODGE** › {message}")
            elif e_type == "effect_apply":
                st.markdown(f"✨ **EFFECT** › {message}")
            else:
                st.markdown(f"• {message}")

def generate_message_from_log_entry(entry, provider=None, hero_name=None):
    """Generate a human-readable message from a CombatLogEntry object."""
    try:
        event_type = entry.event_type

        if event_type == "hit":
            attacker = format_entity_name(getattr(entry, 'attacker_id', 'Unknown'), provider, hero_name)
            defender = format_entity_name(getattr(entry, 'defender_id', 'Unknown'), provider, hero_name)
            damage = round(getattr(entry, 'damage_dealt', 0), 1)
            is_crit = getattr(entry, 'is_crit', False)

            if is_crit:
                return f"{attacker} critically hits {defender} for {damage} damage!"
            else:
                return f"{attacker} hits {defender} for {damage} damage"

        elif event_type == "effect_apply":
            target = format_entity_name(getattr(entry, 'defender_id', 'Unknown'), provider, hero_name)
            effect_name = getattr(entry, 'effect_name', 'Unknown Effect')
            return f"{effect_name} applied to {target}"

        elif event_type == "damage_tick":
            target = format_entity_name(getattr(entry, 'defender_id', 'Unknown'), provider, hero_name)
            effect_name = getattr(entry, 'effect_name', 'Unknown')
            damage = round(getattr(entry, 'damage_dealt', 0), 1)
            return f"{target} takes {damage} damage from {effect_name}"

        else:
            # Generic fallback
            return f"{event_type}: {getattr(entry, 'metadata', 'Unknown event')}"

    except Exception as e:
        return f"Event: {str(entry)}"

def format_entity_name(entity_id, provider=None, hero_name=None):
    """Convert entity IDs to user-friendly display names."""
    if not entity_id:
        return "Unknown"

    # Handle special cases
    if entity_id == 'hero_player':
        return hero_name or "Hero"
    elif entity_id.startswith('enemy_'):
        # For enemy instance IDs like 'enemy_stage_0', extract the stage and look up the template
        if provider and 'stage_' in entity_id:
            try:
                # Extract stage number from 'enemy_stage_X'
                stage_part = entity_id.split('stage_')[-1]
                stage_num = int(stage_part)

                # Get the campaign stages (hardcoded for now, could be passed in)
                campaign_stages = [
                    "goblin_grunt", "enemy_warrior_grunt", "enemy_rogue_thief", "enemy_mage_novice",
                    "orc_warrior", "enemy_warrior_guard", "enemy_rogue_assassin", "enemy_mage_sorcerer",
                    "enemy_warrior_boss", "enemy_rouge_boss", "enemy_mage_boss"
                ]

                # Look up the template ID for this stage
                template_id = campaign_stages[stage_num % len(campaign_stages)]

                # Get the entity name from the template
                if template_id in provider.entities:
                    return provider.entities[template_id].name

            except (ValueError, IndexError):
                pass  # Fall through to fallback logic

        # Fallback: try to extract enemy name from ID
        enemy_part = entity_id.replace('enemy_', '').replace('stage_', '')
        if enemy_part and enemy_part != entity_id:  # Make sure we actually changed something
            return enemy_part.replace('_', ' ').title()

    # Try to look up from provider if available
    if provider and entity_id in provider.entities:
        return provider.entities[entity_id].name

    # Final fallback: capitalize and space
    return entity_id.replace('_', ' ').title()

# Add this function to the battle_log.py file
def generate_weapon_insights(fight_report, player, provider) -> list[str]:
    """Generate strategic insights about weapon performance from simulation report."""

    insights = []

    if not fight_report or not isinstance(fight_report, dict):
        return insights

    # Extract data from simulation report
    damage_breakdown = fight_report.get('damage_breakdown', {})
    logger_entries = fight_report.get('logger_entries', [])

    # Get player stats
    player_damage = damage_breakdown.get('hero_player', {}).get('total_damage', 0)
    player_hits = damage_breakdown.get('hero_player', {}).get('hits', 0)

    # Count effect applications (handle both dict and CombatLogEntry)
    effect_procs = 0
    for entry in logger_entries:
        if isinstance(entry, dict):
            if entry.get('event_type') == 'effect_apply':
                effect_procs += 1
        else:  # CombatLogEntry object
            if getattr(entry, 'event_type', '') == 'effect_apply':
                effect_procs += 1

    # Generate insights based on weapon type
    weapon = player.equipment.get("Weapon")
    if weapon:
        weapon_template = provider.items.get(weapon.base_id)
        skill_id = getattr(weapon_template, 'default_attack_skill', None)

        if skill_id:
            skill = provider.skills.get(skill_id)

            # Dagger insights
            if 'dagger' in weapon.name.lower() and player_hits > 5:
                insights.append("🎯 Your dagger's multi-strike potential is showing! Consider building around attack speed.")

            # Axe insights
            elif 'axe' in weapon.name.lower() and effect_procs > 2:
                insights.append("🩸 Strong bleed uptime! Axes excel against targets that survive multiple hits.")

            # Bow insights
            elif 'bow' in weapon.name.lower() and player_hits > 3:
                insights.append("🏹 Good ranged performance. Bows shine when you can maintain distance.")

    # General insights
    if player_hits > 8:
        insights.append("⚡ High weapon activity! You're making good use of your attack speed.")

    if effect_procs == 0 and player_hits > 3:
        insights.append("💡 Consider weapons with special effects (bleed, poison) for sustained damage.")

    return insights

# Modify the render_battle_log function to include insights
def render_battle_log_with_insights(log_entries, player, provider):
    """Enhanced battle log with weapon insights."""

    # Existing log rendering...
    hero_name = getattr(player, 'name', 'Hero')
    render_battle_log(log_entries, provider, hero_name)

    # Add insights section at the end
    if log_entries:
        st.markdown("---")
        # Create a mock fight report structure for insights
        mock_fight_report = {
            'logger_entries': log_entries,
            'damage_breakdown': {}  # Could be enhanced to include actual damage data
        }
        insights = generate_weapon_insights(mock_fight_report, player, provider)

        if insights:
            st.markdown("### 💡 Combat Insights")
            for insight in insights:
                st.info(insight)
        else:
            st.write("*No special insights this fight.*")
