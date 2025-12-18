"""
Application configuration module.
Loads environment variables and provides configuration settings.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://tribal_user:tribal_pass@localhost:5432/tribal_knowledge_portal"

    # JWT Authentication
    JWT_SECRET: str = "your-secret-key-min-32-characters-long-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Application
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: List[str] = ["http://localhost:5777", "http://localhost:3000"]

    # Logging
    LOG_LEVEL: str = "INFO"

    # OpenAI API
    OPENAI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
