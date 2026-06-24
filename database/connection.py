"""
Database connection factory and session management.
"""
import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from configs.settings import settings
from database.models import Base

logger = logging.getLogger(__name__)


def get_engine(url: str | None = None):
    """Create SQLAlchemy engine with connection pooling."""
    db_url = url or settings.db.url
    engine = create_engine(
        db_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=False,
    )
    return engine


_engine = None
_SessionLocal = None


def init_db(url: str | None = None) -> None:
    """Initialize engine and create all tables."""
    global _engine, _SessionLocal
    _engine = get_engine(url)
    _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(_engine)
    logger.info("Database initialized and tables created.")


def get_session() -> Session:
    """Return a new session (caller must close it)."""
    if _SessionLocal is None:
        init_db()
    return _SessionLocal()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional session context manager."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def health_check() -> bool:
    """Return True if the database is reachable."""
    try:
        with session_scope() as session:
            session.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error(f"DB health check failed: {exc}")
        return False
