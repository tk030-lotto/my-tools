#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_seo.py - data/tools.json を原本として以下を自動生成・同期するスクリプト
  1. index.html 内の JSON-LD（Schema.org WebSite + ItemList）を自動更新
  2. sitemap.xml の lastmod を本日日付に自動更新

使用方法:
    python scripts/update_seo.py

依存ライブラリ: Python標準モジュールのみ（Zero-Dependency）
"""

import json
import os
import re
import sys
from datetime import date

# WindowsコンソールのUTF-8文字化け対策
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# --- パス定義 ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE   = os.path.join(BASE_DIR, 'data', 'tools.json')
INDEX_FILE  = os.path.join(BASE_DIR, 'index.html')
SITEMAP_FILE = os.path.join(BASE_DIR, 'sitemap.xml')

SITE_URL = 'https://tk030-lotto.github.io/my-tools/'


def load_tools():
    """tools.json を読み込む"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_jsonld(tools):
    """
    Schema.org JSON-LD を構築する。
    1つの <script> タグ内に WebSite + ItemList（全ツール）をまとめる。
    """
    items = []
    for i, t in enumerate(tools, start=1):
        # リンク先は Web版 > GitHub の優先順
        url = t.get('web_url') or t.get('github_url') or SITE_URL
        items.append({
            '@type': 'ListItem',
            'position': i,
            'name': t.get('name', ''),
            'description': t.get('description', ''),
            'url': url
        })

    schema = {
        '@context': 'https://schema.org',
        '@graph': [
            {
                '@type': 'WebSite',
                '@id': f'{SITE_URL}#website',
                'url': SITE_URL,
                'name': 'My Tools',
                'description': 'AI開発支援ツールや日常の面倒を減らす無料Webツールの公開カタログサイト',
                'inLanguage': 'ja'
            },
            {
                '@type': 'ItemList',
                '@id': f'{SITE_URL}#itemlist',
                'name': '公開ツール一覧',
                'description': 'AIと一緒に開発した公開ツール一覧',
                'numberOfItems': len(tools),
                'itemListElement': items
            }
        ]
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)


def update_index_html(jsonld_str):
    """
    index.html 内の <script type="application/ld+json" id="seo-jsonld"> の内容を置換する。
    タグが存在しない場合は </head> の直前に挿入する。
    """
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    script_tag = f'<script type="application/ld+json" id="seo-jsonld">\n{jsonld_str}\n</script>'

    # 既存の seo-jsonld タグを置換
    pattern = r'<script[^>]+id="seo-jsonld"[^>]*>.*?</script>'
    if re.search(pattern, html, flags=re.DOTALL):
        html = re.sub(pattern, script_tag, html, flags=re.DOTALL)
        print('[UPDATE] index.html の既存 JSON-LD を更新しました。')
    else:
        # 存在しない場合は </head> の直前に挿入
        html = html.replace('</head>', f'  {script_tag}\n</head>', 1)
        print('[INSERT] index.html に JSON-LD を新規挿入しました。')

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(html)


def update_sitemap():
    """
    sitemap.xml の lastmod を本日日付に更新する。
    ファイルが存在しない場合は新規作成する。
    """
    today = date.today().strftime('%Y-%m-%d')
    content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{SITE_URL}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
'''
    with open(SITEMAP_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'[UPDATE] sitemap.xml を更新しました（lastmod: {today}）。')


def main():
    print('========================================================')
    print('  [SEO] update_seo.py - SEO構造化データを自動同期します')
    print('========================================================')

    # tools.json 読み込み
    tools = load_tools()
    print(f'[LOAD] tools.json 読み込み完了: {len(tools)} 件')

    # JSON-LD 生成
    jsonld_str = build_jsonld(tools)
    print(f'[BUILD] JSON-LD 生成完了（ItemList: {len(tools)} 件）')

    # index.html 更新
    update_index_html(jsonld_str)

    # sitemap.xml 更新
    update_sitemap()

    print('========================================================')
    print(f'  [OK] SEO同期完了: {len(tools)} ツールを構造化データとして提供します。')
    print('========================================================')


if __name__ == '__main__':
    main()
