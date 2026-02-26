"""AI Insights — Strategic recommendations derived from data analysis."""
from __future__ import annotations

import streamlit as st

SPOTIFY_GREEN = "#1DB954"
IG_PINK = "#E1306C"


def render() -> None:
    st.markdown("# 🧠 AI Insights")
    st.caption("Strategic recommendations derived from data analysis across all platforms")

    # =====================================================================
    # What's Working
    # =====================================================================
    st.markdown("## ✅ What's Working")

    col1, col2 = st.columns(2)

    with col1:
        st.success("""
**Video/Reels dominate engagement**
- Reels average **202 likes/post** — 3.2x photos (64 avg)
- Reels drive **51.3%** of interactions despite being a smaller % of posts
- Every music release post that hit 500+ likes was a Video/Reel
        """)

        st.success("""
**Collaborations are a cheat code**
- Collab posts average **261 likes** (2.2x solo at 121)
- @ontout sessions average **1,570 likes** (13x solo!)
- @enjune.music cross-posts average **404 likes** (3.3x solo)
        """)

    with col2:
        st.success("""
**Music releases drive peak engagement**
- Top 5 posts all-time are music release Reels
- "HOW DO YOU LOVE" EP release: 3,997 likes
- "WAIT" release: 3,992 likes
- "HURRICANE" release: 3,694 likes
        """)

        st.success("""
**Optimal posting days identified**
- **Thursday** (193 avg likes) and **Sunday** (187 avg) are clear winners
- Monday is the weakest day (64 avg likes)
- Weekend posting generally outperforms weekday
        """)

    st.divider()

    # =====================================================================
    # Opportunities
    # =====================================================================
    st.markdown("## 🎯 Opportunities")

    col3, col4 = st.columns(2)

    with col3:
        st.info("""
**Collab ratio is way too low**
- Only **55 collab posts** out of 451 music-era posts (12%)
- Collabs get 2.2x engagement but represent a tiny fraction
- Increasing to 25%+ collab ratio could lift overall engagement by 15-20%
        """)

        st.info("""
**@ontout is massively under-leveraged**
- Only **3 posts** with @timjck despite averaging 1,570 likes each
- This is a 13x multiplier sitting on the shelf
- Even 2 sessions per quarter = 8 high-engagement posts/year
        """)

    with col4:
        st.info("""
**Karma Response is the hidden recent leader**
- **36,024 streams** in the recent 3-year period (vs YLNW's 2,569 recent)
- This song has current momentum but is under-promoted on IG
- Cross-platform push could accelerate it further
        """)

        st.info("""
**Stories are 84.3% of views but underutilized for music**
- Massive reach channel (43,641 views in 30 days)
- Could be used for release teasers, behind-the-scenes, session clips
- Currently seems more lifestyle/ephemeral than strategic music content
        """)

    st.divider()

    # =====================================================================
    # Risks
    # =====================================================================
    st.markdown("## ⚠️ Risks")

    col5, col6 = st.columns(2)

    with col5:
        st.warning("""
**2025 engagement dropped 55% from 2024**
- 2024 avg: **216 likes/post** → 2025 avg: **98 likes/post**
- Volume went up (89 → 106 posts) but quality/engagement ratio fell
- Could indicate algorithm changes, audience fatigue, or content mix shift
        """)

        st.warning("""
**Link-in-bio conversion is abysmal**
- Only **5 external link taps** in 30 days
- Despite **936 profile visits** (0.5% conversion)
- The funnel from IG → streaming/website is effectively broken
        """)

    with col6:
        st.warning("""
**Your Love's Not Wasted streams are mostly legacy**
- 1.9M all-time but only **2,569** in the recent 3-year window
- Current velocity may be near-zero (playlist-driven tail)
- Don't over-index on total numbers — focus on recent momentum songs
        """)

        st.warning("""
**Solo post engagement is declining**
- Solo posts average only **121 likes** (vs 261 for collabs)
- As the algorithm favors engagement, lower-performing solo posts get less reach
- This creates a negative feedback loop without intervention
        """)

    st.divider()

    # =====================================================================
    # Action Items
    # =====================================================================
    st.markdown("## 🎬 Action Items")

    actions = [
        {
            "priority": "P0",
            "action": "Schedule 2+ @ontout sessions per quarter",
            "rationale": "13x engagement multiplier. Highest-leverage activity available.",
            "effort": "Medium",
            "impact": "Very High",
        },
        {
            "priority": "P0",
            "action": "Create release-day Reels for every new single",
            "rationale": "Every 500+ like post is a music release Reel. This is the proven format.",
            "effort": "Low",
            "impact": "High",
        },
        {
            "priority": "P1",
            "action": "Test Thursday/Sunday posting schedule",
            "rationale": "2-3x engagement vs worst days (Monday/Friday). Easy scheduling change.",
            "effort": "Low",
            "impact": "Medium",
        },
        {
            "priority": "P1",
            "action": "Fix link-in-bio conversion",
            "rationale": "0.5% conversion from 936 monthly profile visits = wasted traffic. Try Linktree or custom landing page.",
            "effort": "Low",
            "impact": "Medium",
        },
        {
            "priority": "P1",
            "action": "Cross-promote Karma Response on IG",
            "rationale": "Top recent streamer (36K in 3yr) but under-represented on Instagram.",
            "effort": "Low",
            "impact": "Medium",
        },
        {
            "priority": "P2",
            "action": "Increase collab ratio to 25%+",
            "rationale": "Currently 12% collab posts. Each collab gets 2.2x engagement. More collabs = more reach.",
            "effort": "Medium",
            "impact": "High",
        },
        {
            "priority": "P2",
            "action": "Use Stories strategically for music promotion",
            "rationale": "84.3% of views but appears underutilized for music content. Add teasers, studio clips, countdowns.",
            "effort": "Low",
            "impact": "Medium",
        },
        {
            "priority": "P3",
            "action": "Diagnose 2025 engagement drop",
            "rationale": "55% drop YoY needs investigation — content mix, posting time, format changes?",
            "effort": "Medium",
            "impact": "High",
        },
    ]

    for a in actions:
        priority_colors = {"P0": "🔴", "P1": "🟡", "P2": "🔵", "P3": "⚪"}
        icon = priority_colors.get(a["priority"], "⚪")

        with st.expander(f"{icon} [{a['priority']}] {a['action']}"):
            c1, c2 = st.columns(2)
            c1.markdown(f"**Effort:** {a['effort']}")
            c2.markdown(f"**Impact:** {a['impact']}")
            st.markdown(f"**Rationale:** {a['rationale']}")

    st.divider()

    # --- Key numbers summary ---
    st.markdown("## 📊 Key Numbers to Watch")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Current Solo Avg", "121 likes", delta="-55% vs 2024", delta_color="inverse")
    m2.metric("Collab Multiplier", "2.2x", help="Collab avg / Solo avg")
    m3.metric("@ontout Multiplier", "13x", help="1,570 avg vs 121 solo avg")
    m4.metric("Link Conversion", "0.5%", delta="Needs 5-10%", delta_color="inverse")

    st.caption("💡 These insights are generated from static data analysis. Connect live APIs (Spotify for Artists, IG Graph API) for real-time recommendations.")
