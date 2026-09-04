#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_tools.py - noteマガジンおよび公開情報からツール一覧（tools.json）を自動同期・更新するスクリプト

機能:
1. noteマガジンAPIから最新記事一覧を取得
2. ロト系・有料記事・メンバーシップ記事・非公開記事を自動除外
3. 単体記事APIから本文を取得し、GitHub URLやWeb版URL（GitHub Pages）を自動抽出
4. 公開日（publish_at）を正確にフォーマット（YYYY-MM-DD）
5. 既存データを破壊せず、安全に新規追加・補完マージ

使用方法:
    python scripts/sync_tools.py
"""

import json
import os
import re
import sys
import urllib.request

# WindowsコンソールのUTF-8文字化け対策
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

MAGAZINE_API_URL = "https://note.com/api/v1/magazines/m94b759b541f6/notes"
NOTE_DETAIL_API_BASE = "https://note.com/api/v3/notes"
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "tools.json")

# 除外キーワード（ロト系、メンバーシップ、未公開・凍結など）
EXCLUDE_KEYWORDS_TITLE = [
    "ビンゴ5", "ナンバーズ", "NUMBERS", "BINGO",
    "メンバーシップ限定", "会員限定", "凍結", "アーカイブ"
]

def fetch_json(url):
    """URLからJSONデータを取得"""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    with urllib.request.urlopen(req, timeout=10) as res:
        return json.loads(res.read().decode("utf-8"))

def fetch_note_detail(key):
    """単体記事の詳細（本文やリンク等）を取得"""
    url = f"{NOTE_DETAIL_API_BASE}/{key}"
    try:
        data = fetch_json(url)
        return data.get("data", {})
    except Exception as e:
        print(f"[WARN] 記事詳細取得スキップ ({key}): {e}")
        return {}

def is_excluded(title, body=""):
    """除外対象かどうかの判定"""
    # 1. タイトルの除外判定
    for kw in EXCLUDE_KEYWORDS_TITLE:
        if kw in title:
            return True

    # タイトルのロト判定（「プロトコル」「プロトタイプ」等の誤爆を回避）
    if re.search(r'(?<!プ)ロト(?!コル|タイプ)', title):
        return True

    # 2. 本文の除外判定（宝くじ関連の文脈のみ除外）
    if body:
        # ロトくじ判定（「当選」「買い目」「くじ」「予想」と共起する場合のみ）
        if re.search(r'(?<!プ)ロト(?!コル|タイプ)', body) and re.search(r'当選|買い目|くじ|予想', body):
            return True
        if re.search(r'ビンゴ5|ナンバーズ', body) and re.search(r'当選|買い目|くじ|予想', body):
            return True
        if "メンバーシップ限定記事" in body:
            return True

    return False

def extract_urls_from_body(body):
    """記事本文からGitHub URLおよびWeb版（GitHub Pages）URLを抽出"""
    github_url = ""
    web_url = ""

    # href内のURLを抽出
    links = re.findall(r'href="([^"]+)"', body)
    
    # プレーンテキスト内のURLも抽出
    plain_urls = re.findall(r'https?://[^\s<>"]+', body)
    all_links = list(dict.fromkeys(links + plain_urls))

    for url in all_links:
        # GitHub Pages (Webアプリ)
        if "tk030-lotto.github.io" in url:
            # カタログサイト自身は除外
            if "/my-tools" not in url:
                web_url = url.split("?")[0].rstrip("/") + "/"
        # GitHub リポジトリ
        elif "github.com/tk030-lotto" in url:
            # カタログサイト自身は除外
            if "/my-tools" not in url:
                github_url = url.split("?")[0].rstrip("/")

    return github_url, web_url

def generate_tool_id(name, web_url="", github_url=""):
    """ツールIDを生成"""
    if web_url:
        match = re.search(r'tk030-lotto\.github\.io/([^/]+)', web_url)
        if match:
            return match.group(1).rstrip('/')
    if github_url:
        match = re.search(r'github\.com/tk030-lotto/([^/]+)', github_url)
        if match:
            return match.group(1).rstrip('/')
    
    # 英数字・ハイフンのみ抽出、なければローマ字風簡易変換
    cleaned = re.sub(r'[^a-zA-Z0-9\-]', '', name)
    if cleaned:
        return cleaned.lower()
    return f"tool-{abs(hash(name)) % 100000}"

def sync():
    print("========================================================")
    print("  noteマガジンから最新の公開ツール情報を同期します")
    print("========================================================")
    print(f"[SYNC] マガジンAPI取得中: {MAGAZINE_API_URL}")

    try:
        data = fetch_json(MAGAZINE_API_URL)
    except Exception as e:
        print(f"[ERROR] note APIの取得に失敗しました: {e}")
        return

    notes = data.get("data", {}).get("notes", []) or data.get("data", [])
    print(f"[SYNC] マガジン内記事総数: {len(notes)} 件\n")

    current_data = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                current_data = json.load(f)
        except Exception as e:
            print(f"[WARN] 既存 tools.json 読み込みエラー: {e}")
            current_data = []

    # 既存データのnote_url・idマップ
    existing_by_note = {item.get("note_url"): item for item in current_data if item.get("note_url")}
    existing_by_id = {item.get("id"): item for item in current_data if item.get("id")}

    added_count = 0
    updated_count = 0

    for note in notes:
        title = (note.get("name") or note.get("title") or "").strip()
        key = note.get("key") or ""
        note_url = note.get("noteUrl") or f"https://note.com/zero_ai_dev/n/{key}"
        eyecatch = note.get("eyecatch") or ""
        price = note.get("price", 0)
        is_membership = note.get("is_membership", False)

        # 有料記事除外
        if price > 0:
            print(f"[SKIP/有料記事] {title} (¥{price})")
            continue

        # メンバーシップ限定除外
        if is_membership:
            print(f"[SKIP/メンバーシップ] {title}")
            continue

        # 除外キーワード判定（タイトル）
        if is_excluded(title):
            print(f"[SKIP/除外対象] {title}")
            continue

        # 記事公開日の取得（publish_at または created_at）
        raw_date = note.get("publish_at") or note.get("publishAt") or note.get("created_at") or ""
        release_date = raw_date[:10] if raw_date else ""

        # 既存登録チェック
        matched_item = existing_by_note.get(note_url)

        if matched_item:
            # 既存アイテムの補完更新（空のフィールドのみ埋める）
            changed = False
            if not matched_item.get("release_date") and release_date:
                matched_item["release_date"] = release_date
                changed = True
            if not matched_item.get("eyecatch") and eyecatch:
                matched_item["eyecatch"] = eyecatch
                changed = True
            if changed:
                print(f"[UPDATE] 既存ツール情報を補完: {matched_item.get('name')}")
                updated_count += 1
            continue

        # 新規記事の詳細を取得
        print(f"[FETCH] 新規候補の詳細を取得中: {title} (key: {key})")
        detail = fetch_note_detail(key)
        body = detail.get("body", "")

        # 本文の除外判定
        if is_excluded(title, body):
            print(f"[SKIP/本文除外対象] {title}")
            continue

        # URL抽出
        github_url, web_url = extract_urls_from_body(body)
        tool_id = generate_tool_id(title, web_url, github_url)

        # 重複ID回避
        if tool_id in existing_by_id:
            tool_id = f"{tool_id}-{len(current_data) + 1}"

        # プレーンテキスト要約
        plain_text = re.sub(r'<[^>]+>', ' ', body)
        plain_text = ' '.join(plain_text.split())
        description = plain_text[:120] + "..." if len(plain_text) > 120 else plain_text
        if not description:
            description = f"{title} の紹介"

        # タイトルとサブタイトルの分離（「...」形式の場合）
        item_name = title
        item_subtitle = ""
        m_title = re.match(r'^(「[^」]+」)(.*)$', title)
        if m_title:
            item_name = m_title.group(1).strip()
            item_subtitle = m_title.group(2).strip()

        new_item = {
            "id": tool_id,
            "name": item_name,
            "subtitle": item_subtitle,
            "category": "AI開発",
            "description": description,
            "why": "",
            "features": [],
            "github_url": github_url,
            "web_url": web_url,
            "note_url": note_url,
            "eyecatch": eyecatch or (detail.get("eyecatch") or ""),
            "tags": ["AI開発", "Webツール"] if web_url else ["AI開発", "開発支援"],
            "release_date": release_date,
            "status": "公開中"
        }

        current_data.append(new_item)
        existing_by_note[note_url] = new_item
        existing_by_id[tool_id] = new_item
        added_count += 1
        print(f"[NEW] 追加完了: {item_name} {item_subtitle}")
        print(f"      ID: {tool_id} | Web: {web_url or '(なし)'} | GitHub: {github_url or '(なし)'} | 公開日: {release_date}")

    # 常に公開日（release_date）の降順（新着順）でソート
    current_data.sort(key=lambda x: x.get("release_date") or "1970-01-01", reverse=True)

    # UTF-8 で tools.json に保存
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(current_data, f, ensure_ascii=False, indent=2)

    print("\n========================================================")
    print(f"  [OK] 同期完了: 新規追加 {added_count} 件 / 更新 {updated_count} 件 (合計 {len(current_data)} 件)")
    print(f"  データ保存先: {DATA_FILE}")
    print("========================================================")

if __name__ == "__main__":
    sync()
