"""
Live Match Analysis Page
Real-time match tracking with AI-powered analysis
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from src.features.live_match import LiveMatchAnalyzer


def init_session_state():
    """Initialize session state variables"""
    if "live_analyzer" not in st.session_state:
        st.session_state.live_analyzer = LiveMatchAnalyzer()
    
    if "match_started" not in st.session_state:
        st.session_state.match_started = False
    
    if "show_analysis" not in st.session_state:
        st.session_state.show_analysis = {}


def render_match_setup():
    """Render match setup form"""
    st.subheader("⚽ Start New Match")
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.text_input(
            "Home Team",
            placeholder="e.g., Manchester United",
            key="home_team_input"
        )
    
    with col2:
        away_team = st.text_input(
            "Away Team",
            placeholder="e.g., Liverpool",
            key="away_team_input"
        )
    
    # Optional fields
    with st.expander("📋 Additional Information (Optional)"):
        col1, col2 = st.columns(2)
        
        with col1:
            competition = st.text_input("Competition", value="Friendly")
            venue = st.text_input("Venue", value="")
        
        with col2:
            date = st.date_input("Date", value=datetime.now())
            referee = st.text_input("Referee", value="")
    
    if st.button("🚀 Start Match", type="primary", use_container_width=True):
        if not home_team or not away_team:
            st.error("❌ Please enter both team names")
        elif home_team == away_team:
            st.error("❌ Teams must be different")
        else:
            # Start match
            result = st.session_state.live_analyzer.start_match(
                home_team=home_team,
                away_team=away_team,
                competition=competition,
                venue=venue,
                date=str(date),
                referee=referee
            )
            
            st.session_state.match_started = True
            st.success(f"✅ {result['message']}")
            st.rerun()


def render_score_display():
    """Render current score display"""
    analyzer = st.session_state.live_analyzer
    summary = analyzer.get_match_summary()
    
    # Score display
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        st.markdown(f"### {analyzer.match_data['home_team']}")
    
    with col2:
        st.markdown(f"## <center>{summary['score']}</center>", unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"### <div style='text-align: right'>{analyzer.match_data['away_team']}</div>", unsafe_allow_html=True)
    
    # Match info
    st.caption(f"📍 {analyzer.match_data.get('venue', 'Unknown Venue')} | "
              f"🏆 {analyzer.match_data.get('competition', 'Unknown Competition')} | "
              f"📅 {analyzer.match_data.get('date', 'Unknown Date')}")
    
    st.divider()


def render_event_form():
    """Render event addition form"""
    analyzer = st.session_state.live_analyzer
    
    st.subheader("➕ Add Event")
    
    # Event type selection
    col1, col2, col3 = st.columns(3)
    
    with col1:
        event_type = st.selectbox(
            "Event Type",
            options=["goal", "yellow_card", "red_card", "substitution", 
                    "corner", "penalty", "var_review", "halftime", "fulltime"],
            format_func=lambda x: x.replace("_", " ").title(),
            key="event_type"
        )
    
    with col2:
        time = st.text_input(
            "Time",
            placeholder="e.g., 45+2",
            help="Format: 45 or 45+2 or 45:30",
            key="event_time"
        )
    
    with col3:
        team = st.selectbox(
            "Team",
            options=[analyzer.match_data["home_team"], analyzer.match_data["away_team"]],
            key="event_team"
        )
    
    # Event-specific fields
    player = None
    assist = None
    reason = None
    player_out = None
    player_in = None
    decision_type = None
    initial_decision = None
    final_decision = None
    
    if event_type == "goal":
        col1, col2 = st.columns(2)
        with col1:
            player = st.text_input("Goal Scorer", key="goal_player")
        with col2:
            assist = st.text_input("Assist (optional)", key="goal_assist")
    
    elif event_type in ["yellow_card", "red_card"]:
        col1, col2 = st.columns(2)
        with col1:
            player = st.text_input("Player", key="card_player")
        with col2:
            reason = st.text_input("Reason", key="card_reason")
    
    elif event_type == "substitution":
        col1, col2 = st.columns(2)
        with col1:
            player_out = st.text_input("Player Out", key="sub_out")
        with col2:
            player_in = st.text_input("Player In", key="sub_in")
        reason = st.text_input("Reason (optional)", value="Tactical", key="sub_reason")
    
    elif event_type == "var_review":
        col1, col2, col3 = st.columns(3)
        with col1:
            decision_type = st.selectbox(
                "Decision Type",
                ["penalty", "offside", "red_card", "goal"],
                key="var_type"
            )
        with col2:
            initial_decision = st.text_input("Initial Decision", key="var_initial")
        with col3:
            final_decision = st.text_input("Final Decision", key="var_final")
    
    # Description
    description = st.text_area(
        "Description",
        placeholder="Describe what happened...",
        key="event_description"
    )
    
    # Add event button
    if st.button("✅ Add Event", type="primary", use_container_width=True):
        if not time:
            st.error("❌ Please enter event time")
            return
        
        # Build event dictionary
        event = {
            "type": event_type,
            "time": time,
            "team": team,
            "description": description
        }
        
        # Add optional fields
        if player:
            event["player"] = player
        if assist:
            event["assist"] = assist
        if reason:
            event["reason"] = reason
        if player_out:
            event["player_out"] = player_out
        if player_in:
            event["player_in"] = player_in
        if decision_type:
            event["decision_type"] = decision_type
        if initial_decision:
            event["initial_decision"] = initial_decision
        if final_decision:
            event["final_decision"] = final_decision
        
        # Add event
        result = analyzer.add_event(event)
        
        if result["success"]:
            st.success(f"✅ Event added! Current score: {result['current_score']}")
            
            # Store analysis for display
            if result.get("analysis"):
                event_id = len(analyzer.events) - 1
                st.session_state.show_analysis[event_id] = result["analysis"]
            
            st.rerun()
        else:
            st.error(f"❌ {result.get('error', 'Failed to add event')}")


def render_timeline():
    """Render match timeline"""
    analyzer = st.session_state.live_analyzer
    timeline = analyzer.get_timeline()
    
    if not timeline:
        st.info("No events yet. Add your first event above!")
        return
    
    st.subheader("📊 Match Timeline")
    
    # Timeline visualization
    fig = go.Figure()
    
    # Prepare data for timeline
    times = []
    events = []
    colors = []
    
    color_map = {
        "goal": "#00ff00",
        "yellow_card": "#ffff00",
        "red_card": "#ff0000",
        "var_review": "#ff00ff",
        "penalty": "#ffa500",
        "substitution": "#00ffff",
        "corner": "#add8e6",
        "kickoff": "#808080",
        "halftime": "#808080",
        "fulltime": "#808080"
    }
    
    for i, event in enumerate(timeline):
        time_str = event.get("time", "0")
        # Convert time to minutes
        if "+" in time_str:
            base, added = time_str.split("+")
            time_val = int(base) + int(added)
        elif ":" in time_str:
            mins, secs = time_str.split(":")
            time_val = int(mins)
        else:
            time_val = int(time_str) if time_str.isdigit() else 0
        
        times.append(time_val)
        event_label = event.get("type", "unknown").replace("_", " ").title()
        if event.get("player"):
            event_label += f" - {event['player']}"
        events.append(event_label)
        colors.append(color_map.get(event.get("type"), "#808080"))
    
    fig.add_trace(go.Scatter(
        x=times,
        y=[1] * len(times),
        mode='markers+text',
        marker=dict(size=15, color=colors, line=dict(width=2, color='white')),
        text=events,
        textposition="top center",
        hovertemplate='<b>%{text}</b><br>Time: %{x}\'<extra></extra>'
    ))
    
    fig.update_layout(
        showlegend=False,
        height=200,
        xaxis=dict(title="Match Time (minutes)", range=[-5, 100]),
        yaxis=dict(visible=False, range=[0, 2]),
        hovermode='closest'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Event list
    st.subheader("📝 Event List")
    
    # Show last 10 events
    for i, event in enumerate(reversed(timeline[-10:])):
        event_idx = len(timeline) - i - 1
        
        # Event icon
        icon_map = {
            "goal": "⚽",
            "yellow_card": "🟨",
            "red_card": "🟥",
            "var_review": "📹",
            "penalty": "🎯",
            "substitution": "🔄",
            "corner": "🚩",
            "kickoff": "🏁",
            "halftime": "⏸️",
            "fulltime": "🏁"
        }
        
        icon = icon_map.get(event.get("type"), "📌")
        
        with st.expander(f"{icon} **{event.get('time', '?')}'** - {event.get('type', 'unknown').replace('_', ' ').title()}", expanded=(i == 0)):
            st.write(f"**Team:** {event.get('team', 'N/A')}")
            
            if event.get("player"):
                st.write(f"**Player:** {event['player']}")
            
            if event.get("description"):
                st.write(f"**Description:** {event['description']}")
            
            if event.get("score"):
                st.write(f"**Score:** {event['score']}")
            
            # Show AI analysis if available
            if event_idx in st.session_state.show_analysis:
                analysis = st.session_state.show_analysis[event_idx]
                st.divider()
                st.markdown("### 🤖 AI Analysis")
                st.write(analysis.get("analysis", ""))
                
                if analysis.get("impact"):
                    impact_color = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢"
                    }
                    st.caption(f"{impact_color.get(analysis['impact'], '⚪')} Impact: {analysis['impact'].title()}")


def render_statistics():
    """Render match statistics"""
    analyzer = st.session_state.live_analyzer
    summary = analyzer.get_match_summary()
    
    st.subheader("📈 Match Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Events", summary["total_events"])
    
    with col2:
        st.metric("VAR Reviews", summary.get("var_reviews", 0))
    
    with col3:
        home_cards = summary["cards"]["home"]
        st.metric("Home Cards", f"🟨{home_cards['yellow']} 🟥{home_cards['red']}")
    
    with col4:
        away_cards = summary["cards"]["away"]
        st.metric("Away Cards", f"🟨{away_cards['yellow']} 🟥{away_cards['red']}")
    
    # Event breakdown
    if summary.get("event_counts"):
        st.subheader("Event Breakdown")
        
        event_data = summary["event_counts"]
        cols = st.columns(len(event_data))
        
        for i, (event_type, count) in enumerate(event_data.items()):
            with cols[i]:
                st.metric(event_type.replace("_", " ").title(), count)


def render_momentum_analysis():
    """Render momentum analysis"""
    analyzer = st.session_state.live_analyzer
    
    st.subheader("⚡ Momentum Analysis")
    
    if len(analyzer.events) < 3:
        st.info("Need at least 3 events to analyze momentum")
        return
    
    if st.button("🔄 Analyze Current Momentum", use_container_width=True):
        with st.spinner("Analyzing momentum..."):
            momentum = analyzer.get_momentum_analysis(period_minutes=15)
            
            # Display momentum
            if momentum["momentum"] == "balanced":
                st.success("⚖️ **Momentum:** Balanced")
            elif momentum["momentum"] == analyzer.match_data["home_team"]:
                st.success(f"🏠 **Momentum:** {momentum['momentum']}")
            else:
                st.success(f"✈️ **Momentum:** {momentum['momentum']}")
            
            # Activity metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Home Activity", momentum["home_activity"])
            with col2:
                st.metric("Away Activity", momentum["away_activity"])
            
            # AI Analysis
            st.markdown("### 🤖 Tactical Analysis")
            st.write(momentum.get("analysis", ""))


def render_export_options():
    """Render export options"""
    analyzer = st.session_state.live_analyzer
    
    st.subheader("💾 Export Match Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export as JSON", use_container_width=True):
            import json
            match_data = analyzer.export_match_data()
            json_str = json.dumps(match_data, indent=2)
            
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"match_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("🔄 Reset Match", use_container_width=True, type="secondary"):
            if st.session_state.get("confirm_reset"):
                st.session_state.live_analyzer = LiveMatchAnalyzer()
                st.session_state.match_started = False
                st.session_state.show_analysis = {}
                st.session_state.confirm_reset = False
                st.success("✅ Match reset!")
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.warning("⚠️ Click again to confirm reset")


def main():
    """Main live match page"""
    st.title("⚡ Live Match Analysis")
    st.caption("Track match events in real-time with AI-powered analysis")
    
    # Initialize session state
    init_session_state()
    
    # Check if match is started
    if not st.session_state.match_started:
        render_match_setup()
    else:
        # Match in progress
        render_score_display()
        
        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Event", "📊 Timeline", "📈 Statistics", "⚡ Momentum"])
        
        with tab1:
            render_event_form()
        
        with tab2:
            render_timeline()
        
        with tab3:
            render_statistics()
        
        with tab4:
            render_momentum_analysis()
        
        # Export options
        st.divider()
        render_export_options()


if __name__ == "__main__":
    main()

# Made with Bob