from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///:memory:"
    
    
    # JWT Settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # App Settings
    APP_NAME: str = "FoodHub API"
    DEBUG: bool = True
    
    # Default Admin
    ADMIN_EMAIL: str = "admin@foodhub.com"
    ADMIN_PASSWORD: str = "admin123"

    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://food-ordering-system-1-b7m1.onrender.com"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()