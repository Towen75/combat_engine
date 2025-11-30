import sys
import os
from pathlib import Path
from typing import Optional
import pandas as pd
import streamlit as st

# Add the project root to sys.path so we can import src
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.data.game_data_provider import GameDataProvider
from src.game.session import GameSession

@st.cache_resource
def get_game_data_provider():
    """
    Creates cached GameDataProvider for dashboard session.

    Returns:
        GameDataProvider instance or None if loading fails
    """
    try:
        return GameDataProvider()
    except Exception as e:
        st.error(f"Failed to load game data: {e}")
        return None

def get_game_session():
    """
    Returns the persistent GameSession instance.
    Creates it if it doesn't exist.
    """
    if 'game_session' not in st.session_state:
        provider = get_game_data_provider()
        if provider is None:
            st.error("Failed to initialize game data provider")
            return None
        st.session_state.game_session = GameSession(provider)

    return st.session_state.game_session

def load_css():
    """
    Injects custom CSS for the 'Gilded Obsidian' theme.
    """
    st.markdown("""
        <style>
        /* Import Professional Font */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&family=Cinzel:wght@400;700&display=swap');
        
        /* Main Background */
        .stApp {
            background: linear-gradient(135deg, #1a1a1f 0%, #252530 100%);
            color: #e8e8e8;
            font-family: 'Roboto', sans-serif;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #15151a 0%, #0d0d10 100%);
            border-right: 2px solid #d4af37;
            box-shadow: 4px 0 12px rgba(212, 175, 55, 0.15);
        }
        
        [data-testid="stSidebar"] h1 {
            font-family: 'Cinzel', serif;
            font-size: 1.8rem;
            color: #d4af37;
            text-align: center;
            margin-bottom: 1.5rem;
            text-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
        }
        
        /* Headers */
        h1 {
            font-family: 'Cinzel', serif;
            color: #d4af37 !important;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-size: 2.5rem !important;
            border-bottom: 2px solid #d4af37;
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }
        
        h2 {
            font-family: 'Cinzel', serif;
            color: #f0d98d !important;
            font-size: 1.8rem !important;
            margin-top: 1.5rem;
        }
        
        h3 {
            font-family: 'Roboto', sans-serif;
            color: #c9aa71 !important;
            font-size: 1.3rem !important;
            font-weight: 700;
        }
        
        /* Plain Text - Make it gold/visible but be very specific to avoid layout issues */
        .stMarkdown p:not([style*="color"]),
        .stMarkdown span:not([style*="color"]) {
            color: #e8d4a0;
        }
        
        /* Captions */
        .caption, [data-testid="stCaptionContainer"], .stCaptionContainer {
            color: #c9aa71 !important;
        }
        
        /* Markdown text - but not if it has inline styles */
        .stMarkdown:not([style*="color"]) {
            color: #e8d4a0;
        }
        
        /* Labels for inputs */
        label:not([style*="color"]) {
            color: #d4af37 !important;
            font-weight: 600;
        }
        
        /* Selectbox/Dropdown text - make it white for visibility */
        .stSelectbox > div > div > div,
        .stSelectbox label,
        .stSelectbox [data-baseweb="select"] > div {
            color: #ffffff !important;
        }
        
        /* Selectbox background and border */
        .stSelectbox [data-baseweb="select"] {
            background-color: #2c2c35 !important;
            border-color: #4a4a55 !important;
        }
        
        /* Dropdown options */
        [data-baseweb="menu"] li {
            color: #1a1a1f !important;
        }
        
        /* Table text */
        table:not([style*="color"]) {
            color: #e8d4a0;
        }
        
        /* Data editor text */
        [data-testid="stDataFrame"] {
            color: #e8d4a0;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #2c2c35 0%, #1a1a20 100%);
            color: #d4af37;
            border: 2px solid #d4af37;
            border-radius: 8px;
            font-weight: 700;
            font-size: 1rem;
            padding: 0.6rem 1.5rem;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #d4af37 0%, #b8941f 100%);
            color: #1e1e24;
            border-color: #f0d98d;
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(212, 175, 55, 0.4);
        }
        
        /* Primary Button */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #d4af37 0%, #b8941f 100%);
            color: #1a1a1f !important;
            border-color: #f0d98d;
        }
        
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #f0d98d 0%, #d4af37 100%);
            color: #1a1a1f !important;
            box-shadow: 0 8px 16px rgba(212, 175, 55, 0.6);
        }
        
        /* Ensure button text is always readable */
        .stButton > button * {
            color: inherit !important;
        }
        
        /* Input Fields */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div {
            background-color: #2c2c35;
            color: #e8e8e8;
            border: 1px solid #4a4a55;
            border-radius: 6px;
            padding: 0.5rem;
        }
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus {
            border-color: #d4af37;
            box-shadow: 0 0 8px rgba(212, 175, 55, 0.3);
        }
        
        /* Radio Buttons */
        .stRadio > label {
            color: #d4af37 !important;
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .stRadio > div {
            background-color: #2c2c35;
            padding: 0.8rem;
            border-radius: 8px;
            border: 1px solid #4a4a55;
        }
        
        /* Radio button option labels - CRITICAL for visibility */
        .stRadio label span,
        .stRadio [role="radiogroup"] label,
        .stRadio [role="radiogroup"] div,
        [data-baseweb="radio"] label,
        [data-baseweb="radio"] > div {
            color: #ffffff !important;
        }
        
        /* Selectbox selected value text */
        .stSelectbox [data-baseweb="select"] input,
        .stSelectbox [data-baseweb="select"] > div > div,
        .stSelectbox [data-baseweb="select"] span,
        [data-baseweb="select"] input,
        [data-baseweb="select"] span {
            color: #ffffff !important;
        }
        
        /* Dataframe/Tables */
        [data-testid="stDataFrame"] {
            border: 2px solid #4a4a55;
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Divider */
        hr {
            border-color: #d4af37 !important;
            opacity: 0.3;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: #2c2c35;
            color: #d4af37;
            border: 1px solid #4a4a55;
            border-radius: 6px;
            font-weight: 600;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            color: #d4af37;
            font-size: 2rem;
            font-weight: 700;
        }
        
        /* Success/Error Messages */
        .stSuccess {
            background-color: rgba(76, 175, 80, 0.1);
            border-left: 4px solid #4CAF50;
            color: #81C784;
        }
        
        .stError {
            background-color: rgba(244, 67, 54, 0.1);
            border-left: 4px solid #F44336;
            color: #E57373;
        }
        
        .stInfo {
            background-color: rgba(33, 150, 243, 0.1);
            border-left: 4px solid #2196F3;
            color: #64B5F6;
        }
        
        .stWarning {
            background-color: rgba(255, 152, 0, 0.1);
            border-left: 4px solid #FF9800;
            color: #FFB74D;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #2c2c35;
            padding: 0.5rem;
            border-radius: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #c9aa71;
            border-radius: 6px;
            padding: 0.5rem 1rem;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #d4af37;
            color: #1a1a1f;
        }
        </style>
    """, unsafe_allow_html=True)


