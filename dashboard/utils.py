import sys
import os
from pathlib import Path
import pandas as pd
import streamlit as st

# Add the project root to sys.path so we can import src
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.data.game_data_provider import GameDataProvider

@st.cache_resource
def get_game_data_provider():
    """
    Returns a singleton instance of GameDataProvider.
    Cached by Streamlit so we don't reload CSVs on every interaction.
    """
    provider = GameDataProvider()
    return provider

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
