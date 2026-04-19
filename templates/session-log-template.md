# Session Log Template / セッションログテンプレート

> Copy this structure to a Notion page to use as your session log.
> This page serves as "dynamic memory" — updated by Claude at the end of each session.

---

## How to Set Up / セットアップ方法

1. Create a new page in your Notion workspace (e.g., "KB Session Log")
2. **Convert to Wiki** (required for Claude App to access via Notion MCP)
   - Click "..." menu → "Turn into wiki"
   - Then add your Integration: "..." → "Connections" → select your integration
3. Copy the template below into the page
4. Tell Claude App: "Use this page as our session log"

> 💡 **Why "Turn into wiki"?**
> Regular Notion pages don't show the "Connections" menu for integrations.
> Converting to Wiki enables integration access. ([Details](https://developers.notion.com/docs/working-with-page-content))

---

## Template / テンプレート

```markdown
📋 セッションログ — KB作業記録

---

## セッション#1（YYYY-MM-DD）— ステータス

### INGEST完了
1. （記事・論文タイトル）
2. ...

### COMPILE完了
- （更新したWikiページ名）✅
- ...

### 現在のペンディング
☐ （次回やるべきタスク）
☐ ...

### 現在のWiki DB統計
- ソース要約：XX件
- 概念記事：XX件
- 総ページ数：約XX件

---

（以降、セッション#2, #3... と追記されていく）
```

---

## Usage / 使い方

### Starting a session / セッション開始時

> _「前回の続きをやって」_

Claude reads the session log and restores context automatically.

### Ending a session / セッション終了時

> _「今日はここまで」_

Claude automatically updates the session log:
- Checks off completed items
- Adds new pending items
- Updates Wiki DB statistics
