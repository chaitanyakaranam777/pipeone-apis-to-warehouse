"""
GitHub Analytics page.
Queries mart_github_summary (dbt) with raw table fallback.
All charts use Plotly for interactive visualisations.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dashboard.db_queries import get_github_events, get_github_events_raw, get_repo_leaderboard


def render():
    st.title("🐙 GitHub Analytics")
    st.caption("Source: GitHub Public Events API → github_events_raw → dbt mart")

    # Raw events for detail views
    raw = get_github_events_raw()

    # Mart/summary data for aggregated charts
    summary = get_github_events()

    if raw.empty:
        st.warning("No GitHub data available. Run the pipeline to ingest data.")
        return

    # Parse datetimes on raw
    if "created_at" in raw.columns:
        raw["created_at"] = pd.to_datetime(raw["created_at"], errors="coerce", utc=True)
        raw["date"] = raw["created_at"].dt.date
        raw["hour"] = raw["created_at"].dt.hour

    # ── Sidebar filters ───────────────────────────────────────────────────────
    st.sidebar.subheader("🔍 GitHub Filters")
    if "event_type" in raw.columns:
        all_types = sorted(raw["event_type"].dropna().unique().tolist())
        selected_types = st.sidebar.multiselect(
            "Event Types", all_types, default=all_types,
            help="Filter by GitHub event type"
        )
        if selected_types:
            raw = raw[raw["event_type"].isin(selected_types)]

    if "actor_login" in raw.columns and len(raw) > 0:
        top_actors = raw["actor_login"].value_counts().head(20).index.tolist()
        actor_filter = st.sidebar.multiselect(
            "Filter by Actor", top_actors,
            help="Filter to specific users (top 20 shown)"
        )
        if actor_filter:
            raw = raw[raw["actor_login"].isin(actor_filter)]

    # ── KPI row ───────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Events", f"{len(raw):,}")
    k2.metric(
        "Unique Actors",
        f"{raw['actor_login'].nunique():,}" if "actor_login" in raw.columns else "—",
    )
    k3.metric(
        "Unique Repos",
        f"{raw['repo_name'].nunique():,}" if "repo_name" in raw.columns else "—",
    )
    k4.metric(
        "Event Types",
        f"{raw['event_type'].nunique()}" if "event_type" in raw.columns else "—",
    )

    st.markdown("---")

    # ── Row 1: Event type bar + pie ───────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Events by Type")
        if "event_type" in raw.columns:
            tc = raw["event_type"].value_counts().reset_index()
            tc.columns = ["event_type", "count"]
            fig = px.bar(
                tc, x="event_type", y="count", color="event_type",
                color_discrete_sequence=px.colors.qualitative.Plotly,
                labels={"event_type": "Type", "count": "Events"},
            )
            fig.update_layout(showlegend=False, height=320, margin=dict(t=10, b=40))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Event Type Share")
        if "event_type" in raw.columns:
            fig2 = px.pie(
                tc, names="event_type", values="count",
                color_discrete_sequence=px.colors.qualitative.Plotly,
                hole=0.35,
            )
            fig2.update_layout(height=320, margin=dict(t=10, b=10))
            st.plotly_chart(fig2, use_container_width=True)

    # ── Events over time ──────────────────────────────────────────────────────
    if "date" in raw.columns and raw["date"].notna().any():
        st.subheader("Events Over Time")
        daily = raw.groupby("date").size().reset_index(name="events")
        fig3 = px.area(
            daily, x="date", y="events",
            color_discrete_sequence=["#636EFA"],
            labels={"date": "Date", "events": "Event Count"},
        )
        fig3.update_layout(height=280, margin=dict(t=10, b=40))
        st.plotly_chart(fig3, use_container_width=True)

    # ── Row 2: Top actors + hourly heatmap ────────────────────────────────────
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Top 15 Most Active Users")
        if "actor_login" in raw.columns:
            top = raw["actor_login"].value_counts().head(15).reset_index()
            top.columns = ["actor", "events"]
            fig4 = px.bar(
                top, x="events", y="actor", orientation="h",
                color="events", color_continuous_scale="blues",
                labels={"events": "Events", "actor": ""},
            )
            fig4.update_layout(
                yaxis={"categoryorder": "total ascending"},
                height=380, margin=dict(t=10, b=20),
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig4, use_container_width=True)

    with col4:
        st.subheader("Activity by Hour of Day")
        if "hour" in raw.columns:
            hourly = raw.groupby("hour").size().reset_index(name="events")
            fig5 = px.bar(
                hourly, x="hour", y="events",
                color="events", color_continuous_scale="viridis",
                labels={"hour": "Hour (UTC)", "events": "Events"},
            )
            fig5.update_layout(
                height=380, margin=dict(t=10, b=40),
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig5, use_container_width=True)

    # ── Top repositories ──────────────────────────────────────────────────────
    st.subheader("🏆 Top Repositories by Activity")
    repo_df = get_repo_leaderboard()
    if not repo_df.empty and "repo_name" in repo_df.columns:
        show_cols = [c for c in ["repo_name", "total_events", "unique_contributors", "event_type_count"] if c in repo_df.columns]
        st.dataframe(repo_df[show_cols].head(15), use_container_width=True)

    # ── Event type over time (stacked) ────────────────────────────────────────
    if "date" in raw.columns and "event_type" in raw.columns and raw["date"].notna().any():
        st.subheader("Event Types Over Time")
        daily_type = (
            raw.groupby(["date", "event_type"])
            .size()
            .reset_index(name="count")
        )
        fig6 = px.bar(
            daily_type, x="date", y="count", color="event_type",
            barmode="stack",
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={"date": "Date", "count": "Events", "event_type": "Type"},
        )
        fig6.update_layout(height=320, margin=dict(t=10, b=40))
        st.plotly_chart(fig6, use_container_width=True)

    # ── Search ────────────────────────────────────────────────────────────────
    st.subheader("🔎 Search Events")
    query = st.text_input("Filter by repository name or actor login", placeholder="e.g. torvalds or linux")
    display = raw
    if query:
        mask = (
            raw.get("repo_name", pd.Series(dtype=str)).str.contains(query, case=False, na=False)
            | raw.get("actor_login", pd.Series(dtype=str)).str.contains(query, case=False, na=False)
        )
        display = raw[mask]
        st.caption(f"{len(display):,} results for '{query}'")

    show_raw_cols = [c for c in ["event_type", "actor_login", "repo_name", "created_at"] if c in display.columns]
    st.dataframe(display[show_raw_cols].head(100), use_container_width=True)
