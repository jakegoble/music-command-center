"""Streaming — Deep dive into streaming performance."""
from __future__ import annotations

from datetime import datetime

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

from theme import (
    SPOTIFY_GREEN, ACCENT_BLUE, AMBER, GOLD, MUTED, PLOTLY_LAYOUT,
    kpi_row, section, spacer, genre_pill, render_page_title, PLOTLY_CONFIG,
    get_platform_icon_html, time_range_selector, chart_layout,
)


def render() -> None:
    from data_loader import load_songs_all, load_songs_recent, load_songstats_jakke

    songs = load_songs_all()
    recent = load_songs_recent()
    ss = load_songstats_jakke()

    render_page_title("Streaming", "Deep dive into streaming performance across all songs", "#1DB954")

    # --- KPIs with Songstats data ---
    total = songs["streams"].sum()
    avg_streams = songs["streams"].mean()
    median_streams = songs["streams"].median()
    spotify_icon = get_platform_icon_html("spotify", 14)

    kpi_row([
        {"label": "Cross-Platform Streams", "value": f"{ss['cross_platform']['total_streams']:,.0f}", "sub": f"Spotify: {ss['spotify']['total_streams']:,.0f}", "accent": SPOTIFY_GREEN, "icon_html": spotify_icon},
        {"label": "Monthly Listeners", "value": f"{ss['spotify']['monthly_listeners']:,}", "accent": SPOTIFY_GREEN},
        {"label": "Catalog Size", "value": f"{len(songs)} songs", "sub": f"Avg {avg_streams:,.0f} / song"},
        {"label": "Playlists", "value": f"{ss['spotify']['current_playlists']}", "sub": f"Reach: {ss['spotify']['playlist_reach']:,.0f}", "accent": GOLD},
    ])

    spacer(20)

    # --- Filters row ---
    filter_left, filter_right = st.columns([1, 2])
    with filter_left:
        artist_filter = st.selectbox("Filter by Artist", ["All", "Jakke", "iLÜ"], key="streaming_artist")
    with filter_right:
        time_range = time_range_selector("streaming_time_range", default="All")

    filtered = songs if artist_filter == "All" else songs[songs["artist"] == artist_filter]

    # Apply time range filter
    if time_range != "All" and "release_date" in filtered.columns:
        import pandas as pd
        from datetime import datetime, timedelta
        now = pd.Timestamp(datetime.now())
        range_map = {"1m": 30, "3m": 90, "6m": 180, "YTD": (now - pd.Timestamp(f"{now.year}-01-01")).days, "1y": 365}
        days = range_map.get(time_range, 99999)
        cutoff = now - timedelta(days=days)
        filtered = filtered[filtered["release_date"].notna() & (filtered["release_date"] >= cutoff)]

    spacer(12)

    # --- All-time vs Recent side by side ---
    left, right = st.columns(2, gap="large")

    with left:
        section("All-Time — Top 15")
        top15 = filtered.nlargest(15, "streams").sort_values("streams")
        fig1 = px.bar(top15, x="streams", y="song", orientation="h", color_discrete_sequence=[SPOTIFY_GREEN])
        fig1.update_layout(**PLOTLY_LAYOUT, height=480, yaxis_title="", xaxis_title="")
        fig1.update_xaxes(tickformat=",")
        fig1.update_traces(hovertemplate="%{y}<br><b>%{x:,.0f}</b> streams<extra></extra>")
        st.plotly_chart(fig1, use_container_width=True, key="stream_alltime", config=PLOTLY_CONFIG)

    with right:
        section("Recent 3-Year — Top 15")
        top15_recent = recent.nlargest(15, "Streams").sort_values("Streams")
        fig2 = px.bar(top15_recent, x="Streams", y="Song Name", orientation="h", color_discrete_sequence=[ACCENT_BLUE])
        fig2.update_layout(**PLOTLY_LAYOUT, height=480, yaxis_title="", xaxis_title="")
        fig2.update_xaxes(tickformat=",")
        fig2.update_traces(hovertemplate="%{y}<br><b>%{x:,.0f}</b> streams<extra></extra>")
        st.plotly_chart(fig2, use_container_width=True, key="stream_recent", config=PLOTLY_CONFIG)

    spacer(28)

    # --- Popularity scores ---
    section("Spotify Popularity Scores")
    pop_data = filtered[filtered["popularity"] > 0].sort_values("popularity", ascending=True).copy()

    if not pop_data.empty:
        fig_pop = px.bar(
            pop_data, x="popularity", y="song", orientation="h",
            color="popularity", color_continuous_scale=[[0, MUTED], [0.5, ACCENT_BLUE], [1, SPOTIFY_GREEN]],
        )
        fig_pop.update_layout(**PLOTLY_LAYOUT, height=max(300, len(pop_data) * 30), yaxis_title="", xaxis_title="Popularity Score (0-100)", coloraxis_showscale=False)
        fig_pop.update_traces(hovertemplate="%{y}<br>Popularity: <b>%{x}</b>/100<extra></extra>")
        st.plotly_chart(fig_pop, use_container_width=True, key="stream_popularity", config=PLOTLY_CONFIG)
    else:
        st.caption("No popularity scores available for this filter.")

    spacer(28)

    # --- Velocity analysis ---
    section("Velocity — Streams per Day Since Release")
    velocity = filtered.dropna(subset=["release_date"]).copy()
    today = pd.Timestamp(datetime.now())
    velocity["days_since_release"] = (today - velocity["release_date"]).dt.days
    velocity["streams_per_day"] = velocity["streams"] / velocity["days_since_release"].clip(lower=1)
    velocity = velocity.sort_values("streams_per_day", ascending=False)

    left2, right2 = st.columns(2, gap="large")

    with left2:
        top_vel = velocity.head(12).sort_values("streams_per_day")
        fig3 = px.bar(top_vel, x="streams_per_day", y="song", orientation="h", color_discrete_sequence=[AMBER])
        fig3.update_layout(**PLOTLY_LAYOUT, height=400, yaxis_title="", xaxis_title="Streams / Day")
        fig3.update_traces(hovertemplate="%{y}<br><b>%{x:.1f}</b> streams/day<extra></extra>")
        st.plotly_chart(fig3, use_container_width=True, key="stream_velocity", config=PLOTLY_CONFIG)

    with right2:
        section("Release Impact")
        color_col = "artist" if artist_filter == "All" else None
        fig4 = px.scatter(
            velocity, x="release_date", y="streams", size="streams_per_day",
            hover_name="song", color=color_col,
            color_discrete_map={"Jakke": SPOTIFY_GREEN, "iLÜ": "#a78bfa"},
            color_discrete_sequence=[SPOTIFY_GREEN], size_max=45,
        )
        fig4.update_layout(**PLOTLY_LAYOUT, height=400, xaxis_title="", yaxis_title="Total Streams")
        fig4.update_yaxes(tickformat=",")
        fig4.update_traces(hovertemplate="%{hovertext}<br>%{x|%b %Y}<br><b>%{y:,.0f}</b> streams<extra></extra>")
        st.plotly_chart(fig4, use_container_width=True, key="stream_impact", config=PLOTLY_CONFIG)

    spacer(24)

    # --- Dual-axis: Streams vs Popularity (D7) ---
    section("Streams vs Popularity (Dual Axis)")
    dual_data = filtered[filtered["popularity"] > 0].sort_values("streams", ascending=False).head(15).sort_values("streams")
    if not dual_data.empty:
        fig_dual = go.Figure()
        fig_dual.add_trace(go.Bar(
            x=dual_data["streams"], y=dual_data["song"], orientation="h",
            name="Streams", marker_color=SPOTIFY_GREEN, opacity=0.8,
            hovertemplate="%{y}<br><b>%{x:,.0f}</b> streams<extra></extra>",
        ))
        fig_dual.add_trace(go.Scatter(
            x=dual_data["popularity"], y=dual_data["song"], mode="markers",
            name="Popularity", marker=dict(color=GOLD, size=10, symbol="diamond"),
            xaxis="x2",
            hovertemplate="%{y}<br>Popularity: <b>%{x}</b>/100<extra></extra>",
        ))
        fig_dual.update_layout(**chart_layout(
            height=max(340, len(dual_data) * 30),
            yaxis=dict(title=""),
            xaxis=dict(title="Streams", side="bottom"),
            xaxis2=dict(title="Popularity Score", overlaying="x", side="top", showgrid=False, range=[0, 100]),
            legend=dict(orientation="h", y=1.15),
        ))
        fig_dual.update_xaxes(tickformat=",", selector=dict(side="bottom"))
        st.plotly_chart(fig_dual, use_container_width=True, key="stream_dual_axis", config=PLOTLY_CONFIG)
    else:
        st.caption("No songs with popularity scores in current filter.")

    spacer(24)

    # --- Song detail expanders ---
    section("Song Details — Top 10")
    recent_lookup = dict(zip(recent["Song Name"], recent["Streams"]))

    for _, row in filtered.nlargest(10, "streams").iterrows():
        recent_count = recent_lookup.get(row["song"], 0)
        release = row["release_date"].strftime("%b %d, %Y") if pd.notna(row["release_date"]) else "Unknown"
        pct_recent = (recent_count / row["streams"] * 100) if row["streams"] > 0 else 0
        collab_str = row.get("collaborators", "—") if pd.notna(row.get("collaborators", None)) else "—"
        pop_str = f"{int(row['popularity'])}%" if row.get("popularity", 0) > 0 else "—"
        song_genre = row.get("genre", "")
        with st.expander(f"{row['song']} — {row['streams']:,} all-time"):
            if song_genre:
                st.markdown(genre_pill(song_genre), unsafe_allow_html=True)
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("All-Time", f"{row['streams']:,}")
            c2.metric("Recent (3yr)", f"{recent_count:,}")
            c3.metric("% Recent", f"{pct_recent:.1f}%")
            c4.metric("Released", release)
            c5.metric("Popularity", pop_str)
            if collab_str != "—":
                st.caption(f"Collaborators: {collab_str}")
