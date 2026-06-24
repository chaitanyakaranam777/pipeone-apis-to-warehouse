"""GitHub Analytics page."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dashboard.db_utils import (
    get_github_events, get_github_event_types,
    get_github_top_repos, get_github_top_actors, get_github_timeline,
)


def render():
    st.title("🐙 GitHub Analytics")
    st.markdown("Insights from the GitHub Public Events API")
    st.markdown("---")

    # ── Event type distribution ────────────────────────────────────────────────
    st.subheader("Event Type Distribution")
    et_df = get_github_event_types()
    if not et_df.empty:
        fig = px.bar(
            et_df, x="event_type", y="count",
            color="event_type",
            labels={"event_type": "Event Type", "count": "Count"},
            template="plotly_dark",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No GitHub event data found.")

    col1, col2 = st.columns(2)

    # ── Top repos ─────────────────────────────────────────────────────────────
    with col1:
        st.subheader("🏆 Top Repositories by Activity")
        repo_df = get_github_top_repos()
        if not repo_df.empty:
            fig2 = px.bar(
                repo_df.head(15), x="events", y="repo_name",
                orientation="h",
                color="unique_actors",
                color_continuous_scale="Viridis",
                labels={"events": "Events", "repo_name": "Repository"},
                template="plotly_dark",
            )
            fig2.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig2, use_container_width=True)

    # ── Top actors ────────────────────────────────────────────────────────────
    with col2:
        st.subheader("👤 Top Actors")
        actor_df = get_github_top_actors()
        if not actor_df.empty:
            fig3 = px.scatter(
                actor_df, x="events", y="repos",
                size="event_types", hover_name="actor_login",
                color="events",
                color_continuous_scale="Blues",
                labels={"events": "Total Events", "repos": "Unique Repos"},
                template="plotly_dark",
            )
            st.plotly_chart(fig3, use_container_width=True)

    # ── Timeline ──────────────────────────────────────────────────────────────
    st.subheader("📈 Event Activity Timeline")
    tl_df = get_github_timeline()
    if not tl_df.empty:
        fig4 = px.area(
            tl_df, x="hour", y="events",
            labels={"hour": "Time", "events": "Events"},
            template="plotly_dark",
            color_discrete_sequence=["#4CAF50"],
        )
        st.plotly_chart(fig4, use_container_width=True)

    # ── Search & Filter ───────────────────────────────────────────────────────
    st.subheader("🔍 Search Events")
    raw_df = get_github_events()
    if not raw_df.empty:
        search = st.text_input("Filter by repo name or actor", "")
        event_filter = st.multiselect(
            "Event types",
            options=raw_df["event_type"].unique().tolist(),
            default=[],
        )
        filtered = raw_df.copy()
        if search:
            mask = (
                filtered["repo_name"].str.contains(search, case=False, na=False)
                | filtered["actor_login"].str.contains(search, case=False, na=False)
            )
            filtered = filtered[mask]
        if event_filter:
            filtered = filtered[filtered["event_type"].isin(event_filter)]
        st.dataframe(filtered.head(200), use_container_width=True)
