import streamlit as st
import time
from dashboard.utils import get_game_session, get_game_data_provider, load_css, display_portrait
from dashboard.components.item_card import render_item_card
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
        st.markdown(f"### 🛡️ {player.name}")

        # NEW: Display hero portrait
        hero_template = provider.entities[player.template_id]
        display_portrait(hero_template.portrait_path, width=128)

        # Stats Bar
        stats = player.final_stats
        st.caption(f"❤️ HP: {stats.max_health:.0f} | ⚔️ DMG: {stats.base_damage:.1f} | 🛡️ ARM: {stats.armor:.0f} | ⚡ CRIT: {stats.crit_chance*100:.1f}%")

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

        st.markdown("### 🎒 Backpack")
        st.markdown(f"({session.inventory.count}/{session.inventory.capacity})")

        if session.inventory.count == 0:
            st.info("Your inventory is empty.")

        # Render grid of items
        items = session.inventory.items

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

    if st.button("Return to Lobby"):
        session.state = GameState.LOBBY
        st.rerun()

if __name__ == "__main__":
    main()
