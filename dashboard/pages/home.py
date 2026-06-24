"""Home page."""
import streamlit as st
import pandas as pd
from dashboard.db_queries import get_github_events, get_hn_stories, get_ingestion_log, db_connected


def render():
    st.title("🚀 PipeOne — Data Pipeline Dashboard")
    st.markdown("**H1 Project · Foundations of Data Engineering · APIs → Warehouse**")

    # Connection status
    connected = db_connected()
    col1, col2 = st.columns([1, 3])
    with col1:
        if connected:
            st.success("✅ Database Connected")
        else:
            st.warning("⚠️ Demo Mode (no DB)")

    st.markdown("---")

    # KPI tiles
    gh = get_github_events()
    hn = get_hn_stories()
    log = get_ingestion_log()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("GitHub Events", f"{len(gh):,}")
    k2.metric("HN Stories", f"{len(hn):,}")
    k3.metric("Pipeline Runs", f"{len(log):,}")
    k4.metric("Avg HN Score", f"{hn['score'].mean():.0f}" if len(hn) else "—")

    st.markdown("---")
    st.subheader("Recent Pipeline Runs")
    st.dataframe(log[["pipeline","source","records_fetched","records_inserted","status","started_at"]].head(10), use_container_width=True)

    st.markdown("---")
    st.subheader("Architecture Overview")
    st.code("""
  GitHub API ──┐
               ├─► Python Ingestor ─► PostgreSQL ─► dbt ─► Streamlit
  HN API ──────┘         │
                         └── Validation + Logging
    """)

    st.subheader("Project Stack")
    cols = st.columns(5)
    for i, tech in enumerate(["Python 3.11","PostgreSQL","dbt","Streamlit","Docker"]):
        cols[i].info(tech)
