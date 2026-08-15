"""Application settings, read from the environment."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "RAK Properties AI Adoption Index"
    API_V1: str = "/api/v1"

    # Postgres. Neon works well here and has a free tier.
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/rak_ai"

    # Auth. Must be overridden in production.
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8

    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # Below this response rate a department's score is published but flagged.
    RELIABLE_RESPONSE_RATE: float = 60.0
    MINIMUM_RESPONSE_RATE: float = 40.0

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


@lru_cache
def get_settings() -> Settings:
    """Cached so the environment is read once per process."""
    return Settings()


settings = get_settings()
