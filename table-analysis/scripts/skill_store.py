#!/usr/bin/env python3
"""Learned skill storage with confirmation flow and decay tracking.

Skills evolve through stages:
  tentative (1x) -> emerging (2x) -> pending (3x, ask user) -> confirmed -> archived

Data lives in ~/.table-analysis/learned_skills.json.

Usage:
  python skill_store.py list                               # List all with status
  python skill_store.py get <name>                         # Full skill details
  python skill_store.py add <name> <description> <pattern> # Add (tentative)
  python skill_store.py confirm <name>                     # Promote to confirmed
  python skill_store.py use <name>                         # Record usage, auto-evolve stage
  python skill_store.py match <query>                      # Find skills matching query
  python skill_store.py reflect <name> <note>              # Add reflection/improvement note
  python skill_store.py decay                              # Check for unused skills to archive
  python skill_store.py delete <name>                      # Delete a skill
  python skill_store.py clear                              # Clear all
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = Path.home() / ".table-analysis"
SKILLS_FILE = DATA_DIR / "learned_skills.json"

PROMOTE_THRESHOLD = 3       # uses before asking to confirm
DECAY_WARN_DAYS = 30        # warn about unused skills
DECAY_ARCHIVE_DAYS = 90     # archive unused skills


def _load() -> list:
    if SKILLS_FILE.exists():
        return json.loads(SKILLS_FILE.read_text(encoding="utf-8"))
    return []


def _save(data: list):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SKILLS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _now() -> str:
    return datetime.now().isoformat()


def _days_since(iso_str: str) -> int:
    try:
        dt = datetime.fromisoformat(iso_str)
        return (datetime.now() - dt).days
    except (ValueError, TypeError):
        return 999


def _status_icon(status: str) -> str:
    return {"tentative": "?", "emerging": "~", "pending": "^", "confirmed": "+", "archived": "_"}.get(status, " ")


# ── Commands ─────────────────────────────────────────────────────────────────

def cmd_list(args):
    skills = _load()
    if not skills:
        print("No learned skills yet.")
        return
    confirmed = [s for s in skills if s.get("status") == "confirmed"]
    active = [s for s in skills if s.get("status") in ("tentative", "emerging", "pending")]
    archived = [s for s in skills if s.get("status") == "archived"]

    print(f"# Learned Skills ({len(skills)} total)\n")
    if confirmed:
        print("## Confirmed")
        for s in confirmed:
            print(f"  [+] {s['name']}: {s['description']}  (used {s.get('use_count', 0)}x)")
    if active:
        print("## Active (evolving)")
        for s in active:
            icon = _status_icon(s.get("status", "tentative"))
            days = _days_since(s.get("last_used", s.get("created", "")))
            print(f"  [{icon}] {s['name']}: {s['description']}  (used {s.get('use_count', 0)}x, {s['status']}, {days}d ago)")
    if archived:
        print("## Archived")
        for s in archived:
            print(f"  [_] {s['name']}: {s['description']}")


def cmd_get(args):
    skills = _load()
    skill = next((s for s in skills if s["name"] == args.name), None)
    if not skill:
        print(f"Skill '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(skill, ensure_ascii=False, indent=2))


def cmd_add(args):
    skills = _load()
    existing = next((s for s in skills if s["name"] == args.name), None)
    if existing:
        existing["description"] = args.description
        existing["pattern"] = args.pattern
        existing["updated"] = _now()
        if existing.get("reflections"):
            existing["reflections"].append({"note": "Pattern updated", "time": _now()})
        print(f"Updated skill: {args.name} (status: {existing['status']})")
    else:
        skills.append({
            "name": args.name,
            "description": args.description,
            "pattern": args.pattern,
            "status": "tentative",
            "created": _now(),
            "updated": _now(),
            "last_used": _now(),
            "use_count": 0,
            "reflections": [],
        })
        print(f"Added skill: {args.name} (status: tentative)")
    _save(skills)


def cmd_confirm(args):
    skills = _load()
    skill = next((s for s in skills if s["name"] == args.name), None)
    if not skill:
        print(f"Skill '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    skill["status"] = "confirmed"
    skill["confirmed_at"] = _now()
    _save(skills)
    print(f"[CONFIRMED] {args.name}: {skill['description']}")


def cmd_use(args):
    """Record usage and auto-evolve stage."""
    skills = _load()
    skill = next((s for s in skills if s["name"] == args.name), None)
    if not skill:
        print(f"Skill '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    skill["use_count"] = skill.get("use_count", 0) + 1
    skill["last_used"] = _now()
    count = skill["use_count"]
    old_status = skill["status"]

    if old_status == "archived":
        skill["status"] = "tentative"
        print(f"[REVIVED] {args.name} reactivated from archive (used {count}x)")
    elif old_status == "tentative" and count >= 2:
        skill["status"] = "emerging"
        print(f"[EVOLVED] {args.name}: tentative -> emerging (used {count}x)")
    elif old_status == "emerging" and count >= PROMOTE_THRESHOLD:
        skill["status"] = "pending"
        print(f"[EVOLVED] {args.name}: emerging -> pending confirmation (used {count}x)")
        print(f"  This skill has been useful {count} times. Confirm with:")
        print(f"  python skill_store.py confirm \"{args.name}\"")
    else:
        print(f"[USED] {args.name} (count: {count}, status: {skill['status']})")

    _save(skills)


def cmd_match(args):
    """Find skills whose name, description, or pattern match query words."""
    skills = _load()
    if not skills:
        print("No learned skills yet.")
        return
    query_words = set(args.query.lower().split())
    matches = []
    for s in skills:
        if s.get("status") == "archived":
            continue
        text = f"{s['name']} {s['description']} {s['pattern']}".lower()
        if any(w in text for w in query_words):
            matches.append(s)

    # Sort: confirmed first, then by use_count
    matches.sort(key=lambda s: (s.get("status") == "confirmed", s.get("use_count", 0)), reverse=True)

    if matches:
        print(f"# Matching Skills ({len(matches)} found)\n")
        for s in matches:
            icon = _status_icon(s.get("status", "tentative"))
            print(f"  [{icon}] {s['name']}: {s['description']}  (used {s.get('use_count', 0)}x, {s['status']})")
            print(f"      Pattern: {s['pattern'][:200]}")
            print()
    else:
        print("No matching skills found.")


def cmd_reflect(args):
    """Add a reflection/improvement note to a skill."""
    skills = _load()
    skill = next((s for s in skills if s["name"] == args.name), None)
    if not skill:
        print(f"Skill '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    if "reflections" not in skill:
        skill["reflections"] = []
    skill["reflections"].append({"note": args.note, "time": _now()})
    skill["updated"] = _now()
    _save(skills)
    print(f"[REFLECTION] Added note to '{args.name}': {args.note}")


def cmd_decay(args):
    """Check for skills that should be warned or archived due to disuse."""
    skills = _load()
    if not skills:
        print("No skills to check.")
        return
    warnings = []
    archived = []
    for s in skills:
        if s.get("status") in ("archived", "confirmed"):
            continue
        days = _days_since(s.get("last_used", s.get("created", "")))
        if days >= DECAY_ARCHIVE_DAYS:
            s["status"] = "archived"
            s["archived_at"] = _now()
            archived.append(s["name"])
        elif days >= DECAY_WARN_DAYS:
            warnings.append((s["name"], days))

    _save(skills)
    if archived:
        print(f"[ARCHIVED] {len(archived)} skills: {', '.join(archived)}")
    if warnings:
        print(f"[WARNING] {len(warnings)} skills unused >30 days:")
        for name, days in warnings:
            print(f"  - {name} ({days} days)")
    if not archived and not warnings:
        print("All skills are active.")


def cmd_delete(args):
    skills = _load()
    before = len(skills)
    skills = [s for s in skills if s["name"] != args.name]
    if len(skills) == before:
        print(f"Skill '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    _save(skills)
    print(f"Deleted: {args.name}")


def cmd_clear(args):
    _save([])
    print("All learned skills cleared.")


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Table-analysis learned skill store")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all skills with status").set_defaults(func=cmd_list)

    p = sub.add_parser("get", help="Full skill details")
    p.add_argument("name")
    p.set_defaults(func=cmd_get)

    p = sub.add_parser("add", help="Add or update a skill (starts as tentative)")
    p.add_argument("name", help="Short descriptive name")
    p.add_argument("description", help="What this skill does")
    p.add_argument("pattern", help="Reusable analysis pattern (steps/code/prompt)")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("confirm", help="Promote to confirmed")
    p.add_argument("name")
    p.set_defaults(func=cmd_confirm)

    p = sub.add_parser("use", help="Record usage (auto-evolves stage)")
    p.add_argument("name")
    p.set_defaults(func=cmd_use)

    p = sub.add_parser("match", help="Find skills matching query")
    p.add_argument("query")
    p.set_defaults(func=cmd_match)

    p = sub.add_parser("reflect", help="Add improvement note to skill")
    p.add_argument("name")
    p.add_argument("note", help="Reflection or improvement note")
    p.set_defaults(func=cmd_reflect)

    sub.add_parser("decay", help="Check/archive unused skills").set_defaults(func=cmd_decay)

    p = sub.add_parser("delete", help="Delete a skill")
    p.add_argument("name")
    p.set_defaults(func=cmd_delete)

    sub.add_parser("clear", help="Clear all skills").set_defaults(func=cmd_clear)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
