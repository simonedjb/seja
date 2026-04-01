"""
0001_split_quickstart_to_seed_design_upgrade.py

Migrate references from the retired /quickstart skill to the three skills
that replaced it: /seed, /design, and /upgrade.

Scans markdown files under _references/project/, .claude/, and CLAUDE.md for
occurrences of /quickstart and replaces them with the appropriate successor.
"""
from __future__ import annotations

import re
from pathlib import Path

from_version = "1.0.0"
to_version = "2.0.0"

# Patterns and their replacements.  Order matters: more specific patterns
# first so they are not clobbered by the generic fallback.
_REPLACEMENTS: list[tuple[re.Pattern[str], str]] = [
    # /quickstart --upgrade  ->  /upgrade
    (re.compile(r"/quickstart\s+--upgrade\b"), "/upgrade"),
    # /quickstart --workspace  ->  /seed --workspace
    (re.compile(r"/quickstart\s+--workspace\b"), "/seed --workspace"),
    # /quickstart .  or  /quickstart <path>  ->  /seed
    (re.compile(r"/quickstart\s+\.(?=\s|$)"), "/seed ."),
    # Bare /quickstart (word boundary) -> /seed
    (re.compile(r"/quickstart\b"), "/seed"),
]


def _collect_markdown_files(root: Path) -> list[Path]:
    """Return markdown files that might reference /quickstart."""
    files: list[Path] = []

    # _references/project/
    project_dir = root / "_references" / "project"
    if project_dir.is_dir():
        files.extend(sorted(project_dir.rglob("*.md")))

    # .claude/ (skills, rules, agents, etc.)
    claude_dir = root / ".claude"
    if claude_dir.is_dir():
        files.extend(sorted(claude_dir.rglob("*.md")))

    # Root CLAUDE.md
    claude_md = root / "CLAUDE.md"
    if claude_md.is_file():
        files.append(claude_md)

    return files


def _apply_replacements(text: str) -> str:
    """Apply all replacement patterns to *text*."""
    for pattern, replacement in _REPLACEMENTS:
        text = pattern.sub(replacement, text)
    return text


def upgrade(root: Path) -> None:
    """Replace /quickstart references with /seed, /design, /upgrade."""
    files = _collect_markdown_files(root)
    changed_count = 0

    for fpath in files:
        try:
            original = fpath.read_text(encoding="utf-8")
        except OSError:
            continue

        if "/quickstart" not in original:
            continue

        updated = _apply_replacements(original)

        if updated != original:
            fpath.write_text(updated, encoding="utf-8")
            rel = fpath.relative_to(root).as_posix()
            print(f"OK: Updated /quickstart references in {rel}")
            changed_count += 1

    if changed_count == 0:
        print("INFO: No /quickstart references found -- already migrated")
    else:
        print(f"OK: Updated {changed_count} file(s)")


def downgrade(root: Path) -> None:
    """Best-effort reverse: replace /seed back to /quickstart.

    Note: this cannot perfectly reverse all replacements since /upgrade
    may have been written by a human.  It handles the common cases.
    """
    _REVERSE: list[tuple[re.Pattern[str], str]] = [
        (re.compile(r"/upgrade\b"), "/quickstart --upgrade"),
        (re.compile(r"/seed\s+--workspace\b"), "/quickstart --workspace"),
        (re.compile(r"/seed\s+\.(?=\s|$)"), "/quickstart ."),
        (re.compile(r"/seed\b"), "/quickstart"),
    ]

    files = _collect_markdown_files(root)
    for fpath in files:
        try:
            original = fpath.read_text(encoding="utf-8")
        except OSError:
            continue

        text = original
        for pattern, replacement in _REVERSE:
            text = pattern.sub(replacement, text)

        if text != original:
            fpath.write_text(text, encoding="utf-8")
            rel = fpath.relative_to(root).as_posix()
            print(f"OK: Reverted references in {rel}")
