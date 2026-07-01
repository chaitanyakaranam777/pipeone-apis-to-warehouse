"""Unit tests for API clients using mocked HTTP responses."""
import pytest
import responses as rsps_lib
import json
from ingestion.github_client import GitHubClient
from ingestion.hn_client import HackerNewsClient


@rsps_lib.activate
def test_github_fetch_public_events_success():
    fake_events = [
        {"id": f"ev{i}", "type": "PushEvent",
         "actor": {"id": i, "login": f"user{i}"},
         "repo": {"id": i*10, "name": f"org/repo{i}"},
         "public": True, "created_at": "2024-01-15T10:00:00Z",
         "payload": {}}
        for i in range(5)
    ]
    rsps_lib.add(rsps_lib.GET, "https://api.github.com/events",
                 json=fake_events, status=200)

    client = GitHubClient()
    events = client.fetch_public_events(pages=1)
    assert len(events) == 5


@rsps_lib.activate
def test_github_fetch_events_handles_empty():
    rsps_lib.add(rsps_lib.GET, "https://api.github.com/events",
                 json=[], status=200)
    client = GitHubClient()
    events = client.fetch_public_events(pages=1)
    assert events == []


@rsps_lib.activate
def test_github_fetch_events_handles_error(caplog):
    rsps_lib.add(rsps_lib.GET, "https://api.github.com/events",
                 json={"message": "Not Found"}, status=404)
    client = GitHubClient()
    import requests
    # Should not raise, should return empty list
    events = client.fetch_public_events(pages=1)
    assert isinstance(events, list)


@rsps_lib.activate
def test_hn_fetch_top_story_ids():
    rsps_lib.add(rsps_lib.GET,
                 "https://hacker-news.firebaseio.com/v0/topstories.json",
                 json=list(range(1, 201)), status=200)
    client = HackerNewsClient()
    ids = client.fetch_top_story_ids(limit=50)
    assert len(ids) == 50
    assert ids[0] == 1


@rsps_lib.activate
def test_hn_fetch_item_success():
    rsps_lib.add(rsps_lib.GET,
                 "https://hacker-news.firebaseio.com/v0/item/42.json",
                 json={"id": 42, "title": "Test Story", "score": 100,
                       "by": "author", "type": "story", "time": 1705312800,
                       "descendants": 30},
                 status=200)
    client = HackerNewsClient()
    item = client.fetch_item(42)
    assert item["id"] == 42
    assert item["title"] == "Test Story"


@rsps_lib.activate
def test_hn_fetch_item_failure_returns_none():
    rsps_lib.add(rsps_lib.GET,
                 "https://hacker-news.firebaseio.com/v0/item/9999.json",
                 json=None, status=200)
    client = HackerNewsClient()
    item = client.fetch_item(9999)
    # None item returns None
    assert item is None
