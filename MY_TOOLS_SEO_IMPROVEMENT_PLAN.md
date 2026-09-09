# My Tools SEO改修計画書 (MY_TOOLS_SEO_IMPROVEMENT_PLAN.md)

**策定日**: 2026-09-09  
**対象サイト**: [https://tk030-lotto.github.io/my-tools/](https://tk030-lotto.github.io/my-tools/)  
**基本方針**: 既存UI・デザイン・JavaScript機能への変更を行わず、SEOのために必要な技術的要素を最小構成で補う。  
**掲載ツール数**: 全20件（掲載基準改定により「ロト＆ナンバーズ 統合構造解析・出目表可視化ツール」を追加）

---

## 1. 掲載基準の改定について（明記）

従来のMy Toolsでは、ロト関連ツールを一律で掲載対象外としていましたが、今回より以下の通り方針を改定します。

> **【掲載基準の改定】**  
> 従来除外していたロト系ツールのうち、「当選予想」ではなく「過去データの統計・構造解析・可視化」を目的とするオープンソースWebツールである **『ロト＆ナンバーズ 統合構造解析・出目表可視化ツール』を今回からMy Toolsの掲載対象に含める方針** に変更する。

---

## 2. 改修の基本方針

1. **既存UI・デザイン・JavaScript機能への変更を行わない**:
   CSS（`style.css`）やフロントエンドの検索・ソート・モーダルロジック（`app.js`）は一切変更せず、既存の画面表示と操作感を維持する。
2. **Zero-Dependency（ノービルド）の維持**:
   外部ビルドツールを導入せず、静的ファイルのまま保守可能とする。
3. **個別ページを作らない（1ページ完結の維持）**:
   note記事（物語）や各ツールのGitHub Pages（本体）との重複コンテンツを回避する。
4. **原本の一元化（Single Source of Truth）**:
   `data/tools.json` を唯一の情報源とし、今後ツールが増加しても `index.html` や `sitemap.xml` を手動修正する必要がない自動生成構造とする。
5. **sitemap.xml はトップページ1URLのみ**:
   個別ページが存在しない1ページ完結サイトのため、サイトマップのURL数は1件固定とし、ツール追加時は `lastmod`（更新日）のみを自動同期する。

---

## 3. 実施する改修項目一覧

| 改修ID | 対象ファイル | 改修種別 | 内容概要 |
| :---: | :--- | :---: | :--- |
| **M-1** | `index.html` | 変更 | `<title>` タグの最適化（`My Tools — AI開発支援・無料Webツール一覧カタログ`） |
| **M-2** | `index.html` | 変更 | `<link rel="canonical">` の追加（重複URL防止） |
| **M-3** | `scripts/update_seo.py` | 新規作成 | `tools.json` を原本とし、`index.html` の JSON-LD（`ItemList`）および `sitemap.xml` の更新日を自動同期するスクリプト（Python標準モジュールのみ） |
| **M-4** | `index.html` | 変更 | `<meta name="description">` の最適化（約120文字） |
| **M-5** | `index.html` | 変更 | `<meta property="og:title">` および `<meta property="og:url">` の追加・統一 |
| **M-6** | `data/tools.json` | 追加 | 掲載基準改定に伴う「ロト＆ナンバーズ 統合構造解析・出目表可視化ツール」の登録（全20ツール） |
| **M-7** | `scripts/sync_tools.py` | 変更 | 同期処理完了時に `update_seo.py` を自動実行し、`記事同期.bat` 一発でSEOまで自動同期 |
| **F-1** | `robots.txt` | 新規作成 | クロール許可およびサイトマップパスの明記 |
| **F-2** | `sitemap.xml` | 新規作成 | トップページ1URLの正規パスを明記（自動更新対象） |

---

## 4. 自動同期アーキテクチャ

```text
【新ツール追加時】
       │
       ▼
[note記事を公開] 
       │
       ▼
[記事同期.bat を実行]（ダブルクリック）
       │
       ├──▶ [1] scripts/sync_tools.py
       │         ・noteマガジンから最新記事を取得
       │         ・data/tools.json を自動更新・ソート
       │
       └──▶ [2] scripts/update_seo.py（自動連動）
                 ・最新の tools.json を読み込み
                 ・index.html の JSON-LD（ItemList: 全20件〜）を機械可読データとして自動生成
                 ・sitemap.xml の更新日（lastmod）を自動同期
       │
       ▼
【完了】画面表示データとSEO構造化データが完全自動で最新化
```

---

## 5. 対象ファイルと具体的な変更内容

### 5.1 `data/tools.json`（新規ツールの追加）

全20件目として以下のオブジェクトを追加します。

```json
{
  "id": "lotto-numbers-visualization-tool",
  "name": "ロト＆ナンバーズ 統合構造解析・出目表可視化ツール",
  "subtitle": "ロトを「予想」するのではなく「構造を見る」",
  "category": "その他",
  "description": "ロト7・ロト6・ミニロト・ナンバーズ3・ナンバーズ4の過去出目データを統合分析し、出現頻度・引っ張り・スライド・未出現スパン・共起ペアなどを直感的に可視化するブラウザ完結型Webツール。",
  "why": "当選番号の「予想」ではなく、過去データから数字の構造や出現パターン・傾向を客観的に観察・検証できる分析環境を作るため。",
  "features": [
    "ロト7/6/ミニロト/ナンバーズ3/4の5種を1つの画面で切り替え分析",
    "出目表・出現頻度4段階（HOT/GOLD/RECOVERY/COLD）・スライド・未出現スパン可視化",
    "過去の基準回号に戻って再検証可能なタイムトラベル機能＆Markdown出力対応"
  ],
  "github_url": "https://github.com/tk030-lotto/lotto-numbers-visualization-tool",
  "web_url": "https://tk030-lotto.github.io/lotto-numbers-visualization-tool/",
  "note_url": "https://note.com/zero_ai_dev/n/ndf9d3ef0a479",
  "eyecatch": "https://assets.st-note.com/production/uploads/images/310744895/rectangle_large_type_2_77f4f02b82eaece8874190984f5221a0.png",
  "tags": [
    "データ可視化",
    "Webツール",
    "統計・分析",
    "React"
  ],
  "release_date": "2026-09-06",
  "status": "公開中"
}
```

### 5.2 `index.html` の変更内容

`<head>` セクションのみを更新します（`<body>` のUI部分は変更なし）。

```html
<title>My Tools — AI開発支援・無料Webツール一覧カタログ</title>
<meta name="description" content="日常の面倒を減らす無料Webツール＆AI開発支援ツールの公開カタログ。「引き継いでみよう」「エラーで止まらない」「CookScale」など、ブラウザですぐ使える個人開発ツールをまとめています。ソースコード（GitHub）と開発ストーリー（note）も公開中。">
<link rel="canonical" href="https://tk030-lotto.github.io/my-tools/">

<!-- OGP & Twitter Cards -->
<meta property="og:title" content="My Tools — AI開発支援・無料Webツール一覧カタログ">
<meta property="og:description" content="日常の面倒を減らす無料Webツール＆AI開発支援ツールの公開カタログ。「引き継いでみよう」「エラーで止まらない」「CookScale」など、ブラウザですぐ使える個人開発ツールをまとめています。">
<meta property="og:type" content="website">
<meta property="og:url" content="https://tk030-lotto.github.io/my-tools/">
<meta property="og:image" content="https://assets.st-note.com/production/uploads/images/296872352/ce71b7f267b987408937f876e7c147bd.png">
<meta name="twitter:card" content="summary_large_image">

<!-- 構造化データ (Schema.org) ※scripts/update_seo.py により自動生成・同期 -->
<script type="application/ld+json" id="seo-jsonld">
...
</script>
```

### 5.3 `robots.txt`

```text
User-agent: *
Allow: /

Sitemap: https://tk030-lotto.github.io/my-tools/sitemap.xml
```

### 5.4 `sitemap.xml`

トップページ1URLのみを明記します。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://tk030-lotto.github.io/my-tools/</loc>
    <lastmod>2026-09-09</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
```

---

## 6. テスト・検証項目

1. `update_seo.py` 実行による `index.html` および `sitemap.xml` の自動更新テスト
   - `<head>` 内に `<title>`、`<meta name="description">`、`<link rel="canonical">`、および **20ツールを含むJSON-LD（ItemList）が静的に埋め込まれている** ことを確認
   - `sitemap.xml` にトップページ1URLのみが記載され、`lastmod` が最新日付に更新されていることを確認
2. ブラウザでの全20ツール表示・検索・タブ切り替え・モーダル表示テスト
3. JSON-LD構文検証（Schema.org準拠、エラーなし）
4. `記事同期.bat` との連動確認（ツール追加時に自動でSEOメタデータまで最新化）
