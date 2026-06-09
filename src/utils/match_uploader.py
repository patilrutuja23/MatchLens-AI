"""
Match File Uploader
Handles file uploads and processing for MatchLens AI
"""

import json
from typing import Dict, Optional, Tuple, List
from pathlib import Path
from datetime import datetime
from src.utils.validation import validate_json_file, validate_csv_file


class MatchUploader:
    """Handles match file uploads and validation"""
    
    SUPPORTED_FORMATS = [".json", ".csv"]
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    
    def __init__(self, upload_dir: str = "./data/matches/uploaded"):
        """
        Initialize match uploader
        
        Args:
            upload_dir: Directory to store uploaded files
        """
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def process_upload(
        self,
        file_content: bytes,
        filename: str
    ) -> Tuple[bool, Optional[Dict], List[str], List[str]]:
        """
        Process uploaded file
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Tuple of (success, match_data, errors, warnings)
        """
        errors = []
        warnings = []
        
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.SUPPORTED_FORMATS:
            errors.append(
                f"Unsupported file format: {file_ext}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )
            return False, None, errors, warnings
        
        # Check file size
        file_size = len(file_content)
        if file_size > self.MAX_FILE_SIZE:
            errors.append(
                f"File too large: {file_size / 1024 / 1024:.2f} MB. "
                f"Maximum size: {self.MAX_FILE_SIZE / 1024 / 1024:.0f} MB"
            )
            return False, None, errors, warnings
        
        if file_size == 0:
            errors.append("File is empty")
            return False, None, errors, warnings
        
        # Decode file content
        try:
            content_str = file_content.decode('utf-8')
        except UnicodeDecodeError:
            errors.append("File encoding error. Please use UTF-8 encoding.")
            return False, None, errors, warnings
        
        # Validate based on file type
        if file_ext == ".json":
            is_valid, match_data, val_errors, val_warnings = validate_json_file(content_str)
        elif file_ext == ".csv":
            is_valid, match_data, val_errors, val_warnings = validate_csv_file(content_str)
        else:
            errors.append(f"Unsupported file type: {file_ext}")
            return False, None, errors, warnings
        
        errors.extend(val_errors)
        warnings.extend(val_warnings)
        
        # Save file if valid
        if is_valid and match_data:
            saved_path = self._save_uploaded_file(content_str, filename, match_data)
            if saved_path:
                match_data["_uploaded_file"] = str(saved_path)
                match_data["_upload_time"] = datetime.now().isoformat()
        
        return is_valid, match_data, errors, warnings
    
    def _save_uploaded_file(
        self,
        content: str,
        original_filename: str,
        match_data: Dict
    ) -> Optional[Path]:
        """
        Save uploaded file to disk
        
        Args:
            content: File content
            original_filename: Original filename
            match_data: Parsed match data
            
        Returns:
            Path to saved file or None
        """
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            home = match_data.get("home_team", "team1").replace(" ", "_")
            away = match_data.get("away_team", "team2").replace(" ", "_")
            
            file_ext = Path(original_filename).suffix
            new_filename = f"{timestamp}_{home}_vs_{away}{file_ext}"
            
            save_path = self.upload_dir / new_filename
            
            # Save as JSON for consistency
            json_path = save_path.with_suffix('.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(match_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved uploaded match to: {json_path}")
            return json_path
            
        except Exception as e:
            print(f"❌ Failed to save uploaded file: {e}")
            return None
    
    def get_match_preview(self, match_data: Dict) -> Dict:
        """
        Generate preview information for match data
        
        Args:
            match_data: Match data dictionary
            
        Returns:
            Preview information dictionary
        """
        preview = {
            "teams": f"{match_data.get('home_team', 'Unknown')} vs {match_data.get('away_team', 'Unknown')}",
            "score": match_data.get("score", "N/A"),
            "date": match_data.get("date", "N/A"),
            "competition": match_data.get("competition", "N/A"),
            "total_events": len(match_data.get("events", [])),
            "event_summary": {}
        }
        
        # Count events by type
        events = match_data.get("events", [])
        for event in events:
            event_type = event.get("type", "unknown")
            preview["event_summary"][event_type] = preview["event_summary"].get(event_type, 0) + 1
        
        # Calculate goals
        goals = [e for e in events if e.get("type") == "goal"]
        home_goals = len([g for g in goals if g.get("team") == match_data.get("home_team")])
        away_goals = len([g for g in goals if g.get("team") == match_data.get("away_team")])
        
        if not match_data.get("score"):
            preview["calculated_score"] = f"{home_goals}-{away_goals}"
        
        # Count cards
        yellow_cards = len([e for e in events if e.get("type") == "yellow_card"])
        red_cards = len([e for e in events if e.get("type") == "red_card"])
        
        preview["cards"] = {
            "yellow": yellow_cards,
            "red": red_cards
        }
        
        # VAR reviews
        var_reviews = len([e for e in events if e.get("type") == "var_review"])
        preview["var_reviews"] = var_reviews
        
        return preview
    
    def list_uploaded_matches(self) -> List[Dict]:
        """
        List all uploaded match files
        
        Returns:
            List of match file information
        """
        matches = []
        
        if not self.upload_dir.exists():
            return matches
        
        for json_file in self.upload_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    match_data = json.load(f)
                
                matches.append({
                    "filename": json_file.name,
                    "path": str(json_file),
                    "teams": f"{match_data.get('home_team', 'Unknown')} vs {match_data.get('away_team', 'Unknown')}",
                    "date": match_data.get("date", "N/A"),
                    "upload_time": match_data.get("_upload_time", "N/A")
                })
            except Exception as e:
                print(f"⚠️  Error reading {json_file.name}: {e}")
        
        # Sort by upload time (newest first)
        matches.sort(key=lambda x: x.get("upload_time", ""), reverse=True)
        
        return matches
    
    def load_match_file(self, filepath: str) -> Optional[Dict]:
        """
        Load a match file
        
        Args:
            filepath: Path to match file
            
        Returns:
            Match data or None
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading match file: {e}")
            return None


# Made with Bob