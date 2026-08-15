"""Database engine and session handling."""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

def _engine_options(url: str) -> dict:
    """SQLite needs different arguments, and the test suite runs on it."""
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    # Neon and most managed Postgres close idle connections; this reconnects quietly.
    return {"pool_pre_ping": True}


engine = create_engine(settings.DATABASE_URL, future=True, **_engine_options(settings.DATABASE_URL))

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency. One session per request, always closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
