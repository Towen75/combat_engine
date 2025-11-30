import streamlit as st
import time
from dashboard.utils import (
    get_game_session,
    get_game_data_provider,
    load_css,
    display_portrait,
    generate_equipment_quickview,
    generate_backpack_quickview,
    create_smooth_transition,
    analyze_weapon_performance
)
from dashboard.components.item_card import render_item_card
from dashboard.components.weapon_comparison import render_weapon_comparison
from src.game.enums import GameState
from src.data.typed_models import ItemSlot

# Page Config
st.set_page_config(page_title="The Campaign", page_icon="🗺️", layout="wide")
load_css()

def main():
    st.title("🗺️ THE CAMPAIGN")

    session = get_game_session()
    if session is None:
        st.error("Failed to initialize game session")
        return

    provider = get_game_data_provider()

    # Add state transition handling
    if 'previous_state' not in st.session_state:
        st.session_state.previous_state = session.state

    current_state = session.state

    # Handle transitions
    if current_state != st.session_state.previous_state:
        create_smooth_transition(st.session_state.previous_state, current_state, session)
        st.session_state.previous_state = current_state

    # DEBUG: State Visualizer
    with st.expander("Debug State", expanded=True):
        st.write(f"State: {session.state}")
        st.write(f"Stage: {session.current_stage}")
        if session.player:
            st.write(f"HP: {session.player.final_stats.max_health:.0f}")

        # Show combat report if available
        if session.last_report:
            st.write("**Last Combat Report:**")
            # Fix: Use correct report structure
            duration = session.last_report.get('duration', 0)
            total_events = session.last_report.get('total_events', 0)
            damage_breakdown = session.last_report.get('damage_breakdown', {})

            # Calculate total hits and player damage from damage_breakdown
            total_hits = sum(stats.get('hits', 0) for stats in damage_breakdown.values())
            player_damage = damage_breakdown.get('hero_player', {}).get('total_damage', 0)

            st.write(f"- Duration: {duration:.2f}s")
            st.write(f"- Total Events: {total_events}")
            st.write(f"- Total Hits: {total_hits}")
            st.write(f"- Player Damage: {player_damage:.1f}")

    # --- ROUTER ---
    if session.state == GameState.LOBBY:
        render_lobby(session, provider)
    elif session.state == GameState.PREPARATION:
        render_preparation(session, provider)
    elif session.state == GameState.COMBAT:
        render_combat(session)
    elif session.state == GameState.VICTORY:
        render_victory(session)
    elif session.state == GameState.GAME_OVER:
        render_game_over(session)

# --- VIEWS ---

