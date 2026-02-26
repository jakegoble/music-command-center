"""Collaborators — Network visualization and collab impact."""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

from theme import (
    IG_PINK, SPOTIFY_GREEN, ACCENT_BLUE, GOLD, AMBER, MUTED,
    PLOTLY_CONFIG, apply_theme, kpi_row, section, spacer, avatar,
    render_page_title, collab_chip, collab_chips,
)

TIER_COLORS = {1: GOLD, 2: ACCENT_BLUE, 3: MUTED}
TIER_LABELS = {1: "High Impact", 2: "Regular", 3: "One-off"}


def render() -> None:
    from data_loader import load_ig_collaborators, load_music_collaborators

    collabs = load_ig_collaborators()
    music_collabs = load_music_collaborators()

    render_page_title("Collaborators", "Creative network — music collaborators and Instagram engagement", "#9B59B6")

    # ─── MUSIC COLLABORATORS ───
    section("Music Collaborators")

    total_collab_streams = music_collabs["total_streams"].sum()
    top_music = music_collabs.loc[music_collabs["total_streams"].idxmax()]
    unique_roles = music_collabs["role"].nunique()

    kpi_row([
        {"label": "Music Collaborators", "value": str(len(music_collabs)), "accent": SPOTIFY_GREEN},
        {"label": "Total Collab Streams", "value": f"{total_collab_streams:,.0f}", "accent": SPOTIFY_GREEN},
        {"label": "Top Collaborator", "value": top_music["collaborator"], "sub": f"{top_music['total_streams']:,.0f} streams across {top_music['tracks']} tracks", "accent": GOLD},
        {"label": "Unique Roles", "value": str(unique_roles), "sub": "Writer, Producer, Featured, Remix"},
    ])

    spacer(12)

    left, right = st.columns(2, gap="large")

    with left:
        section("Streams by Collaborator")
        mc_sorted = music_collabs.sort_values("total_streams")
        fig_mc = px.bar(
            mc_sorted, x="total_streams", y="collaborator", orientation="h",
            color_discrete_sequence=[SPOTIFY_GREEN],
        )
        apply_theme(fig_mc, height=max(340, len(mc_sorted) * 32), yaxis_title="", xaxis_title="Total Streams")
        fig_mc.update_xaxes(tickformat=",")
        fig_mc.update_traces(hovertemplate="%{y}<br><b>%{x:,.0f}</b> streams<extra></extra>")
        st.plotly_chart(fig_mc, use_container_width=True, key="music_collab_streams", config=PLOTLY_CONFIG)

    with right:
        section("Collaborators by Role")
        role_counts = music_collabs.groupby("role").agg(
            count=("collaborator", "count"),
            streams=("total_streams", "sum"),
        ).reset_index().sort_values("streams", ascending=False)

        role_colors = {
            "Writer/Producer": SPOTIFY_GREEN,
            "Featured": ACCENT_BLUE,
            "Remix": AMBER,
            "Remix/Featured": IG_PINK,
            "Label/Project": GOLD,
            "Co-Artist (iLÜ)": "#a78bfa",
            "Writer": MUTED,
        }
        colors = [role_colors.get(r, MUTED) for r in role_counts["role"]]

        fig_role = go.Figure()
        fig_role.add_trace(go.Bar(
            x=role_counts["streams"], y=role_counts["role"], orientation="h",
            marker_color=colors, text=role_counts["count"].apply(lambda x: f"{x} artist{'s' if x > 1 else ''}"),
            textposition="outside", textfont=dict(color="#8b949e", size=11),
            hovertemplate="%{y}<br><b>%{x:,.0f}</b> streams<extra></extra>",
        ))
        apply_theme(fig_role, height=280, yaxis_title="", xaxis_title="Total Streams")
        fig_role.update_xaxes(tickformat=",")
        st.plotly_chart(fig_role, use_container_width=True, key="music_collab_roles", config=PLOTLY_CONFIG)

    spacer(16)

    # Music collaborator table
    section("Music Collaborator Details")
    mc_display = music_collabs.sort_values("total_streams", ascending=False).copy()
    mc_display["total_streams"] = mc_display["total_streams"].apply(lambda x: f"{x:,}")
    mc_display["avg_streams"] = mc_display["avg_streams"].apply(lambda x: f"{x:,.0f}")
    mc_display.columns = ["Collaborator", "Tracks", "Role", "Total Streams", "Avg Streams/Track"]
    st.dataframe(mc_display, use_container_width=True, hide_index=True)

    spacer(12)

    # ─── INSTAGRAM COLLABORATORS ───
    section("Instagram Collaborators")

    top_collab = collabs.loc[collabs["avg_likes"].idxmax()]
    kpi_row([
        {"label": "IG Collaborators", "value": str(len(collabs)), "accent": IG_PINK},
        {"label": "Total Collab Posts", "value": str(int(collabs["collabs"].sum()))},
        {"label": "Avg Collab Likes", "value": f"{collabs['avg_likes'].mean():.0f}", "sub": "vs 121 solo avg"},
        {"label": "Top IG Collab", "value": f"@{top_collab['collaborator']}", "sub": f"Avg {top_collab['avg_likes']:,} likes", "accent": GOLD},
    ])

    spacer(12)

    left, right = st.columns(2, gap="large")

    with left:
        section("Solo vs Collab — Avg Engagement")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["Solo (396 posts)", "Collab (55 posts)"], y=[121, 261],
            marker_color=[MUTED, IG_PINK], text=["121", "261"],
            textposition="outside", textfont=dict(color="#f0f6fc", size=14),
            hovertemplate="%{x}<br>Avg <b>%{y}</b> likes/post<extra></extra>",
        ))
        fig.add_annotation(x=1, y=285, text="2.2x higher", showarrow=False, font=dict(color=SPOTIFY_GREEN, size=13))
        apply_theme(fig, height=340, yaxis_title="Avg Likes / Post")
        st.plotly_chart(fig, use_container_width=True, key="collab_solo_vs", config=PLOTLY_CONFIG)

    with right:
        section("Avg Likes by Collaborator")
        sorted_c = collabs.sort_values("avg_likes", ascending=True)
        colors = sorted_c["tier"].map(TIER_COLORS).tolist()
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=sorted_c["avg_likes"],
            y=sorted_c["collaborator"].apply(lambda x: f"@{x}"),
            orientation="h", marker_color=colors,
            hovertemplate="@%{y}<br>Avg <b>%{x:,}</b> likes<extra></extra>",
        ))
        apply_theme(fig3, height=max(340, len(collabs) * 28), yaxis_title="", xaxis_title="Avg Likes")
        for tier, label, color, xpos in [(1, "Tier 1", GOLD, 0.98), (2, "Tier 2", ACCENT_BLUE, 0.85), (3, "Tier 3", MUTED, 0.72)]:
            fig3.add_annotation(x=xpos, y=1.06, xref="paper", yref="paper", text=f"<b>{label}</b>",
                                font=dict(color=color, size=11), showarrow=False)
        st.plotly_chart(fig3, use_container_width=True, key="collab_tier_chart", config=PLOTLY_CONFIG)

    spacer(16)

    # --- Leaderboard ---
    section("IG Collaborator Leaderboard")
    display = collabs.copy()
    display["Tier"] = display["tier"].map(TIER_LABELS)
    display = display.sort_values("avg_likes", ascending=False)
    display_table = display[["collaborator", "collabs", "total_likes", "avg_likes", "Tier"]].copy()
    display_table.columns = ["Collaborator", "Posts", "Total Likes", "Avg Likes", "Tier"]
    display_table["Collaborator"] = display_table["Collaborator"].apply(lambda x: f"@{x}")
    st.dataframe(display_table, use_container_width=True, hide_index=True)

    spacer(16)

    # --- Deep dives ---
    section("Key Collaborator Deep Dives")

    with st.expander("@enjune.music — 16 posts · Avg 404 likes · Tier 1"):
        st.markdown(avatar("Enjune Music", 32) + ' <span style="font-weight:600;color:#f0f6fc;vertical-align:middle">Enjune Music</span>', unsafe_allow_html=True)
        st.markdown("""
Jake's music brand account. Cross-posts between personal and brand.

- **16 collab posts** over the music era (2022–2026)
- **Total engagement**: 6,471 likes
- **Average**: 404 likes/post (3.3x solo average)
- **Notable**: HOW DO YOU LOVE EP release hit **3,997 likes** (all-time #1)
- **Strategy**: Every major release should be co-posted with @enjune.music
        """)

    with st.expander("@timjck / @ontout — 3 posts · Avg 1,570 likes · Tier 1"):
        st.markdown(avatar("Tim JCK", 32) + ' <span style="font-weight:600;color:#f0f6fc;vertical-align:middle">Tim JCK / @ontout</span>', unsafe_allow_html=True)
        st.markdown("""
@ontout sessions = highest-impact collaboration by far.

- **3 collab posts** — small sample but wildly consistent
- **Average**: 1,570 likes/post (**13x solo average**)
- "CAN I PRAY on @ontout" — 3,234 likes
- "Your love never goes to waste @ontout" — 1,357 likes
- **Recommendation**: Schedule 2+ @ontout sessions per quarter
        """)

    with st.expander("@curtreynolds — 3 posts · Avg 132 likes · Tier 2"):
        st.markdown(avatar("Curt Reynolds", 32) + ' <span style="font-weight:600;color:#f0f6fc;vertical-align:middle">Curt Reynolds</span>', unsafe_allow_html=True)
        st.markdown("Consistent performer, slightly above solo average. Reliable but not a breakout multiplier.")

    spacer(12)

    # --- Recommendations ---
    section("Recommendations")
    st.markdown("""
1. **@timjck / @ontout** — 13x solo engagement. Highest-leverage collab available. Target 2+ sessions/quarter.
2. **@enjune.music** — Every release should be cross-posted. 3.3x solo average.
3. **Allen Blickle** — 6 tracks, 2.29M streams. Most prolific music collaborator. Continue the partnership.
4. **Nuage** — 2 tracks averaging 180K streams each. Strong fit for organic/chill releases.
5. **Increase collab ratio** — Currently 12% of IG posts. Aim for 25%+. Each collab gets 2.2x engagement.
    """)
