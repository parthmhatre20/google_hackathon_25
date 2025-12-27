from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Google Cloud
    google_credentials_path: str = ""
    google_project_id: str = ""
    
    # Gemini API
    gemini_api_key: str = ""
    gemini_api_keys: str = ""  # Comma-separated list of API keys for rotation
    
    # Firebase
    firebase_credentials_path: str = ""
    
    # Flask Frontend
    flask_secret_key: str = "dev-secret-key-change-in-production"
    
    # Application
    environment: str = "development"
    debug: bool = True
    allowed_origins: str = "http://localhost:3000,http://localhost:8080,http://localhost:5000,http://127.0.0.1:5000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    def get_api_keys_list(self) -> list:
        """Get list of all API keys for rotation"""
        keys = []
        
        # Add keys from GEMINI_API_KEYS (comma-separated)
        if self.gemini_api_keys:
            keys.extend([k.strip() for k in self.gemini_api_keys.split(',') if k.strip()])
        
        # Add single key from GEMINI_API_KEY if not already in list
        if self.gemini_api_key and self.gemini_api_key not in keys:
            keys.append(self.gemini_api_key)
        
        return keys

settings = Settings()