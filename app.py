"""Music Command Center v5.0 — Songstats-inspired design."""
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

    /* Collapse header to zero height but let sidebar button escape */
    header[data-testid="stHeader"] {
        visibility: hidden;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        overflow: visible !important;
        pointer-events: none !important;
    }

    /* Re-show the expand-sidebar button as a fixed overlay */
    [data-testid="stExpandSidebarButton"] {
        visibility: visible !important;
        pointer-events: auto !important;
        position: fixed !important;
        top: 0.6rem !important;
        left: 0.6rem !important;
        z-index: 999995 !important;
    }

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

    /* Tabs — left-aligned */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #21262d; justify-content: flex-start; }
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
# Initialize session state
# ---------------------------------------------------------------------------
if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"
if "active_artist" not in st.session_state:
    st.session_state.active_artist = "jakke"

# ---------------------------------------------------------------------------
# Sidebar — artist identity + switcher + navigation
# ---------------------------------------------------------------------------
from theme import (
    load_artist_profile, get_platform_icon_html, get_platform_badge_row,
    PLATFORM_COLORS, SPOTIFY_GREEN, MUTED, TEXT, CARD_BG, BORDER,
)

ARTIST_KEYS = ["jakke", "enjune"]

with st.sidebar:
    # ── Artist Identity Block ──
    profile = load_artist_profile(st.session_state.active_artist)
    name = profile.get("name", "Jakke")
    subtitle = profile.get("subtitle", "ARTIST")
    verified = profile.get("verified", False)
    flag = profile.get("country_flag", "")
    perf = profile.get("performance", {})
    socials = profile.get("social_links", {})

    verified_badge = ' <span style="color:#1DB954;font-size:0.85rem" title="Verified">&#10003;</span>' if verified else ""
    flag_html = f' <span style="font-size:0.95rem">{flag}</span>' if flag else ""

    # Avatar with gradient
    hue = sum(ord(c) for c in name) % 360
    st.markdown(f"""
    <div style="padding:12px 0 8px 0;display:flex;align-items:center;gap:12px">
        <div style="display:inline-flex;align-items:center;justify-content:center;
            width:44px;height:44px;border-radius:50%;
            background:linear-gradient(135deg, hsl({hue},50%,35%), hsl({(hue+60)%360},40%,25%));
            color:#f0f6fc;font-size:17px;font-weight:700;flex-shrink:0">
            {name[0].upper()}{name[1].upper() if len(name) > 1 else ''}
        </div>
        <div>
            <div style="font-size:1.1rem;font-weight:700;color:#f0f6fc;letter-spacing:-0.02em">
                {name}{verified_badge}{flag_html}
            </div>
            <div style="font-size:0.65rem;color:{MUTED};font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin-top:1px">
                {subtitle}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Social links row
    if socials:
        icons_html = []
        for platform, url in list(socials.items())[:6]:
            icon = get_platform_icon_html(platform, 14)
            icons_html.append(
                f'<a href="{url}" target="_blank" rel="noopener" '
                f'style="text-decoration:none;opacity:0.6;transition:opacity 0.15s" '
                f'onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0.6">'
                f'{icon}</a>'
            )
        st.markdown(
            f'<div style="display:flex;gap:6px;align-items:center;margin:2px 0 8px 0">{"".join(icons_html)}</div>',
            unsafe_allow_html=True,
        )

    # Performance snapshot (sidebar mini-stats)
    if perf:
        stats_html = []
        key_metrics = ["streams", "monthly_listeners", "followers", "playlists"]
        for key in key_metrics:
            data = perf.get(key)
            if not data:
                continue
            label = key.replace("_", " ").title()
            value = data.get("display", "")
            platforms = data.get("platforms", [])
            badges = get_platform_badge_row(platforms, 10, 2) if platforms else ""
            stats_html.append(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04)">'
                f'<div style="display:flex;align-items:center;gap:4px">'
                f'{badges}'
                f'<span style="color:{MUTED};font-size:0.7rem;font-weight:500">{label}</span>'
                f'</div>'
                f'<span style="color:#f0f6fc;font-size:0.78rem;font-weight:700">{value}</span>'
                f'</div>'
            )
        if stats_html:
            st.markdown(
                f'<div style="background:{CARD_BG};border:1px solid {BORDER};border-radius:8px;'
                f'padding:8px 12px;margin-bottom:12px">{"".join(stats_html)}</div>',
                unsafe_allow_html=True,
            )

    # Artist switcher
    st.markdown('<div style="margin-bottom:8px"></div>', unsafe_allow_html=True)
    artist_labels = {"jakke": "Jakke", "enjune": "Enjune"}
    current_idx = ARTIST_KEYS.index(st.session_state.active_artist)
    selected = st.selectbox(
        "Artist", ARTIST_KEYS, index=current_idx,
        format_func=lambda k: artist_labels.get(k, k),
        key="artist_switcher", label_visibility="collapsed",
    )
    if selected != st.session_state.active_artist:
        st.session_state.active_artist = selected
        st.rerun()

    st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

    # ── Navigation ──
    for group_name, group_pages in NAV_GROUPS.items():
        st.markdown(f'<p class="sidebar-section">{group_name}</p>', unsafe_allow_html=True)
        for icon, label, page_key in group_pages:
            is_active = (st.session_state.current_page == page_key)
            if is_active:
                st.markdown(
                    f'<div style="background:rgba(29,185,84,0.12);border-left:3px solid #1DB954;'
                    f'border-radius:8px;padding:9px 11px;margin:1px 0;">'
                    f'<span style="color:#f0f6fc;font-weight:600;font-size:0.88rem">'
                    f'{icon}  {label}</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                if st.button(f"{icon}  {label}", key=f"nav_{page_key}", use_container_width=True):
                    st.session_state.current_page = page_key
                    st.rerun()

    # Bottom
    st.markdown('<div style="height:40px"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.7rem;color:#484f58;padding:0 14px">'
        'v5.0 · Songstats design</div>',
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
