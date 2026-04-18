# claude-notion-brain 🧠

**Claude × Notion で「外部脳」を構築する — プログラミング経験不要**

研究者やナレッジワーカーが、AIに自分の蓄積した知識を横断的に活用してもらうための仕組みを、ゼロから構築するガイドです。
Claude AI（アプリ）がNotionに情報をINPUTし、Claude Code（CLT)がそれを読みときます。シンプルなPythonスクリプトが両者を同期する仕組みです。

> 📖 **[English version](README.md)**

---

## なぜ Claude Code（CLT） だけで完結しなかったのか？

最初はClaude Code（CLT）だけですべてやろうとしました — Notion MCPに接続して、直接読み書きする構成です。
**しかし、できませんでした。** 
ところが、結果的に、Claude Codeだけで完結しなかったことが**良い設計**に繋がりました。

### 技術的な壁

Claude Code（CLI）はOAuth認証でNotion MCPに接続できますが、2026年4月時点で既知のバグがあります。**OAuthトークンが約1時間で切れ、自動更新されません**（[GitHub #28256](https://github.com/anthropics/claude-code/issues/28256)）。セッションを開くたびに手動で再認証が必要で、これは日常使いには致命的でした。

### 予想外のメリット

Claude AI（アプリ）とClaude Code（CLT）に分けたことで、単なる回避策ではなく**より良い運用**が生まれました。

| | Claude Code（CLI） | Claude アプリ（スマホ/PC） |
|---|---|---|
| **得意** | ファイル操作、コーディング、100件超の文書横断参照 | 安定したNotion MCP接続、自然な対話、いつでもポケットに |
| **苦手** | Notion MCPが不安定、ターミナル限定 | ファイルシステムアクセス不可、スクリプト実行不可 |
| **最適な役割** | QUERY（読んで合成する） | INGEST/COMPILE（Notionに書く） |

**最大の発見: スマホで知識を収集できること。** 外出先で面白い論文を見つけた？ Xで新しい研究の知見を見た？ 時は、即スマホのClaudeに「これKBに追加して」と伝えるだけ。Claudeがその場で評価・要約し、Notionに書き込みます — 帰宅までに情報のデータベース化は終了、さらにWiki化も行います。

（帰宅後）PCでClaude Codeを開いたら `python3 sync_notion_kb.py` で自動的に同期され、あなたのAIアシスタントは、今日あなたが見つけたものをもう知っている状態でReady GOです。

---

## こんな人のために

- 論文・記事・ブックマークが溜まる一方で、AIが活用してくれない**研究者**
- 「読んだはずなのに、どこにあったか思い出せない」**ナレッジワーカー**
- プログラミング経験はないけど、AIを実務に活かしたい**非エンジニア**
- _「自分が読んできたものを、AIにも知っていてほしい」_ と思うすべての人

## 何が作れるか

```
あなたが記事・論文を収集
        ↓
Claude アプリが Notion に整理（INGEST / COMPILE）
        ↓
Python スクリプトでローカルに同期
        ↓
Claude Code（CLT） が横断検索・回答合成（QUERY）
        ↓
あなたの知識ベースに基づいた回答
```

### 3層アーキテクチャ

| レイヤー | 場所 | 内容 |
|---|---|---|
| **Raw（原典層）** | Notion: 情報集約DB | 元の記事・論文・URL — AIは読むだけで変更しない |
| **Wiki（知識層）** | Notion: Wiki DB | AIが生成・維持するソース要約・概念記事・合成分析 |
| **Schema（定義層）** | SCHEMA.md | AIの操作ルールと構造定義 |

### 役割分担

| タスク | 誰が | どうやって |
|---|---|---|
| ソース収集 | あなた | URL・論文・メモをNotionに保存 |
| INGEST・COMPILE | Claude アプリ（スマホ/PC） | Notion MCP経由でWiki DBに書き込み |
| QUERY | Claude Code（ターミナル/IDE） | ローカルMarkdownを横断参照 |
| SYNC | Pythonスクリプト | `python3 sync_notion_kb.py` |

## 必要なもの

- [Claude Pro/Max サブスクリプション](https://claude.ai)（Claude Code + Claude アプリ用）
- [Notion](https://notion.so) アカウント（まずは無料プランでOK）
- Python 3.8以上（macOS/Linuxにはプリインストール済み）
- ターミナルの基本操作（コマンドのコピペができればOK）

## セットアップ手順

### ステップ1: Notionにデータベースを作成

Notionに2つのデータベースを作成します。

**情報集約DB（Raw Sources）** のプロパティ:

| プロパティ名 | 型 |
|---|---|
| タイトル | タイトル |
| 要約 | テキスト |
| ソース種別 | セレクト（URL / PDF / X投稿 / その他） |
| 元URL | URL |
| 関連プロジェクト | マルチセレクト |
| 有益性スコア | セレクト（◎必須 / ○有益 / △参考程度） |
| タグ | マルチセレクト |
| 収集日 | 日付 |
| ステータス | セレクト（未読 / 確認済 / 対応済） |

**Wiki DB（統合知識層）** のプロパティ:

| プロパティ名 | 型 |
|---|---|
| タイトル | タイトル |
| 要約（1-2文） | テキスト |
| タイプ | セレクト（ソース要約 / 概念記事 / 合成分析 / Q&A出力 / スタブ） |
| 元ソース | URL |
| 関連プロジェクト | マルチセレクト |
| 信頼度 | セレクト（established / emerging / speculative） |
| タグ | マルチセレクト |
| 作成日 | 日付 |
| 最終更新日 | 日付 |
| ステータス | セレクト |

> 💡 プロパティ名は自由に変更できます。`config.json` を合わせて更新してください。

### ステップ2: Notionインテグレーションを作成

1. [Notion Integrations](https://www.notion.so/profile/integrations) を開く
2. **「新しいインテグレーション」** をクリック
3. 名前を入力（例: `Claude Code Sync`）、ワークスペースを選択
4. **「内部インテグレーションシークレット」**（`ntn_...`）をコピー
5. Notionで各データベースを開き → **「…」** → **「接続」** → 作成したインテグレーションを追加

### ステップ3: APIキーを保存

```bash
echo 'NOTION_API_KEY=ntn_あなたのキー' > ~/.notion_env
```

> ⚠️ このファイルは絶対にgitにコミットしないでください。`.gitignore` でデフォルトで除外されています。

### ステップ4: 同期スクリプトを設定・実行

```bash
# リポジトリをクローン
git clone https://github.com/YOUR_USERNAME/claude-notion-brain.git
cd claude-notion-brain/scripts

# 設定ファイルをコピーして編集
cp config.json.example config.json
# config.json を編集: YOUR_RAW_DATABASE_ID と YOUR_WIKI_DATABASE_ID を
# 実際のNotion データベースIDに置き換え

# 同期を実行
python3 sync_notion_kb.py
```

**データベースIDの確認方法**: Notionでデータベースをフルページで開きます。URLは以下の形式です:
```
https://notion.so/YOUR_WORKSPACE/DATABASE_ID?v=...
```
32文字の `DATABASE_ID` をコピーし、ハイフン区切りにします:
`12345678-1234-1234-1234-123456789abc`

### ステップ5: Claude アプリをNotionに接続

1. Claude アプリ（スマホまたはPC）を開く
2. **設定** → **Connectors**（または **MCP**）
3. **Notion** を追加し、ワークスペースへのアクセスを許可
4. これでClaudeに「情報集約DBに追加して」「Wiki記事を作成して」と依頼できます

### ステップ6: CLAUDE.md にルールを追加

`~/.claude/CLAUDE.md` に以下を追加:

```markdown
## 外部脳（Notion KB）
- **知識ベース**: `~/notion_kb/`（情報集約DB + Wiki DB統合知識層）
- **鮮度チェック**: セッション冒頭で `~/notion_kb/INDEX.md` の同期日時を確認し、
  24時間以上経過していれば `python3 ~/scripts/sync_notion_kb.py` を実行
- **QUERYサイクル**: LLM・質的分析・マーケティング・KJ法等に関連する質問を受けたら、
  `~/notion_kb/wiki/INDEX.md` → 個別記事を横断参照して回答に反映する
- **スキーマ定義**: `~/notion_kb/SCHEMA.md`
```

### ステップ7: スキーマをKBにコピー

```bash
cp templates/SCHEMA.md ~/notion_kb/SCHEMA.md
```

## 日常のワークフロー

### スマホで（Claude アプリ）

> _「この論文を見つけました: [URL]。情報集約DBに追加して、Wiki要約も作成してください。」_

Claude がURLを読み、評価し、情報集約DBに追加し、Wiki記事を作成します — すべてNotion MCP経由。

### PCで（Claude Code CLT）

```bash
# Notionから最新データを同期
python3 ~/scripts/sync_notion_kb.py

# Claude Code に自然に質問するだけ:
# 「質的研究のデータ飽和について、KBに何かある？」
# Claude Code がWiki記事を横断参照して回答を合成します。
```

## アーキテクチャ

システム全体図は [docs/architecture.md](docs/architecture.md) を参照してください。

## よくある質問

### Claude Code(CLT) から直接 Notion MCP に接続できないの？

2026年4月時点で、Claude Code(CLT) の Notion MCP 向け OAuth トークン自動更新に不具合があります（[GitHub #28256](https://github.com/anthropics/claude-code/issues/28256)）。約1時間でトークンが切れ、毎回手動で再認証が必要です。ローカル同期方式の方が安定しており、オフラインでも動作します。

### プログラミングスキルは必要？

不要です。必要な操作は：
- ターミナルでコマンドをコピペ
- JSONファイルのIDを自分のものに置き換え
- `python3 sync_notion_kb.py` を実行

だけです。

### データベースのスキーマはカスタマイズできる？

はい！ `config.json` でNotionのプロパティ名と型を設定できます。スクリプトは完全に設定ファイル駆動です。

### どのくらいの頻度で同期すべき？

CLAUDE.md のルールでは24時間以上経過したら自動同期を推奨しています。多くの研究者にとっては、1日1回またはセッションごとで十分です。

## このプロジェクトの背景

このプロジェクトは、社会科学の研究者が「外部脳」を作りたいという思いから生まれました。論文、記事、研究ノートから蓄積した知識を、日常のAIとの対話で横断的に活用できるようにする仕組みです。

核心的なアイデア: **「書く」と「読む」を分離する。** Claude アプリはコンテンツを理解し、Notionに構造化されたノートを書くのが得意。Claude Code(CLT)はファイルを読み、多数のドキュメントを横断して知識を合成するのが得意。シンプルなPythonスクリプトが両者をつなぎます。

**エンジニアではない研究者が、ゼロから構築して実際に動いている仕組みです。**

## 謝辞

このプロジェクトは以下の方々・サービスに触発され、生まれました。

- [Anthropic Claude](https://anthropic.com) — AIパートナーであり共同制作者
  （Claude Codeはこのリポジトリに直接コントリビュートしています）
- [Notion](https://www.notion.com/ja) — 外部脳の知識基盤を支えるプラットフォーム
- [Andrej Karpathy](https://x.com/karpathy/status/2039805659525644595) — 
  Xへの「LLM Knowledge Bases」投稿が着想のきっかけに
- [hooeem](https://x.com/hooeem/status/2041196025906418094) — 
  Xの「How to create your own LLM knowledge bases today」記事が着想のきっかけに
- [Claude Code Studio](https://x.com/ClaudeCode_love/status/2042886840177557533) — 
  Xの「元OpenAIの社員が実践するClaude Code×Obsidianで『AI外部脳』をゼロから作る完全ガイド」記事が着想のきっかけに

## ライセンス

MIT License。[LICENSE](LICENSE) を参照。

## コントリビューション

Issue や Pull Request を歓迎します！特に非エンジニアや社会科学・人文科学分野の研究者からのフィードバックを大切にしています。
