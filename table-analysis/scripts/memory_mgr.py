#!/usr/bin/env python3
"""Tiered memory manager for table-analysis skill.

Three-tier architecture (inspired by self-improving skill):
  HOT  — ~/.table-analysis/memory.json     (always loaded, ≤80 entries)
  WARM — ~/.table-analysis/domains/*.json  (loaded on context match)
  COLD — ~/.table-analysis/archive/*.json  (loaded on explicit query)

Corrections log: ~/.table-analysis/corrections.json (last 50, with promotion tracking)

Usage:
  python memory_mgr.py hot                              # Show HOT memory
  python memory_mgr.py set <category> <key> <value>     # Set HOT entry
  python memory_mgr.py correct <type> <what> <fix>      # Log a correction
  python memory_mgr.py relevant <query>                 # Search all tiers
  python memory_mgr.py promote <key>                    # Promote correction -> HOT
  python memory_mgr.py demote <key>                     # HOT -> WARM domain
  python memory_mgr.py stats                            # Tier statistics
  python memory_mgr.py compact                          # Merge duplicates, enforce limits
  python memory_mgr.py corrections [--last N]           # Show recent corrections
  python memory_mgr.py init                             # Initialize directory structure
  python memory_mgr.py clear                            # Clear all (with export)
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = Path.home() / ".table-analysis"
HOT_FILE = DATA_DIR / "memory.json"
CORRECTIONS_FILE = DATA_DIR / "corrections.json"
DOMAINS_DIR = DATA_DIR / "domains"
ARCHIVE_DIR = DATA_DIR / "archive"

HOT_LIMIT = 80
CORRECTIONS_LIMIT = 50
PROMOTE_THRESHOLD = 3       # corrections before asking to promote
WARM_DECAY_DAYS = 30        # unused HOT -> WARM
COLD_DECAY_DAYS = 90        # unused WARM -> COLD


def _load_json(path: Path) -> dict | list:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {} if path.suffix == ".json" and "corrections" not in path.name else []


def _save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_hot() -> dict:
    if HOT_FILE.exists():
        return json.loads(HOT_FILE.read_text(encoding="utf-8"))
    return {}


def _save_hot(data: dict):
    _save_json(HOT_FILE, data)


def _load_corrections() -> list:
    if CORRECTIONS_FILE.exists():
        return json.loads(CORRECTIONS_FILE.read_text(encoding="utf-8"))
    return []


def _save_corrections(data: list):
    _save_json(CORRECTIONS_FILE, data[-CORRECTIONS_LIMIT:])


def _load_domain(name: str) -> dict:
    p = DOMAINS_DIR / f"{name}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def _save_domain(name: str, data: dict):
    _save_json(DOMAINS_DIR / f"{name}.json", data)


def _now() -> str:
    return datetime.now().isoformat()


# ── Commands ─────────────────────────────────────────────────────────────────

def cmd_init(args):
    """Initialize the tiered directory structure."""
    for d in [DATA_DIR, DOMAINS_DIR, ARCHIVE_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    for f, default in [(HOT_FILE, {}), (CORRECTIONS_FILE, [])]:
        if not f.exists():
            _save_json(f, default)
    print(f"Initialized: {DATA_DIR}")
    print(f"  HOT:         {HOT_FILE}")
    print(f"  Corrections: {CORRECTIONS_FILE}")
    print(f"  WARM:        {DOMAINS_DIR}/")
    print(f"  COLD:        {ARCHIVE_DIR}/")


def cmd_hot(args):
    """Show HOT memory (always loaded)."""
    data = _load_hot()
    if not data:
        print("HOT memory is empty.")
        return
    total = sum(len(v) for v in data.values())
    print(f"# HOT Memory ({total} entries)\n")
    for cat, items in sorted(data.items()):
        print(f"## {cat}")
        for key, entry in items.items():
            val = entry["value"] if isinstance(entry, dict) else str(entry)
            used = entry.get("use_count", 0) if isinstance(entry, dict) else 0
            print(f"  - {key}: {val}  (used {used}x)")
        print()


def cmd_set(args):
    """Set an entry in HOT memory."""
    data = _load_hot()
    if args.category not in data:
        data[args.category] = {}
    existing = data[args.category].get(args.key)
    data[args.category][args.key] = {
        "value": args.value,
        "updated": _now(),
        "last_used": _now(),
        "use_count": (existing.get("use_count", 0) + 1) if existing else 1,
        "status": "confirmed" if args.confirmed else (existing.get("status", "tentative") if existing else "tentative"),
    }
    _save_hot(data)
    status = data[args.category][args.key]["status"]
    print(f"[HOT] [{args.category}] {args.key} = {args.value}  (status: {status})")


def cmd_correct(args):
    """Log a correction with promotion tracking."""
    corrections = _load_corrections()
    existing = next((c for c in corrections if c["key"] == args.what), None)
    if existing:
        existing["count"] += 1
        existing["last_seen"] = _now()
        existing["history"].append({"fix": args.fix, "time": _now()})
        if existing["count"] >= PROMOTE_THRESHOLD and existing["status"] == "tentative":
            existing["status"] = "pending_promotion"
            print(f"[CORRECTION] '{args.what}' corrected {existing['count']}x -> PENDING PROMOTION")
            print(f"  Run: python memory_mgr.py promote \"{args.what}\"")
        else:
            print(f"[CORRECTION] '{args.what}' updated (count: {existing['count']})")
    else:
        corrections.append({
            "key": args.what,
            "type": args.type,
            "fix": args.fix,
            "count": 1,
            "status": "tentative",
            "created": _now(),
            "last_seen": _now(),
            "history": [{"fix": args.fix, "time": _now()}],
        })
        print(f"[CORRECTION] Logged: [{args.type}] {args.what} -> {args.fix}")
    _save_corrections(corrections)


def cmd_corrections(args):
    """Show recent corrections."""
    corrections = _load_corrections()
    if not corrections:
        print("No corrections logged yet.")
        return
    last_n = corrections[-args.last:]
    print(f"# Recent Corrections (last {len(last_n)})\n")
    for c in reversed(last_n):
        status_icon = {"tentative": "?", "pending_promotion": "^", "promoted": "+", "rejected": "x"}.get(c["status"], " ")
        print(f"  [{status_icon}] ({c['type']}) {c['key']} -> {c['fix']}  (count: {c['count']}, status: {c['status']})")


def cmd_promote(args):
    """Promote a correction to HOT memory."""
    corrections = _load_corrections()
    target = next((c for c in corrections if c["key"] == args.key), None)
    if not target:
        print(f"Correction '{args.key}' not found.", file=sys.stderr)
        sys.exit(1)

    hot = _load_hot()
    cat = target["type"]
    if cat not in hot:
        hot[cat] = {}
    hot[cat][target["key"]] = {
        "value": target["fix"],
        "updated": _now(),
        "last_used": _now(),
        "use_count": target["count"],
        "status": "confirmed",
        "promoted_from": "corrections",
    }
    _save_hot(hot)
    target["status"] = "promoted"
    _save_corrections(corrections)
    print(f"[PROMOTED] '{target['key']}' -> HOT [{cat}]  (value: {target['fix']})")


def cmd_demote(args):
    """Move a HOT entry to WARM (domain file)."""
    hot = _load_hot()
    domain = args.domain or "general"
    found = False
    for cat, items in hot.items():
        if args.key in items:
            entry = items.pop(args.key)
            if not items:
                del hot[cat]
            warm = _load_domain(domain)
            if cat not in warm:
                warm[cat] = {}
            warm[cat][args.key] = entry
            warm[cat][args.key]["demoted_at"] = _now()
            _save_domain(domain, warm)
            _save_hot(hot)
            print(f"[DEMOTED] '{args.key}' -> WARM domains/{domain}.json")
            found = True
            break
    if not found:
        print(f"Key '{args.key}' not found in HOT memory.", file=sys.stderr)
        sys.exit(1)


def cmd_relevant(args):
    """Search all tiers for entries matching query words."""
    query_words = set(args.query.lower().split())
    results = {"hot": {}, "warm": {}, "corrections": []}

    # HOT
    for cat, items in _load_hot().items():
        for key, entry in items.items():
            val = entry["value"] if isinstance(entry, dict) else str(entry)
            if any(w in f"{cat} {key} {val}".lower() for w in query_words):
                if cat not in results["hot"]:
                    results["hot"][cat] = {}
                results["hot"][cat][key] = val

    # WARM (domains)
    if DOMAINS_DIR.exists():
        for f in DOMAINS_DIR.glob("*.json"):
            domain = _load_domain(f.stem)
            for cat, items in domain.items():
                for key, entry in items.items():
                    val = entry["value"] if isinstance(entry, dict) else str(entry)
                    if any(w in f"{cat} {key} {val}".lower() for w in query_words):
                        label = f"warm/{f.stem}"
                        if label not in results["warm"]:
                            results["warm"][label] = {}
                        results["warm"][label][key] = val

    # Corrections
    for c in _load_corrections():
        text = f"{c['type']} {c['key']} {c['fix']}".lower()
        if any(w in text for w in query_words):
            results["corrections"].append(f"[{c['type']}] {c['key']} -> {c['fix']} (x{c['count']})")

    if not any(results.values()):
        print("No relevant memory found across any tier.")
        return
    print(json.dumps({k: v for k, v in results.items() if v}, ensure_ascii=False, indent=2))


def cmd_use(args):
    """Mark an entry as used (bump use_count and last_used)."""
    hot = _load_hot()
    for cat, items in hot.items():
        if args.key in items:
            entry = items[args.key]
            entry["use_count"] = entry.get("use_count", 0) + 1
            entry["last_used"] = _now()
            _save_hot(hot)
            print(f"[USED] {args.key} (count: {entry['use_count']})")
            return
    print(f"Key '{args.key}' not found in HOT.", file=sys.stderr)


def cmd_compact(args):
    """Enforce HOT limit by demoting least-used entries; trim corrections."""
    hot = _load_hot()
    all_entries = []
    for cat, items in hot.items():
        for key, entry in items.items():
            all_entries.append((cat, key, entry))

    if len(all_entries) > HOT_LIMIT:
        all_entries.sort(key=lambda e: (e[2].get("status") == "confirmed", e[2].get("use_count", 0)), reverse=True)
        keep = all_entries[:HOT_LIMIT]
        demote = all_entries[HOT_LIMIT:]
        new_hot = {}
        for cat, key, entry in keep:
            new_hot.setdefault(cat, {})[key] = entry
        _save_hot(new_hot)
        warm = _load_domain("overflow")
        for cat, key, entry in demote:
            warm.setdefault(cat, {})[key] = entry
            entry["demoted_at"] = _now()
        _save_domain("overflow", warm)
        print(f"[COMPACT] Kept {len(keep)} in HOT, demoted {len(demote)} to WARM/overflow")
    else:
        print(f"[COMPACT] HOT has {len(all_entries)}/{HOT_LIMIT} entries, no compaction needed.")

    corrections = _load_corrections()
    if len(corrections) > CORRECTIONS_LIMIT:
        trimmed = len(corrections) - CORRECTIONS_LIMIT
        _save_corrections(corrections)
        print(f"[COMPACT] Trimmed {trimmed} old corrections.")


def cmd_stats(args):
    """Show tier statistics."""
    hot = _load_hot()
    hot_count = sum(len(v) for v in hot.values())
    corrections = _load_corrections()
    pending = sum(1 for c in corrections if c.get("status") == "pending_promotion")

    warm_files = list(DOMAINS_DIR.glob("*.json")) if DOMAINS_DIR.exists() else []
    warm_count = 0
    for f in warm_files:
        d = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
        warm_count += sum(len(v) for v in d.values()) if isinstance(d, dict) else 0

    cold_files = list(ARCHIVE_DIR.glob("*.json")) if ARCHIVE_DIR.exists() else []

    print(f"# Table-Analysis Memory Stats\n")
    print(f"  HOT  (always loaded):   {hot_count} entries  ({HOT_LIMIT} max)")
    print(f"  WARM (load on demand):  {warm_count} entries across {len(warm_files)} domain files")
    print(f"  COLD (archived):        {len(cold_files)} archive files")
    print(f"  Corrections log:        {len(corrections)} entries ({pending} pending promotion)")


def cmd_clear(args):
    """Clear all memory (with export option)."""
    if args.export:
        export = {
            "hot": _load_hot(),
            "corrections": _load_corrections(),
            "domains": {},
        }
        if DOMAINS_DIR.exists():
            for f in DOMAINS_DIR.glob("*.json"):
                export["domains"][f.stem] = json.loads(f.read_text(encoding="utf-8"))
        out = DATA_DIR / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        _save_json(out, export)
        print(f"Exported to: {out}")

    _save_json(HOT_FILE, {})
    _save_json(CORRECTIONS_FILE, [])
    if DOMAINS_DIR.exists():
        for f in DOMAINS_DIR.glob("*.json"):
            f.unlink()
    print("All memory cleared.")


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Table-analysis tiered memory manager")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Initialize directory structure").set_defaults(func=cmd_init)

    sub.add_parser("hot", help="Show HOT memory").set_defaults(func=cmd_hot)

    p = sub.add_parser("set", help="Set a HOT memory entry")
    p.add_argument("category", help="preferences|analysis_patterns|domain_knowledge|user_context")
    p.add_argument("key", help="Short key name")
    p.add_argument("value", help="Value to store")
    p.add_argument("--confirmed", action="store_true", help="Mark as confirmed immediately")
    p.set_defaults(func=cmd_set)

    p = sub.add_parser("correct", help="Log a correction")
    p.add_argument("type", help="Type: metric|format|method|interpretation|domain")
    p.add_argument("what", help="What was wrong")
    p.add_argument("fix", help="Correct approach")
    p.set_defaults(func=cmd_correct)

    p = sub.add_parser("corrections", help="Show recent corrections")
    p.add_argument("--last", type=int, default=20)
    p.set_defaults(func=cmd_corrections)

    p = sub.add_parser("promote", help="Promote correction to HOT")
    p.add_argument("key", help="Correction key to promote")
    p.set_defaults(func=cmd_promote)

    p = sub.add_parser("demote", help="Demote HOT entry to WARM")
    p.add_argument("key")
    p.add_argument("--domain", default="general", help="Target domain file")
    p.set_defaults(func=cmd_demote)

    p = sub.add_parser("relevant", help="Search all tiers")
    p.add_argument("query")
    p.set_defaults(func=cmd_relevant)

    p = sub.add_parser("use", help="Mark entry as used")
    p.add_argument("key")
    p.set_defaults(func=cmd_use)

    sub.add_parser("compact", help="Enforce limits, demote overflow").set_defaults(func=cmd_compact)
    sub.add_parser("stats", help="Tier statistics").set_defaults(func=cmd_stats)

    p = sub.add_parser("clear", help="Clear all memory")
    p.add_argument("--export", action="store_true", help="Export before clearing")
    p.set_defaults(func=cmd_clear)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
