"""
Match Story Generator Page
"""

import streamlit as st
from src.features.story_generator import StoryGenerator
from src.utils.config import load_config

def render_story_page():
    """Render the Match Story Generator page"""
    
    st.title("📝 Match Story Generator")
    st.markdown("Generate engaging match narratives powered by AI")
    
    # Initialize generator
    if 'story_generator' not in st.session_state:
        st.session_state.story_generator = StoryGenerator()
    
    generator = st.session_state.story_generator
    
    # Load sample match data
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
    
    # Story customization options
    st.subheader("✍️ Customize Your Story")
    
    col1, col2 = st.columns(2)
    
    with col1:
        style = st.selectbox(
            "Story Style",
            ["dramatic", "analytical", "casual"],
            format_func=lambda x: x.title(),
            help="Choose the narrative style for your match story"
        )
    
    with col2:
        length = st.selectbox(
            "Story Length",
            ["short", "medium", "long"],
            index=1,
            format_func=lambda x: x.title(),
            help="Choose how detailed you want the story to be"
        )
    
    st.markdown("---")
    
    # Quick Summary
    st.subheader("⚡ Quick Summary")
    
    if st.button("Generate Quick Summary", type="secondary"):
        with st.spinner("Generating summary..."):
            summary = generator.generate_quick_summary(match_data)
            st.info(summary)
    
    st.markdown("---")
    
    # Full Story Generation
    st.subheader("📖 Full Match Story")
    
    if st.button("🎬 Generate Full Story", type="primary"):
        with st.spinner(f"Crafting your {style} match story... This may take a moment."):
            # Generate story
            story_result = generator.generate_match_story(
                match_data=match_data,
                style=style,
                length=length
            )
            
            # Display results
            st.success("Story Generated Successfully!")
            
            # Story metadata
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Style", story_result['style'].title())
            with col2:
                st.metric("Length", story_result['length'].title())
            with col3:
                st.metric("Word Count", story_result['word_count'])
            
            st.markdown("---")
            
            # Display full story
            st.markdown(story_result['full_story'])
            
            # Download button
            st.download_button(
                label="📥 Download Story",
                data=story_result['full_story'],
                file_name=f"match_story_{match_data['home_team']}_vs_{match_data['away_team']}.md",
                mime="text/markdown"
            )
            
            # Show individual sections
            st.markdown("---")
            st.subheader("📑 Story Sections")
            
            sections = story_result['sections']
            
            with st.expander("📰 Title"):
                st.write(sections['title'])
            
            with st.expander("🎬 Introduction"):
                st.write(sections['introduction'])
            
            with st.expander("⚽ First Half"):
                st.write(sections['first_half'])
            
            with st.expander("⚽ Second Half"):
                st.write(sections['second_half'])
            
            with st.expander("🏁 Conclusion"):
                st.write(sections['conclusion'])
            
            # Player highlights
            if sections['player_highlights']:
                st.markdown("---")
                st.subheader("⭐ Player Highlights")
                
                for player, highlight in sections['player_highlights'].items():
                    with st.expander(f"🏃 {player}"):
                        st.write(highlight)
            
            # Key moments timeline
            if sections['key_moments']:
                st.markdown("---")
                st.subheader("⏱️ Key Moments Timeline")
                
                for moment in sections['key_moments']:
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.write(f"**{moment['time']}'**")
                    with col2:
                        st.write(f"{moment['type'].upper()}: {moment['description']}")
    
    # Story examples
    st.markdown("---")
    st.subheader("💡 Story Style Examples")
    
    with st.expander("Dramatic Style"):
        st.write("""
        **Example:** "In a pulsating encounter that had fans on the edge of their seats, 
        Manchester United snatched a dramatic late winner against their fierce rivals..."
        
        - Vivid descriptions
        - Emotional language
        - Builds tension and excitement
        """)
    
    with st.expander("Analytical Style"):
        st.write("""
        **Example:** "Manchester United's tactical flexibility proved decisive as they 
        exploited Liverpool's high defensive line through well-timed counter-attacks..."
        
        - Focus on tactics and strategy
        - Technical analysis
        - Statistical insights
        """)
    
    with st.expander("Casual Style"):
        st.write("""
        **Example:** "What a game! United really turned it on in the second half and 
        showed why they're one of the best teams in the league..."
        
        - Conversational tone
        - Easy to understand
        - Relatable language
        """)

def _get_sample_match_data():
    """Get sample match data"""
    return {
        "home_team": "Manchester United",
        "away_team": "Liverpool",
        "final_score": "3-2",
        "halftime_score": "1-1",
        "competition": "Premier League",
        "venue": "Old Trafford",
        "date": "2026-06-08",
        "attendance": "74,879",
        "man_of_match": "Bruno Fernandes",
        "duration": 90,
        "key_stats": {
            "possession": "52% - 48%",
            "shots": "18 - 14",
            "shots_on_target": "8 - 6"
        },
        "events": [
            {
                "time": 12,
                "type": "goal",
                "team": "home",
                "player": "Marcus Rashford",
                "description": "Clinical finish after quick counter-attack"
            },
            {
                "time": 28,
                "type": "goal",
                "team": "away",
                "player": "Mohamed Salah",
                "description": "Curling shot from edge of the box"
            },
            {
                "time": 56,
                "type": "goal",
                "team": "away",
                "player": "Darwin Nunez",
                "description": "Header from corner kick"
            },
            {
                "time": 73,
                "type": "goal",
                "team": "home",
                "player": "Bruno Fernandes",
                "description": "Penalty conversion"
            },
            {
                "time": 89,
                "type": "goal",
                "team": "home",
                "player": "Alejandro Garnacho",
                "description": "Late winner from substitute"
            }
        ],
        "top_performers": [
            {
                "name": "Bruno Fernandes",
                "team": "Manchester United",
                "position": "Midfielder",
                "rating": 9.2,
                "stats": {
                    "goals": 1,
                    "assists": 2,
                    "key_passes": 5
                }
            },
            {
                "name": "Mohamed Salah",
                "team": "Liverpool",
                "position": "Forward",
                "rating": 8.5,
                "stats": {
                    "goals": 1,
                    "shots": 4,
                    "dribbles": 6
                }
            },
            {
                "name": "Marcus Rashford",
                "team": "Manchester United",
                "position": "Forward",
                "rating": 8.3,
                "stats": {
                    "goals": 1,
                    "shots": 5,
                    "key_passes": 3
                }
            }
        ]
    }

# Made with Bob
