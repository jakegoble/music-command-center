"""Dashboard — KPI summary and key metrics at a glance."""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Colors
SPOTIFY_GREEN = "#1DB954"
IG_PINK = "#E1306C"
ACCENT_BLUE = "#58a6ff"
MUTED = "#8b949e"
CARD_BG = "#161b22"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#f0f6fc", family="system-ui, -apple-system, sans-serif"),
    margin=dict(l=0, r=0, t=40, b=0),
    hoverlabel=dict(bgcolor="#21262d", font_color="#f0f6fc"),
)


def render() -> None:
    from data_loader import load_songs_all, load_songs_recent, load_ig_insights, load_ig_yearly, load_ig_content_type

    songs = load_songs_all()
    recent = load_songs_recent()
    ig = load_ig_insights()
    yearly = load_ig_yearly()
    content_type = load_ig_content_type()

    st.markdown("# 🏠 Dashboard")
    st.caption("At-a-glance health check of the entire music business")

    # --- KPI row ---
    total_streams = songs["streams"].sum()
    top_song_streams = songs["streams"].max()
    top_song_name = songs.loc[songs["streams"].idxmax(), "song"]
    catalog_size = len(songs)
    atmos_count = 7  # from catalog spec

    c1, c2, c3 = st.columns(3)
    c1.metric("Total All-Time Streams", f"{total_streams:,.0f}")
    c2.metric("IG Followers", f"{ig['account']['followers']:,}")
    c3.metric("Catalog Size", f"{catalog_size} songs ({atmos_count} Dolby Atmos)")

    c4, c5, c6 = st.columns(3)
    c4.metric("Top Song", f"{top_song_streams:,.0f}", help=top_song_name)
    c5.metric("30-Day IG Reach", f"{ig['overview']['accounts_reached']:,} accounts")
    c6.metric("30-Day IG Views", f"{ig['overview']['views_30d']:,}")

    st.divider()

    # --- Charts row 1 ---
    left, right = st.columns(2)

    with left:
        st.markdown('<p class="section-header">Top 10 Songs — All-Time Streams</p>', unsafe_allow_html=True)
        top10 = songs.nlargest(10, "streams").sort_values("streams")
        fig = px.bar(
            top10,
            x="streams",
            y="song",
            orientation="h",
            color_discrete_sequence=[SPOTIFY_GREEN],
        )
        fig.update_layout(**PLOTLY_LAYOUT, height=380, yaxis_title="", xaxis_title="Streams")
        fig.update_traces(hovertemplate="%{y}<br>%{x:,.0f} streams<extra></extra>")
        st.plotly_chart(fig, use_container_width=True, key="dash_top10")

    with right:
        st.markdown('<p class="section-header">IG Engagement by Year (2018–2026)</p>', unsafe_allow_html=True)
        recent_years = yearly[yearly["year"] >= 2018].sort_values("year")
        fig2 = px.line(
            recent_years,
            x="year",
            y="avg_likes",
            markers=True,
            color_discrete_sequence=[IG_PINK],
        )
        fig2.update_layout(**PLOTLY_LAYOUT, height=380, xaxis_title="Year", yaxis_title="Avg Likes / Post")
        fig2.update_traces(
            hovertemplate="Year %{x}<br>Avg %{y:.0f} likes<extra></extra>",
            line=dict(width=3),
            marker=dict(size=10),
        )
        st.plotly_chart(fig2, use_container_width=True, key="dash_ig_yearly")

    # --- Charts row 2 ---
    left2, right2 = st.columns(2)

    with left2:
        st.markdown('<p class="section-header">Top 10 Recent Songs (3-Year Streams)</p>', unsafe_allow_html=True)
        top_recent = recent.nlargest(10, "Streams").sort_values("Streams")
        fig3 = px.bar(
            top_recent,
            x="Streams",
            y="Song Name",
            orientation="h",
            color_discrete_sequence=[ACCENT_BLUE],
        )
        fig3.update_layout(**PLOTLY_LAYOUT, height=380, yaxis_title="", xaxis_title="Streams (3yr)")
        fig3.update_traces(hovertemplate="%{y}<br>%{x:,.0f} streams<extra></extra>")
        st.plotly_chart(fig3, use_container_width=True, key="dash_recent")

    with right2:
        st.markdown('<p class="section-header">Content Type Performance (IG)</p>', unsafe_allow_html=True)
        fig4 = px.pie(
            content_type,
            values="avg_likes",
            names="type",
            color="type",
            color_discrete_map={
                "Video/Reel": IG_PINK,
                "Carousel": ACCENT_BLUE,
                "Photo": MUTED,
            },
            hole=0.45,
        )
        fig4.update_layout(**PLOTLY_LAYOUT, height=380, showlegend=True, legend=dict(orientation="h", y=-0.1))
        fig4.update_traces(
            textinfo="label+percent",
            textfont_color="#f0f6fc",
            hovertemplate="%{label}<br>Avg %{value} likes (%{percent})<extra></extra>",
        )
        st.plotly_chart(fig4, use_container_width=True, key="dash_content_type")
