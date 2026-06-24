"""
Database loader: upserts validated records into PostgreSQL.
"""
import logging
from datetime import datetime
from typing import List, Dict, Any

from sqlalchemy.dialects.postgresql import insert

from database.connection import session_scope
from database.models import GitHubEvent, GitHubRepo, HackerNewsStory, IngestionLog

logger = logging.getLogger(__name__)


def upsert_github_events(records: List[Dict[str, Any]]) -> Dict[str, int]:
    """Upsert GitHub events. Returns counts of inserted/skipped."""
    inserted = skipped = 0
    with session_scope() as session:
        for rec in records:
            stmt = (
                insert(GitHubEvent)
                .values(**rec)
                .on_conflict_do_nothing(index_elements=["event_id"])
            )
            result = session.execute(stmt)
            if result.rowcount:
                inserted += 1
            else:
                skipped += 1
    logger.info(f"GitHub events: inserted={inserted}, skipped={skipped}")
    return {"inserted": inserted, "skipped": skipped}


def upsert_hn_stories(records: List[Dict[str, Any]]) -> Dict[str, int]:
    """Upsert HN stories. Returns counts."""
    inserted = skipped = 0
    with session_scope() as session:
        for rec in records:
            stmt = (
                insert(HackerNewsStory)
                .values(**rec)
                .on_conflict_do_update(
                    index_elements=["hn_id"],
                    set_={
                        "score": rec["score"],
                        "comment_count": rec["comment_count"],
                        "ingested_at": datetime.utcnow(),
                    },
                )
            )
            result = session.execute(stmt)
            if result.rowcount:
                inserted += 1
            else:
                skipped += 1
    logger.info(f"HN stories: inserted={inserted}, skipped={skipped}")
    return {"inserted": inserted, "skipped": skipped}


def log_ingestion(
    pipeline: str,
    source: str,
    records_fetched: int,
    records_inserted: int,
    records_skipped: int,
    status: str = "success",
    error_message: str | None = None,
) -> None:
    """Write a row to the ingestion audit log."""
    with session_scope() as session:
        entry = IngestionLog(
            pipeline=pipeline,
            source=source,
            records_fetched=records_fetched,
            records_inserted=records_inserted,
            records_skipped=records_skipped,
            status=status,
            error_message=error_message,
            finished_at=datetime.utcnow(),
        )
        session.add(entry)
    logger.info(f"Ingestion log written: pipeline={pipeline}, status={status}")
