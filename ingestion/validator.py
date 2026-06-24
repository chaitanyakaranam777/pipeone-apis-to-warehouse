"""
Data validation for GitHub events and HN stories.
Returns validated records and a validation report.
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


class ValidationReport:
    """Stores validation statistics."""

    def __init__(self, source: str):
        self.source = source
        self.total = 0
        self.valid = 0
        self.invalid = 0
        self.duplicates_removed = 0
        self.issues: List[str] = []

    def __repr__(self) -> str:
        return (
            f"ValidationReport(source={self.source}, total={self.total}, "
            f"valid={self.valid}, invalid={self.invalid}, "
            f"dupes_removed={self.duplicates_removed})"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "total": self.total,
            "valid": self.valid,
            "invalid": self.invalid,
            "duplicates_removed": self.duplicates_removed,
            "issues": self.issues,
        }


def validate_github_events(
    raw_events: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], ValidationReport]:
    """
    Validate raw GitHub events.
    - Ensures required fields exist
    - Normalises created_at to datetime
    - Removes duplicates by event_id
    """
    report = ValidationReport("github_events")
    report.total = len(raw_events)

    cleaned: List[Dict[str, Any]] = []
    seen_ids = set()

    for ev in raw_events:
        event_id = ev.get("id")
        if not event_id:
            report.invalid += 1
            report.issues.append("Missing event id")
            continue

        if event_id in seen_ids:
            report.duplicates_removed += 1
            continue
        seen_ids.add(event_id)

        event_type = ev.get("type")
        if not event_type:
            report.invalid += 1
            report.issues.append(f"Missing event_type for id={event_id}")
            continue

        actor = ev.get("actor") or {}
        repo = ev.get("repo") or {}
        payload = ev.get("payload") or {}

        try:
            created_at = (
                datetime.fromisoformat(ev["created_at"].replace("Z", "+00:00"))
                if ev.get("created_at")
                else None
            )
        except (ValueError, KeyError):
            created_at = None

        cleaned.append({
            "event_id": str(event_id),
            "event_type": event_type,
            "actor_id": actor.get("id"),
            "actor_login": actor.get("login"),
            "repo_id": repo.get("id"),
            "repo_name": repo.get("name"),
            "public": ev.get("public", True),
            "created_at": created_at,
            "payload_size": len(str(payload)),
        })
        report.valid += 1

    logger.info(f"GitHub validation: {report}")
    return cleaned, report


def validate_hn_stories(
    raw_stories: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], ValidationReport]:
    """
    Validate raw HN stories.
    - Removes entries without title or id
    - Deduplicates by hn_id
    """
    report = ValidationReport("hn_stories")
    report.total = len(raw_stories)

    cleaned: List[Dict[str, Any]] = []
    seen_ids: set = set()

    for story in raw_stories:
        hn_id = story.get("id")
        if not hn_id:
            report.invalid += 1
            continue

        if hn_id in seen_ids:
            report.duplicates_removed += 1
            continue
        seen_ids.add(hn_id)

        title = story.get("title", "").strip()
        if not title:
            report.invalid += 1
            report.issues.append(f"Empty title for id={hn_id}")
            continue

        cleaned.append({
            "hn_id": int(hn_id),
            "title": title,
            "url": story.get("url"),
            "score": int(story.get("score", 0)),
            "author": story.get("by"),
            "comment_count": int(story.get("descendants", 0)),
            "story_type": story.get("type", "story"),
            "time_posted": story.get("time_posted"),
        })
        report.valid += 1

    logger.info(f"HN validation: {report}")
    return cleaned, report
