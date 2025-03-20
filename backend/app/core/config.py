from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Document Classification"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "doc_classifier")
    SQLALCHEMY_DATABASE_URI: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".txt", ".pdf", ".docx"]
    
    # ML Model
    MODEL_NAME: str = "facebook/bart-large-mnli"
    CLASSIFICATION_CATEGORIES: List[str] = [
        "Technical Documentation",
        "Business Proposal",
        "Legal Document",
        "Academic Paper",
        "General Article",
        "Other"
    ]
    # Confidence thresholds
    CONFIDENCE_THRESHOLDS: dict = {
        "high": 0.60,    # Green: 60% and above
        "medium": 0.35,  # Yellow: 35-60%
        "low": 0.20      # Red: Below 35%
    }
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    class Config:
        case_sensitive = True

settings = Settings() 