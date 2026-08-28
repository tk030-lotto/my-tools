@echo off
chcp 65001 > nul
title My Tools - ローカルプレビューサーバー

echo ========================================================
echo   My Tools カタログサイトをローカルで起動しています...
echo   ブラウザで http://localhost:8085 を開きます
echo ========================================================
echo.
echo [サーバー停止方法] このウィンドウを閉じるか Ctrl + C を押してください。
echo.

start "" "http://localhost:8085"
python -m http.server 8085
