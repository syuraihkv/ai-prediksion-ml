"""
Configuration settings for FastAPI backend
Loads environment variables and provides configuration
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    API_TITLE: str = "AI Market Prediction API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/ai_prediction")
    
    # Redis Settings (for caching)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # API Keys
    COINMARKETCAP_API_KEY: str = os.getenv("COINMARKETCAP_API_KEY", "")
    COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")
    FRED_API_KEY: str = os.getenv("FRED_API_KEY", "")
    TWELVEDATA_API_KEY: str = os.getenv("TWELVEDATA_API_KEY", "")
    NEWS_DATA_API_KEY: str = os.getenv("NEWS_DATA_API_KEY", "")
    
    # Model Settings
    MODELS_DIR: str = "../data/models"
    
    # Cache Settings
    CACHE_TTL: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
