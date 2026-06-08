"""
Match Momentum Explainer Page
"""

import streamlit as st
import plotly.graph_objects as go
from src.features.momentum_explainer import MomentumExplainer
from src.utils.config import load_config

def render_momentum_page():
    """Render the Match Momentum Explainer page"""
    
    st.title("📈 Match Momentum Explainer")
    st.markdown("Understand how momentum shifted throughout the match using AI analysis")
    
    # Initialize explainer
    if 'momentum_explainer' not in st.session_state:
        st.session_state.momentum_explainer = MomentumExplainer()
    
    explainer = st.session_state.momentum_explainer
    
    # Load sample match data (in production, this would come from user selection)
    match_data = _get_sample_match_data()
    
    # Display match info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Match", f"{match_data['home_team']} vs {match_data['away_team']}")
    with col2:
        st.metric("Final Score", match_data['final_score'])
    with col3:
        st.metric("Competition", match_data['competition'])
    
    st.markdown("---")
    
    # Time period selector
    st.subheader("🕐 Select Time Period")
    
    col1, col2 = st.columns(2)
    with col1:
        start_time = st.slider("Start Time (minutes)", 0, 90, 0)
    with col2:
        end_time = st.slider("End Time (minutes)", 0, 90, 45)
    
    if start_time >= end_time:
        st.warning("End time must be greater than start time")
        return
    
    # Filter events for selected period
    time_period = f"{start_time}-{end_time} minutes"
    events = [
        event for event in match_data.get('events', [])
        if start_time <= event.get('time', 0) < end_time
    ]
    
    if st.button("🔍 Analyze Momentum", type="primary"):
        if not events:
            st.warning("No events found in this time period")
            return
        
        with st.spinner("Analyzing momentum shift..."):
            # Analyze momentum
            analysis = explainer.analyze_momentum_shift(
                match_data,
                time_period,
                events
            )
            
            # Display results
            st.success("Analysis Complete!")
            
            # Momentum metrics
            st.subheader("📊 Momentum Metrics")
            metrics = analysis['metrics']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Events", metrics['total_events'])
            with col2:
                st.metric("Attacking Events", metrics['attacking_events'])
            with col3:
                st.metric("Defensive Events", metrics['defensive_events'])
            with col4:
                momentum_score = metrics['momentum_score']
                st.metric(
                    "Momentum Score",
                    momentum_score,
                    delta=f"{'Attacking' if momentum_score > 0 else 'Defensive'}"
                )
            
            # Momentum visualization
            st.subheader("📈 Momentum Visualization")
            fig = _create_momentum_chart(metrics)
            st.plotly_chart(fig, use_container_width=True)
            
            # AI Explanation
            st.subheader("🤖 AI Explanation")
            st.markdown(analysis['explanation'])
            
            # Key Events
            if analysis['key_events']:
                st.subheader("⚡ Key Events")
                for event in analysis['key_events']:
                    with st.expander(f"{event['time']}' - {event['type']}"):
                        st.write(f"**Team:** {event.get('team', 'Unknown')}")
                        st.write(f"**Description:** {event.get('description', 'No description')}")
    
    # Full match timeline
    st.markdown("---")
    st.subheader("📅 Full Match Timeline")
    
    if st.button("Generate Full Timeline"):
        with st.spinner("Generating match timeline..."):
            timeline = explainer.get_momentum_timeline(match_data, interval_minutes=15)
            
            for period_analysis in timeline:
                with st.expander(f"⏱️ {period_analysis['time_period']}"):
                    metrics = period_analysis['metrics']
                    st.write(f"**Momentum Score:** {metrics['momentum_score']}")
                    st.write(f"**Total Events:** {metrics['total_events']}")
                    
                    if period_analysis['key_events']:
                        st.write("**Key Events:**")
                        for event in period_analysis['key_events'][:3]:
                            st.write(f"- {event['time']}': {event['type']}")

def _get_sample_match_data():
    """Get sample match data (placeholder)"""
    return {
        "home_team": "Manchester United",
        "away_team": "Liverpool",
        "final_score": "2-1",
        "halftime_score": "1-0",
        "competition": "Premier League",
        "venue": "Old Trafford",
        "date": "2026-06-08",
        "duration": 90,
        "events": [
            {"time": 12, "type": "goal", "team": "home", "description": "Header from corner", "dangerous": True},
            {"time": 23, "type": "shot", "team": "away", "description": "Shot saved", "dangerous": True},
            {"time": 34, "type": "yellow_card", "team": "away", "description": "Tactical foul"},
            {"time": 56, "type": "goal", "team": "away", "description": "Long range strike", "dangerous": True},
            {"time": 67, "type": "substitution", "team": "home", "description": "Fresh legs"},
            {"time": 78, "type": "goal", "team": "home", "description": "Counter attack", "dangerous": True},
            {"time": 85, "type": "var", "team": "away", "description": "Penalty check - no penalty"},
        ]
    }

def _create_momentum_chart(metrics):
    """Create momentum visualization chart"""
    fig = go.Figure()
    
    # Add bars for attacking vs defensive events
    fig.add_trace(go.Bar(
        name='Attacking',
        x=['Events'],
        y=[metrics['attacking_events']],
        marker_color='green'
    ))
    
    fig.add_trace(go.Bar(
        name='Defensive',
        x=['Events'],
        y=[metrics['defensive_events']],
        marker_color='red'
    ))
    
    fig.update_layout(
        title='Attacking vs Defensive Events',
        barmode='group',
        height=300
    )
    
    return fig

# Made with Bob
