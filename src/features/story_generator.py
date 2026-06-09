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
    
    def _parse_time(self, time_value) -> int:
        """Parse time value to integer, handling various formats"""
        if time_value is None:
            return 0
        try:
            if isinstance(time_value, (int, float)):
                return int(time_value)
            elif isinstance(time_value, str):
                # Extract base minute from formats like "45+3" or "90+2"
                time_str = str(time_value).strip()
                if '+' in time_str:
                    return int(time_str.split('+')[0])
                else:
                    return int(time_str)
            else:
                return 0
        except (ValueError, AttributeError, TypeError) as e:
            return 0
    
    def _extract_key_moments(self, match_data: Dict) -> List[Dict]:
        """Extract and enrich key moments from match data"""
        key_moments = []
        
        priority_events = ["goal", "red_card", "penalty", "var_decision", "injury", "substitution"]
        
        for event in match_data.get("events", []):
            event_type = event.get("type", "").lower()
            
            if any(priority in event_type for priority in priority_events):
                time_value = event.get("time", 0)
                moment = {
                    "time": self._parse_time(time_value),
                    "time_display": str(time_value),  # Keep original for display
                    "type": event.get("type", ""),
                    "description": event.get("description", ""),
                    "team": event.get("team", ""),
                    "player": event.get("player", ""),
                    "impact": self._calculate_moment_impact(event, match_data)
                }
                key_moments.append(moment)
        
        # Sort by time (now guaranteed to be int)
        key_moments.sort(key=lambda x: x["time"])
        
        return key_moments
    
    def _calculate_moment_impact(self, event: Dict, match_data: Dict) -> int:
        """Calculate the impact score of a moment (0-100)"""
        impact = 50  # Base impact
        
        event_type = event.get("type", "").lower()
        time = self._parse_time(event.get("time", 0))
        
        # Event type impact
        if "goal" in event_type:
            impact += 30
        if "red_card" in event_type:
            impact += 25
        if "penalty" in event_type:
            impact += 20
        if "var" in event_type:
            impact += 15
        
        # Timing impact (late goals more impactful)
        if time > 80:
            impact += 20
        elif time > 70:
            impact += 10
        
        # Score context (equalizers and winners more impactful)
        if "equalizer" in event.get("description", "").lower():
            impact += 15
        if "winner" in event.get("description", "").lower():
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
        
        # Find moment with highest impact
        turning_point = max(key_moments, key=lambda x: x.get("impact", 0))
        
        # Calculate momentum swing
        momentum_swing = self._calculate_momentum_swing(turning_point, match_data)
        
        # Generate reason
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
        event_type = event.get("type", "").lower()
        
        if "goal" in event_type:
            swing = 60
        elif "red_card" in event_type:
            swing = 50
        elif "penalty" in event_type:
            swing = 40
        elif "var" in event_type:
            swing = 30
        
        # Adjust for timing
        time = self._parse_time(event.get("time", 0))
        if time > 80:
            swing = int(swing * 1.3)
        
        return min(swing, 100)
    
    def _generate_turning_point_reason(self, event: Dict, match_data: Dict) -> str:
        """Generate explanation for why this was the turning point"""
        event_type = event.get("type", "").lower()
        time = self._parse_time(event.get("time", 0))
        
        reasons = []
        
        if "goal" in event_type:
            if time > 80:
                reasons.append("Late goal completely shifted momentum")
            if "equalizer" in event.get("description", "").lower():
                reasons.append("Equalizer changed the psychological balance")
            if "winner" in event.get("description", "").lower():
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
        
        # Analyze goals
        goals = [m for m in key_moments if "goal" in m.get("type", "").lower()]
        if goals:
            goal_times = [g.get("time", 0) for g in goals]
            if any(t > 80 for t in goal_times):
                narrative["late_drama"] = True
                narrative["key_themes"].append("late_drama")
            
            # Check for comeback
            if len(goals) >= 2:
                teams = [g.get("team", "") for g in goals]
                if len(set(teams)) > 1:
                    narrative["comeback"] = True
                    narrative["key_themes"].append("comeback")
        
        # Analyze drama level
        red_cards = [m for m in key_moments if "red" in m.get("type", "").lower()]
        penalties = [m for m in key_moments if "penalty" in m.get("type", "").lower()]
        
        drama_score = len(goals) * 2 + len(red_cards) * 3 + len(penalties) * 2
        if drama_score > 8:
            narrative["drama_level"] = "high"
            narrative["match_type"] = "thriller"
        elif drama_score > 4:
            narrative["drama_level"] = "medium"
            narrative["match_type"] = "competitive"
        else:
            narrative["drama_level"] = "low"
            narrative["match_type"] = "tactical"
        
        return narrative
    
    def _generate_dynamic_title(self, match_data: Dict, key_moments: List[Dict], narrative: Dict) -> str:
        """Generate a dynamic, context-aware title"""
        home_team = match_data.get("home_team", "Home")
        away_team = match_data.get("away_team", "Away")
        score = match_data.get("final_score", "0-0")
        
        # Build context with narrative elements
        context_parts = [
            f"Match: {home_team} {score} {away_team}",
            f"Competition: {match_data.get('competition', 'Football Match')}",
            f"Match Type: {narrative.get('match_type', 'competitive')}",
            f"Drama Level: {narrative.get('drama_level', 'medium')}"
        ]
        
        if narrative.get("comeback"):
            context_parts.append("Notable: Dramatic comeback")
        if narrative.get("late_drama"):
            context_parts.append("Notable: Late drama with goals after 80th minute")
        
        # Add key moments summary
        goals = [m for m in key_moments if "goal" in m.get("type", "").lower()]
        if goals:
            context_parts.append(f"Goals: {len(goals)} scored")
        
        context = "\n".join(context_parts)
        
        system_prompt = """You are a creative sports journalist. Create a compelling, 
        unique headline that captures the essence of this match. Use dramatic language 
        for thrillers, tactical language for low-scoring games, and emphasize comebacks 
        or late drama when present. Make it exciting and memorable. Maximum 12 words."""
        
        user_message = "Create a unique, engaging headline for this specific match."
        
        title = self.granite_client.generate_with_context(
            system_prompt=system_prompt,
            user_message=user_message,
            context=context
        )
        
        return title.strip().strip('"').strip("'")
    
    def _generate_dynamic_introduction(self, match_data: Dict, style: str, narrative: Dict) -> str:
        """Generate dynamic introduction based on match narrative"""
        home_team = match_data.get("home_team", "Home")
        away_team = match_data.get("away_team", "Away")
        venue = match_data.get("venue", "Stadium")
        date = match_data.get("date", "Today")
        score = match_data.get("final_score", "0-0")
        
        style_instructions = {
            "dramatic": "Write with vivid imagery, emotional language, and build suspense",
            "analytical": "Focus on tactical setup, formations, and strategic approaches",
            "casual": "Write conversationally, as if describing the match to a friend at a pub"
        }
        
        # Build rich context
        context_parts = [
            f"Match: {home_team} {score} {away_team}",
            f"Venue: {venue}",
            f"Date: {date}",
            f"Competition: {match_data.get('competition', 'Football Match')}",
            f"Attendance: {match_data.get('attendance', 'Full stadium')}",
            f"Match Character: {narrative.get('match_type', 'competitive')} encounter"
        ]
        
        if narrative.get("comeback"):
            context_parts.append("Key Feature: Dramatic comeback story")
        if narrative.get("late_drama"):
            context_parts.append("Key Feature: Late goals changed everything")
        
        context = "\n".join(context_parts)
        
        system_prompt = f"""You are a sports journalist. {style_instructions.get(style, '')}
        Write a unique, engaging introduction that sets the scene for THIS SPECIFIC match. 
        Reference the actual teams, venue, and match outcome. Avoid generic phrases. 
        Make readers feel they're there. 2-3 sentences."""
        
        user_message = f"Write a unique introduction for this {narrative.get('match_type', 'competitive')} match between {home_team} and {away_team}."
        
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
        """Generate dynamic half story with specific events"""
        # Filter moments for this half
        if half == "first":
            half_moments = [m for m in key_moments if m["time"] <= 45]
            time_range = "first 45 minutes"
            score_context = match_data.get('halftime_score', '0-0')
        else:
            half_moments = [m for m in key_moments if m["time"] > 45]
            time_range = "second half"
            score_context = match_data.get('final_score', '0-0')
        
        # Build detailed moments description
        moments_details = []
        for m in half_moments:
            detail = f"{m['time']}' - {m['type']}: {m['description']}"
            if m.get('player'):
                detail += f" ({m['player']})"
            moments_details.append(detail)
        
        moments_text = "\n".join(moments_details) if moments_details else "No major incidents"
        
        # Add narrative context
        context_parts = [
            f"Match: {match_data.get('home_team', 'Home')} vs {match_data.get('away_team', 'Away')}",
            f"Period: {time_range}",
            f"Score at end of period: {score_context}",
            f"Match Type: {narrative.get('match_type', 'competitive')}",
            "",
            "Specific Events:",
            moments_text
        ]
        
        if half == "second" and narrative.get("late_drama"):
            context_parts.append("\nNotable: Late drama with crucial goals")
        if half == "second" and narrative.get("comeback"):
            context_parts.append("\nNotable: Comeback unfolded in this period")
        
        context = "\n".join(context_parts)
        
        system_prompt = f"""You are a sports journalist writing a match report. 
        Describe the {half} half with specific references to the actual events listed. 
        Use the players' names, exact timings, and describe HOW goals were scored or 
        incidents occurred. Write in a {style} style. Make it unique and engaging. 
        Avoid generic descriptions. 3-4 sentences."""
        
        user_message = f"Describe the {half} half with specific details from the events listed."
        
        return self.granite_client.generate_with_context(
            system_prompt=system_prompt,
            user_message=user_message,
            context=context
        )
    
    def _generate_turning_point_narrative(self, turning_point: Dict, style: str) -> str:
        """Generate narrative for the turning point"""
        if turning_point.get("impact_score", 0) == 0:
            return "No clear turning point emerged in this evenly-contested match."
        
        minute = turning_point.get("minute", 0)
        event_type = turning_point.get("event_type", "")
        description = turning_point.get("description", "")
        player = turning_point.get("player", "")
        reason = turning_point.get("reason", "")
        
        context = f"""Turning Point Details:
Minute: {minute}'
Event: {event_type}
Description: {description}
Player: {player}
Impact Score: {turning_point.get('impact_score', 0)}/100
Momentum Swing: {turning_point.get('momentum_swing', 0)}
Why it mattered: {reason}"""
        
        system_prompt = f"""You are a sports analyst. Describe this match's turning point 
        with dramatic flair. Explain WHY this moment changed everything. Reference the 
        specific minute, player, and event. Write in a {style} style. 2-3 sentences."""
        
        user_message = "Describe this turning point and its impact on the match."
        
        return self.granite_client.generate_with_context(
            system_prompt=system_prompt,
            user_message=user_message,
            context=context
        )
    
    def _generate_dynamic_conclusion(self, match_data: Dict, style: str, narrative: Dict) -> str:
        """Generate dynamic conclusion based on match outcome"""
        home_team = match_data.get("home_team", "Home")
        away_team = match_data.get("away_team", "Away")
        score = match_data.get("final_score", "0-0")
        
        context_parts = [
            f"Final Result: {home_team} {score} {away_team}",
            f"Match Type: {narrative.get('match_type', 'competitive')}",
            f"Man of the Match: {match_data.get('man_of_match', 'Not awarded')}",
            f"Key Stats: Possession {match_data.get('key_stats', {}).get('possession', 'N/A')}"
        ]
        
        if narrative.get("comeback"):
            context_parts.append("Narrative: Dramatic comeback defined the match")
        if narrative.get("late_drama"):
            context_parts.append("Narrative: Late goals provided thrilling finish")
        
        context = "\n".join(context_parts)
        
        system_prompt = f"""You are a sports journalist. Write a conclusion that 
        summarizes THIS SPECIFIC match's outcome and significance. Reference the 
        actual result, key performers, and what it means for both teams. 
        Write in a {style} style. Avoid clichés. 2-3 sentences."""
        
        user_message = f"Write a unique conclusion for this {narrative.get('match_type', 'competitive')} match."
        
        return self.granite_client.generate_with_context(
            system_prompt=system_prompt,
            user_message=user_message,
            context=context
        )
    
    def _generate_dynamic_player_highlights(self, match_data: Dict) -> Dict:
        """Generate unique player highlights"""
        highlights = {}
        top_players = match_data.get("top_performers", [])
        
        for player in top_players[:3]:
            player_name = player.get("name", "Unknown")
            player_stats = player.get("stats", {})
            team = player.get("team", "Unknown")
            position = player.get("position", "Unknown")
            rating = player.get("rating", "N/A")
            
            # Build specific context
            context = f"""Player: {player_name}
Team: {team}
Position: {position}
Rating: {rating}
Specific Stats: {player_stats}
Key Actions: {player.get('key_actions', 'Multiple contributions')}"""
            
            system_prompt = """You are a sports analyst. Write a brief, specific highlight 
            of this player's performance. Reference their actual stats and contributions. 
            Avoid generic praise. 2 sentences."""
            
            user_message = f"Describe {player_name}'s specific contributions in this match."
            
            highlights[player_name] = self.granite_client.generate_with_context(
                system_prompt=system_prompt,
                user_message=user_message,
                context=context
            )
        
        return highlights
    
    def _generate_explainability_data(self, match_data: Dict, key_moments: List[Dict], turning_point: Dict) -> Dict:
        """Generate explainability metadata for the story"""
        factors = []
        evidence = []
        
        # Analyze factors
        if key_moments:
            factors.append("Key Match Events")
            evidence.append(f"{len(key_moments)} significant moments analyzed")
        
        goals = [m for m in key_moments if "goal" in m.get("type", "").lower()]
        if goals:
            factors.append("Goals Scored")
            evidence.append(f"{len(goals)} goals with timing and context")
        
        if match_data.get("key_stats"):
            factors.append("Match Statistics")
            evidence.append("Possession, shots, and tactical data")
        
        if match_data.get("top_performers"):
            factors.append("Player Performances")
            evidence.append(f"{len(match_data.get('top_performers', []))} top performers evaluated")
        
        if turning_point.get("impact_score", 0) > 0:
            factors.append("Turning Point Analysis")
            evidence.append(f"Critical moment at {turning_point.get('minute', 0)}' identified")
        
        # Calculate confidence score
        confidence = 70  # Base confidence
        if len(key_moments) > 3:
            confidence += 10
        if goals:
            confidence += 10
        if match_data.get("key_stats"):
            confidence += 5
        if match_data.get("top_performers"):
            confidence += 5
        
        confidence = min(confidence, 95)
        
        return {
            "confidence_score": confidence,
            "factors_considered": factors,
            "evidence_used": evidence,
            "key_events_count": len(key_moments),
            "analysis_depth": "comprehensive" if confidence > 85 else "detailed"
        }
    
    def _combine_story_sections(self, sections: Dict, length: str) -> str:
        """Combine story sections into full narrative"""
        story_parts = [
            f"# {sections['title']}\n",
            sections['introduction'],
            "\n## First Half\n",
            sections['first_half']
        ]
        
        # Add turning point if significant
        if sections['turning_point_data'].get('impact_score', 0) > 60:
            story_parts.extend([
                "\n## Match Turning Point\n",
                sections['turning_point']
            ])
        
        story_parts.extend([
            "\n## Second Half\n",
            sections['second_half'],
            "\n## Conclusion\n",
            sections['conclusion']
        ])
        
        # Add player highlights for medium/long stories
        if length in ["medium", "long"] and sections['player_highlights']:
            story_parts.append("\n## Player Highlights\n")
            for player, highlight in sections['player_highlights'].items():
                story_parts.append(f"\n**{player}**: {highlight}")
        
        return "\n".join(story_parts)
    
    def generate_quick_summary(self, match_data: Dict) -> str:
        """Generate a quick 2-3 sentence match summary"""
        home_team = match_data.get("home_team", "Home")
        away_team = match_data.get("away_team", "Away")
        score = match_data.get("final_score", "0-0")
        
        context = f"""Match: {home_team} {score} {away_team}
Competition: {match_data.get('competition', 'Football Match')}
Key Events: {len(match_data.get('events', []))} total events
Man of Match: {match_data.get('man_of_match', 'Not awarded')}"""
        
        system_prompt = """You are a sports journalist. Write a concise 2-3 sentence 
        summary with specific details about THIS match. Include the score and a key moment."""
        
        user_message = f"Summarize the {home_team} vs {away_team} match."
        
        return self.granite_client.generate_with_context(
            system_prompt=system_prompt,
            user_message=user_message,
            context=context
        )

# Made with Bob
