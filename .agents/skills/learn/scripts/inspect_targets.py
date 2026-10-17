#!/usr/bin/env python3
"""Read-only inventory of customization targets for the `learn` skill.

Reports which rule files and skill files already exist, and which of them
already cover a topic, so an agent never guesses at existing coverage.

This script only reads. It creates, modifies, and deletes nothing.

Usage:
    python inspect_targets.py --workspace .
    python inspect_targets.py --workspace . --global --topic "powershell"
    python inspect_targets.py --workspace . --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Rule files: single-file customizations that are read as standing constraints.
# Coverage is deliberately broad — a workspace that keeps its rules somewhere
# other than AGENTS.md must not be nudged into creating an AGENTS.md duplicate.
RULE_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "RULES.md",
    "CONVENTIONS.md",
    "CONTRIBUTING.md",
    ".cursorrules",
    ".windsurfrules",
    ".clinerules",
    ".rules",
    os.path.join(".github", "copilot-instructions.md"),
    os.path.join(".cursor", "rules", ".cursorrules"),
)

# Rule directories: every *.md inside is a rule file.
RULE_DIRS = (
    "rules",
    ".rules",
    ".clinerules",
    os.path.join(".agent", "rules"),
    os.path.join(".agents", "rules"),
    os.path.join(".cursor", "rules"),
    os.path.join(".github", "instructions"),
)

# Skill roots: each immediate subdirectory may hold a SKILL.md.
SKILL_ROOTS = (
    "skills",
    os.path.join(".agent", "skills"),
    os.path.join(".agents", "skills"),
    os.path.join(".claude", "skills"),
    os.path.join(".opencode", "skills"),
)

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".next", "dist", "build"}

MAX_READ_BYTES = 512 * 1024
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def read_text(path: Path) -> str:
    try:
        if path.stat().st_size > MAX_READ_BYTES:
            return ""
        # utf-8-sig also strips a leading BOM, which Windows editors add often
        # enough that a frontmatter regex anchored at ^--- would otherwise miss.
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""


def parse_frontmatter(text: str) -> dict:
    """Return the leading YAML frontmatter as a flat dict, ignoring nested keys."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    fields: dict = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.startswith((" ", "\t", "#")):
            continue
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip()
    return fields


def collect_rule_files(root: Path) -> list:
    found = []
    for rel in RULE_FILES:
        path = root / rel
        if path.is_file():
            found.append(path)
    dirs = [root / rel for rel in RULE_DIRS]
    # A rule directory passed in directly (e.g. ~/.agents/rules) is already a
    # rule dir, so it must not have "rules" appended to it again.
    if root.name in ("rules", ".rules", ".clinerules", "instructions"):
        dirs.insert(0, root)
    for directory in dirs:
        if directory.is_dir():
            found.extend(sorted(p for p in directory.glob("*.md") if p.is_file()))
    # De-duplicate, preserving order.
    seen = set()
    unique = []
    for path in found:
        key = str(path).lower()
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def collect_skill_files(root: Path) -> list:
    """Return SKILL.md files, descending at most one level into each skill root."""
    roots = [root / rel for rel in SKILL_ROOTS]
    # A skills root passed in directly (e.g. ~/.agents/skills) must not have
    # "skills" appended to it again.
    if root.name == "skills":
        roots.insert(0, root)
    found = []
    for directory in roots:
        if not directory.is_dir():
            continue
        for entry in sorted(directory.iterdir()):
            if not entry.is_dir() or entry.name in SKIP_DIRS:
                continue
            candidate = entry / "SKILL.md"
            if candidate.is_file():
                found.append(candidate)
            else:
                # One more level, for grouped roots such as skills/<domain>/<name>/.
                for nested in sorted(p for p in entry.iterdir() if p.is_dir()):
                    deeper = nested / "SKILL.md"
                    if deeper.is_file():
                        found.append(deeper)
    # De-duplicate, preserving order.
    seen = set()
    unique = []
    for path in found:
        key = str(path).lower()
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def match_topic(path: Path, text: str, pattern: re.Pattern) -> list:
    hits = []
    for number, line in enumerate(text.splitlines(), start=1):
        if pattern.search(line):
            hits.append({"line": number, "text": line.strip()[:200]})
    return hits


