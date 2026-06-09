"""
Live Match Analysis
Real-time match event tracking and AI analysis
"""

from typing import Dict, List, Optional
from datetime import datetime
from src.utils.granite_client import GraniteClient
from src.features.momentum_explainer import MomentumExplainer
from src.features.var_explainer import VARExplainer


class LiveMatchAnalyzer:
    """Handles live match event tracking and real-time analysis"""
    
    EVENT_TYPES = [
        "goal", "yellow_card", "red_card", "substitution",
        "corner", "penalty", "var_review", "kickoff", "halftime", "fulltime"
    ]
    
    MAJOR_EVENTS = ["goal", "red_card", "penalty", "var_review"]
    
    def __init__(self):
        """Initialize live match analyzer"""
        self.granite_client = GraniteClient()
        self.momentum_explainer = MomentumExplainer()
        self.var_explainer = VARExplainer()
        
        # Match state
        self.match_data = None
        self.events = []
        self.current_score = {"home": 0, "away": 0}
        self.match_started = False
        self.match_ended = False
    
    def start_match(self, home_team: str, away_team: str, **kwargs) -> Dict:
        """
        Start a new live match
        
        Args:
            home_team: Home team name
            away_team: Away team name
            **kwargs: Additional match information
            
        Returns:
            Match initialization data
        """
        self.match_data = {
            "home_team": home_team,
            "away_team": away_team,
            "date": kwargs.get("date", datetime.now().strftime("%Y-%m-%d")),
            "competition": kwargs.get("competition", "Friendly"),
            "venue": kwargs.get("venue", ""),
            "events": []
        }
        
        self.events = []
        self.current_score = {"home": 0, "away": 0}
        self.match_started = True
        self.match_ended = False
        
        # Add kickoff event
        kickoff_event = {
            "type": "kickoff",
            "time": "0",
            "team": home_team,
            "description": "Match kicks off",
            "timestamp": datetime.now().isoformat()
        }
        
        self.add_event(kickoff_event)
        
        return {
            "status": "started",
            "match_data": self.match_data,
            "message": f"Match started: {home_team} vs {away_team}"
        }
    
    def add_event(self, event: Dict) -> Dict:
        """
        Add a new event to the live match
        
        Args:
            event: Event dictionary
            
        Returns:
            Result with event analysis
        """
        if not self.match_started or self.match_data is None:
            return {
                "success": False,
                "error": "Match not started. Call start_match() first."
            }
        
        if self.match_ended:
            return {
                "success": False,
                "error": "Match has ended. Cannot add more events."
            }
        
        # Validate event
        if "type" not in event:
            return {
                "success": False,
                "error": "Event must have a 'type' field"
            }
        
        if event["type"] not in self.EVENT_TYPES:
            return {
                "success": False,
                "error": f"Invalid event type. Valid types: {', '.join(self.EVENT_TYPES)}"
            }
        
        # Add timestamp if not present
        if "timestamp" not in event:
            event["timestamp"] = datetime.now().isoformat()
        
        # Update score for goals
        if event["type"] == "goal":
            team = event.get("team", "")
            if team == self.match_data["home_team"]:
                self.current_score["home"] += 1
            elif team == self.match_data["away_team"]:
                self.current_score["away"] += 1
            
            event["score"] = f"{self.current_score['home']}-{self.current_score['away']}"
        
        # Add event to lists
        self.events.append(event)
        self.match_data["events"].append(event)
        
        # Generate AI analysis for major events
        analysis = None
        if event["type"] in self.MAJOR_EVENTS:
            analysis = self._analyze_event(event)
        
        # Check for match end
        if event["type"] == "fulltime":
            self.match_ended = True
            self.match_data["final_score"] = f"{self.current_score['home']}-{self.current_score['away']}"
        
        return {
            "success": True,
            "event": event,
            "current_score": f"{self.current_score['home']}-{self.current_score['away']}",
            "total_events": len(self.events),
            "analysis": analysis
        }
    
    def _analyze_event(self, event: Dict) -> Dict:
        """
        Generate AI analysis for a major event
        
        Args:
            event: Event to analyze
            
        Returns:
            Analysis dictionary
        """
        event_type = event["type"]
        
        if event_type == "goal":
            return self._analyze_goal(event)
        elif event_type == "var_review":
            return self._analyze_var_review(event)
        elif event_type == "red_card":
            return self._analyze_red_card(event)
        elif event_type == "penalty":
            return self._analyze_penalty(event)
        
        return {}
    
    def _analyze_goal(self, event: Dict) -> Dict:
        """Analyze a goal event"""
        player = event.get("player", "Unknown")
        team = event.get("team", "Unknown")
        time = event.get("time", "Unknown")
        
        prompt = f"""Analyze this goal:
Player: {player}
Team: {team}
Time: {time}'
Score: {event.get('score', 'Unknown')}
Description: {event.get('description', 'Goal scored')}

Provide a brief tactical analysis of this goal and its impact on the match."""
        
        analysis = self.granite_client.generate(prompt, max_tokens=200)
        
        return {
            "type": "goal_analysis",
            "analysis": analysis,
            "impact": "high"
        }
    
    def _analyze_var_review(self, event: Dict) -> Dict:
        """Analyze a VAR review event"""
        if not event.get("decision_type"):
            return {"type": "var_analysis", "analysis": "VAR review in progress"}
        
        if self.match_data is None:
            return {"type": "var_analysis", "analysis": "Match data not available"}
        
        # Use VAR explainer for detailed analysis
        match_context = {
            "home_team": self.match_data["home_team"],
            "away_team": self.match_data["away_team"],
            "score": f"{self.current_score['home']}-{self.current_score['away']}",
            "time": event.get("time", "Unknown")
        }
        
        incident_details = {
            "time": event.get("time", "Unknown"),
            "description": event.get("description", "VAR review"),
            "initial_decision": event.get("initial_decision", "Unknown"),
            "final_decision": event.get("final_decision", "Unknown"),
            "review_duration": event.get("review_duration", "Unknown")
        }
        
        result = self.var_explainer.explain_var_decision(
            decision_type=event.get("decision_type", "review"),
            match_context=match_context,
            incident_details=incident_details
        )
        
        return {
            "type": "var_analysis",
            "analysis": result.get("explanation", ""),
            "confidence": result.get("confidence_score", 0.7),
            "rules_used": result.get("rules_used", []),
            "impact": "high"
        }
    
    def _analyze_red_card(self, event: Dict) -> Dict:
        """Analyze a red card event"""
        player = event.get("player", "Unknown")
        team = event.get("team", "Unknown")
        reason = event.get("reason", "Unknown")
        
        prompt = f"""Analyze this red card incident:
Player: {player}
Team: {team}
Reason: {reason}
Time: {event.get('time', 'Unknown')}'

Explain the tactical implications of this red card for both teams."""
        
        analysis = self.granite_client.generate(prompt, max_tokens=200)
        
        return {
            "type": "red_card_analysis",
            "analysis": analysis,
            "impact": "critical"
        }
    
    def _analyze_penalty(self, event: Dict) -> Dict:
        """Analyze a penalty event"""
        team = event.get("team", "Unknown")
        awarded = event.get("awarded", True)
        
        prompt = f"""Analyze this penalty situation:
Team: {team}
Awarded: {awarded}
Time: {event.get('time', 'Unknown')}'
Description: {event.get('description', 'Penalty situation')}

Provide a brief analysis of this penalty decision."""
        
        analysis = self.granite_client.generate(prompt, max_tokens=150)
        
        return {
            "type": "penalty_analysis",
            "analysis": analysis,
            "impact": "high"
        }
    
    def get_momentum_analysis(self, period_minutes: int = 15) -> Dict:
        """
        Analyze momentum for recent period
        
        Args:
            period_minutes: Minutes to analyze
            
        Returns:
            Momentum analysis
        """
        if len(self.events) < 3:
            return {
                "momentum": "neutral",
                "analysis": "Not enough events to analyze momentum"
            }
        
        if self.match_data is None:
            return {
                "momentum": "neutral",
                "analysis": "Match data not available"
            }
        
        # Get recent events
        recent_events = self.events[-10:]  # Last 10 events
        
        # Count events by team
        home_events = len([e for e in recent_events if e.get("team") == self.match_data["home_team"]])
        away_events = len([e for e in recent_events if e.get("team") == self.match_data["away_team"]])
        
        # Determine momentum
        if home_events > away_events * 1.5:
            momentum = self.match_data["home_team"]
        elif away_events > home_events * 1.5:
            momentum = self.match_data["away_team"]
        else:
            momentum = "balanced"
        
        # Generate analysis
        match_context = {
            "home_team": self.match_data["home_team"],
            "away_team": self.match_data["away_team"],
            "score": f"{self.current_score['home']}-{self.current_score['away']}",
            "period": f"Last {period_minutes} minutes"
        }
        
        period_description = f"Recent period with {len(recent_events)} events"
        
        result = self.momentum_explainer.analyze_momentum_shift(
            match_data=match_context,
            time_period=f"Last {period_minutes} minutes",
            events=recent_events
        )
        
        return {
            "momentum": momentum,
            "analysis": result.get("explanation", ""),
            "recent_events": len(recent_events),
            "home_activity": home_events,
            "away_activity": away_events
        }
    
    def get_match_summary(self) -> Dict:
        """
        Get comprehensive match summary
        
        Returns:
            Match summary dictionary
        """
        if not self.match_data:
            return {"error": "No match data available"}
        
        # Count events by type
        event_counts = {}
        for event in self.events:
            event_type = event.get("type", "unknown")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Count cards by team
        home_yellows = len([e for e in self.events if e.get("type") == "yellow_card" and e.get("team") == self.match_data["home_team"]])
        away_yellows = len([e for e in self.events if e.get("type") == "yellow_card" and e.get("team") == self.match_data["away_team"]])
        home_reds = len([e for e in self.events if e.get("type") == "red_card" and e.get("team") == self.match_data["home_team"]])
        away_reds = len([e for e in self.events if e.get("type") == "red_card" and e.get("team") == self.match_data["away_team"]])
        
        return {
            "teams": f"{self.match_data['home_team']} vs {self.match_data['away_team']}",
            "score": f"{self.current_score['home']}-{self.current_score['away']}",
            "status": "finished" if self.match_ended else "in_progress",
            "total_events": len(self.events),
            "event_counts": event_counts,
            "cards": {
                "home": {"yellow": home_yellows, "red": home_reds},
                "away": {"yellow": away_yellows, "red": away_reds}
            },
            "var_reviews": event_counts.get("var_review", 0)
        }
    
    def get_timeline(self) -> List[Dict]:
        """
        Get match timeline
        
        Returns:
            List of events with timestamps
        """
        return self.events.copy()
    
    def export_match_data(self) -> Dict:
        """
        Export complete match data
        
        Returns:
            Complete match data dictionary
        """
        if not self.match_data:
            return {}
        
        export_data = self.match_data.copy()
        export_data["final_score"] = f"{self.current_score['home']}-{self.current_score['away']}"
        export_data["status"] = "finished" if self.match_ended else "in_progress"
        export_data["export_time"] = datetime.now().isoformat()
        
        return export_data


# Made with Bob