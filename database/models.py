"""
SQLAlchemy ORM models for PipeOne raw/staging tables.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text,
    DateTime, Boolean, Float, Index, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class GitHubEvent(Base):
    """Raw GitHub public events."""
    __tablename__ = "github_events_raw"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), nullable=False, unique=True)
    event_type = Column(String(64), nullable=False)
    actor_id = Column(BigInteger, nullable=True)
    actor_login = Column(String(255), nullable=True)
    repo_id = Column(BigInteger, nullable=True)
    repo_name = Column(String(512), nullable=True)
    public = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=True)
    payload_size = Column(Integer, nullable=True)
    ingested_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_github_events_created_at", "created_at"),
        Index("ix_github_events_actor_login", "actor_login"),
        Index("ix_github_events_event_type", "event_type"),
    )


class GitHubRepo(Base):
    """Deduplicated repository metadata from events."""
    __tablename__ = "github_repos_raw"

    id = Column(Integer, primary_key=True, autoincrement=True)
    repo_id = Column(BigInteger, nullable=False, unique=True)
    repo_name = Column(String(512), nullable=False)
    owner = Column(String(255), nullable=True)
    language = Column(String(64), nullable=True)
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    open_issues = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    html_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    ingested_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_github_repos_name", "repo_name"),
    )


class HackerNewsStory(Base):
    """Raw Hacker News top stories."""
    __tablename__ = "hn_stories_raw"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hn_id = Column(BigInteger, nullable=False, unique=True)
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=True)
    score = Column(Integer, default=0)
    author = Column(String(255), nullable=True)
    comment_count = Column(Integer, default=0)
    story_type = Column(String(32), default="story")
    time_posted = Column(DateTime, nullable=True)
    ingested_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_hn_stories_score", "score"),
        Index("ix_hn_stories_time", "time_posted"),
    )


class IngestionLog(Base):
    """Audit log for every pipeline run."""
    __tablename__ = "ingestion_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline = Column(String(64), nullable=False)
    source = Column(String(64), nullable=False)
    records_fetched = Column(Integer, default=0)
    records_inserted = Column(Integer, default=0)
    records_skipped = Column(Integer, default=0)
    status = Column(String(32), default="running")
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_ingestion_log_pipeline", "pipeline"),
        Index("ix_ingestion_log_status", "status"),
    )
