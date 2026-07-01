"""
Hacker News Analytics page.
Queries mart_hn_top_stories (dbt) with raw table fallback.
All charts use Plotly for interactive visualisations.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dashboard.db_queries import get_hn_stories


def render():
    st.title("📰 Hacker News Analytics")
    st.caption("Source: Hacker News Firebase API → hn_stories_raw → dbt mart")

    df = get_hn_stories()

    if df.empty:
        st.warning("No Hacker News data available. Run the pipeline to ingest data.")
        return

    # Parse datetimes
    if "time_posted" in df.columns:
        df["time_posted"] = pd.to_datetime(df["time_posted"], errors="coerce", utc=True)
        df["date"] = df["time_posted"].dt.date
        df["hour"] = df["time_posted"].dt.hour

    # ── Sidebar filters ───────────────────────────────────────────────────────
    st.sidebar.subheader("🔍 HN Filters")

    max_score = int(df["score"].max()) if len(df) > 0 else 500
    min_score = st.sidebar.slider(
        "Minimum Score", 0, max_score, 0,
        help="Only show stories at or above this score"
    )
    df = df[df["score"] >= min_score]

    if "story_type" in df.columns:
        types = sorted(df["story_type"].dropna().unique().tolist())
        sel_types = st.sidebar.multiselect("Story Type", types, default=types)
        if sel_types:
            df = df[df["story_type"].isin(sel_types)]

    # ── KPI row ───────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Stories", f"{len(df):,}")
    k2.metric(
        "Avg Score",
        f"{df['score'].mean():.1f}" if len(df) > 0 else "—",
    )
    k3.metric(
        "Avg Comments",
        f"{df['comment_count'].mean():.1f}" if len(df) > 0 else "—",
    )
    k4.metric(
        "Unique Authors",
        f"{df['author'].nunique():,}" if "author" in df.columns else "—",
    )

    st.markdown("---")

    # ── Row 1: Score histogram + top domains ──────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Score Distribution")
        fig = px.histogram(
            df, x="score", nbins=30,
            color_discrete_sequence=["#ff6600"],
            labels={"score": "Score", "count": "Stories"},
        )
        fig.update_layout(height=320, margin=dict(t=10, b=40), bargap=0.1)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top 10 Domains")
        if "domain" in df.columns:
            dom = df["domain"].value_counts().head(10).reset_index()
            dom.columns = ["domain", "count"]
            fig2 = px.bar(
                dom, x="count", y="domain", orientation="h",
                color="count", color_continuous_scale="oranges",
                labels={"count": "Stories", "domain": ""},
            )
            fig2.update_layout(
                yaxis={"categoryorder": "total ascending"},
                height=320, margin=dict(t=10, b=20),
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig2, use_container_width=True)

    # ── Score vs Comments scatter ─────────────────────────────────────────────
    st.subheader("Score vs Comments")
    hover_cols = [c for c in ["title", "author", "domain"] if c in df.columns]
    fig3 = px.scatter(
        df, x="score", y="comment_count",
        hover_data=hover_cols if hover_cols else None,
        color="score",
        color_continuous_scale="reds",
        size="comment_count" if "comment_count" in df.columns else None,
        size_max=25,
        labels={"score": "Score", "comment_count": "Comments"},
        opacity=0.7,
    )
    fig3.update_layout(height=380, margin=dict(t=10, b=40))
    st.plotly_chart(fig3, use_container_width=True)

    # ── Row 2: Stories over time + story type breakdown ───────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Stories Over Time")
        if "date" in df.columns and df["date"].notna().any():
            daily = df.groupby("date").agg(
                stories=("hn_id" if "hn_id" in df.columns else "score", "count"),
                avg_score=("score", "mean"),
            ).reset_index()
            fig4 = px.area(
                daily, x="date", y="stories",
                color_discrete_sequence=["#ff6600"],
                labels={"date": "Date", "stories": "Stories"},
            )
            fig4.update_layout(height=300, margin=dict(t=10, b=40))
            st.plotly_chart(fig4, use_container_width=True)

    with col4:
        st.subheader("Story Type Breakdown")
        if "story_type" in df.columns:
            type_counts = df["story_type"].value_counts().reset_index()
            type_counts.columns = ["story_type", "count"]
            fig5 = px.pie(
                type_counts, names="story_type", values="count",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.35,
            )
            fig5.update_layout(height=300, margin=dict(t=10, b=10))
            st.plotly_chart(fig5, use_container_width=True)

    # ── Top stories table ─────────────────────────────────────────────────────
    st.subheader("🏆 Top Stories by Score")
    table_cols = [c for c in ["title", "score", "comment_count", "author", "domain", "story_type"] if c in df.columns]
    top_stories = df.sort_values("score", ascending=False)[table_cols].head(25).reset_index(drop=True)
    top_stories.index += 1  # 1-based ranking
    st.dataframe(top_stories, use_container_width=True)

    # ── Domain enrichment (from mart) ─────────────────────────────────────────
    if "domain_avg_score" in df.columns:
        st.subheader("Domain Performance (dbt Enriched)")
        domain_perf = (
            df[["domain", "domain_story_count", "domain_avg_score", "domain_max_score"]]
            .drop_duplicates("domain")
            .sort_values("domain_avg_score", ascending=False)
            .head(15)
        )
        fig6 = px.bar(
            domain_perf, x="domain_avg_score", y="domain",
            orientation="h",
            color="domain_avg_score",
            color_continuous_scale="Oranges",
            labels={"domain_avg_score": "Avg Score", "domain": ""},
            title="Average Score by Domain",
        )
        fig6.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=380, margin=dict(t=40, b=20),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig6, use_container_width=True)

    # ── Search ────────────────────────────────────────────────────────────────
    st.subheader("🔎 Search Stories")
    q = st.text_input("Search by title or author", placeholder="e.g. PostgreSQL or dbt")
    if q:
        mask = (
            df.get("title", pd.Series(dtype=str)).str.contains(q, case=False, na=False)
            | df.get("author", pd.Series(dtype=str)).str.contains(q, case=False, na=False)
        )
        results = df[mask]
        st.caption(f"{len(results):,} results for '{q}'")
        st.dataframe(results[table_cols].reset_index(drop=True), use_container_width=True)
