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

    /* Kill auto-generated page nav (belt-and-suspenders with config.toml) */
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

    /* Sidebar radio nav — hide circles, style as nav items */
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label {
        background: transparent;
        border: none;
        border-radius: 8px;
        padding: 9px 14px;
        margin: 1px 0;
        cursor: pointer;
        transition: all 0.15s ease;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:hover {
        background: rgba(255,255,255,0.04);
    }
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label > div:first-child {
        display: none;
    }
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-checked="true"],
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:has(input:checked) {
        background: rgba(29, 185, 84, 0.12);
        border-left: 3px solid #1DB954;
        padding-left: 11px;
    }
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label p {
        font-size: 0.88rem;
        font-weight: 500;
        color: #c9d1d9;
    }
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:has(input:checked) p {
        color: #f0f6fc;
        font-weight: 600;
    }
    section[data-testid="stSidebar"] .stRadio > label { display: none; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 10px;
        padding: 16px 20px;
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
    }
    .stTabs [data-baseweb="tab"]:hover { color: #f0f6fc; background: rgba(255,255,255,0.03); }
    .stTabs [aria-selected="true"] {
        background: rgba(29,185,84,0.1) !important;
        color: #1DB954 !important;
        border-bottom: 2px solid #1DB954 !important;
        font-weight: 600;
    }

    /* Expanders */
    details[data-testid="stExpander"] {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 10px;
    }
    details[data-testid="stExpander"] summary {
        font-weight: 500;
        padding: 12px 16px;
    }

    /* Dataframes */
    .stDataFrame { border-radius: 10px; overflow: hidden; }

    /* Selectbox */
    .stSelectbox > div > div { background: #161b22; border-color: #21262d; }

    /* Alerts */
    div[data-testid="stAlert"] { border-radius: 10px; font-size: 0.9rem; }

    /* Plotly spacing */
    .stPlotlyChart { margin-bottom: -12px; }

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
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar — grouped navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    # Brand header
    st.markdown("""
    <div style="padding:8px 0 16px 0">
        <div style="font-size:1.3rem;font-weight:700;color:#f0f6fc;letter-spacing:-0.02em">
            🎵 Music Command Center
        </div>
        <div style="font-size:0.78rem;color:#8b949e;margin-top:4px">
            Jakke · iLÜ · Enjune Music
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Section: Music
    st.markdown('<p class="sidebar-section">Music</p>', unsafe_allow_html=True)
    page = st.radio(
        "Navigate",
        [
            "🏠  Dashboard",
            "📊  Streaming",
            "🎵  Catalog",
            "📦  Catalog Manager",
            "💰  Revenue",
        ],
        label_visibility="collapsed",
        key="nav_music",
    )

    # Section: Social & Growth
    st.markdown('<p class="sidebar-section">Social & Growth</p>', unsafe_allow_html=True)
    page2 = st.radio(
        "Social",
        [
            "📱  Instagram",
            "🤝  Collaborators",
            "📈  Growth",
        ],
        label_visibility="collapsed",
        key="nav_social",
    )

    # Section: Tools & Insights
    st.markdown('<p class="sidebar-section">Tools & Insights</p>', unsafe_allow_html=True)
    page3 = st.radio(
        "Tools",
        [
            "🌐  Cross-Platform",
            "🧠  AI Insights",
        ],
        label_visibility="collapsed",
        key="nav_tools",
    )

    # Bottom
    st.markdown('<div style="height:40px"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.7rem;color:#484f58;padding:0 14px">'
        'v3.0 · Live APIs + Static fallback</div>',
        unsafe_allow_html=True,
    )

# Resolve which radio group was clicked
# Only one can change at a time; default to Dashboard
active_page = "🏠  Dashboard"
for key, default_idx in [("nav_music", 0), ("nav_social", 0), ("nav_tools", 0)]:
    pass  # Streamlit handles radio state

# Combine: whichever was most recently clicked
# Use session state to track last-clicked group
if "last_nav_group" not in st.session_state:
    st.session_state.last_nav_group = "nav_music"

# Detect which group changed
for key in ["nav_music", "nav_social", "nav_tools"]:
    if key in st.session_state:
        current_val = st.session_state[key]
        prev_key = f"_prev_{key}"
        if prev_key not in st.session_state:
            st.session_state[prev_key] = current_val
        if current_val != st.session_state[prev_key]:
            st.session_state.last_nav_group = key
            st.session_state[prev_key] = current_val

# Get the active page from the last-clicked group
group = st.session_state.last_nav_group
if group == "nav_music":
    active_page = page
elif group == "nav_social":
    active_page = page2
elif group == "nav_tools":
    active_page = page3

# ---------------------------------------------------------------------------
# Page routing
# ---------------------------------------------------------------------------
if active_page == "🏠  Dashboard":
    from pages.dashboard import render
elif active_page == "📊  Streaming":
    from pages.streaming import render
elif active_page == "🎵  Catalog":
    from pages.catalog import render
elif active_page == "📦  Catalog Manager":
    from pages.catalog_manager import render
elif active_page == "💰  Revenue":
    from pages.revenue import render
elif active_page == "📱  Instagram":
    from pages.instagram import render
elif active_page == "🤝  Collaborators":
    from pages.collaborators import render
elif active_page == "📈  Growth":
    from pages.growth import render
elif active_page == "🌐  Cross-Platform":
    from pages.cross_platform import render
elif active_page == "🧠  AI Insights":
    from pages.ai_insights import render
else:
    from pages.dashboard import render

render()
