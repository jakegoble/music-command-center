"""Music Command Center v5.2 — Compact sidebar, polished design, consistent charts."""
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
# Navigation definition (no emojis — clean text labels)
# ---------------------------------------------------------------------------
NAV_GROUPS = {
    "MUSIC": [
        ("Dashboard", "dashboard"),
        ("Streaming", "streaming"),
        ("Catalog", "catalog"),
        ("Revenue", "revenue"),
    ],
    "SOCIAL & GROWTH": [
        ("Instagram", "instagram"),
        ("Collaborators", "collaborators"),
        ("Growth", "growth"),
    ],
    "TOOLS & INSIGHTS": [
        ("Cross-Platform", "cross_platform"),
        ("AI Insights", "ai_insights"),
    ],
}

# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* === GLOBAL FONT === */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    /* === Header: collapse but rescue sidebar toggle === */
    header[data-testid="stHeader"] {
        visibility: hidden;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        overflow: visible !important;
        pointer-events: none !important;
    }
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

    /* === MAIN CONTENT LAYOUT === */
    .stApp > div:first-child { padding-top: 0 !important; }
    .main .block-container {
        padding: 1.5rem 2rem 2rem !important;
        max-width: 1200px !important;
    }

    /* === TIGHTER HEADER SPACING === */
    h1 { margin-bottom: 0.3rem !important; }
    h2 { margin-bottom: 0.2rem !important; }
    h3 { margin-bottom: 0.15rem !important; }

    /* === TIGHTER ELEMENT GAPS IN MAIN CONTENT === */
    .main [data-testid="stVerticalBlock"] > div {
        margin-bottom: 0 !important;
    }
    .main [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] {
        margin-bottom: 0 !important;
    }

    /* === DARK BACKGROUNDS === */
    .stApp { background-color: #0e1117; }
    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #161b22;
    }

    /* === SIDEBAR: Kill ALL gaps at EVERY nesting level === */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
        margin: 0 !important;
        padding: 0 !important;
        gap: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        gap: 0 !important;
    }

    /* === SIDEBAR: Force left-alignment on ALL element containers === */
    [data-testid="stSidebar"] [data-testid="stElementContainer"] {
        margin: 0 !important;
        padding: 0 !important;
        display: block !important;
        text-align: left !important;
        align-items: flex-start !important;
        justify-content: flex-start !important;
    }

    /* === SIDEBAR: Kill margin/padding on stMarkdown AND inner p tags === */
    [data-testid="stSidebar"] [data-testid="stMarkdown"] {
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdown"] p {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* === SIDEBAR PADDING: Tighter overall === */
    [data-testid="stSidebarContent"] {
        padding: 1rem 0.75rem !important;
    }

    /* === NAV BUTTONS: Full-width, left-aligned, compact === */
    [data-testid="stSidebar"] [data-testid="stButton"] {
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        display: block !important;
        text-align: left !important;
    }
    /* Kill centering on button's parent wrapper divs */
    [data-testid="stSidebar"] [data-testid="stButton"] > div {
        display: block !important;
        text-align: left !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] button {
        width: 100% !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 6px 10px 6px 14px !important;
        margin: 0 !important;
        border: none !important;
        border-left: 3px solid transparent !important;
        border-radius: 0 4px 4px 0 !important;
        background: transparent !important;
        color: rgba(255, 255, 255, 0.6) !important;
        font-size: 13.5px !important;
        font-weight: 400 !important;
        line-height: 1.3 !important;
        transition: all 0.15s ease !important;
        min-height: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
        background: rgba(255, 255, 255, 0.04) !important;
        color: rgba(255, 255, 255, 0.9) !important;
        border-left-color: rgba(255, 255, 255, 0.15) !important;
    }
    /* Kill ALL focus/active/focus-visible states to prevent multi-highlight */
    [data-testid="stSidebar"] [data-testid="stButton"] button:focus,
    [data-testid="stSidebar"] [data-testid="stButton"] button:active,
    [data-testid="stSidebar"] [data-testid="stButton"] button:focus-visible,
    [data-testid="stSidebar"] [data-testid="stButton"] button:focus:not(:focus-visible) {
        box-shadow: none !important;
        outline: none !important;
        background: transparent !important;
        color: rgba(255, 255, 255, 0.6) !important;
        border-left-color: transparent !important;
    }

    /* === ACTIVE NAV ITEM: Green left border, subtle bg === */
    [data-testid="stSidebar"] .nav-active {
        display: block !important;
        text-align: left !important;
        padding: 6px 10px 6px 11px !important;
        margin: 0 !important;
        background: rgba(29, 185, 84, 0.10) !important;
        border-left: 3px solid #1DB954 !important;
        border-radius: 0 4px 4px 0 !important;
        color: #1DB954 !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
        line-height: 1.3 !important;
    }

    /* === SECTION HEADERS: Tiny, barely visible gray, left-aligned === */
    [data-testid="stSidebar"] .sidebar-section {
        text-align: left !important;
        font-size: 9.5px !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        color: rgba(255, 255, 255, 0.2) !important;
        padding: 10px 0 2px 14px !important;
        margin: 0 !important;
        line-height: 1 !important;
    }

    /* === SELECTBOX (artist switcher): Compact === */
    [data-testid="stSidebar"] [data-testid="stSelectbox"] {
        margin-top: 4px !important;
        margin-bottom: 6px !important;
    }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] label {
        display: none !important;
    }

    /* === PROFILE HEADER: Left-aligned flex row === */
    [data-testid="stSidebar"] .artist-profile-header {
        text-align: left !important;
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        padding: 4px 0 6px 0 !important;
        margin: 0 !important;
    }

    /* === STATS TABLE: Compact === */
    .sidebar-stats {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 6px;
        padding: 6px 10px;
        margin: 2px 0 4px 0;
    }

    /* === SOCIAL ICONS ROW === */
    .social-icons-row {
        margin: 2px 0 4px 0 !important;
        padding: 0 !important;
    }

    /* === SIDEBAR DIVIDERS === */
    [data-testid="stSidebar"] hr {
        margin: 6px 0 !important;
        border-color: rgba(255, 255, 255, 0.06) !important;
    }

    /* === METRIC CARDS === */
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

    /* === HORIZONTAL BLOCKS (KPI rows) === */
    [data-testid="stHorizontalBlock"] {
        gap: 12px !important;
    }

    /* === TABS — left-aligned === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 1px solid #21262d;
        justify-content: flex-start;
        padding-left: 0 !important;
    }
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

    /* === EXPANDERS === */
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

    /* === DATAFRAMES === */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    }

    /* === SELECTBOX (main content) === */
    .stSelectbox > div > div { background: #161b22; border-color: #21262d; }

    /* === ALERTS === */
    div[data-testid="stAlert"] { border-radius: 10px; font-size: 0.9rem; }

    /* === CHART CONTAINERS: Subtle border === */
    [data-testid="stPlotlyChart"] {
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 4px;
        margin-bottom: 4px !important;
    }

    /* === DIVIDERS === */
    hr {
        border-color: rgba(255, 255, 255, 0.06) !important;
        margin: 0.75rem 0 !important;
    }

    /* === CHART SECTION HEADERS === */
    .chart-header {
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        color: rgba(255, 255, 255, 0.4) !important;
        margin-bottom: 4px !important;
    }

    /* === Utility: data-card === */
    .data-card {
        background: rgba(20,20,25,0.5);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
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
# Sidebar — artist identity + switcher + compact navigation
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

    # Avatar + name
    hue = sum(ord(c) for c in name) % 360
    st.markdown(f"""
    <div class="artist-profile-header">
        <div style="display:inline-flex;align-items:center;justify-content:center;
            width:36px;height:36px;border-radius:50%;
            background:linear-gradient(135deg, hsl({hue},50%,35%), hsl({(hue+60)%360},40%,25%));
            color:#f0f6fc;font-size:14px;font-weight:700;flex-shrink:0">
            {name[0].upper()}{name[1].upper() if len(name) > 1 else ''}
        </div>
        <div>
            <div style="font-size:0.95rem;font-weight:700;color:#f0f6fc;letter-spacing:-0.02em;line-height:1.2">
                {name}{verified_badge}{flag_html}
            </div>
            <div style="font-size:0.6rem;color:rgba(255,255,255,0.35);font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin-top:1px">
                {subtitle}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Social links row
    if socials:
        icons_html = []
        for platform, url in list(socials.items())[:6]:
            icon = get_platform_icon_html(platform, 13)
            icons_html.append(
                f'<a href="{url}" target="_blank" rel="noopener" '
                f'style="text-decoration:none;opacity:0.5;transition:opacity 0.15s" '
                f'onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0.5">'
                f'{icon}</a>'
            )
        st.markdown(
            f'<div class="social-icons-row" style="display:flex;gap:5px;align-items:center">{"".join(icons_html)}</div>',
            unsafe_allow_html=True,
        )

    # Performance snapshot (compact)
    if perf:
        stats_html = []
        key_metrics = ["streams", "monthly_listeners", "followers", "playlists"]
        for key in key_metrics:
            data = perf.get(key)
            if not data:
                continue
            label = key.replace("_", " ").title()
            value = data.get("display", "")
            stats_html.append(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:3px 0;border-bottom:1px solid rgba(255,255,255,0.04)">'
                f'<span style="color:rgba(255,255,255,0.4);font-size:0.68rem;font-weight:500">{label}</span>'
                f'<span style="color:#f0f6fc;font-size:0.75rem;font-weight:700">{value}</span>'
                f'</div>'
            )
        if stats_html:
            st.markdown(
                f'<div class="sidebar-stats">{"".join(stats_html)}</div>',
                unsafe_allow_html=True,
            )

    # Artist switcher
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

    # ── Compact Navigation ──
    for group_name, group_pages in NAV_GROUPS.items():
        st.markdown(f'<p class="sidebar-section">{group_name}</p>', unsafe_allow_html=True)
        for label, page_key in group_pages:
            is_active = (st.session_state.current_page == page_key)
            if is_active:
                st.markdown(
                    f'<div class="nav-active">{label}</div>',
                    unsafe_allow_html=True,
                )
            else:
                if st.button(label, key=f"nav_{page_key}", use_container_width=True):
                    st.session_state.current_page = page_key
                    st.rerun()

    # Version footer
    st.markdown(
        '<div style="font-size:0.65rem;color:rgba(255,255,255,0.2);padding:12px 0 0 0">'
        'v5.2</div>',
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
