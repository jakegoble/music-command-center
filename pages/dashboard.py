"""Dashboard — KPI summary and key metrics at a glance."""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from theme import (
    SPOTIFY_GREEN, IG_PINK, ACCENT_BLUE, MUTED, GOLD, AMBER,
    PLOTLY_LAYOUT, kpi_row, section, spacer,
)


def render() -> None:
    from data_loader import (
        load_songs_all, load_songs_recent, load_ig_insights,
        load_ig_yearly, load_ig_content_type,
        load_songstats_jakke, load_songstats_enjune,
    )

    songs = load_songs_all()
    recent = load_songs_recent()
    ig = load_ig_insights()
    yearly = load_ig_yearly()
    content_type = load_ig_content_type()
    ss = load_songstats_jakke()
    enjune = load_songstats_enjune()

    # --- Page header ---
    st.markdown("""
    <div style="margin-bottom:28px">
        <h1 style="margin:0;font-size:1.8rem;font-weight:700;color:#f0f6fc">Dashboard</h1>
        <p style="color:#8b949e;margin:4px 0 0 0;font-size:0.9rem">At-a-glance health check across streaming, social, and catalog</p>
    </div>
    """, unsafe_allow_html=True)

    # --- KPI Row 1: Streaming ---
    top_song = songs.loc[songs["streams"].idxmax()]
    kpi_row([
        {"label": "Cross-Platform Streams", "value": f"{ss['cross_platform']['total_streams']:,.0f}", "sub": f"Spotify: {ss['spotify']['total_streams']:,.0f}", "accent": SPOTIFY_GREEN},
        {"label": "Monthly Listeners", "value": f"{ss['spotify']['monthly_listeners']:,}", "accent": SPOTIFY_GREEN},
        {"label": "Playlists", "value": f"{ss['spotify']['current_playlists']}", "sub": f"Reach: {ss['spotify']['playlist_reach']:,.0f}", "accent": SPOTIFY_GREEN},
        {"label": "Top Song", "value": top_song["song"], "sub": f"{top_song['streams']:,.0f} streams", "accent": GOLD},
    ])
    spacer(14)

    # --- KPI Row 2: Social + Enjune ---
    combined_streams = ss["cross_platform"]["total_streams"] + enjune["spotify"]["total_streams"]
    currently_playlisted = ", ".join(ss["currently_playlisted"])
    kpi_row([
        {"label": "IG Followers", "value": f"{ig['account']['followers']:,}", "accent": IG_PINK},
        {"label": "30-Day IG Views", "value": f"{ig['overview']['views_30d']:,}", "sub": f"{ig['overview']['accounts_reached']:,} reached", "accent": IG_PINK},
        {"label": "Enjune (Legacy)", "value": f"{enjune['spotify']['total_streams']:,.0f}", "sub": f"{enjune['spotify']['monthly_listeners']:,} monthly listeners", "accent": AMBER},
        {"label": "Combined Universe", "value": f"{combined_streams:,.0f}", "sub": "Jakke + Enjune streams", "accent": GOLD},
    ])
    spacer(12)

    # --- Currently playlisted indicator ---
    st.markdown(f"""
    <div style="background:#161b22;border:1px solid #21262d;border-radius:10px;padding:14px 18px;margin-bottom:8px">
        <span style="color:#8b949e;font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em">Currently Playlisted</span>
        <span style="color:#1DB954;font-size:0.9rem;margin-left:12px;font-weight:500">{currently_playlisted}</span>
        <span style="color:#484f58;font-size:0.78rem;margin-left:8px">on {ss['spotify']['current_playlists']} playlists</span>
    </div>
    """, unsafe_allow_html=True)

    spacer(24)

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
        section("Top Playlists by Reach")
        playlists = ss["top_playlists"][:8]
        pl_names = [p["name"][:30] for p in reversed(playlists)]
        pl_followers = [p["followers"] for p in reversed(playlists)]
        fig4 = px.bar(x=pl_followers, y=pl_names, orientation="h", color_discrete_sequence=[SPOTIFY_GREEN])
        fig4.update_layout(**PLOTLY_LAYOUT, height=380, yaxis_title="", xaxis_title="")
        fig4.update_xaxes(tickformat=",")
        fig4.update_traces(hovertemplate="%{y}<br><b>%{x:,}</b> followers<extra></extra>")
        st.plotly_chart(fig4, use_container_width=True, key="dash_playlists")
