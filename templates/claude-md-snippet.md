# CLAUDE.md Snippet: External Brain Integration

Add the following section to your `CLAUDE.md` (or `~/.claude/CLAUDE.md` for global settings).

---

```markdown
## External Brain (Notion KB)
- **Knowledge Base**: `~/notion_kb/` (Raw Sources DB + Wiki DB Knowledge Layer)
- **Freshness Check**: At session start, check sync timestamp in `~/notion_kb/INDEX.md`.
  If older than 24 hours, run `python3 ~/scripts/sync_notion_kb.py`
- **QUERY Cycle**: When questions relate to your research domains,
  cross-reference `~/notion_kb/wiki/INDEX.md` → individual articles to inform your answers.
- **Schema Definition**: `~/notion_kb/SCHEMA.md`
```

---

## How It Works

1. **Session start**: Claude Code automatically checks when the KB was last synced.
   If stale (>24h), it re-syncs from Notion before proceeding.

2. **During conversation**: When you ask about topics covered in your KB,
   Claude Code reads the local Markdown files and incorporates that knowledge.

3. **Role division**:
   - **Claude (app)**: INGEST / COMPILE / LINT — writes to Notion Wiki DB
   - **Claude Code**: QUERY — reads local copy, cross-references, synthesizes answers
