"""
Match Data Validation
Validates uploaded match data for MatchLens AI
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json


class MatchValidator:
    """Validates match data structure and content"""
    
    # Required fields for match data
    REQUIRED_FIELDS = ["home_team", "away_team", "events"]
    
    # Valid event types
    VALID_EVENT_TYPES = [
        "goal", "yellow_card", "red_card", "substitution",
        "corner", "penalty", "var_review", "kickoff", "halftime", "fulltime"
    ]
    
    # Required fields for events
    EVENT_REQUIRED_FIELDS = ["type", "time", "team"]
    
    def __init__(self):
        """Initialize validator"""
        self.errors = []
        self.warnings = []
    
    def validate_match_data(self, data: Dict) -> Tuple[bool, List[str], List[str]]:
        """
        Validate complete match data
        
        Args:
            data: Match data dictionary
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        # Check required fields
        self._validate_required_fields(data)
        
        # Validate team names
        self._validate_teams(data)
        
        # Validate events
        if "events" in data:
            self._validate_events(data["events"])
        
        # Validate optional fields
        self._validate_optional_fields(data)
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _validate_required_fields(self, data: Dict):
        """Check if all required fields are present"""
        for field in self.REQUIRED_FIELDS:
            if field not in data:
                self.errors.append(f"Missing required field: '{field}'")
            elif data[field] is None:
                self.errors.append(f"Field '{field}' cannot be null")
    
    def _validate_teams(self, data: Dict):
        """Validate team information"""
        if "home_team" in data:
            if not isinstance(data["home_team"], str):
                self.errors.append("'home_team' must be a string")
            elif not data["home_team"].strip():
                self.errors.append("'home_team' cannot be empty")
        
        if "away_team" in data:
            if not isinstance(data["away_team"], str):
                self.errors.append("'away_team' must be a string")
            elif not data["away_team"].strip():
                self.errors.append("'away_team' cannot be empty")
        
        # Check if teams are different
        if "home_team" in data and "away_team" in data:
            if data["home_team"] == data["away_team"]:
                self.errors.append("'home_team' and 'away_team' must be different")
    
    def _validate_events(self, events: List[Dict]):
        """Validate events list"""
        if not isinstance(events, list):
            self.errors.append("'events' must be a list")
            return
        
        if len(events) == 0:
            self.warnings.append("No events found in match data")
            return
        
        for i, event in enumerate(events):
            self._validate_single_event(event, i)
    
    def _validate_single_event(self, event: Dict, index: int):
        """Validate a single event"""
        if not isinstance(event, dict):
            self.errors.append(f"Event {index} must be a dictionary")
            return
        
        # Check required event fields
        for field in self.EVENT_REQUIRED_FIELDS:
            if field not in event:
                self.errors.append(f"Event {index}: Missing required field '{field}'")
        
        # Validate event type
        if "type" in event:
            event_type = event["type"].lower() if isinstance(event["type"], str) else ""
            if event_type not in self.VALID_EVENT_TYPES:
                self.errors.append(
                    f"Event {index}: Invalid event type '{event['type']}'. "
                    f"Valid types: {', '.join(self.VALID_EVENT_TYPES)}"
                )
        
        # Validate time format
        if "time" in event:
            if not self._validate_time_format(event["time"]):
                self.errors.append(
                    f"Event {index}: Invalid time format '{event['time']}'. "
                    f"Expected format: '45' or '45+2' or '45:30'"
                )
        
        # Validate team
        if "team" in event:
            if not isinstance(event["team"], str):
                self.errors.append(f"Event {index}: 'team' must be a string")
        
        # Validate specific event types
        event_type = event.get("type", "").lower()
        if event_type == "goal":
            self._validate_goal_event(event, index)
        elif event_type in ["yellow_card", "red_card"]:
            self._validate_card_event(event, index)
        elif event_type == "substitution":
            self._validate_substitution_event(event, index)
        elif event_type == "var_review":
            self._validate_var_event(event, index)
    
    def _validate_time_format(self, time_str: str) -> bool:
        """Validate time format (e.g., '45', '45+2', '45:30')"""
        if not isinstance(time_str, str):
            return False
        
        # Remove any quotes or extra spaces
        time_str = str(time_str).strip().strip("'\"")
        
        # Check for formats: 45, 45+2, 45:30
        import re
        patterns = [
            r'^\d+$',           # 45
            r'^\d+\+\d+$',      # 45+2
            r'^\d+:\d+$'        # 45:30
        ]
        
        return any(re.match(pattern, time_str) for pattern in patterns)
    
    def _validate_goal_event(self, event: Dict, index: int):
        """Validate goal-specific fields"""
        if "player" not in event:
            self.warnings.append(f"Event {index}: Goal event missing 'player' field")
        
        if "assist" in event and not event["assist"]:
            self.warnings.append(f"Event {index}: Empty 'assist' field")
    
    def _validate_card_event(self, event: Dict, index: int):
        """Validate card-specific fields"""
        if "player" not in event:
            self.errors.append(f"Event {index}: Card event must have 'player' field")
        
        if "reason" not in event:
            self.warnings.append(f"Event {index}: Card event missing 'reason' field")
    
    def _validate_substitution_event(self, event: Dict, index: int):
        """Validate substitution-specific fields"""
        if "player_out" not in event:
            self.errors.append(f"Event {index}: Substitution missing 'player_out' field")
        
        if "player_in" not in event:
            self.errors.append(f"Event {index}: Substitution missing 'player_in' field")
    
    def _validate_var_event(self, event: Dict, index: int):
        """Validate VAR-specific fields"""
        if "decision_type" not in event:
            self.warnings.append(f"Event {index}: VAR event missing 'decision_type' field")
        
        if "initial_decision" not in event:
            self.warnings.append(f"Event {index}: VAR event missing 'initial_decision' field")
        
        if "final_decision" not in event:
            self.warnings.append(f"Event {index}: VAR event missing 'final_decision' field")
    
    def _validate_optional_fields(self, data: Dict):
        """Validate optional fields if present"""
        # Validate score
        if "score" in data:
            if not isinstance(data["score"], str):
                self.warnings.append("'score' should be a string (e.g., '2-1')")
        
        # Validate date
        if "date" in data:
            if not isinstance(data["date"], str):
                self.warnings.append("'date' should be a string")
        
        # Validate competition
        if "competition" in data:
            if not isinstance(data["competition"], str):
                self.warnings.append("'competition' should be a string")
        
        # Validate possession
        if "possession" in data:
            possession = data["possession"]
            if isinstance(possession, dict):
                if "home" in possession and "away" in possession:
                    home = possession["home"]
                    away = possession["away"]
                    if isinstance(home, (int, float)) and isinstance(away, (int, float)):
                        total = home + away
                        if abs(total - 100) > 1:  # Allow 1% tolerance
                            self.warnings.append(
                                f"Possession percentages should sum to 100 (got {total})"
                            )


