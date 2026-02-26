"""Collaborators — Network visualization and collab impact."""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

IG_PINK = "#E1306C"
SPOTIFY_GREEN = "#1DB954"
ACCENT_BLUE = "#58a6ff"
GOLD = "#f0c040"
MUTED = "#8b949e"
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#f0f6fc", family="system-ui, -apple-system, sans-serif"),
    margin=dict(l=0, r=0, t=40, b=0),
    hoverlabel=dict(bgcolor="#21262d", font_color="#f0f6fc"),
)

TIER_COLORS = {1: GOLD, 2: ACCENT_BLUE, 3: MUTED}
TIER_LABELS = {1: "High Impact", 2: "Regular", 3: "One-off"}


def render() -> None:
    from data_loader import load_ig_collaborators

    collabs = load_ig_collaborators()

    st.markdown("# 🤝 Collaborators")
    st.caption("Creative network analysis and collab performance")

    # --- KPI row ---
    total_collabs = len(collabs)
    total_collab_posts = collabs["collabs"].sum()
    avg_collab_likes = collabs["avg_likes"].mean()
    top_collab = collabs.loc[collabs["avg_likes"].idxmax()]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Collaborators", f"{total_collabs}")
    c2.metric("Total Collab Posts", f"{total_collab_posts}")
    c3.metric("Avg Collab Likes", f"{avg_collab_likes:.0f}")
    c4.metric("Top Collab", f"@{top_collab['collaborator']}", help=f"Avg {top_collab['avg_likes']:,} likes")

    st.divider()

    # --- Solo vs Collab ---
    left, right = st.columns(2)

    with left:
        st.markdown('<p class="section-header">Solo vs Collab Performance</p>', unsafe_allow_html=True)
        comparison = pd.DataFrame([
            {"Type": "Solo Posts", "Count": 396, "Avg Likes": 121},
            {"Type": "Collab Posts", "Count": 55, "Avg Likes": 261},
        ])
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["Solo", "Collab"],
            y=[121, 261],
            marker_color=[MUTED, IG_PINK],
            text=[121, 261],
            textposition="outside",
            textfont_color="#f0f6fc",
            hovertemplate="%{x}<br>Avg %{y} likes/post<extra></extra>",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=350, yaxis_title="Avg Likes / Post")
        # Add annotation
        fig.add_annotation(
            x="Collab", y=280,
            text="2.2x more engagement",
            showarrow=False,
            font=dict(color=SPOTIFY_GREEN, size=14, family="system-ui"),
        )
        st.plotly_chart(fig, use_container_width=True, key="collab_solo_vs")

    with right:
        st.markdown('<p class="section-header">Post Volume</p>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=["Solo", "Collab"],
            y=[396, 55],
            marker_color=[MUTED, IG_PINK],
            text=[396, 55],
            textposition="outside",
            textfont_color="#f0f6fc",
            hovertemplate="%{x}<br>%{y} posts<extra></extra>",
        ))
        fig2.update_layout(**PLOTLY_LAYOUT, height=350, yaxis_title="Number of Posts")
        fig2.add_annotation(
            x="Collab", y=75,
            text="Only 12% of posts — big opportunity",
            showarrow=False,
            font=dict(color=GOLD, size=13, family="system-ui"),
        )
        st.plotly_chart(fig2, use_container_width=True, key="collab_volume")

    st.divider()

    # --- Collab Leaderboard ---
    st.markdown('<p class="section-header">Collaborator Leaderboard</p>', unsafe_allow_html=True)

    display = collabs.copy()
    display["Tier"] = display["tier"].map(TIER_LABELS)
    display = display.sort_values("avg_likes", ascending=False)
    display_table = display[["collaborator", "collabs", "total_likes", "avg_likes", "Tier"]].copy()
    display_table.columns = ["Collaborator", "Posts", "Total Likes", "Avg Likes", "Tier"]
    display_table["Collaborator"] = display_table["Collaborator"].apply(lambda x: f"@{x}")

    st.dataframe(display_table, use_container_width=True, hide_index=True)

    st.divider()

    # --- Tier breakdown chart ---
    st.markdown('<p class="section-header">Avg Likes by Collaborator</p>', unsafe_allow_html=True)
    sorted_c = collabs.sort_values("avg_likes", ascending=True)
    colors = sorted_c["tier"].map(TIER_COLORS).tolist()

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=sorted_c["avg_likes"],
        y=sorted_c["collaborator"].apply(lambda x: f"@{x}"),
        orientation="h",
        marker_color=colors,
        hovertemplate="@%{y}<br>Avg %{x:,} likes<extra></extra>",
    ))
    fig3.update_layout(**PLOTLY_LAYOUT, height=max(350, len(collabs) * 30), yaxis_title="", xaxis_title="Avg Likes / Collab Post")

    # Tier legend annotations
    fig3.add_annotation(x=0.98, y=1.05, xref="paper", yref="paper", text="<b>Tier 1</b>", font=dict(color=GOLD, size=12), showarrow=False)
    fig3.add_annotation(x=0.85, y=1.05, xref="paper", yref="paper", text="<b>Tier 2</b>", font=dict(color=ACCENT_BLUE, size=12), showarrow=False)
    fig3.add_annotation(x=0.72, y=1.05, xref="paper", yref="paper", text="<b>Tier 3</b>", font=dict(color=MUTED, size=12), showarrow=False)

    st.plotly_chart(fig3, use_container_width=True, key="collab_tier_chart")

    st.divider()

    # --- Key collab deep dives ---
    st.markdown('<p class="section-header">Key Collaborator Deep Dives</p>', unsafe_allow_html=True)

    with st.expander("🎵 @enjune.music — 16 posts, Avg 404 likes (Tier 1)"):
        st.markdown("""
**Enjune Music** is Jake's music brand account. Collabs with @enjune.music are essentially cross-posts
between Jake's personal brand and the music project brand.

- **16 collab posts** over the music era (2022–2026)
- **Total engagement**: 6,471 likes
- **Average**: 404 likes/post (3.3x solo average)
- **Notable**: HOW DO YOU LOVE EP release collab post hit **3,997 likes** (all-time #1)
- **Strategy**: Every major release should be co-posted with @enjune.music
        """)

    with st.expander("🔥 @timjck / @ontout — 3 posts, Avg 1,570 likes (Tier 1)"):
        st.markdown("""
**Tim JCK** (through the @ontout sessions) represents Jake's highest-impact collaboration by far.

- **3 collab posts** (small sample, but consistent)
- **Average**: 1,570 likes/post (**13x solo average!**)
- **Posts**:
  - "CAN I PRAY on @ontout" — 3,234 likes
  - "Your love never goes to waste @ontout" — 1,357 likes
  - Third session — additional engagement
- **Key insight**: @ontout's audience overlap creates massive amplification
- **Recommendation**: Schedule 2+ @ontout sessions per quarter
        """)

    with st.expander("💡 @curtreynolds — 3 posts, Avg 132 likes (Tier 2)"):
        st.markdown("""
- **3 collab posts**, steady performance
- **Average**: 132 likes/post (slightly above solo average)
- Consistent but not a breakout collaborator
        """)

    st.divider()

    # --- Recommendations ---
    st.markdown('<p class="section-header">Collaboration Recommendations</p>', unsafe_allow_html=True)
    st.info("""
**Who should Jake collaborate with more?**

1. **@timjck / @ontout** — 13x solo engagement. This is the highest-leverage collab by far. Target 2+ sessions/quarter.
2. **@enjune.music** — Every release should be cross-posted. 3.3x solo average.
3. **@360realityaudio** — Only 1 post but 208 avg likes. Dolby Atmos angle could unlock a tech/audio audience.
4. **New Tier 1 targets** — Look for artists with 50K-200K followers in the indie/electronic space. @ontout's success pattern (live session format + cross-audience) is the model to replicate.
5. **Reduce solo posting** — Only 12% of posts are collabs, but they drive 2.2x engagement. Aim for 25%+ collab ratio.
    """)
