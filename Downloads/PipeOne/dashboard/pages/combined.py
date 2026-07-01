"""
Combined Dashboard — cross-source GitHub + HN analytics.
Queries mart_combined_activity and mart_repo_leaderboard (dbt)
with raw table fallbacks.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dashboard.db_queries import (
    get_github_events_raw,
    get_hn_stories,
    get_combined_activity,
    get_repo_leaderboard,
    get_ingestion_log,
)


def render():
    st.title("🔗 Combined Dashboard")
    st.caption("Cross-source insights: GitHub Events + Hacker News — powered by dbt marts")

    gh = get_github_events_raw()
    hn = get_hn_stories()
    combined = get_combined_activity()
    repos = get_repo_leaderboard()
    log = get_ingestion_log()

    # ── Platform comparison KPIs ──────────────────────────────────────────────
    st.subheader("Platform Comparison")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("GH Events", f"{len(gh):,}", help="Total GitHub events ingested")
    c2.metric(
        "GH Actors",
        f"{gh['actor_login'].nunique():,}" if "actor_login" in gh.columns else "—",
    )
    c3.metric(
        "GH Repos",
        f"{gh['repo_name'].nunique():,}" if "repo_name" in gh.columns else "—",
    )
    c4.metric("HN Stories", f"{len(hn):,}", help="Total HN stories ingested")
    c5.metric(
        "HN Avg Score",
        f"{hn['score'].mean():.0f}" if len(hn) > 0 else "—",
    )
    c6.metric(
        "HN Avg Comments",
        f"{hn['comment_count'].mean():.0f}" if len(hn) > 0 else "—",
    )

    st.markdown("---")

    # ── Cross-source activity timeline ────────────────────────────────────────
    st.subheader("📈 Activity Over Time — GitHub vs Hacker News")

    if not combined.empty and "activity_date" in combined.columns:
        fig = go.Figure()

        if "github_events" in combined.columns:
            fig.add_trace(go.Scatter(
                x=combined["activity_date"],
                y=combined["github_events"],
                name="GitHub Events",
                line=dict(color="#6cc644", width=2),
                fill="tozeroy",
                fillcolor="rgba(108, 198, 68, 0.1)",
            ))

        if "hn_stories" in combined.columns:
            fig.add_trace(go.Scatter(
                x=combined["activity_date"],
                y=combined["hn_stories"],
                name="HN Stories",
                line=dict(color="#ff6600", width=2),
                fill="tozeroy",
                fillcolor="rgba(255, 102, 0, 0.1)",
                yaxis="y2",
            ))

        fig.update_layout(
            height=380,
            margin=dict(t=20, b=40),
            legend=dict(orientation="h", y=1.08),
            yaxis=dict(title="GitHub Events", titlefont=dict(color="#6cc644")),
            yaxis2=dict(
                title="HN Stories",
                titlefont=dict(color="#ff6600"),
                overlaying="y",
                side="right",
            ),
            xaxis_title="Date",
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Combined activity data not available yet.")

    st.markdown("---")

    # ── Trending repos + top HN ───────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔥 Trending GitHub Repositories")
        if not repos.empty and "repo_name" in repos.columns:
            top_repos = repos.head(15).copy()
            fig2 = px.bar(
                top_repos,
                x="total_events",
                y="repo_name",
                orientation="h",
                color="total_events",
                color_continuous_scale="greens",
                labels={"total_events": "Events", "repo_name": ""},
            )
            fig2.update_layout(
                yaxis={"categoryorder": "total ascending"},
                height=420,
                margin=dict(t=10, b=20),
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No repository data available.")

    with col2:
        st.subheader("🏆 Top Hacker News Stories")
        if not hn.empty:
            cols = [c for c in ["title", "score", "comment_count", "domain"] if c in hn.columns]
            top_hn = hn.sort_values("score", ascending=False)[cols].head(15).reset_index(drop=True)
            top_hn.index += 1
            st.dataframe(top_hn, use_container_width=True, height=420)
        else:
            st.info("No HN story data available.")

    st.markdown("---")

    # ── Event type treemap ────────────────────────────────────────────────────
    if not gh.empty and "event_type" in gh.columns:
        st.subheader("GitHub Event Type Breakdown")
        et = gh["event_type"].value_counts().reset_index()
        et.columns = ["event_type", "count"]
        fig3 = px.treemap(
            et, path=["event_type"], values="count",
            color="count",
            color_continuous_scale="greens",
            title="",
        )
        fig3.update_layout(height=360, margin=dict(t=10, b=10))
        st.plotly_chart(fig3, use_container_width=True)

    # ── HN domain vs GitHub repo activity side-by-side ────────────────────────
    st.subheader("Domain & Repo Activity Comparison")
    col3, col4 = st.columns(2)

    with col3:
        if not hn.empty and "domain" in hn.columns:
            dom = hn["domain"].value_counts().head(10).reset_index()
            dom.columns = ["domain", "stories"]
            fig4 = px.pie(
                dom, names="domain", values="stories",
                title="HN: Stories by Domain",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.3,
            )
            fig4.update_layout(height=340, margin=dict(t=40, b=10))
            st.plotly_chart(fig4, use_container_width=True)

    with col4:
        if not gh.empty and "event_type" in gh.columns:
            et2 = gh["event_type"].value_counts().head(8).reset_index()
            et2.columns = ["event_type", "count"]
            fig5 = px.pie(
                et2, names="event_type", values="count",
                title="GitHub: Events by Type",
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.3,
            )
            fig5.update_layout(height=340, margin=dict(t=40, b=10))
            st.plotly_chart(fig5, use_container_width=True)

    st.markdown("---")

    # ── Pipeline health summary ────────────────────────────────────────────────
    st.subheader("🔧 Pipeline Health")
    if not log.empty:
        # Success rate by pipeline
        if "status" in log.columns and "pipeline" in log.columns:
            health = log.groupby(["pipeline", "status"]).size().reset_index(name="runs")
            fig6 = px.bar(
                health, x="pipeline", y="runs", color="status",
                color_discrete_map={"success": "#00CC96", "failed": "#EF553B"},
                barmode="group",
                labels={"pipeline": "Pipeline", "runs": "Runs", "status": "Status"},
                title="Pipeline Runs: Success vs Failure",
            )
            fig6.update_layout(height=300, margin=dict(t=40, b=20))
            st.plotly_chart(fig6, use_container_width=True)

        status_cols = [c for c in ["pipeline", "records_fetched", "records_inserted", "status", "started_at"] if c in log.columns]
        st.dataframe(log[status_cols].head(10), use_container_width=True)
    else:
        st.info("No pipeline run history yet.")
