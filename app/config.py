from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """Main application settings."""

    # JWT Settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    cookie_name: str = "access_token"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str
    db_echo: bool = False

    # FastAPI
    app_name: str = "FastAPI Lab 4"
    app_version: str = "1.0.0"

    # API
    api_prefix: str = "/api/v1"

    # Session
    session_expire_minutes: int = 30

@lru_cache()
def get_settings() -> Settings:
    """Single instance cache for settings."""
    return Settings()