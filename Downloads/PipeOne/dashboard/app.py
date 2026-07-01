"""
PipeOne Streamlit Dashboard — entry point.

Run:
    streamlit run dashboard/app.py

Pages:
    Home            — KPIs, pipeline health, architecture
    GitHub          — event analytics with Plotly charts
    Hacker News     — story analytics with Plotly charts
    Combined        — cross-source insights and trending data
"""
import os
import sys

# Ensure the project root is on sys.path when launched from any directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="PipeOne Analytics",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Dark mode toggle (applied before any content renders) ─────────────────────
dark = st.sidebar.checkbox("🌙 Dark Mode", value=True)
if dark:
    st.markdown(
        """
        <style>
        body, .stApp, [data-testid="stAppViewContainer"] {
            background-color: #0e1117;
            color: #fafafa;
        }
        [data-testid="stSidebar"] {
            background-color: #161b22;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ── Sidebar navigation ─────────────────────────────────────────────────────────
st.sidebar.title("🚀 PipeOne")
st.sidebar.caption("APIs → PostgreSQL → dbt → Dashboard")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "🐙 GitHub Analytics", "📰 Hacker News", "🔗 Combined Dashboard"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")

# Show connection status in sidebar
from dashboard.db_queries import db_connected
if db_connected():
    st.sidebar.success("🟢 Database connected")
else:
    st.sidebar.warning("🟡 Demo mode (no DB)")

st.sidebar.markdown("---")
st.sidebar.caption(
    "**H1 — PipeOne**\n\n"
    "Foundations of Data Engineering\n\n"
    "GitHub + HN → PostgreSQL → dbt → Streamlit"
)

# ── Page routing ───────────────────────────────────────────────────────────────
if page == "🏠 Home":
    from dashboard.pages.home import render
elif page == "🐙 GitHub Analytics":
    from dashboard.pages.github import render
elif page == "📰 Hacker News":
    from dashboard.pages.hackernews import render
else:
    from dashboard.pages.combined import render

render()
