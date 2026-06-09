"""
Match Upload Page
Upload and validate match data files
"""

import streamlit as st
import json
from src.utils.match_uploader import MatchUploader


def render_upload_page():
    """Render the match upload page"""
    
    st.title("📤 Upload Match Data")
    st.markdown("Upload JSON or CSV match files for analysis")
    
    # Initialize uploader
    if 'match_uploader' not in st.session_state:
        st.session_state.match_uploader = MatchUploader()
    
    uploader = st.session_state.match_uploader
    
    # File uploader
    st.subheader("📁 Select File")
    
    uploaded_file = st.file_uploader(
        "Drop your match file here or click to browse",
        type=["json", "csv"],
        help="Supported formats: JSON, CSV (max 10MB)",
        key="match_file_uploader"
    )
    
    if uploaded_file is not None:
        # Show file info
        st.info(f"📄 **File:** {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
        
        # Process upload button
        if st.button("🔍 Validate & Load", type="primary", use_container_width=True):
            with st.spinner("Processing file..."):
                # Read file content
                file_content = uploaded_file.read()
                
                # Process upload
                success, match_data, errors, warnings = uploader.process_upload(
                    file_content,
                    uploaded_file.name
                )
                
                # Display errors
                if errors:
                    st.error("❌ **Validation Errors:**")
                    for error in errors:
                        st.error(f"• {error}")
                
                # Display warnings
                if warnings:
                    st.warning("⚠️ **Warnings:**")
                    for warning in warnings:
                        st.warning(f"• {warning}")
                
                # Show preview if valid
                if success and match_data:
                    st.success("✅ **File validated successfully!**")
                    
                    # Get preview
                    preview = uploader.get_match_preview(match_data)
                    
                    # Display preview
                    st.subheader("👀 Match Preview")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Match", preview["teams"])
                    with col2:
                        score = preview.get("score", preview.get("calculated_score", "N/A"))
                        st.metric("Score", score)
                    with col3:
                        st.metric("Total Events", preview["total_events"])
                    
                    # Additional info
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Date:** {preview.get('date', 'N/A')}")
                        st.write(f"**Competition:** {preview.get('competition', 'N/A')}")
                    with col2:
                        cards = preview.get("cards", {})
                        st.write(f"**Yellow Cards:** {cards.get('yellow', 0)}")
                        st.write(f"**Red Cards:** {cards.get('red', 0)}")
                        st.write(f"**VAR Reviews:** {preview.get('var_reviews', 0)}")
                    
                    # Event summary
                    if preview.get("event_summary"):
                        st.subheader("📊 Event Summary")
                        
                        event_summary = preview["event_summary"]
                        cols = st.columns(min(len(event_summary), 4))
                        
                        for i, (event_type, count) in enumerate(event_summary.items()):
                            col_idx = i % len(cols)
                            with cols[col_idx]:
                                st.metric(
                                    event_type.replace("_", " ").title(),
                                    count
                                )
                    
                    # Show raw data in expander
                    with st.expander("🔍 View Raw Data"):
                        st.json(match_data)
                    
                    # Load match button
                    st.divider()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ Load Match for Analysis", type="primary", use_container_width=True):
                            st.session_state.current_match = match_data
                            st.session_state.match_loaded = True
                            # Automatically switch to "Uploaded Match" in sidebar
                            st.session_state.selected_match = "Uploaded Match"
                            st.success("✅ Match loaded! Navigate to analysis pages to explore.")
                            st.balloons()
                    
                    with col2:
                        # Download processed JSON
                        json_str = json.dumps(match_data, indent=2)
                        st.download_button(
                            label="💾 Download as JSON",
                            data=json_str,
                            file_name=f"processed_{uploaded_file.name.replace('.csv', '.json')}",
                            mime="application/json",
                            use_container_width=True
                        )
    
    # Divider
    st.divider()
    
    # Previously uploaded matches
    st.subheader("📚 Previously Uploaded Matches")
    
    uploaded_matches = uploader.list_uploaded_matches()
    
    if uploaded_matches:
        for match in uploaded_matches[:10]:  # Show last 10
            with st.expander(f"📄 {match['teams']} - {match['date']}"):
                st.write(f"**File:** {match['filename']}")
                st.write(f"**Uploaded:** {match['upload_time']}")
                
                if st.button(f"Load {match['filename']}", key=f"load_{match['filename']}"):
                    match_data = uploader.load_match_file(match['path'])
                    if match_data:
                        st.session_state.current_match = match_data
                        st.session_state.match_loaded = True
                        st.success(f"✅ Loaded {match['teams']}")
                        st.rerun()
    else:
        st.info("No previously uploaded matches found")
    
    # Divider
    st.divider()
    
    # Sample files section
    st.subheader("📝 Sample Files")
    st.markdown("Download sample files to see the expected format:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**JSON Format:**")
        try:
            with open("data/matches/sample_match.json", "r") as f:
                sample_json = f.read()
            st.download_button(
                label="📥 Download sample_match.json",
                data=sample_json,
                file_name="sample_match.json",
                mime="application/json",
                use_container_width=True
            )
        except FileNotFoundError:
            st.caption("Sample JSON file not found")
    
    with col2:
        st.markdown("**CSV Format:**")
        try:
            with open("data/matches/sample_match.csv", "r") as f:
                sample_csv = f.read()
            st.download_button(
                label="📥 Download sample_match.csv",
                data=sample_csv,
                file_name="sample_match.csv",
                mime="text/csv",
                use_container_width=True
            )
        except FileNotFoundError:
            st.caption("Sample CSV file not found")
    
    # Format guide
    st.divider()
    
    with st.expander("📖 File Format Guide"):
        st.markdown("""
        ### Required Fields
        
        **Match Information:**
        - `home_team` (string): Home team name
        - `away_team` (string): Away team name
        - `events` (array): List of match events
        
        **Event Fields:**
        - `type` (string): Event type (goal, yellow_card, red_card, substitution, corner, penalty, var_review, etc.)
        - `time` (string): Event time (e.g., "45", "45+2", "45:30")
        - `team` (string): Team involved
        
        **Optional Fields:**
        - `score`, `date`, `competition`, `venue`, `referee`
        - Event-specific fields: `player`, `assist`, `reason`, `player_out`, `player_in`, etc.
        
        ### Valid Event Types
        - goal, yellow_card, red_card, substitution
        - corner, penalty, var_review
        - kickoff, halftime, fulltime
        
        ### Example JSON Structure
        ```json
        {
          "home_team": "Team A",
          "away_team": "Team B",
          "score": "2-1",
          "events": [
            {
              "type": "goal",
              "time": "23",
              "team": "Team A",
              "player": "Player Name",
              "description": "Great goal!"
            }
          ]
        }
        ```
        
        ### Example CSV Structure
        ```csv
        home_team,away_team,score,type,time,team,player,description
        Team A,Team B,2-1,goal,23,Team A,Player Name,Great goal!
        ```
        """)


if __name__ == "__main__":
    render_upload_page()

# Made with Bob