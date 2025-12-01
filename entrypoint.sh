#!/bin/sh
# Copy cookies.txt to a working location before starting the app
# This prevents yt-dlp from corrupting the original mounted file
cp /usr/src/ythls-FastAPI/cookies.txt /usr/src/ythls-FastAPI/cookies_work.txt 2>/dev/null || true
exec python3 basla.py
