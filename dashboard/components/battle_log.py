import streamlit as st

def render_battle_log(events):
    """
    Renders the battle log with styled events.
    
    Args:
        events (list): A list of event dictionaries/objects from the combat engine.
    """
    st.markdown("### 📜 Battle Log")
    
    with st.container(border=True, height=300):
        if not events:
            st.info("⚔️ No combat events yet. Start a fight!")
            return

        for i, event in enumerate(events):
            # Determine style based on event type
            e_type = event.get("type", "info")
            message = event.get("message", str(event))
            
            # Color coding with emoji icons (matching spec)
            if e_type == "damage":
                st.markdown(f"🔴 **DAMAGE** › {message}")
            elif e_type == "heal":
                st.markdown(f"🟢 **HEAL** › {message}")
            elif e_type == "block":
                st.markdown(f"🛡️ **BLOCK** › {message}")
            elif e_type == "crit":
                st.markdown(f"🟡 **CRITICAL HIT!** › {message}")
            elif e_type == "dodge":
                st.markdown(f"💨 **DODGE** › {message}")
            else:
                st.markdown(f"• {message}")
