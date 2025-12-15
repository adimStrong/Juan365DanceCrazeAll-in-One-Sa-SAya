"""
Google Sheets Dashboard Configuration
"""

# Google Sheet ID (from fb_video_scraper project)
SHEET_ID = '1GB-FfBOykCuXUwbz6Mpp7-JyWSMgK-5jtoPc3xV86_w'

# Google Sheets API scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

# Credentials file path
CREDENTIALS_FILE = 'credentials.json'

# Dashboard settings
DASHBOARD_TITLE = "Video Engagement Dashboard"

# Sheets to exclude from dashboard
EXCLUDED_SHEETS = ['Employee Edition']
