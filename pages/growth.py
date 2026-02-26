"""Growth — Timeline view of career arc across all platforms."""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from theme import (
    IG_PINK, SPOTIFY_GREEN, ACCENT_BLUE, GOLD, MUTED,
    apply_theme, chart_layout, section, spacer, render_page_title, PLOTLY_CONFIG,
)

MILESTONES = [
    {"year": 2012, "event": "First Instagram post", "icon": "📸", "detail": "27 posts, 12 avg likes — the beginning"},
    {"year": 2015, "event": "Peak posting era", "icon": "📱", "detail": "203 posts in one year — most active year ever"},
    {"year": 2016, "event": "Peak lifestyle era", "icon": "🌟", "detail": "49,921 total likes, 299 avg — golden lifestyle content"},
    {"year": 2017, "event": "Engagement peak", "icon": "🔥", "detail": "470 avg likes/post — highest engagement rate ever"},
    {"year": 2018, "event": "Burning Man era", "icon": "🏜️", "detail": "249 avg likes, iconic carousel posts"},
    {"year": 2021, "event": "Hiatus / reset", "icon": "⏸️", "detail": "Only 10 posts — quiet year before the music pivot"},
    {"year": 2022, "event": "Enjune Music era begins", "icon": "🎵", "detail": "HOW DO YOU LOVE EP (3,997 likes), Sugar Tide (240K streams)"},
    {"year": 2023, "event": "Catalog expansion", "icon": "🎶", "detail": "Hurricane (170K streams), 137 posts, consistent output"},
    {"year": 2024, "event": "Breakout year", "icon": "🚀", "detail": "Your Love's Not Wasted (1.9M streams), WAIT + @ontout breakthrough"},
    {"year": 2025, "event": "EP + live shows", "icon": "🎤", "detail": "Without Peace, iLÜ launch, 1,065-like live recap post"},
    {"year": 2026, "event": "Current", "icon": "📍", "detail": "26,353 followers, 3.26M total streams, music command center era"},
]


def render() -> None:
    from data_loader import load_ig_yearly, load_ig_monthly

    yearly = load_ig_yearly()
    monthly = load_ig_monthly()

    render_page_title("Growth", "Timeline view of the entire career arc", "#2ECC71")

    # --- Career milestones as a styled timeline ---
    section("Career Milestones")
    for i, ms in enumerate(MILESTONES):
        is_last = i == len(MILESTONES) - 1
        border_style = "border-left:2px solid #21262d;" if not is_last else "border-left:2px solid #1DB954;"
        st.markdown(f"""
        <div style="display:flex;gap:16px;{border_style}padding:0 0 16px 20px;margin-left:8px">
            <div>
                <span style="font-size:0.75rem;color:#8b949e;font-weight:600">{ms['year']}</span>
                <span style="margin:0 8px">{ms['icon']}</span>
                <span style="color:#f0f6fc;font-weight:600">{ms['event']}</span>
                <br><span style="font-size:0.82rem;color:#8b949e">{ms['detail']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    spacer(16)

    # --- Engagement over time ---
    section("Engagement Over Time — Avg Likes by Year")
    fig1 = go.Figure()
    ys = yearly.sort_values("year")
    fig1.add_trace(go.Scatter(
        x=ys["year"], y=ys["avg_likes"], mode="lines+markers",
        line=dict(color=IG_PINK, width=3), marker=dict(size=8, color=IG_PINK),
        fill="tozeroy", fillcolor="rgba(225,48,108,0.08)",
        hovertemplate="<b>%{x}</b><br>Avg %{y:.0f} likes/post<extra></extra>",
    ))
    fig1.add_annotation(x=2017, y=470, text="Peak: 470", showarrow=True, arrowhead=0, arrowcolor=GOLD, font=dict(color=GOLD, size=11))
    fig1.add_annotation(x=2024, y=216, text="Music breakout", showarrow=True, arrowhead=0, arrowcolor=SPOTIFY_GREEN, font=dict(color=SPOTIFY_GREEN, size=11))
    apply_theme(fig1, height=380, yaxis_title="Avg Likes / Post", xaxis_title="")
    st.plotly_chart(fig1, use_container_width=True, key="growth_yearly", config=PLOTLY_CONFIG)

    spacer(16)

    # --- Monthly engagement (music era) ---
    section("Monthly Engagement (Music Era: 2022–2026)")
    music_era = monthly[monthly["month"] >= "2022-01-01"].sort_values("month")

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=music_era["month"], y=music_era["likes"], name="Total Likes",
        marker_color=IG_PINK, opacity=0.7,
        hovertemplate="%{x|%b %Y}<br><b>%{y:,}</b> likes<extra></extra>",
    ))
    fig2.add_trace(go.Scatter(
        x=music_era["month"], y=music_era["avg_likes"], name="Avg Likes",
        mode="lines+markers", line=dict(color=ACCENT_BLUE, width=2), yaxis="y2",
        hovertemplate="%{x|%b %Y}<br>Avg <b>%{y:.0f}</b> likes<extra></extra>",
    ))
    fig2.update_layout(**chart_layout(
        height=380,
        yaxis=dict(title="Total Likes"),
        yaxis2=dict(title="Avg Likes", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", y=1.08),
    ))
    st.plotly_chart(fig2, use_container_width=True, key="growth_monthly", config=PLOTLY_CONFIG)

    spacer(16)

    # --- Cumulative growth ---
    left, right = st.columns(2, gap="large")
    with left:
        section("Cumulative Likes")
        ys_cum = ys.copy()
        ys_cum["cumulative_likes"] = ys_cum["total_likes"].cumsum()
        fig4 = px.area(ys_cum, x="year", y="cumulative_likes", color_discrete_sequence=[IG_PINK])
        apply_theme(fig4, height=300, xaxis_title="", yaxis_title="")
        fig4.update_yaxes(tickformat=",")
        fig4.update_traces(hovertemplate="<b>%{x}</b><br>%{y:,} total likes<extra></extra>")
        st.plotly_chart(fig4, use_container_width=True, key="growth_cum_likes", config=PLOTLY_CONFIG)

    with right:
        section("Cumulative Posts")
        ys_cum["cumulative_posts"] = ys_cum["posts"].cumsum()
        fig5 = px.area(ys_cum, x="year", y="cumulative_posts", color_discrete_sequence=[ACCENT_BLUE])
        apply_theme(fig5, height=300, xaxis_title="", yaxis_title="")
        fig5.update_traces(hovertemplate="<b>%{x}</b><br>%{y:,} total posts<extra></extra>")
        st.plotly_chart(fig5, use_container_width=True, key="growth_cum_posts", config=PLOTLY_CONFIG)
