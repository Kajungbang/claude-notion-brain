# KB Schema Definition

> This page defines the schema for your personal Knowledge Base.
> Paste this into Claude's Project Instructions or reference it from CLAUDE.md.

---

## Overview

**Purpose**: Build and maintain a personal knowledge base centered on your research domain.

**3-Layer Architecture**:

- `Raw Sources DB` (raw layer): Original sources and materials. AI reads but never modifies.
- `Wiki DB (Knowledge Layer)` (wiki layer): Integrated knowledge generated and maintained by AI.
- This page (schema layer): Rules and structural definitions for AI operations.

---

## 4 Operation Cycles

### INGEST (New material intake)

1. Read new entries from Raw Sources DB
2. Create a Source Summary page in Wiki DB (Type: Source Summary)
3. Concepts mentioned in 2+ sources → create Concept Article
4. Mentioned only once → create Stub
5. Update Master Index

### COMPILE (Wiki maintenance)

1. Append new information to existing Concept Articles (never overwrite)
2. Add links between related pages
3. Verify Master Index consistency

### QUERY (Cross-reference search)

1. Identify relevant pages via Master Index
2. Cross-reference related pages to synthesize answers
3. Save as Q&A Output in Wiki DB

### LINT (Health check)

1. Flag contradictory statements with ⚠️
2. Identify orphan pages (no incoming links)
3. Check for pages not updated in 6+ months
4. Save report to Wiki DB (Type: Q&A Output)

---

## Page Creation Criteria

| Condition | Action |
| --- | --- |
| Mentioned in 2+ sources | Create Concept Article (500-1500 chars) |
| 1 source only | Create Stub (1-2 sentences) |
| Important person/org/tool | Create Person/Org page |
| Cross-cutting analysis | Create Synthesis page |

## Quality Standards

- Source Summary: 200-500 chars, summarize (don't copy)
- Concept Article: 500-1500 chars, definition sentence at the top
- Contradictions: flag with ⚠️, present both sides
- Confidence: established (multiple sources) / emerging (1 source) / speculative (inference)

---

## Tag System

**Domain tags**: _(customize for your field — e.g., LLM / Qualitative Analysis / Marketing / Statistics)_

**Project tags**: _(customize — e.g., Project A / Paper B / Tool Evaluation)_

---

## Important Rules

- NEVER edit Raw Sources DB (raw layer) pages
- Use Wiki DB's "Source" field to link back to Raw Sources DB
- Keep this schema under ~80 lines (context window budget)
