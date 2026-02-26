"""Growth — Timeline view of career arc across all platforms."""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

IG_PINK = "#E1306C"
SPOTIFY_GREEN = "#1DB954"
ACCENT_BLUE = "#58a6ff"
GOLD = "#f0c040"
MUTED = "#8b949e"
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#f0f6fc", family="system-ui, -apple-system, sans-serif"),
    margin=dict(l=0, r=0, t=40, b=0),
    hoverlabel=dict(bgcolor="#21262d", font_color="#f0f6fc"),
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

    st.markdown("# 📈 Growth")
    st.caption("Timeline view of the entire career arc")

    # --- Career milestones ---
    st.markdown('<p class="section-header">Career Milestones</p>', unsafe_allow_html=True)

    for ms in MILESTONES:
        col_icon, col_text = st.columns([0.08, 0.92])
        with col_icon:
            st.markdown(f"### {ms['icon']}")
        with col_text:
            st.markdown(f"**{ms['year']}** — {ms['event']}")
            st.caption(ms["detail"])

    st.divider()

    # --- Engagement over time (yearly) ---
    st.markdown('<p class="section-header">Engagement Over Time — Avg Likes by Year</p>', unsafe_allow_html=True)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=yearly.sort_values("year")["year"],
        y=yearly.sort_values("year")["avg_likes"],
        mode="lines+markers",
        line=dict(color=IG_PINK, width=3),
        marker=dict(size=10, color=IG_PINK),
        fill="tozeroy",
        fillcolor="rgba(225,48,108,0.1)",
        hovertemplate="Year %{x}<br>Avg %{y:.0f} likes/post<extra></extra>",
    ))
    # Annotate key moments
    fig1.add_annotation(x=2017, y=470, text="Peak: 470 avg", showarrow=True, arrowhead=2, font=dict(color=GOLD, size=12))
    fig1.add_annotation(x=2024, y=216, text="Music breakout", showarrow=True, arrowhead=2, font=dict(color=SPOTIFY_GREEN, size=12))
    fig1.update_layout(**PLOTLY_LAYOUT, height=400, xaxis_title="Year", yaxis_title="Avg Likes / Post")
    st.plotly_chart(fig1, use_container_width=True, key="growth_yearly")

    st.divider()

    # --- Monthly engagement (2022-2026) ---
    st.markdown('<p class="section-header">Monthly Engagement (Music Era: 2022–2026)</p>', unsafe_allow_html=True)

    music_era = monthly[monthly["month"] >= "2022-01-01"].sort_values("month")

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=music_era["month"],
        y=music_era["likes"],
        name="Total Likes",
        marker_color=IG_PINK,
        opacity=0.7,
        hovertemplate="%{x|%b %Y}<br>%{y:,} likes<extra></extra>",
    ))
    fig2.add_trace(go.Scatter(
        x=music_era["month"],
        y=music_era["avg_likes"],
        name="Avg Likes",
        mode="lines+markers",
        line=dict(color=ACCENT_BLUE, width=2),
        yaxis="y2",
        hovertemplate="%{x|%b %Y}<br>Avg %{y:.0f} likes<extra></extra>",
    ))
    fig2.update_layout(
        **PLOTLY_LAYOUT,
        height=400,
        yaxis=dict(title="Total Likes"),
        yaxis2=dict(title="Avg Likes", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig2, use_container_width=True, key="growth_monthly")

    st.divider()

    # --- Posting cadence ---
    st.markdown('<p class="section-header">Posting Cadence — Monthly Post Counts</p>', unsafe_allow_html=True)

    fig3 = px.bar(
        music_era, x="month", y="posts",
        color_discrete_sequence=[ACCENT_BLUE],
    )
    fig3.update_layout(**PLOTLY_LAYOUT, height=300, xaxis_title="Month", yaxis_title="Posts")
    fig3.update_traces(hovertemplate="%{x|%b %Y}<br>%{y} posts<extra></extra>")
    st.plotly_chart(fig3, use_container_width=True, key="growth_cadence")

    st.divider()

    # --- Platform growth trajectory (placeholder) ---
    st.markdown('<p class="section-header">Platform Growth Trajectory</p>', unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        # Total likes per year
        yearly_sorted = yearly.sort_values("year")
        yearly_sorted["cumulative_likes"] = yearly_sorted["total_likes"].cumsum()
        fig4 = px.area(
            yearly_sorted, x="year", y="cumulative_likes",
            color_discrete_sequence=[IG_PINK],
        )
        fig4.update_layout(**PLOTLY_LAYOUT, height=300, xaxis_title="Year", yaxis_title="Cumulative Likes")
        fig4.update_traces(hovertemplate="Year %{x}<br>%{y:,} total likes<extra></extra>")
        st.plotly_chart(fig4, use_container_width=True, key="growth_cum_likes")

    with right:
        # Total posts per year
        yearly_sorted["cumulative_posts"] = yearly_sorted["posts"].cumsum()
        fig5 = px.area(
            yearly_sorted, x="year", y="cumulative_posts",
            color_discrete_sequence=[ACCENT_BLUE],
        )
        fig5.update_layout(**PLOTLY_LAYOUT, height=300, xaxis_title="Year", yaxis_title="Cumulative Posts")
        fig5.update_traces(hovertemplate="Year %{x}<br>%{y:,} total posts<extra></extra>")
        st.plotly_chart(fig5, use_container_width=True, key="growth_cum_posts")

    st.info("🔮 **Future**: When Spotify for Artists API is connected, this page will overlay streaming growth with social growth for a unified trajectory view.")
