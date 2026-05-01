# claude-notion-brain 🧠

**Build your external brain with Claude × Notion — no coding experience required.**

A step-by-step guide for researchers and knowledge workers to build a personal knowledge base that AI can actually use. Claude AI writes to Notion, Claude Code reads from it, and a simple Python script keeps them in sync.

> 📖 **[日本語版はこちら / Japanese version](README_ja.md)**

---

## Who Is This For?

- **Social science researchers** who want AI to understand their accumulated knowledge
- **Knowledge workers** drowning in papers, articles, and bookmarks
- **Non-engineers** who want a practical AI workflow without deep technical skills
- Anyone who thinks _"I've read so much, but my AI assistant doesn't know any of it"_

## Why Not Just Claude Code?

We originally tried to do everything in Claude Code — connect to Notion via MCP, read and write directly. **It didn't work.** Here's why, and why the alternative turned out to be _better_.

### The Technical Barrier

Claude Code (CLI) connects to Notion via OAuth-based remote MCP. As of April 2026, there's a known bug: **OAuth tokens expire every ~1 hour and don't auto-refresh** ([GitHub #28256](https://github.com/anthropics/claude-code/issues/28256)). Every session requires manual re-authentication. For daily use, this is a dealbreaker.

### The Unexpected Upside

Splitting the work between Claude App and Claude Code wasn't just a workaround — it turned out to be a **better design**:

| | Claude Code (CLI) | Claude App (Mobile/Desktop) |
|---|---|---|
| **Strengths** | File system access, coding, cross-referencing 100+ docs | Stable Notion MCP, natural conversation, always in your pocket |
| **Weaknesses** | Notion MCP unreliable, terminal-only | No file system, no scripting |
| **Best for** | QUERY (reading & synthesizing) | INGEST/COMPILE (writing to Notion) |

**The key insight: you can collect knowledge from your phone.** Found an interesting paper on the train? A tweet with a new research finding? Just tell Claude on your phone: _"Add this to my KB."_ Claude evaluates it, summarizes it, and writes it to Notion — all before you get to your desk.

By the time you open Claude Code on your computer, `python3 sync_notion_kb.py` pulls everything down, and your AI assistant already knows what you found today.

## What You'll Build

```
You find articles & papers (anytime, anywhere)
        ↓
Claude App writes to Notion via phone/desktop (INGEST/COMPILE)
        ↓
Python script syncs to local files
        ↓
Claude Code reads & cross-references (QUERY)
        ↓
Answers informed by YOUR knowledge base
```

### The 3+1 Layer Architecture

| Layer | Where | What | Type |
|---|---|---|---|
| **Raw** | Notion: Raw Sources DB | Original articles, papers, URLs — never modified by AI | Static |
| **Wiki** | Notion: Wiki DB | AI-generated summaries, concept articles, synthesis | AI-maintained |
| **Schema** | SCHEMA.md | Rules governing how AI reads and writes | Static |
| **Session Log** | Notion (regular page) | Work-in-progress state — what's done, what's pending | **Dynamic** |

> The Session Log layer was added in v2.0. See [What's New in v2.0](#whats-new-in-v20-session-log) below.

### Role Division

| Task | Who | How |
|---|---|---|
| Collect sources | You | Save URLs, papers, notes to Notion |
| INGEST & COMPILE | Claude App (mobile/desktop) | Summarize, create wiki entries via Notion MCP |
| QUERY | Claude Code (terminal/IDE) | Cross-reference local Markdown copies |
| SYNC | Python script | `python3 sync_notion_kb.py` |

## Prerequisites

- [Claude Pro/Max subscription](https://claude.ai) (for Claude Code + Claude App)
- [Notion](https://notion.so) account (free plan works)
- Python 3.8+ (pre-installed on macOS/Linux)
- Basic terminal skills (copy-paste commands)

## Quick Start

### Step 1: Set Up Notion Databases

Create two databases in Notion:

**Raw Sources DB** with these properties:

| Property | Type |
|---|---|
| タイトル (Title) | Title |
| 要約 (Summary) | Rich text |
| ソース種別 (Source Type) | Select: URL / PDF / SNS / Other |
| 元URL (Source URL) | URL |
| 関連プロジェクト (Projects) | Multi-select |
| 有益性スコア (Usefulness) | Select: ◎ / ○ / △ |
| タグ (Tags) | Multi-select |
| 収集日 (Collected) | Date |
| ステータス (Status) | Select: Unread / Reviewed / Done |

**Wiki DB (Knowledge Layer)** with these properties:

| Property | Type |
|---|---|
| タイトル (Title) | Title |
| 要約 (Summary) | Rich text |
| タイプ (Type) | Select: Source Summary / Concept Article / Synthesis / Q&A / Stub |
| 元ソース (Source) | URL |
| 関連プロジェクト (Projects) | Multi-select |
| 信頼度 (Confidence) | Select: established / emerging / speculative |
| タグ (Tags) | Multi-select |
| 作成日 (Created) | Date |
| 最終更新日 (Last Updated) | Date |
| ステータス (Status) | Select |

> 💡 Property names can be in any language. Just update `config.json` to match.

### Step 2: Create a Notion Integration

1. Go to [Notion Integrations](https://www.notion.so/profile/integrations)
2. Click **"New integration"**
3. Name it (e.g., `Claude Code Sync`), select your workspace
4. Copy the **Internal Integration Secret** (`ntn_...`)
5. In Notion, open each database → **"..."** → **"Connections"** → add your integration

### Step 3: Store Your API Key

```bash
echo 'NOTION_API_KEY=ntn_YOUR_KEY_HERE' > ~/.notion_env
```

> ⚠️ Never commit this file to git. It's in `.gitignore` by default.

### Step 4: Configure and Run the Sync Script

```bash
# Clone this repository
git clone https://github.com/YOUR_USERNAME/claude-notion-brain.git
cd claude-notion-brain/scripts

# Copy the example config and edit it
cp config.json.example config.json
# Edit config.json: replace YOUR_RAW_DATABASE_ID and YOUR_WIKI_DATABASE_ID
# with your actual Notion database IDs

# Run the sync
python3 sync_notion_kb.py
```

**How to find your database ID**: Open the database in Notion as a full page. The URL will be:
```
https://notion.so/YOUR_WORKSPACE/DATABASE_ID?v=...
```
Copy the 32-character `DATABASE_ID` and format it with hyphens:
`12345678-1234-1234-1234-123456789abc`

### Step 5: Connect Claude App to Notion

1. Open Claude App (mobile or desktop)
2. Go to **Settings** → **Connectors** (or **MCP**)
3. Add **Notion** and authorize access to your workspace
4. You can now ask Claude to read your Raw Sources DB and write to Wiki DB

### Step 6: Add the CLAUDE.md Rule

Add this to your `~/.claude/CLAUDE.md`:

```markdown
## External Brain (Notion KB)
- **Knowledge Base**: `~/notion_kb/` (Raw Sources DB + Wiki DB Knowledge Layer)
- **Freshness Check**: At session start, check sync timestamp in `~/notion_kb/INDEX.md`.
  If older than 24 hours, run `python3 ~/scripts/sync_notion_kb.py`
- **QUERY Cycle**: When questions relate to your research domains,
  cross-reference `~/notion_kb/wiki/INDEX.md` → individual articles to inform answers.
- **Schema Definition**: `~/notion_kb/SCHEMA.md`
```

### Step 7: Copy the Schema to Your KB

```bash
cp templates/SCHEMA.md ~/notion_kb/SCHEMA.md
```

## Daily Workflow

### On Your Phone (Claude App)

> _"I found this interesting paper: [URL]. Please add it to my Raw Sources DB and create a Wiki summary."_

Claude reads the URL, evaluates it, adds it to your Raw Sources DB, and creates a wiki entry — all via Notion MCP.

### On Your Computer (Claude Code)

```bash
# Sync latest changes from Notion
python3 ~/scripts/sync_notion_kb.py

# Then in Claude Code, just ask naturally:
# "What does my KB say about data saturation in qualitative research?"
# Claude Code will cross-reference your wiki articles and synthesize an answer.
```

## What's New in v2.0: Session Log

The v1.0 3-layer architecture organized **static** knowledge beautifully, solving the problem of Claude Code (CLI) "forgetting everything by morning" with an external brain.
But then we discovered that **Claude App — the one writing to Notion — also had imperfect memory.**

Claude App does have a cross-session memory feature, but it's **not complete**:

- It skews toward recent conversations — older memories fade
- KB work logs (what was INGESTed, what's still pending) are too much to remember
- Every new session starts with "Where did we leave off last time?"

**Session Log** solves this by adding a **dynamic memory** layer:

```
Session ends → Claude updates the Session Log in Notion
                (completed items, pending tasks, statistics)
                        ↓
Next session starts → "Pick up where we left off"
                        ↓
Claude reads Session Log → context fully restored
```

### How to set it up

1. Create a new Notion page for session logging
2. Copy the template from [`templates/session-log-template.md`](templates/session-log-template.md)
3. Tell Claude App: "Use this page as our session log"

> ⚠️ **Do not convert to Wiki.** Notion Wiki pages are not fully supported by the public API (including OAuth/MCP). Claude App cannot write to Wiki pages. Keep the session log as a regular document page.

### How it works in practice

**Starting a session:**
> _"Pick up where we left off."_
>
> Claude: "I've checked the session log. Last time we INGESTed 2 articles and have 2 pending items..."

**Ending a session:**
> _"That's all for today."_
>
> Claude automatically updates the session log with completed work and new pending items.

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full system diagram.

## FAQ

### Why not connect Claude Code directly to Notion MCP?

As of April 2026, Claude Code's OAuth token refresh for Notion MCP is unreliable ([GitHub #28256](https://github.com/anthropics/claude-code/issues/28256)). Tokens expire hourly, requiring manual re-authentication. The local sync approach is more stable and works offline.

### Do I need programming skills?

No. You only need to:
- Copy-paste terminal commands
- Edit a JSON config file (replace placeholder IDs with yours)
- Run `python3 sync_notion_kb.py` when you want to update

### Can I customize the database schema?

Yes! Edit `config.json` to match your Notion property names and types. The sync script is fully config-driven.

### How often should I sync?

The CLAUDE.md rule suggests auto-syncing if >24 hours old. For most researchers, once per day or per session is sufficient.

## Background

This project was born from a social science researcher's desire to build an "external brain" — a system where accumulated knowledge from papers, articles, and research notes could be cross-referenced by AI during daily work.

The key insight: **separate "writing" from "reading."** Claude App excels at understanding content and writing structured notes to Notion. Claude Code excels at reading files and synthesizing knowledge across many documents. A simple Python script bridges the gap.

### Related Articles (Zenn)

- [Building an "External Brain" with Claude × Notion (non-engineer edition)](https://zenn.dev/kajungbang/articles/5c00f3bf7d7416) — v1.0: Building the system
- [The "External Brain" That Fixed Its Own Weakness](https://zenn.dev/kajungbang/articles/fb31e447bcf14d) — v2.0: Session Log

## Acknowledgements

This project was built in collaboration with, and inspired by:

- [Anthropic Claude](https://anthropic.com) — AI partner and co-creator
- [Notion](https://www.notion.com) — knowledge base layer that makes it all possible
- [Andrej Karpathy](https://x.com/karpathy/status/2039805659525644595) — 
  whose X post on "LLM Knowledge Bases" sparked the initial idea
- [hooeem](https://x.com/hooeem/status/2041196025906418094) — 
  whose X article "How to create your own LLM knowledge bases today (full course)" also sparked the initial idea
- [Claude Code Studio](https://x.com/ClaudeCode_love/status/2042886840177557533) — 
  whose X article "Building an AI External Brain from Scratch with Claude Code × Obsidian: A Complete Guide by a Former OpenAI Employee" also sparked

## License

MIT License. See [LICENSE](LICENSE).

## Contributing

Issues and pull requests are welcome! This project especially values contributions from non-engineers and researchers in social sciences, humanities, and other fields.
