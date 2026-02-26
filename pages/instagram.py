"""Instagram — Complete IG analytics with sub-tabs."""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

from theme import (
    IG_PINK, IG_PURPLE, IG_ORANGE, ACCENT_BLUE, MUTED, GOLD,
    PLOTLY_CONFIG, chart_layout, apply_theme, kpi_row, section, spacer, platform_icon,
    render_page_title, get_platform_icon_html,
)

# UTC → ET offset (EST = -5)
UTC_TO_ET_OFFSET = -5


def _utc_to_et(hour_utc: int) -> int:
    """Convert a UTC hour (0-23) to Eastern Time."""
    return (hour_utc + UTC_TO_ET_OFFSET) % 24


def render() -> None:
    from data_loader import (
        load_ig_insights, load_ig_yearly, load_ig_monthly,
        load_ig_top_posts, load_ig_content_type, load_ig_day_of_week,
    )

    ig = load_ig_insights()
    yearly = load_ig_yearly()
    monthly = load_ig_monthly()
    top_posts = load_ig_top_posts()
    content_type = load_ig_content_type()
    dow = load_ig_day_of_week()

    # Calculate engagement rate
    followers = ig["account"]["followers"]
    interactions = ig["overview"]["interactions"]
    engagement_rate = (interactions / followers * 100) if followers > 0 else 0

    render_page_title("Instagram", f"@jakke · {followers:,} followers · {ig['account']['posts_count']:,} posts", "#E1306C")

    tab_overview, tab_posts, tab_top, tab_history = st.tabs(["Overview (30d)", "Post Performance", "Top Posts", "Historical"])

    # ── TAB A: Overview ──
    with tab_overview:
        ov = ig["overview"]
        kpi_row([
            {"label": "Views", "value": f"{ov['views_30d']:,}", "accent": IG_PINK},
            {"label": "Reach", "value": f"{ov['accounts_reached']:,}"},
            {"label": "Engagement Rate", "value": f"{engagement_rate:.2f}%", "sub": f"{interactions:,} interactions / {followers:,} followers", "accent": IG_PINK},
            {"label": "Engaged Accounts", "value": f"{ov['accounts_engaged']:,}"},
            {"label": "Profile Visits", "value": f"{ov['profile_visits']:,}", "sub": f"{ov['external_link_taps']} link taps"},
        ])

        spacer(16)
        left, right = st.columns(2, gap="large")

        with left:
            section("Views by Content Type")
            views = ig["views_by_content_type"]
            views_df = pd.DataFrame([
                {"Type": "Stories", "Views": views["stories"]},
                {"Type": "Reels", "Views": views["reels"]},
                {"Type": "Posts", "Views": views["posts"]},
            ])
            fig = px.bar(views_df, x="Type", y="Views", color="Type",
                         color_discrete_map={"Stories": IG_PURPLE, "Reels": IG_PINK, "Posts": IG_ORANGE})
            apply_theme(fig, height=320, showlegend=False, xaxis_title="", yaxis_title="")
            fig.update_yaxes(tickformat=",")
            fig.update_traces(hovertemplate="%{x}<br><b>%{y:,}</b> views<extra></extra>")
            st.plotly_chart(fig, use_container_width=True, key="ig_views_type", config=PLOTLY_CONFIG)

        with right:
            section("Interactions by Content Type")
            inter = ig["interactions_by_content_type"]
            inter_df = pd.DataFrame([
                {"Type": "Reels", "Interactions": inter["reels"]},
                {"Type": "Stories", "Interactions": inter["stories"]},
                {"Type": "Posts", "Interactions": inter["posts"]},
            ])
            fig2 = px.bar(inter_df, x="Type", y="Interactions", color="Type",
                          color_discrete_map={"Stories": IG_PURPLE, "Reels": IG_PINK, "Posts": IG_ORANGE})
            apply_theme(fig2, height=320, showlegend=False, xaxis_title="", yaxis_title="")
            fig2.update_traces(hovertemplate="%{x}<br><b>%{y:,}</b> interactions<extra></extra>")
            st.plotly_chart(fig2, use_container_width=True, key="ig_inter_type", config=PLOTLY_CONFIG)

        spacer(12)
        section("Follower Active Hours (Eastern Time)")
        hours = ig["follower_active_hours"]
        # Convert UTC hours to ET
        hours_df = pd.DataFrame([
            {"Hour_ET": _utc_to_et(int(h)), "Active": v}
            for h, v in hours.items()
        ]).sort_values("Hour_ET")
        hours_df["Label"] = hours_df["Hour_ET"].apply(
            lambda h: f"{h % 12 or 12}{'AM' if h < 12 else 'PM'}"
        )

        # Find peak hours
        peak = hours_df.nlargest(3, "Active")
        peak_labels = ", ".join(peak["Label"].tolist())

        fig3 = px.bar(hours_df, x="Label", y="Active", color_discrete_sequence=[IG_PINK])
        apply_theme(fig3, height=260, xaxis_title="", yaxis_title="")
        fig3.update_traces(hovertemplate="%{x} ET<br><b>%{y:,}</b> active<extra></extra>")
        st.plotly_chart(fig3, use_container_width=True, key="ig_active_hours", config=PLOTLY_CONFIG)
        st.caption(f"Peak hours (ET): {peak_labels}")

        spacer(16)
        msg = ig["messaging"]
        kpi_row([
            {"label": "DMs Started", "value": str(msg["conversations_started"]), "accent": IG_PINK},
            {"label": "Response Rate", "value": f"{msg['response_rate']:.0%}"},
            {"label": "Avg Response Time", "value": f"{msg['avg_response_time_hours']:.1f} hrs"},
        ])

    # ── TAB B: Post Performance ──
    with tab_posts:
        years = sorted(yearly["year"].unique(), reverse=True)
        selected_year = st.selectbox("Year", years, key="ig_year_select")

        year_data = yearly[yearly["year"] == selected_year].iloc[0]
        kpi_row([
            {"label": "Posts", "value": str(int(year_data["posts"])), "accent": IG_PINK},
            {"label": "Total Likes", "value": f"{year_data['total_likes']:,}"},
            {"label": "Avg Likes", "value": f"{year_data['avg_likes']:.0f}"},
            {"label": "Top Post", "value": f"{year_data['top_likes']:,}", "sub": "likes"},
        ])

        spacer(16)
        year_monthly = monthly[monthly["month"].dt.year == selected_year].sort_values("month")
        if not year_monthly.empty:
            left, right = st.columns(2, gap="large")
            with left:
                section("Monthly Engagement")
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=year_monthly["month"].dt.strftime("%b"), y=year_monthly["likes"],
                    name="Likes", marker_color=IG_PINK,
                    hovertemplate="%{x}<br><b>%{y:,}</b> likes<extra></extra>",
                ))
                fig.add_trace(go.Scatter(
                    x=year_monthly["month"].dt.strftime("%b"), y=year_monthly["posts"] * 50,
                    name="Posts", mode="lines+markers", line=dict(color=ACCENT_BLUE, width=2),
                    yaxis="y2", hovertemplate="%{x}<br><b>%{text}</b> posts<extra></extra>",
                    text=year_monthly["posts"],
                ))
                fig.update_layout(**chart_layout(
                    height=340,
                    yaxis=dict(title="Likes"),
                    yaxis2=dict(title="Posts", overlaying="y", side="right", showgrid=False),
                    legend=dict(orientation="h", y=1.1),
                ))
                st.plotly_chart(fig, use_container_width=True, key="ig_monthly_eng", config=PLOTLY_CONFIG)

            with right:
                section("Content Type Breakdown")
                ct_fig = px.pie(content_type, values="posts", names="type", color="type",
                                color_discrete_map={"Video/Reel": IG_PINK, "Carousel": ACCENT_BLUE, "Photo": MUTED}, hole=0.45)
                apply_theme(ct_fig, height=340, showlegend=True,
                            uniformtext_minsize=10, uniformtext_mode="hide",
                            legend=dict(orientation="h", y=-0.05))
                ct_fig.update_traces(textinfo="label+percent", textfont_color="#f0f6fc",
                                     textposition="auto", insidetextorientation="radial")
                st.plotly_chart(ct_fig, use_container_width=True, key="ig_ct_pie", config=PLOTLY_CONFIG)

        spacer(12)
        left2, right2 = st.columns(2, gap="large")
        with left2:
            section("Day-of-Week Performance")
            day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            dow_sorted = dow.set_index("day").reindex(day_order).reset_index()
            fig_dow = px.bar(dow_sorted, x="day", y="avg_likes", color="avg_likes",
                             color_continuous_scale=[[0, MUTED], [1, IG_PINK]])
            apply_theme(fig_dow, height=300, coloraxis_showscale=False, xaxis_title="", yaxis_title="Avg Likes")
            fig_dow.update_traces(hovertemplate="%{x}<br>Avg <b>%{y:.0f}</b> likes<extra></extra>")
            st.plotly_chart(fig_dow, use_container_width=True, key="ig_dow", config=PLOTLY_CONFIG)

        with right2:
            section("Solo vs Collab")
            fig_sc = go.Figure()
            fig_sc.add_trace(go.Bar(
                x=["Solo (396 posts)", "Collab (55 posts)"], y=[121, 261],
                marker_color=[MUTED, IG_PINK], text=[121, 261], textposition="outside", textfont_color="#f0f6fc",
                hovertemplate="%{x}<br>Avg <b>%{y}</b> likes<extra></extra>",
            ))
            apply_theme(fig_sc, height=300, yaxis_title="Avg Likes/Post")
            st.plotly_chart(fig_sc, use_container_width=True, key="ig_solo_collab", config=PLOTLY_CONFIG)

    # ── TAB C: Top Posts ──
    with tab_top:
        section("Top 20 Posts — All Time")
        display = top_posts.copy()
        display["Link"] = display["shortcode"].apply(lambda s: f"https://instagram.com/p/{s}")
        display["Date"] = display["date"].dt.strftime("%b %d, %Y")
        display["Collab"] = display["collaborator"].fillna("Solo")

        st.dataframe(
            display[["rank", "Date", "likes", "comments", "type", "Collab", "caption_preview", "Link"]].rename(
                columns={"rank": "#", "likes": "Likes", "comments": "Comments", "type": "Type", "caption_preview": "Caption"}
            ),
            use_container_width=True, hide_index=True,
            column_config={"Link": st.column_config.LinkColumn("Post", display_text="Open")},
        )

        spacer(12)
        section("Top Post Likes by Year")
        top_by_year = top_posts.copy()
        top_by_year["year"] = top_by_year["date"].dt.year
        yearly_top = top_by_year.groupby("year")["likes"].max().reset_index()

        fig_trend = px.line(yearly_top, x="year", y="likes", markers=True, color_discrete_sequence=[IG_PINK])
        apply_theme(fig_trend, height=280, xaxis_title="", yaxis_title="Likes")
        fig_trend.update_traces(line=dict(width=3), marker=dict(size=9))
        fig_trend.update_yaxes(tickformat=",")
        st.plotly_chart(fig_trend, use_container_width=True, key="ig_top_trend", config=PLOTLY_CONFIG)

    # ── TAB D: Historical ──
    with tab_history:
        section("Year-by-Year Stats (2012–2026)")
        hist = yearly.sort_values("year", ascending=False).copy()
        hist_display = hist[["year", "posts", "total_likes", "avg_likes", "top_likes", "comments", "photos", "videos", "carousels"]].copy()
        hist_display.columns = ["Year", "Posts", "Total Likes", "Avg Likes", "Top Likes", "Comments", "Photos", "Videos", "Carousels"]
        st.dataframe(hist_display, use_container_width=True, hide_index=True)

        spacer(12)
        left, right = st.columns(2, gap="large")
        with left:
            section("Posting Frequency")
            fig_freq = px.bar(yearly.sort_values("year"), x="year", y="posts", color_discrete_sequence=[IG_PINK])
            apply_theme(fig_freq, height=320, xaxis_title="", yaxis_title="Posts")
            fig_freq.update_traces(hovertemplate="%{x}<br><b>%{y}</b> posts<extra></extra>")
            st.plotly_chart(fig_freq, use_container_width=True, key="ig_freq", config=PLOTLY_CONFIG)

        with right:
            section("Content Format Evolution")
            format_data = yearly.sort_values("year")[["year", "photos", "videos", "carousels"]].copy()
            fig_fmt = go.Figure()
            fig_fmt.add_trace(go.Bar(x=format_data["year"], y=format_data["photos"], name="Photos", marker_color=MUTED))
            fig_fmt.add_trace(go.Bar(x=format_data["year"], y=format_data["videos"], name="Videos/Reels", marker_color=IG_PINK))
            fig_fmt.add_trace(go.Bar(x=format_data["year"], y=format_data["carousels"], name="Carousels", marker_color=ACCENT_BLUE))
            apply_theme(fig_fmt, height=320, barmode="stack", xaxis_title="", yaxis_title="Posts",
                        legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_fmt, use_container_width=True, key="ig_format_evo", config=PLOTLY_CONFIG)
