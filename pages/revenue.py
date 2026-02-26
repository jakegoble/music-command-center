"""Revenue — Streaming revenue estimates, splits, and projections."""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

from theme import (
    SPOTIFY_GREEN, ACCENT_BLUE, GOLD, AMBER, MUTED, IG_PINK,
    PLOTLY_CONFIG, apply_theme, kpi_row, section, spacer, platform_icon,
    render_page_title,
)


def render() -> None:
    from data_loader import load_songs_all, load_songstats_jakke, load_songstats_enjune
    from services.revenue_estimator import (
        estimate_revenue, RATES, PLATFORM_SPLIT, get_jake_split,
    )

    songs = load_songs_all()
    ss = load_songstats_jakke()
    enjune = load_songstats_enjune()

    render_page_title("Revenue", "Streaming revenue estimates, ownership splits, and projections", "#f0c040")

    # --- Compute revenue ---
    jakke_cross = ss["cross_platform"]["total_streams"]
    enjune_total = enjune["spotify"]["total_streams"]
    combined = jakke_cross + enjune_total

    jakke_rev = estimate_revenue(jakke_cross)
    enjune_rev = estimate_revenue(enjune_total)
    combined_rev = estimate_revenue(combined)

    # Per-track revenue with splits
    songs_rev = songs.copy()
    songs_rev["est_total_streams"] = (songs_rev["streams"] / 0.60).astype(int)
    songs_rev["est_revenue"] = songs_rev["est_total_streams"].apply(
        lambda s: estimate_revenue(s).estimated_revenue
    )
    songs_rev["jake_split"] = songs_rev["song"].apply(get_jake_split)
    songs_rev["jake_revenue"] = songs_rev["est_revenue"] * songs_rev["jake_split"]

    total_jake_revenue = songs_rev["jake_revenue"].sum()
    total_est_revenue = songs_rev["est_revenue"].sum()
    avg_split = total_jake_revenue / total_est_revenue if total_est_revenue > 0 else 1.0

    # --- KPIs ---
    kpi_row([
        {"label": "Est. Total Revenue", "value": f"${combined_rev.estimated_revenue:,.0f}", "sub": f"From {combined:,.0f} cross-platform streams", "accent": GOLD},
        {"label": "Jake's Net Revenue", "value": f"${total_jake_revenue:,.0f}", "sub": f"After splits (avg {avg_split:.0%} ownership)", "accent": SPOTIFY_GREEN},
        {"label": "Enjune Revenue", "value": f"${enjune_rev.estimated_revenue:,.0f}", "sub": f"{enjune_total:,.0f} streams", "accent": AMBER},
        {"label": "Blended Rate", "value": f"${combined_rev.blended_rate:.4f}", "sub": "Per stream (all platforms)"},
    ])

    spacer(16)

    # --- Revenue by platform ---
    left, right = st.columns(2, gap="large")

    with left:
        section("Revenue by Platform")
        platform_data = []
        for platform, info in combined_rev.platform_breakdown.items():
            platform_data.append({
                "Platform": platform,
                "Revenue": info["revenue"],
                "Streams": info["streams"],
                "Rate": info["rate"],
            })
        plat_df = pd.DataFrame(platform_data).sort_values("Revenue", ascending=True)

        colors = {
            "Spotify": SPOTIFY_GREEN, "Apple Music": "#fc3c44", "YouTube Music": "#ff0000",
            "Amazon Music": "#00a8e1", "Deezer": "#a238ff", "Tidal": "#000000", "Other": MUTED,
        }
        fig = px.bar(
            plat_df, x="Revenue", y="Platform", orientation="h",
            color="Platform", color_discrete_map=colors,
        )
        apply_theme(fig, height=340, yaxis_title="", xaxis_title="Estimated Revenue ($)", showlegend=False)
        fig.update_xaxes(tickprefix="$", tickformat=",")
        fig.update_traces(hovertemplate="%{y}<br><b>$%{x:,.0f}</b><extra></extra>")
        st.plotly_chart(fig, use_container_width=True, key="rev_by_platform", config=PLOTLY_CONFIG)

    with right:
        section("Per-Stream Rates by Platform")
        rate_df = pd.DataFrame([
            {"Platform": p, "Rate": r} for p, r in RATES.items() if p != "Other"
        ]).sort_values("Rate")
        fig_rates = px.bar(
            rate_df, x="Rate", y="Platform", orientation="h",
            color_discrete_sequence=[ACCENT_BLUE],
        )
        apply_theme(fig_rates, height=340, yaxis_title="", xaxis_title="$/Stream")
        fig_rates.update_xaxes(tickprefix="$")
        fig_rates.update_traces(hovertemplate="%{y}<br><b>$%{x:.4f}</b>/stream<extra></extra>")
        st.plotly_chart(fig_rates, use_container_width=True, key="rev_rates", config=PLOTLY_CONFIG)

    spacer(16)

    # --- Top earners (Jake's share) ---
    section("Top Earning Tracks — Jake's Share")
    top_earners = songs_rev.nlargest(15, "jake_revenue").sort_values("jake_revenue")
    fig_top = go.Figure()
    fig_top.add_trace(go.Bar(
        x=top_earners["jake_revenue"], y=top_earners["song"], orientation="h",
        marker_color=GOLD,
        text=top_earners["jake_split"].apply(lambda x: f"{x:.0%}"),
        textposition="outside", textfont=dict(color=MUTED, size=10),
        hovertemplate="%{y}<br>Jake's share: <b>$%{x:,.2f}</b><extra></extra>",
    ))
    apply_theme(fig_top, height=480, yaxis_title="", xaxis_title="Jake's Revenue ($)")
    fig_top.update_xaxes(tickprefix="$", tickformat=",")
    st.plotly_chart(fig_top, use_container_width=True, key="rev_top_earners", config=PLOTLY_CONFIG)

    spacer(16)

    # --- Revenue table with splits ---
    section("Revenue by Track")
    rev_display = songs_rev[[
        "song", "artist", "streams", "est_total_streams", "est_revenue", "jake_split", "jake_revenue",
    ]].sort_values("jake_revenue", ascending=False).copy()
    rev_display["streams"] = rev_display["streams"].apply(lambda x: f"{x:,}")
    rev_display["est_total_streams"] = rev_display["est_total_streams"].apply(lambda x: f"{x:,}")
    rev_display["est_revenue"] = rev_display["est_revenue"].apply(lambda x: f"${x:,.2f}")
    rev_display["jake_split"] = rev_display["jake_split"].apply(lambda x: f"{x:.0%}")
    rev_display["jake_revenue"] = rev_display["jake_revenue"].apply(lambda x: f"${x:,.2f}")
    rev_display.columns = ["Song", "Artist", "Spotify Streams", "Est. Total", "Total Rev", "Jake's %", "Jake's Share"]
    st.dataframe(rev_display, use_container_width=True, hide_index=True, height=400)

    spacer(12)

    # --- Projection tool ---
    section("Revenue Projection Tool")
    st.markdown("""
<div style="background:#161b22;border:1px solid #21262d;border-radius:10px;padding:14px 18px;margin-bottom:16px">
    <span style="color:#8b949e;font-size:0.82rem">Adjust sliders to model future revenue. Projections apply Jake's average split ({avg_split:.0%}) to new streams.</span>
</div>
    """.format(avg_split=avg_split), unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        monthly_streams = st.slider("Monthly Spotify Streams", min_value=10000, max_value=500000, value=50000, step=5000, key="rev_monthly")
    with col_s2:
        months = st.slider("Projection Months", min_value=3, max_value=36, value=12, step=3, key="rev_months")

    # Build projection
    projection_data = []
    cumulative_streams = combined
    cumulative_revenue = combined_rev.estimated_revenue

    for m in range(1, months + 1):
        monthly_cross = int(monthly_streams / 0.60)
        monthly_rev = estimate_revenue(monthly_cross).estimated_revenue
        monthly_jake = monthly_rev * avg_split
        cumulative_streams += monthly_cross
        cumulative_revenue += monthly_rev
        projection_data.append({
            "Month": m,
            "Monthly Streams": monthly_cross,
            "Monthly Revenue": monthly_rev,
            "Jake's Monthly": monthly_jake,
            "Cumulative Streams": cumulative_streams,
            "Cumulative Revenue": cumulative_revenue,
        })

    proj_df = pd.DataFrame(projection_data)

    left2, right2 = st.columns(2, gap="large")

    with left2:
        section("Cumulative Revenue Projection")
        fig_proj = go.Figure()
        fig_proj.add_trace(go.Scatter(
            x=proj_df["Month"], y=proj_df["Cumulative Revenue"],
            mode="lines+markers", line=dict(color=GOLD, width=3),
            marker=dict(size=6), fill="tozeroy", fillcolor="rgba(240,192,64,0.08)",
            hovertemplate="Month %{x}<br><b>$%{y:,.0f}</b><extra></extra>",
        ))
        apply_theme(fig_proj, height=340, xaxis_title="Month", yaxis_title="Cumulative Revenue ($)")
        fig_proj.update_yaxes(tickprefix="$", tickformat=",")
        st.plotly_chart(fig_proj, use_container_width=True, key="rev_projection", config=PLOTLY_CONFIG)

    with right2:
        section("Projection Summary")
        final = proj_df.iloc[-1]
        annual_rev = proj_df["Monthly Revenue"].sum()
        annual_jake = proj_df["Jake's Monthly"].sum()

        kpi_row([
            {"label": f"{months}-Month Revenue", "value": f"${annual_rev:,.0f}", "accent": GOLD},
            {"label": f"Jake's {months}-Month", "value": f"${annual_jake:,.0f}", "accent": SPOTIFY_GREEN},
        ])
        spacer(12)
        kpi_row([
            {"label": "Final Total Streams", "value": f"{final['Cumulative Streams']:,.0f}", "accent": SPOTIFY_GREEN},
            {"label": "Final Total Revenue", "value": f"${final['Cumulative Revenue']:,.0f}", "accent": GOLD},
        ])

    spacer(12)
    st.caption("Revenue estimates use industry-average per-stream rates. Splits are default assumptions (50/50 for co-writes) — adjust in revenue_estimator.py. Actual payouts vary by territory, subscription type, and distributor terms.")
