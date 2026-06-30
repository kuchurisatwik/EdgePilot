"""Engine, session factory and the FastAPI ``get_db`` dependency."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models.base import Base  # re-exported for convenience

__all__ = ["Base", "engine", "SessionLocal", "get_db"]

engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Iterator[Session]:
    """Yield a request-scoped session; always closed afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
