"""Collaborators — Network visualization and collab impact."""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from theme import (
    IG_PINK, SPOTIFY_GREEN, ACCENT_BLUE, GOLD, MUTED,
    PLOTLY_LAYOUT, kpi_row, section, spacer,
)

TIER_COLORS = {1: GOLD, 2: ACCENT_BLUE, 3: MUTED}
TIER_LABELS = {1: "High Impact", 2: "Regular", 3: "One-off"}


def render() -> None:
    from data_loader import load_ig_collaborators

    collabs = load_ig_collaborators()

    st.markdown("""
    <div style="margin-bottom:28px">
        <h1 style="margin:0;font-size:1.8rem;font-weight:700;color:#f0f6fc">Collaborators</h1>
        <p style="color:#8b949e;margin:4px 0 0 0;font-size:0.9rem">Creative network analysis and collaboration performance</p>
    </div>
    """, unsafe_allow_html=True)

    # --- KPIs ---
    top_collab = collabs.loc[collabs["avg_likes"].idxmax()]
    kpi_row([
        {"label": "Collaborators", "value": str(len(collabs))},
        {"label": "Total Collab Posts", "value": str(int(collabs["collabs"].sum()))},
        {"label": "Avg Collab Likes", "value": f"{collabs['avg_likes'].mean():.0f}", "sub": "vs 121 solo avg"},
        {"label": "Top Collab", "value": f"@{top_collab['collaborator']}", "sub": f"Avg {top_collab['avg_likes']:,} likes", "accent": GOLD},
    ])

    spacer(28)

    # --- Solo vs Collab ---
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
        fig.update_layout(**PLOTLY_LAYOUT, height=340, yaxis_title="Avg Likes / Post")
        st.plotly_chart(fig, use_container_width=True, key="collab_solo_vs")

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
        fig3.update_layout(**PLOTLY_LAYOUT, height=max(340, len(collabs) * 28), yaxis_title="", xaxis_title="Avg Likes")
        # Tier legend
        for tier, label, color, xpos in [(1, "Tier 1", GOLD, 0.98), (2, "Tier 2", ACCENT_BLUE, 0.85), (3, "Tier 3", MUTED, 0.72)]:
            fig3.add_annotation(x=xpos, y=1.06, xref="paper", yref="paper", text=f"<b>{label}</b>",
                                font=dict(color=color, size=11), showarrow=False)
        st.plotly_chart(fig3, use_container_width=True, key="collab_tier_chart")

    spacer(24)

    # --- Leaderboard ---
    section("Collaborator Leaderboard")
    display = collabs.copy()
    display["Tier"] = display["tier"].map(TIER_LABELS)
    display = display.sort_values("avg_likes", ascending=False)
    display_table = display[["collaborator", "collabs", "total_likes", "avg_likes", "Tier"]].copy()
    display_table.columns = ["Collaborator", "Posts", "Total Likes", "Avg Likes", "Tier"]
    display_table["Collaborator"] = display_table["Collaborator"].apply(lambda x: f"@{x}")
    st.dataframe(display_table, use_container_width=True, hide_index=True)

    spacer(24)

    # --- Deep dives ---
    section("Key Collaborator Deep Dives")

    with st.expander("@enjune.music — 16 posts · Avg 404 likes · Tier 1"):
        st.markdown("""
**Enjune Music** is Jake's music brand account. Cross-posts between personal and brand.

- **16 collab posts** over the music era (2022–2026)
- **Total engagement**: 6,471 likes
- **Average**: 404 likes/post (3.3x solo average)
- **Notable**: HOW DO YOU LOVE EP release hit **3,997 likes** (all-time #1)
- **Strategy**: Every major release should be co-posted with @enjune.music
        """)

    with st.expander("@timjck / @ontout — 3 posts · Avg 1,570 likes · Tier 1"):
        st.markdown("""
**Tim JCK** through @ontout sessions = highest-impact collaboration by far.

- **3 collab posts** — small sample but wildly consistent
- **Average**: 1,570 likes/post (**13x solo average**)
- "CAN I PRAY on @ontout" — 3,234 likes
- "Your love never goes to waste @ontout" — 1,357 likes
- **Recommendation**: Schedule 2+ @ontout sessions per quarter
        """)

    with st.expander("@curtreynolds — 3 posts · Avg 132 likes · Tier 2"):
        st.markdown("Consistent performer, slightly above solo average. Reliable but not a breakout multiplier.")

    spacer(20)

    # --- Recommendations ---
    section("Recommendations")
    st.markdown("""
1. **@timjck / @ontout** — 13x solo engagement. Highest-leverage collab available. Target 2+ sessions/quarter.
2. **@enjune.music** — Every release should be cross-posted. 3.3x solo average.
3. **@360realityaudio** — Only 1 post but 208 avg likes. Dolby Atmos angle could unlock a tech/audio audience.
4. **New Tier 1 targets** — Indie/electronic artists with 50K-200K followers. Replicate the @ontout live session format.
5. **Increase collab ratio** — Currently 12% of posts. Aim for 25%+. Each collab gets 2.2x engagement.
    """)
