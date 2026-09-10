@echo off
setlocal
title note記事同期 - My Tools

echo ========================================================
echo   [SYNC] noteマガジンから最新の公開ツールを同期します
echo ========================================================
echo.

python "%~dp0scripts\sync_tools.py"
if errorlevel 1 (
    echo.
    echo [ERROR] 記事の同期処理でエラーが発生しました。
    echo コミットおよびプッシュは中止します。
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   [GIT] 変更の有無を確認しています...
echo ========================================================
echo.

git diff --quiet "%~dp0data\tools.json" "%~dp0index.html" "%~dp0sitemap.xml"
if not errorlevel 1 (
    echo 変更はありませんでした。ローカルおよびリモートは最新状態です。
    echo.
    echo ========================================================
    echo   同期処理が完了しました。
    echo ========================================================
    echo.
    pause
    exit /b 0
)

echo 更新されたファイルが検出されました。
echo GitHub へのコミットおよびプッシュを実行します...
echo.

git add "%~dp0data\tools.json" "%~dp0index.html" "%~dp0sitemap.xml"
if errorlevel 1 (
    echo [ERROR] git add に失敗しました。
    pause
    exit /b 1
)

git commit -m "chore: note記事同期による公開ツール情報の更新 (%DATE%)"
if errorlevel 1 (
    echo [ERROR] git commit に失敗しました。
    pause
    exit /b 1
)

echo.
echo リモートリポジトリ (origin/main) へプッシュ中...
git push origin main
if errorlevel 1 (
    echo.
    echo [ERROR] git push に失敗しました。ネットワーク接続等をご確認ください。
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   同期およびGitHubへのプッシュが完了しました。
echo   GitHub Pages の自動デプロイが開始されます。
echo ========================================================
echo.
pause
