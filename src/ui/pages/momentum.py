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
        st.metric("Match", f"{match_data.get('home_team', 'Unknown')} vs {match_data.get('away_team', 'Unknown')}")
    with col2:
        score = match_data.get('score', match_data.get('final_score', 'N/A'))
        st.metric("Final Score", score)
    with col3:
        st.metric("Competition", match_data.get('competition', 'Unknown'))
    
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
    events = match_data.get('events', [])
    
    # Filter events by time
    filtered_events = []
    for event in events:
        event_time = _parse_event_time(event.get('time', 0))
        if start_time <= event_time < end_time:
            filtered_events.append(event)
    
    if st.button("🔍 Analyze Momentum", type="primary"):
        if not filtered_events:
            st.warning("No events found in this time period")
            return
        
        with st.spinner("Analyzing momentum shift..."):
            # Analyze momentum
            analysis = explainer.analyze_momentum_shift(
                match_data,
                time_period,
                filtered_events
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

def _get_match_data():
    """Get match data from session state or sample data based on sidebar selection"""
    import json
    
    # Check sidebar selection
    selected_match = st.session_state.get('selected_match', 'Sample Match')
    
    # Debug output
    with st.sidebar.expander("🔍 Debug Info", expanded=False):
        st.write(f"**Selected:** {selected_match}")
        st.write(f"**current_match exists:** {'current_match' in st.session_state}")
        st.write(f"**match_loaded:** {st.session_state.get('match_loaded', False)}")
        if 'current_match' in st.session_state:
            match = st.session_state.current_match
            st.write(f"**Teams:** {match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')}")
    
    if selected_match == "Uploaded Match":
        # Check for uploaded match
        if 'current_match' in st.session_state and st.session_state.get('match_loaded'):
            return st.session_state.current_match
        
        # Check for live match
        if 'live_analyzer' in st.session_state:
            analyzer = st.session_state.live_analyzer
            if analyzer.match_started and analyzer.match_data:
                return analyzer.export_match_data()
        
        # No uploaded match found - show helpful message
        st.error("⚠️ 'Uploaded Match' selected but no match data found in session!")
        st.info("💡 Go to Upload Match page and click '✅ Load Match for Analysis'")
        return None
    
    else:  # Sample Match
        # Load sample match data
        try:
            with open("data/matches/sample_match.json", "r") as f:
                sample_data = json.load(f)
                # Normalize field names
                if 'score' in sample_data and 'final_score' not in sample_data:
                    sample_data['final_score'] = sample_data['score']
                return sample_data
        except FileNotFoundError:
            st.error("Sample match file not found")
            return None

def _parse_event_time(time_value):
    """Parse event time to minutes"""
    if isinstance(time_value, (int, float)):
        return int(time_value)
    
    if isinstance(time_value, str):
        # Handle formats like "45", "45+2", "45:30"
        time_str = str(time_value).strip()
        
        if '+' in time_str:
            base, added = time_str.split('+')
            return int(base) + int(added)
        elif ':' in time_str:
            mins, secs = time_str.split(':')
            return int(mins)
        else:
            try:
                return int(time_str)
            except:
                return 0
    
    return 0

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
