"""
Tests for ingestion/loader.py using an in-memory SQLite database.

The loader auto-detects dialect and uses the SQLite code path, so these
tests run in CI without any PostgreSQL instance.
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from database.models import Base, GitHubEvent, HackerNewsStory, IngestionLog
from database.connection import _engine, _SessionLocal
import database.connection as db_conn
from ingestion.loader import upsert_github_events, upsert_hn_stories, log_ingestion


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def sqlite_db(monkeypatch):
    """
    Patch the global engine/session to an in-memory SQLite database.
    Each test gets a fresh schema.
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    monkeypatch.setattr(db_conn, "_engine", engine)
    monkeypatch.setattr(db_conn, "_SessionLocal", Session)
    yield engine


# ── GitHub Events ─────────────────────────────────────────────────────────────

GITHUB_RECORDS = [
    {
        "event_id": "gh_001",
        "event_type": "PushEvent",
        "actor_login": "alice",
        "repo_name": "alice/project",
        "created_at": datetime(2024, 1, 15, 10, 0),
    },
    {
        "event_id": "gh_002",
        "event_type": "WatchEvent",
        "actor_login": "bob",
        "repo_name": "bob/repo",
        "created_at": datetime(2024, 1, 15, 11, 0),
    },
]


def test_upsert_github_events_inserts_new_records():
    counts = upsert_github_events(GITHUB_RECORDS)
    assert counts["inserted"] == 2
    assert counts["skipped"] == 0


def test_upsert_github_events_skips_duplicates():
    upsert_github_events(GITHUB_RECORDS)
    counts = upsert_github_events(GITHUB_RECORDS)  # same records again
    assert counts["inserted"] == 0
    assert counts["skipped"] == 2


def test_upsert_github_events_partial_duplicate():
    upsert_github_events([GITHUB_RECORDS[0]])
    new_record = {
        "event_id": "gh_003",
        "event_type": "ForkEvent",
        "actor_login": "carol",
        "repo_name": "carol/fork",
    }
    counts = upsert_github_events([GITHUB_RECORDS[0], new_record])
    assert counts["inserted"] == 1
    assert counts["skipped"] == 1


def test_upsert_github_events_empty_input():
    counts = upsert_github_events([])
    assert counts["inserted"] == 0
    assert counts["skipped"] == 0


# ── HN Stories ────────────────────────────────────────────────────────────────

HN_RECORDS = [
    {
        "hn_id": 42001,
        "title": "Ask HN: Learning data engineering",
        "score": 300,
        "author": "techuser",
        "comment_count": 80,
        "story_type": "ask",
    },
    {
        "hn_id": 42002,
        "title": "PostgreSQL 17 Released",
        "url": "https://postgresql.org",
        "score": 700,
        "author": "dbfan",
        "comment_count": 200,
        "story_type": "story",
    },
]


def test_upsert_hn_stories_inserts_new_records():
    counts = upsert_hn_stories(HN_RECORDS)
    assert counts["inserted"] == 2
    assert counts["skipped"] == 0


def test_upsert_hn_stories_updates_existing_score():
    upsert_hn_stories(HN_RECORDS)
    updated = [{**HN_RECORDS[0], "score": 999, "comment_count": 150}]
    counts = upsert_hn_stories(updated)
    # In SQLite path, existing record is updated → counts as skipped (not re-inserted)
    assert counts["skipped"] == 1
    assert counts["inserted"] == 0


def test_upsert_hn_stories_empty_input():
    counts = upsert_hn_stories([])
    assert counts["inserted"] == 0
    assert counts["skipped"] == 0


# ── Ingestion Log ─────────────────────────────────────────────────────────────

def test_log_ingestion_writes_row(sqlite_db):
    log_ingestion(
        pipeline="test_pipe",
        source="test_src",
        records_fetched=100,
        records_inserted=90,
        records_skipped=10,
        status="success",
    )
    Session = sessionmaker(bind=sqlite_db)
    with Session() as session:
        row = session.query(IngestionLog).filter_by(pipeline="test_pipe").first()
    assert row is not None
    assert row.status == "success"
    assert row.records_inserted == 90


def test_log_ingestion_writes_failure_row(sqlite_db):
    log_ingestion(
        pipeline="broken_pipe",
        source="api",
        records_fetched=0,
        records_inserted=0,
        records_skipped=0,
        status="failed",
        error_message="Connection timeout",
    )
    Session = sessionmaker(bind=sqlite_db)
    with Session() as session:
        row = session.query(IngestionLog).filter_by(pipeline="broken_pipe").first()
    assert row.status == "failed"
    assert "timeout" in row.error_message.lower()
