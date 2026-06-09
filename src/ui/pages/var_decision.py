"""
VAR Decision Explainer Page
"""

import streamlit as st
from src.features.var_explainer import VARExplainer
from src.utils.config import load_config

def render_var_page():
    """Render the VAR Decision Explainer page"""
    
    st.title("🎥 VAR Decision Explainer")
    st.markdown("Understand VAR decisions with AI-powered explanations and rule references")
    
    # Initialize explainer
    if 'var_explainer' not in st.session_state:
        st.session_state.var_explainer = VARExplainer()
    
    explainer = st.session_state.var_explainer
    
    # Get match data from session state or use sample
    match_data = _get_match_data()
    
    if match_data is None:
        st.warning("⚠️ No match data loaded!")
        st.info("Please upload a match file or start a live match first.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Go to Upload Match", use_container_width=True):
                st.session_state.page = "📤 Upload Match"
                st.rerun()
        with col2:
            if st.button("⚡ Go to Live Match", use_container_width=True):
                st.session_state.page = "⚡ Live Match"
                st.rerun()
        return
    
    # Display match info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Match", f"{match_data['home_team']} vs {match_data['away_team']}")
    with col2:
        # Handle both 'score' and 'final_score' keys
        score = match_data.get('final_score') or match_data.get('score', 'N/A')
        st.metric("Final Score", score)
    with col3:
        var_stats = explainer.get_var_statistics(match_data)
        st.metric("VAR Reviews", var_stats['total_var_reviews'])
    
    st.markdown("---")
    
    # VAR Decision Selector
    st.subheader("🔍 Select VAR Decision")
    
    var_events = [
        event for event in match_data.get('events', [])
        if event.get('type', '').lower() == 'var'
    ]
    
    if not var_events:
        st.info("No VAR decisions in this match. Try the sample decision below.")
        var_events = [_get_sample_var_decision()]
    
    # Create selection options
    var_options = [
        f"{event['time']}' - {event.get('decision_type', 'VAR')} - {event.get('description', 'Decision')}"
        for event in var_events
    ]
    
    selected_index = st.selectbox(
        "Choose a VAR decision to analyze",
        range(len(var_options)),
        format_func=lambda x: var_options[x]
    )
    
    # Handle potential None return from selectbox
    if selected_index is None:
        st.error("Please select a VAR decision to analyze")
        return
    
    selected_var = var_events[selected_index]
    
    # Display decision details
    st.subheader("📋 Decision Details")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Time:** {selected_var['time']}'")
        st.write(f"**Type:** {selected_var.get('decision_type', 'Unknown')}")
        st.write(f"**Initial Decision:** {selected_var.get('initial_decision', 'Unknown')}")
    with col2:
        st.write(f"**VAR Review:** {selected_var.get('var_review', 'Unknown')}")
        st.write(f"**Final Decision:** {selected_var.get('final_decision', 'Unknown')}")
        st.write(f"**Review Duration:** {selected_var.get('review_duration', 'Unknown')} seconds")
    
    st.markdown("---")
    
    # Analyze button
    if st.button("🤖 Explain Decision", type="primary"):
        with st.spinner("Analyzing VAR decision..."):
            # Prepare match context
            match_context = {
                "teams": f"{match_data['home_team']} vs {match_data['away_team']}",
                "score": match_data.get('final_score') or match_data.get('score', 'N/A'),
                "time": f"{selected_var['time']}'"
            }
            
            # Get explanation
            explanation = explainer.explain_var_decision(
                decision_type=selected_var.get('decision_type', 'VAR'),
                match_context=match_context,
                incident_details=selected_var
            )
            
            # Display results
            st.success("Analysis Complete!")
            
            # AI Explanation
            st.subheader("🤖 AI Explanation")
            st.markdown(explanation['explanation'])
            
            # Relevant Rules (handle both old and new formats)
            st.subheader("📖 Relevant VAR Rules")
            
            # Check for new RAG format
            if 'rules_used' in explanation:
                for i, rule in enumerate(explanation['rules_used'], 1):
                    st.info(f"**Rule {i}:** {rule}")
                
                # Show confidence score if available
                if 'confidence_score' in explanation:
                    st.metric("Confidence Score", f"{explanation['confidence_score']:.0%}")
                
                # Show retrieved evidence if available
                if 'retrieved_evidence' in explanation:
                    with st.expander("📚 Retrieved Evidence"):
                        for evidence in explanation['retrieved_evidence']:
                            st.write(f"**Source {evidence['rank']}:** {evidence['source']}")
                            st.write(f"Relevance: {evidence['relevance']:.0%}")
                            st.caption(evidence['text'][:200] + "...")
                            st.divider()
            
            # Fallback to old format
            elif 'relevant_rules' in explanation:
                for i, rule in enumerate(explanation['relevant_rules'], 1):
                    st.info(f"**Rule {i}:** {rule}")
            else:
                st.info("No specific rules retrieved for this decision")
            
            # Decision Factors
            st.subheader("⚖️ Decision Factors")
            factors = explanation['decision_factors']
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Clear & Obvious Error:** {'Yes' if factors['clear_and_obvious'] else 'No'}")
                st.write(f"**Multiple Angles Used:** {'Yes' if factors['multiple_angles_used'] else 'No'}")
            with col2:
                st.write(f"**Decision Type:** {factors['decision_type']}")
            
            if factors['key_considerations']:
                st.write("**Key Considerations:**")
                for consideration in factors['key_considerations']:
                    st.write(f"- {consideration}")
    
    # VAR Statistics
    st.markdown("---")
    st.subheader("📊 Match VAR Statistics")
    
    if st.button("Show VAR Statistics"):
        stats = explainer.get_var_statistics(match_data)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Reviews", stats['total_var_reviews'])
        with col2:
            st.metric("Overturned", stats['decisions_overturned'])
        with col3:
            st.metric("Upheld", stats['decisions_upheld'])
        with col4:
            st.metric("Avg Review Time", f"{stats['average_review_time']:.1f}s")
        
        if stats['by_type']:
            st.write("**Decisions by Type:**")
            for decision_type, count in stats['by_type'].items():
                st.write(f"- {decision_type.title()}: {count}")
    
    # Educational section
    st.markdown("---")
    st.subheader("📚 Learn About VAR")
    
    with st.expander("What is VAR?"):
        st.write("""
        **Video Assistant Referee (VAR)** is a technology system that helps match officials 
        make more accurate decisions by reviewing video footage of incidents.
        
        VAR can review:
        - Goals and offenses leading up to a goal
        - Penalty decisions
        - Direct red card incidents
        - Mistaken identity
        """)
    
    with st.expander("How does VAR work?"):
        st.write("""
        1. **Incident occurs** on the field
        2. **VAR team reviews** multiple camera angles
        3. **Communication** between VAR and on-field referee
        4. **On-field review** (if needed) at pitch-side monitor
        5. **Final decision** made by on-field referee
        
        The process typically takes 30-90 seconds.
        """)