# ========== Portrait Loading Utilities ==========

@st.cache_data
def load_portrait_image(portrait_path: str) -> Optional[bytes]:
    """
    Load PNG portrait image from assets directory.

    Args:
        portrait_path: Relative path to portrait file (e.g., 'assets/portraits/hero.png')

    Returns:
        Image bytes if file exists and is valid PNG, None otherwise
    """
    if not portrait_path or portrait_path.strip() == "":
        return None

    try:
        # Convert relative path to absolute path from project root
        full_path = PROJECT_ROOT / portrait_path

        # Validate file exists
        if not full_path.exists():
            st.warning(f"Portrait file not found: {full_path}")
            return None

        # Validate it's a PNG file
        if full_path.suffix.lower() != '.png':
            st.warning(f"Portrait file is not PNG: {full_path}")
            return None

        # Read and validate image data
        with open(full_path, 'rb') as f:
            image_bytes = f.read()

        # Basic validation - check PNG header
        if not image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            st.warning(f"Invalid PNG file: {full_path}")
            return None

        return image_bytes

    except Exception as e:
        st.error(f"Error loading portrait {portrait_path}: {e}")
        return None


def display_portrait(portrait_path: str, width: int = 128) -> None:
    """
    Display portrait image in Streamlit with fixed width for layout stability.

    Args:
        portrait_path: Relative path to portrait file
        width: Fixed width in pixels (default 128 for consistent layout)
    """
    image_bytes = load_portrait_image(portrait_path)

    if image_bytes is not None:
        # Use fixed width to prevent layout shift
        st.image(image_bytes, width=width, caption=None, use_column_width=False)
    else:
        # Fallback display for missing portraits
        st.image(
            "https://via.placeholder.com/128x128/4a4a55/ffffff?text=No+Portrait",
            width=width,
            caption="Portrait not available",
            use_column_width=False
        )


