# My Tools — 公開ツールカタログサイト

AIと一緒に開発した公開ツール・ユーティリティ・開発支援ツールを一覧できる静的カタログサイトです。  
Zero-Dependency（ビルド不要・HTML/CSS/Vanilla JS）で構築されており、GitHub Pages上でそのまま高速に動作します。

---

## 🎯 コンセプト

```text
                 ┌─────────────┐
                 │ GitHub Pages│
                 │   ツール一覧  │ （目録・カタログ）
                 └──────┬──────┘
                        │
             ┌──────────┴──────────┐
             ↓                     ↓
       ┌──────────┐          ┌──────────┐
       │  GitHub  │          │   note   │
       │ ソースコード│          │ 開発ストーリー│ （実物・解説）
       └──────────┘          └──────────┘
```

- **GitHub**: 実物（ソースコード、Issue、リポジトリ）
- **note**: 物語（開発経緯、解決した面倒、使い方）
- **GitHub Pages**: 目録（現在公開されているツールの検索・一覧入口）

---

## 📁 ディレクトリ構成

```text
公開ツール一覧サイト/
│
├── index.html            # メインページ（セマンティック構造・OGP対応）
├── css/
│   └── style.css         # シニアプロトコル第18条準拠 ミニマル・ダークUI
├── js/
│   └── app.js            # tools.jsonからの動的描画・リアルタイム検索・カテゴリ絞り込み
├── data/
│   └── tools.json        # ツールマスターデータ（1件追加するだけで一覧反映）
├── scripts/
│   └── sync_tools.py     # noteマガジンから最新記事を自動同期するスクリプト
└── README.md             # 本書
```

---

## 🛠️ 新しいツールの追加方法

### 方法1: `data/tools.json` を直接編集（推奨・最も確実）

`data/tools.json` の配列に新しいツールのオブジェクトを追加します：

```json
{
  "id": "my-new-tool",
  "name": "ツール名",
  "subtitle": "短いキャッチコピー",
  "category": "AI開発", // "AI開発" | "開発支援" | "ファイル・PC" | "その他"
  "description": "何のツールかを1文で説明",
  "why": "どんな面倒・課題を解決するために作ったか",
  "features": [
    "主な特徴1",
    "主な特徴2"
  ],
  "github_url": "https://github.com/tk030-lotto/...",
  "web_url": "https://tk030-lotto.github.io/.../", // なければ空文字 ""
  "note_url": "https://note.com/zero_ai_dev/n/...",
  "eyecatch": "サムネイル画像URL",
  "tags": ["AI開発", "Webツール"],
  "release_date": "2026-08-24",
  "status": "公開中"
}
```

### 方法2: 同期スクリプトを実行

noteマガジン（`https://note.com/zero_ai_dev/m/m94b759b541f6`）に新しい記事を追加した後、以下のコマンドを実行します：

```bash
python scripts/sync_tools.py
```

ロト系ツールやメンバーシップ限定記事は自動的にスキップされ、一般公開ツールのみが `data/tools.json` に追加されます。

---

## 🌐 GitHub Pages への公開手順（後から公開する場合）

本サイトを GitHub Pages で公開したい場合は、以下の手順で設定してください。

1. **GitHub に新しいリポジトリを作成**（例: `my-tools` または `portfolio`）
2. **本フォルダのファイルをプッシュ**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: My Tools catalog site"
   git branch -M main
   git remote add origin https://github.com/tk030-lotto/<リポジトリ名>.git
   git push -u origin main
   ```
3. **GitHub リポジトリ設定で GitHub Pages を有効化**
   - リポジトリの **Settings** > **Pages** を開く
   - **Source** を `Deploy from a branch` に設定
   - **Branch** を `main` / `/(root)` を選択して **Save**
4. 数分後、`https://tk030-lotto.github.io/<リポジトリ名>/` でカタログサイトが公開されます。

---

## 📄 ライセンス

MIT License
