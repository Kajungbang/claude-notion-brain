#!/usr/bin/env python3
"""
Notion Knowledge Base → Local Markdown Sync Script

Syncs two Notion databases (Raw layer + Wiki layer) to local Markdown files
for use as Claude Code's knowledge base.

No external dependencies — uses only Python standard library.

Usage:
    1. Copy config.json.example to config.json and fill in your settings
    2. Run: python3 sync_notion_kb.py
"""

import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config.json"


def load_config():
    if not CONFIG_FILE.exists():
        print(f"Error: {CONFIG_FILE} not found.")
        print(f"Copy config.json.example to config.json and fill in your settings.")
        raise SystemExit(1)
    with open(CONFIG_FILE) as f:
        return json.load(f)


def load_api_key(config):
    env_file = Path(config["env_file"]).expanduser()
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith("NOTION_API_KEY="):
                return line.split("=", 1)[1]
    raise RuntimeError(f"NOTION_API_KEY not found in {env_file}")


API_KEY = None
API_VERSION = "2022-06-28"


def notion_request(endpoint, body=None):
    global API_KEY
    url = f"https://api.notion.com/v1/{endpoint}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method="POST" if body else "GET")
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Notion-Version", API_VERSION)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get_all_pages(db_id):
    pages = []
    has_more = True
    start_cursor = None
    while has_more:
        body = {"page_size": 100}
        if start_cursor:
            body["start_cursor"] = start_cursor
        result = notion_request(f"databases/{db_id}/query", body)
        pages.extend(result["results"])
        has_more = result.get("has_more", False)
        start_cursor = result.get("next_cursor")
    return pages


# --- Property extractors ---

def extract_text(rich_text_list):
    return "".join(t.get("plain_text", "") for t in rich_text_list)


def extract_select(prop):
    sel = prop.get("select")
    return sel["name"] if sel else ""


def extract_multi_select(prop):
    return [s["name"] for s in prop.get("multi_select", [])]


def extract_date(prop):
    d = prop.get("date")
    return d["start"] if d else ""


def extract_url(prop):
    return prop.get("url") or ""


def sanitize_filename(title):
    name = re.sub(r'[\\/*?:"<>|]', "_", title)
    return name[:80].strip()


def get_title(props, field_name="タイトル"):
    title_prop = props.get(field_name, {})
    return extract_text(title_prop.get("title", []))


# --- Generic page-to-markdown converter ---

def page_to_markdown(page, field_map):
    """Convert a Notion page to Markdown using a field mapping.

    field_map is a list of dicts:
        {"label": "Display Label", "field": "Notion property name",
         "type": "text|select|multi_select|date|url", "optional": True/False}
    """
    props = page["properties"]
    title = ""
    lines = []

    for fm in field_map:
        field = fm["field"]
        prop = props.get(field, {})
        ftype = fm["type"]

        if ftype == "title":
            title = extract_text(prop.get("title", []))
            lines.append(f"# {title}")
            lines.append("")
            continue

        if ftype == "text":
            val = extract_text(prop.get("rich_text", []))
        elif ftype == "select":
            val = extract_select(prop)
        elif ftype == "multi_select":
            items = extract_multi_select(prop)
            val = ", ".join(items) if items else ""
        elif ftype == "date":
            val = extract_date(prop)
        elif ftype == "url":
            val = extract_url(prop)
        else:
            val = ""

        if fm.get("optional") and not val:
            continue

        if fm.get("section"):
            lines.extend(["", f"## {fm['label']}", "", val, ""])
        else:
            lines.append(f"- **{fm['label']}**: {val}")

    return title, "\n".join(lines)


# --- Index generators ---

def generate_index(db_name, entries, group_key, display_fn):
    lines = [
        f"# {db_name}（sync: {datetime.now().strftime('%Y-%m-%d %H:%M')}）",
        "",
        f"Total entries: {len(entries)}",
        "",
    ]
    grouped = {}
    for e in entries:
        for g in (e.get(group_key) or ["Uncategorized"]):
            grouped.setdefault(g, []).append(e)

    for group in sorted(grouped.keys()):
        lines.append(f"## {group}")
        lines.append("")
        for e in grouped[group]:
            lines.append(f"- {display_fn(e)}")
        lines.append("")
    return "\n".join(lines)


def generate_master_index(db_results):
    lines = [
        f"# Notion Knowledge Base（sync: {datetime.now().strftime('%Y-%m-%d %H:%M')}）",
        "",
        "| DB | Count | INDEX |",
        "|---|---|---|",
    ]
    for name, count, subdir in db_results:
        lines.append(f"| {name} | {count} | [{subdir}/INDEX.md]({subdir}/INDEX.md) |")

    lines.extend([
        "",
        "## Usage",
        "- Overview: this file → each DB's INDEX.md",
        "- Details: individual Markdown files in each subdirectory",
        f"- Re-sync: `python3 {Path(__file__).name}`",
    ])
    return "\n".join(lines)


# --- Sync logic ---

def sync_database(db_config, output_dir):
    db_id = db_config["id"]
    db_name = db_config["name"]
    subdir = db_config["subdir"]
    field_map = db_config["fields"]
    group_key = db_config.get("group_by", "tags")

    out_dir = output_dir / subdir
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[{db_name}] Fetching...")
    pages = get_all_pages(db_id)
    print(f"  {len(pages)} pages retrieved")

    entries = []
    for page in pages:
        title, md = page_to_markdown(page, field_map)
        if not title:
            continue

        filename = sanitize_filename(title) + ".md"
        with open(out_dir / filename, "w", encoding="utf-8") as f:
            f.write(md)

        props = page["properties"]
        entry = {"title": title}
        for fm in field_map:
            if fm["type"] == "title":
                continue
            prop = props.get(fm["field"], {})
            if fm["type"] == "multi_select":
                entry[fm["field"]] = extract_multi_select(prop)
            elif fm["type"] == "select":
                entry[fm["field"]] = extract_select(prop)
        entries.append(entry)

    display_fn = db_config.get("display_fn", lambda e: e["title"])
    if isinstance(display_fn, str):
        fmt = display_fn
        display_fn = lambda e, f=fmt: f.format(**{k: (', '.join(v) if isinstance(v, list) else v) for k, v in e.items()})

    index_md = generate_index(db_name, entries, group_key, display_fn)
    with open(out_dir / "INDEX.md", "w", encoding="utf-8") as f:
        f.write(index_md)

    print(f"  {len(entries)} entries written to {out_dir}")
    return db_name, len(entries), subdir


def main():
    global API_KEY
    config = load_config()
    API_KEY = load_api_key(config)
    output_dir = Path(config["output_dir"]).expanduser()
    output_dir.mkdir(exist_ok=True)

    db_results = []
    for db_config in config["databases"]:
        result = sync_database(db_config, output_dir)
        db_results.append(result)

    master = generate_master_index(db_results)
    with open(output_dir / "INDEX.md", "w", encoding="utf-8") as f:
        f.write(master)

    total = sum(r[1] for r in db_results)
    print(f"\nDone: {total} entries total")
    print(f"Master INDEX: {output_dir / 'INDEX.md'}")


if __name__ == "__main__":
    main()
