"""Catalog — Song library with metadata and rights info."""
from __future__ import annotations

import plotly.express as px
import pandas as pd
import streamlit as st

from theme import SPOTIFY_GREEN, ACCENT_BLUE, GOLD, MUTED, PLOTLY_LAYOUT, kpi_row, section, spacer


def render() -> None:
    from data_loader import load_songs_all, load_catalog, load_songstats_jakke

    songs = load_songs_all()
    catalog_raw = load_catalog()
    ss = load_songstats_jakke()

    st.markdown("""
    <div style="margin-bottom:28px">
        <h1 style="margin:0;font-size:1.8rem;font-weight:700;color:#f0f6fc">Catalog</h1>
        <p style="color:#8b949e;margin:4px 0 0 0;font-size:0.9rem">Complete song library with metadata, rights, and release history</p>
    </div>
    """, unsafe_allow_html=True)

    # Merge catalog recordings with streaming data
    recordings = catalog_raw[catalog_raw["Type"] == "Recording"].copy()
    recordings = recordings.rename(columns={"Title": "song", "Artist/Project": "artist_cat"})

    merged = songs.merge(recordings[["song", "Writers", "ISRC", "Dolby Atmos"]], on="song", how="left")
    merged["Writers"] = merged["Writers"].fillna("—")
    merged["ISRC"] = merged["ISRC"].fillna("—")
    merged["Dolby Atmos"] = merged["Dolby Atmos"].fillna("No")

    # Use artist column from songs CSV (already has correct Jakke/iLÜ)
    if "artist" not in merged.columns:
        merged["artist"] = "Jakke"

    # Add collaborators and popularity from songs CSV
    merged["collaborators"] = merged["collaborators"].fillna("—")
    merged["popularity"] = merged["popularity"].fillna(0).astype(int)

    # Mark currently playlisted
    playlisted = set(ss.get("currently_playlisted", []))
    merged["Playlisted"] = merged["song"].apply(lambda s: "Yes" if s in playlisted else "")

    # --- KPI cards ---
    atmos_count = len(merged[merged["Dolby Atmos"] == "Yes"])
    jakke_count = len(merged[merged["artist"] == "Jakke"])
    ilu_count = len(merged[merged["artist"] == "iLÜ"])
    playlisted_count = len(merged[merged["Playlisted"] == "Yes"])

    kpi_row([
        {"label": "Total Songs", "value": str(len(merged)), "accent": SPOTIFY_GREEN},
        {"label": "Jakke", "value": str(jakke_count), "sub": "Primary artist"},
        {"label": "iLÜ", "value": str(ilu_count), "sub": "Ambient project"},
        {"label": "Dolby Atmos", "value": str(atmos_count), "sub": "Spatial audio"},
        {"label": "Currently Playlisted", "value": str(playlisted_count), "accent": GOLD},
    ])

    spacer(24)

    # --- Artist filter ---
    artist_filter = st.selectbox("Filter by Artist", ["All", "Jakke", "iLÜ"], key="catalog_artist")
    if artist_filter != "All":
        merged = merged[merged["artist"] == artist_filter]

    # --- Song table ---
    display = merged[["song", "artist", "streams", "popularity", "collaborators", "release_date", "Playlisted", "Dolby Atmos"]].copy()
    display.columns = ["Song", "Artist", "Streams", "Popularity", "Collaborators", "Release Date", "Playlisted", "Atmos"]
    display = display.sort_values("Streams", ascending=False).reset_index(drop=True)
    display["Streams"] = display["Streams"].apply(lambda x: f"{x:,}")
    display["Release Date"] = display["Release Date"].dt.strftime("%Y-%m-%d").fillna("—")
    display["Popularity"] = display["Popularity"].apply(lambda x: f"{x}%" if x > 0 else "—")

    st.dataframe(display, use_container_width=True, hide_index=True, height=520)

    spacer(24)

    # --- Release timeline ---
    section("Release Timeline")
    timeline_data = merged.dropna(subset=["release_date"]).copy()
    fig = px.scatter(
        timeline_data, x="release_date", y="streams", size="streams",
        color="artist" if artist_filter == "All" else None,
        color_discrete_map={"Jakke": SPOTIFY_GREEN, "iLÜ": "#a78bfa"},
        hover_name="song", size_max=40,
    )
    fig.update_layout(**PLOTLY_LAYOUT, height=400, xaxis_title="", yaxis_title="All-Time Streams")
    fig.update_yaxes(tickformat=",")
    fig.update_traces(hovertemplate="%{hovertext}<br>Released %{x|%b %Y}<br><b>%{y:,.0f}</b> streams<extra></extra>")
    st.plotly_chart(fig, use_container_width=True, key="catalog_timeline")

    spacer(16)

    # --- Remix groupings ---
    section("Remix Groupings")
    suffixes = [" (Remix)", " (Club Mix)", " (Lofi Remix)", " (Acoustic)",
                " (TRØVES Remix)", " (Curt Reynolds Remix)", " (Jako Diaz Remix)",
                " (Jackets Remix)", " (Big Picture Mix)"]
    base_songs: dict[str, list] = {}
    for _, row in songs.iterrows():
        name = row["song"]
        for suffix in suffixes:
            if suffix in name:
                base = name.replace(suffix, "")
                if base not in base_songs:
                    base_songs[base] = []
                base_songs[base].append({"variant": name, "streams": row["streams"]})
                break

    for base in list(base_songs.keys()):
        original = songs[songs["song"] == base]
        if not original.empty:
            base_songs[base].insert(0, {"variant": base + " (Original)", "streams": original.iloc[0]["streams"]})

    if base_songs:
        for base, variants in base_songs.items():
            total = sum(v["streams"] for v in variants)
            with st.expander(f"{base} — {len(variants)} versions · {total:,} total streams"):
                for v in sorted(variants, key=lambda x: x["streams"], reverse=True):
                    st.markdown(f"**{v['variant']}** — {v['streams']:,} streams")
    else:
        st.caption("No remix groupings found.")
