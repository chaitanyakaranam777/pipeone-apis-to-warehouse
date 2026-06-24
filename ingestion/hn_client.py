"""
Hacker News Firebase REST API client.
Fetches top stories with full item details.
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from configs.settings import settings
from ingestion.base_client import BaseAPIClient

logger = logging.getLogger(__name__)


class HackerNewsClient(BaseAPIClient):
    """Client for the Hacker News Firebase API."""

    def __init__(self):
        super().__init__(settings.api.hn_base_url)

    def fetch_top_story_ids(self, limit: int = 100) -> List[int]:
        """Return the top N story IDs."""
        try:
            ids = self.get("/topstories.json")
            return ids[:limit]
        except Exception as exc:
            logger.error(f"Failed to fetch top story IDs: {exc}")
            return []

    def fetch_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single HN item by ID."""
        try:
            return self.get(f"/item/{item_id}.json")
        except Exception as exc:
            logger.warning(f"Failed to fetch item {item_id}: {exc}")
            return None

    def fetch_top_stories(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch full details for the top N HN stories.
        Skips jobs, polls, and items without a title.
        """
        story_ids = self.fetch_top_story_ids(limit=limit * 2)
        stories: List[Dict[str, Any]] = []
        fetched = 0

        for sid in story_ids:
            if fetched >= limit:
                break
            item = self.fetch_item(sid)
            if not item:
                continue
            if item.get("type") not in ("story", "ask", "show"):
                continue
            if not item.get("title"):
                continue

            item["time_posted"] = (
                datetime.utcfromtimestamp(item["time"]) if item.get("time") else None
            )
            stories.append(item)
            fetched += 1

        logger.info(f"Fetched {len(stories)} HN stories.")
        return stories
