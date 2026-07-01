"""
Integration tests for database models and connection.
Uses SQLite in-memory — no PostgreSQL required.
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from database.models import Base, GitHubEvent, HackerNewsStory, IngestionLog


@pytest.fixture(scope="module")
def sqlite_session():
    """Shared in-memory SQLite session for all DB tests."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


# ── GitHubEvent ───────────────────────────────────────────────────────────────

def test_github_event_insert(sqlite_session):
    ev = GitHubEvent(
        event_id="db_test_001",
        event_type="PushEvent",
        actor_login="alice",
        repo_name="alice/repo",
        created_at=datetime.now(tz=timezone.utc),
    )
    sqlite_session.add(ev)
    sqlite_session.commit()
    result = sqlite_session.query(GitHubEvent).filter_by(event_id="db_test_001").first()
    assert result is not None
    assert result.actor_login == "alice"
    assert result.event_type == "PushEvent"


def test_github_event_unique_constraint(sqlite_session):
    """Inserting duplicate event_id must raise IntegrityError."""
    ev1 = GitHubEvent(event_id="dup_db_001", event_type="PushEvent")
    ev2 = GitHubEvent(event_id="dup_db_001", event_type="WatchEvent")
    sqlite_session.add(ev1)
    sqlite_session.commit()
    sqlite_session.add(ev2)
    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError):
        sqlite_session.commit()
    sqlite_session.rollback()


def test_github_event_optional_fields(sqlite_session):
    """Event must be insertable with only required fields."""
    ev = GitHubEvent(event_id="minimal_001", event_type="CreateEvent")
    sqlite_session.add(ev)
    sqlite_session.commit()
    result = sqlite_session.query(GitHubEvent).filter_by(event_id="minimal_001").first()
    assert result is not None
    assert result.actor_login is None


# ── HackerNewsStory ───────────────────────────────────────────────────────────

def test_hn_story_insert(sqlite_session):
    story = HackerNewsStory(
        hn_id=99001,
        title="Test Story About Python and dbt",
        score=250,
        author="testuser",
        comment_count=45,
    )
    sqlite_session.add(story)
    sqlite_session.commit()
    result = sqlite_session.query(HackerNewsStory).filter_by(hn_id=99001).first()
    assert result.title == "Test Story About Python and dbt"
    assert result.score == 250
    assert result.comment_count == 45


def test_hn_story_unique_constraint(sqlite_session):
    s1 = HackerNewsStory(hn_id=99999, title="First")
    s2 = HackerNewsStory(hn_id=99999, title="Duplicate")
    sqlite_session.add(s1)
    sqlite_session.commit()
    sqlite_session.add(s2)
    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError):
        sqlite_session.commit()
    sqlite_session.rollback()


# ── IngestionLog ──────────────────────────────────────────────────────────────

def test_ingestion_log_insert(sqlite_session):
    log = IngestionLog(
        pipeline="test_pipeline",
        source="test_source",
        records_fetched=100,
        records_inserted=95,
        records_skipped=5,
        status="success",
        finished_at=datetime.now(tz=timezone.utc),
    )
    sqlite_session.add(log)
    sqlite_session.commit()
    result = sqlite_session.query(IngestionLog).filter_by(pipeline="test_pipeline").first()
    assert result.status == "success"
    assert result.records_inserted == 95


def test_ingestion_log_failure_entry(sqlite_session):
    log = IngestionLog(
        pipeline="failing_pipeline",
        source="bad_api",
        records_fetched=0,
        records_inserted=0,
        records_skipped=0,
        status="failed",
        error_message="Connection refused after 3 retries",
        finished_at=datetime.now(tz=timezone.utc),
    )
    sqlite_session.add(log)
    sqlite_session.commit()
    result = sqlite_session.query(IngestionLog).filter_by(pipeline="failing_pipeline").first()
    assert result.status == "failed"
    assert "refused" in result.error_message


# ── Connection ────────────────────────────────────────────────────────────────

def test_sqlite_connection_works(sqlite_session):
    result = sqlite_session.execute(text("SELECT 1")).fetchone()
    assert result[0] == 1


def test_all_tables_created(sqlite_session):
    """All four ORM tables must be present in the schema."""
    tables = {row[0] for row in sqlite_session.execute(
        text("SELECT name FROM sqlite_master WHERE type='table'")
    ).fetchall()}
    assert "github_events_raw" in tables
    assert "hn_stories_raw" in tables
    assert "ingestion_log" in tables
