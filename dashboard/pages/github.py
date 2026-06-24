"""GitHub Analytics page."""
import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.db_queries import get_github_events


def render():
    st.title("🐙 GitHub Analytics")

    df = get_github_events()
    if df.empty:
        st.warning("No GitHub data available.")
        return

    # Ensure datetime
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
        df["hour"] = df["created_at"].dt.floor("h")
        df["date"] = df["created_at"].dt.date

    # Filters
    st.sidebar.subheader("Filters")
    event_types = sorted(df["event_type"].dropna().unique().tolist()) if "event_type" in df.columns else []
    selected_types = st.sidebar.multiselect("Event Types", event_types, default=event_types)
    if selected_types:
        df = df[df["event_type"].isin(selected_types)]

    # KPIs
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Events", f"{len(df):,}")
    k2.metric("Unique Actors", f"{df['actor_login'].nunique():,}" if "actor_login" in df.columns else "—")
    k3.metric("Unique Repos", f"{df['repo_name'].nunique():,}" if "repo_name" in df.columns else "—")

    st.markdown("---")

    # Event type distribution
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Events by Type")
        type_counts = df["event_type"].value_counts().reset_index()
        type_counts.columns = ["event_type", "count"]
        fig = px.bar(type_counts, x="event_type", y="count", color="event_type",
                     labels={"event_type": "Event Type", "count": "Count"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Event Type Share")
        fig2 = px.pie(type_counts, names="event_type", values="count")
        st.plotly_chart(fig2, use_container_width=True)

    # Timeline
    if "date" in df.columns:
        st.subheader("Events Over Time")
        daily = df.groupby("date").size().reset_index(name="events")
        fig3 = px.line(daily, x="date", y="events", markers=True)
        st.plotly_chart(fig3, use_container_width=True)

    # Top actors
    if "actor_login" in df.columns:
        st.subheader("Top 15 Most Active Users")
        top_actors = df["actor_login"].value_counts().head(15).reset_index()
        top_actors.columns = ["actor", "events"]
        fig4 = px.bar(top_actors, x="events", y="actor", orientation="h",
                      color="events", color_continuous_scale="blues")
        fig4.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig4, use_container_width=True)

    # Search
    st.subheader("Search Events")
    search = st.text_input("Filter by repo or actor name")
    if search:
        mask = (
            df.get("repo_name", pd.Series(dtype=str)).str.contains(search, case=False, na=False) |
            df.get("actor_login", pd.Series(dtype=str)).str.contains(search, case=False, na=False)
        )
        st.dataframe(df[mask].head(50), use_container_width=True)
    else:
        st.dataframe(df.head(50), use_container_width=True)
