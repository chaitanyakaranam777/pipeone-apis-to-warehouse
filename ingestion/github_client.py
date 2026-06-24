"""
GitHub Public Events API client.
Fetches events with pagination, deduplication, and repo enrichment.
"""
import logging
from typing import List, Dict, Any, Optional

from configs.settings import settings
from ingestion.base_client import BaseAPIClient

logger = logging.getLogger(__name__)


class GitHubClient(BaseAPIClient):
    """Client for the GitHub REST API v3."""

    def __init__(self):
        headers: Dict[str, str] = {}
        token = settings.api.github_token
        if token:
            headers["Authorization"] = f"Bearer {token}"
        super().__init__(settings.api.github_base_url, headers=headers)

    def fetch_public_events(self, pages: int = 3) -> List[Dict[str, Any]]:
        """
        Fetch public GitHub events across multiple pages.
        Returns a flat list of raw event dicts.
        """
        all_events: List[Dict[str, Any]] = []
        seen_ids = set()
        for page in range(1, pages + 1):
            logger.info(f"Fetching GitHub events page {page}/{pages}")
            try:
                events = self.get("/events", params={"per_page": 100, "page": page})
                if not events:
                    logger.info("No more events returned.")
                    break
                for ev in events:
                    eid = ev.get("id")
                    if eid and eid not in seen_ids:
                        seen_ids.add(eid)
                        all_events.append(ev)
            except Exception as exc:
                logger.error(f"Failed to fetch page {page}: {exc}")
                break
        logger.info(f"Fetched {len(all_events)} unique GitHub events.")
        return all_events

    def fetch_repo_details(self, repo_full_name: str) -> Optional[Dict[str, Any]]:
        """Fetch metadata for a single repository."""
        try:
            return self.get(f"/repos/{repo_full_name}")
        except Exception as exc:
            logger.warning(f"Could not fetch repo {repo_full_name}: {exc}")
            return None

    def fetch_trending_repos(self, language: str = "", since: str = "daily") -> List[Dict[str, Any]]:
        """Fetch trending repositories by searching recently created repos with many stars."""
        try:
            query = "stars:>100 sort:stars"
            if language:
                query += f" language:{language}"
            result = self.get("/search/repositories", params={"q": query, "per_page": 30})
            return result.get("items", [])
        except Exception as exc:
            logger.error(f"Failed to fetch trending repos: {exc}")
            return []
