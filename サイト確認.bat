@echo off
title My Tools - ローカルプレビュー

echo ========================================================
echo   My Tools カタログサイトをローカルで起動しています...
echo   ブラウザで http://localhost:8085 を開きます
echo ========================================================
echo.

start "" "http://localhost:8085"
python -m http.server 8085