def render_combat_log(session, provider):
    """Render detailed combat log for weapon mechanics visibility.

    Args:
        session: GameSession with combat results
        provider: GameDataProvider for entity/item lookups
    """
    # Access combat simulation results
    report = session.last_report
    if not report:
        st.warning("No combat data available")
        return

    # Extract weapon mechanics events from CombatLogger.entries
    skill_events = []
    attack_events = []
    effect_events = []
    damage_events = []

    # Parse CombatLogger entries for weapon-relevant events
    logger_entries = report.get('logger_entries', [])
    for entry in logger_entries:
        event_type = entry.event_type

        if event_type == 'hit':
            # Regular attacks (basic attacks from both player and enemy)
            attack_events.append({
                'attacker_id': entry.attacker_id,
                'defender_id': entry.defender_id,
                'damage': entry.damage_dealt or 0,
                'is_crit': entry.is_crit or False,
                'timestamp': entry.timestamp
            })

        elif event_type == 'skill_use' or event_type == 'skill':
            # Weapon skill usage - check if it's a special weapon skill vs basic attack
            skill_obj = entry.metadata.get('skill')
            skill_id = skill_obj.id if hasattr(skill_obj, 'id') else str(skill_obj)

            # Only treat as special ability if it's not a basic attack skill
            if not skill_id.startswith('attack_') or skill_id in ['attack_dual_slash', 'attack_heavy_swing', 'attack_cleave', 'attack_precise_shot']:
                # This is a special weapon skill
                skill_events.append({
                    'entity_id': entry.attacker_id,
                    'skill_name': skill_obj,
                    'damage_breakdown': entry.metadata.get('damage_breakdown', []),
                    'timestamp': entry.timestamp
                })
            else:
                # This is a basic attack, treat it as a regular attack
                attack_events.append({
                    'attacker_id': entry.attacker_id,
                    'defender_id': entry.defender_id,
                    'damage': entry.metadata.get('damage_breakdown', [0])[0] if entry.metadata.get('damage_breakdown') else 0,
                    'is_crit': False,  # Skills don't track crit separately in current implementation
                    'timestamp': entry.timestamp
                })

        elif event_type == 'effect_apply':
            # Status effect applications (bleed, poison, etc.)
            effect_events.append({
                'target_id': entry.defender_id,
                'effect_name': entry.effect_name,
                'stacks': entry.effect_stacks or 1,
                'timestamp': entry.timestamp
            })

        elif event_type == 'damage_tick':
            # Damage over time from effects
            damage_events.append({
                'target_id': entry.defender_id,
                'effect_name': entry.effect_name,
                'damage': entry.damage_dealt or 0,
                'timestamp': entry.timestamp
            })

    # Display all attacks (regular attacks from both sides)
    with st.expander("⚔️ Combat Attacks", expanded=True):
        if attack_events:
            # Sort by timestamp to show chronological order
            attack_events.sort(key=lambda x: x.get('timestamp', 0))

            for event in attack_events:
                message = format_attack_message(event, provider)
                st.write(f"⚔️ {message}")
        else:
            st.info("No attacks occurred in this combat")

    # Display weapon skill usage (keeping for now as separate section)
    with st.expander("🗡️ Special Abilities", expanded=False):
        if skill_events:
            for event in skill_events:
                message = format_skill_message(event, provider)
                st.write(f"🔸 {message}")
        else:
            st.info("No special abilities used in this combat")

    # Display effect applications and damage
    with st.expander("✨ Combat Effects", expanded=True):
        if effect_events or damage_events:
            # Show effect applications
            for event in effect_events:
                message = format_effect_message(event, provider)
                st.write(f"💫 {message}")

            # Show damage over time
            dot_summary = {}
            for event in damage_events:
                key = f"{event['target_id']}_{event['effect_name']}"
                if key not in dot_summary:
                    dot_summary[key] = {
                        'target_id': event['target_id'],
                        'effect_name': event['effect_name'],
                        'total_damage': 0,
                        'ticks': 0
                    }
                dot_summary[key]['total_damage'] += event['damage']
                dot_summary[key]['ticks'] += 1

            for summary in dot_summary.values():
                target_name = get_entity_display_name(summary['target_id'], provider)
                effect_name = summary['effect_name'].replace('_', ' ').title()
                st.write(f"💔 {target_name} took {summary['total_damage']:.1f} {effect_name} damage ({summary['ticks']} ticks)")
        else:
            st.info("No special effects triggered")

    # Summary statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        total_damage = report.get('damage_analysis', {}).get('summary', {}).get('total_damage', 0)
        st.metric("Total Damage", f"{total_damage:.1f}")
    with col2:
        duration = report.get('performance_analysis', {}).get('simulation_duration', 0)
        st.metric("Combat Duration", f"{duration:.2f}s")
    with col3:
        effect_count = len(effect_events)
        st.metric("Effects Applied", effect_count)

def format_attack_message(event, provider):
    """Format a regular attack message.

    Args:
        event: Attack event data
        provider: GameDataProvider for entity lookups

    Returns:
        Formatted message string
    """
    attacker_name = get_entity_display_name(event['attacker_id'], provider)
    defender_name = get_entity_display_name(event['defender_id'], provider)
    damage = int(event.get('damage', 0))
    is_crit = event.get('is_crit', False)

    if is_crit:
        return f"{attacker_name} critically hits {defender_name} for {damage} damage!"
    else:
        return f"{attacker_name} attacks {defender_name} for {damage} damage"

def format_skill_message(event, provider):
    """Format a weapon skill usage message.

    Args:
        event: Skill event data
        provider: GameDataProvider for entity lookups

    Returns:
        Formatted message string
    """
    entity_name = get_entity_display_name(event['entity_id'], provider)

    # Handle skill name - could be string or skill object
    skill_obj = event['skill_name']
    if hasattr(skill_obj, 'name'):
        # It's a skill object, extract the name
        skill_name = skill_obj.name
    else:
        # It's already a string
        skill_name = skill_obj or 'Unknown Skill'

    damage_breakdown = event.get('damage_breakdown', [])

    if damage_breakdown and len(damage_breakdown) > 1:
        # Multi-hit skill (e.g., Dual Slash)
        total = sum(damage_breakdown)
        hits_str = " + ".join(f"{int(d)}" for d in damage_breakdown)
        return f"{entity_name} {skill_name.lower()}s ({hits_str} = {int(total)} damage)"
    elif damage_breakdown and len(damage_breakdown) == 1:
        # Single-hit skill (e.g., Heavy Swing)
        return f"{entity_name} {skill_name.lower()}s for {int(damage_breakdown[0])} damage"
    else:
        # No damage data available
        return f"{entity_name} uses {skill_name}"

