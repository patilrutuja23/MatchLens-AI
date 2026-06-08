"""
Streamlit Sidebar Component
Navigation and settings for MatchLens AI
"""

import streamlit as st

def render_sidebar() -> str:
    """
    Render sidebar with navigation and settings
    
    Returns:
        Selected page name
    """
    with st.sidebar:
        # App header
        st.title("⚽ MatchLens AI")
        st.markdown("*Explainable AI for Football Fans*")
        st.markdown("---")
        
        # Navigation
        st.subheader("📊 Features")
        page = st.radio(
            "Select Feature",
            ["Match Momentum", "VAR Decisions", "Match Story"],
            label_visibility="collapsed",
            index=0  # Ensure a default selection
        )
        
        st.markdown("---")
        
        # Settings section
        st.subheader("⚙️ Settings")
        
        # Match selection
        st.selectbox(
            "Select Match",
            ["Sample Match", "Upload Custom Match"],
            key="selected_match"
        )
        
        # AI Settings
        with st.expander("AI Settings"):
            st.slider(
                "Response Detail Level",
                min_value=1,
                max_value=5,
                value=3,
                key="detail_level"
            )
            
            st.selectbox(
                "Explanation Style",
                ["Detailed", "Concise", "Technical"],
                key="explanation_style"
            )
        
        st.markdown("---")
        
        # Info section
        st.subheader("ℹ️ About")
        st.info("""
        **MatchLens AI** uses Hugging Face Granite AI to provide:
        
        - 📈 Match momentum analysis
        - 🎥 VAR decision explanations
        - 📝 AI-generated match stories
        
        Built with Hugging Face Granite Models
        """)
        
        # Footer
        st.markdown("---")
        st.caption("Powered by Hugging Face Granite AI")
        st.caption("© 2026 MatchLens AI")
    
    # Ensure we always return a string, defaulting to first option if None
    return page if page is not None else "Match Momentum"

# Made with Bob
