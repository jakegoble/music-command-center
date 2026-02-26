"""Instagram — Complete IG analytics with sub-tabs."""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

IG_PINK = "#E1306C"
IG_PURPLE = "#833AB4"
IG_ORANGE = "#F77737"
ACCENT_BLUE = "#58a6ff"
MUTED = "#8b949e"
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#f0f6fc", family="system-ui, -apple-system, sans-serif"),
    margin=dict(l=0, r=0, t=40, b=0),
    hoverlabel=dict(bgcolor="#21262d", font_color="#f0f6fc"),
)


def render() -> None:
    from data_loader import (
        load_ig_insights,
        load_ig_yearly,
        load_ig_monthly,
        load_ig_top_posts,
        load_ig_content_type,
        load_ig_day_of_week,
    )

    ig = load_ig_insights()
    yearly = load_ig_yearly()
    monthly = load_ig_monthly()
    top_posts = load_ig_top_posts()
    content_type = load_ig_content_type()
    dow = load_ig_day_of_week()

    st.markdown("# 📱 Instagram")
    st.caption(f"@jakke · {ig['account']['followers']:,} followers · {ig['account']['posts_count']:,} posts")

    tab_overview, tab_posts, tab_top, tab_history = st.tabs(["Overview (30d)", "Post Performance", "Top Posts", "Historical"])

    # =====================================================================
    # TAB A: Overview (30-day)
    # =====================================================================
    with tab_overview:
        ov = ig["overview"]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Views", f"{ov['views_30d']:,}")
        c2.metric("Reach", f"{ov['accounts_reached']:,}")
        c3.metric("Interactions", f"{ov['interactions']:,}")
        c4.metric("Engaged", f"{ov['accounts_engaged']:,}")
        c5.metric("Profile Visits", f"{ov['profile_visits']:,}")

        st.divider()

        left, right = st.columns(2)

        with left:
            st.markdown('<p class="section-header">Views by Content Type</p>', unsafe_allow_html=True)
            views = ig["views_by_content_type"]
            views_df = pd.DataFrame([
                {"Type": "Stories", "Views": views["stories"]},
                {"Type": "Reels", "Views": views["reels"]},
                {"Type": "Posts", "Views": views["posts"]},
            ])
            fig = px.bar(
                views_df, x="Type", y="Views",
                color="Type",
                color_discrete_map={"Stories": IG_PURPLE, "Reels": IG_PINK, "Posts": IG_ORANGE},
            )
            fig.update_layout(**PLOTLY_LAYOUT, height=350, showlegend=False, xaxis_title="", yaxis_title="Views")
            fig.update_traces(hovertemplate="%{x}<br>%{y:,} views<extra></extra>")
            st.plotly_chart(fig, use_container_width=True, key="ig_views_type")

        with right:
            st.markdown('<p class="section-header">Interactions by Content Type</p>', unsafe_allow_html=True)
            inter = ig["interactions_by_content_type"]
            inter_df = pd.DataFrame([
                {"Type": "Reels", "Interactions": inter["reels"]},
                {"Type": "Stories", "Interactions": inter["stories"]},
                {"Type": "Posts", "Interactions": inter["posts"]},
            ])
            fig2 = px.bar(
                inter_df, x="Type", y="Interactions",
                color="Type",
                color_discrete_map={"Stories": IG_PURPLE, "Reels": IG_PINK, "Posts": IG_ORANGE},
            )
            fig2.update_layout(**PLOTLY_LAYOUT, height=350, showlegend=False, xaxis_title="", yaxis_title="Interactions")
            fig2.update_traces(hovertemplate="%{x}<br>%{y:,} interactions<extra></extra>")
            st.plotly_chart(fig2, use_container_width=True, key="ig_inter_type")

        st.divider()

        # Follower active hours
        st.markdown('<p class="section-header">Follower Active Hours</p>', unsafe_allow_html=True)
        hours = ig["follower_active_hours"]
        hours_df = pd.DataFrame([{"Hour": int(h), "Active Followers": v} for h, v in hours.items()])
        hours_df = hours_df.sort_values("Hour")
        hours_df["Label"] = hours_df["Hour"].apply(lambda h: f"{h}:00")

        fig3 = px.bar(hours_df, x="Label", y="Active Followers", color_discrete_sequence=[IG_PINK])
        fig3.update_layout(**PLOTLY_LAYOUT, height=300, xaxis_title="Hour (UTC)", yaxis_title="Active Followers")
        fig3.update_traces(hovertemplate="%{x}<br>%{y:,} active<extra></extra>")
        st.plotly_chart(fig3, use_container_width=True, key="ig_active_hours")

        # Messaging stats
        st.divider()
        m1, m2, m3 = st.columns(3)
        msg = ig["messaging"]
        m1.metric("Conversations Started", f"{msg['conversations_started']}")
        m2.metric("Response Rate", f"{msg['response_rate']:.1%}")
        m3.metric("Avg Response Time", f"{msg['avg_response_time_hours']:.1f} hrs")

    # =====================================================================
    # TAB B: Post Performance
    # =====================================================================
    with tab_posts:
        # Year selector
        years = sorted(yearly["year"].unique(), reverse=True)
        selected_year = st.selectbox("Year", years, key="ig_year_select")

        year_data = yearly[yearly["year"] == selected_year].iloc[0]
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Posts", f"{year_data['posts']}")
        p2.metric("Total Likes", f"{year_data['total_likes']:,}")
        p3.metric("Avg Likes", f"{year_data['avg_likes']:.0f}")
        p4.metric("Top Post Likes", f"{year_data['top_likes']:,}")

        st.divider()

        # Monthly engagement for selected year
        year_monthly = monthly[monthly["month"].dt.year == selected_year].sort_values("month")
        if not year_monthly.empty:
            left, right = st.columns(2)
            with left:
                st.markdown('<p class="section-header">Monthly Engagement</p>', unsafe_allow_html=True)
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=year_monthly["month"].dt.strftime("%b"),
                    y=year_monthly["likes"],
                    name="Total Likes",
                    marker_color=IG_PINK,
                    hovertemplate="%{x}<br>%{y:,} likes<extra></extra>",
                ))
                fig.add_trace(go.Scatter(
                    x=year_monthly["month"].dt.strftime("%b"),
                    y=year_monthly["posts"] * 50,  # scale for visibility
                    name="Posts (scaled)",
                    mode="lines+markers",
                    line=dict(color=ACCENT_BLUE, width=2),
                    yaxis="y2",
                    hovertemplate="%{x}<br>%{text} posts<extra></extra>",
                    text=year_monthly["posts"],
                ))
                fig.update_layout(
                    **PLOTLY_LAYOUT,
                    height=350,
                    yaxis=dict(title="Total Likes"),
                    yaxis2=dict(title="Posts", overlaying="y", side="right", showgrid=False),
                    legend=dict(orientation="h", y=1.1),
                )
                st.plotly_chart(fig, use_container_width=True, key="ig_monthly_eng")

            with right:
                st.markdown('<p class="section-header">Content Type Breakdown</p>', unsafe_allow_html=True)
                ct_fig = px.pie(
                    content_type, values="posts", names="type",
                    color="type",
                    color_discrete_map={"Video/Reel": IG_PINK, "Carousel": ACCENT_BLUE, "Photo": MUTED},
                    hole=0.4,
                )
                ct_fig.update_layout(**PLOTLY_LAYOUT, height=350, showlegend=True, legend=dict(orientation="h", y=-0.1))
                ct_fig.update_traces(textinfo="label+percent", textfont_color="#f0f6fc")
                st.plotly_chart(ct_fig, use_container_width=True, key="ig_ct_pie")

        st.divider()

        # Day-of-week heatmap
        left2, right2 = st.columns(2)
        with left2:
            st.markdown('<p class="section-header">Day-of-Week Performance</p>', unsafe_allow_html=True)
            day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            dow_sorted = dow.set_index("day").reindex(day_order).reset_index()
            fig_dow = px.bar(
                dow_sorted, x="day", y="avg_likes",
                color="avg_likes",
                color_continuous_scale=[[0, MUTED], [1, IG_PINK]],
            )
            fig_dow.update_layout(**PLOTLY_LAYOUT, height=300, coloraxis_showscale=False, xaxis_title="", yaxis_title="Avg Likes")
            fig_dow.update_traces(hovertemplate="%{x}<br>Avg %{y:.0f} likes<extra></extra>")
            st.plotly_chart(fig_dow, use_container_width=True, key="ig_dow")

        with right2:
            st.markdown('<p class="section-header">Solo vs Collab</p>', unsafe_allow_html=True)
            solo_collab = pd.DataFrame([
                {"Type": "Solo", "Posts": 396, "Avg Likes": 121},
                {"Type": "Collab", "Posts": 55, "Avg Likes": 261},
            ])
            fig_sc = px.bar(
                solo_collab, x="Type", y="Avg Likes",
                color="Type",
                color_discrete_map={"Solo": MUTED, "Collab": IG_PINK},
                text="Avg Likes",
            )
            fig_sc.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=False, xaxis_title="", yaxis_title="Avg Likes/Post")
            fig_sc.update_traces(textposition="outside", textfont_color="#f0f6fc")
            st.plotly_chart(fig_sc, use_container_width=True, key="ig_solo_collab")

    # =====================================================================
    # TAB C: Top Posts
    # =====================================================================
    with tab_top:
        st.markdown('<p class="section-header">Top 20 Posts — All Time</p>', unsafe_allow_html=True)

        display = top_posts.copy()
        display["Link"] = display["shortcode"].apply(lambda s: f"https://instagram.com/p/{s}")
        display["Date"] = display["date"].dt.strftime("%b %d, %Y")
        display["Collab"] = display["collaborator"].fillna("Solo")

        st.dataframe(
            display[["rank", "Date", "likes", "comments", "type", "Collab", "caption_preview", "Link"]].rename(
                columns={"rank": "#", "likes": "Likes", "comments": "Comments", "type": "Type", "caption_preview": "Caption"}
            ),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Link": st.column_config.LinkColumn("Post Link", display_text="Open"),
            },
        )

        st.divider()

        # Engagement trend by year (top posts)
        st.markdown('<p class="section-header">Engagement Trend — Top Posts by Year</p>', unsafe_allow_html=True)
        top_by_year = top_posts.copy()
        top_by_year["year"] = top_by_year["date"].dt.year
        yearly_top = top_by_year.groupby("year")["likes"].max().reset_index()

        fig_trend = px.line(
            yearly_top, x="year", y="likes",
            markers=True,
            color_discrete_sequence=[IG_PINK],
        )
        fig_trend.update_layout(**PLOTLY_LAYOUT, height=300, xaxis_title="Year", yaxis_title="Top Post Likes")
        fig_trend.update_traces(line=dict(width=3), marker=dict(size=10))
        st.plotly_chart(fig_trend, use_container_width=True, key="ig_top_trend")

    # =====================================================================
    # TAB D: Historical
    # =====================================================================
    with tab_history:
        st.markdown('<p class="section-header">Year-by-Year Stats (2012–2026)</p>', unsafe_allow_html=True)

        hist = yearly.sort_values("year", ascending=False).copy()
        hist_display = hist[["year", "posts", "total_likes", "avg_likes", "top_likes", "comments", "photos", "videos", "carousels"]].copy()
        hist_display.columns = ["Year", "Posts", "Total Likes", "Avg Likes", "Top Likes", "Comments", "Photos", "Videos", "Carousels"]
        st.dataframe(hist_display, use_container_width=True, hide_index=True)

        st.divider()

        # Posting frequency timeline
        left, right = st.columns(2)
        with left:
            st.markdown('<p class="section-header">Posting Frequency</p>', unsafe_allow_html=True)
            fig_freq = px.bar(
                yearly.sort_values("year"), x="year", y="posts",
                color_discrete_sequence=[IG_PINK],
            )
            fig_freq.update_layout(**PLOTLY_LAYOUT, height=350, xaxis_title="Year", yaxis_title="Posts")
            fig_freq.update_traces(hovertemplate="Year %{x}<br>%{y} posts<extra></extra>")
            st.plotly_chart(fig_freq, use_container_width=True, key="ig_freq")

        with right:
            st.markdown('<p class="section-header">Content Format Evolution</p>', unsafe_allow_html=True)
            format_data = yearly.sort_values("year")[["year", "photos", "videos", "carousels"]].copy()
            fig_fmt = go.Figure()
            fig_fmt.add_trace(go.Bar(x=format_data["year"], y=format_data["photos"], name="Photos", marker_color=MUTED))
            fig_fmt.add_trace(go.Bar(x=format_data["year"], y=format_data["videos"], name="Videos/Reels", marker_color=IG_PINK))
            fig_fmt.add_trace(go.Bar(x=format_data["year"], y=format_data["carousels"], name="Carousels", marker_color=ACCENT_BLUE))
            fig_fmt.update_layout(**PLOTLY_LAYOUT, height=350, barmode="stack", xaxis_title="Year", yaxis_title="Posts", legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_fmt, use_container_width=True, key="ig_format_evo")
