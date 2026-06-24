"""
PipeOne Streamlit Dashboard — multi-page analytics app.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="PipeOne Analytics",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar nav ──────────────────────────────────────────────────────────────
PAGES = {
    "🏠 Home": "home",
    "🐙 GitHub Analytics": "github",
    "📰 Hacker News Analytics": "hackernews",
    "🔗 Combined Dashboard": "combined",
}

st.sidebar.title("PipeOne")
st.sidebar.caption("APIs → Warehouse · Data Pipeline")
page = st.sidebar.radio("Navigate", list(PAGES.keys()))

# Dark-mode toggle
dark = st.sidebar.checkbox("Dark Mode", value=True)
if dark:
    st.markdown(
        "<style>body, .stApp { background-color: #0e1117; color: #fafafa; }</style>",
        unsafe_allow_html=True,
    )

st.sidebar.markdown("---")
st.sidebar.info("H1 — PipeOne Internship Project\nFoundations of Data Engineering")

# ── Page router ──────────────────────────────────────────────────────────────
key = PAGES[page]
if key == "home":
    from dashboard.pages import home as p
elif key == "github":
    from dashboard.pages import github as p
elif key == "hackernews":
    from dashboard.pages import hackernews as p
else:
    from dashboard.pages import combined as p

p.render()
