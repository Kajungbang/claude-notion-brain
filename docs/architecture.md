# Architecture / アーキテクチャ

## System Overview / システム全体像

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR BRAIN (You)                      │
│         Collect articles, papers, URLs, ideas            │
└──────────────┬──────────────────────────────┬────────────┘
               │ feed                         │ ask
               ▼                              ▼
┌──────────────────────┐        ┌──────────────────────────┐
│   Claude App         │        │   Claude Code            │
│   (Mobile/Desktop)   │        │   (Terminal/IDE)         │
│                      │        │                          │
│   ┌────────────────┐ │        │   ┌──────────────────┐   │
│   │ Notion MCP     │ │        │   │ Local Markdown   │   │
│   │ (read + write) │ │        │   │ ~/notion_kb/     │   │
│   └───────┬────────┘ │        │   │ (read only)      │   │
│           │          │        │   └────────▲─────────┘   │
│   INGEST  │ COMPILE  │        │            │  QUERY      │
│   LINT    │          │        │   Cross-reference &      │
└───────────┼──────────┘        │   synthesize answers     │
            │                   └────────────┼─────────────┘
            ▼                                │
┌───────────────────────────────────────────────────────────┐
│                      Notion                               │
│                                                           │
│  ┌─────────────────┐    ┌──────────────────────────────┐  │
│  │ Raw Sources DB  │───▶│ Wiki DB (Knowledge Layer)    │  │
│  │ (raw layer)     │    │ (wiki layer)                 │  │
│  │                 │    │                              │  │
│  │ • URLs          │    │ • Source Summaries           │  │
│  │ • Papers        │    │ • Concept Articles           │  │
│  │ • SNS posts     │    │ • Synthesis                  │  │
│  │ • PDF notes     │    │ • Q&A Outputs                │  │
│  └─────────────────┘    └──────────────────────────────┘  │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Schema Definition (schema layer)                    │  │
│  │ Rules for AI operations                             │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Session Log (dynamic memory) ← NEW in v2.0         │  │
│  │ • What was done (INGEST/COMPILE history)            │  │
│  │ • What's pending                                    │  │
│  │ • Wiki DB statistics                                │  │
│  │ → Updated by Claude App at end of each session      │  │
│  │ → Read by Claude App at start of next session       │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
            │
            │  python3 sync_notion_kb.py
            │  (Notion API → local Markdown)
            ▼
┌───────────────────────────────────────────────────────────┐
│  ~/notion_kb/                                             │
│  ├── INDEX.md          (master index)                     │
│  ├── SCHEMA.md         (operation rules)                  │
│  ├── info/             (raw sources, read-only copies)    │
│  │   ├── INDEX.md                                         │
│  │   └── *.md                                             │
│  └── wiki/             (knowledge layer copies)           │
│      ├── INDEX.md                                         │
│      └── *.md                                             │
└───────────────────────────────────────────────────────────┘
```

## Role Division / 役割分担

| Role | Environment | What it does |
|---|---|---|
| **Collect** | You (human) | Find interesting articles, papers, URLs |
| **INGEST** | Claude App + Notion MCP | Summarize sources, create wiki entries |
| **COMPILE** | Claude App + Notion MCP | Update existing articles, add cross-links |
| **QUERY** | Claude Code + local files | Cross-reference knowledge, answer questions |
| **LINT** | Claude App + Notion MCP | Check consistency, flag contradictions |
| **SESSION** | Claude App + Notion | Update session log (dynamic memory) at session end |
| **SYNC** | Python script (cron/manual) | Pull Notion → local Markdown for Claude Code |

## v2.0: 3+1 Layer Architecture / 3層+1アーキテクチャ

The original 3-layer architecture (Raw, Wiki, Schema) stores **static** knowledge. But session-to-session context — what was done, what's pending — was lost between conversations.

**Session Log** adds a **dynamic memory** layer: Claude App updates it at the end of each session, and reads it at the start of the next. This means "pick up where we left off" just works.

| Layer | Type | Purpose |
|---|---|---|
| Raw Sources DB | Static | Original materials |
| Wiki DB | AI-maintained | Integrated knowledge |
| Schema | Static | Operation rules |
| **Session Log** | **Dynamic** | **Work-in-progress state** |

## Why This Architecture? / なぜこの構成か

### Problem / 課題
- Claude Code (CLI) cannot reliably connect to Notion MCP due to OAuth token refresh issues
- Claude App (mobile/desktop) can connect to Notion but lacks file system access and advanced coding
- Knowledge scattered across tools is hard to use cross-referentially

### Solution / 解決策
- **Write** via Claude App (stable Notion MCP connection)
- **Read** via Claude Code (local Markdown copies, zero auth issues)
- **Sync** via simple Python script (no dependencies, just stdlib)

### Benefits / メリット
- No external dependencies (Python standard library only)
- Works offline after sync
- Claude Code can cross-reference 100+ articles in seconds
- Your knowledge base grows organically through daily use
