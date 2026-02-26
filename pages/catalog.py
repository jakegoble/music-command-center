"""Catalog — Unified song library with metadata, revenue, and health."""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

from theme import (
    SPOTIFY_GREEN, ACCENT_BLUE, GOLD, AMBER, MUTED, IG_PINK,
    PLOTLY_LAYOUT, kpi_row, section, spacer, genre_pill,
    GENRE_COLORS, inject_page_accent, track_row,
)


def render() -> None:
    from data_loader import load_songs_all, load_catalog, load_songstats_jakke, load_songstats_enjune
    from services.revenue_estimator import estimate_revenue, RATES, PLATFORM_SPLIT, get_jake_split

    songs = load_songs_all()
    catalog_raw = load_catalog()
    ss = load_songstats_jakke()
    enjune = load_songstats_enjune()

    inject_page_accent("catalog")

    st.markdown("""
    <div style="margin-bottom:28px">
        <h1 style="margin:0;font-size:1.8rem;font-weight:700;color:#f0f6fc">Catalog</h1>
        <p style="color:#8b949e;margin:4px 0 0 0;font-size:0.9rem">Complete library — metadata, revenue estimates, rights, and release history</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Build unified catalog ---
    recordings = catalog_raw[catalog_raw["Type"] == "Recording"].copy()
    recordings = recordings.rename(columns={"Title": "song", "Artist/Project": "project"})

    unified = songs.merge(
        recordings[["song", "project", "Writers", "ISRC", "ISWC", "Dolby Atmos"]],
        on="song", how="left",
    )
    unified["Writers"] = unified["Writers"].fillna("—")
    unified["ISRC"] = unified["ISRC"].fillna("—")
    unified["ISWC"] = unified["ISWC"].fillna("—")
    unified["Dolby Atmos"] = unified["Dolby Atmos"].fillna("No")
    unified["project"] = unified["project"].fillna(unified["artist"])
    unified["collaborators"] = unified["collaborators"].fillna("—")

    # Revenue per track (Spotify streams → estimated cross-platform total)
    unified["est_revenue"] = unified["streams"].apply(
        lambda s: estimate_revenue(int(s / 0.60)).estimated_revenue if s > 0 else 0
    )

    # Splits
    unified["jake_split"] = unified["song"].apply(get_jake_split)
    unified["jake_revenue"] = unified["est_revenue"] * unified["jake_split"]

    # Songstats popularity
    track_pop = ss.get("track_popularity", {})
    enjune_pop = enjune.get("track_popularity", {})
    all_pop = {**enjune_pop, **track_pop}
    unified["ss_popularity"] = unified["song"].map(all_pop).fillna(0).astype(int)

    # Playlisted
    playlisted = set(ss.get("currently_playlisted", []))
    unified["Playlisted"] = unified["song"].apply(lambda s: "Yes" if s in playlisted else "")

    # --- KPIs ---
    total_revenue = unified["est_revenue"].sum()
    atmos_count = len(unified[unified["Dolby Atmos"] == "Yes"])
    has_isrc = len(unified[unified["ISRC"] != "—"])
    missing_isrc = len(unified) - has_isrc
    playlisted_count = len(unified[unified["Playlisted"] == "Yes"])

    kpi_row([
        {"label": "Total Songs", "value": str(len(unified)), "sub": f"Jakke: {len(unified[unified['artist'] == 'Jakke'])} · iLÜ: {len(unified[unified['artist'] == 'iLÜ'])}", "accent": SPOTIFY_GREEN},
        {"label": "Est. Revenue", "value": f"${total_revenue:,.0f}", "sub": f"Blended rate ~${total_revenue / unified['streams'].sum():.4f}/stream" if unified["streams"].sum() > 0 else "", "accent": GOLD},
        {"label": "ISRC Coverage", "value": f"{has_isrc}/{len(unified)}", "sub": f"{missing_isrc} missing" if missing_isrc > 0 else "Complete", "accent": SPOTIFY_GREEN if missing_isrc == 0 else AMBER},
        {"label": "Dolby Atmos", "value": str(atmos_count), "sub": f"{atmos_count}/{len(unified)} tracks"},
        {"label": "Playlisted", "value": str(playlisted_count), "accent": SPOTIFY_GREEN},
    ])

    spacer(8)

    # Genre summary
    genre_counts = unified["genre"].value_counts()
    genre_html = " ".join(
        f'{genre_pill(g)} <span style="color:#484f58;font-size:0.72rem;margin-right:8px">{c}</span>'
        for g, c in genre_counts.items() if g
    )
    if genre_html:
        st.markdown(f'<div style="margin-bottom:16px">{genre_html}</div>', unsafe_allow_html=True)

    tab_overview, tab_revenue, tab_health, tab_remixes, tab_timeline = st.tabs(
        ["Overview", "Revenue", "Health", "Remixes", "Timeline"]
    )

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1: Overview — Full table with filters
    # ══════════════════════════════════════════════════════════════════════════
    with tab_overview:
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            artist_filter = st.selectbox("Artist", ["All", "Jakke", "iLÜ"], key="cat_artist")
        with col_f2:
            atmos_filter = st.selectbox("Dolby Atmos", ["All", "Yes", "No"], key="cat_atmos")
        with col_f3:
            sort_by = st.selectbox("Sort by", ["Streams (High→Low)", "Revenue (High→Low)", "Popularity", "Release Date", "Song Name"], key="cat_sort")

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

        spacer(8)
        display = filtered[[
            "song", "artist", "genre", "streams", "ss_popularity", "est_revenue",
            "jake_split", "jake_revenue",
            "Writers", "ISRC", "Dolby Atmos", "release_date", "collaborators",
        ]].copy()
        display["release_date"] = display["release_date"].dt.strftime("%Y-%m-%d").fillna("—")
        display["streams"] = display["streams"].apply(lambda x: f"{x:,}")
        display["est_revenue"] = display["est_revenue"].apply(lambda x: f"${x:,.2f}")
        display["jake_split"] = display["jake_split"].apply(lambda x: f"{x:.0%}")
        display["jake_revenue"] = display["jake_revenue"].apply(lambda x: f"${x:,.2f}")
        display["ss_popularity"] = display["ss_popularity"].apply(lambda x: str(x) if x > 0 else "—")
        display["genre"] = display["genre"].fillna("—")
        display["collaborators"] = display["collaborators"].fillna("—")
        display.columns = [
            "Song", "Artist", "Genre", "Streams", "Popularity", "Est. Revenue",
            "Jake's %", "Jake's Rev",
            "Writers", "ISRC", "Atmos", "Released", "Collaborators",
        ]
        st.dataframe(display, use_container_width=True, hide_index=True, height=520)

        spacer(20)

        # Track list with artwork placeholders (D9)
        section("Track Details")

        # Visual track list — top 10
        top_tracks = unified.nlargest(10, "streams")
        for _, t in top_tracks.iterrows():
            is_pl = t["song"] in playlisted
            st.markdown(
                track_row(
                    t["song"], t["artist"], f"{t['streams']:,}",
                    genre=t.get("genre", ""), playlisted=is_pl,
                ),
                unsafe_allow_html=True,
            )

        spacer(12)
        selected_track = st.selectbox(
            "Select a track for detail",
            unified.sort_values("streams", ascending=False)["song"].tolist(),
            key="cat_track_select",
        )

        if selected_track:
            track = unified[unified["song"] == selected_track].iloc[0]
            track_genre = track.get("genre", "")

            # Track header with artwork placeholder
            st.markdown(
                track_row(
                    track["song"], track["artist"], f"{track['streams']:,}",
                    genre=track_genre, playlisted=selected_track in playlisted,
                ),
                unsafe_allow_html=True,
            )
            spacer(8)
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("Streams", f"{track['streams']:,}")
            c2.metric("Popularity", str(track["ss_popularity"]) if track["ss_popularity"] > 0 else "—")
            c3.metric("Est. Revenue", f"${track['est_revenue']:,.2f}")
            c4.metric("Jake's Share", f"${track['jake_revenue']:,.2f}")
            c5.metric("Split", f"{track['jake_split']:.0%}")
            c6.metric("Atmos", track["Dolby Atmos"])

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
                status_color = SPOTIFY_GREEN if is_playlisted else "#8b949e"
                status_text = "Currently Playlisted" if is_playlisted else "Not Currently Playlisted"
                st.markdown(f"**Playlist Status:** <span style='color:{status_color}'>{status_text}</span>", unsafe_allow_html=True)

                if track["streams"] > 0:
                    rev = estimate_revenue(int(track["streams"] / 0.60))
                    st.markdown("**Revenue by Platform (Est.):**")
                    for plat, data in sorted(rev.platform_breakdown.items(), key=lambda x: x[1]["revenue"], reverse=True):
                        if data["revenue"] > 0.50:
                            st.markdown(f"- {plat}: ${data['revenue']:,.2f} ({data['streams']:,} streams)")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2: Revenue — Charts and breakdowns
    # ══════════════════════════════════════════════════════════════════════════
    with tab_revenue:
        left, right = st.columns(2, gap="large")

        with left:
            section("Revenue by Track (Top 15)")
            top_rev = unified.nlargest(15, "est_revenue").sort_values("est_revenue")
            fig_rev = px.bar(
                top_rev, x="est_revenue", y="song", orientation="h",
                color_discrete_sequence=[GOLD],
            )
            fig_rev.update_layout(**PLOTLY_LAYOUT, height=480, yaxis_title="", xaxis_title="Estimated Revenue ($)")
            fig_rev.update_xaxes(tickprefix="$", tickformat=",")
            fig_rev.update_traces(hovertemplate="%{y}<br><b>$%{x:,.2f}</b><extra></extra>")
            st.plotly_chart(fig_rev, use_container_width=True, key="cat_revenue_track")

        with right:
            section("Revenue by Platform (Estimated Split)")
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
            fig_plat.update_layout(**PLOTLY_LAYOUT, height=480, showlegend=True,
                                   uniformtext_minsize=10, uniformtext_mode="hide",
                                   legend=dict(orientation="h", y=-0.05))
            fig_plat.update_traces(textinfo="label+percent", textfont_color="#f0f6fc",
                                   textposition="auto", insidetextorientation="radial",
                                   hovertemplate="%{label}<br><b>$%{value:,.0f}</b><br>%{percent}<extra></extra>")
            st.plotly_chart(fig_plat, use_container_width=True, key="cat_revenue_platform")

        spacer(16)
        st.caption("Revenue estimates use industry-average per-stream rates across platforms. Actual payouts vary by territory, subscription type, and distributor terms.")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3: Health — Missing metadata
    # ══════════════════════════════════════════════════════════════════════════
    with tab_health:
        col1, col2, col3 = st.columns(3, gap="large")

        with col1:
            missing = unified[unified["ISRC"] == "—"][["song", "artist"]].copy()
            items = "".join(f"<div style='color:#c9d1d9;font-size:0.85rem;padding:2px 0'>• <b>{r['song']}</b> ({r['artist']})</div>" for _, r in missing.iterrows()) if not missing.empty else "<div style='color:#3fb950;font-size:0.85rem'>All tracks have ISRCs</div>"
            st.markdown(f"""
<div style="background:#161b22;border:1px solid #21262d;border-radius:10px;padding:18px 20px">
<div style="font-size:0.78rem;color:#8b949e;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px">Missing ISRCs</div>
{items}
</div>""", unsafe_allow_html=True)

        with col2:
            no_date = unified[unified["release_date"].isna()][["song", "artist"]].copy()
            items = "".join(f"<div style='color:#c9d1d9;font-size:0.85rem;padding:2px 0'>• <b>{r['song']}</b> ({r['artist']})</div>" for _, r in no_date.iterrows()) if not no_date.empty else "<div style='color:#3fb950;font-size:0.85rem'>All tracks have release dates</div>"
            st.markdown(f"""
<div style="background:#161b22;border:1px solid #21262d;border-radius:10px;padding:18px 20px">
<div style="font-size:0.78rem;color:#8b949e;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px">Missing Release Dates</div>
{items}
</div>""", unsafe_allow_html=True)

        with col3:
            no_atmos = unified[unified["Dolby Atmos"] != "Yes"][["song", "artist"]].copy()
            rows = no_atmos.head(10)
            items = "".join(f"<div style='color:#c9d1d9;font-size:0.85rem;padding:2px 0'>• <b>{r['song']}</b> ({r['artist']})</div>" for _, r in rows.iterrows()) if not no_atmos.empty else "<div style='color:#3fb950;font-size:0.85rem'>All tracks have Atmos mixes</div>"
            extra = f"<div style='color:#484f58;font-size:0.78rem;margin-top:4px'>...and {len(no_atmos) - 10} more</div>" if len(no_atmos) > 10 else ""
            st.markdown(f"""
<div style="background:#161b22;border:1px solid #21262d;border-radius:10px;padding:18px 20px">
<div style="font-size:0.78rem;color:#8b949e;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px">No Dolby Atmos</div>
{items}{extra}
</div>""", unsafe_allow_html=True)

        spacer(20)

        # Currently playlisted indicator
        playlisted_list = ss.get("currently_playlisted", [])
        if playlisted_list:
            section("Currently Playlisted")
            st.markdown(f"""
<div style="background:#161b22;border:1px solid #21262d;border-radius:10px;padding:14px 18px">
    <span style="color:#1DB954;font-size:0.95rem;font-weight:500">{', '.join(playlisted_list)}</span>
    <span style="color:#484f58;font-size:0.78rem;margin-left:8px">on {ss['spotify']['current_playlists']} playlists · reach {ss['spotify']['playlist_reach']:,}</span>
</div>
            """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4: Remixes — Grouped variants
    # ══════════════════════════════════════════════════════════════════════════
    with tab_remixes:
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

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 5: Timeline — Release bubble chart
    # ══════════════════════════════════════════════════════════════════════════
    with tab_timeline:
        section("Release Timeline")
        timeline_data = unified.dropna(subset=["release_date"]).copy()
        fig = px.scatter(
            timeline_data, x="release_date", y="streams", size="streams",
            color="artist",
            color_discrete_map={"Jakke": SPOTIFY_GREEN, "iLÜ": "#a78bfa"},
            hover_name="song", size_max=40,
        )
        fig.update_layout(**PLOTLY_LAYOUT, height=400, xaxis_title="", yaxis_title="All-Time Streams")
        fig.update_yaxes(tickformat=",")
        fig.update_traces(hovertemplate="%{hovertext}<br>Released %{x|%b %Y}<br><b>%{y:,.0f}</b> streams<extra></extra>")
        st.plotly_chart(fig, use_container_width=True, key="cat_timeline")
