"""
MatchLens AI - Main Application Entry Point
Built with Hugging Face Granite Models

This is the main Streamlit application that orchestrates all features:
- Match Momentum Explainer
- VAR Decision Explainer
- Match Story Generator
"""

import streamlit as st
from src.ui.sidebar import render_sidebar
from src.ui.pages.momentum import render_momentum_page
from src.ui.pages.var_decision import render_var_page
from src.ui.pages.story_generator import render_story_page
from src.utils.config import load_config

# Page configuration
st.set_page_config(
    page_title="MatchLens AI",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function"""
    
    # Load configuration
    config = load_config()
    
    # Render sidebar and get selected page
    selected_page = render_sidebar()
    
    # Render selected page
    if selected_page == "Match Momentum":
        render_momentum_page()
    elif selected_page == "VAR Decisions":
        render_var_page()
    elif selected_page == "Match Story":
        render_story_page()

if __name__ == "__main__":
    main()

# Made with Bob
