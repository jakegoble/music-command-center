"""Shared design tokens, Plotly layout, and HTML card/component helpers.

Single source of truth for all visual theming across the Music Command Center.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
SPOTIFY_GREEN = "#1DB954"
IG_PINK = "#E1306C"
IG_PURPLE = "#833AB4"
IG_ORANGE = "#F77737"
ACCENT_BLUE = "#58a6ff"
GOLD = "#f0c040"
AMBER = "#f0883e"
MUTED = "#8b949e"
TEXT = "#f0f6fc"
TEXT_DIM = "#8b949e"
BG = "#0e1117"
CARD_BG = "#161b22"
BORDER = "#21262d"

# Platform colors (comprehensive — used for theming, chart colors, icons)
PLATFORM_COLORS: dict[str, str] = {
    "spotify": SPOTIFY_GREEN,
    "apple_music": "#fc3c44",
    "youtube": "#ff0000",
    "youtube_music": "#ff0000",
    "amazon_music": "#00a8e1",
    "deezer": "#a238ff",
    "tidal": "#000000",
    "instagram": IG_PINK,
    "soundcloud": "#ff5500",
    "lastfm": "#d51007",
    "beatport": "#94D500",
    "tiktok": "#69C9D0",
    "facebook": "#1877F2",
    "x_twitter": "#ffffff",
    "shazam": "#0088FF",
    # Display-name aliases (for backward compat)
    "Spotify": SPOTIFY_GREEN,
    "Apple Music": "#fc3c44",
    "YouTube": "#ff0000",
    "YouTube Music": "#ff0000",
    "Amazon Music": "#00a8e1",
    "Deezer": "#a238ff",
    "Tidal": "#000000",
    "Instagram": IG_PINK,
    "SoundCloud": "#ff5500",
    "Last.fm": "#d51007",
}

# Page-specific accent colors
PAGE_ACCENTS: dict[str, str] = {
    "dashboard": GOLD,
    "streaming": SPOTIFY_GREEN,
    "catalog": ACCENT_BLUE,
    "revenue": GOLD,
    "instagram": IG_PINK,
    "collaborators": "#9B59B6",
    "growth": "#2ECC71",
    "cross_platform": ACCENT_BLUE,
    "ai_insights": "#E74C3C",
}

# Genre colors for pill badges
GENRE_COLORS: dict[str, str] = {
    "Organic House": "#2d6a4f",
    "Deep House": "#1a5276",
    "Melodic House": "#4a235a",
    "Melodic Techno": "#6c3483",
    "Progressive House": "#1f618d",
    "Indie Electronic": "#784212",
    "Downtempo": "#1b4332",
    "Chillwave": "#154360",
    "Lo-Fi": "#5d4037",
    "Ambient": "#263238",
    "Acoustic": "#4e342e",
}


# ---------------------------------------------------------------------------
# Platform SVG icons (inline base64 for Streamlit Cloud compatibility)
# ---------------------------------------------------------------------------
_PLATFORM_SVGS: dict[str, str] = {
    "spotify": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#1DB954"><path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/></svg>',
    "apple_music": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fc3c44"><path d="M23.997 6.124a9.23 9.23 0 00-.24-2.19C23.44 2.624 22.695 1.624 21.577.89A5.03 5.03 0 0019.703.237a10.2 10.2 0 00-1.898-.122C17.34.09 16.87.07 16.404.06c-.466-.01-1.334-.02-2.204-.03L12 .02 4.998.05c-.63.01-1.1.025-1.565.05A10.2 10.2 0 001.535.222 5.03 5.03 0 00.237 1.024C-.432 1.847-.04 2.724.04 3.934a9.23 9.23 0 00.08 2.19v11.752a9.23 9.23 0 00.24 2.19c.317 1.31 1.062 2.31 2.18 3.043A5.03 5.03 0 004.3 23.763c.616.063 1.237.1 1.858.11l1.398.04h8.888l1.398-.04c.621-.01 1.242-.047 1.858-.11a5.03 5.03 0 001.874-.752c.668-.413 1.112-1.033 1.186-1.8a9.23 9.23 0 00.24-2.19V6.124zM16.95 13.52c0 .578-.036 1.143-.215 1.699-.39 1.213-1.364 1.944-2.573 2.072-1.625.172-2.882-.86-2.98-2.436-.083-1.348.813-2.502 2.134-2.756.472-.09.955-.13 1.414-.237.383-.09.59-.328.604-.734.01-.208.013-.417.013-.626V8.12c0-.354-.118-.478-.47-.416l-5.198 1.073c-.154.03-.247.12-.264.276-.02.182-.036.365-.036.548v7.166c0 .55-.028 1.098-.188 1.627-.37 1.224-1.334 1.97-2.55 2.115-1.65.197-2.958-.806-3.073-2.385-.097-1.333.773-2.49 2.083-2.76.49-.1.993-.148 1.471-.263.349-.085.548-.315.565-.68.003-.068.006-.137.006-.205V7.388c0-.435.08-.554.5-.638l7.506-1.524c.333-.07.459.04.459.387v7.907z"/></svg>',
    "youtube": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#ff0000"><path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>',
    "instagram": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#E1306C"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>',
    "soundcloud": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#ff5500"><path d="M1.175 12.225c-.051 0-.094.046-.101.1l-.233 2.154.233 2.105c.007.058.05.098.101.098.05 0 .09-.04.099-.098l.255-2.105-.27-2.154c-.009-.06-.05-.1-.1-.1m-.899.828c-.06 0-.091.037-.104.094L0 14.479l.172 1.308c.013.06.045.094.104.094.059 0 .09-.037.104-.094l.199-1.308-.199-1.332c-.014-.057-.045-.094-.104-.094m1.836-1.035c-.065 0-.105.05-.112.109l-.209 2.36.209 2.222c.007.06.047.11.112.11.065 0 .105-.05.114-.11l.24-2.222-.24-2.36c-.009-.06-.049-.11-.114-.11m.922-.08c-.073 0-.118.058-.124.12l-.193 2.441.193 2.27c.006.065.051.12.124.12.072 0 .117-.055.123-.12l.217-2.27-.217-2.44c-.006-.063-.05-.12-.123-.12m.922-.098c-.082 0-.131.062-.137.128l-.175 2.539.175 2.318c.006.07.055.128.137.128.081 0 .13-.058.136-.128l.2-2.318-.2-2.539c-.006-.066-.055-.128-.136-.128m.93-.208c-.09 0-.14.072-.145.14l-.16 2.747.16 2.353c.005.073.055.14.145.14.088 0 .138-.067.144-.14l.18-2.353-.18-2.747c-.006-.068-.056-.14-.144-.14m.928-.259c-.098 0-.148.078-.153.149l-.143 3.006.143 2.38c.005.076.055.149.153.149.097 0 .148-.073.152-.149l.163-2.38-.163-3.006c-.005-.071-.055-.149-.152-.149m.93-.143c-.106 0-.155.087-.16.16l-.127 3.148.127 2.394c.005.08.054.16.16.16s.155-.08.16-.16l.144-2.394-.144-3.148c-.005-.073-.054-.16-.16-.16m.928-.09c-.114 0-.164.093-.168.168l-.112 3.24.112 2.399c.004.084.054.168.168.168.113 0 .163-.084.167-.168l.127-2.399-.127-3.24c-.004-.075-.054-.167-.167-.167m1.983-1.263c-.17 0-.215.087-.217.184l-.09 4.57.09 2.393c.002.1.048.184.217.184.168 0 .213-.084.215-.184l.1-2.393-.1-4.57c-.002-.097-.047-.184-.215-.184m-.947.535c-.16 0-.2.09-.204.175l-.1 4.035.1 2.4c.004.09.044.175.204.175.159 0 .199-.085.202-.175l.115-2.4-.115-4.035c-.003-.085-.043-.175-.202-.175m1.89-.96c-.178 0-.223.098-.225.196l-.075 4.995.075 2.387c.002.104.047.196.225.196s.222-.092.224-.196l.085-2.387-.085-4.995c-.002-.098-.046-.196-.224-.196m.95-.09c-.184 0-.232.103-.233.203l-.062 5.085.062 2.384c.001.108.049.203.233.203.183 0 .231-.095.232-.203l.07-2.384-.07-5.085c-.001-.1-.05-.203-.233-.203m.95-.12c-.19 0-.24.109-.241.213l-.05 5.205.05 2.375c.001.112.051.213.241.213.189 0 .24-.101.24-.213l.055-2.375-.056-5.205c0-.104-.05-.213-.24-.213m6.19 1.143c-.66 0-1.285.13-1.86.365a6.024 6.024 0 00-5.99-5.553c-.4 0-.795.043-1.18.127-.15.033-.2.097-.2.193v10.907c0 .1.065.188.163.2h9.066A3.41 3.41 0 0024 14.605a3.41 3.41 0 00-3.41-3.41"/></svg>',
    "beatport": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#94D500"><path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm3.2 16.8h-2.4v-2.4H10.4v2.4H8v-2.4H5.6V12H8V9.6h2.4V12h2.4V9.6h2.4V12h2.4v2.4h-2.4v2.4z"/></svg>',
    "tiktok": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#69C9D0"><path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1v-3.5a6.37 6.37 0 00-.79-.05A6.34 6.34 0 003.15 15.2a6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.34-6.34V9.08a8.16 8.16 0 004.76 1.52v-3.4a4.85 4.85 0 01-1-.51z"/></svg>',
    "lastfm": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#d51007"><path d="M10.584 17.21l-.88-2.392s-1.43 1.594-3.573 1.594c-1.897 0-3.244-1.649-3.244-4.288 0-3.382 1.704-4.591 3.381-4.591 2.422 0 3.19 1.567 3.849 3.574l.88 2.749c.88 2.666 2.529 4.81 7.285 4.81 3.409 0 5.718-1.044 5.718-3.793 0-2.227-1.265-3.381-3.63-3.931l-1.758-.385c-1.21-.275-1.567-.77-1.567-1.595 0-.934.742-1.484 1.952-1.484 1.32 0 2.034.495 2.144 1.677l2.749-.33c-.22-2.474-1.924-3.492-4.729-3.492-2.474 0-4.893.935-4.893 3.932 0 1.87.907 3.051 3.189 3.601l1.87.44c1.402.33 1.869.907 1.869 1.704 0 1.017-.99 1.43-2.86 1.43-2.776 0-3.932-1.457-4.59-3.464l-.907-2.749c-1.155-3.573-2.997-4.893-6.653-4.893C2.144 5.333 0 7.89 0 12.233c0 4.18 2.144 6.434 5.993 6.434 3.106 0 4.591-1.457 4.591-1.457z"/></svg>',
    "facebook": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#1877F2"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>',
    "x_twitter": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#ffffff"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>',
    "amazon_music": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#00a8e1"><path d="M13.958 10.09c0 1.232.029 2.256-.591 3.351-.502.891-1.301 1.438-2.186 1.438-1.214 0-1.922-.924-1.922-2.292 0-2.692 2.415-3.182 4.7-3.182v.685zm3.186 7.705a.66.66 0 01-.753.069c-1.06-.878-1.247-1.287-1.826-2.126-1.749 1.784-2.981 2.318-5.246 2.318-2.682 0-4.762-1.653-4.762-4.966 0-2.586 1.401-4.346 3.399-5.205 1.729-.762 4.148-.897 5.993-1.106v-.413c0-.762.058-1.665-.389-2.326-.388-.588-1.132-.832-1.788-.832-1.213 0-2.29.623-2.554 1.914-.055.283-.261.562-.547.576l-3.062-.33c-.26-.058-.547-.264-.472-.66C5.943 1.862 9.044.248 11.823.248c1.401 0 3.232.372 4.338 1.434 1.401 1.311 1.268 3.059 1.268 4.966v4.498c0 1.349.559 1.942 1.087 2.674.184.262.224.576-.01.77-.585.489-1.629 1.398-2.202 1.905l-.16-.2zM21.779 19.56C19.169 21.66 15.316 22.8 12 22.8c-4.554 0-8.659-1.685-11.764-4.484-.243-.22-.026-.52.268-.35 3.353 1.949 7.497 3.124 11.78 3.124 2.888 0 6.062-.6 8.981-1.838.44-.19.81.29.514.309z"/></svg>',
    "deezer": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#a238ff"><rect x="0" y="18" width="4" height="2" rx="0.5"/><rect x="5" y="18" width="4" height="2" rx="0.5"/><rect x="5" y="15" width="4" height="2" rx="0.5"/><rect x="10" y="18" width="4" height="2" rx="0.5"/><rect x="10" y="15" width="4" height="2" rx="0.5"/><rect x="10" y="12" width="4" height="2" rx="0.5"/><rect x="15" y="18" width="4" height="2" rx="0.5"/><rect x="15" y="15" width="4" height="2" rx="0.5"/><rect x="15" y="12" width="4" height="2" rx="0.5"/><rect x="15" y="9" width="4" height="2" rx="0.5"/><rect x="20" y="18" width="4" height="2" rx="0.5"/><rect x="20" y="15" width="4" height="2" rx="0.5"/><rect x="20" y="12" width="4" height="2" rx="0.5"/><rect x="20" y="9" width="4" height="2" rx="0.5"/><rect x="20" y="6" width="4" height="2" rx="0.5"/></svg>',
    "shazam": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0088FF"><path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm3.102 15.98a4.683 4.683 0 01-6.622 0l-2.57-2.57a.75.75 0 111.06-1.06l2.57 2.57a3.183 3.183 0 004.502 0 3.183 3.183 0 000-4.502l-2.57-2.57a.75.75 0 111.06-1.06l2.57 2.57a4.683 4.683 0 010 6.622zm-.634-4.1l-2.57 2.57a.75.75 0 01-1.06-1.06l2.57-2.57a3.183 3.183 0 000-4.502 3.183 3.183 0 00-4.502 0l-2.57 2.57a.75.75 0 01-1.06-1.06l2.57-2.57a4.683 4.683 0 016.622 0 4.683 4.683 0 010 6.622z"/></svg>',
}


def _svg_to_base64(svg: str) -> str:
    """Convert raw SVG string to a base64 data URI."""
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def get_platform_icon_html(platform: str, size: int = 16) -> str:
    """Return an <img> tag for a platform SVG icon."""
    key = platform.lower().replace(" ", "_").replace(".", "")
    svg = _PLATFORM_SVGS.get(key)
    if not svg:
        # Fallback: colored dot
        color = PLATFORM_COLORS.get(platform, PLATFORM_COLORS.get(key, MUTED))
        return f'<span style="color:{color};font-size:{size}px;line-height:1">●</span>'
    src = _svg_to_base64(svg)
    return f'<img src="{src}" width="{size}" height="{size}" style="vertical-align:middle" />'


def get_platform_badge_row(platforms: list[str], size: int = 14, gap: int = 3) -> str:
    """Return HTML for a row of tiny platform icon badges."""
    icons = [get_platform_icon_html(p, size) for p in platforms]
    return f'<span style="display:inline-flex;gap:{gap}px;align-items:center">{"".join(icons)}</span>'


def get_page_accent(page_name: str) -> str:
    """Return the accent color for a given page."""
    return PAGE_ACCENTS.get(page_name, ACCENT_BLUE)


# ---------------------------------------------------------------------------
# Plotly shared layout
# ---------------------------------------------------------------------------
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT, family="'Inter', system-ui, -apple-system, sans-serif", size=13),
    margin=dict(l=0, r=0, t=36, b=0),
    hoverlabel=dict(bgcolor="#21262d", font_color=TEXT, font_size=13),
    xaxis=dict(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.08)",
        gridwidth=1,
        griddash="dot",
        zerolinecolor="rgba(255,255,255,0.06)",
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.08)",
        gridwidth=1,
        zerolinecolor="rgba(255,255,255,0.06)",
    ),
)

# Pie/donut chart layout additions (merge into update_layout calls)
PIE_LAYOUT = dict(
    uniformtext_minsize=10,
    uniformtext_mode="hide",
)


def chart_layout(**overrides) -> dict:
    """Build a Plotly layout dict that safely merges with PLOTLY_LAYOUT.

    Use this instead of **PLOTLY_LAYOUT when you need to override yaxis, yaxis2, legend, etc.
    This avoids the 'got multiple values for keyword argument' error.
    """
    layout = dict(PLOTLY_LAYOUT)
    for key in ["xaxis", "yaxis", "xaxis2", "yaxis2"]:
        if key in overrides:
            base = dict(layout.get(key, {}))
            base.update(overrides.pop(key))
            layout[key] = base
    layout.update(overrides)
    return layout


# ---------------------------------------------------------------------------
# KPI card — clean single-line HTML (fixes HTML leak bug)
# ---------------------------------------------------------------------------
def kpi_card(label: str, value: str, *, delta: str = "", accent: str = SPOTIFY_GREEN,
             sub: str = "", icon_html: str = "") -> str:
    """Return HTML for a styled KPI card with depth. Uses spans to avoid nested div rendering issues."""
    icon_block = f'<span style="float:right;margin-top:2px">{icon_html}</span>' if icon_html else ""
    parts = [
        f'<div style="background:linear-gradient(135deg, {CARD_BG} 0%, #1c2333 100%);'
        f'border:1px solid {BORDER};border-left:3px solid {accent};border-radius:10px;'
        f'padding:18px 20px;box-shadow:0 2px 8px rgba(0,0,0,0.3);'
        f'transition:transform 0.15s ease, box-shadow 0.15s ease;">',
        icon_block,
        f'<span style="font-size:0.78rem;color:{MUTED};font-weight:500;letter-spacing:0.03em;text-transform:uppercase;display:block;">{label}</span>',
        f'<span style="font-size:1.65rem;color:{TEXT};font-weight:700;margin-top:4px;line-height:1.2;display:block;">{value}</span>',
    ]
    if delta:
        is_neg = delta.startswith("-") or "down" in delta.lower()
        color = "#f85149" if is_neg else SPOTIFY_GREEN
        parts.append(f'<span style="font-size:0.8rem;color:{color};margin-top:4px;display:block;">{delta}</span>')
    if sub:
        parts.append(f'<span style="font-size:0.75rem;color:{MUTED};margin-top:2px;display:block;">{sub}</span>')
    parts.append('</div>')
    return "".join(parts)


def kpi_row(cards: list[dict]) -> None:
    """Render a row of KPI cards. Each dict has: label, value, and optional accent/delta/sub/icon_html."""
    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        with col:
            st.markdown(kpi_card(**card), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Section header
# ---------------------------------------------------------------------------
def section(title: str, accent: str = "") -> None:
    """Render a subtle uppercase section header."""
    color = accent or MUTED
    st.markdown(
        f'<p style="color:{color};font-size:0.72rem;font-weight:600;letter-spacing:0.1em;'
        f'text-transform:uppercase;margin:28px 0 8px 0">{title}</p>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Genre pill badge
# ---------------------------------------------------------------------------
def genre_pill(genre: str) -> str:
    """Return inline HTML for a genre pill badge."""
    bg = GENRE_COLORS.get(genre, "#333")
    return (
        f'<span style="display:inline-block;background:{bg};color:#f0f6fc;'
        f'font-size:0.68rem;font-weight:600;padding:3px 10px;border-radius:12px;'
        f'letter-spacing:0.03em;white-space:nowrap">{genre}</span>'
    )


def genre_pills(genres: list[str]) -> str:
    """Return inline HTML for multiple genre pill badges."""
    return " ".join(genre_pill(g) for g in genres if g)


def genre_tag(genre: str) -> str:
    """Return a hashtag-style genre tag (Songstats style)."""
    return (
        f'<span style="display:inline-block;background:rgba(255,255,255,0.06);color:{MUTED};'
        f'font-size:0.72rem;font-weight:500;padding:4px 12px;border-radius:14px;'
        f'margin:2px 4px 2px 0">#{genre}</span>'
    )


def genre_tags(genres: list[str]) -> str:
    """Return HTML for a row of hashtag-style genre tags."""
    return "".join(genre_tag(g) for g in genres if g)


# ---------------------------------------------------------------------------
# Platform icon (simple colored dot — kept for backward compat)
# ---------------------------------------------------------------------------
PLATFORM_ICONS: dict[str, tuple[str, str]] = {
    "Spotify": ("●", SPOTIFY_GREEN),
    "Apple Music": ("●", "#fc3c44"),
    "YouTube": ("▶", "#ff0000"),
    "YouTube Music": ("▶", "#ff0000"),
    "Amazon Music": ("●", "#00a8e1"),
    "Deezer": ("●", "#a238ff"),
    "Tidal": ("●", "#000000"),
    "Instagram": ("●", IG_PINK),
    "SoundCloud": ("●", "#ff5500"),
    "Last.fm": ("●", "#d51007"),
}


def platform_icon(name: str, size: str = "0.85rem") -> str:
    """Return HTML span with a colored platform indicator dot."""
    marker, color = PLATFORM_ICONS.get(name, ("●", MUTED))
    return f'<span style="color:{color};font-size:{size};margin-right:4px">{marker}</span>'


# ---------------------------------------------------------------------------
# Avatar placeholder (colored initials)
# ---------------------------------------------------------------------------
def avatar(name: str, size: int = 40) -> str:
    """Return HTML for a circular avatar with initials."""
    initials = "".join(w[0].upper() for w in name.split()[:2]) if name else "?"
    # Generate a stable color from the name
    hue = sum(ord(c) for c in name) % 360
    bg = f"hsl({hue}, 45%, 35%)"
    return (
        f'<div style="display:inline-flex;align-items:center;justify-content:center;'
        f'width:{size}px;height:{size}px;border-radius:50%;background:{bg};'
        f'color:#f0f6fc;font-size:{size // 3}px;font-weight:700;flex-shrink:0">'
        f'{initials}</div>'
    )


# ---------------------------------------------------------------------------
# Artist header with avatar
# ---------------------------------------------------------------------------
def artist_header(name: str, subtitle: str = "", verified: bool = False,
                  flag: str = "") -> str:
    """Return HTML for an artist header with avatar circle."""
    av = avatar(name, 48)
    badge = ' <span style="color:#1DB954;font-size:0.9rem" title="Verified">&#10003;</span>' if verified else ""
    flag_html = f' <span style="font-size:1rem">{flag}</span>' if flag else ""
    sub_html = f'<span style="font-size:0.8rem;color:{MUTED};display:block;margin-top:2px">{subtitle}</span>' if subtitle else ""
    return (
        f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:20px">'
        f'{av}'
        f'<div><span style="font-size:1.4rem;font-weight:700;color:{TEXT}">{name}</span>'
        f'{badge}{flag_html}{sub_html}</div>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Collaborator chips
# ---------------------------------------------------------------------------
def collab_chip(name: str, role: str = "") -> str:
    """Return HTML for a single collaborator chip."""
    role_html = f' <span style="color:{MUTED};font-size:0.65rem">({role})</span>' if role else ""
    return (
        f'<span style="display:inline-block;background:rgba(255,255,255,0.06);'
        f'border:1px solid {BORDER};color:{TEXT};font-size:0.78rem;font-weight:500;'
        f'padding:4px 12px;border-radius:16px;margin:3px 4px 3px 0">'
        f'{name}{role_html}</span>'
    )


def collab_chips(collaborators: list[dict]) -> str:
    """Return HTML for a row of collaborator chips. Each dict has name and optional role."""
    return "".join(collab_chip(c.get("name", ""), c.get("role", "")) for c in collaborators)


# ---------------------------------------------------------------------------
# Social links row
# ---------------------------------------------------------------------------
def social_links_row(links: dict[str, str], size: int = 18) -> str:
    """Return HTML for a row of clickable platform icons."""
    parts = []
    for platform, url in links.items():
        icon = get_platform_icon_html(platform, size)
        parts.append(
            f'<a href="{url}" target="_blank" rel="noopener" '
            f'style="text-decoration:none;opacity:0.8;transition:opacity 0.15s" '
            f'onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0.8">'
            f'{icon}</a>'
        )
    return f'<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:8px 0">{"".join(parts)}</div>'


# ---------------------------------------------------------------------------
# Performance sidebar (Songstats-style right rail)
# ---------------------------------------------------------------------------
def performance_metric(label: str, value: str, platforms: list[str] | None = None,
                       accent: str = SPOTIFY_GREEN) -> str:
    """Return HTML for a single performance metric row."""
    badges = get_platform_badge_row(platforms, 12) if platforms else ""
    return (
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f'padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.04)">'
        f'<div><span style="color:{MUTED};font-size:0.75rem;font-weight:500;display:block">{label}</span>'
        f'{badges}</div>'
        f'<span style="color:{accent};font-size:1.1rem;font-weight:700">{value}</span>'
        f'</div>'
    )


def performance_sidebar(metrics: dict, accent: str = SPOTIFY_GREEN) -> str:
    """Return HTML for a full Songstats-style performance sidebar.

    metrics: dict from artist_profiles.json 'performance' section.
    """
    rows = []
    for key, data in metrics.items():
        label = key.replace("_", " ").title()
        value = data.get("display", str(data.get("value", "")))
        platforms = data.get("platforms", [])
        rows.append(performance_metric(label, value, platforms, accent))
    return (
        f'<div style="background:linear-gradient(135deg, {CARD_BG} 0%, #1c2333 100%);'
        f'border:1px solid {BORDER};border-top:3px solid {accent};border-radius:10px;'
        f'padding:16px 20px;box-shadow:0 2px 8px rgba(0,0,0,0.3)">'
        f'<div style="font-size:0.72rem;color:{MUTED};font-weight:600;letter-spacing:0.1em;'
        f'text-transform:uppercase;margin-bottom:8px">Performance</div>'
        f'{"".join(rows)}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Track row (for catalog — Songstats-style)
# ---------------------------------------------------------------------------
def track_row(name: str, artist: str, streams: str, genre: str = "",
              playlisted: bool = False, artwork_color: str = "") -> str:
    """Return HTML for a single track row card."""
    # Artwork placeholder
    hue = sum(ord(c) for c in name) % 360
    art_bg = artwork_color or f"hsl({hue}, 30%, 25%)"
    initial = name[0].upper() if name else "?"
    art = (
        f'<div style="width:48px;height:48px;border-radius:6px;background:{art_bg};'
        f'display:flex;align-items:center;justify-content:center;flex-shrink:0;'
        f'font-size:1.2rem;color:rgba(255,255,255,0.3)">&#9835;</div>'
    )
    playlist_dot = f'<span style="color:{SPOTIFY_GREEN};font-size:0.6rem;margin-left:6px" title="Currently Playlisted">&#9679;</span>' if playlisted else ""
    genre_html = f' {genre_pill(genre)}' if genre else ""
    return (
        f'<div style="display:flex;align-items:center;gap:12px;padding:10px 14px;'
        f'background:{CARD_BG};border:1px solid {BORDER};border-radius:8px;margin-bottom:6px;'
        f'transition:background 0.15s">'
        f'{art}'
        f'<div style="flex:1;min-width:0">'
        f'<div style="color:{TEXT};font-size:0.88rem;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{name}{playlist_dot}</div>'
        f'<div style="color:{MUTED};font-size:0.75rem">{artist}{genre_html}</div>'
        f'</div>'
        f'<div style="text-align:right;flex-shrink:0">'
        f'<div style="color:{TEXT};font-size:0.9rem;font-weight:600">{streams}</div>'
        f'</div>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Time range selector
# ---------------------------------------------------------------------------
def time_range_selector(key: str, options: list[str] | None = None,
                        default: str = "All") -> str:
    """Render a time range pill selector and return the selected value."""
    opts = options or ["1m", "3m", "6m", "YTD", "1y", "All"]
    return st.radio(
        "Time range", opts, index=opts.index(default) if default in opts else len(opts) - 1,
        key=key, horizontal=True, label_visibility="collapsed",
    )


# ---------------------------------------------------------------------------
# Page accent CSS injection
# ---------------------------------------------------------------------------
def inject_page_accent(page_name: str) -> None:
    """Inject CSS that themes the current page with its accent color."""
    accent = get_page_accent(page_name)
    st.markdown(f"""
    <style>
        /* Page accent border on headers */
        .page-accent-bar {{
            height: 3px;
            background: {accent};
            border-radius: 2px;
            margin-bottom: 16px;
        }}
    </style>
    """, unsafe_allow_html=True)
    st.markdown(f'<div class="page-accent-bar"></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Spacer
# ---------------------------------------------------------------------------
def spacer(height: int = 24) -> None:
    st.markdown(f'<div style="height:{height}px"></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Data loader for artist profiles
# ---------------------------------------------------------------------------
_DATA_DIR = Path(__file__).parent / "data"


def load_artist_profile(artist_key: str) -> dict:
    """Load an artist profile from artist_profiles.json."""
    with open(_DATA_DIR / "artist_profiles.json") as f:
        profiles = json.load(f)
    return profiles.get(artist_key, {})
