"""Shared design tokens, Plotly layout, and HTML card helpers."""
from __future__ import annotations

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

# Platform colors
PLATFORM_COLORS = {
    "Spotify": SPOTIFY_GREEN,
    "Apple Music": "#fc3c44",
    "YouTube": "#ff0000",
    "YouTube Music": "#ff0000",
    "Amazon Music": "#00a8e1",
    "Deezer": "#a238ff",
    "Tidal": "#000000",
    "Instagram": IG_PINK,
    "SoundCloud": "#ff5500",
}

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
def kpi_card(label: str, value: str, *, delta: str = "", accent: str = SPOTIFY_GREEN, sub: str = "") -> str:
    """Return HTML for a styled KPI card. Uses spans to avoid nested div rendering issues."""
    parts = [
        f'<div style="background:{CARD_BG};border:1px solid {BORDER};border-left:3px solid {accent};border-radius:10px;padding:18px 20px;">',
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
    """Render a row of KPI cards. Each dict has: label, value, and optional accent/delta/sub."""
    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        with col:
            st.markdown(kpi_card(**card), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Section header
# ---------------------------------------------------------------------------
def section(title: str) -> None:
    """Render a subtle uppercase section header."""
    st.markdown(
        f'<p style="color:{MUTED};font-size:0.72rem;font-weight:600;letter-spacing:0.1em;'
        f'text-transform:uppercase;margin:28px 0 8px 0">{title}</p>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Spacer
# ---------------------------------------------------------------------------
def spacer(height: int = 24) -> None:
    st.markdown(f'<div style="height:{height}px"></div>', unsafe_allow_html=True)