def validate_json_file(file_content: str) -> Tuple[bool, Optional[Dict], List[str], List[str]]:
    """
    Validate JSON file content
    
    Args:
        file_content: JSON file content as string
        
    Returns:
        Tuple of (is_valid, parsed_data, errors, warnings)
    """
    errors = []
    warnings = []
    
    # Try to parse JSON
    try:
        data = json.loads(file_content)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON format: {str(e)}")
        return False, None, errors, warnings
    
    # Validate match data
    validator = MatchValidator()
    is_valid, val_errors, val_warnings = validator.validate_match_data(data)
    
    errors.extend(val_errors)
    warnings.extend(val_warnings)
    
    return is_valid, data, errors, warnings


def validate_csv_file(file_content: str) -> Tuple[bool, Optional[Dict], List[str], List[str]]:
    """
    Validate and convert CSV file content to match data
    
    Args:
        file_content: CSV file content as string
        
    Returns:
        Tuple of (is_valid, parsed_data, errors, warnings)
    """
    import csv
    from io import StringIO
    
    errors = []
    warnings = []
    
    try:
        # Parse CSV
        csv_reader = csv.DictReader(StringIO(file_content))
        rows = list(csv_reader)
        
        if len(rows) == 0:
            errors.append("CSV file is empty")
            return False, None, errors, warnings
        
        # Extract match info from first row
        first_row = rows[0]
        
        match_data = {
            "home_team": first_row.get("home_team", ""),
            "away_team": first_row.get("away_team", ""),
            "events": []
        }
        
        # Add optional fields
        if "score" in first_row:
            match_data["score"] = first_row["score"]
        if "date" in first_row:
            match_data["date"] = first_row["date"]
        if "competition" in first_row:
            match_data["competition"] = first_row["competition"]
        
        # Convert rows to events
        for row in rows:
            if "type" in row and "time" in row:
                event = {
                    "type": row["type"],
                    "time": row["time"],
                    "team": row.get("team", "")
                }
                
                # Add optional event fields
                for field in ["player", "assist", "reason", "player_out", "player_in",
                             "decision_type", "initial_decision", "final_decision", "description"]:
                    if field in row and row[field]:
                        event[field] = row[field]
                
                match_data["events"].append(event)
        
        # Validate converted data
        validator = MatchValidator()
        is_valid, val_errors, val_warnings = validator.validate_match_data(match_data)
        
        errors.extend(val_errors)
        warnings.extend(val_warnings)
        
        return is_valid, match_data, errors, warnings
        
    except Exception as e:
        errors.append(f"Error parsing CSV: {str(e)}")
        return False, None, errors, warnings


# Made with Bob