"""
Main pipeline orchestrator.
Runs GitHub and Hacker News ingestion end-to-end.
"""
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import init_db
from ingestion.github_client import GitHubClient
from ingestion.hn_client import HackerNewsClient
from ingestion.validator import validate_github_events, validate_hn_stories
from ingestion.loader import upsert_github_events, upsert_hn_stories, log_ingestion

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def run_github_pipeline(pages: int = 3) -> dict:
    """Run the full GitHub events ingestion pipeline."""
    logger.info("=== GitHub Pipeline START ===")
    gh = GitHubClient()
    raw = gh.fetch_public_events(pages=pages)
    validated, report = validate_github_events(raw)
    counts = upsert_github_events(validated)
    log_ingestion(
        pipeline="github_events",
        source="github_api",
        records_fetched=report.total,
        records_inserted=counts["inserted"],
        records_skipped=counts["skipped"],
        status="success",
    )
    logger.info(f"=== GitHub Pipeline DONE: {counts} ===")
    return {"report": report.to_dict(), "counts": counts}


def run_hn_pipeline(limit: int = 100) -> dict:
    """Run the full Hacker News ingestion pipeline."""
    logger.info("=== HN Pipeline START ===")
    hn = HackerNewsClient()
    raw = hn.fetch_top_stories(limit=limit)
    validated, report = validate_hn_stories(raw)
    counts = upsert_hn_stories(validated)
    log_ingestion(
        pipeline="hn_stories",
        source="hackernews_api",
        records_fetched=report.total,
        records_inserted=counts["inserted"],
        records_skipped=counts["skipped"],
        status="success",
    )
    logger.info(f"=== HN Pipeline DONE: {counts} ===")
    return {"report": report.to_dict(), "counts": counts}


def run_all():
    """Run both pipelines."""
    logger.info("Initialising database...")
    init_db()
    gh_result = run_github_pipeline()
    hn_result = run_hn_pipeline()
    logger.info("All pipelines complete.")
    return {"github": gh_result, "hn": hn_result}


if __name__ == "__main__":
    run_all()
