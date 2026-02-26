"""Catalog — Song library with metadata and rights info."""
from __future__ import annotations

import plotly.express as px
import pandas as pd
import streamlit as st

SPOTIFY_GREEN = "#1DB954"
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#f0f6fc", family="system-ui, -apple-system, sans-serif"),
    margin=dict(l=0, r=0, t=40, b=0),
    hoverlabel=dict(bgcolor="#21262d", font_color="#f0f6fc"),
)


def render() -> None:
    from data_loader import load_songs_all, load_catalog

    songs = load_songs_all()
    catalog_raw = load_catalog()

    st.markdown("# 🎵 Catalog")
    st.caption("Complete song library with metadata and rights")

    # Merge catalog (recordings only) with streaming data
    recordings = catalog_raw[catalog_raw["Type"] == "Recording"].copy()
    recordings = recordings.rename(columns={"Title": "song", "Artist/Project": "artist"})

    merged = songs.merge(recordings[["song", "artist", "Writers", "ISRC", "Dolby Atmos"]], on="song", how="left")
    merged["artist"] = merged["artist"].fillna("Jakke")
    merged["Writers"] = merged["Writers"].fillna("—")
    merged["ISRC"] = merged["ISRC"].fillna("—")
    merged["Dolby Atmos"] = merged["Dolby Atmos"].fillna("No")

    # --- Artist filter ---
    artist_filter = st.selectbox("Filter by Artist", ["All", "Jakke", "iLÜ"])
    if artist_filter != "All":
        merged = merged[merged["artist"] == artist_filter]

    # --- Song table ---
    st.markdown(f"**{len(merged)} songs**")
    display = merged[["song", "artist", "streams", "release_date", "Writers", "ISRC", "Dolby Atmos"]].copy()
    display.columns = ["Song", "Artist", "Streams", "Release Date", "Writers", "ISRC", "Dolby Atmos"]
    display = display.sort_values("Streams", ascending=False).reset_index(drop=True)
    display["Streams"] = display["Streams"].apply(lambda x: f"{x:,}")
    display["Release Date"] = display["Release Date"].dt.strftime("%Y-%m-%d").fillna("—")

    st.dataframe(display, use_container_width=True, hide_index=True, height=500)

    st.divider()

    # --- Release timeline ---
    st.markdown('<p class="section-header">Release Timeline</p>', unsafe_allow_html=True)
    timeline_data = merged.dropna(subset=["release_date"]).copy()
    fig = px.scatter(
        timeline_data,
        x="release_date",
        y="streams",
        size="streams",
        color="artist" if artist_filter == "All" else None,
        color_discrete_map={"Jakke": SPOTIFY_GREEN, "iLÜ": "#a78bfa"},
        hover_name="song",
        size_max=40,
    )
    fig.update_layout(**PLOTLY_LAYOUT, height=400, xaxis_title="Release Date", yaxis_title="All-Time Streams")
    fig.update_traces(hovertemplate="%{hovertext}<br>Released %{x|%b %Y}<br>%{y:,.0f} streams<extra></extra>")
    st.plotly_chart(fig, use_container_width=True, key="catalog_timeline")

    # --- Remix groupings ---
    st.divider()
    st.markdown('<p class="section-header">Remix Groupings</p>', unsafe_allow_html=True)

    # Find songs that have remix variants
    base_songs = {}
    for _, row in songs.iterrows():
        name = row["song"]
        # Check if this is a remix variant
        for suffix in [" (Remix)", " (Club Mix)", " (Lofi Remix)", " (Acoustic)"]:
            if suffix in name:
                base = name.replace(suffix, "")
                if base not in base_songs:
                    base_songs[base] = []
                base_songs[base].append({"variant": name, "streams": row["streams"]})
                break

    # Add originals
    for base in list(base_songs.keys()):
        original = songs[songs["song"] == base]
        if not original.empty:
            base_songs[base].insert(0, {"variant": base + " (Original)", "streams": original.iloc[0]["streams"]})

    if base_songs:
        for base, variants in base_songs.items():
            with st.expander(f"🎶 {base} — {len(variants)} versions"):
                for v in sorted(variants, key=lambda x: x["streams"], reverse=True):
                    st.markdown(f"- **{v['variant']}** — {v['streams']:,} streams")
    else:
        st.info("No remix groupings found.")
