"""
Cached data-access helpers for the Streamlit dashboard.
Falls back to sample data if PostgreSQL is unavailable.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import streamlit as st
from sqlalchemy import text, create_engine
from datetime import datetime, timedelta
import random

from configs.settings import settings


def _get_engine():
    try:
        engine = create_engine(settings.db.url, pool_pre_ping=True)
        with engine.connect() as c:
            c.execute(text("SELECT 1"))
        return engine
    except Exception:
        return None


def _sample_github_events(n: int = 300) -> pd.DataFrame:
    types = ["PushEvent","PullRequestEvent","IssuesEvent","WatchEvent","ForkEvent","CreateEvent"]
    actors = [f"user_{i}" for i in range(1, 31)]
    repos = [f"org_{i}/repo_{j}" for i in range(1,6) for j in range(1,8)]
    now = datetime.utcnow()
    rows = []
    for _ in range(n):
        rows.append({
            "event_type": random.choice(types),
            "actor_login": random.choice(actors),
            "repo_name": random.choice(repos),
            "created_at": now - timedelta(hours=random.randint(0, 72)),
        })
    return pd.DataFrame(rows)


def _sample_hn_stories(n: int = 100) -> pd.DataFrame:
    domains = ["github.com","medium.com","ycombinator.com","techcrunch.com","arxiv.org"]
    now = datetime.utcnow()
    rows = []
    for i in range(n):
        rows.append({
            "hn_id": 1000 + i,
            "title": f"Sample story {i+1}: interesting tech topic",
            "domain": random.choice(domains),
            "score": random.randint(10, 500),
            "author": f"author_{random.randint(1,20)}",
            "comment_count": random.randint(0, 200),
            "story_type": "story",
            "time_posted": now - timedelta(hours=random.randint(0, 48)),
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=300)
def get_github_events() -> pd.DataFrame:
    engine = _get_engine()
    if engine:
        try:
            return pd.read_sql("SELECT * FROM github_events_raw ORDER BY created_at DESC LIMIT 1000", engine)
        except Exception:
            pass
    return _sample_github_events()


@st.cache_data(ttl=300)
def get_hn_stories() -> pd.DataFrame:
    engine = _get_engine()
    if engine:
        try:
            return pd.read_sql("SELECT * FROM hn_stories_raw ORDER BY score DESC LIMIT 500", engine)
        except Exception:
            pass
    return _sample_hn_stories()


@st.cache_data(ttl=300)
def get_ingestion_log() -> pd.DataFrame:
    engine = _get_engine()
    if engine:
        try:
            return pd.read_sql("SELECT * FROM ingestion_log ORDER BY started_at DESC LIMIT 50", engine)
        except Exception:
            pass
    now = datetime.utcnow()
    return pd.DataFrame([
        {"pipeline":"github_events","source":"github_api","records_fetched":280,"records_inserted":250,
         "records_skipped":30,"status":"success","started_at": now - timedelta(minutes=10),"finished_at": now - timedelta(minutes=9)},
        {"pipeline":"hn_stories","source":"hackernews_api","records_fetched":100,"records_inserted":98,
         "records_skipped":2,"status":"success","started_at": now - timedelta(minutes=5),"finished_at": now - timedelta(minutes=4)},
    ])


def db_connected() -> bool:
    return _get_engine() is not None
