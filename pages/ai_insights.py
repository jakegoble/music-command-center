"""AI Insights — Strategy brain of the entire Command Center."""
from __future__ import annotations

from datetime import datetime

import plotly.graph_objects as go
import streamlit as st

from theme import (
    SPOTIFY_GREEN, IG_PINK, GOLD, MUTED, ACCENT_BLUE, AMBER,
    TEXT, CARD_BG, BORDER,
    apply_theme, section, spacer, render_page_title, PLOTLY_CONFIG,
)


# ---------------------------------------------------------------------------
# Score helpers
# ---------------------------------------------------------------------------
_WEIGHTS = {
    "Streaming": 0.30,
    "Social": 0.25,
    "Collaborations": 0.20,
    "Funnel": 0.15,
    "Catalog": 0.10,
}
_ICONS = {
    "Streaming": "\U0001f3b5",
    "Social": "\U0001f4f1",
    "Collaborations": "\U0001f91d",
    "Funnel": "\U0001f517",
    "Catalog": "\U0001f4bf",
}


def _score_color(score: int) -> str:
    """Return hex color for a 0-100 score."""
    if score >= 75:
        return SPOTIFY_GREEN
    if score >= 55:
        return "#FFC107"
    if score >= 35:
        return "#FF9800"
    return "#F44336"


def _score_label(score: int) -> str:
    """Return status label for a 0-100 score."""
    if score >= 75:
        return "Strong"
    if score >= 55:
        return "Developing"
    if score >= 35:
        return "Needs Work"
    return "Critical"


def _norm(value: float, benchmark: float) -> float:
    """Normalize value against benchmark, capped at 100."""
    return min(100.0, value / benchmark * 100) if benchmark > 0 else 0.0


def _hex_to_rgb(hex_color: str) -> str:
    """Convert #RRGGBB to 'R,G,B' string for rgba() usage."""
    h = hex_color.lstrip("#")
    if len(h) == 6:
        return f"{int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)}"
    return "139,148,158"


def _calc_scores(ss: dict, songs, ig: dict, ig_yearly) -> dict[str, int]:
    """Calculate 5 strategy sub-scores (0-100) from real data."""

    # --- Streaming (30%) ---
    streaming = int(
        0.30 * _norm(ss["spotify"]["monthly_listeners"], 50_000)
        + 0.25 * _norm(ss["spotify"]["playlist_reach"], 2_000_000)
        + 0.25 * _norm(ss["spotify"]["current_playlists"], 75)
        + 0.20 * _norm(songs["popularity"].mean(), 33)
    )

    # --- Social (25%) ---
    followers = ig["account"]["followers"]
    eng_rate = ig["overview"]["interactions"] / followers if followers else 0
    reached_pct = ig["overview"]["accounts_reached"] / followers if followers else 0

    # YoY trend: compare two most recent full years (skip partial current year)
    yearly_sorted = ig_yearly.sort_values("year", ascending=False)
    full_years = yearly_sorted[yearly_sorted["posts"] >= 20]
    if len(full_years) >= 2:
        latest_avg = full_years.iloc[0]["avg_likes"]
        prior_avg = full_years.iloc[1]["avg_likes"]
        trend_pct = (latest_avg - prior_avg) / prior_avg if prior_avg else 0
        trend_score = max(0.0, min(100.0, 50 + trend_pct * 100))
    else:
        trend_score = 50.0

    social = int(
        0.35 * _norm(eng_rate, 0.05)
        + 0.25 * 80  # Reel performance (3.2x photos — strong)
        + 0.20 * _norm(reached_pct, 0.35)
        + 0.20 * trend_score
    )

    # --- Collaborations (20%) ---
    collab_multi = 2.2
    collab_rate = 55 / 451  # ~12.2% of posts
    collaborations = int(
        0.35 * _norm(collab_multi, 3.0)
        + 0.25 * 95  # Music collab output quality (Allen Blickle: 2.29M)
        + 0.25 * _norm(collab_rate, 0.25)
        + 0.15 * _norm(3, 12)  # @ontout utilization
    )

    # --- Funnel (15%) ---
    link_taps = ig["overview"]["external_link_taps"]
    profile_visits = ig["overview"]["profile_visits"]
    link_ctr = link_taps / profile_visits if profile_visits else 0
    visit_rate = profile_visits / followers if followers else 0
    funnel = int(
        0.70 * _norm(link_ctr, 0.03)
        + 0.30 * _norm(visit_rate, 0.08)
    )

    # --- Catalog (10%) ---
    total_songs = len(songs)
    n_genres = songs["genre"].nunique() if "genre" in songs.columns else 5
    avg_streams = songs["streams"].mean()
    catalog = int(
        0.40 * _norm(total_songs, 75)
        + 0.30 * _norm(n_genres, 10)
        + 0.30 * _norm(avg_streams, 200_000)
    )

    return {
        "Streaming": streaming,
        "Social": social,
        "Collaborations": collaborations,
        "Funnel": funnel,
        "Catalog": catalog,
    }


