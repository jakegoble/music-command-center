"""Cross-Platform — Unified analytics across all connected platforms."""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

from theme import (
    SPOTIFY_GREEN, IG_PINK, ACCENT_BLUE, GOLD, AMBER, MUTED,
    PLOTLY_LAYOUT, kpi_row, section, spacer,
)


def render() -> None:
    from data_loader import load_songstats_jakke, load_songstats_enjune, load_ig_insights, load_songs_all
    from services.config import get_all_api_status
    from services.youtube_client import get_channel_stats, get_recent_videos, is_available as yt_available
    from services.lastfm_client import get_artist_info, get_similar_artists, is_available as lastfm_available

    ss = load_songstats_jakke()
    enjune = load_songstats_enjune()
    ig = load_ig_insights()
    songs = load_songs_all()

    st.markdown("""
    <div style="margin-bottom:28px">
        <h1 style="margin:0;font-size:1.8rem;font-weight:700;color:#f0f6fc">Cross-Platform</h1>
        <p style="color:#8b949e;margin:4px 0 0 0;font-size:0.9rem">Unified view across streaming, social, and video platforms</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Universe KPIs ---
    combined_streams = ss["cross_platform"]["total_streams"] + enjune["spotify"]["total_streams"]
    combined_playlists = ss["cross_platform"].get("total_playlists", ss["spotify"]["current_playlists"]) + enjune.get("cross_platform", enjune["spotify"]).get("total_playlists", enjune["spotify"]["current_playlists"])
    combined_followers = ss["cross_platform"].get("total_followers", ss["spotify"]["followers"]) + ig["account"]["followers"]

    kpi_row([
        {"label": "Total Streams (All Artists)", "value": f"{combined_streams:,.0f}", "sub": f"Jakke: {ss['cross_platform']['total_streams']:,.0f} · Enjune: {enjune['spotify']['total_streams']:,.0f}", "accent": GOLD},
        {"label": "Total Followers", "value": f"{combined_followers:,}", "sub": f"Spotify: {ss['spotify']['followers']:,} · IG: {ig['account']['followers']:,}", "accent": ACCENT_BLUE},
        {"label": "Monthly Listeners", "value": f"{ss['spotify']['monthly_listeners']:,}", "sub": f"Enjune: {enjune['spotify']['monthly_listeners']:,}", "accent": SPOTIFY_GREEN},
        {"label": "Total Playlists", "value": f"{combined_playlists:,}", "sub": f"Reach: {ss['spotify']['playlist_reach'] + enjune['spotify']['playlist_reach']:,.0f}", "accent": SPOTIFY_GREEN},
    ])

    spacer(28)

    # --- Platform breakdown chart ---
    left, right = st.columns(2, gap="large")

    with left:
        section("Streams by Artist Project")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["Jakke (Spotify)", "Jakke (Cross-Platform)", "Enjune"],
            y=[ss["spotify"]["total_streams"], ss["cross_platform"]["total_streams"], enjune["spotify"]["total_streams"]],
            marker_color=[SPOTIFY_GREEN, ACCENT_BLUE, AMBER],
            text=[f"{ss['spotify']['total_streams']:,.0f}", f"{ss['cross_platform']['total_streams']:,.0f}", f"{enjune['spotify']['total_streams']:,.0f}"],
            textposition="outside", textfont=dict(color="#f0f6fc", size=11),
            hovertemplate="%{x}<br><b>%{y:,.0f}</b> streams<extra></extra>",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=360, yaxis_title="Streams")
        fig.update_yaxes(tickformat=",")
        st.plotly_chart(fig, use_container_width=True, key="xp_streams_artist")

    with right:
        section("Follower Distribution")
        follower_data = pd.DataFrame([
            {"Platform": "Instagram", "Followers": ig["account"]["followers"]},
            {"Platform": "Spotify (Jakke)", "Followers": ss["spotify"]["followers"]},
            {"Platform": "Spotify (Enjune)", "Followers": enjune["spotify"]["followers"]},
        ])
        colors_map = {"Instagram": IG_PINK, "Spotify (Jakke)": SPOTIFY_GREEN, "Spotify (Enjune)": AMBER}
        fig2 = px.pie(follower_data, values="Followers", names="Platform", color="Platform",
                      color_discrete_map=colors_map, hole=0.45)
        fig2.update_layout(**PLOTLY_LAYOUT, height=360, showlegend=True, legend=dict(orientation="h", y=-0.05))
        fig2.update_traces(textinfo="label+percent", textfont_color="#f0f6fc",
                           hovertemplate="%{label}<br><b>%{value:,}</b> followers<extra></extra>")
        st.plotly_chart(fig2, use_container_width=True, key="xp_followers")

    spacer(28)

    # --- Playlist intelligence ---
    section("Top Playlists Across All Projects")
    jakke_playlists = [{"name": p["name"], "followers": p["followers"], "artist": "Jakke"} for p in ss.get("top_playlists", [])]
    enjune_playlists = [{"name": p["name"], "followers": p["followers"], "artist": "Enjune"} for p in enjune.get("top_playlists", [])]
    all_playlists = sorted(jakke_playlists + enjune_playlists, key=lambda x: x["followers"], reverse=True)[:15]

    if all_playlists:
        pl_df = pd.DataFrame(all_playlists)
        pl_sorted = pl_df.sort_values("followers")
        fig_pl = px.bar(
            pl_sorted, x="followers", y="name", orientation="h",
            color="artist", color_discrete_map={"Jakke": SPOTIFY_GREEN, "Enjune": AMBER},
        )
        fig_pl.update_layout(**PLOTLY_LAYOUT, height=max(360, len(all_playlists) * 28), yaxis_title="", xaxis_title="Playlist Followers")
        fig_pl.update_xaxes(tickformat=",")
        fig_pl.update_traces(hovertemplate="%{y}<br><b>%{x:,}</b> followers<extra></extra>")
        st.plotly_chart(fig_pl, use_container_width=True, key="xp_playlists")

    spacer(28)

    # --- YouTube (live data if configured) ---
    section("YouTube")
    if yt_available():
        yt_stats = get_channel_stats()
        if yt_stats:
            kpi_row([
                {"label": "Subscribers", "value": f"{yt_stats['subscribers']:,}", "accent": "#ff0000"},
                {"label": "Total Views", "value": f"{yt_stats['total_views']:,}"},
                {"label": "Videos", "value": str(yt_stats["video_count"])},
            ])
            spacer(16)
            videos = get_recent_videos(limit=5)
            if videos:
                section("Recent Videos")
                for v in videos:
                    with st.expander(f"{v['title']} — {v['views']:,} views"):
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Views", f"{v['views']:,}")
                        c2.metric("Likes", f"{v['likes']:,}")
                        c3.metric("Comments", f"{v['comments']:,}")
                        st.markdown(f"[Watch on YouTube]({v['url']})")
        else:
            st.info("YouTube channel ID configured but no data returned. Verify JAKKE_YOUTUBE_CHANNEL.")
    else:
        st.markdown("""
<div style="background:#161b22;border:1px solid #21262d;border-radius:10px;padding:18px 20px">
<div style="color:#8b949e;font-size:0.88rem">
YouTube data requires a free API key. Set <code>YOUTUBE_API_KEY</code> and <code>JAKKE_YOUTUBE_CHANNEL</code> in secrets.
</div></div>
        """, unsafe_allow_html=True)

    spacer(28)

    # --- Last.fm (live data if configured) ---
    section("Last.fm")
    if lastfm_available():
        jakke_lastfm = get_artist_info("Jakke")
        if jakke_lastfm:
            kpi_row([
                {"label": "Last.fm Listeners", "value": f"{jakke_lastfm['listeners']:,}", "accent": "#d51007"},
                {"label": "Scrobbles", "value": f"{jakke_lastfm['playcount']:,}"},
                {"label": "Tags", "value": ", ".join(jakke_lastfm["tags"][:3]) if jakke_lastfm["tags"] else "—"},
            ])

            spacer(16)
            similar = get_similar_artists("Jakke", limit=8)
            if similar:
                section("Similar Artists (Last.fm)")
                sim_df = pd.DataFrame(similar)
                sim_df["match_pct"] = (sim_df["match"] * 100).round(1)
                fig_sim = px.bar(
                    sim_df.sort_values("match_pct"), x="match_pct", y="name",
                    orientation="h", color_discrete_sequence=[ACCENT_BLUE],
                )
                fig_sim.update_layout(**PLOTLY_LAYOUT, height=max(280, len(similar) * 32), yaxis_title="", xaxis_title="Match %")
                fig_sim.update_traces(hovertemplate="%{y}<br><b>%{x:.1f}%</b> match<extra></extra>")
                st.plotly_chart(fig_sim, use_container_width=True, key="xp_lastfm_similar")
    else:
        st.markdown("""
<div style="background:#161b22;border:1px solid #21262d;border-radius:10px;padding:18px 20px">
<div style="color:#8b949e;font-size:0.88rem">
Last.fm data requires a free API key. Set <code>LASTFM_API_KEY</code> in secrets.
</div></div>
        """, unsafe_allow_html=True)

    spacer(28)

    # --- API Connection Status ---
    section("API Connection Status")
    statuses = get_all_api_status()
    cols = st.columns(len(statuses))
    for col, status in zip(cols, statuses):
        with col:
            icon = "🟢" if status.configured else "⚪"
            label = "Connected" if status.configured else "Not configured"
            st.markdown(f"""
<div style="background:#161b22;border:1px solid #21262d;border-radius:10px;padding:12px 14px;text-align:center">
    <div style="font-size:1.2rem;margin-bottom:4px">{icon}</div>
    <div style="font-size:0.75rem;color:#8b949e;font-weight:600;text-transform:uppercase;letter-spacing:0.05em">{status.name}</div>
    <div style="font-size:0.72rem;color:{'#3fb950' if status.configured else '#484f58'};margin-top:2px">{label}</div>
</div>
            """, unsafe_allow_html=True)
