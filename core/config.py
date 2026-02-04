"""
Ayarların yönetimi
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Uygulama ayarları"""
    
    # Veritabanı
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/mergenx")
    
    # API
    API_TITLE: str = "MergenX API"
    API_VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    class Config:
        env_file = ".env"


settings = Settings()
