"""
Match Momentum Explainer
Analyzes and explains momentum shifts during football matches
"""

from typing import Dict, List, Optional
import pandas as pd
from src.utils.granite_client import GraniteClient
from src.utils.vector_db import VectorDatabase

class MomentumExplainer:
    """Explains match momentum changes using AI"""
    
    def __init__(self):
        """Initialize momentum explainer"""
        self.granite_client = GraniteClient()
        self.vector_db = VectorDatabase()
    
    def analyze_momentum_shift(
        self,
        match_data: Dict,
        time_period: str,
        events: List[Dict]
    ) -> Dict:
        """
        Analyze momentum shift in a specific time period
        
        Args:
            match_data: Overall match information
            time_period: Time period of analysis (e.g., "45-60 minutes")
            events: List of events during this period
            
        Returns:
            Analysis results with explanation
        """
        # Prepare context
        context = self._prepare_momentum_context(match_data, time_period, events)
        
        # Search for similar historical patterns
        similar_patterns = self.vector_db.search(
            query=f"momentum shift {time_period} {events}",
            k=3
        )
        
        # Generate explanation
        explanation = self._generate_momentum_explanation(
            context,
            similar_patterns
        )
        
        # Calculate momentum metrics
        metrics = self._calculate_momentum_metrics(events)
        
        return {
            "explanation": explanation,
            "metrics": metrics,
            "similar_patterns": similar_patterns,
            "key_events": self._identify_key_events(events)
        }
    
    def _prepare_momentum_context(
        self,
        match_data: Dict,
        time_period: str,
        events: List[Dict]
    ) -> str:
        """Prepare context string for AI analysis"""
        teams = f"{match_data.get('home_team', 'Home')} vs {match_data.get('away_team', 'Away')}"
        score = match_data.get('score', '0-0')
        
        event_summary = "\n".join([
            f"- {event.get('time', 'Unknown')}: {event.get('type', 'Event')} - {event.get('description', '')}"
            for event in events[:5]  # Top 5 events
        ])
        
        context = f"""Match: {teams}
Score: {score}
Time Period: {time_period}

Key Events:
{event_summary}

Total Events: {len(events)}"""
        
        return context
    
    def _generate_momentum_explanation(
        self,
        context: str,
        similar_patterns: List
    ) -> str:
        """Generate AI explanation for momentum shift"""
        system_prompt = """You are an expert football analyst. Analyze the momentum 
        shift in this match period and explain what caused it, how it affected the game, 
        and what tactical changes might have contributed. Be specific and educational."""
        
        # Add similar patterns to context if available
        if similar_patterns:
            pattern_context = "\n\nSimilar historical patterns:\n"
            for doc, meta, dist in similar_patterns[:2]:
                pattern_context += f"- {doc[:200]}...\n"
            context += pattern_context
        
        user_message = "Explain the momentum shift in this period and its impact on the match."
        
        return self.granite_client.generate_with_context(
            system_prompt=system_prompt,
            user_message=user_message,
            context=context
        )
    
    def _calculate_momentum_metrics(self, events: List[Dict]) -> Dict:
        """Calculate momentum metrics from events"""
        metrics = {
            "total_events": len(events),
            "attacking_events": 0,
            "defensive_events": 0,
            "possession_changes": 0,
            "dangerous_attacks": 0
        }
        
        attacking_types = ["shot", "corner", "free_kick", "attack"]
        defensive_types = ["tackle", "clearance", "block", "interception"]
        
        for event in events:
            event_type = event.get("type", "").lower()
            
            if any(att in event_type for att in attacking_types):
                metrics["attacking_events"] += 1
            
            if any(def_type in event_type for def_type in defensive_types):
                metrics["defensive_events"] += 1
            
            if "possession" in event_type:
                metrics["possession_changes"] += 1
            
            if event.get("dangerous", False):
                metrics["dangerous_attacks"] += 1
        
        # Calculate momentum score (-100 to 100)
        if metrics["total_events"] > 0:
            attack_ratio = metrics["attacking_events"] / metrics["total_events"]
            metrics["momentum_score"] = int((attack_ratio - 0.5) * 200)
        else:
            metrics["momentum_score"] = 0
        
        return metrics
    
    def _identify_key_events(self, events: List[Dict]) -> List[Dict]:
        """Identify key events that influenced momentum"""
        key_events = []
        
        # Priority event types
        priority_types = ["goal", "red_card", "penalty", "var_decision"]
        
        for event in events:
            event_type = event.get("type", "").lower()
            
            # Add high priority events
            if any(priority in event_type for priority in priority_types):
                key_events.append(event)
            
            # Add dangerous attacks
            elif event.get("dangerous", False):
                key_events.append(event)
        
        # Sort by time
        key_events.sort(key=lambda x: x.get("time", 0))
        
        return key_events[:5]  # Return top 5 key events
    
    def get_momentum_timeline(
        self,
        match_data: Dict,
        interval_minutes: int = 15
    ) -> List[Dict]:
        """
        Generate momentum timeline for entire match
        
        Args:
            match_data: Complete match data
            interval_minutes: Time interval for analysis
            
        Returns:
            List of momentum analysis for each interval
        """
        timeline = []
        match_duration = match_data.get("duration", 90)
        
        for start_time in range(0, match_duration, interval_minutes):
            end_time = min(start_time + interval_minutes, match_duration)
            time_period = f"{start_time}-{end_time} minutes"
            
            # Filter events for this period
            events = []
            for event in match_data.get("events", []):
                event_time = event.get("time", 0)
                # Convert time to int if it's a string
                if isinstance(event_time, str):
                    # Handle formats like "45", "45+2", "45:30"
                    if '+' in event_time:
                        base, added = event_time.split('+')
                        event_time = int(base) + int(added)
                    elif ':' in event_time:
                        mins, secs = event_time.split(':')
                        event_time = int(mins)
                    else:
                        try:
                            event_time = int(event_time)
                        except:
                            event_time = 0
                elif isinstance(event_time, (int, float)):
                    event_time = int(event_time)
                else:
                    event_time = 0
                
                if start_time <= event_time < end_time:
                    events.append(event)
            
            if events:
                analysis = self.analyze_momentum_shift(
                    match_data,
                    time_period,
                    events
                )
                analysis["time_period"] = time_period
                timeline.append(analysis)
        
        return timeline

# Made with Bob
