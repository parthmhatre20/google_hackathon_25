from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Google Cloud
    google_credentials_path: str = ""
    google_project_id: str = ""
    
    # Gemini API
    gemini_api_key: str = ""
    
    # Firebase
    firebase_credentials_path: str = ""
    
    # Application
    environment: str = "development"
    debug: bool = True
    allowed_origins: str = "http://localhost:3000,http://localhost:8080"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

settings = Settings()