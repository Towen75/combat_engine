import streamlit as st
from utils import get_game_data_provider, load_css

# Page Config
st.set_page_config(
    page_title="Gladiator Engine Control Center",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load Custom Theme
load_css()

def main():
    # Sidebar Header with Icon
    st.sidebar.markdown("# ⚔️ GLADIATOR ENGINE")
    st.sidebar.markdown("---")
    
    # Engine Status
    st.sidebar.subheader("⚙️ Engine Status")
    try:
        provider = get_game_data_provider()
        stats = provider.get_data_stats()
        st.sidebar.success("✓ Engine Loaded")
        st.sidebar.caption(f"**Items:** {stats['items']} | **Skills:** {stats['skills']}")
        st.sidebar.caption(f"**Affixes:** {stats['affixes']} | **Effects:** {stats['effects']}")
    except Exception as e:
        st.sidebar.error(f"✗ Engine Error")
        st.sidebar.caption(str(e)[:50])
    
    st.sidebar.markdown("---")
    
    # Hot Reload Button
    st.sidebar.subheader("🔄 Data Management")
    if st.sidebar.button("🔥 Hot Reload CSVs", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Global Settings
    st.sidebar.subheader("⚙️ Global Settings")
    
    # Initialize session state for RNG seed if not exists
    if 'rng_seed' not in st.session_state:
        st.session_state.rng_seed = 42
        
    st.session_state.rng_seed = st.sidebar.number_input(
        "🎲 RNG Seed",
        min_value=0,
        value=st.session_state.rng_seed,
        help="Deterministic seed for reproducible combat"
    )
    
    log_level = st.sidebar.selectbox(
        "📝 Log Level",
        ["INFO", "DEBUG", "WARNING"],
        index=0,
        help="Logging verbosity level"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.caption("💀 *May the strongest warrior prevail* 💀")
    
    # Main Content
    st.title("⚔️ GLADIATOR ENGINE CONTROL CENTER")
    
    st.markdown("""
    Welcome to the **Arena**, where legends are forged and battles are won.
    
    ### Choose Your Workspace
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 🔨 THE FORGE
        **Content Editor**
        
        Create and modify Items, Skills, Affixes, and Effects with type-safe forms.
        """)
        
    with col2:
        st.markdown("""
        #### ⚔️ THE ARENA
        **Combat Debugger**
        
        Test 1-on-1 combat scenarios with detailed battle logs and state inspection.
        """)
        
    with col3:
        st.markdown("""
        #### 🏛️ THE COLISEUM
        **Batch Simulator**
        
        Run thousands of simulations and analyze balance with visual charts.
        """)

if __name__ == "__main__":
    main()
