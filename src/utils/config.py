"""
Configuration management for MatchLens AI
Loads environment variables and application settings
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # Hugging Face Configuration
    huggingface_token: str = os.getenv("HUGGINGFACE_TOKEN", "")
    
    # IBM Granite Model Configuration
    # Primary: granite-3.0-8b-instruct (recommended for Inference API)
    # Fallback: granite-3.3-8b-instruct or granite-20b-code-instruct
    granite_model_id: str = os.getenv("GRANITE_MODEL_ID", "ibm-granite/granite-3.0-8b-instruct")
    
    # Alternative Granite models (in order of preference)
    granite_fallback_models: list = [
        "ibm-granite/granite-3.0-8b-instruct",
        "ibm-granite/granite-8b-code-instruct",
        "ibm-granite/granite-20b-code-instruct-8k",
        "ibm-granite/granite-3.3-8b-instruct"
    ]
    
    # Application Settings
    app_title: str = os.getenv("APP_TITLE", "MatchLens AI")
    app_icon: str = os.getenv("APP_ICON", "⚽")
    debug_mode: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"
    
    # Vector Database Settings
    vector_db_path: str = os.getenv("VECTOR_DB_PATH", "./data/vector_db")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Match Data Settings
    match_data_path: str = os.getenv("MATCH_DATA_PATH", "./data/matches")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def validate_huggingface_config(self) -> tuple[bool, str]:
        """
        Validate Hugging Face configuration
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.huggingface_token:
            return False, "HUGGINGFACE_TOKEN is not set in .env file. Please add your Hugging Face token."
        
        if not self.huggingface_token.startswith("hf_"):
            return False, "HUGGINGFACE_TOKEN appears to be invalid. It should start with 'hf_'."
        
        if not self.granite_model_id:
            return False, "GRANITE_MODEL_ID is not set in .env file."
        
        # Check if it's a Granite model
        if "granite" not in self.granite_model_id.lower():
            return False, f"Model '{self.granite_model_id}' does not appear to be a Granite model. Please use an IBM Granite model."
        
        return True, ""
    
    def get_granite_model_info(self) -> dict:
        """
        Get information about the configured Granite model
        
        Returns:
            Dictionary with model information
        """
        model_info = {
            "model_id": self.granite_model_id,
            "is_granite": "granite" in self.granite_model_id.lower(),
            "is_ibm": "ibm" in self.granite_model_id.lower(),
            "model_type": "unknown"
        }
        
        # Determine model type
        if "code" in self.granite_model_id.lower():
            model_info["model_type"] = "code"
        elif "instruct" in self.granite_model_id.lower():
            model_info["model_type"] = "instruct"
        elif "chat" in self.granite_model_id.lower():
            model_info["model_type"] = "chat"
        
        return model_info

def load_config() -> Settings:
    """Load and return application configuration"""
    config = Settings()
    
    # Validate configuration if debug mode is enabled
    if config.debug_mode:
        is_valid, error_msg = config.validate_huggingface_config()
        if not is_valid:
            print(f"⚠️  Configuration Warning: {error_msg}")
        else:
            model_info = config.get_granite_model_info()
            print(f"✅ Configuration valid")
            print(f"   Model: {model_info['model_id']}")
            print(f"   Type: {model_info['model_type']}")
    
    return config

def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent.parent

def ensure_directories():
    """Ensure required directories exist"""
    root = get_project_root()
    directories = [
        root / "data" / "vector_db",
        root / "data" / "matches",
        root / "logs"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Made with Bob