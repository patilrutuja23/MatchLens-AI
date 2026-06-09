"""
Match Story Generator
Generates engaging match narratives using AI with dynamic content and turning point analysis
"""

from typing import Dict, List, Optional, Tuple
from src.utils.granite_client import GraniteClient
from src.utils.vector_db import VectorDatabase
import random

class StoryGenerator:
    """Generates compelling match stories using AI with enhanced dynamics"""
    
    def __init__(self):
        """Initialize story generator"""
        self.granite_client = GraniteClient()
        self.vector_db = VectorDatabase()
    
    def generate_match_story(
        self,
        match_data: Dict,
        style: str = "dramatic",
        length: str = "medium"
    ) -> Dict:
        """
        Generate a complete match story with dynamic content
        
        Args:
            match_data: Complete match data
            style: Story style (dramatic, analytical, casual)
            length: Story length (short, medium, long)
            
        Returns:
            Generated story with sections and metadata
        """
        # Extract key moments and analyze match
        key_moments = self._extract_key_moments(match_data)
        turning_point = self._identify_turning_point(match_data, key_moments)
        match_narrative = self._analyze_match_narrative(match_data, key_moments)
        
        # Generate story sections with unique content
        story_sections = {
            "title": self._generate_dynamic_title(match_data, key_moments, match_narrative),
            "introduction": self._generate_dynamic_introduction(match_data, style, match_narrative),
            "first_half": self._generate_dynamic_half_story(match_data, "first", key_moments, style, match_narrative),
            "second_half": self._generate_dynamic_half_story(match_data, "second", key_moments, style, match_narrative),
            "turning_point": self._generate_turning_point_narrative(turning_point, style),
            "conclusion": self._generate_dynamic_conclusion(match_data, style, match_narrative),
            "key_moments": key_moments,
            "player_highlights": self._generate_dynamic_player_highlights(match_data),
            "turning_point_data": turning_point
        }
        
        # Add explainability metadata
        explainability = self._generate_explainability_data(match_data, key_moments, turning_point)
        
        # Combine into full story
        full_story = self._combine_story_sections(story_sections, length)
        
        return {
            "full_story": full_story,
            "sections": story_sections,
            "style": style,
            "length": length,
            "word_count": len(full_story.split()),
            "explainability": explainability,
            "match_narrative": match_narrative
        }
    
    def generate_quick_summary(self, match_data: Dict) -> str:
        """Generate a quick 2-3 sentence summary of the match"""
        home_team = match_data.get("home_team", "Home")
        away_team = match_data.get("away_team", "Away")
        score = match_data.get("final_score") or match_data.get("score", "0-0")
        
        system_prompt = """You are a professional sports journalist.
Write a concise 2-3 sentence summary of the match that captures the key moments and final result."""
        
        events = match_data.get("events", [])
        key_events = [e for e in events if e.get("type") in ["goal", "red_card", "penalty", "var"]]
        
        events_text = "\n".join([
            f"- {e.get('time', 0)}': {e.get('type', 'event')} - {e.get('description', '')}"
            for e in key_events[:5]
        ])
        
        context = f"""Match: {home_team} vs {away_team}
Final Score: {score}
Key Events:
{events_text if events_text else 'No major events'}"""
        
        user_message = "Write a brief, engaging summary of this match."
        
        return self.granite_client.generate_with_context(
            system_prompt=system_prompt,
            user_message=user_message,
            context=context
        )
    
    def _parse_time(self, time_value) -> int:
        """Parse time value to integer, handling various formats"""
        if time_value is None:
            return 0
        
        if isinstance(time_value, (int, float)):
            return int(time_value)
        
        if isinstance(time_value, str):
            time_str = str(time_value).strip()
            if '+' in time_str:
                base_time = time_str.split('+')[0]
                return int(base_time)
            return int(time_str)
        
        return 0
    
    def _extract_key_moments(self, match_data: Dict) -> List[Dict]:
        """Extract and enrich key moments from match data"""
        key_moments = []
        priority_events = ["goal", "red_card", "penalty", "var_decision", "injury", "substitution"]
        
        events = match_data.get("events", [])
        for event in events:
            event_type = str(event.get("type", "")).lower()
            
            if any(priority in event_type for priority in priority_events):
                time_value = event.get("time", 0)
                parsed_time = self._parse_time(time_value)
                
                moment = {
                    "time": parsed_time,
                    "time_display": str(time_value),
                    "type": event.get("type", ""),
                    "description": event.get("description", ""),
                    "team": event.get("team", ""),
                    "player": event.get("player", ""),
                    "impact": self._calculate_moment_impact(event, match_data)
                }
                key_moments.append(moment)
        
        key_moments.sort(key=lambda x: x.get("time", 0))
        return key_moments
    
    def _calculate_moment_impact(self, event: Dict, match_data: Dict) -> int:
        """Calculate the impact score of a moment (0-100)"""
        impact = 50
        event_type = str(event.get("type", "")).lower()
        time = self._parse_time(event.get("time", 0))
        
        if "goal" in event_type:
            impact += 30
        if "red_card" in event_type:
            impact += 25
        if "penalty" in event_type:
            impact += 20
        if "var" in event_type:
            impact += 15
        
        if time > 80:
            impact += 20
        elif time > 70:
            impact += 10
        
        description = str(event.get("description", "")).lower()
        if "equalizer" in description:
            impact += 15
        if "winner" in description:
            impact += 20
        
        return min(impact, 100)
    
    def _identify_turning_point(self, match_data: Dict, key_moments: List[Dict]) -> Dict:
        """Identify the most impactful turning point in the match"""
        if not key_moments:
            return {
                "minute": 0,
                "event_type": "None",
                "description": "No significant turning point identified",
                "impact_score": 0,
                "momentum_swing": 0,
                "reason": "Match had no major incidents"
            }
        
        turning_point = max(key_moments, key=lambda x: x.get("impact", 0))
        momentum_swing = self._calculate_momentum_swing(turning_point, match_data)
        reason = self._generate_turning_point_reason(turning_point, match_data)
        
        return {
            "minute": turning_point.get("time", 0),
            "event_type": turning_point.get("type", "Unknown"),
            "description": turning_point.get("description", ""),
            "player": turning_point.get("player", ""),
            "team": turning_point.get("team", ""),
            "impact_score": turning_point.get("impact", 0),
            "momentum_swing": momentum_swing,
            "reason": reason
        }
    
    def _calculate_momentum_swing(self, event: Dict, match_data: Dict) -> int:
        """Calculate momentum swing from an event (-100 to +100)"""
        swing = 0
        event_type = str(event.get("type", "")).lower()
        
        if "goal" in event_type:
            swing = 60
        elif "red_card" in event_type:
            swing = 50
        elif "penalty" in event_type:
            swing = 40
        elif "var" in event_type:
            swing = 30
        
        time = self._parse_time(event.get("time", 0))
        if time > 80:
            swing = int(swing * 1.3)
        
        return min(swing, 100)
    
    def _generate_turning_point_reason(self, event: Dict, match_data: Dict) -> str:
        """Generate explanation for why this was the turning point"""
        event_type = str(event.get("type", "")).lower()
        time = self._parse_time(event.get("time", 0))
        reasons = []
        
        if "goal" in event_type:
            if time > 80:
                reasons.append("Late goal completely shifted momentum")
            description = str(event.get("description", "")).lower()
            if "equalizer" in description:
                reasons.append("Equalizer changed the psychological balance")
            if "winner" in description:
                reasons.append("Match-winning goal sealed the result")
        
        if "red_card" in event_type:
            reasons.append("Numerical disadvantage forced tactical reorganization")
        
        if "penalty" in event_type:
            reasons.append("High-pressure moment with significant consequences")
        
        if not reasons:
            reasons.append("Critical moment that influenced the match outcome")
        
        return "; ".join(reasons)
    
    def _analyze_match_narrative(self, match_data: Dict, key_moments: List[Dict]) -> Dict:
        """Analyze the overall match narrative for dynamic story generation"""
        narrative = {
            "match_type": "balanced",
            "drama_level": "medium",
            "comeback": False,
            "late_drama": False,
            "dominant_team": None,
            "key_themes": []
        }
        
        goals = [m for m in key_moments if "goal" in str(m.get("type", "")).lower()]
        if goals:
            goal_times = [self._parse_time(g.get("time", 0)) for g in goals]
            if any(t > 80 for t in goal_times):
                narrative["late_drama"] = True
                narrative["key_themes"].append("late_drama")
            
            if len(goals) >= 4:
                narrative["drama_level"] = "high"
                narrative["key_themes"].append("goal_fest")
        
        red_cards = [m for m in key_moments if "red_card" in str(m.get("type", "")).lower()]
        if red_cards:
            narrative["drama_level"] = "high"
            narrative["key_themes"].append("controversy")
        
        var_decisions = [m for m in key_moments if "var" in str(m.get("type", "")).lower()]
        if var_decisions:
            narrative["key_themes"].append("var_drama")
        
        return narrative
    
    def _generate_dynamic_title(self, match_data: Dict, key_moments: List[Dict], narrative: Dict) -> str:
        """Generate a dynamic, engaging title based on match narrative"""
        home_team = match_data.get("home_team", "Home")
        away_team = match_data.get("away_team", "Away")
        score = match_data.get("final_score") or match_data.get("score", "0-0")
        
        if narrative.get("late_drama"):
            return f"Late Drama as {home_team} and {away_team} Share Spoils {score}"
        elif narrative.get("comeback"):
            return f"Incredible Comeback: {home_team} vs {away_team} Ends {score}"
        elif "goal_fest" in narrative.get("key_themes", []):
            return f"Goal Thriller: {home_team} {score} {away_team}"
        elif "controversy" in narrative.get("key_themes", []):
            return f"Controversial Clash: {home_team} vs {away_team} ({score})"
        else:
            return f"{home_team} vs {away_team}: Match Report ({score})"
    
    def _generate_dynamic_introduction(self, match_data: Dict, style: str, narrative: Dict) -> str:
        """Generate dynamic introduction based on match narrative"""
        home_team = match_data.get("home_team", "Home")
        away_team = match_data.get("away_team", "Away")
        score = match_data.get("final_score") or match_data.get("score", "0-0")
        venue = match_data.get("venue", "the stadium")
        
        system_prompt = f"""You are a professional sports journalist writing in a {style} style.
Write an engaging 2-3 sentence introduction for a match report."""
        
        context = f"""Match: {home_team} vs {away_team}
Final Score: {score}
Venue: {venue}
Drama Level: {narrative.get('drama_level', 'medium')}
Key Themes: {', '.join(narrative.get('key_themes', ['competitive match']))}"""
        
        user_message = "Write an engaging introduction that captures the essence of this match."
        
        return self.granite_client.generate_with_context(
            system_prompt=system_prompt,
            user_message=user_message,
            context=context
        )
    
    def _generate_dynamic_half_story(
        self,
        match_data: Dict,
        half: str,
        key_moments: List[Dict],
        style: str,
        narrative: Dict
    ) -> str:
        """Generate dynamic half story with key moments"""
        if half == "first":
            time_range = "first half"
            moments = [m for m in key_moments if self._parse_time(m.get("time", 0)) <= 45]
        else:
            time_range = "second half"
            moments = [m for m in key_moments if self._parse_time(m.get("time", 0)) > 45]
        
        if not moments:
            return f"The {time_range} saw both teams probing for opportunities without major incidents."
        
        home_team = match_data.get("home_team", "Home")
        away_team = match_data.get("away_team", "Away")
        score_context = match_data.get("final_score") or match_data.get("score", "0-0")
        
        system_prompt = f"""You are a professional sports journalist writing in a {style} style.
Write an engaging narrative about the {time_range} of the match, incorporating the key moments."""
        
        moments_text = "\n".join([
            f"- {m.get('time_display', m.get('time', 0))}': {m.get('type', 'Event')} - {m.get('description', 'No description')}"
            for m in moments
        ])
        
        context = f"""Match: {home_team} vs {away_team}
Final Score: {score_context}
{time_range.title()} Key Moments:
{moments_text}"""
        
        user_message = f"Write an engaging narrative about the {time_range}, weaving in these key moments naturally."
        
        return self.granite_client.generate_with_context(
            system_prompt=system_prompt,
            user_message=user_message,
            context=context
        )
    
    def _generate_turning_point_narrative(self, turning_point: Dict, style: str) -> str:
        """Generate narrative about the match's turning point"""
        if turning_point.get("impact_score", 0) == 0:
            return "The match flowed without a clear turning point, with both teams evenly matched throughout."
        
        system_prompt = f"""You are a professional sports journalist writing in a {style} style.
Write a compelling 2-3 sentence narrative about the match's turning point."""
        
        context = f"""Turning Point:
Minute: {turning_point.get('minute', 0)}'
Event: {turning_point.get('event_type', 'Unknown')}
Description: {turning_point.get('description', 'No description')}
Player: {turning_point.get('player', 'Unknown')}
Team: {turning_point.get('team', 'Unknown')}
Impact Score: {turning_point.get('impact_score', 0)}/100
Reason: {turning_point.get('reason', 'Critical moment')}"""
        
        user_message = "Describe this turning point moment and its impact on the match."
        
        return self.granite_client.generate_with_context(
            system_prompt=system_prompt,
            user_message=user_message,
            context=context
        )
    
    def _generate_dynamic_conclusion(self, match_data: Dict, style: str, narrative: Dict) -> str:
        """Generate dynamic conclusion based on match outcome"""
        home_team = match_data.get("home_team", "Home")
        away_team = match_data.get("away_team", "Away")
        score = match_data.get("final_score") or match_data.get("score", "0-0")
        
        system_prompt = f"""You are a professional sports journalist writing in a {style} style.
Write a compelling 2-3 sentence conclusion that summarizes the match and its implications."""
        
        context = f"""Match: {home_team} vs {away_team}
Final Score: {score}
Drama Level: {narrative.get('drama_level', 'medium')}
Key Themes: {', '.join(narrative.get('key_themes', ['competitive match']))}"""
        
        user_message = "Write a conclusion that wraps up the match report and hints at what's next for both teams."
        
        return self.granite_client.generate_with_context(
            system_prompt=system_prompt,
            user_message=user_message,
            context=context
        )
    
    def _generate_dynamic_player_highlights(self, match_data: Dict) -> List[Dict]:
        """Generate player highlights from match data"""
        highlights = []
        
        events = match_data.get("events", [])
        for event in events:
            player = event.get("player")
            if player and event.get("type") in ["goal", "assist", "red_card", "yellow_card"]:
                highlights.append({
                    "player": player,
                    "team": event.get("team", "Unknown"),
                    "action": event.get("type", "action"),
                    "time": event.get("time", 0),
                    "description": event.get("description", "")
                })
        
        return highlights[:5]
    
    def _generate_explainability_data(
        self,
        match_data: Dict,
        key_moments: List[Dict],
        turning_point: Dict
    ) -> Dict:
        """Generate explainability metadata for transparency"""
        return {
            "key_moments_count": len(key_moments),
            "turning_point_minute": turning_point.get("minute", 0),
            "turning_point_impact": turning_point.get("impact_score", 0),
            "data_sources": ["match_events", "team_statistics", "player_actions"],
            "ai_model": "IBM Granite",
            "generation_method": "Dynamic narrative generation with RAG"
        }
    
    def _combine_story_sections(self, sections: Dict, length: str) -> str:
        """Combine story sections into full narrative"""
        story_parts = [
            f"# {sections['title']}\n",
            f"\n{sections['introduction']}\n",
            f"\n## First Half\n{sections['first_half']}\n",
            f"\n## Second Half\n{sections['second_half']}\n",
            f"\n## The Turning Point\n{sections['turning_point']}\n",
            f"\n## Conclusion\n{sections['conclusion']}\n"
        ]
        
        if length == "long" and sections.get('player_highlights'):
            highlights_text = "\n## Player Highlights\n"
            for highlight in sections['player_highlights'][:3]:
                highlights_text += f"- **{highlight['player']}** ({highlight['team']}): {highlight['action']} at {highlight['time']}'\n"
            story_parts.append(highlights_text)
        
        return "".join(story_parts)

# Made with Bob
