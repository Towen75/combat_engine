import streamlit as st
import pandas as pd

def render_entity_card(key_prefix, items_df, skills_df):
    """
    Renders a card for configuring an entity (Attacker or Defender).
    
    Args:
        key_prefix (str): Unique prefix for streamlit widgets (e.g., "attacker", "defender").
        items_df (pd.DataFrame): DataFrame containing available items.
        skills_df (pd.DataFrame): DataFrame containing available skills.
        
    Returns:
        dict: A dictionary containing the configured entity stats and equipment.
    """
    # Card Header
    icon = "⚔️" if key_prefix == "attacker" else "🛡️"
    st.markdown(f"### {icon} {key_prefix.upper()}")
    
    with st.container(border=True):
        # Base Stats Section
        st.markdown("**⚡ Base Stats**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            health = st.number_input(
                "❤️ Health",
                min_value=1,
                max_value=9999,
                value=100,
                key=f"{key_prefix}_health",
                help="Maximum health points"
            )
        with col2:
            damage = st.number_input(
                "⚔️ Damage",
                min_value=0,
                max_value=999,
                value=10,
                key=f"{key_prefix}_damage",
                help="Base damage per hit"
            )
        with col3:
            speed = st.number_input(
                "⚡ Speed",
                min_value=0,
                max_value=100,
                value=10,
                key=f"{key_prefix}_speed",
                help="Action speed"
            )
            
        st.markdown("---")
        
        # Equipment Section
        st.markdown("**🗡️ Equipment Rack**")
        
        # Filter items by slot for better UX - handle case insensitivity
        if 'slot' in items_df.columns and len(items_df) > 0:
            # Create lowercase version for comparison
            items_df_copy = items_df.copy()
            items_df_copy['slot_lower'] = items_df_copy['slot'].str.lower()
            
            weapon_items = items_df_copy[items_df_copy['slot_lower'] == 'weapon']
            weapons = ["None"] + weapon_items['name'].tolist()
            
            chest_items = items_df_copy[items_df_copy['slot_lower'] == 'chest']
            armor = ["None"] + chest_items['name'].tolist()
        else:
            weapons = ["None"]
            armor = ["None"]
        
        col1, col2 = st.columns(2)
        with col1:
            main_hand = st.selectbox(
                "🗡️ Main Hand",
                weapons,
                key=f"{key_prefix}_main_hand",
                help="Primary weapon"
            )
        with col2:
            chest = st.selectbox(
                "🛡️ Chest",
                armor,
                key=f"{key_prefix}_chest",
                help="Chest armor"
            )
        
    return {
        "health": health,
        "damage": damage,
        "speed": speed,
        "equipment": {
            "main_hand": main_hand if main_hand != "None" else None,
            "chest": chest if chest != "None" else None
        }
    }
