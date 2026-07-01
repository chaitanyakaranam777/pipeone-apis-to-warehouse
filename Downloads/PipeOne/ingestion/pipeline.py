"""
Main pipeline orchestrator for PipeOne.

Entry point: python ingestion/pipeline.py

Runs both API ingestion pipelines sequentially:
  1. GitHub Public Events
  2. Hacker News Top Stories

Each pipeline:
  - Fetches raw data from the API
  - Validates and deduplicates records
  - Upserts into PostgreSQL
  - Writes an audit row to ingestion_log

Exit codes:
  0 — both pipelines succeeded
  1 — one or more pipelines failed
"""
import logging
import sys
import os
import time

# Ensure project root is on the path when run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import init_db, health_check
from ingestion.github_client import GitHubClient
from ingestion.hn_client import HackerNewsClient
from ingestion.validator import validate_github_events, validate_hn_stories
from ingestion.loader import upsert_github_events, upsert_hn_stories, log_ingestion

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("pipeone.pipeline")


def run_github_pipeline(pages: int = 3) -> dict:
    """
    GitHub Events ingestion pipeline.

    Args:
        pages: Number of API pages to fetch (100 events/page max).

    Returns:
        {"report": ValidationReport.to_dict(), "counts": {"inserted": int, "skipped": int}}
    """
    logger.info("=" * 50)
    logger.info("GitHub Pipeline — START")
    logger.info("=" * 50)
    start = time.time()

    try:
        gh = GitHubClient()
        raw = gh.fetch_public_events(pages=pages)
        logger.info(f"Fetched {len(raw)} raw GitHub events")

        validated, report = validate_github_events(raw)
        logger.info(
            f"Validation complete: valid={report.valid}, "
            f"invalid={report.invalid}, dupes={report.duplicates_removed}"
        )

        counts = upsert_github_events(validated)

        log_ingestion(
            pipeline="github_events",
            source="github_api",
            records_fetched=report.total,
            records_inserted=counts["inserted"],
            records_skipped=counts["skipped"],
            status="success",
        )

        elapsed = time.time() - start
        logger.info(f"GitHub Pipeline — DONE in {elapsed:.1f}s | {counts}")
        return {"report": report.to_dict(), "counts": counts}

    except Exception as exc:
        elapsed = time.time() - start
        logger.error(f"GitHub Pipeline — FAILED after {elapsed:.1f}s: {exc}", exc_info=True)
        log_ingestion(
            pipeline="github_events",
            source="github_api",
            records_fetched=0,
            records_inserted=0,
            records_skipped=0,
            status="failed",
            error_message=str(exc),
        )
        raise


def run_hn_pipeline(limit: int = 100) -> dict:
    """
    Hacker News ingestion pipeline.

    Args:
        limit: Maximum number of stories to fetch.

    Returns:
        {"report": ValidationReport.to_dict(), "counts": {"inserted": int, "skipped": int}}
    """
    logger.info("=" * 50)
    logger.info("Hacker News Pipeline — START")
    logger.info("=" * 50)
    start = time.time()

    try:
        hn = HackerNewsClient()
        raw = hn.fetch_top_stories(limit=limit)
        logger.info(f"Fetched {len(raw)} raw HN stories")

        validated, report = validate_hn_stories(raw)
        logger.info(
            f"Validation complete: valid={report.valid}, "
            f"invalid={report.invalid}, dupes={report.duplicates_removed}"
        )

        counts = upsert_hn_stories(validated)

        log_ingestion(
            pipeline="hn_stories",
            source="hackernews_api",
            records_fetched=report.total,
            records_inserted=counts["inserted"],
            records_skipped=counts["skipped"],
            status="success",
        )

        elapsed = time.time() - start
        logger.info(f"HN Pipeline — DONE in {elapsed:.1f}s | {counts}")
        return {"report": report.to_dict(), "counts": counts}

    except Exception as exc:
        elapsed = time.time() - start
        logger.error(f"HN Pipeline — FAILED after {elapsed:.1f}s: {exc}", exc_info=True)
        log_ingestion(
            pipeline="hn_stories",
            source="hackernews_api",
            records_fetched=0,
            records_inserted=0,
            records_skipped=0,
            status="failed",
            error_message=str(exc),
        )
        raise


def run_all(github_pages: int = 3, hn_limit: int = 100) -> dict:
    """
    Run both ingestion pipelines end-to-end.

    1. Waits for PostgreSQL to be ready.
    2. Creates all tables if they don't exist.
    3. Runs GitHub then HN pipeline.

    Returns combined results dict.
    """
    logger.info("PipeOne — Starting full ingestion run")
    total_start = time.time()

    # Wait for database
    logger.info("Waiting for database...")
    for attempt in range(1, 11):
        try:
            init_db()
            if health_check():
                logger.info("Database ready")
                break
        except Exception as exc:
            logger.warning(f"DB not ready (attempt {attempt}/10): {exc}")
            time.sleep(3)
    else:
        logger.error("Database unreachable after 10 attempts. Exiting.")
        sys.exit(1)

    failures = []
    results: dict = {}

    # GitHub pipeline
    try:
        results["github"] = run_github_pipeline(pages=github_pages)
    except Exception as exc:
        logger.error(f"GitHub pipeline failed: {exc}")
        failures.append("github")
        results["github"] = {"error": str(exc)}

    # HN pipeline
    try:
        results["hn"] = run_hn_pipeline(limit=hn_limit)
    except Exception as exc:
        logger.error(f"HN pipeline failed: {exc}")
        failures.append("hn")
        results["hn"] = {"error": str(exc)}

    elapsed = time.time() - total_start
    logger.info(f"PipeOne — All pipelines finished in {elapsed:.1f}s")

    if failures:
        logger.error(f"Failed pipelines: {failures}")
        sys.exit(1)

    return results


if __name__ == "__main__":
    run_all()
