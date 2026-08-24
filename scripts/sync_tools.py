#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_tools.py - noteマガジンおよび公開情報からツール一覧（tools.json）を同期・更新するスクリプト

使用方法:
    python scripts/sync_tools.py
"""

import json
import os
import re
import urllib.request

MAGAZINE_API_URL = "https://note.com/api/v1/magazines/m94b759b541f6/notes"
CREATOR_CONTENTS_API_URL = "https://note.com/api/v2/creators/zero_ai_dev/contents?kind=note&page=1"
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "tools.json")

# 除外キーワード（ロト系、メンバーシップ、未公開・凍結など）
EXCLUDE_KEYWORDS = [
    "ビンゴ5", "ナンバーズ", "ロト", "LOTO", "NUMBERS", "BINGO",
    "メンバーシップ", "会員限定", "有料", "凍結", "アーカイブ"
]

def fetch_json(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode("utf-8"))

def is_excluded(title, body=""):
    combined = f"{title} {body}"
    for kw in EXCLUDE_KEYWORDS:
        if kw in combined:
            return True
    return False

def sync():
    print(f"[SYNC] noteマガジンから最新情報を取得中: {MAGAZINE_API_URL}")
    try:
        data = fetch_json(MAGAZINE_API_URL)
    except Exception as e:
        print(f"[ERROR] note API取得失敗: {e}")
        return

    notes = data.get("data", {}).get("notes", []) or data.get("data", [])
    print(f"[SYNC] マガジン内記事数: {len(notes)} 件")

    current_data = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            current_data = json.load(f)

    existing_notes = {item.get("note_url"): item for item in current_data if item.get("note_url")}

    added_count = 0
    for note in notes:
        title = note.get("name") or note.get("title") or ""
        note_url = note.get("noteUrl") or f"https://note.com/zero_ai_dev/n/{note.get('key')}"
        eyecatch = note.get("eyecatch") or ""
        body = note.get("body") or note.get("summary") or ""
        is_membership = note.get("is_membership", False)

        if is_membership:
            print(f"[SKIP/メンバーシップ] {title}")
            continue

        if is_excluded(title, body):
            print(f"[SKIP/除外キーワード] {title}")
            continue

        if note_url not in existing_notes:
            print(f"[NEW] 新規掲載候補を検知: {title} ({note_url})")
            new_item = {
                "id": f"tool-{len(current_data) + 1}",
                "name": title,
                "subtitle": "",
                "category": "AI開発",
                "description": body[:120] if body else f"{title}の紹介",
                "why": "",
                "features": [],
                "github_url": "",
                "web_url": "",
                "note_url": note_url,
                "eyecatch": eyecatch,
                "tags": ["公開ツール"],
                "release_date": (note.get("publishAt") or "")[:10],
                "status": "公開中"
            }
            current_data.append(new_item)
            added_count += 1

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(current_data, f, ensure_ascii=False, indent=2)

    print(f"[SYNC] 完了: 新規追加 {added_count} 件 (合計 {len(current_data)} 件)")

if __name__ == "__main__":
    sync()
