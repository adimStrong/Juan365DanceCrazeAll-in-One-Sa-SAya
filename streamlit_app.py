"""
Video Engagement Dashboard
Displays engagement data from Google Sheets (FB, IG, TikTok)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sheets_reader import read_all_data, get_summary_stats
from config import DASHBOARD_TITLE

# Page config
st.set_page_config(
    page_title=DASHBOARD_TITLE,
    page_icon="📊",
    layout="wide"
)

def format_number(num):
    """Format large numbers with K/M suffix."""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(int(num))


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    """Load data from Google Sheets with caching."""
    return read_all_data()


def main():
    st.title(f"📊 {DASHBOARD_TITLE}")

    # Load data
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Make sure credentials.json is in the project folder and the service account has access to the Google Sheet.")
        return

    if df.empty:
        st.warning("No data found in the Google Sheet.")
        return

    # Sidebar filters
    st.sidebar.header("Filters")

    # Platform filter
    platforms = ['All'] + sorted(df['platform'].unique().tolist())
    selected_platform = st.sidebar.selectbox("Platform", platforms)

    # Content creator filter
    creators = ['All'] + sorted([c for c in df['content_creator'].unique() if c])
    selected_creator = st.sidebar.selectbox("Content Creator", creators)

    # Sheet filter
    sheets = ['All'] + sorted(df['sheet'].unique().tolist())
    selected_sheet = st.sidebar.selectbox("Sheet", sheets)

    # Apply filters
    filtered_df = df.copy()
    if selected_platform != 'All':
        filtered_df = filtered_df[filtered_df['platform'] == selected_platform]
    if selected_creator != 'All':
        filtered_df = filtered_df[filtered_df['content_creator'] == selected_creator]
    if selected_sheet != 'All':
        filtered_df = filtered_df[filtered_df['sheet'] == selected_sheet]

    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    # Summary metrics
    stats = get_summary_stats(filtered_df)

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Total Posts", format_number(stats['total_posts']))
    with col2:
        st.metric("Total Reactions", format_number(stats['total_reactions']))
    with col3:
        st.metric("Total Comments", format_number(stats['total_comments']))
    with col4:
        st.metric("Total Shares", format_number(stats['total_shares']))
    with col5:
        st.metric("Total Views", format_number(stats.get('total_views', 0)))
    with col6:
        st.metric("Total Engagement", format_number(stats['total_engagement']))

    st.divider()

    # Charts row
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Platform Distribution")
        if not filtered_df.empty:
            platform_counts = filtered_df['platform'].value_counts()
            fig = px.pie(
                values=platform_counts.values,
                names=platform_counts.index,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📊 Engagement by Platform")
        if not filtered_df.empty:
            platform_engagement = filtered_df.groupby('platform').agg({
                'reactions': 'sum',
                'comments': 'sum',
                'shares': 'sum'
            }).reset_index()

            fig = px.bar(
                platform_engagement,
                x='platform',
                y=['reactions', 'comments', 'shares'],
                barmode='group',
                color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
            )
            fig.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                xaxis_title="",
                yaxis_title="Count",
                legend_title=""
            )
            st.plotly_chart(fig, use_container_width=True)

    # Top performers
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Top Creators by Engagement")
        if not filtered_df.empty and filtered_df['content_creator'].str.strip().any():
            creator_engagement = filtered_df[filtered_df['content_creator'].str.strip() != ''].groupby('content_creator').agg({
                'engagement': 'sum',
                'video_link': 'count'
            }).rename(columns={'video_link': 'posts'}).sort_values('engagement', ascending=False).head(10)

            fig = px.bar(
                creator_engagement.reset_index(),
                x='engagement',
                y='content_creator',
                orientation='h',
                color='engagement',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                xaxis_title="Total Engagement",
                yaxis_title="",
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📹 Top Posts by Engagement")
        if not filtered_df.empty:
            top_posts = filtered_df.nlargest(10, 'engagement')[['content_creator', 'platform', 'reactions', 'comments', 'shares', 'views', 'engagement', 'video_link']]

            # Make video links clickable
            def make_clickable(url):
                if pd.isna(url) or not url:
                    return ""
                short_url = url[:40] + "..." if len(url) > 40 else url
                return f'<a href="{url}" target="_blank">{short_url}</a>'

            # Show views for platforms that have them
            def format_views(row):
                if row['views'] > 0:
                    return f"{row['views']:,}"
                return '-'

            display_df = top_posts.copy()
            display_df['views'] = display_df.apply(format_views, axis=1)
            display_df['video_link'] = display_df['video_link'].apply(make_clickable)

            st.write(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)

    # ===== FACEBOOK VIEWS SECTION =====
    st.divider()
    st.subheader("📘 Facebook Views")

    # Filter Facebook only with views > 0
    fb_df = filtered_df[(filtered_df['platform'] == 'Facebook') & (filtered_df['views'] > 0)]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🏆 Top Creators by Views (Facebook)**")
        if not fb_df.empty:
            fb_creator_views = fb_df.groupby('content_creator').agg({
                'views': 'sum',
                'video_link': 'count'
            }).rename(columns={'video_link': 'videos'}).sort_values('views', ascending=False).head(10)

            fig = px.bar(
                fb_creator_views.reset_index(),
                x='views',
                y='content_creator',
                orientation='h',
                color='views',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                xaxis_title="Total Views",
                yaxis_title="",
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)

            # Show stats
            total_fb_views = fb_df['views'].sum()
            st.success(f"📊 Total Facebook Views: **{total_fb_views:,}** from **{len(fb_df)}** videos")
        else:
            st.info("No Facebook views data available yet. Run the scraper to collect views.")

    with col2:
        st.markdown("**📹 Top 10 Videos by Views (Facebook)**")
        if not fb_df.empty:
            top_fb_views = fb_df.nlargest(10, 'views')[['content_creator', 'views', 'reactions', 'comments', 'shares', 'video_link']]

            # Make video links clickable
            def make_link(url):
                if pd.isna(url) or not url:
                    return ""
                short_url = url[:35] + "..." if len(url) > 35 else url
                return f'<a href="{url}" target="_blank">{short_url}</a>'

            display_fb_views = top_fb_views.copy()
            display_fb_views['video_link'] = display_fb_views['video_link'].apply(make_link)
            display_fb_views['views'] = display_fb_views['views'].apply(lambda x: f"{x:,}")

            st.write(display_fb_views.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("No Facebook views data available yet. Run the scraper to collect views.")

    # ===== TIKTOK VIEWS SECTION =====
    st.divider()
    st.subheader("🎵 TikTok Views")

    # Filter TikTok only with views > 0
    tiktok_df = filtered_df[(filtered_df['platform'] == 'TikTok') & (filtered_df['views'] > 0)]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🏆 Top Creators by Views (TikTok)**")
        if not tiktok_df.empty:
            creator_views = tiktok_df.groupby('content_creator').agg({
                'views': 'sum',
                'video_link': 'count'
            }).rename(columns={'video_link': 'videos'}).sort_values('views', ascending=False).head(10)

            fig = px.bar(
                creator_views.reset_index(),
                x='views',
                y='content_creator',
                orientation='h',
                color='views',
                color_continuous_scale='Purples'
            )
            fig.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                xaxis_title="Total Views",
                yaxis_title="",
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)

            # Show stats
            total_tiktok_views = tiktok_df['views'].sum()
            st.success(f"📊 Total TikTok Views: **{total_tiktok_views:,}** from **{len(tiktok_df)}** videos")
        else:
            st.info("No TikTok views data available yet. Run the scraper to collect views.")

    with col2:
        st.markdown("**📹 Top 10 Videos by Views (TikTok)**")
        if not tiktok_df.empty:
            top_views = tiktok_df.nlargest(10, 'views')[['content_creator', 'views', 'reactions', 'comments', 'shares', 'video_link']]

            # Make video links clickable
            def make_link(url):
                if pd.isna(url) or not url:
                    return ""
                short_url = url[:35] + "..." if len(url) > 35 else url
                return f'<a href="{url}" target="_blank">{short_url}</a>'

            display_views = top_views.copy()
            display_views['video_link'] = display_views['video_link'].apply(make_link)
            display_views['views'] = display_views['views'].apply(lambda x: f"{x:,}")

            st.write(display_views.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("No TikTok views data available yet. Run the scraper to collect views.")

    # ===== VIEWS COMPARISON =====
    st.divider()
    st.subheader("📊 Views Comparison by Platform")

    # Get views data for both platforms
    views_by_platform = filtered_df[filtered_df['views'] > 0].groupby('platform').agg({
        'views': 'sum',
        'video_link': 'count'
    }).rename(columns={'video_link': 'videos'}).reset_index()

    if not views_by_platform.empty:
        col1, col2 = st.columns(2)

        with col1:
            fig = px.pie(
                views_by_platform,
                values='views',
                names='platform',
                title='Total Views Distribution',
                color_discrete_sequence=['#4267B2', '#000000', '#E1306C']  # FB blue, TikTok black, IG pink
            )
            fig.update_layout(margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Top 10 Views - All Platforms Combined
            st.markdown("**🏆 Top 10 by Views (All Platforms)**")
            top_views_all = filtered_df[filtered_df['views'] > 0].nlargest(10, 'views')[['content_creator', 'platform', 'views', 'reactions', 'video_link']]
            if not top_views_all.empty:
                top_display = top_views_all.copy()
                top_display['Rank'] = range(1, len(top_display) + 1)
                top_display['views'] = top_display['views'].apply(lambda x: f"{x:,}")
                top_display['reactions'] = top_display['reactions'].apply(lambda x: f"{x:,}")
                top_display = top_display[['Rank', 'content_creator', 'platform', 'views', 'reactions']]
                top_display.columns = ['#', 'Creator', 'Platform', 'Views', 'Reactions']
                st.dataframe(top_display, hide_index=True, use_container_width=True)
            else:
                st.info("No views data available")
    else:
        st.info("No views data available yet. Run the scraper to collect views from Facebook and TikTok.")

    # All posts table
    st.divider()
    st.subheader("📋 All Posts")

    # Sortable dataframe
    if not filtered_df.empty:
        display_cols = ['content_creator', 'platform', 'sheet', 'reactions', 'comments', 'shares', 'views', 'engagement', 'video_link']
        display_df = filtered_df[display_cols].sort_values('engagement', ascending=False).copy()

        # Show views for all platforms that have them
        display_df['views'] = display_df['views'].apply(
            lambda x: x if x > 0 else '-'
        )

        st.dataframe(
            display_df,
            column_config={
                "content_creator": "Creator",
                "platform": "Platform",
                "sheet": "Sheet",
                "reactions": st.column_config.NumberColumn("Reactions", format="%d"),
                "comments": st.column_config.NumberColumn("Comments", format="%d"),
                "shares": st.column_config.NumberColumn("Shares", format="%d"),
                "views": st.column_config.TextColumn("Views"),
                "engagement": st.column_config.NumberColumn("Total", format="%d"),
                "video_link": st.column_config.LinkColumn("Video Link", display_text="Open")
            },
            height=600,
            use_container_width=True,
            hide_index=True
        )

    # Footer
    st.divider()
    st.caption(f"Data source: Google Sheets | {len(filtered_df)} posts displayed")


if __name__ == "__main__":
    main()
