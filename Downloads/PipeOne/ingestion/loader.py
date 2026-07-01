"""
Database loader: upserts validated records into PostgreSQL (and SQLite for tests).

Design:
- PostgreSQL: uses native INSERT … ON CONFLICT for true atomic upserts.
- SQLite (test/CI): falls back to SELECT-then-INSERT deduplication.
- All operations are wrapped in session_scope() for automatic rollback on failure.
- Every function returns a counts dict {inserted, skipped} for pipeline reporting.
"""
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert

from database.connection import session_scope, get_session
from database.models import GitHubEvent, HackerNewsStory, IngestionLog

logger = logging.getLogger(__name__)


def _is_postgres(session) -> bool:
    """Return True when the active dialect is PostgreSQL."""
    return session.bind.dialect.name == "postgresql"


# ── GitHub Events ─────────────────────────────────────────────────────────────

def upsert_github_events(records: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Upsert GitHub events into github_events_raw.

    PostgreSQL: INSERT … ON CONFLICT (event_id) DO NOTHING — fully idempotent.
    SQLite:     SELECT existing IDs, skip duplicates, bulk insert new rows.

    Returns:
        {"inserted": int, "skipped": int}
    """
    if not records:
        logger.info("GitHub events: no records to upsert")
        return {"inserted": 0, "skipped": 0}

    inserted = skipped = 0

    with session_scope() as session:
        if _is_postgres(session):
            # Batch into chunks of 500 to avoid parameter limits
            for chunk in _chunks(records, 500):
                stmt = (
                    pg_insert(GitHubEvent)
                    .values(chunk)
                    .on_conflict_do_nothing(index_elements=["event_id"])
                )
                result = session.execute(stmt)
                inserted += result.rowcount
                skipped += len(chunk) - result.rowcount
        else:
            # SQLite path — used by tests
            existing_ids = {
                row[0] for row in
                session.execute(text("SELECT event_id FROM github_events_raw")).fetchall()
            }
            new_records = []
            for rec in records:
                if rec["event_id"] in existing_ids:
                    skipped += 1
                else:
                    existing_ids.add(rec["event_id"])
                    new_records.append(rec)
            for rec in new_records:
                session.add(GitHubEvent(**rec))
                inserted += 1

    logger.info(f"GitHub events upsert: inserted={inserted}, skipped={skipped}")
    return {"inserted": inserted, "skipped": skipped}


# ── Hacker News Stories ───────────────────────────────────────────────────────

def upsert_hn_stories(records: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Upsert HN stories into hn_stories_raw.

    PostgreSQL: INSERT … ON CONFLICT (hn_id) DO UPDATE — refreshes score + comment_count.
    SQLite:     Merge by hand (update if exists, insert if not).

    Returns:
        {"inserted": int, "skipped": int}
    """
    if not records:
        logger.info("HN stories: no records to upsert")
        return {"inserted": 0, "skipped": 0}

    inserted = skipped = 0

    with session_scope() as session:
        if _is_postgres(session):
            for chunk in _chunks(records, 500):
                stmt = (
                    pg_insert(HackerNewsStory)
                    .values(chunk)
                    .on_conflict_do_update(
                        index_elements=["hn_id"],
                        set_={
                            "score": pg_insert(HackerNewsStory).excluded.score,
                            "comment_count": pg_insert(HackerNewsStory).excluded.comment_count,
                            "ingested_at": datetime.now(tz=timezone.utc),
                        },
                    )
                )
                result = session.execute(stmt)
                inserted += result.rowcount
                skipped += len(chunk) - result.rowcount
        else:
            # SQLite path
            existing = {
                row[0]: row[1]
                for row in session.execute(
                    text("SELECT hn_id, id FROM hn_stories_raw")
                ).fetchall()
            }
            for rec in records:
                hn_id = rec["hn_id"]
                if hn_id in existing:
                    # Update mutable fields
                    session.execute(
                        text(
                            "UPDATE hn_stories_raw SET score=:score, "
                            "comment_count=:cc WHERE hn_id=:hn_id"
                        ),
                        {"score": rec["score"], "cc": rec["comment_count"], "hn_id": hn_id},
                    )
                    skipped += 1
                else:
                    session.add(HackerNewsStory(**rec))
                    existing[hn_id] = True
                    inserted += 1

    logger.info(f"HN stories upsert: inserted={inserted}, skipped={skipped}")
    return {"inserted": inserted, "skipped": skipped}


# ── Ingestion Audit Log ───────────────────────────────────────────────────────

def log_ingestion(
    pipeline: str,
    source: str,
    records_fetched: int,
    records_inserted: int,
    records_skipped: int,
    status: str = "success",
    error_message: str | None = None,
) -> None:
    """
    Append one row to ingestion_log for observability.
    Never raises — logging failures must not break the pipeline.
    """
    try:
        with session_scope() as session:
            entry = IngestionLog(
                pipeline=pipeline,
                source=source,
                records_fetched=records_fetched,
                records_inserted=records_inserted,
                records_skipped=records_skipped,
                status=status,
                error_message=error_message,
                finished_at=datetime.now(tz=timezone.utc),
            )
            session.add(entry)
        logger.info(f"Ingestion log: pipeline={pipeline}, status={status}")
    except Exception as exc:
        logger.error(f"Failed to write ingestion log: {exc}")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _chunks(lst: list, size: int):
    """Yield successive chunks of `size` from `lst`."""
    for i in range(0, len(lst), size):
        yield lst[i: i + size]
