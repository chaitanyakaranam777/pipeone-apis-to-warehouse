"""Combined Dashboard — GitHub + HN cross-source analytics."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dashboard.db_queries import get_github_events, get_hn_stories


def render():
    st.title("🔗 Combined Dashboard")
    st.caption("GitHub Events + Hacker News — side-by-side insights")

    gh = get_github_events()
    hn = get_hn_stories()

    # ── Trending repos on GitHub ──────────────────────────────────────────────
    st.subheader("🔥 Trending GitHub Repositories (by event volume)")
    if "repo_name" in gh.columns:
        trending = gh["repo_name"].value_counts().head(10).reset_index()
        trending.columns = ["repository", "events"]
        fig = px.bar(trending, x="events", y="repository", orientation="h",
                     color="events", color_continuous_scale="greens",
                     title="Most Active Repositories")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    # ── Top HN stories ────────────────────────────────────────────────────────
    st.subheader("🏆 Trending Hacker News Stories")
    if not hn.empty:
        top = hn.sort_values("score", ascending=False).head(10)
        cols_to_show = [c for c in ["title", "score", "comment_count", "domain"] if c in top.columns]
        st.dataframe(top[cols_to_show].reset_index(drop=True), use_container_width=True)

    st.markdown("---")

    # ── Side-by-side KPI comparison ───────────────────────────────────────────
    st.subheader("Platform Comparison")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**GitHub**")
        st.metric("Total Events", f"{len(gh):,}")
        st.metric("Unique Actors", f"{gh['actor_login'].nunique():,}" if "actor_login" in gh.columns else "—")
        st.metric("Unique Repos", f"{gh['repo_name'].nunique():,}" if "repo_name" in gh.columns else "—")
    with c2:
        st.markdown("**Hacker News**")
        st.metric("Total Stories", f"{len(hn):,}")
        st.metric("Avg Score", f"{hn['score'].mean():.1f}")
        st.metric("Avg Comments", f"{hn['comment_count'].mean():.1f}")

    # ── Combined activity timeline ────────────────────────────────────────────
    st.subheader("Activity Over Time")
    fig2 = go.Figure()

    if "created_at" in gh.columns:
        gh["created_at"] = pd.to_datetime(gh["created_at"], errors="coerce", utc=True)
        gh_daily = gh.groupby(gh["created_at"].dt.date).size().reset_index(name="github_events")
        fig2.add_trace(go.Scatter(x=gh_daily["created_at"], y=gh_daily["github_events"],
                                  name="GitHub Events", line=dict(color="#6cc644")))

    if "time_posted" in hn.columns:
        hn["time_posted"] = pd.to_datetime(hn["time_posted"], errors="coerce", utc=True)
        hn_daily = hn.groupby(hn["time_posted"].dt.date).size().reset_index(name="hn_stories")
        fig2.add_trace(go.Scatter(x=hn_daily["time_posted"], y=hn_daily["hn_stories"],
                                  name="HN Stories", line=dict(color="#ff6600")))

    fig2.update_layout(xaxis_title="Date", yaxis_title="Count", legend_title="Source")
    st.plotly_chart(fig2, use_container_width=True)

    # ── GitHub event type breakdown ───────────────────────────────────────────
    if "event_type" in gh.columns:
        st.subheader("GitHub Event Type Breakdown")
        et = gh["event_type"].value_counts().reset_index()
        et.columns = ["event_type", "count"]
        fig3 = px.treemap(et, path=["event_type"], values="count",
                          color="count", color_continuous_scale="greens")
        st.plotly_chart(fig3, use_container_width=True)
