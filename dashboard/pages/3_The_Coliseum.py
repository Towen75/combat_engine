import streamlit as st
import pandas as pd
import altair as alt
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.simulation.batch_runner import SimulationBatchRunner
from src.core.models import Entity, EntityStats
from src.core.state import StateManager
from dashboard.utils import get_game_data_provider, load_css

# Apply black and gold styling
load_css()

def render_coliseum():
    st.title("🏛️ THE COLISEUM")
    st.caption("Batch Simulation & Balance Analytics")
    
    # 1. Setup Configuration
    with st.expander("⚙️ Simulation Config", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            iterations = st.slider("Iterations", min_value=10, max_value=1000, value=100, step=10)
        with col2:
            matchup = st.selectbox("Matchup Preset", ["Warrior vs Tank", "Rogue vs Mage"])
            
        run_btn = st.button("🔴 Run Simulation", type="primary", use_container_width=True)
        
    if run_btn:
        with st.spinner(f"Simulating {iterations} battles..."):
            # 2. Run Real Batch
            results_df = run_real_batch(matchup, iterations)
            
        # 3. Render Results
        render_results(results_df)

def run_real_batch(matchup_type, iterations):
    # define templates based on selection
    if matchup_type == "Warrior vs Tank":
        attacker = Entity("warrior", EntityStats(base_damage=25, max_health=150, attack_speed=1.0), "Warrior")
        defender = Entity("tank", EntityStats(base_damage=10, max_health=300, armor=20), "Tank")
    else:
        attacker = Entity("rogue", EntityStats(base_damage=40, max_health=80, attack_speed=1.5, crit_chance=0.3), "Rogue")
        defender = Entity("mage", EntityStats(base_damage=60, max_health=70, armor=0), "Mage")
    
    # Initialize Runner
    runner = SimulationBatchRunner(batch_id="dashboard_run")
    seed = st.session_state.get("rng_seed", 42)
    
    # Execute
    results = runner.run_batch(attacker, defender, iterations, seed)
    
    # Convert to DataFrame ensuring 'dps' exists
    data = {
        "winner": results.winners,
        "duration": results.durations,
        "remaining_hp": results.remaining_hps,
        "dps": results.dps  # This now exists in BatchResult
    }
    
    return pd.DataFrame(data)

def render_results(df):
    st.divider()
    
    # Summary Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        win_rate = (df['winner'] == df['winner'].mode()[0]).mean()
        st.metric("Dominant Winner", df['winner'].mode()[0], f"{win_rate:.1%}")
    with col2:
        st.metric("Avg Duration", f"{df['duration'].mean():.1f}s")
    with col3:
        st.metric("Avg DPS", f"{df['dps'].mean():.1f}")

    # Charts
    col_charts_1, col_charts_2 = st.columns(2)
    
    with col_charts_1:
        st.markdown("#### Win Distribution")
        win_counts = df['winner'].value_counts().reset_index()
        win_counts.columns = ['winner', 'count']
        
        pie = alt.Chart(win_counts).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="count", type="quantitative"),
            color=alt.Color(field="winner", type="nominal"),
            tooltip=["winner", "count"]
        )
        st.altair_chart(pie, use_container_width=True)
        
    with col_charts_2:
        st.markdown("#### DPS Variance")
        # Box plot requires numeric 'dps' column
        box = alt.Chart(df).mark_boxplot().encode(
            y=alt.Y("dps", title="Damage Per Second"),
            color=alt.value("#d4af37")
        )
        st.altair_chart(box, use_container_width=True)

if __name__ == "__main__":
    render_coliseum()