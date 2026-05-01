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

### v2.0: Session Log (Dynamic Memory)

If you use Claude App for INGEST/COMPILE work, add this rule to Claude App's Project Instructions:

```markdown
## Session Log (Dynamic Memory)
- At the end of each session, update the Session Log page in Notion with:
  completed items, new pending items, and Wiki DB statistics.
- At the start of each session, read the Session Log to restore context.
- The Session Log must be a regular page (not a Wiki page) — Wiki pages cannot be written via MCP.
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
