"""AI Insights — Strategic recommendations derived from data analysis."""
from __future__ import annotations

import streamlit as st

from theme import SPOTIFY_GREEN, IG_PINK, GOLD, MUTED, ACCENT_BLUE, AMBER, kpi_row, section, spacer


def render() -> None:
    from data_loader import load_songstats_jakke, load_songstats_enjune, load_songs_all

    ss = load_songstats_jakke()
    enjune = load_songstats_enjune()
    songs = load_songs_all()

    # Compute key metrics
    top_song = songs.loc[songs["streams"].idxmax()]
    combined_streams = ss["cross_platform"]["total_streams"] + enjune["spotify"]["total_streams"]

    st.markdown("""
    <div style="margin-bottom:28px">
        <h1 style="margin:0;font-size:1.8rem;font-weight:700;color:#f0f6fc">AI Insights</h1>
        <p style="color:#8b949e;margin:4px 0 0 0;font-size:0.9rem">Strategic recommendations derived from cross-platform data analysis</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Key numbers to watch (top) ---
    kpi_row([
        {"label": "Cross-Platform Streams", "value": f"{ss['cross_platform']['total_streams']:,.0f}", "sub": f"+ {enjune['spotify']['total_streams']:,.0f} Enjune", "accent": SPOTIFY_GREEN},
        {"label": "Collab Multiplier", "value": "2.2x", "sub": "Collab avg / Solo avg", "accent": IG_PINK},
        {"label": "@ontout Multiplier", "value": "13x", "sub": "1,570 avg vs 121 solo", "accent": GOLD},
        {"label": "Playlist Reach", "value": f"{ss['cross_platform']['playlist_reach']:,.0f}", "sub": f"{ss['spotify']['current_playlists']} playlists", "accent": SPOTIFY_GREEN},
    ])

    spacer(32)

    # ── What's Working ──
    section("What's Working")
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(f"""
<div style="background:#0d2818;border:1px solid #1a4a2e;border-radius:10px;padding:18px 20px;margin-bottom:12px">
<div style="font-weight:600;color:#3fb950;margin-bottom:8px">Your Love's Not Wasted is a breakout hit</div>
<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.6">
<b>{top_song['streams']:,.0f} all-time streams</b> — more than 5x the next closest song.
Popularity score of {ss['track_popularity'].get("Your Love's Not Wasted", 'N/A')}/100.
Driving the majority of catalog discovery.
</div></div>

<div style="background:#0d2818;border:1px solid #1a4a2e;border-radius:10px;padding:18px 20px">
<div style="font-weight:600;color:#3fb950;margin-bottom:8px">Currently playlisted songs have momentum</div>
<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.6">
<b>{', '.join(ss['currently_playlisted'])}</b> are on active playlists right now.
Combined playlist reach of <b>{ss['spotify']['playlist_reach']:,.0f}</b> listeners.
These songs are being pushed by the algorithm — lean into them.
</div></div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
<div style="background:#0d2818;border:1px solid #1a4a2e;border-radius:10px;padding:18px 20px;margin-bottom:12px">
<div style="font-weight:600;color:#3fb950;margin-bottom:8px">Video/Reels dominate IG engagement</div>
<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.6">
Reels average <b>202 likes/post</b> — 3.2x photos (64 avg). Drive 51.3% of interactions.
Every music release post that hit 500+ likes was a Reel.
</div></div>

<div style="background:#0d2818;border:1px solid #1a4a2e;border-radius:10px;padding:18px 20px">
<div style="font-weight:600;color:#3fb950;margin-bottom:8px">Collaborations are a cheat code</div>
<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.6">
Collab posts average <b>261 likes</b> (2.2x solo). @ontout sessions average <b>1,570 likes</b> (13x solo).
Allen Blickle: <b>6 tracks, 2.29M streams</b>. Most prolific music partner.
</div></div>
        """, unsafe_allow_html=True)

    spacer(28)

    # ── Opportunities ──
    section("Opportunities")
    col3, col4 = st.columns(2, gap="large")

    with col3:
        st.markdown(f"""
<div style="background:#0d1d2d;border:1px solid #1a3a5c;border-radius:10px;padding:18px 20px;margin-bottom:12px">
<div style="font-weight:600;color:#58a6ff;margin-bottom:8px">Enjune catalog is underleveraged</div>
<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.6">
<b>{enjune['spotify']['total_streams']:,.0f} streams</b> across {len(enjune['catalog'])} tracks. Lost In The Woods
alone has popularity 34. Cross-promote Enjune catalog to Jakke's {ss['spotify']['monthly_listeners']:,}
monthly listeners for quick streaming gains.
</div></div>

<div style="background:#0d1d2d;border:1px solid #1a3a5c;border-radius:10px;padding:18px 20px">
<div style="font-weight:600;color:#58a6ff;margin-bottom:8px">@ontout is massively under-leveraged</div>
<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.6">
Only <b>3 posts</b> with @timjck despite averaging 1,570 likes each. This is a 13x multiplier
sitting on the shelf. Even 2 sessions/quarter = 8 high-engagement posts/year.
</div></div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
<div style="background:#0d1d2d;border:1px solid #1a3a5c;border-radius:10px;padding:18px 20px;margin-bottom:12px">
<div style="font-weight:600;color:#58a6ff;margin-bottom:8px">Brick by Brick + Late Night rising</div>
<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.6">
Popularity scores of <b>{ss['track_popularity'].get('Brick by Brick', 'N/A')}</b> and
<b>{ss['track_popularity'].get('Late Night', 'N/A')}</b> respectively. Both currently playlisted.
These have recent momentum — pitch to more playlists while scores are climbing.
</div></div>

<div style="background:#0d1d2d;border:1px solid #1a3a5c;border-radius:10px;padding:18px 20px">
<div style="font-weight:600;color:#58a6ff;margin-bottom:8px">Stories are 84.3% of IG views</div>
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
<div style="font-weight:600;color:#f0883e;margin-bottom:8px">2025 IG engagement dropped 55%</div>
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
        {"p": "P0", "color": "#f85149", "action": "Pitch Delicate, Brick by Brick, Late Night to more playlists", "effort": "Medium", "impact": "High", "rationale": "Currently playlisted with rising popularity scores. Strike while the algorithm is warm."},
        {"p": "P1", "color": "#f0c040", "action": "Cross-promote Enjune catalog to Jakke audience", "effort": "Low", "impact": "Medium", "rationale": f"2.65M Enjune streams are disconnected from {ss['spotify']['monthly_listeners']:,} Jakke monthly listeners."},
        {"p": "P1", "color": "#f0c040", "action": "Fix link-in-bio conversion", "effort": "Low", "impact": "Medium", "rationale": "0.5% conversion from 936 monthly visits = wasted traffic. Try Linktree or custom landing."},
        {"p": "P1", "color": "#f0c040", "action": "Test Thursday/Sunday posting schedule", "effort": "Low", "impact": "Medium", "rationale": "2-3x engagement vs worst days. Easy scheduling change."},
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
