"""Hacker News Analytics page."""
import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.db_queries import get_hn_stories


def render():
    st.title("📰 Hacker News Analytics")

    df = get_hn_stories()
    if df.empty:
        st.warning("No HN data available.")
        return

    if "time_posted" in df.columns:
        df["time_posted"] = pd.to_datetime(df["time_posted"], errors="coerce", utc=True)

    # Sidebar filters
    min_score = st.sidebar.slider("Min Score", 0, int(df["score"].max() or 500), 10)
    df = df[df["score"] >= min_score]

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Stories", f"{len(df):,}")
    k2.metric("Avg Score", f"{df['score'].mean():.1f}")
    k3.metric("Avg Comments", f"{df['comment_count'].mean():.1f}")
    k4.metric("Unique Authors", f"{df['author'].nunique():,}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Score Distribution")
        fig = px.histogram(df, x="score", nbins=30, color_discrete_sequence=["#ff6600"])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top Domains")
        if "domain" in df.columns:
            domain_counts = df["domain"].value_counts().head(10).reset_index()
            domain_counts.columns = ["domain", "count"]
            fig2 = px.bar(domain_counts, x="count", y="domain", orientation="h",
                          color="count", color_continuous_scale="oranges")
            fig2.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig2, use_container_width=True)

    # Score vs comments scatter
    st.subheader("Score vs Comments")
    fig3 = px.scatter(df, x="score", y="comment_count", hover_data=["title"],
                      color="score", color_continuous_scale="reds",
                      labels={"score": "Score", "comment_count": "Comments"})
    st.plotly_chart(fig3, use_container_width=True)

    # Top stories table
    st.subheader("Top Stories")
    cols_to_show = [c for c in ["title", "score", "comment_count", "author", "domain"] if c in df.columns]
    st.dataframe(df.sort_values("score", ascending=False)[cols_to_show].head(20), use_container_width=True)

    # Search
    st.subheader("Search Stories")
    query = st.text_input("Search by title or author")
    if query:
        mask = (
            df.get("title", pd.Series(dtype=str)).str.contains(query, case=False, na=False) |
            df.get("author", pd.Series(dtype=str)).str.contains(query, case=False, na=False)
        )
        st.dataframe(df[mask][cols_to_show], use_container_width=True)
