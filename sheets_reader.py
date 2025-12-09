"""
Google Sheets Reader
Reads engagement data from Google Sheets for the dashboard.
Supports both local credentials.json and Streamlit Cloud secrets.
"""

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import os
import re
from config import SHEET_ID, SCOPES, CREDENTIALS_FILE


def get_client():
    """
    Get authenticated Google Sheets client.
    Supports:
    1. Streamlit Cloud secrets (st.secrets["gcp_service_account"])
    2. Local credentials.json file
    """
    # Try Streamlit secrets first (for Streamlit Cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=SCOPES
            )
            client = gspread.authorize(creds)
            return client
    except Exception:
        pass  # Fall back to local credentials

    # Fall back to local credentials.json
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(
            f"credentials.json not found!\n\n"
            f"Please copy credentials.json from fb_video_scraper project,\n"
            f"or configure Streamlit Cloud secrets."
        )

    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client


def detect_platform(url):
    """Detect platform from video URL."""
    if not url:
        return 'Unknown'
    url_lower = url.lower()
    if 'facebook.com' in url_lower or 'fb.com' in url_lower:
        return 'Facebook'
    elif 'instagram.com' in url_lower:
        return 'Instagram'
    elif 'tiktok.com' in url_lower:
        return 'TikTok'
    elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'YouTube'
    return 'Other'


def find_columns(header_row):
    """Auto-detect column positions from header row."""
    columns = {
        'content_creator': None,
        'video_link': None,
        'reactions': None,
        'comments': None,
        'shares': None,
        'views': None,
    }

    for idx, col in enumerate(header_row):
        col_lower = col.lower().strip()

        # Content creator column (usually first column)
        if idx == 0 and ('creator' in col_lower or 'name' in col_lower or 'content' in col_lower):
            columns['content_creator'] = idx
        elif idx == 0:
            columns['content_creator'] = idx  # Assume first column is creator

        # Video link column
        if 'video' in col_lower and 'link' in col_lower:
            columns['video_link'] = idx
        elif 'link' in col_lower and columns['video_link'] is None:
            columns['video_link'] = idx
        elif 'url' in col_lower and columns['video_link'] is None:
            columns['video_link'] = idx

        # Reactions/Likes column
        if 'reaction' in col_lower or 'like' in col_lower:
            columns['reactions'] = idx

        # Comments column
        if 'comment' in col_lower:
            columns['comments'] = idx

        # Shares column
        if 'share' in col_lower:
            columns['shares'] = idx

        # Views column (TikTok only)
        if 'view' in col_lower or 'play' in col_lower:
            columns['views'] = idx

    return columns


def parse_number(value):
    """Parse a number from string, handling K/M suffixes."""
    if not value:
        return 0
    if isinstance(value, (int, float)):
        return int(value)

    value = str(value).strip().replace(',', '')

    # Handle K (thousands) and M (millions) suffixes
    multiplier = 1
    if value.endswith('K') or value.endswith('k'):
        multiplier = 1000
        value = value[:-1]
    elif value.endswith('M') or value.endswith('m'):
        multiplier = 1000000
        value = value[:-1]

    try:
        return int(float(value) * multiplier)
    except (ValueError, TypeError):
        return 0


def read_all_data():
    """
    Read all engagement data from all sheets.
    Returns a pandas DataFrame with all data.
    """
    client = get_client()
    spreadsheet = client.open_by_key(SHEET_ID)
    sheets = spreadsheet.worksheets()

    all_data = []

    for sheet in sheets:
        all_values = sheet.get_all_values()

        if len(all_values) < 2:
            continue

        # Find header row
        header_row_idx = 0
        for idx, row in enumerate(all_values):
            row_text = ' '.join(row).lower()
            if 'link' in row_text or 'url' in row_text:
                header_row_idx = idx
                break

        # Auto-detect columns
        header_row = all_values[header_row_idx]
        columns = find_columns(header_row)

        if columns.get('video_link') is None:
            continue

        # Process data rows
        for row in all_values[header_row_idx + 1:]:
            if len(row) <= columns['video_link']:
                continue

            video_link = row[columns['video_link']] if columns['video_link'] is not None else ''

            # Skip empty rows
            if not video_link or not video_link.strip():
                continue

            # Skip non-video URLs
            if 'http' not in video_link.lower():
                continue

            content_creator = row[columns['content_creator']] if columns['content_creator'] is not None and len(row) > columns['content_creator'] else ''
            reactions = parse_number(row[columns['reactions']]) if columns['reactions'] is not None and len(row) > columns['reactions'] else 0
            comments = parse_number(row[columns['comments']]) if columns['comments'] is not None and len(row) > columns['comments'] else 0
            shares = parse_number(row[columns['shares']]) if columns['shares'] is not None and len(row) > columns['shares'] else 0
            views = parse_number(row[columns['views']]) if columns['views'] is not None and len(row) > columns['views'] else 0

            platform = detect_platform(video_link)
            engagement = reactions + comments + shares

            all_data.append({
                'sheet': sheet.title,
                'content_creator': content_creator,
                'video_link': video_link.strip(),
                'platform': platform,
                'reactions': reactions,
                'comments': comments,
                'shares': shares,
                'views': views,
                'engagement': engagement,
            })

    df = pd.DataFrame(all_data)
    return df


def get_summary_stats(df):
    """Get summary statistics from the data."""
    if df.empty:
        return {
            'total_posts': 0,
            'total_reactions': 0,
            'total_comments': 0,
            'total_shares': 0,
            'total_views': 0,
            'total_engagement': 0,
            'platforms': {},
            'creators': [],
        }

    return {
        'total_posts': len(df),
        'total_reactions': df['reactions'].sum(),
        'total_comments': df['comments'].sum(),
        'total_shares': df['shares'].sum(),
        'total_views': df['views'].sum() if 'views' in df.columns else 0,
        'total_engagement': df['engagement'].sum(),
        'platforms': df['platform'].value_counts().to_dict(),
        'creators': df['content_creator'].unique().tolist(),
    }


if __name__ == '__main__':
    print("Testing Google Sheets connection...")
    print()

    try:
        df = read_all_data()
        print(f"Loaded {len(df)} rows")
        print()
        print("Summary:")
        stats = get_summary_stats(df)
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print()
        print("Sample data:")
        print(df.head())
    except Exception as e:
        print(f"Error: {e}")