def describe(path: Path, topic_re, topic: str) -> dict:
    text = read_text(path)
    entry = {
        "path": str(path),
        "kind": "skill" if path.name == "SKILL.md" and path.parent.name != "rules" else "rule",
        "bytes": path.stat().st_size if path.exists() else 0,
    }
    if entry["kind"] == "skill":
        front = parse_frontmatter(text)
        entry["name"] = front.get("name", "")
        entry["description"] = front.get("description", "")
    if topic_re is not None:
        entry["topic_hits"] = match_topic(path, text, topic_re)
        entry["topic_match_count"] = len(entry["topic_hits"])
    return entry


def global_roots() -> list:
    """Known user-level targets. Returns files and directories that exist."""
    home = Path.home()
    found = []
    for rel in ("AGENTS.md", "CLAUDE.md", "GEMINI.md", ".cursorrules", ".clinerules"):
        candidate = home / rel
        if candidate.is_file():
            found.append(candidate)
    for rel in ("rules", ".rules", ".clinerules", ".agent/rules", ".agents/rules",
                ".cursor/rules", ".agent/skills", ".agents/skills", ".claude/skills",
                ".opencode/skills"):
        candidate = home / rel
        if candidate.is_dir():
            found.append(candidate)
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Inventory rule and skill targets (read-only).")
    parser.add_argument("--workspace", default=".", help="Workspace root to inspect (default: .)")
    parser.add_argument("--global", dest="include_global", action="store_true",
                        help="Also inspect known user-level (global) targets")
    parser.add_argument("--topic", default="", help="Topic keyword or regex to search for")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a text report")
    args = parser.parse_args(argv)

    scope_specs = []
    if args.include_global:
        for entry in global_roots():
            scope_specs.append(("global", entry if entry.is_dir() else entry.parent, entry))
    workspace_root = Path(args.workspace).expanduser().resolve()
    if not workspace_root.is_dir():
        print("error: --workspace is not a directory: %s" % workspace_root, file=sys.stderr)
        return 2
    scope_specs.append(("workspace", workspace_root, None))

    topic_re = None
    if args.topic.strip():
        try:
            topic_re = re.compile(args.topic.strip(), re.IGNORECASE)
        except re.error as exc:
            print("error: --topic is not a valid regex: %s" % exc, file=sys.stderr)
            return 2

    report = {"scopes": [], "topic": args.topic.strip()}
    covered = []

    for scope, root, single in scope_specs:
        if single is not None and not single.is_dir():
            files = [single]
            skills = []
        else:
            files = collect_rule_files(root)
            skills = collect_skill_files(root)

        scope_entry = {
            "scope": scope,
            "root": str(root),
            "rule_files": [describe(p, topic_re, args.topic) for p in files],
            "skill_files": [describe(p, topic_re, args.topic) for p in skills],
        }
        for entry in scope_entry["rule_files"] + scope_entry["skill_files"]:
            if entry.get("topic_match_count"):
                covered.append(entry)
        report["scopes"].append(scope_entry)

    report["topic_covered_by"] = [e["path"] for e in covered]

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    for scope_entry in report["scopes"]:
        print("== %s: %s" % (scope_entry["scope"], scope_entry["root"]))
        for label in ("rule_files", "skill_files"):
            entries = scope_entry[label]
            print("  %s: %d" % (label, len(entries)))
            for entry in entries:
                line = "    - %s (%d bytes)" % (entry["path"], entry["bytes"])
                if entry["kind"] == "skill":
                    line += " [skill: %s]" % (entry.get("name") or "<no frontmatter name>")
                if entry.get("topic_match_count"):
                    line += "  <-- topic matches: %d" % entry["topic_match_count"]
                print(line)
        print("")

    if args.topic.strip():
        if covered:
            print("Topic %r already appears in %d file(s):" % (args.topic, len(covered)))
            for entry in covered:
                print("  %s" % entry["path"])
                for hit in entry["topic_hits"][:5]:
                    print("    L%d: %s" % (hit["line"], hit["text"]))
            print("\nPrefer updating an existing file over creating a new one.")
        else:
            print("Topic %r is not covered by any existing target." % args.topic)
            print("A new file may be justified — confirm the classification first.")
    else:
        print("Pass --topic <keyword> to see whether an existing file already covers it.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
