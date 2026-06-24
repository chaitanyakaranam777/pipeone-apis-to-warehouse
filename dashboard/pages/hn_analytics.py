"""Hacker News Analytics page."""
import streamlit as st
import plotly.express as px
from dashboard.db_utils import get_hn_stories, get_hn_score_distribution, get_hn_top_authors


def render():
    st.title("📰 Hacker News Analytics")
    st.markdown("Insights from the Hacker News Firebase API — top stories, scores & authors.")
    st.markdown("---")

    stories_df = get_hn_stories()

    if stories_df.empty:
        st.info("No Hacker News data found. Run the ingestion pipeline first.")
        return

    # ── KPIs ──────────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Stories", f"{len(stories_df):,}")
    col2.metric("Max Score", f"{int(stories_df['score'].max()):,}")
    col3.metric("Avg Comments", f"{stories_df['comment_count'].mean():.1f}")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    # ── Score tier pie ─────────────────────────────────────────────────────────
    with col_left:
        st.subheader("Score Tier Breakdown")
        tier_df = get_hn_score_distribution()
        if not tier_df.empty:
            fig = px.pie(
                tier_df, names="tier", values="count",
                color_discrete_sequence=px.colors.sequential.Oranges_r,
                template="plotly_dark",
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── Top authors ───────────────────────────────────────────────────────────
    with col_right:
        st.subheader("Top Authors")
        auth_df = get_hn_top_authors()
        if not auth_df.empty:
            fig2 = px.bar(
                auth_df.head(15), x="stories", y="author",
                orientation="h",
                color="avg_score",
                color_continuous_scale="Oranges",
                labels={"stories": "Stories", "author": "Author"},
                template="plotly_dark",
            )
            fig2.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig2, use_container_width=True)

    # ── Score vs comments scatter ─────────────────────────────────────────────
    st.subheader("Score vs. Comments")
    fig3 = px.scatter(
        stories_df, x="score", y="comment_count",
        hover_name="title",
        color="story_type",
        template="plotly_dark",
        labels={"score": "Score", "comment_count": "Comments"},
        opacity=0.7,
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ── Top stories table ─────────────────────────────────────────────────────
    st.subheader("🔥 Top Stories")
    search = st.text_input("Search story titles", "")
    show_df = stories_df.copy()
    if search:
        show_df = show_df[show_df["title"].str.contains(search, case=False, na=False)]
    st.dataframe(
        show_df[["title", "score", "comment_count", "author", "url", "time_posted"]].head(100),
        use_container_width=True,
    )
