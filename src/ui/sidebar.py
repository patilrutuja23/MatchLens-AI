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
            ["📤 Upload Match", "⚡ Live Match", "Match Momentum", "VAR Decisions", "Match Story"],
            label_visibility="collapsed",
            index=0  # Default to Upload Match
        )
        
        st.markdown("---")
        
        # Settings section
        st.subheader("⚙️ Settings")
        
        # Match selection (only show if not on Upload or Live pages)
        if page not in ["📤 Upload Match", "⚡ Live Match"]:
            match_option = st.selectbox(
                "Select Match",
                ["Sample Match", "Uploaded Match"],
                key="selected_match"
            )
            
            # Show loaded match info if available
            if "match_loaded" in st.session_state and st.session_state.match_loaded:
                if "current_match" in st.session_state:
                    match_data = st.session_state.current_match
                    st.success(f"✅ Loaded: {match_data.get('home_team', 'Unknown')} vs {match_data.get('away_team', 'Unknown')}")
        
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
        **MatchLens AI** uses Hugging Face AI to provide:
        
        - 📤 Match file upload & validation
        - ⚡ Live match tracking
        - 📈 Match momentum analysis
        - 🎥 VAR decision explanations (RAG-enhanced)
        - 📝 AI-generated match stories
        
        Built with Hugging Face Models
        """)
        
        # Footer
        st.markdown("---")
        st.caption("Powered by Hugging Face AI")
        st.caption("© 2026 MatchLens AI")
    
    # Ensure we always return a string, defaulting to first option if None
    return page if page is not None else "📤 Upload Match"

# Made with Bob
