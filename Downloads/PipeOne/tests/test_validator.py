"""Unit tests for the data validation module."""
import pytest
from datetime import datetime
from ingestion.validator import validate_github_events, validate_hn_stories


# ── GitHub Events ─────────────────────────────────────────────────────────────

SAMPLE_EVENTS = [
    {
        "id": "1001",
        "type": "PushEvent",
        "actor": {"id": 1, "login": "alice"},
        "repo": {"id": 100, "name": "alice/myrepo"},
        "public": True,
        "created_at": "2024-01-15T10:00:00Z",
        "payload": {"commits": []},
    },
    {
        "id": "1002",
        "type": "WatchEvent",
        "actor": {"id": 2, "login": "bob"},
        "repo": {"id": 200, "name": "bob/otherrepo"},
        "public": True,
        "created_at": "2024-01-15T11:00:00Z",
        "payload": {},
    },
]


def test_validate_github_events_basic():
    cleaned, report = validate_github_events(SAMPLE_EVENTS)
    assert len(cleaned) == 2
    assert report.valid == 2
    assert report.invalid == 0


def test_validate_github_events_missing_id():
    bad = [{"type": "PushEvent", "actor": {}, "repo": {}, "public": True}]
    cleaned, report = validate_github_events(bad)
    assert len(cleaned) == 0
    assert report.invalid == 1


def test_validate_github_events_missing_type():
    bad = [{"id": "999", "actor": {}, "repo": {}, "public": True}]
    cleaned, report = validate_github_events(bad)
    assert len(cleaned) == 0
    assert report.invalid == 1


def test_validate_github_events_deduplication():
    duped = SAMPLE_EVENTS + [SAMPLE_EVENTS[0]]  # duplicate first event
    cleaned, report = validate_github_events(duped)
    assert len(cleaned) == 2
    assert report.duplicates_removed == 1


def test_validate_github_events_created_at_parsed():
    cleaned, _ = validate_github_events(SAMPLE_EVENTS)
    assert isinstance(cleaned[0]["created_at"], datetime)


def test_validate_github_events_empty():
    cleaned, report = validate_github_events([])
    assert cleaned == []
    assert report.total == 0


# ── HN Stories ────────────────────────────────────────────────────────────────

SAMPLE_STORIES = [
    {
        "id": 42001,
        "title": "Ask HN: How do you learn data engineering?",
        "url": None,
        "score": 350,
        "by": "techuser",
        "descendants": 120,
        "type": "ask",
        "time": 1705312800,
        "time_posted": datetime(2024, 1, 15, 10, 0),
    },
    {
        "id": 42002,
        "title": "PostgreSQL 17 Released",
        "url": "https://postgresql.org/news",
        "score": 800,
        "by": "dbfan",
        "descendants": 250,
        "type": "story",
        "time": 1705316400,
        "time_posted": datetime(2024, 1, 15, 11, 0),
    },
]


def test_validate_hn_stories_basic():
    cleaned, report = validate_hn_stories(SAMPLE_STORIES)
    assert len(cleaned) == 2
    assert report.valid == 2
    assert report.invalid == 0


def test_validate_hn_stories_missing_id():
    bad = [{"title": "Some story", "score": 10, "type": "story"}]
    cleaned, report = validate_hn_stories(bad)
    assert len(cleaned) == 0
    assert report.invalid == 1


def test_validate_hn_stories_empty_title():
    bad = [{"id": 9999, "title": "", "score": 10, "type": "story"}]
    cleaned, report = validate_hn_stories(bad)
    assert len(cleaned) == 0
    assert report.invalid == 1


def test_validate_hn_stories_deduplication():
    duped = SAMPLE_STORIES + [SAMPLE_STORIES[0]]
    cleaned, report = validate_hn_stories(duped)
    assert len(cleaned) == 2
    assert report.duplicates_removed == 1


def test_validate_hn_stories_fields_present():
    cleaned, _ = validate_hn_stories(SAMPLE_STORIES)
    for story in cleaned:
        assert "hn_id" in story
        assert "title" in story
        assert "score" in story


def test_validate_hn_stories_empty():
    cleaned, report = validate_hn_stories([])
    assert cleaned == []
    assert report.total == 0