def format_effect_message(event, provider):
    """Format a status effect application message.

    Args:
        event: Effect event data
        provider: GameDataProvider for entity lookups

    Returns:
        Formatted message string
    """
    target_name = get_entity_display_name(event['target_id'], provider)
    effect_name = event['effect_name'].replace('_', ' ').title()
    stacks = event.get('stacks', 1)

    if stacks > 1:
        return f"{effect_name} ({stacks} stacks) applied to {target_name}"
    else:
        return f"{effect_name} applied to {target_name}"

def get_entity_display_name(entity_id, provider):
    """Get display name for an entity ID.

    Args:
        entity_id: Entity identifier
        provider: GameDataProvider for lookups

    Returns:
        Display name string
    """
    if not entity_id:
        return "Unknown"

    # Handle special cases
    if entity_id == 'hero_player':
        return "Hero"
    elif entity_id.startswith('enemy_'):
        # Try to get enemy name from template
        try:
            enemy_template = provider.entities.get(entity_id.replace('enemy_', ''))
            if enemy_template:
                return enemy_template.name
        except:
            pass
        return "Enemy"

    # Fallback
    return entity_id.replace('_', ' ').title()

def render_lobby(session, provider):
    st.markdown("### 🏰 Choose Your Hero")

    # Filter entities for archetypes containing "Hero" (case insensitive) or specific ID pattern
    # Assuming 'entities.csv' has archetype column.
    # Logic: Get all entities, filter where archetype == 'Hero'
    hero_options = [
        eid for eid, e in provider.entities.items()
        if e.archetype.lower() == "hero"
    ]

    if not hero_options:
        st.warning("No 'Hero' archetypes found in entities.csv.")
        return

    c1, c2 = st.columns([1, 2])
    with c1:
        selected_hero = st.selectbox("Select Class", hero_options, format_func=lambda x: provider.entities[x].name)
        seed = st.number_input("Destiny Seed", value=42, help="Determines the entire campaign generation")

    with c2:
        # Show Hero Preview
        template = provider.entities[selected_hero]

        # NEW: Display hero portrait
        display_portrait(template.portrait_path, width=128)

        st.info(f"""
        **{template.name}**

        *HP:* {template.base_health} | *Dmg:* {template.base_damage} | *Spd:* {template.attack_speed}

        *{template.description}*
        """)

    if st.button("⚔️ Begin Campaign", type="primary", use_container_width=True):
        session.start_new_run(selected_hero, seed)
        st.rerun()