# ---------------------------------------------------------------------------
# HTML component builders
# ---------------------------------------------------------------------------
def _score_pill_html(name: str, score: int) -> str:
    """Render a sub-score pill badge."""
    color = _score_color(score)
    icon = _ICONS.get(name, "")
    rgb = _hex_to_rgb(color)
    return (
        f'<span style="display:inline-block;background:rgba({rgb},0.12);'
        f'color:{color};padding:5px 14px;border-radius:14px;font-size:13px;'
        f'font-weight:600;margin:3px 6px 3px 0;white-space:nowrap">'
        f'{icon} {name}: {score}</span>'
    )


def _insight_card(icon: str, title: str, highlight: str, explanation: str,
                  accent: str) -> str:
    """Build HTML for a single insight card with left-side icon + colored accent bar."""
    rgb = _hex_to_rgb(accent)
    return (
        f'<div style="display:flex;gap:14px;padding:16px 20px;margin-bottom:2px;'
        f'background:rgba({rgb},0.04);border-left:3px solid {accent};'
        f'border-radius:0 8px 8px 0">'
        f'<div style="font-size:24px;line-height:1.2;flex-shrink:0">{icon}</div>'
        f'<div>'
        f'<div style="font-weight:600;font-size:15px;color:{TEXT};margin-bottom:4px">{title}</div>'
        f'<div style="font-size:13px;color:rgba(255,255,255,0.5);margin-bottom:6px">'
        f'<span style="color:{accent};font-weight:600">{highlight}</span></div>'
        f'<div style="font-size:13px;color:rgba(255,255,255,0.40)">{explanation}</div>'
        f'</div></div>'
    )


def _priority_header(label: str, count: int, color: str) -> str:
    """Build HTML for a priority lane header."""
    return (
        f'<div style="font-size:12px;font-weight:700;letter-spacing:1px;text-transform:uppercase;'
        f'color:{color};margin:24px 0 8px 0">{label}'
        f'<span style="float:right;color:rgba(255,255,255,0.3);font-weight:400;font-size:11px">'
        f'{count} item{"s" if count != 1 else ""}</span></div>'
    )


def _action_card(icon: str, title: str, effort: str, impact: str,
                 data_point: str, accent: str) -> str:
    """Build HTML for a single action item card with effort/impact badges."""
    effort_colors = {"Low": SPOTIFY_GREEN, "Medium": "#FFC107", "High": "#F44336"}
    impact_colors = {"Very High": SPOTIFY_GREEN, "High": "#66BB6A", "Medium": "#FFC107", "Low": "#FF9800"}
    ec = effort_colors.get(effort, MUTED)
    ic = impact_colors.get(impact, MUTED)
    rgb = _hex_to_rgb(accent)
    ec_rgb = _hex_to_rgb(ec)
    ic_rgb = _hex_to_rgb(ic)
    return (
        f'<div style="display:flex;align-items:flex-start;gap:12px;padding:14px 16px;'
        f'background:rgba({rgb},0.04);border-left:3px solid {accent};'
        f'border-radius:0 6px 6px 0;margin-bottom:2px">'
        f'<div style="font-size:20px;margin-top:1px;flex-shrink:0">{icon}</div>'
        f'<div style="flex:1">'
        f'<div style="font-weight:600;font-size:14px;color:{TEXT}">{title}</div>'
        f'<div style="display:flex;gap:12px;margin-top:6px;flex-wrap:wrap">'
        f'<span style="font-size:11px;padding:2px 8px;border-radius:10px;'
        f'background:rgba({ec_rgb},0.12);color:{ec}">Effort: {effort}</span>'
        f'<span style="font-size:11px;padding:2px 8px;border-radius:10px;'
        f'background:rgba({ic_rgb},0.12);color:{ic}">Impact: {impact}</span>'
        f'<span style="font-size:11px;color:rgba(255,255,255,0.35)">{data_point}</span>'
        f'</div></div></div>'
    )


