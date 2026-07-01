"""
Cached data-access helpers for the PipeOne Streamlit dashboard.

Query strategy (in priority order):
  1. dbt mart tables  — fully transformed, analytics-ready
  2. Raw PostgreSQL   — available immediately after ingestion, before dbt runs
  3. Sample data      — demo mode when no database is connected

All public functions are decorated with @st.cache_data(ttl=300) so the
dashboard doesn't hammer the database on every page interaction.
"""
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Optional
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import streamlit as st
from sqlalchemy import text, create_engine
from sqlalchemy.engine import Engine

from configs.settings import settings

logger = logging.getLogger(__name__)

# ── Engine factory ────────────────────────────────────────────────────────────

@st.cache_resource
def _get_engine() -> Optional[Engine]:
    """
    Return a SQLAlchemy engine if PostgreSQL is reachable, else None.
    Cached as a resource so the connection pool is shared across reruns.
    """
    try:
        engine = create_engine(
            settings.db.url,
            pool_pre_ping=True,
            pool_size=3,
            max_overflow=5,
            connect_args={"connect_timeout": 5},
        )
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as exc:
        logger.debug(f"DB not available: {exc}")
        return None


def db_connected() -> bool:
    """Return True if PostgreSQL is reachable."""
    return _get_engine() is not None


def _table_exists(engine: Engine, table_name: str) -> bool:
    """Check whether a table or view exists in the database."""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT EXISTS ("
                    "  SELECT 1 FROM information_schema.tables"
                    "  WHERE table_name = :name"
                    ")"
                ),
                {"name": table_name},
            )
            return result.scalar()
    except Exception:
        return False


def _read_sql_safe(engine: Engine, query: str) -> Optional[pd.DataFrame]:
    """Execute a SQL query and return a DataFrame, or None on error."""
    try:
        return pd.read_sql(query, engine)
    except Exception as exc:
        logger.warning(f"Query failed: {exc}")
        return None


# ── Sample data generators (demo mode) ───────────────────────────────────────

def _sample_github_events(n: int = 300) -> pd.DataFrame:
    """Generate realistic-looking sample GitHub event data."""
    event_types = [
        "PushEvent", "PullRequestEvent", "IssuesEvent",
        "WatchEvent", "ForkEvent", "CreateEvent", "DeleteEvent",
    ]
    actors = [f"dev_{i}" for i in range(1, 31)]
    repos = [f"org_{i}/repo_{j}" for i in range(1, 6) for j in range(1, 8)]
    now = datetime.utcnow()
    rows = [
        {
            "event_type": random.choice(event_types),
            "actor_login": random.choice(actors),
            "repo_name": random.choice(repos),
            "created_at": now - timedelta(hours=random.randint(0, 72)),
        }
        for _ in range(n)
    ]
    return pd.DataFrame(rows)


def _sample_hn_stories(n: int = 100) -> pd.DataFrame:
    """Generate realistic-looking sample HN story data."""
    domains = [
        "github.com", "medium.com", "ycombinator.com",
        "techcrunch.com", "arxiv.org", "substack.com",
    ]
    title_templates = [
        "Ask HN: How do you {} in production?",
        "Show HN: I built a {} from scratch",
        "{} 2.0 released — what's new",
        "Why {} matters for data engineering",
        "The complete guide to {} in 2024",
    ]
    topics = ["PostgreSQL", "dbt", "Streamlit", "Kafka", "Spark", "Airflow", "Python"]
    now = datetime.utcnow()
    rows = [
        {
            "hn_id": 40000 + i,
            "title": random.choice(title_templates).format(random.choice(topics)),
            "domain": random.choice(domains),
            "score": random.randint(10, 600),
            "author": f"author_{random.randint(1, 20)}",
            "comment_count": random.randint(0, 250),
            "story_type": "story",
            "time_posted": now - timedelta(hours=random.randint(0, 48)),
        }
        for i in range(n)
    ]
    return pd.DataFrame(rows)


def _sample_ingestion_log() -> pd.DataFrame:
    """Generate sample pipeline run history."""
    now = datetime.utcnow()
    return pd.DataFrame([
        {
            "pipeline": "github_events", "source": "github_api",
            "records_fetched": 280, "records_inserted": 250, "records_skipped": 30,
            "status": "success", "insert_rate_pct": 89.3,
            "started_at": now - timedelta(minutes=10),
            "finished_at": now - timedelta(minutes=9),
        },
        {
            "pipeline": "hn_stories", "source": "hackernews_api",
            "records_fetched": 100, "records_inserted": 98, "records_skipped": 2,
            "status": "success", "insert_rate_pct": 98.0,
            "started_at": now - timedelta(minutes=5),
            "finished_at": now - timedelta(minutes=4),
        },
        {
            "pipeline": "github_events", "source": "github_api",
            "records_fetched": 295, "records_inserted": 180, "records_skipped": 115,
            "status": "success", "insert_rate_pct": 61.0,
            "started_at": now - timedelta(hours=1),
            "finished_at": now - timedelta(hours=1),
        },
    ])


def _sample_github_summary() -> pd.DataFrame:
    """Sample for mart_github_summary shape."""
    event_types = ["PushEvent", "PullRequestEvent", "WatchEvent", "ForkEvent", "IssuesEvent"]
    now = datetime.utcnow()
    rows = []
    for day_offset in range(7):
        for et in event_types:
            rows.append({
                "event_date": (now - timedelta(days=day_offset)).date(),
                "event_type": et,
                "total_events": random.randint(5, 80),
                "unique_actors": random.randint(2, 20),
            })
    return pd.DataFrame(rows)


