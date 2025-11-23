import streamlit as st
import pandas as pd
from pathlib import Path
import os
from utils import get_game_data_provider, load_css
from components.forge_editors import render_skills_editor, render_affixes_editor, render_effects_editor
from components.item_card import render_item_card  # Import the new component

# Apply black and gold styling
load_css()

def render_forge():
    st.title("🔨 THE FORGE")
    st.caption("Game Data Management")
    
    provider = get_game_data_provider()
    
    # Data Type Selector
    st.markdown("## 📚 Select Data Type")
    
    data_type = st.radio(
        "Choose what you want to edit:",
        ["Items", "Skills", "Affixes", "Effects"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    if data_type == "Items":
        render_items_editor(provider)
    elif data_type == "Skills":
        render_skills_editor()
    elif data_type == "Affixes":
        render_affixes_editor()
    elif data_type == "Effects":
        render_effects_editor()

def render_items_editor(provider):
    # Layout: Editor on Left (2/3), Preview on Right (1/3)
    col_editor, col_preview = st.columns([2, 1], gap="medium")
    
    data_dir = Path(os.path.dirname(__file__)).parent.parent / "data"
    items_path = data_dir / "items.csv"
    
    try:
        if items_path.exists():
            df = pd.read_csv(items_path)
        else:
            st.warning("⚠️ items.csv not found. Creating new DataFrame.")
            df = pd.DataFrame(columns=["item_id", "name", "slot", "rarity", "implicit_affixes", "affix_pools", "num_random_affixes"])
            
        with col_editor:
            st.markdown("### ⚔️ Item Registry")
            st.caption("Select a row to preview the item card.")
            
            # Use session state to track selection if needed, 
            # but st.data_editor return value captures changes.
            # To implement "Click row to preview", we need Streamlit 1.35+ selection_mode
            # or we can add a selector box.
            
            # Let's add a selector for the preview to be explicit and stable
            item_ids = df["item_id"].tolist() if "item_id" in df.columns else []
            
            # Editor
            with st.container(border=True):
                edited_df = st.data_editor(
                    df,
                    num_rows="dynamic",
                    column_config={
                        "item_id": st.column_config.TextColumn("ID", required=True),
                        "name": st.column_config.TextColumn("Name", required=True),
                        "slot": st.column_config.SelectboxColumn(
                            "Slot",
                            options=["weapon", "chest", "head", "legs", "feet", "hands", "ring", "amulet", "offhand"],
                            required=True
                        ),
                        "rarity": st.column_config.SelectboxColumn(
                            "Rarity",
                            options=["common", "uncommon", "rare", "epic", "legendary", "mythic"],
                            required=True
                        ),
                        "num_random_affixes": st.column_config.NumberColumn(
                            "RNG Slots", min_value=0, max_value=10
                        ),
                         "implicit_affixes": st.column_config.TextColumn(
                            "Implicits", help="IDs separated by |"
                        )
                    },
                    use_container_width=True,
                    height=500,
                    key="item_editor_grid"
                )
            
            # Save Actions
            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                if st.button("💾 Save", type="primary", use_container_width=True):
                    edited_df.to_csv(items_path, index=False)
                    st.success("Saved!")
                    st.cache_resource.clear()
            
            with c2:
                 if st.button("🔄 Reload", use_container_width=True):
                    st.rerun()

        # Preview Column
        with col_preview:
            st.markdown("### 👁️ Preview")
            
            # Initialize reroll state
            if "forge_reroll_count" not in st.session_state:
                st.session_state.forge_reroll_count = 0
            
            # Item Selector
            if not item_ids:
                st.info("No items to preview.")
            else:
                col_sel, col_btn = st.columns([2, 1])
                with col_sel:
                    preview_id = st.selectbox("Select Item", item_ids, label_visibility="collapsed")
                with col_btn:
                    if st.button("🎲 Re-roll", use_container_width=True, help="Roll new quality and affixes"):
                        st.session_state.forge_reroll_count += 1
                
                if preview_id:
                    # Find the item data in the EDITED dataframe so we see changes live!
                    selected_rows = edited_df[edited_df["item_id"] == preview_id]
                    
                    if not selected_rows.empty:
                        item_data = selected_rows.iloc[0].to_dict()
                        # Pass the reroll counter as seed
                        render_item_card(item_data, provider, seed=st.session_state.forge_reroll_count)
                    else:
                        st.warning("Item data not found.")

    except Exception as e:
        st.error(f"❌ Error in item editor: {e}")

if __name__ == "__main__":
    render_forge()