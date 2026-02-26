"""Dashboard — KPI summary and key metrics at a glance."""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from theme import (
    SPOTIFY_GREEN, IG_PINK, ACCENT_BLUE, MUTED, GOLD,
    PLOTLY_LAYOUT, kpi_row, section, spacer,
)


def render() -> None:
    from data_loader import load_songs_all, load_songs_recent, load_ig_insights, load_ig_yearly, load_ig_content_type

    songs = load_songs_all()
    recent = load_songs_recent()
    ig = load_ig_insights()
    yearly = load_ig_yearly()
    content_type = load_ig_content_type()

    # --- Page header ---
    st.markdown("""
    <div style="margin-bottom:28px">
        <h1 style="margin:0;font-size:1.8rem;font-weight:700;color:#f0f6fc">Dashboard</h1>
        <p style="color:#8b949e;margin:4px 0 0 0;font-size:0.9rem">At-a-glance health check across streaming, social, and catalog</p>
    </div>
    """, unsafe_allow_html=True)

    # --- KPI cards ---
    total_streams = songs["streams"].sum()
    top_song = songs.loc[songs["streams"].idxmax()]
    recent_top = recent.nlargest(1, "Streams").iloc[0]

    kpi_row([
        {"label": "All-Time Streams", "value": f"{total_streams:,.0f}", "accent": SPOTIFY_GREEN},
        {"label": "IG Followers", "value": f"{ig['account']['followers']:,}", "accent": IG_PINK},
        {"label": "Catalog", "value": "30 songs", "sub": "7 with Dolby Atmos"},
    ])
    spacer(14)
    kpi_row([
        {"label": "Top Song (All-Time)", "value": f"{top_song['streams']:,.0f}", "sub": top_song["song"], "accent": SPOTIFY_GREEN},
        {"label": "Top Song (Recent 3yr)", "value": f"{recent_top['Streams']:,}", "sub": recent_top["Song Name"], "accent": ACCENT_BLUE},
        {"label": "30-Day IG Views", "value": f"{ig['overview']['views_30d']:,}", "sub": f"{ig['overview']['accounts_reached']:,} accounts reached", "accent": IG_PINK},
    ])

    spacer(32)

    # --- Charts row 1 ---
    left, right = st.columns(2, gap="large")

    with left:
        section("Top 10 Songs — All-Time Streams")
        top10 = songs.nlargest(10, "streams").sort_values("streams")
        fig = px.bar(top10, x="streams", y="song", orientation="h", color_discrete_sequence=[SPOTIFY_GREEN])
        fig.update_layout(**PLOTLY_LAYOUT, height=380, yaxis_title="", xaxis_title="")
        fig.update_xaxes(tickformat=",")
        fig.update_traces(hovertemplate="%{y}<br><b>%{x:,.0f}</b> streams<extra></extra>")
        st.plotly_chart(fig, use_container_width=True, key="dash_top10")

    with right:
        section("IG Engagement by Year")
        recent_years = yearly[yearly["year"] >= 2017].sort_values("year")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=recent_years["year"], y=recent_years["avg_likes"],
            mode="lines+markers",
            line=dict(color=IG_PINK, width=3),
            marker=dict(size=8, color=IG_PINK),
            fill="tozeroy",
            fillcolor="rgba(225,48,108,0.08)",
            hovertemplate="<b>%{x}</b><br>Avg %{y:.0f} likes/post<extra></extra>",
        ))
        fig2.add_annotation(x=2017, y=470, text="Peak: 470", showarrow=True, arrowhead=0, arrowcolor=GOLD, font=dict(color=GOLD, size=11))
        fig2.update_layout(**PLOTLY_LAYOUT, height=380, yaxis_title="Avg Likes / Post", xaxis_title="")
        st.plotly_chart(fig2, use_container_width=True, key="dash_ig_yearly")

    spacer(16)

    # --- Charts row 2 ---
    left2, right2 = st.columns(2, gap="large")

    with left2:
        section("Top 10 Recent Songs (3-Year)")
        top_recent = recent.nlargest(10, "Streams").sort_values("Streams")
        fig3 = px.bar(top_recent, x="Streams", y="Song Name", orientation="h", color_discrete_sequence=[ACCENT_BLUE])
        fig3.update_layout(**PLOTLY_LAYOUT, height=380, yaxis_title="", xaxis_title="")
        fig3.update_xaxes(tickformat=",")
        fig3.update_traces(hovertemplate="%{y}<br><b>%{x:,.0f}</b> streams<extra></extra>")
        st.plotly_chart(fig3, use_container_width=True, key="dash_recent")

    with right2:
        section("Content Type Performance (IG)")
        fig4 = px.pie(
            content_type, values="avg_likes", names="type", color="type",
            color_discrete_map={"Video/Reel": IG_PINK, "Carousel": ACCENT_BLUE, "Photo": MUTED},
            hole=0.5,
        )
        fig4.update_layout(**PLOTLY_LAYOUT, height=380, showlegend=True, legend=dict(orientation="h", y=-0.05, font=dict(size=12)))
        fig4.update_traces(
            textinfo="label+percent", textfont=dict(color="#f0f6fc", size=13),
            hovertemplate="%{label}<br>Avg <b>%{value}</b> likes (%{percent})<extra></extra>",
        )
        st.plotly_chart(fig4, use_container_width=True, key="dash_content_type")
