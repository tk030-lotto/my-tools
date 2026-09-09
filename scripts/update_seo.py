#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_seo.py - data/tools.json を原本として、index.html の JSON-LD 構造化データ
および sitemap.xml の最終更新日を自動生成・同期するスクリプト

特徴:
- Zero-Dependency (Python標準ライブラリのみ使用)
- 原本一元化: tools.json の内容から自動的に ItemList 構造化データを生成
- 既存の index.html 内 <script type="application/ld+json" id="seo-jsonld"> を安全に更新
- sitemap.xml (トップページ1URL) の lastmod を自動更新
"""

import datetime
import json
import os
import re
import sys

# WindowsコンソールUTF-8対策
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "tools.json")
INDEX_HTML = os.path.join(BASE_DIR, "index.html")
SITEMAP_XML = os.path.join(BASE_DIR, "sitemap.xml")

SITE_URL = "https://tk030-lotto.github.io/my-tools/"

def generate_json_ld(tools):
    """tools.json のリストから Schema.org WebSite + ItemList の JSON-LD を生成"""
    today_str = datetime.date.today().isoformat()
    
    item_list_elements = []
    for idx, tool in enumerate(tools):
        name = tool.get("name", "")
        # description がなければ subtitle や name から補完
        description = tool.get("description") or tool.get("subtitle") or f"{name} の紹介"
        # プレーンテキスト化（HTMLタグ等があれば除去）
        description = re.sub(r'<[^>]+>', '', description).strip()
        if len(description) > 150:
            description = description[:147] + "..."
            
        # URLの優先順位: web_url > github_url > note_url
        target_url = tool.get("web_url") or tool.get("github_url") or tool.get("note_url") or SITE_URL
        
        item_list_elements.append({
            "@type": "ListItem",
            "position": idx + 1,
            "name": name,
            "description": description,
            "url": target_url
        })
    
    schema_data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": f"{SITE_URL}#website",
                "url": SITE_URL,
                "name": "My Tools",
                "description": "AI開発支援ツールや日常の面倒を減らす無料Webツールの公開カタログサイト",
                "inLanguage": "ja"
            },
            {
                "@type": "ItemList",
                "@id": f"{SITE_URL}#itemlist",
                "name": "公開ツール一覧",
                "description": f"AIと一緒に開発した公開ツール {len(tools)}選",
                "numberOfItems": len(tools),
                "itemListElement": item_list_elements
            }
        ]
    }
    
    return json.dumps(schema_data, ensure_ascii=False, indent=2)

def update_index_html(json_ld_string):
    """index.html の <script type="application/ld+json" id="seo-jsonld"> を更新"""
    if not os.path.exists(INDEX_HTML):
        print(f"[ERROR] index.html が見つかりません: {INDEX_HTML}")
        return False
        
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        content = f.read()
        
    target_tag = f'<script type="application/ld+json" id="seo-jsonld">\n{json_ld_string}\n  </script>'
    
    pattern = r'<script type="application/ld\+json" id="seo-jsonld">.*?</script>'
    if re.search(pattern, content, flags=re.DOTALL):
        # 既存タグの置換
        new_content = re.sub(pattern, target_tag, content, flags=re.DOTALL)
    else:
        # タグがまだない場合は </head> の直前に挿入
        if "</head>" in content:
            new_content = content.replace("</head>", f"  {target_tag}\n</head>")
        else:
            print("[ERROR] index.html に </head> が見つかりません")
            return False
            
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    print(f"[UPDATE] index.html の構造化データ (JSON-LD ItemList) を更新しました")
    return True

def update_sitemap():
    """sitemap.xml を更新 (トップページ1URLのみ、lastmodを本日の日付に設定)"""
    today_str = datetime.date.today().isoformat()
    
    sitemap_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{SITE_URL}</loc>
    <lastmod>{today_str}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
'''
    with open(SITEMAP_XML, "w", encoding="utf-8") as f:
        f.write(sitemap_content)
        
    print(f"[UPDATE] sitemap.xml を更新しました (lastmod: {today_str})")
    return True

def run():
    print("========================================================")
    print("  [SEO] tools.json から SEO構造化データ・サイトマップを自動生成")
    print("========================================================")
    
    if not os.path.exists(DATA_FILE):
        print(f"[ERROR] tools.json が見つかりません: {DATA_FILE}")
        return False
        
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        tools = json.load(f)
        
    print(f"[INFO] 掲載ツール総数: {len(tools)} 件")
    
    # 1. JSON-LD 生成
    json_ld_string = generate_json_ld(tools)
    
    # 2. index.html 更新
    update_index_html(json_ld_string)
    
    # 3. sitemap.xml 更新
    update_sitemap()
    
    print("========================================================")
    print("  [OK] SEO自動生成・同期が完了しました")
    print("========================================================")
    return True

if __name__ == "__main__":
    run()
