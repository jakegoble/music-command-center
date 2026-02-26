"""Catalog Manager — Full catalog with metadata, cross-platform links, and rights info."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from theme import (
    SPOTIFY_GREEN, ACCENT_BLUE, GOLD, AMBER, MUTED, IG_PINK,
    PLOTLY_LAYOUT, kpi_row, section, spacer,
)


def render() -> None:
    from data_loader import load_songs_all, load_catalog, load_songstats_jakke, load_songstats_enjune
    from services.revenue_estimator import estimate_revenue, RATES

    songs = load_songs_all()
    catalog_raw = load_catalog()
    ss = load_songstats_jakke()
    enjune = load_songstats_enjune()

    st.markdown("""
    <div style="margin-bottom:28px">
        <h1 style="margin:0;font-size:1.8rem;font-weight:700;color:#f0f6fc">Catalog Manager</h1>
        <p style="color:#8b949e;margin:4px 0 0 0;font-size:0.9rem">Master catalog — metadata, rights, streaming data, and revenue estimates</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Build unified catalog ---
    recordings = catalog_raw[catalog_raw["Type"] == "Recording"].copy()
    recordings = recordings.rename(columns={"Title": "song", "Artist/Project": "project"})

    # Merge catalog metadata with streaming data
    unified = songs.merge(
        recordings[["song", "project", "Writers", "ISRC", "ISWC", "Dolby Atmos"]],
        on="song", how="left",
    )
    unified["Writers"] = unified["Writers"].fillna("—")
    unified["ISRC"] = unified["ISRC"].fillna("—")
    unified["ISWC"] = unified["ISWC"].fillna("—")
    unified["Dolby Atmos"] = unified["Dolby Atmos"].fillna("No")
    unified["project"] = unified["project"].fillna(unified["artist"])

    # Add revenue estimates per track
    unified["est_revenue"] = unified["streams"].apply(
        lambda s: estimate_revenue(int(s / 0.60)).estimated_revenue if s > 0 else 0
    )

    # Add Songstats popularity
    track_pop = ss.get("track_popularity", {})
    enjune_pop = enjune.get("track_popularity", {})
    all_pop = {**enjune_pop, **track_pop}
    unified["ss_popularity"] = unified["song"].map(all_pop).fillna(0).astype(int)

    # --- KPIs ---
    total_revenue = unified["est_revenue"].sum()
    atmos_count = len(unified[unified["Dolby Atmos"] == "Yes"])
    has_isrc = len(unified[unified["ISRC"] != "—"])
    missing_isrc = len(unified) - has_isrc
    playlisted = ss.get("currently_playlisted", [])

    kpi_row([
        {"label": "Total Catalog", "value": str(len(unified)), "sub": f"Jakke: {len(unified[unified['artist'] == 'Jakke'])} · iLÜ: {len(unified[unified['artist'] == 'iLÜ'])}", "accent": SPOTIFY_GREEN},
        {"label": "Est. Total Revenue", "value": f"${total_revenue:,.0f}", "sub": f"Blended rate ~${total_revenue / unified['streams'].sum():.4f}/stream" if unified["streams"].sum() > 0 else "", "accent": GOLD},
        {"label": "Dolby Atmos", "value": str(atmos_count), "sub": f"{atmos_count}/{len(unified)} tracks"},
        {"label": "ISRC Coverage", "value": f"{has_isrc}/{len(unified)}", "sub": f"{missing_isrc} missing" if missing_isrc > 0 else "Complete", "accent": SPOTIFY_GREEN if missing_isrc == 0 else AMBER},
    ])

    spacer(20)

    # --- Filters ---
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        artist_filter = st.selectbox("Artist", ["All", "Jakke", "iLÜ"], key="cm_artist")
    with col_f2:
        atmos_filter = st.selectbox("Dolby Atmos", ["All", "Yes", "No"], key="cm_atmos")
    with col_f3:
        sort_by = st.selectbox("Sort by", ["Streams (High→Low)", "Revenue (High→Low)", "Popularity", "Release Date", "Song Name"], key="cm_sort")

    filtered = unified.copy()
    if artist_filter != "All":
        filtered = filtered[filtered["artist"] == artist_filter]
    if atmos_filter != "All":
        filtered = filtered[filtered["Dolby Atmos"] == atmos_filter]

    sort_map = {
        "Streams (High→Low)": ("streams", False),
        "Revenue (High→Low)": ("est_revenue", False),
        "Popularity": ("ss_popularity", False),
        "Release Date": ("release_date", False),
        "Song Name": ("song", True),
    }
    sort_col, sort_asc = sort_map[sort_by]
    filtered = filtered.sort_values(sort_col, ascending=sort_asc, na_position="last")

    spacer(12)

    # --- Master table ---
    section("Full Catalog")
    display = filtered[[
        "song", "artist", "streams", "ss_popularity", "est_revenue",
        "Writers", "ISRC", "Dolby Atmos", "release_date", "collaborators",
    ]].copy()
    display["release_date"] = display["release_date"].dt.strftime("%Y-%m-%d").fillna("—")
    display["streams"] = display["streams"].apply(lambda x: f"{x:,}")
    display["est_revenue"] = display["est_revenue"].apply(lambda x: f"${x:,.2f}")
    display["ss_popularity"] = display["ss_popularity"].apply(lambda x: str(x) if x > 0 else "—")
    display["collaborators"] = display["collaborators"].fillna("—")
    display.columns = [
        "Song", "Artist", "Streams", "Popularity", "Est. Revenue",
        "Writers", "ISRC", "Atmos", "Released", "Collaborators",
    ]
    st.dataframe(display, use_container_width=True, hide_index=True, height=520)

    spacer(28)

    # --- Revenue breakdown ---
    left, right = st.columns(2, gap="large")

    with left:
        section("Revenue by Track (Top 15)")
        top_rev = filtered.nlargest(15, "est_revenue").sort_values("est_revenue")
        fig_rev = px.bar(
            top_rev, x="est_revenue", y="song", orientation="h",
            color_discrete_sequence=[GOLD],
        )
        fig_rev.update_layout(**PLOTLY_LAYOUT, height=480, yaxis_title="", xaxis_title="Estimated Revenue ($)")
        fig_rev.update_xaxes(tickprefix="$", tickformat=",")
        fig_rev.update_traces(hovertemplate="%{y}<br><b>$%{x:,.2f}</b><extra></extra>")
        st.plotly_chart(fig_rev, use_container_width=True, key="cm_revenue_track")

    with right:
        section("Revenue by Platform (Estimated Split)")
        from services.revenue_estimator import PLATFORM_SPLIT
        total_streams = unified["streams"].sum()
        platform_data = []
        for platform, share in PLATFORM_SPLIT.items():
            streams = int(total_streams * share)
            rate = RATES.get(platform, RATES["Other"])
            revenue = streams * rate
            platform_data.append({"Platform": platform, "Revenue": revenue, "Streams": streams})

        platform_df = pd.DataFrame(platform_data).sort_values("Revenue", ascending=False)
        colors = {
            "Spotify": SPOTIFY_GREEN, "Apple Music": "#fc3c44", "YouTube Music": "#ff0000",
            "Amazon Music": "#00a8e1", "Deezer": "#a238ff", "Tidal": "#000000", "Other": MUTED,
        }
        fig_plat = px.pie(
            platform_df, values="Revenue", names="Platform",
            color="Platform", color_discrete_map=colors, hole=0.45,
        )
        fig_plat.update_layout(**PLOTLY_LAYOUT, height=480, showlegend=True, legend=dict(orientation="h", y=-0.05))
        fig_plat.update_traces(textinfo="label+percent", textfont_color="#f0f6fc",
                               hovertemplate="%{label}<br><b>$%{value:,.0f}</b><br>%{percent}<extra></extra>")
        st.plotly_chart(fig_plat, use_container_width=True, key="cm_revenue_platform")

    spacer(28)

    # --- Catalog health ---
    section("Catalog Health")
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown("""
<div style="background:#161b22;border:1px solid #21262d;border-radius:10px;padding:18px 20px">
<div style="font-size:0.78rem;color:#8b949e;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px">Missing ISRCs</div>
""", unsafe_allow_html=True)
        missing = unified[unified["ISRC"] == "—"][["song", "artist"]].copy()
        if not missing.empty:
            for _, row in missing.iterrows():
                st.markdown(f"- **{row['song']}** ({row['artist']})")
        else:
            st.markdown("All tracks have ISRCs")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