def _sample_combined_activity() -> pd.DataFrame:
    now = datetime.utcnow()
    rows = []
    for i in range(14):
        rows.append({
            "activity_date": (now - timedelta(days=i)).date(),
            "github_events": random.randint(50, 300),
            "github_unique_actors": random.randint(10, 60),
            "hn_stories": random.randint(10, 50),
            "hn_avg_score": random.randint(50, 300),
        })
    return pd.DataFrame(rows)


# ── Public query functions ────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def get_github_events() -> pd.DataFrame:
    """
    Return GitHub events.
    Tries mart_github_summary → github_events_raw → sample data.
    """
    engine = _get_engine()
    if engine:
        # Prefer the mart (post-dbt)
        if _table_exists(engine, "mart_github_summary"):
            df = _read_sql_safe(
                engine,
                "SELECT * FROM marts.mart_github_summary ORDER BY event_date DESC",
            )
            if df is not None and not df.empty:
                return df

        # Fall back to raw table (pre-dbt)
        df = _read_sql_safe(
            engine,
            "SELECT event_type, actor_login, repo_name, created_at "
            "FROM github_events_raw ORDER BY created_at DESC LIMIT 2000",
        )
        if df is not None and not df.empty:
            return df

    return _sample_github_events()


@st.cache_data(ttl=300)
def get_github_events_raw() -> pd.DataFrame:
    """Always return the raw events table (for event-level detail views)."""
    engine = _get_engine()
    if engine:
        df = _read_sql_safe(
            engine,
            "SELECT event_type, actor_login, repo_name, created_at "
            "FROM github_events_raw ORDER BY created_at DESC LIMIT 2000",
        )
        if df is not None and not df.empty:
            return df
    return _sample_github_events()


@st.cache_data(ttl=300)
def get_hn_stories() -> pd.DataFrame:
    """
    Return HN stories.
    Tries mart_hn_top_stories → hn_stories_raw → sample data.
    """
    engine = _get_engine()
    if engine:
        if _table_exists(engine, "mart_hn_top_stories"):
            df = _read_sql_safe(
                engine,
                "SELECT * FROM marts.mart_hn_top_stories ORDER BY score DESC",
            )
            if df is not None and not df.empty:
                return df

        df = _read_sql_safe(
            engine,
            "SELECT hn_id, title, url, score, author, comment_count, "
            "story_type, time_posted FROM hn_stories_raw ORDER BY score DESC LIMIT 500",
        )
        if df is not None and not df.empty:
            # Add domain column from URL
            df["domain"] = df["url"].apply(
                lambda u: u.replace("https://", "").replace("http://", "").split("/")[0]
                if isinstance(u, str) and u
                else "self"
            )
            return df

    return _sample_hn_stories()


@st.cache_data(ttl=300)
def get_ingestion_log() -> pd.DataFrame:
    """
    Return pipeline run history.
    Tries mart_pipeline_health → ingestion_log → sample data.
    """
    engine = _get_engine()
    if engine:
        if _table_exists(engine, "mart_pipeline_health"):
            df = _read_sql_safe(
                engine,
                "SELECT * FROM marts.mart_pipeline_health ORDER BY started_at DESC LIMIT 50",
            )
            if df is not None and not df.empty:
                return df

        df = _read_sql_safe(
            engine,
            "SELECT pipeline, source, records_fetched, records_inserted, "
            "records_skipped, status, error_message, started_at, finished_at "
            "FROM ingestion_log ORDER BY started_at DESC LIMIT 50",
        )
        if df is not None and not df.empty:
            return df

    return _sample_ingestion_log()


@st.cache_data(ttl=300)
def get_combined_activity() -> pd.DataFrame:
    """
    Return cross-source daily activity.
    Tries mart_combined_activity → builds from raw → sample.
    """
    engine = _get_engine()
    if engine:
        if _table_exists(engine, "mart_combined_activity"):
            df = _read_sql_safe(
                engine,
                "SELECT * FROM marts.mart_combined_activity ORDER BY activity_date DESC",
            )
            if df is not None and not df.empty:
                return df

        # Build from raw tables
        df = _read_sql_safe(
            engine,
            """
            SELECT
                DATE_TRUNC('day', created_at) AS activity_date,
                COUNT(*) AS github_events,
                COUNT(DISTINCT actor_login) AS github_unique_actors
            FROM github_events_raw
            WHERE created_at IS NOT NULL
            GROUP BY 1
            ORDER BY 1 DESC
            """,
        )
        if df is not None and not df.empty:
            return df

    return _sample_combined_activity()


@st.cache_data(ttl=300)
def get_repo_leaderboard() -> pd.DataFrame:
    """Return top repos by event volume."""
    engine = _get_engine()
    if engine:
        if _table_exists(engine, "mart_repo_leaderboard"):
            df = _read_sql_safe(
                engine,
                "SELECT * FROM marts.mart_repo_leaderboard ORDER BY total_events DESC LIMIT 20",
            )
            if df is not None and not df.empty:
                return df

        df = _read_sql_safe(
            engine,
            """
            SELECT repo_name, COUNT(*) AS total_events
            FROM github_events_raw
            WHERE repo_name IS NOT NULL
            GROUP BY repo_name
            ORDER BY total_events DESC
            LIMIT 20
            """,
        )
        if df is not None and not df.empty:
            return df

    # Sample data
    repos = [f"org_{i}/repo_{j}" for i in range(1, 4) for j in range(1, 8)]
    return pd.DataFrame({
        "repo_name": repos,
        "total_events": sorted([random.randint(10, 200) for _ in repos], reverse=True),
    })
