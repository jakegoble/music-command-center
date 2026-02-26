"""Streaming — Deep dive into streaming performance."""
from __future__ import annotations

from datetime import datetime

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

SPOTIFY_GREEN = "#1DB954"
ACCENT_BLUE = "#58a6ff"
AMBER = "#f0883e"
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#f0f6fc", family="system-ui, -apple-system, sans-serif"),
    margin=dict(l=0, r=0, t=40, b=0),
    hoverlabel=dict(bgcolor="#21262d", font_color="#f0f6fc"),
)


def render() -> None:
    from data_loader import load_songs_all, load_songs_recent

    songs = load_songs_all()
    recent = load_songs_recent()

    st.markdown("# 📊 Streaming")
    st.caption("Deep dive into streaming performance across all songs")

    # --- KPI row ---
    total = songs["streams"].sum()
    avg_streams = songs["streams"].mean()
    median_streams = songs["streams"].median()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Streams", f"{total:,.0f}")
    c2.metric("Songs", f"{len(songs)}")
    c3.metric("Avg Streams/Song", f"{avg_streams:,.0f}")
    c4.metric("Median Streams", f"{median_streams:,.0f}")

    st.divider()

    # --- All-time rankings ---
    st.markdown('<p class="section-header">All-Time Rankings — All 30 Songs</p>', unsafe_allow_html=True)
    sorted_all = songs.sort_values("streams", ascending=True)
    fig1 = px.bar(
        sorted_all,
        x="streams",
        y="song",
        orientation="h",
        color_discrete_sequence=[SPOTIFY_GREEN],
    )
    fig1.update_layout(**PLOTLY_LAYOUT, height=max(400, len(songs) * 28), yaxis_title="", xaxis_title="All-Time Streams")
    fig1.update_traces(hovertemplate="%{y}<br>%{x:,.0f} streams<extra></extra>")
    st.plotly_chart(fig1, use_container_width=True, key="stream_alltime")

    st.divider()

    # --- Recent period rankings ---
    st.markdown('<p class="section-header">Recent Period (3-Year) Rankings</p>', unsafe_allow_html=True)
    sorted_recent = recent.sort_values("Streams", ascending=True)
    fig2 = px.bar(
        sorted_recent,
        x="Streams",
        y="Song Name",
        orientation="h",
        color_discrete_sequence=[ACCENT_BLUE],
    )
    fig2.update_layout(**PLOTLY_LAYOUT, height=max(400, len(recent) * 28), yaxis_title="", xaxis_title="Streams (3yr)")
    fig2.update_traces(hovertemplate="%{y}<br>%{x:,.0f} recent streams<extra></extra>")
    st.plotly_chart(fig2, use_container_width=True, key="stream_recent")

    st.divider()

    # --- Velocity analysis ---
    st.markdown('<p class="section-header">Velocity Analysis — Streams per Day Since Release</p>', unsafe_allow_html=True)
    velocity = songs.dropna(subset=["release_date"]).copy()
    today = pd.Timestamp(datetime.now())
    velocity["days_since_release"] = (today - velocity["release_date"]).dt.days
    velocity["streams_per_day"] = velocity["streams"] / velocity["days_since_release"].clip(lower=1)
    velocity = velocity.sort_values("streams_per_day", ascending=False)

    top_velocity = velocity.head(15).sort_values("streams_per_day")
    fig3 = px.bar(
        top_velocity,
        x="streams_per_day",
        y="song",
        orientation="h",
        color_discrete_sequence=[AMBER],
    )
    fig3.update_layout(**PLOTLY_LAYOUT, height=450, yaxis_title="", xaxis_title="Streams / Day")
    fig3.update_traces(hovertemplate="%{y}<br>%{x:.1f} streams/day<extra></extra>")
    st.plotly_chart(fig3, use_container_width=True, key="stream_velocity")

    st.divider()

    # --- Release impact scatter ---
    st.markdown('<p class="section-header">Release Impact — Date vs Total Streams</p>', unsafe_allow_html=True)
    fig4 = px.scatter(
        velocity,
        x="release_date",
        y="streams",
        size="streams_per_day",
        hover_name="song",
        color_discrete_sequence=[SPOTIFY_GREEN],
        size_max=50,
    )
    fig4.update_layout(**PLOTLY_LAYOUT, height=450, xaxis_title="Release Date", yaxis_title="Total Streams")
    fig4.update_traces(
        hovertemplate="%{hovertext}<br>Released %{x|%b %d, %Y}<br>%{y:,.0f} total streams<br>Size = velocity<extra></extra>"
    )
    st.plotly_chart(fig4, use_container_width=True, key="stream_impact")

    # --- Song detail expanders ---
    st.divider()
    st.markdown('<p class="section-header">Song Details</p>', unsafe_allow_html=True)

    # Merge all-time with recent
    recent_lookup = dict(zip(recent["Song Name"], recent["Streams"]))

    for _, row in songs.nlargest(10, "streams").iterrows():
        recent_count = recent_lookup.get(row["song"], 0)
        release = row["release_date"].strftime("%b %d, %Y") if pd.notna(row["release_date"]) else "Unknown"
        with st.expander(f"🎵 {row['song']} — {row['streams']:,} all-time"):
            c1, c2, c3 = st.columns(3)
            c1.metric("All-Time Streams", f"{row['streams']:,}")
            c2.metric("Recent (3yr) Streams", f"{recent_count:,}")
            c3.metric("Release Date", release)
