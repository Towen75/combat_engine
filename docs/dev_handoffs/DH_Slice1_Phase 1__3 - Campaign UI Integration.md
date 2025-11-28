# 🚀 Implementation Hand-off: Phase 1.3 - Campaign UI Integration

**Related Work Item:** Phase 1.3 - Campaign UI Integration

## 📦 File Manifest
| Action | File Path | Description |
| :--- | :--- | :--- |
| ✏️ Modify | `src/game/session.py` | Add `last_report` storage to expose combat details to UI |
| ✏️ Modify | `dashboard/utils.py` | Add `get_game_session` helper |
| 🆕 Create | `dashboard/pages/4_Campaign.py` | Main Campaign Logic & UI Layouts |

---

## 1️⃣ Configuration & Dependencies
*No new pip packages required.*

---

## 2️⃣ Code Changes

### A. `src/game/session.py`
**Path:** `src/game/session.py`
**Context:** Small update to store the simulation report so the UI can display what happened during combat.

```python
# ... inside GameSession class ...

    def __init__(self, provider: GameDataProvider):
        # ... existing init ...
        self.loot_stash: List[Item] = [] 
        
        # Last run analytics
        self.last_report: Dict[str, Any] = {} # <--- Changed from last_combat_log list to dict

    def execute_combat_turn(self) -> bool:
        # ... inside execute_combat_turn ...
        
        # 7. Run Simulation
        # ... existing setup ...
        
        # Run for max 60 seconds or until death
        runner.run_simulation(duration=60.0)
        
        # Store report for UI
        self.last_report = runner.get_simulation_report() # <--- NEW: Capture report
        
        # 8. Resolve Outcome
        # ... rest of function ...
```

### B. `dashboard/utils.py`
**Path:** `dashboard/utils.py`
**Context:** Add a helper to manage the Session singleton within Streamlit's state.

```python
# ... existing imports ...
from src.game.session import GameSession # Add import

# ... existing functions ...

def get_game_session():
    """
    Returns the persistent GameSession instance.
    Creates it if it doesn't exist.
    """
    if 'game_session' not in st.session_state:
        provider = get_game_data_provider()
        st.session_state.game_session = GameSession(provider)
    
    return st.session_state.game_session
```

### C. `dashboard/pages/4_Campaign.py`
**Path:** `dashboard/pages/4_Campaign.py`
**Context:** The main UI logic. Implements the State Machine view router (Lobby -> Prep -> Combat -> Loot).

```python
import streamlit as st
import time
from dashboard.utils import get_game_session, get_game_data_provider, load_css
from dashboard.components.item_card import render_item_card
from src.game.enums import GameState
from src.data.typed_models import ItemSlot

# Page Config
st.set_page_config(page_title="The Campaign", page_icon="🗺️", layout="wide")
load_css()

def main():
    st.title("🗺️ THE CAMPAIGN")
    
    session = get_game_session()
    provider = get_game_data_provider()

    # DEBUG: State Visualizer
    with st.expander("Debug State", expanded=False):
        st.write(f"State: {session.state}")
        st.write(f"Stage: {session.current_stage}")
        if session.player:
            st.write(f"HP: {session.player.final_stats.max_health}")

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
                        st.markdown(f"**{slot_name}:** {equipped_item.name} <span style='color:orange'>({equipped_item.rarity})</span>", unsafe_allow_html=True)
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

    # --- RIGHT: INVENTORY ---
    with col_inv:
        st.markdown(f"### 🎒 Backpack ({session.inventory.count}/{session.inventory.capacity})")
        
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
        success = session.execute_combat_turn()
        st.rerun()

def render_combat(session):
    st.subheader("⚔️ Combat Resolution")
    
    # In Phase 1.2, execute_combat_turn runs synchronously and changes state immediately.
    # If we are in COMBAT state here, it means we probably want to show results 
    # before moving to VICTORY/GAMEOVER.
    # However, the session likely already transitioned state inside `execute_combat_turn`.
    # This view might be skipped if we re-run immediately.
    # BUT, if we want an animation or "Processing..." view, this is it.
    
    # For Slice 1, we just show the results from the last report.
    
    report = session.last_report
    if not report:
        st.error("No combat report found.")
        if st.button("Back"):
            session.state = GameState.PREPARATION
            st.rerun()
        return

    # Basic Result Display
    perf = report.get('performance_analysis', {})
    dmg = report.get('damage_analysis', {}).get('summary', {})
    
    st.write(f"**Duration:** {perf.get('simulation_duration', 0):.2f}s")
    st.write(f"**Total Hits:** {dmg.get('total_hits', 0)}")
    
    # Transition
    if session.state == GameState.VICTORY:
        st.success("Victory!")
        if st.button("Claim Loot"):
            st.rerun() # Will render VICTORY view
            
    elif session.state == GameState.GAME_OVER:
        st.error("Defeat!")
        if st.button("View Aftermath"):
            st.rerun()

def render_victory(session):
    st.title("🏆 VICTORY")
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
    st.error(f"You fell at Stage {session.current_stage + 1}")
    
    if st.button("Return to Lobby"):
        session.state = GameState.LOBBY
        st.rerun()

if __name__ == "__main__":
    main()
```

---

## 🧪 Verification Steps

**1. Launch Dashboard**
```bash
streamlit run dashboard/app.py
```

**2. Playthrough Check**
1.  **Lobby:** Select a Hero. Set seed to `1`. Click Start.
2.  **Prep:** Equip the starter items (if any are in inventory).
3.  **Fight:** Click "Fight Next Enemy". Wait for result.
4.  **Victory:** If you win, click "Take" on loot. Check Backpack.
5.  **Prep:** See if you can equip the new loot.
6.  **Next:** Advance stage and verify enemy changes (logs or difficulty).

## ⚠️ Rollback Plan
If this crashes the app:
1.  Delete `dashboard/pages/4_Campaign.py`.
2.  Revert `src/game/session.py`.
3.  The main app will still work, just missing the new page.