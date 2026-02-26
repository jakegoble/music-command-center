"""AI Insights — Strategic recommendations derived from data analysis."""
from __future__ import annotations

import streamlit as st

from theme import SPOTIFY_GREEN, IG_PINK, GOLD, MUTED, ACCENT_BLUE, kpi_row, section, spacer


def render() -> None:
    st.markdown("""
    <div style="margin-bottom:28px">
        <h1 style="margin:0;font-size:1.8rem;font-weight:700;color:#f0f6fc">AI Insights</h1>
        <p style="color:#8b949e;margin:4px 0 0 0;font-size:0.9rem">Strategic recommendations derived from cross-platform data analysis</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Key numbers to watch (top) ---
    kpi_row([
        {"label": "Solo Avg Likes", "value": "121", "delta": "-55% vs 2024", "accent": IG_PINK},
        {"label": "Collab Multiplier", "value": "2.2x", "sub": "Collab avg / Solo avg", "accent": SPOTIFY_GREEN},
        {"label": "@ontout Multiplier", "value": "13x", "sub": "1,570 avg vs 121 solo", "accent": GOLD},
        {"label": "Link Conversion", "value": "0.5%", "delta": "Needs 5-10%", "accent": IG_PINK},
    ])

    spacer(32)

    # ── What's Working ──
    section("What's Working")
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
<div style="background:#0d2818;border:1px solid #1a4a2e;border-radius:10px;padding:18px 20px;margin-bottom:12px">
<div style="font-weight:600;color:#3fb950;margin-bottom:8px">Video/Reels dominate engagement</div>
<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.6">
Reels average <b>202 likes/post</b> — 3.2x photos (64 avg). Drive 51.3% of interactions.
Every music release post that hit 500+ likes was a Reel.
</div></div>

<div style="background:#0d2818;border:1px solid #1a4a2e;border-radius:10px;padding:18px 20px">
<div style="font-weight:600;color:#3fb950;margin-bottom:8px">Collaborations are a cheat code</div>
<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.6">
Collab posts average <b>261 likes</b> (2.2x solo). @ontout sessions average <b>1,570 likes</b> (13x solo).
@enjune.music cross-posts average <b>404 likes</b> (3.3x solo).
</div></div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
<div style="background:#0d2818;border:1px solid #1a4a2e;border-radius:10px;padding:18px 20px;margin-bottom:12px">
<div style="font-weight:600;color:#3fb950;margin-bottom:8px">Music releases drive peak engagement</div>
<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.6">
Top 5 posts all-time are music release Reels. HOW DO YOU LOVE EP: 3,997 likes.
WAIT: 3,992 likes. HURRICANE: 3,694 likes.
</div></div>

<div style="background:#0d2818;border:1px solid #1a4a2e;border-radius:10px;padding:18px 20px">
<div style="font-weight:600;color:#3fb950;margin-bottom:8px">Optimal posting days identified</div>
<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.6">
<b>Thursday</b> (193 avg) and <b>Sunday</b> (187 avg) are clear winners.
Monday is weakest (64 avg). Weekend posting outperforms weekday.
</div></div>
        """, unsafe_allow_html=True)

    spacer(28)

    # ── Opportunities ──
    section("Opportunities")
    col3, col4 = st.columns(2, gap="large")

    with col3:
        st.markdown("""
<div style="background:#0d1d2d;border:1px solid #1a3a5c;border-radius:10px;padding:18px 20px;margin-bottom:12px">
<div style="font-weight:600;color:#58a6ff;margin-bottom:8px">Collab ratio is way too low</div>
<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.6">
Only <b>55 collab posts</b> out of 451 music-era posts (12%). Collabs get 2.2x engagement but
represent a tiny fraction. Increasing to 25%+ could lift overall engagement 15-20%.
</div></div>

<div style="background:#0d1d2d;border:1px solid #1a3a5c;border-radius:10px;padding:18px 20px">
<div style="font-weight:600;color:#58a6ff;margin-bottom:8px">@ontout is massively under-leveraged</div>
<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.6">
Only <b>3 posts</b> with @timjck despite averaging 1,570 likes each. This is a 13x multiplier
sitting on the shelf. Even 2 sessions/quarter = 8 high-engagement posts/year.
</div></div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
<div style="background:#0d1d2d;border:1px solid #1a3a5c;border-radius:10px;padding:18px 20px;margin-bottom:12px">
<div style="font-weight:600;color:#58a6ff;margin-bottom:8px">Karma Response is the hidden leader</div>
<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.6">
<b>36,024 streams</b> in the recent 3-year period (vs YLNW's 2,569 recent). This song has current
momentum but is under-promoted on IG. Cross-platform push could accelerate it.
</div></div>

<div style="background:#0d1d2d;border:1px solid #1a3a5c;border-radius:10px;padding:18px 20px">
<div style="font-weight:600;color:#58a6ff;margin-bottom:8px">Stories are 84.3% of views</div>
<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.6">
Massive reach channel (43,641 views in 30 days) but underutilized for music promotion.
Could be used for release teasers, behind-the-scenes, session clips.
</div></div>
        """, unsafe_allow_html=True)

    spacer(28)

    # ── Risks ──
    section("Risks")
    col5, col6 = st.columns(2, gap="large")

    with col5:
        st.markdown("""
<div style="background:#2d1b0e;border:1px solid #5c3a1a;border-radius:10px;padding:18px 20px;margin-bottom:12px">
<div style="font-weight:600;color:#f0883e;margin-bottom:8px">2025 engagement dropped 55%</div>
<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.6">
2024 avg: <b>216 likes/post</b> → 2025: <b>98 likes/post</b>. Volume went up (89 → 106 posts)
but quality/engagement ratio fell. Algorithm changes, audience fatigue, or content mix shift.
</div></div>

<div style="background:#2d1b0e;border:1px solid #5c3a1a;border-radius:10px;padding:18px 20px">
<div style="font-weight:600;color:#f0883e;margin-bottom:8px">Link-in-bio conversion is broken</div>
<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.6">
Only <b>5 external link taps</b> in 30 days despite 936 profile visits (0.5% conversion).
The funnel from IG → streaming/website is effectively non-functional.
</div></div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown("""
<div style="background:#2d1b0e;border:1px solid #5c3a1a;border-radius:10px;padding:18px 20px;margin-bottom:12px">
<div style="font-weight:600;color:#f0883e;margin-bottom:8px">YLNW streams are mostly legacy</div>
<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.6">
1.9M all-time but only <b>2,569</b> in the recent 3-year window. Current velocity may be near-zero
(playlist-driven tail). Don't over-index on total numbers — focus on recent momentum.
</div></div>

<div style="background:#2d1b0e;border:1px solid #5c3a1a;border-radius:10px;padding:18px 20px">
<div style="font-weight:600;color:#f0883e;margin-bottom:8px">Solo post engagement declining</div>
<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.6">
Solo posts average only <b>121 likes</b> (vs 261 for collabs). As the algorithm favors engagement,
lower-performing solo posts get less reach — negative feedback loop.
</div></div>
        """, unsafe_allow_html=True)

    spacer(32)

    # ── Action Items ──
    section("Action Items")

    actions = [
        {"p": "P0", "color": "#f85149", "action": "Schedule 2+ @ontout sessions per quarter", "effort": "Medium", "impact": "Very High", "rationale": "13x engagement multiplier. Highest-leverage activity available."},
        {"p": "P0", "color": "#f85149", "action": "Create release-day Reels for every new single", "effort": "Low", "impact": "High", "rationale": "Every 500+ like post is a music release Reel. This is the proven format."},
        {"p": "P1", "color": "#f0c040", "action": "Test Thursday/Sunday posting schedule", "effort": "Low", "impact": "Medium", "rationale": "2-3x engagement vs worst days. Easy scheduling change."},
        {"p": "P1", "color": "#f0c040", "action": "Fix link-in-bio conversion", "effort": "Low", "impact": "Medium", "rationale": "0.5% conversion from 936 monthly visits = wasted traffic. Try Linktree or custom landing."},
        {"p": "P1", "color": "#f0c040", "action": "Cross-promote Karma Response on IG", "effort": "Low", "impact": "Medium", "rationale": "Top recent streamer (36K in 3yr) but under-represented on Instagram."},
        {"p": "P2", "color": "#58a6ff", "action": "Increase collab ratio to 25%+", "effort": "Medium", "impact": "High", "rationale": "Currently 12% collab posts. Each collab gets 2.2x engagement."},
        {"p": "P2", "color": "#58a6ff", "action": "Use Stories for strategic music promotion", "effort": "Low", "impact": "Medium", "rationale": "84.3% of views. Add teasers, studio clips, countdowns."},
        {"p": "P3", "color": "#8b949e", "action": "Diagnose 2025 engagement drop", "effort": "Medium", "impact": "High", "rationale": "55% YoY drop needs investigation — content mix, posting time, format changes?"},
    ]

    for a in actions:
        with st.expander(f"[{a['p']}] {a['action']}"):
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**Priority:** <span style='color:{a['color']}'>{a['p']}</span>", unsafe_allow_html=True)
            c2.markdown(f"**Effort:** {a['effort']}")
            c3.markdown(f"**Impact:** {a['impact']}")
            st.markdown(f"{a['rationale']}")

    spacer(20)
    st.caption("These insights are generated from static data analysis. Connect live APIs (Spotify for Artists, IG Graph API) for real-time recommendations.")