def _mini_card(icon: str, label: str, value: str, sub: str,
               sub_color: str = "") -> str:
    """Build HTML for a key metrics mini card."""
    sc = sub_color or "rgba(255,255,255,0.4)"
    return (
        f'<div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:14px 16px">'
        f'<div style="font-size:11px;color:rgba(255,255,255,0.4);text-transform:uppercase;'
        f'letter-spacing:0.5px">{icon} {label}</div>'
        f'<div style="font-size:28px;font-weight:700;color:{TEXT};margin:4px 0 2px">{value}</div>'
        f'<div style="font-size:12px;color:{sc}">{sub}</div>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Action items data
# ---------------------------------------------------------------------------
ACTIONS = [
    {"p": "P0", "icon": "\U0001f3af", "title": "Schedule 2+ @ontout sessions per quarter",
     "effort": "Low", "impact": "Very High", "data": "13x engagement multiplier",
     "effort_n": 1, "impact_n": 5},
    {"p": "P0", "icon": "\U0001f3ac", "title": "Create release-day Reels for every new single",
     "effort": "Medium", "impact": "Very High", "data": "3.2x photos",
     "effort_n": 3, "impact_n": 5},
    {"p": "P0", "icon": "\U0001f4cb", "title": "Pitch Delicate, Brick by Brick, Late Night to more playlists",
     "effort": "Medium", "impact": "High", "data": "Reach: 1.72M",
     "effort_n": 3, "impact_n": 4},
    {"p": "P1", "icon": "\U0001f48e", "title": "Cross-promote Enjune catalog to Jakke audience",
     "effort": "Low", "impact": "High", "data": "2.65M untapped",
     "effort_n": 1, "impact_n": 4},
    {"p": "P1", "icon": "\U0001f517", "title": "Fix link-in-bio conversion",
     "effort": "Low", "impact": "High", "data": "0.5% \u2192 target 3%+",
     "effort_n": 1, "impact_n": 4},
    {"p": "P1", "icon": "\U0001f4c5", "title": "Test Thursday/Sunday posting schedule",
     "effort": "Low", "impact": "Medium", "data": "2-week test",
     "effort_n": 1, "impact_n": 3},
    {"p": "P2", "icon": "\U0001f91d", "title": "Increase collab ratio to 25%+",
     "effort": "Medium", "impact": "Medium", "data": "Currently ~15%",
     "effort_n": 3, "impact_n": 3},
    {"p": "P2", "icon": "\U0001f4f8", "title": "Use Stories for strategic music promotion",
     "effort": "Low", "impact": "Medium", "data": "84.3% of IG views",
     "effort_n": 1, "impact_n": 3},
    {"p": "P3", "icon": "\U0001f4c9", "title": "Diagnose 2025 engagement drop",
     "effort": "High", "impact": "High", "data": "55% decline",
     "effort_n": 4, "impact_n": 4},
]

PRIORITY_COLORS = {
    "P0": {"label": "\U0001f534 DO NOW", "color": "#F44336"},
    "P1": {"label": "\U0001f7e1 DO NEXT", "color": "#FFC107"},
    "P2": {"label": "\U0001f535 EXPERIMENT", "color": "#2196F3"},
    "P3": {"label": "\u26aa INVESTIGATE", "color": "#8b949e"},
}


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------
def render() -> None:
    from data_loader import (
        load_songstats_jakke, load_songstats_enjune, load_songs_all,
        load_ig_insights, load_ig_yearly,
    )

    ss = load_songstats_jakke()
    enjune = load_songstats_enjune()
    songs = load_songs_all()
    ig = load_ig_insights()
    ig_yearly = load_ig_yearly()

    render_page_title(
        "AI Insights",
        "Strategy brain \u2014 scores, recommendations, and action items",
        "#E74C3C",
    )

    # --- Calculate scores ---
    scores = _calc_scores(ss, songs, ig, ig_yearly)
    composite = int(sum(scores[k] * _WEIGHTS[k] for k in scores))

    # ── This Week's Focus ──
    top_action = ACTIONS[0]
    st.markdown(f"""
    <div style="background:linear-gradient(135deg, rgba(244,67,54,0.08), rgba(255,193,7,0.08));
                border:1px solid rgba(244,67,54,0.2);border-radius:12px;padding:20px 24px;
                margin-bottom:16px">
        <div style="font-size:10px;text-transform:uppercase;letter-spacing:1.5px;
                    color:rgba(255,255,255,0.35);margin-bottom:8px">
            \u26a1 THIS WEEK'S FOCUS</div>
        <div style="font-size:18px;font-weight:600;color:{TEXT}">
            {top_action['icon']} {top_action['title']}</div>
        <div style="font-size:13px;color:rgba(255,255,255,0.5);margin-top:6px">
            {top_action['data']} \u00b7 Effort: {top_action['effort']} \u00b7 Impact: {top_action['impact']}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Strategy Score Hero ──
    section("Strategy Score")
    bar_color = _score_color(composite)
    pills_html = "".join(_score_pill_html(k, scores[k]) for k in _WEIGHTS)
    month_label = datetime.now().strftime("%B %Y")

    st.markdown(f"""
    <div style="background:linear-gradient(135deg, {CARD_BG} 0%, #1c2333 100%);
                border:1px solid {BORDER};border-radius:12px;padding:24px 28px;
                box-shadow:0 2px 12px rgba(0,0,0,0.3)">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
            <div style="font-size:13px;color:{MUTED};font-weight:600;letter-spacing:0.08em;
                        text-transform:uppercase">
                \U0001f9e0 Strategy Score</div>
            <div style="font-size:12px;color:rgba(255,255,255,0.25)">{month_label}</div>
        </div>
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:16px">
            <div style="flex:1;background:rgba(255,255,255,0.06);border-radius:8px;height:28px;
                        overflow:hidden">
                <div style="width:{composite}%;height:100%;background:{bar_color};border-radius:8px;
                            transition:width 0.5s ease"></div>
            </div>
            <div style="font-size:28px;font-weight:700;color:{bar_color};white-space:nowrap">
                {composite} / 100</div>
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:0">{pills_html}</div>
    </div>
    """, unsafe_allow_html=True)

    spacer(16)

    # ── Strategy Radar Chart + Score Breakdown ──
    left_radar, right_breakdown = st.columns([3, 2], gap="large")

    with left_radar:
        section("Strategy Shape")
        categories = list(_WEIGHTS.keys())
        values = [scores[c] for c in categories]
        target = [80, 70, 75, 60, 70]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor=f"rgba({_hex_to_rgb(SPOTIFY_GREEN)},0.15)",
            line=dict(color=SPOTIFY_GREEN, width=2),
            marker=dict(size=8, color=SPOTIFY_GREEN),
            name="Current",
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=target + [target[0]],
            theta=categories + [categories[0]],
            fill="none",
            line=dict(color="rgba(255,255,255,0.15)", width=1, dash="dot"),
            marker=dict(size=0),
            name="Target",
        ))
        # Radar uses polar layout — apply_theme's xaxis/yaxis don't apply
        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    visible=True, range=[0, 100],
                    tickfont=dict(size=10, color="rgba(255,255,255,0.25)"),
                    gridcolor="rgba(255,255,255,0.06)",
                ),
                angularaxis=dict(
                    tickfont=dict(size=12, color="rgba(255,255,255,0.55)"),
                ),
            ),
            showlegend=True,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.6)", family="Inter, sans-serif"),
            margin=dict(t=30, b=30, l=60, r=60),
            height=380,
            legend=dict(
                orientation="h", y=-0.05, x=0.5, xanchor="center",
                font=dict(size=11), bgcolor="rgba(0,0,0,0)",
            ),
        )
        st.plotly_chart(fig_radar, use_container_width=True, config=PLOTLY_CONFIG,
                        key="ai_radar")

    with right_breakdown:
        section("Score Breakdown")
        for name in _WEIGHTS:
            s = scores[name]
            icon = _ICONS[name]
            color = _score_color(s)
            label = _score_label(s)
            weight_pct = int(_WEIGHTS[name] * 100)
            st.markdown(f"""
            <div style="margin-bottom:12px">
                <div style="display:flex;justify-content:space-between;align-items:center;
                            margin-bottom:4px">
                    <span style="font-size:13px;color:{TEXT};font-weight:500">
                        {icon} {name}</span>
                    <span style="font-size:13px;font-weight:700;color:{color}">
                        {s}/100 \u00b7 {label}</span>
                </div>
                <div style="background:rgba(255,255,255,0.06);border-radius:4px;height:6px;
                            overflow:hidden">
                    <div style="width:{s}%;height:100%;background:{color};border-radius:4px">
                    </div>
                </div>
                <div style="font-size:10px;color:rgba(255,255,255,0.25);margin-top:2px">
                    {weight_pct}% of total score</div>
            </div>
            """, unsafe_allow_html=True)

    spacer(16)

    # ── What's Working ──
    section("What's Working", SPOTIFY_GREEN)
    top_song = songs.loc[songs["streams"].idxmax()]
    top_song_pop = int(top_song["popularity"]) if top_song["popularity"] > 0 else "N/A"
    playlisted = ", ".join(ss["currently_playlisted"])

    working_html = "\n".join([
        _insight_card(
            "\U0001f3c6", "Your Love's Not Wasted is a breakout hit",
            f"{top_song['streams']:,.0f} streams \u00b7 5x the next closest song \u00b7 Pop: {top_song_pop}",
            "Driving the majority of catalog discovery.", SPOTIFY_GREEN,
        ),
        _insight_card(
            "\U0001f3ac", "Video/Reels dominate IG engagement",
            "202 avg likes/post \u00b7 3.2x photos \u00b7 51.3% of interactions",
            "Every music release post that hit 500+ likes was a Reel.", SPOTIFY_GREEN,
        ),
        _insight_card(
            "\U0001f4cb", "Currently playlisted songs have momentum",
            f"{playlisted} \u00b7 Reach: {ss['spotify']['playlist_reach']:,.0f}",
            "Being pushed by the algorithm \u2014 lean in.", SPOTIFY_GREEN,
        ),
        _insight_card(
            "\U0001f91d", "Collaborations are a cheat code",
            "261 avg likes (2.2x solo) \u00b7 @ontout: 13x \u00b7 Allen Blickle: 6 tracks, 2.29M streams",
            "Collab content consistently outperforms solo content.", SPOTIFY_GREEN,
        ),
    ])
    st.markdown(working_html, unsafe_allow_html=True)

    spacer(16)

    # ── Opportunities ──
    section("Opportunities", "#FFC107")
    bb_pop = ss["track_popularity"].get("Brick by Brick", "N/A")
    ln_pop = ss["track_popularity"].get("Late Night", "N/A")

    opp_html = "\n".join([
        _insight_card(
            "\U0001f48e", "Enjune catalog is underleveraged",
            f"{enjune['spotify']['total_streams']:,.0f} Enjune streams disconnected from "
            f"{ss['spotify']['monthly_listeners']:,} Jakke listeners",
            "Cross-promote Enjune catalog for quick streaming gains.", "#FFC107",
        ),
        _insight_card(
            "\U0001f4c8", "Brick by Brick + Late Night rising",
            f"Popularity: {bb_pop} and {ln_pop} \u00b7 Both currently playlisted",
            "These have recent momentum \u2014 pitch to more playlists while scores are climbing.",
            "#FFC107",
        ),
        _insight_card(
            "\U0001f3af", "@ontout is massively under-leveraged",
            "Only 3 posts despite 1,570 avg likes each \u00b7 13x multiplier sitting on the shelf",
            "Even 2 sessions/quarter = 8 high-engagement posts/year.", "#FFC107",
        ),
        _insight_card(
            "\U0001f4f8", "Stories are 84.3% of IG views but underutilized",
            "43,641 views in 30 days \u00b7 Massive reach channel",
            "Could be used for release teasers, behind-the-scenes, session clips.", "#FFC107",
        ),
    ])
    st.markdown(opp_html, unsafe_allow_html=True)

    spacer(16)

    # ── Risks ──
    section("Risks", "#F44336")
    risk_html = "\n".join([
        _insight_card(
            "\U0001f4c9", "2025 IG engagement dropped 55%",
            "2024 avg: 216 likes/post \u2192 2025: 98 likes/post \u00b7 Volume up, quality down",
            "Algorithm changes, audience fatigue, or content mix shift.", "#F44336",
        ),
        _insight_card(
            "\u231b", "YLNW streams are mostly legacy",
            "1.9M all-time but only 2,569 in recent 3-year window",
            "Current velocity may be near-zero \u2014 focus on recent momentum songs.", "#F44336",
        ),
        _insight_card(
            "\U0001f517", "Link-in-bio conversion is broken",
            "5 link taps / 936 profile visits = 0.5% conversion",
            "The funnel from IG \u2192 streaming/website is effectively non-functional.",
            "#F44336",
        ),
        _insight_card(
            "\U0001f53b", "Solo post engagement declining",
            "Solo: 121 avg likes vs Collab: 261 \u00b7 Negative feedback loop",
            "As the algorithm favors engagement, lower-performing solo posts get less reach.",
            "#F44336",
        ),
    ])
    st.markdown(risk_html, unsafe_allow_html=True)

    spacer(16)

    # ── Action Items — Priority Lanes ──
    total_actions = len(ACTIONS)
    section(f"Action Items \u00b7 {total_actions} items")

    for p_key, p_info in PRIORITY_COLORS.items():
        lane_actions = [a for a in ACTIONS if a["p"] == p_key]
        if not lane_actions:
            continue
        st.markdown(
            _priority_header(p_info["label"], len(lane_actions), p_info["color"]),
            unsafe_allow_html=True,
        )
        cards = "\n".join(
            _action_card(
                a["icon"], a["title"], a["effort"], a["impact"],
                a["data"], p_info["color"],
            )
            for a in lane_actions
        )
        st.markdown(cards, unsafe_allow_html=True)

    spacer(16)

    # ── Quick Wins vs Big Bets — Effort/Impact Matrix ──
    section("Quick Wins vs Big Bets")
    p_dot_colors = {
        "P0": "#F44336", "P1": "#FFC107", "P2": "#2196F3", "P3": "#8b949e",
    }

    fig_matrix = go.Figure()
    for p_key in ["P0", "P1", "P2", "P3"]:
        items = [a for a in ACTIONS if a["p"] == p_key]
        if not items:
            continue
        fig_matrix.add_trace(go.Scatter(
            x=[a["effort_n"] for a in items],
            y=[a["impact_n"] for a in items],
            mode="markers+text",
            marker=dict(size=22, color=p_dot_colors[p_key], opacity=0.85),
            text=[a["icon"] for a in items],
            textposition="middle center",
            textfont=dict(size=14),
            hovertext=[
                f"{a['icon']} {a['title']}<br>Effort: {a['effort_n']}/5 \u00b7 "
                f"Impact: {a['impact_n']}/5"
                for a in items
            ],
            hoverinfo="text",
            name=PRIORITY_COLORS[p_key]["label"],
            showlegend=False,
        ))

    # Quadrant labels
    fig_matrix.add_annotation(
        x=1, y=4.8, text="\u26a1 QUICK WINS", showarrow=False,
        font=dict(size=11, color=SPOTIFY_GREEN), xanchor="left",
    )
    fig_matrix.add_annotation(
        x=3.5, y=4.8, text="\U0001f680 BIG BETS", showarrow=False,
        font=dict(size=11, color="#FFC107"), xanchor="left",
    )
    fig_matrix.add_annotation(
        x=1, y=1.2, text="\U0001f4a4 LOW PRIORITY", showarrow=False,
        font=dict(size=11, color="rgba(255,255,255,0.2)"), xanchor="left",
    )
    fig_matrix.add_annotation(
        x=3.5, y=1.2, text="\u26a0\ufe0f RESOURCE HEAVY", showarrow=False,
        font=dict(size=11, color="rgba(255,255,255,0.2)"), xanchor="left",
    )

    # Quadrant dividers
    fig_matrix.add_hline(
        y=3, line=dict(color="rgba(255,255,255,0.08)", width=1, dash="dot"),
    )
    fig_matrix.add_vline(
        x=2.5, line=dict(color="rgba(255,255,255,0.08)", width=1, dash="dot"),
    )

    apply_theme(
        fig_matrix, height=380, showlegend=False,
        xaxis=dict(
            title="Effort \u2192", range=[0.3, 5.2], dtick=1,
            gridcolor="rgba(255,255,255,0.05)", showgrid=True,
        ),
        yaxis=dict(
            title="Impact \u2192", range=[0.8, 5.5], dtick=1,
            gridcolor="rgba(255,255,255,0.05)", showgrid=True,
        ),
    )
    st.plotly_chart(fig_matrix, use_container_width=True, config=PLOTLY_CONFIG,
                    key="ai_matrix")

    spacer(16)

    # ── Key Metrics Grid ──
    section("Key Metrics That Drive These Insights")
    followers = ig["account"]["followers"]
    interactions = ig["overview"]["interactions"]
    eng_rate = interactions / followers * 100 if followers else 0
    link_taps = ig["overview"]["external_link_taps"]
    profile_visits = ig["overview"]["profile_visits"]
    link_ctr = link_taps / profile_visits * 100 if profile_visits else 0

    r1 = st.columns(3)
    with r1[0]:
        st.markdown(_mini_card(
            "\U0001f4f1", "IG Engagement Rate", f"{eng_rate:.1f}%",
            "\u25bc from 3.8% (2024)", "#F44336",
        ), unsafe_allow_html=True)
    with r1[1]:
        st.markdown(_mini_card(
            "\U0001f3ac", "Reel vs Photo", "3.2x",
            "Reels win (202 vs 64 avg)", SPOTIFY_GREEN,
        ), unsafe_allow_html=True)
    with r1[2]:
        st.markdown(_mini_card(
            "\U0001f517", "Link-in-Bio CTR", f"{link_ctr:.1f}%",
            "\u25bc critically low", "#F44336",
        ), unsafe_allow_html=True)

    spacer(8)

    r2 = st.columns(3)
    with r2[0]:
        st.markdown(_mini_card(
            "\U0001f91d", "Collab Multiplier", "2.2x",
            "vs solo posts", "#FFC107",
        ), unsafe_allow_html=True)
    with r2[1]:
        st.markdown(_mini_card(
            "\U0001f3af", "@ontout Multiplier", "13x",
            "3 posts only", SPOTIFY_GREEN,
        ), unsafe_allow_html=True)
    with r2[2]:
        st.markdown(_mini_card(
            "\U0001f4cb", "Playlist Reach",
            f"{ss['spotify']['playlist_reach']:,.0f}",
            f"{ss['spotify']['current_playlists']} playlists", SPOTIFY_GREEN,
        ), unsafe_allow_html=True)

    spacer(8)

    r3 = st.columns(3)
    with r3[0]:
        st.markdown(_mini_card(
            "\U0001f4f8", "Story % of IG Views", "84.3%",
            "mostly untapped", "#FFC107",
        ), unsafe_allow_html=True)
    with r3[1]:
        st.markdown(_mini_card(
            "\U0001f48e", "Enjune Streams",
            f"{enjune['spotify']['total_streams']:,.0f}",
            f"{enjune['spotify']['monthly_listeners']:,} listeners", ACCENT_BLUE,
        ), unsafe_allow_html=True)
    with r3[2]:
        avg_pop = songs["popularity"].mean()
        st.markdown(_mini_card(
            "\U0001f4c8", "Avg Popularity Score", f"{avg_pop:.0f}/100",
            "catalog average", MUTED,
        ), unsafe_allow_html=True)

    spacer(16)

    # ── Footer ──
    st.markdown("""
    <div style="text-align:center;padding:24px 0 12px;color:rgba(255,255,255,0.2);font-size:11px">
        \U0001f9e0 Insights generated from static data analysis \u00b7 Last updated: Feb 2026
        <br>Connect live APIs (Spotify for Artists, IG Graph API) for real-time recommendations
    </div>
    """, unsafe_allow_html=True)
