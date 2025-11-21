import streamlit as st
import pandas as pd
from pathlib import Path
import os
import sys

# Add project root to path to import source modules
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.data.typed_models import (
    ItemSlot, Rarity, DamageType, TriggerEvent, 
    EffectType, ModType
)
from dashboard.utils import get_game_data_provider

def get_csv_path(filename):
    """Helper to get absolute path to data files."""
    return PROJECT_ROOT / "data" / filename

def save_dataframe(df, filename):
    """Saves dataframe to CSV and clears cache."""
    path = get_csv_path(filename)
    try:
        df.to_csv(path, index=False)
        st.success(f"✅ Saved {filename} successfully!")
        st.cache_resource.clear() # Force reload of engine data
        return True
    except Exception as e:
        st.error(f"❌ Failed to save: {e}")
        return False

# -----------------------------------------------------------------------------
# 1. ITEMS EDITOR
# -----------------------------------------------------------------------------
def render_items_editor():
    st.markdown("### 🛡️ Items Registry")
    st.caption("Define base item templates. These are the blueprints for generation.")
    
    path = get_csv_path("items.csv")
    if not path.exists():
        st.error(f"File not found: {path}")
        return

    df = pd.read_csv(path)
    
    # Get valid options from Enums
    slot_options = [s.value for s in ItemSlot]
    rarity_options = [r.value for r in Rarity]
    
    # Configure the editor
    with st.container(border=True):
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            height=500,
            column_config={
                "item_id": st.column_config.TextColumn(
                    "ID", help="Unique identifier (snake_case)", required=True, width="medium"
                ),
                "name": st.column_config.TextColumn(
                    "Display Name", required=True, width="medium"
                ),
                "slot": st.column_config.SelectboxColumn(
                    "Slot", options=slot_options, required=True, width="small"
                ),
                "rarity": st.column_config.SelectboxColumn(
                    "Rarity", options=rarity_options, required=True, width="small"
                ),
                "num_random_affixes": st.column_config.NumberColumn(
                    "RNG Slots", min_value=0, max_value=10, width="small"
                ),
                "affix_pools": st.column_config.TextColumn(
                    "Affix Pools", help="Pipe-separated list (e.g. weapon_pool|axe_pool)"
                ),
                "implicit_affixes": st.column_config.TextColumn(
                    "Implicits", help="Fixed affix IDs (e.g. crit_damage)"
                )
            }
        )

    if st.button("💾 Save Items", type="primary", use_container_width=True):
        save_dataframe(edited_df, "items.csv")

# -----------------------------------------------------------------------------
# 2. SKILLS EDITOR
# -----------------------------------------------------------------------------
def render_skills_editor():
    st.markdown("### ⚔️ Skills Registry")
    st.caption("Define active combat abilities.")
    
    path = get_csv_path("skills.csv")
    df = pd.read_csv(path)
    
    # Get options
    damage_types = [d.value for d in DamageType]
    triggers = [t.value for t in TriggerEvent]
    
    # Get valid Effect IDs for the trigger_result dropdown
    provider = get_game_data_provider()
    effect_ids = list(provider.get_effects().keys())
    
    with st.container(border=True):
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            height=500,
            column_config={
                "skill_id": st.column_config.TextColumn("ID", required=True),
                "damage_type": st.column_config.SelectboxColumn(
                    "Dmg Type", options=damage_types, required=True
                ),
                "trigger_event": st.column_config.SelectboxColumn(
                    "Trigger", options=triggers
                ),
                "trigger_result": st.column_config.SelectboxColumn(
                    "Effect Applied", options=effect_ids, help="Effect ID to apply on trigger"
                ),
                "proc_rate": st.column_config.NumberColumn(
                    "Proc %", min_value=0.0, max_value=1.0, format="%.2f"
                ),
                "resource_cost": st.column_config.NumberColumn("Cost", min_value=0),
                "cooldown": st.column_config.NumberColumn("CD (s)", min_value=0.0)
            }
        )

    if st.button("💾 Save Skills", type="primary", use_container_width=True):
        save_dataframe(edited_df, "skills.csv")

# -----------------------------------------------------------------------------
# 3. AFFIXES EDITOR
# -----------------------------------------------------------------------------
def render_affixes_editor():
    st.markdown("### 💎 Affixes Registry")
    st.caption("Item modifiers that roll dynamically.")
    
    path = get_csv_path("affixes.csv")
    df = pd.read_csv(path)
    
    mod_types = [m.value for m in ModType]
    triggers = [t.value for t in TriggerEvent]
    
    with st.container(border=True):
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            height=500,
            column_config={
                "affix_id": st.column_config.TextColumn("ID", required=True),
                "mod_type": st.column_config.SelectboxColumn(
                    "Type", options=mod_types, required=True
                ),
                "base_value": st.column_config.TextColumn(
                    "Value", help="Base number. Supports dual '0.5;0.3'"
                ),
                "stat_affected": st.column_config.TextColumn(
                    "Stat", help="Must match EntityStats field"
                ),
                "trigger_event": st.column_config.SelectboxColumn(
                    "Trigger", options=triggers
                ),
                "dual_stat": st.column_config.CheckboxColumn("Dual?", default=False),
                "scaling_power": st.column_config.CheckboxColumn("Scales?", default=False),
            }
        )

    if st.button("💾 Save Affixes", type="primary", use_container_width=True):
        save_dataframe(edited_df, "affixes.csv")

# -----------------------------------------------------------------------------
# 4. EFFECTS EDITOR
# -----------------------------------------------------------------------------
def render_effects_editor():
    st.markdown("### 🧪 Effects Registry")
    st.caption("Buffs, Debuffs, and DoTs.")
    
    path = get_csv_path("effects.csv")
    df = pd.read_csv(path)
    
    effect_types = [e.value for e in EffectType]
    
    with st.container(border=True):
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            height=500,
            column_config={
                "effect_id": st.column_config.TextColumn("ID", required=True),
                "type": st.column_config.SelectboxColumn(
                    "Type", options=effect_types, required=True
                ),
                "max_stacks": st.column_config.NumberColumn("Stacks", min_value=1),
                "duration": st.column_config.NumberColumn("Duration (s)", min_value=0.0),
                "tick_interval": st.column_config.NumberColumn("Tick (s)", min_value=0.0),
                "damage_per_tick": st.column_config.NumberColumn("Dmg/Tick"),
                "stat_multiplier": st.column_config.NumberColumn("Stat Mult"),
            }
        )

    if st.button("💾 Save Effects", type="primary", use_container_width=True):
        save_dataframe(edited_df, "effects.csv")