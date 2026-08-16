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

    # Held as a string, not a list, on purpose.
    #
    # pydantic-settings parses any list-typed field as JSON before validators
    # run, so a value like https://example.com fails at import time with a JSON
    # decode error that says nothing about the real problem. Accepting a plain
    # string and splitting it ourselves means both formats work.
    CORS_ORIGINS: str = "http://localhost:5173"

    # Below this response rate a department's score is published but flagged.
    RELIABLE_RESPONSE_RATE: float = 60.0
    MINIMUM_RESPONSE_RATE: float = 40.0

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    @property
    def cors_origins(self) -> List[str]:
        """
        The allowed origins, however they were written.

        Accepts a JSON array, a comma-separated list, or a single URL, and
        strips trailing slashes because a browser sends the origin without one
        and a mismatch there blocks every request with no useful error.
        """
        raw = (self.CORS_ORIGINS or "").strip()
        if not raw:
            return []

        if raw.startswith("["):
            import json

            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(o).strip().rstrip("/") for o in parsed if str(o).strip()]
            except json.JSONDecodeError:
                raw = raw.strip("[]")

        return [part.strip().strip('"').strip("'").rstrip("/") for part in raw.split(",") if part.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached so the environment is read once per process."""
    return Settings()


settings = get_settings()