def get_portrait_cache_key(entity_id: str) -> str:
    """
    Generate cache key for portrait images.

    Args:
        entity_id: Entity identifier

    Returns:
        Cache key string
    """
    return f"portrait_{entity_id}"

# ========== UI Intelligence Utilities ==========

import time
import streamlit as st
from typing import Dict, Any, List

def generate_equipment_quickview(player, provider) -> Dict[str, Any]:
    """Generate intelligent equipment summary for collapsed header."""

    weapon = player.equipment.get("Weapon")
    if weapon:
        weapon_template = provider.items.get(weapon.base_id)
        skill_id = getattr(weapon_template, 'default_attack_skill', None)

        if skill_id:
            skill = provider.skills.get(skill_id)
            weapon_info = {
                'name': weapon.name,
                'skill_name': skill.name if skill else 'Basic Attack',
                'damage_type': skill.damage_type if skill else 'Physical',
                'hits': skill.hits if skill else 1,
                'effects': []
            }

            # Extract weapon effects
            if hasattr(skill, 'trigger_result') and skill.trigger_result:
                weapon_info['effects'].append(skill.trigger_result)

            return weapon_info

    return {'name': 'Unarmed', 'skill_name': 'Strike', 'damage_type': 'Physical', 'hits': 1, 'effects': []}

def generate_backpack_quickview(inventory, provider) -> Dict[str, Any]:
    """Generate intelligent backpack summary for collapsed header."""

    items = inventory.items
    if not items:
        return {'status': 'empty', 'highlights': []}

    # Analyze item quality distribution
    quality_counts = {}
    highlights = []

    for item in items:
        quality = item.quality_tier
        quality_counts[quality] = quality_counts.get(quality, 0) + 1

        # Find notable items
        if hasattr(item, 'rarity') and item.rarity in ['rare', 'epic', 'legendary']:
            highlights.append(f"{item.name} ({item.rarity})")

    return {
        'status': f"{len(items)}/{inventory.capacity} items",
        'quality_dist': quality_counts,
        'highlights': highlights[:3]  # Top 3 notable items
    }

def create_smooth_transition(from_state: str, to_state: str, session):
    """Create smooth UI transitions between game states."""

    transition_config = {
        ('preparation', 'combat'): {
            'message': "⚔️ Entering Combat...",
            'preview_func': lambda: generate_weapon_preview(session.player),
            'duration': 2.0
        },
        ('combat', 'victory'): {
            'message': "🎉 Victory Achieved!",
            'celebration': True,
            'duration': 3.0
        },
        ('combat', 'game_over'): {
            'message': "💀 Combat Ended...",
            'reflection': True,
            'duration': 2.0
        }
    }

    config = transition_config.get((from_state, to_state))
    if config:
        with st.empty():
            progress_bar = st.progress(0)
            status_text = st.empty()

            steps = 100
            for i in range(steps + 1):
                progress_bar.progress(i)

                if i < 30:
                    status_text.markdown(f"## {config['message']}")
                elif i < 70 and 'preview_func' in config:
                    preview = config['preview_func']()
                    status_text.markdown(f"## {config['message']}\n{preview}")
                else:
                    status_text.markdown("## Loading results...")

                time.sleep(config['duration'] / steps)

            progress_bar.empty()
            status_text.empty()

def generate_weapon_preview(player) -> str:
    """Generate weapon preview for combat transition."""
    weapon = player.equipment.get("Weapon")
    if weapon:
        return f"**Weapon:** {weapon.name}\n*Prepare for battle!* ⚔️"
    return "*Unarmed combat initiated!* 👊"

def analyze_weapon_performance(current_fight, previous_fights) -> List[str]:
    """Analyze weapon performance across fights for comparison insights."""

    if not previous_fights:
        return ["First fight - establishing weapon baseline!"]

    insights = []

    # Extract basic metrics from simulation reports
    def get_player_hits(report):
        return report.get('damage_breakdown', {}).get('hero_player', {}).get('hits', 0)

    current_hits = get_player_hits(current_fight)
    avg_prev_hits = sum(get_player_hits(fight) for fight in previous_fights) / len(previous_fights)

    # Hit count analysis
    if current_hits > avg_prev_hits * 1.5:
        insights.append("🎯 **High hit count!** Your current weapon excels at multi-strikes.")
    elif current_hits < avg_prev_hits * 0.7:
        insights.append("🎯 **Lower hit count.** Consider weapons with higher attack speed.")

    # Placeholder for more advanced analysis
    insights.append("📊 Weapon performance analysis is being enhanced...")

    return insights if insights else ["Weapon performance is consistent with previous fights."]
