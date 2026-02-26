"""Music Command Center v3.0 — Jakke / iLÜ / Enjune Music."""
from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# App config (must be first st. call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Music Command Center",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Navigation definition
# ---------------------------------------------------------------------------
NAV_GROUPS = {
    "MUSIC": [
        ("🏠", "Dashboard", "dashboard"),
        ("📊", "Streaming", "streaming"),
        ("🎵", "Catalog", "catalog"),
        ("💰", "Revenue", "revenue"),
    ],
    "SOCIAL & GROWTH": [
        ("📱", "Instagram", "instagram"),
        ("🤝", "Collaborators", "collaborators"),
        ("📈", "Growth", "growth"),
    ],
    "TOOLS & INSIGHTS": [
        ("🌐", "Cross-Platform", "cross_platform"),
        ("🧠", "AI Insights", "ai_insights"),
    ],
}

# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Kill Streamlit chrome */
    header[data-testid="stHeader"] { display: none !important; }
    div[data-testid="stToolbar"] { display: none !important; }
    div[data-testid="stDecoration"] { display: none !important; }
    div[data-testid="stStatusWidget"] { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }

    /* Kill auto-generated page nav */
    [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="stSidebarNavSeparator"] { display: none !important; }

    /* Layout */
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

    /* Sidebar nav buttons — style as nav items */
    section[data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: none !important;
        color: #c9d1d9 !important;
        text-align: left !important;
        padding: 9px 14px !important;
        margin: 1px 0 !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        width: 100% !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.04) !important;
        color: #f0f6fc !important;
    }
    section[data-testid="stSidebar"] .stButton > button:focus {
        box-shadow: none !important;
    }

    /* Metric cards — depth + hover */
    [data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.4);
    }
    [data-testid="stMetricLabel"] { color: #8b949e; font-size: 0.8rem; font-weight: 500; }
    [data-testid="stMetricValue"] { color: #f0f6fc; font-size: 1.5rem; font-weight: 700; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #21262d; }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px 8px 0 0;
        color: #8b949e;
        padding: 10px 18px;
        font-weight: 500;
        font-size: 0.88rem;
        transition: all 0.15s ease;
    }
    .stTabs [data-baseweb="tab"]:hover { color: #f0f6fc; background: rgba(255,255,255,0.03); }
    .stTabs [aria-selected="true"] {
        background: rgba(29,185,84,0.1) !important;
        color: #1DB954 !important;
        border-bottom: 2px solid #1DB954 !important;
        font-weight: 600;
    }

    /* Expanders — depth */
    details[data-testid="stExpander"] {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        transition: box-shadow 0.15s ease;
    }
    details[data-testid="stExpander"]:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.35);
    }
    details[data-testid="stExpander"] summary {
        font-weight: 500;
        padding: 12px 16px;
    }

    /* Dataframes */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    }

    /* Selectbox */
    .stSelectbox > div > div { background: #161b22; border-color: #21262d; }

    /* Alerts */
    div[data-testid="stAlert"] { border-radius: 10px; font-size: 0.9rem; }

    /* Plotly — depth + hover */
    .stPlotlyChart {
        margin-bottom: -12px;
        border-radius: 10px;
        transition: transform 0.15s ease;
    }
    .stPlotlyChart:hover { transform: translateY(-1px); }

    /* Divider */
    hr { border-color: #161b22 !important; margin: 1.5rem 0 !important; }

    /* Section headers in sidebar */
    .sidebar-section {
        font-size: 0.65rem;
        font-weight: 700;
        color: #484f58;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 16px 14px 4px 14px;
        margin: 0;
    }

    /* Genre pill badges */
    .genre-pill {
        display: inline-block;
        font-size: 0.68rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 12px;
        letter-spacing: 0.03em;
        white-space: nowrap;
        color: #f0f6fc;
    }

    /* Gradient header cards */
    .gradient-card {
        background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Initialize current page in session state
# ---------------------------------------------------------------------------
if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"

# ---------------------------------------------------------------------------
# Sidebar — button-based navigation (exactly one active at a time)
# ---------------------------------------------------------------------------
with st.sidebar:
    # Brand header with avatar
    st.markdown("""
    <div style="padding:8px 0 16px 0;display:flex;align-items:center;gap:12px">
        <div style="display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#1DB954,#1a5276);color:#f0f6fc;font-size:16px;font-weight:700;flex-shrink:0">JG</div>
        <div>
            <div style="font-size:1.15rem;font-weight:700;color:#f0f6fc;letter-spacing:-0.02em">
                Music Command Center
            </div>
            <div style="font-size:0.72rem;color:#8b949e;margin-top:2px">
                Jakke · iLÜ · Enjune Music
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for group_name, group_pages in NAV_GROUPS.items():
        st.markdown(f'<p class="sidebar-section">{group_name}</p>', unsafe_allow_html=True)
        for icon, label, page_key in group_pages:
            is_active = (st.session_state.current_page == page_key)
            if is_active:
                # Active item — styled HTML (not a button)
                st.markdown(
                    f'<div style="background:rgba(29,185,84,0.12);border-left:3px solid #1DB954;'
                    f'border-radius:8px;padding:9px 11px;margin:1px 0;">'
                    f'<span style="color:#f0f6fc;font-weight:600;font-size:0.88rem">'
                    f'{icon}  {label}</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                # Inactive item — clickable button
                if st.button(f"{icon}  {label}", key=f"nav_{page_key}", use_container_width=True):
                    st.session_state.current_page = page_key
                    st.rerun()

    # Bottom
    st.markdown('<div style="height:40px"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.7rem;color:#484f58;padding:0 14px">'
        'v4.0 · Live APIs + Static fallback</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Page routing
# ---------------------------------------------------------------------------
PAGE_MODULES = {
    "dashboard": "pages.dashboard",
    "streaming": "pages.streaming",
    "catalog": "pages.catalog",
    "revenue": "pages.revenue",
    "instagram": "pages.instagram",
    "collaborators": "pages.collaborators",
    "growth": "pages.growth",
    "cross_platform": "pages.cross_platform",
    "ai_insights": "pages.ai_insights",
}

import importlib

module_name = PAGE_MODULES.get(st.session_state.current_page, "pages.dashboard")
page_module = importlib.import_module(module_name)
page_module.render()
