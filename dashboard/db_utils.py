"""
Shared database query helpers for the Streamlit dashboard.
Uses SQLAlchemy + Pandas to return DataFrames.
"""
import os
import pandas as pd
from sqlalchemy import create_engine, text

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        url = (
            f"postgresql://{os.getenv('POSTGRES_USER','pipeone_user')}:"
            f"{os.getenv('POSTGRES_PASSWORD','pipeone_pass')}@"
            f"{os.getenv('POSTGRES_HOST','localhost')}:"
            f"{os.getenv('POSTGRES_PORT','5432')}/"
            f"{os.getenv('POSTGRES_DB','pipeone')}"
        )
        _engine = create_engine(url, pool_pre_ping=True)
    return _engine


def query_df(sql: str, params: dict | None = None) -> pd.DataFrame:
    """Execute SQL and return a DataFrame. Returns empty DF on error."""
    try:
        with get_engine().connect() as conn:
            return pd.read_sql(text(sql), conn, params=params)
    except Exception as e:
        return pd.DataFrame()


def get_github_events() -> pd.DataFrame:
    return query_df("""
        SELECT event_id, event_type, actor_login, repo_name,
               created_at, payload_size, ingested_at
        FROM github_events_raw
        ORDER BY created_at DESC
        LIMIT 5000
    """)


def get_github_event_types() -> pd.DataFrame:
    return query_df("""
        SELECT event_type, COUNT(*) as count
        FROM github_events_raw
        GROUP BY event_type
        ORDER BY count DESC
    """)


def get_github_top_repos() -> pd.DataFrame:
    return query_df("""
        SELECT repo_name,
               COUNT(*) as events,
               COUNT(DISTINCT actor_login) as unique_actors
        FROM github_events_raw
        GROUP BY repo_name
        ORDER BY events DESC
        LIMIT 20
    """)


def get_github_top_actors() -> pd.DataFrame:
    return query_df("""
        SELECT actor_login,
               COUNT(*) as events,
               COUNT(DISTINCT event_type) as event_types,
               COUNT(DISTINCT repo_name) as repos
        FROM github_events_raw
        WHERE actor_login IS NOT NULL
        GROUP BY actor_login
        ORDER BY events DESC
        LIMIT 20
    """)


def get_github_timeline() -> pd.DataFrame:
    return query_df("""
        SELECT DATE_TRUNC('hour', created_at) as hour,
               COUNT(*) as events
        FROM github_events_raw
        WHERE created_at IS NOT NULL
        GROUP BY 1
        ORDER BY 1
    """)


def get_hn_stories() -> pd.DataFrame:
    return query_df("""
        SELECT hn_id, title, url, score, author,
               comment_count, story_type, time_posted
        FROM hn_stories_raw
        ORDER BY score DESC
        LIMIT 2000
    """)


def get_hn_score_distribution() -> pd.DataFrame:
    return query_df("""
        SELECT
            CASE
                WHEN score >= 500 THEN 'Viral (500+)'
                WHEN score >= 100 THEN 'Popular (100-499)'
                WHEN score >= 10  THEN 'Moderate (10-99)'
                ELSE 'Low (<10)'
            END as tier,
            COUNT(*) as count
        FROM hn_stories_raw
        GROUP BY 1
        ORDER BY count DESC
    """)


def get_hn_top_authors() -> pd.DataFrame:
    return query_df("""
        SELECT author,
               COUNT(*) as stories,
               AVG(score) as avg_score,
               SUM(comment_count) as total_comments
        FROM hn_stories_raw
        WHERE author IS NOT NULL
        GROUP BY author
        ORDER BY stories DESC
        LIMIT 20
    """)


def get_ingestion_log() -> pd.DataFrame:
    return query_df("""
        SELECT pipeline, source, records_fetched, records_inserted,
               records_skipped, status, started_at, finished_at
        FROM ingestion_log
        ORDER BY started_at DESC
        LIMIT 50
    """)


def get_kpis() -> dict:
    df = query_df("""
        SELECT
            (SELECT COUNT(*) FROM github_events_raw) AS github_events,
            (SELECT COUNT(DISTINCT actor_login) FROM github_events_raw) AS github_actors,
            (SELECT COUNT(DISTINCT repo_name) FROM github_events_raw) AS github_repos,
            (SELECT COUNT(*) FROM hn_stories_raw) AS hn_stories,
            (SELECT COALESCE(AVG(score),0) FROM hn_stories_raw) AS hn_avg_score
    """)
    if df.empty:
        return {}
    return df.iloc[0].to_dict()
