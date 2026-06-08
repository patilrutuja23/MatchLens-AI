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
    
    # Load sample match data
    match_data = _get_sample_match_data()
    
    # Display match info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Match", f"{match_data['home_team']} vs {match_data['away_team']}")
    with col2:
        st.metric("Final Score", match_data['final_score'])
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
                "score": match_data['final_score'],
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
            
            # Relevant Rules
            st.subheader("📖 Relevant VAR Rules")
            for i, rule in enumerate(explanation['relevant_rules'], 1):
                st.info(f"**Rule {i}:** {rule}")
            
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

def _get_sample_match_data():
    """Get sample match data"""
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
