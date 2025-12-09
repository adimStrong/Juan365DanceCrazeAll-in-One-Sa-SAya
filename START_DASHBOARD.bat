@echo off
title Video Engagement Dashboard
color 0A

echo ============================================================
echo    VIDEO ENGAGEMENT DASHBOARD
echo    Reading data from Google Sheets (FB, IG, TikTok)
echo ============================================================
echo.

cd /d "%~dp0"

echo Starting Streamlit dashboard...
echo.
echo Dashboard will open at: http://localhost:8501
echo Press Ctrl+C to stop the server.
echo.

python -m streamlit run streamlit_app.py

pause
