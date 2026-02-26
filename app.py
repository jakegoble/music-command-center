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
# Global CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Kill the entire Streamlit top header / toolbar / deploy bar */
    header[data-testid="stHeader"] { display: none !important; }
    div[data-testid="stToolbar"] { display: none !important; }
    div[data-testid="stDecoration"] { display: none !important; }
    div[data-testid="stStatusWidget"] { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }

    /* Remove top padding that the hidden header leaves behind */
    .stApp > div:first-child { padding-top: 0 !important; }
    .block-container { padding-top: 2rem !important; }

    /* Base font */
    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Dark backgrounds */
    .stApp { background-color: #0e1117; }
    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #161b22;
    }

    /* ── Sidebar nav styling ── */
    /* Hide the radio button circles */
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label {
        background: transparent;
        border: none;
        border-radius: 8px;
        padding: 10px 14px;
        margin: 2px 0;
        cursor: pointer;
        transition: all 0.15s ease;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:hover {
        background: rgba(255,255,255,0.04);
    }
    /* Hide the actual radio circle */
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label > div:first-child {
        display: none;
    }
    /* Active nav item */
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-checked="true"],
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:has(input:checked) {
        background: rgba(29, 185, 84, 0.12);
        border-left: 3px solid #1DB954;
        padding-left: 11px;
    }
    /* Nav text styling */
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label p {
        font-size: 0.92rem;
        font-weight: 500;
        color: #c9d1d9;
    }
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:has(input:checked) p {
        color: #f0f6fc;
        font-weight: 600;
    }
    /* Hide radio group label */
    section[data-testid="stSidebar"] .stRadio > label { display: none; }

    /* ── Metric cards (fallback for st.metric) ── */
    [data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 10px;
        padding: 16px 20px;
    }
    [data-testid="stMetricLabel"] { color: #8b949e; font-size: 0.8rem; font-weight: 500; }
    [data-testid="stMetricValue"] { color: #f0f6fc; font-size: 1.5rem; font-weight: 700; }
    [data-testid="stMetricDelta"] { font-size: 0.8rem; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #21262d; }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px 8px 0 0;
        color: #8b949e;
        padding: 10px 18px;
        font-weight: 500;
        font-size: 0.88rem;
    }
    .stTabs [data-baseweb="tab"]:hover { color: #f0f6fc; background: rgba(255,255,255,0.03); }
    .stTabs [aria-selected="true"] {
        background: rgba(29,185,84,0.1) !important;
        color: #1DB954 !important;
        border-bottom: 2px solid #1DB954 !important;
        font-weight: 600;
    }

    /* ── Expanders ── */
    details[data-testid="stExpander"] {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 10px;
    }
    details[data-testid="stExpander"] summary {
        font-weight: 500;
        padding: 12px 16px;
    }

    /* ── Dataframes ── */
    .stDataFrame { border-radius: 10px; overflow: hidden; }

    /* ── Selectbox ── */
    .stSelectbox > div > div { background: #161b22; border-color: #21262d; }

    /* ── Info/Success/Warning boxes ── */
    div[data-testid="stAlert"] { border-radius: 10px; font-size: 0.9rem; }

    /* ── Plotly chart containers — tighter spacing ── */
    .stPlotlyChart { margin-bottom: -12px; }

    /* ── Divider ── */
    hr { border-color: #161b22 !important; margin: 1.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    # Logo / brand area
    st.markdown("""
    <div style="padding: 8px 0 20px 0">
        <div style="font-size: 1.3rem; font-weight: 700; color: #f0f6fc; letter-spacing: -0.02em">
            🎵 Music Command Center
        </div>
        <div style="font-size: 0.78rem; color: #8b949e; margin-top: 4px">
            Jakke · iLÜ · Enjune Music
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        [
            "🏠  Dashboard",
            "🎵  Catalog",
            "📦  Catalog Manager",
            "📊  Streaming",
            "💰  Revenue",
            "🌐  Cross-Platform",
            "📱  Instagram",
            "🤝  Collaborators",
            "📈  Growth",
            "🧠  AI Insights",
        ],
        label_visibility="collapsed",
        key="nav_radio",
    )

    # Bottom
    st.markdown('<div style="height: 40px"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.7rem;color:#484f58;padding:0 14px">'
        'v3.0 · Live APIs + Static fallback</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Page routing
# ---------------------------------------------------------------------------
if page == "🏠  Dashboard":
    from pages.dashboard import render
elif page == "🎵  Catalog":
    from pages.catalog import render
elif page == "📦  Catalog Manager":
    from pages.catalog_manager import render
elif page == "📊  Streaming":
    from pages.streaming import render
elif page == "💰  Revenue":
    from pages.revenue import render
elif page == "🌐  Cross-Platform":
    from pages.cross_platform import render
elif page == "📱  Instagram":
    from pages.instagram import render
elif page == "🤝  Collaborators":
    from pages.collaborators import render
elif page == "📈  Growth":
    from pages.growth import render
elif page == "🧠  AI Insights":
    from pages.ai_insights import render
else:
    from pages.dashboard import render

render()