<div style="background:#161b22;border:1px solid #21262d;border-radius:10px;padding:18px 20px">
<div style="font-size:0.78rem;color:#8b949e;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px">Missing Release Dates</div>
""", unsafe_allow_html=True)
        no_date = unified[unified["release_date"].isna()][["song", "artist"]].copy()
        if not no_date.empty:
            for _, row in no_date.iterrows():
                st.markdown(f"- **{row['song']}** ({row['artist']})")
        else:
            st.markdown("All tracks have release dates")
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("""
<div style="background:#161b22;border:1px solid #21262d;border-radius:10px;padding:18px 20px">
<div style="font-size:0.78rem;color:#8b949e;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px">No Dolby Atmos</div>
""", unsafe_allow_html=True)
        no_atmos = unified[unified["Dolby Atmos"] != "Yes"][["song", "artist"]].copy()
        if not no_atmos.empty:
            for _, row in no_atmos.head(10).iterrows():
                st.markdown(f"- **{row['song']}** ({row['artist']})")
            if len(no_atmos) > 10:
                st.caption(f"...and {len(no_atmos) - 10} more")
        else:
            st.markdown("All tracks have Atmos mixes")
        st.markdown("</div>", unsafe_allow_html=True)

    spacer(28)

    # --- Track deep dives ---
    section("Track Deep Dives")
    selected_track = st.selectbox(
        "Select a track",
        unified.sort_values("streams", ascending=False)["song"].tolist(),
        key="cm_track_select",
    )

    if selected_track:
        track = unified[unified["song"] == selected_track].iloc[0]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Streams", f"{track['streams']:,}")
        c2.metric("Popularity", str(track["ss_popularity"]) if track["ss_popularity"] > 0 else "—")
        c3.metric("Est. Revenue", f"${track['est_revenue']:,.2f}")
        c4.metric("Artist", track["artist"])
        c5.metric("Atmos", track["Dolby Atmos"])

        spacer(12)
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
**Writers:** {track['Writers']}
**ISRC:** `{track['ISRC']}`
**ISWC:** `{track['ISWC']}`
**Released:** {track['release_date'].strftime('%B %d, %Y') if pd.notna(track['release_date']) else 'Unknown'}
**Collaborators:** {track['collaborators'] if pd.notna(track.get('collaborators')) else '—'}
            """)

        with col_b:
            is_playlisted = selected_track in playlisted
            status = f"<span style='color:{SPOTIFY_GREEN}'>Currently Playlisted</span>" if is_playlisted else "<span style='color:#8b949e'>Not Currently Playlisted</span>"
            st.markdown(f"**Playlist Status:** {status}", unsafe_allow_html=True)

            # Revenue breakdown for this track
            if track["streams"] > 0:
                rev = estimate_revenue(int(track["streams"] / 0.60))
                st.markdown("**Revenue by Platform (Est.):**")
                for plat, data in sorted(rev.platform_breakdown.items(), key=lambda x: x[1]["revenue"], reverse=True):
                    if data["revenue"] > 0.50:
                        st.markdown(f"- {plat}: ${data['revenue']:,.2f} ({data['streams']:,} streams)")

    spacer(20)

    # --- Currently playlisted indicator ---
    if playlisted:
        section("Currently Playlisted")
        st.markdown(f"""
<div style="background:#161b22;border:1px solid #21262d;border-radius:10px;padding:14px 18px">
    <span style="color:#1DB954;font-size:0.95rem;font-weight:500">{', '.join(playlisted)}</span>
    <span style="color:#484f58;font-size:0.78rem;margin-left:8px">on {ss['spotify']['current_playlists']} playlists · reach {ss['spotify']['playlist_reach']:,}</span>
</div>
        """, unsafe_allow_html=True)