def _get_match_data():
    """Get match data from session state or sample data based on sidebar selection"""
    import json
    
    # Check sidebar selection
    selected_match = st.session_state.get('selected_match', 'Sample Match')
    
    if selected_match == "Uploaded Match":
        # Check for uploaded match
        if 'current_match' in st.session_state and st.session_state.get('match_loaded'):
            return st.session_state.current_match
        
        # Check for live match
        if 'live_analyzer' in st.session_state:
            analyzer = st.session_state.live_analyzer
            if analyzer.match_started and analyzer.match_data:
                return analyzer.export_match_data()
        
        # No uploaded match found
        return None
    
    else:  # Sample Match
        # Load sample match data
        try:
            with open("data/matches/sample_match.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            st.error("Sample match file not found")
            return None

def _get_sample_match_data():
    """Get sample match data (fallback)"""
    return {
        "home_team": "Manchester City",
        "away_team": "Arsenal",
        "final_score": "2-2",
        "competition": "Premier League",
        "events": [
            {
                "time": 23,
                "type": "var",
                "decision_type": "penalty",
                "description": "Potential penalty for handball",
                "initial_decision": "No penalty",
                "var_review": "Checked for handball",
                "final_decision": "Penalty awarded",
                "review_duration": 45
            },
            {
                "time": 67,
                "type": "var",
                "decision_type": "offside",
                "description": "Goal check for offside",
                "initial_decision": "Goal",
                "var_review": "Offside check",
                "final_decision": "Goal disallowed",
                "review_duration": 60
            }
        ]
    }

def _get_sample_var_decision():
    """Get a sample VAR decision"""
    return {
        "time": 34,
        "type": "var",
        "decision_type": "red_card",
        "description": "Potential red card for dangerous tackle",
        "initial_decision": "Yellow card",
        "var_review": "Checked for serious foul play",
        "final_decision": "Red card",
        "review_duration": 75
    }

# Made with Bob
