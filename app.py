"""Music Command Center v2.0 — Jakke / iLÜ analytics dashboard."""
from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# App config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Music Command Center",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Global CSS — dark theme overrides
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* Dark background overrides */
    .stApp { background-color: #0e1117; }
    section[data-testid="stSidebar"] { background-color: #161b22; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 16px 20px;
    }
    [data-testid="stMetricLabel"] { color: #8b949e; font-size: 0.85rem; }
    [data-testid="stMetricValue"] { color: #f0f6fc; font-size: 1.6rem; font-weight: 700; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: #161b22;
        border-radius: 8px;
        color: #8b949e;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background: #1DB954 !important;
        color: #fff !important;
    }

    /* Expanders */
    .streamlit-expanderHeader { background: #161b22; border-radius: 8px; }

    /* Hide default streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Section headers */
    .section-header {
        color: #8b949e;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🎵 Music Command Center")
    st.caption("Jakke · iLÜ · Enjune Music")
    st.divider()

    page = st.radio(
        "Navigate",
        [
            "🏠 Dashboard",
            "🎵 Catalog",
            "📊 Streaming",
            "📱 Instagram",
            "🤝 Collaborators",
            "📈 Growth",
            "🧠 AI Insights",
        ],
        label_visibility="collapsed",
        key="nav_radio",
    )

    st.divider()
    st.caption("v2.0 · Built with Streamlit + Plotly")

# ---------------------------------------------------------------------------
# Page routing
# ---------------------------------------------------------------------------
if page == "🏠 Dashboard":
    from pages.dashboard import render
    render()
elif page == "🎵 Catalog":
    from pages.catalog import render
    render()
elif page == "📊 Streaming":
    from pages.streaming import render
    render()
elif page == "📱 Instagram":
    from pages.instagram import render
    render()
elif page == "🤝 Collaborators":
    from pages.collaborators import render
    render()
elif page == "📈 Growth":
    from pages.growth import render
    render()
elif page == "🧠 AI Insights":
    from pages.ai_insights import render
    render()