def render_preparation(session, provider):
    player = session.player
    st.subheader(f"Stage {session.current_stage + 1}: Preparation")

    col_hero, col_inv = st.columns([1, 1])

    # --- LEFT: HERO & SLOTS ---
    with col_hero:
        # Generate equipment summary for header
        weapon_name = "Unarmed"
        weapon_skill = "Strike"
        if player.equipment.get("Weapon"):
            weapon_item = player.equipment["Weapon"]
            weapon_name = weapon_item.name
            # Try to get skill name from weapon template
            try:
                weapon_template = provider.items.get(weapon_item.template_id)
                if weapon_template and hasattr(weapon_template, 'default_skill'):
                    skill_id = weapon_template.default_skill
                    skill = provider.skills.get(skill_id)
                    if skill:
                        weapon_skill = skill.name
            except:
                pass  # Fallback to default

        # Stats summary for header
        stats = player.final_stats
        stats_summary = f"❤️{stats.max_health:.0f} ⚔️{stats.base_damage:.1f} 🛡️{stats.armor:.0f}"

        # Equipment expander with intelligent header
        # Generate quick-view for header display
        weapon_info = generate_equipment_quickview(player, provider)
        quick_view = f"{weapon_info['name']} ({weapon_info['skill_name']})"

        with st.expander(f"🛡️ Equipment - {player.name} | {quick_view} | {stats_summary}", expanded=False):
            # Always show quick view first
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**⚔️ Weapon Summary**")
                st.markdown(f"""
                - **Name:** {weapon_info['name']}
                - **Skill:** {weapon_info['skill_name']}
                - **Type:** {weapon_info['damage_type']}
                - **Hits:** {weapon_info['hits']} per attack
                - **Effects:** {', '.join(weapon_info['effects']) if weapon_info['effects'] else 'None'}
                """)

            with col2:
                st.markdown("**📊 Combat Stats**")
                st.markdown(f"""
                - **❤️ Health:** {stats.max_health:.0f}
                - **⚔️ Damage:** {stats.base_damage:.1f}
                - **🛡️ Armor:** {stats.armor:.0f}
                - **⚡ Crit:** {stats.crit_chance*100:.1f}%
                """)

            st.markdown("---")

            # Full expanded view with hero details
            st.markdown(f"### 🛡️ {player.name}")

            # NEW: Display hero portrait (with safe lookup)
            hero_template = None
            if player.template_id:
                hero_template = provider.entities.get(player.template_id)
            if hero_template:
                display_portrait(hero_template.portrait_path, width=128)
            else:
                # Fallback if no template found - could use a default portrait
                st.caption("Hero portrait not available")

            st.markdown("#### Currently Equipped")

            # Render slots dynamically based on Enum
            slots = [s for s in ItemSlot]

            for slot in slots:
                slot_name = slot.value
                equipped_item = player.equipment.get(slot_name)

                with st.container(border=True):
                    c_info, c_btn = st.columns([3, 1])
                    with c_info:
                        if equipped_item:
                            # 1. Basic Info
                            st.markdown(f"**{slot_name}:** {equipped_item.name} <span style='color:orange'>({equipped_item.rarity})</span>", unsafe_allow_html=True)

                            # 2. NEW: Display Affixes underneath
                            if equipped_item.affixes:
                                for affix in equipped_item.affixes:
                                    # Simple formatting
                                    val = affix.value
                                    # Handle multipliers for display
                                    if affix.mod_type == "multiplier":
                                        val = f"{val * 100:.1f}%"
                                    else:
                                        val = f"{val:.1f}"

                                    st.caption(f"• {affix.description.replace('{value}', str(val))}")
                            else:
                                st.caption("• *No Affixes*")
                        else:
                            st.markdown(f"**{slot_name}:** *Empty*")

                    with c_btn:
                        if equipped_item:
                            if st.button("Unequip", key=f"unequip_{slot_name}"):
                                if session.inventory.is_full:
                                    st.error("Inventory Full!")
                                else:
                                    session.inventory.unequip_item(player, slot_name)
                                    st.rerun()

    # --- RIGHT: INVENTORY & NEXT ENEMY ---
    with col_inv:
        # Show next enemy info
        enemy_id = session._get_current_enemy_id()
        enemy_template = provider.entities[enemy_id]

        st.markdown("### 🎯 Next Enemy")
        # NEW: Display enemy portrait
        display_portrait(enemy_template.portrait_path, width=128)

        st.info(f"""
        **{enemy_template.name}**

        *HP:* {enemy_template.base_health} | *Dmg:* {enemy_template.base_damage} | *Arm:* {enemy_template.armor}

        *{enemy_template.description}*
        """)

        # Generate backpack summary for header
        inventory = session.inventory
        capacity_text = f"{inventory.count}/{inventory.capacity}"

        # Find notable items for header highlights
        notable_items = []
        if inventory.items:
            for item in inventory.items:
                if item.rarity in ['rare', 'epic']:
                    notable_items.append(f"{item.name} ({item.rarity})")
            notable_items = notable_items[:2]  # Limit to 2 highlights

        header_text = f"🎒 Backpack ({capacity_text})"
        if notable_items:
            header_text += f" - {', '.join(notable_items)}"
        elif inventory.count == 0:
            header_text += " - Empty"
        else:
            header_text += f" - {inventory.count} items"

        # Backpack expander with expanded state by default (for new users)
        with st.expander(header_text, expanded=True):
            if inventory.count == 0:
                st.info("Your inventory is empty.")
            else:
                # Render grid of items
                items = inventory.items

                # Display in rows of 2
                for i in range(0, len(items), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(items):
                            item = items[i+j]
                            with cols[j]:
                                # Render visual card
                                render_item_card(item.__dict__, provider)

                                # Action Button
                                if st.button("Equip", key=f"equip_{item.instance_id}", use_container_width=True):
                                    session.inventory.equip_item(player, item.instance_id)
                                    st.rerun()

    st.markdown("---")
    if st.button("🔴 FIGHT NEXT ENEMY", type="primary", use_container_width=True):
        # Run combat logic once
        with st.spinner("Fighting enemy..."):
            success = session.execute_combat_turn()
            if success:
                st.success("Combat completed!")
            else:
                st.error("Combat completed!")
        st.rerun()

def render_combat(session):
    st.subheader("⚔️ Combat Resolution")

    # Show combat results from the last run
    report = session.last_report
    if not report:
        st.error("No combat report found.")
        if st.button("Back to Preparation"):
            session.state = GameState.PREPARATION
            st.rerun()
        return

    # Show results
    perf = report.get('performance_analysis', {})
    dmg = report.get('damage_analysis', {}).get('summary', {})

    if session.state == GameState.VICTORY:
        st.success("🎉 VICTORY! 🎉")
        st.balloons()
    elif session.state == GameState.GAME_OVER:
        st.error("💀 DEFEAT! 💀")

    # NEW: Show defeated enemy info
    provider = get_game_data_provider()
    if provider:
        enemy_id = session._get_current_enemy_id()
        enemy_template = provider.entities[enemy_id]
    else:
        st.error("Could not load game data")
        return

    col_player, col_enemy = st.columns([1, 1])

    with col_player:
        st.markdown("### 🛡️ Your Hero")
        # Could add hero portrait here too if desired
        st.info("Combat completed!")

    with col_enemy:
        st.markdown("### 💀 Defeated Enemy")
        # NEW: Display enemy portrait
        display_portrait(enemy_template.portrait_path, width=128)

        st.info(f"""
        **{enemy_template.name}**

        *Was defeated in battle*
        """)

    # Show combat stats
    render_combat_stats(session)

    # Continue button
    st.markdown("---")
    if st.button("Continue", type="primary"):
        st.rerun()

# Helper to show stats
def render_combat_stats(session):
    report = session.last_report
    if not report:
        return

    with st.expander("⚔️ Combat Report", expanded=True):
        # Fix: Use correct report structure
        duration = report.get('duration', 0)
        total_events = report.get('total_events', 0)
        damage_breakdown = report.get('damage_breakdown', {})

        # Calculate stats from damage_breakdown
        total_hits = sum(stats.get('hits', 0) for stats in damage_breakdown.values())
        player_damage = damage_breakdown.get('hero_player', {}).get('total_damage', 0)

        c1, c2, c3 = st.columns(3)
        c1.metric("Duration", f"{duration:.2f}s")
        c2.metric("Total Hits", total_hits)
        c3.metric("Player Damage", f"{player_damage:.1f}")

def render_victory(session):
    st.title("🏆 VICTORY")

    render_combat_stats(session)
    st.balloons()

    # Add weapon comparison insights
    provider = get_game_data_provider()
    if provider and session.combat_log and len(session.combat_log) > 1:
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

    # NEW: Add combat log display with insights
    if provider:
        from dashboard.components.battle_log import render_battle_log_with_insights
        render_battle_log_with_insights(session.last_report.get('logger_entries', []), session.player, provider)

    st.markdown("### 💰 Loot Found")

    if not session.loot_stash:
        st.info("No loot found.")
    else:
        # Loot Grid
        cols = st.columns(3)
        provider = get_game_data_provider()

        # Iterate over a copy or by index to safely modify list via claims
        # We use index for claim_loot
        for idx, item in enumerate(session.loot_stash):
            col = cols[idx % 3]
            with col:
                render_item_card(item.__dict__, provider)
                if st.button("Take", key=f"take_{idx}_{item.instance_id}"):
                    if session.claim_loot(idx):
                        st.toast(f"Picked up {item.name}")
                        st.rerun()
                    else:
                        st.error("Inventory Full!")

    st.markdown("---")
    if st.button("➡️ Advance to Next Stage", type="primary"):
        session.advance_stage()
        st.rerun()

def render_game_over(session):
    st.title("💀 GAME OVER")
    render_combat_stats(session)
    st.error(f"You fell at Stage {session.current_stage + 1}")

    # NEW: Add combat log display
    provider = get_game_data_provider()
    if provider:
        render_combat_log(session, provider)

    if st.button("Return to Lobby"):
        session.state = GameState.LOBBY
        st.rerun()

if __name__ == "__main__":
    main()
