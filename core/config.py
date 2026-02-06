"""
Configuration management using Pydantic Settings.
Handles all environment variables and application settings.
"""
from typing import Literal
from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.
    
    All settings are loaded from environment variables with case-sensitive parsing.
    Configuration is loaded from .env file if present.
    """
    
    # ============================================================================
    # Project Information
    # ============================================================================
    PROJECT_NAME: str = Field(
        default="Harezmi Intelligence",
        description="Project name"
    )
    API_V1_STR: str = Field(
        default="/api/v1",
        description="API v1 prefix"
    )
    VERSION: str = Field(
        default="1.0.0",
        description="API version"
    )
    
    # ============================================================================
    # Environment
    # ============================================================================
    ENV: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Environment"
    )
    DEBUG: bool = Field(
        default=True,
        description="Debug mode"
    )
    
    # ============================================================================
    # Database Configuration (PostgreSQL + PostGIS + pgvector)
    # ============================================================================
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql+asyncpg://harezmi:harezmi_dev_password@127.0.0.1:5433/harezmi_dev",
        description="Async PostgreSQL connection string (postgresql+asyncpg://)"
    )
    
    # Connection pool settings
    DB_POOL_SIZE: int = Field(
        default=20,
        description="Database connection pool size"
    )
    DB_MAX_OVERFLOW: int = Field(
        default=10,
        description="Maximum overflow connections"
    )
    DB_POOL_TIMEOUT: int = Field(
        default=30,
        description="Pool connection timeout in seconds"
    )
    DB_POOL_RECYCLE: int = Field(
        default=3600,
        description="Connection recycle time in seconds"
    )
    DB_ECHO: bool = Field(
        default=False,
        description="Echo SQL queries (debug)"
    )
    
    # ============================================================================
    # Redis Configuration
    # ============================================================================
    REDIS_URL: RedisDsn = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string"
    )
    
    # ============================================================================
    # Security & Authentication
    # ============================================================================
    SECRET_KEY: str = Field(
        default="your-secret-key-change-this-in-production-minimum-32-characters",
        description="Secret key for JWT encoding/decoding"
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Refresh token expiration in days"
    )
    
    # ============================================================================
    # External Services
    # ============================================================================
    GROQ_API_KEY: str | None = Field(
        default=None,
        description="Groq API key for LLM services"
    )
    
    # ============================================================================
    # CORS Configuration
    # ============================================================================
    CORS_ORIGINS: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ],
        description="Allowed CORS origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Allow credentials in CORS"
    )
    CORS_ALLOW_METHODS: list[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        description="Allowed HTTP methods"
    )
    CORS_ALLOW_HEADERS: list[str] = Field(
        default=["*"],
        description="Allowed headers"
    )
    
    # ============================================================================
    # Logging
    # ============================================================================
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    LOG_FORMAT: Literal["json", "text"] = Field(
        default="json",
        description="Log format"
    )
    
    # ============================================================================
    # Feature Flags
    # ============================================================================
    ENABLE_CACHE: bool = Field(
        default=True,
        description="Enable Redis caching"
    )
    ENABLE_VECTOR_SEARCH: bool = Field(
        default=True,
        description="Enable pgvector search"
    )
    ENABLE_GEOSPATIAL_QUERIES: bool = Field(
        default=True,
        description="Enable PostGIS queries"
    )
    
    # ============================================================================
    # Pydantic Configuration
    # ============================================================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,  # Case-sensitive environment variables
        extra="ignore",  # Ignore extra fields
    )


# Global settings instance
settings = Settings()
