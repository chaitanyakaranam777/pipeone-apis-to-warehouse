"""Integration tests for database models and connection (uses SQLite for CI)."""
import pytest
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from database.models import Base, GitHubEvent, HackerNewsStory, IngestionLog


@pytest.fixture(scope="module")
def sqlite_session():
    """In-memory SQLite session for DB tests (no Postgres needed)."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_github_event_insert(sqlite_session):
    ev = GitHubEvent(
        event_id="test_001",
        event_type="PushEvent",
        actor_login="alice",
        repo_name="alice/repo",
        created_at=datetime.utcnow(),
    )
    sqlite_session.add(ev)
    sqlite_session.commit()
    result = sqlite_session.query(GitHubEvent).filter_by(event_id="test_001").first()
    assert result is not None
    assert result.actor_login == "alice"


def test_github_event_unique_constraint(sqlite_session):
    ev1 = GitHubEvent(event_id="dup_001", event_type="PushEvent")
    ev2 = GitHubEvent(event_id="dup_001", event_type="WatchEvent")
    sqlite_session.add(ev1)
    sqlite_session.commit()
    sqlite_session.add(ev2)
    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError):
        sqlite_session.commit()
    sqlite_session.rollback()


def test_hn_story_insert(sqlite_session):
    story = HackerNewsStory(
        hn_id=99001,
        title="Test Story About Python",
        score=250,
        author="testuser",
        comment_count=45,
    )
    sqlite_session.add(story)
    sqlite_session.commit()
    result = sqlite_session.query(HackerNewsStory).filter_by(hn_id=99001).first()
    assert result.title == "Test Story About Python"
    assert result.score == 250


def test_ingestion_log_insert(sqlite_session):
    log = IngestionLog(
        pipeline="test_pipeline",
        source="test_source",
        records_fetched=100,
        records_inserted=95,
        records_skipped=5,
        status="success",
        finished_at=datetime.utcnow(),
    )
    sqlite_session.add(log)
    sqlite_session.commit()
    result = sqlite_session.query(IngestionLog).filter_by(pipeline="test_pipeline").first()
    assert result.status == "success"
    assert result.records_inserted == 95


def test_sqlite_connection_works(sqlite_session):
    result = sqlite_session.execute(text("SELECT 1")).fetchone()
    assert result[0] == 1
