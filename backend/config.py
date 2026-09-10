import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    APP_NAME: str = "Price Comparison API"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database
    DATABASE_URL: str = "sqlite:///./comparison.db"

    # Scrapers
    SELENIUM_HEADLESS: bool = False
    SELENIUM_TIMEOUT: int = 100  # seconds
    MOCK_FALLBACK: bool = False   # fallback to mock items if scrapers are blocked or fail
    
    # Matching
    MATCHING_THRESHOLD: float = 75.0  # RapidFuzz similarity threshold (0-100)
    CACHE_EXPIRY_SECONDS: int = 3600  # 1 hour cache for scraped results

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
