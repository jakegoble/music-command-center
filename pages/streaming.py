"""Streaming — Deep dive into streaming performance."""
from __future__ import annotations

from datetime import datetime

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

from theme import SPOTIFY_GREEN, ACCENT_BLUE, AMBER, MUTED, PLOTLY_LAYOUT, kpi_row, section, spacer


def render() -> None:
    from data_loader import load_songs_all, load_songs_recent

    songs = load_songs_all()
    recent = load_songs_recent()

    st.markdown("""
    <div style="margin-bottom:28px">
        <h1 style="margin:0;font-size:1.8rem;font-weight:700;color:#f0f6fc">Streaming</h1>
        <p style="color:#8b949e;margin:4px 0 0 0;font-size:0.9rem">Deep dive into streaming performance across all songs</p>
    </div>
    """, unsafe_allow_html=True)

    # --- KPIs ---
    total = songs["streams"].sum()
    avg_streams = songs["streams"].mean()
    median_streams = songs["streams"].median()

    kpi_row([
        {"label": "Total Streams", "value": f"{total:,.0f}", "accent": SPOTIFY_GREEN},
        {"label": "Catalog Size", "value": f"{len(songs)} songs"},
        {"label": "Avg / Song", "value": f"{avg_streams:,.0f}"},
        {"label": "Median", "value": f"{median_streams:,.0f}", "sub": "50th percentile"},
    ])

    spacer(28)

    # --- All-time vs Recent side by side ---
    left, right = st.columns(2, gap="large")

    with left:
        section("All-Time — Top 15")
        top15 = songs.nlargest(15, "streams").sort_values("streams")
        fig1 = px.bar(top15, x="streams", y="song", orientation="h", color_discrete_sequence=[SPOTIFY_GREEN])
        fig1.update_layout(**PLOTLY_LAYOUT, height=480, yaxis_title="", xaxis_title="")
        fig1.update_xaxes(tickformat=",")
        fig1.update_traces(hovertemplate="%{y}<br><b>%{x:,.0f}</b> streams<extra></extra>")
        st.plotly_chart(fig1, use_container_width=True, key="stream_alltime")

    with right:
        section("Recent 3-Year — Top 15")
        top15_recent = recent.nlargest(15, "Streams").sort_values("Streams")
        fig2 = px.bar(top15_recent, x="Streams", y="Song Name", orientation="h", color_discrete_sequence=[ACCENT_BLUE])
        fig2.update_layout(**PLOTLY_LAYOUT, height=480, yaxis_title="", xaxis_title="")
        fig2.update_xaxes(tickformat=",")
        fig2.update_traces(hovertemplate="%{y}<br><b>%{x:,.0f}</b> streams<extra></extra>")
        st.plotly_chart(fig2, use_container_width=True, key="stream_recent")

    spacer(28)

    # --- Velocity analysis ---
    section("Velocity — Streams per Day Since Release")
    velocity = songs.dropna(subset=["release_date"]).copy()
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
        st.plotly_chart(fig3, use_container_width=True, key="stream_velocity")

    with right2:
        section("Release Impact")
        fig4 = px.scatter(
            velocity, x="release_date", y="streams", size="streams_per_day",
            hover_name="song", color_discrete_sequence=[SPOTIFY_GREEN], size_max=45,
        )
        fig4.update_layout(**PLOTLY_LAYOUT, height=400, xaxis_title="", yaxis_title="Total Streams")
        fig4.update_yaxes(tickformat=",")
        fig4.update_traces(hovertemplate="%{hovertext}<br>%{x|%b %Y}<br><b>%{y:,.0f}</b> streams<extra></extra>")
        st.plotly_chart(fig4, use_container_width=True, key="stream_impact")

    spacer(24)

    # --- Song detail expanders ---
    section("Song Details — Top 10")
    recent_lookup = dict(zip(recent["Song Name"], recent["Streams"]))

    for _, row in songs.nlargest(10, "streams").iterrows():
        recent_count = recent_lookup.get(row["song"], 0)
        release = row["release_date"].strftime("%b %d, %Y") if pd.notna(row["release_date"]) else "Unknown"
        pct_recent = (recent_count / row["streams"] * 100) if row["streams"] > 0 else 0
        with st.expander(f"{row['song']} — {row['streams']:,} all-time"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("All-Time", f"{row['streams']:,}")
            c2.metric("Recent (3yr)", f"{recent_count:,}")
            c3.metric("% Recent", f"{pct_recent:.1f}%")
            c4.metric("Released", release)
