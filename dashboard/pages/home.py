"""
Home page — KPIs, pipeline health, architecture overview.
Queries mart_pipeline_health (dbt) with raw table fallback.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.db_queries import (
    get_github_events_raw,
    get_hn_stories,
    get_ingestion_log,
    db_connected,
)


def render():
    st.title("🚀 PipeOne — Data Pipeline Dashboard")
    st.markdown("**H1 Project · Foundations of Data Engineering · APIs → Warehouse**")

    # ── Connection status ─────────────────────────────────────────────────────
    connected = db_connected()
    if connected:
        st.success("✅ PostgreSQL connected — showing live data")
    else:
        st.info(
            "⚠️ **Demo Mode** — PostgreSQL not detected. "
            "Run `docker compose up` or `python ingestion/pipeline.py` to load real data."
        )

    st.markdown("---")

    # ── KPI tiles ─────────────────────────────────────────────────────────────
    gh = get_github_events_raw()
    hn = get_hn_stories()
    log = get_ingestion_log()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(
        "GitHub Events",
        f"{len(gh):,}",
        help="Total events in github_events_raw",
    )
    k2.metric(
        "HN Stories",
        f"{len(hn):,}",
        help="Total stories in hn_stories_raw",
    )
    k3.metric(
        "Pipeline Runs",
        f"{len(log):,}",
        help="Rows in ingestion_log",
    )
    k4.metric(
        "Avg HN Score",
        f"{hn['score'].mean():.0f}" if len(hn) > 0 else "—",
        help="Mean score across all ingested stories",
    )

    st.markdown("---")

    # ── Pipeline health chart ─────────────────────────────────────────────────
    st.subheader("Pipeline Run History")
    if not log.empty:
        # Records inserted per run
        chart_cols = [c for c in ["pipeline", "records_fetched", "records_inserted", "status"] if c in log.columns]
        display_log = log[chart_cols].head(10).copy()

        if "records_inserted" in display_log.columns and "records_fetched" in display_log.columns:
            fig = px.bar(
                display_log.head(10).reset_index(drop=True),
                x=display_log.head(10).index,
                y=["records_fetched", "records_inserted"] if "records_fetched" in display_log.columns else ["records_inserted"],
                barmode="overlay",
                labels={"value": "Records", "index": "Run #", "variable": "Metric"},
                color_discrete_map={"records_fetched": "#636EFA", "records_inserted": "#00CC96"},
                title="Records Fetched vs Inserted per Run",
            )
            fig.update_layout(height=300, margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)

        status_cols = [c for c in ["pipeline", "source", "records_fetched", "records_inserted", "records_skipped", "status", "started_at"] if c in log.columns]
        st.dataframe(log[status_cols].head(10), use_container_width=True)
    else:
        st.info("No pipeline runs recorded yet. Run `python ingestion/pipeline.py` to start.")

    st.markdown("---")

    # ── Event type quick breakdown ────────────────────────────────────────────
    if not gh.empty and "event_type" in gh.columns:
        st.subheader("Quick GitHub Event Breakdown")
        et = gh["event_type"].value_counts().reset_index()
        et.columns = ["event_type", "count"]
        fig2 = px.pie(et.head(8), names="event_type", values="count",
                      title="Event Types Ingested",
                      color_discrete_sequence=px.colors.qualitative.Set3)
        fig2.update_layout(height=320, margin=dict(t=40, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Architecture ──────────────────────────────────────────────────────────
    st.subheader("Pipeline Architecture")
    st.code(
        "GitHub API  ──┐\n"
        "              ├──► Python ETL ──► PostgreSQL ──► dbt ──► Streamlit\n"
        "HN API ───────┘         │\n"
        "                        └── Validate + Deduplicate + ingestion_log",
        language="text",
    )

    # ── Tech stack ────────────────────────────────────────────────────────────
    st.subheader("Tech Stack")
    cols = st.columns(5)
    stack = [
        ("Python 3.11", "🐍"),
        ("PostgreSQL", "🐘"),
        ("dbt", "⚙️"),
        ("Streamlit", "📊"),
        ("Docker", "🐳"),
    ]
    for col, (tech, icon) in zip(cols, stack):
        col.info(f"{icon} {tech}")
