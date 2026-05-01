"""
0002_rename_seed_to_setup.py

Migrate references from the retired /seed skill to its successor /setup.

Scans markdown files under _references/project/, .claude/, and CLAUDE.md for
occurrences of /seed and replaces them with /setup.

Version axis: run_migrations.py reads the consumer-side .seja-version file
(public release tag like "v0.1.0"), NOT the internal .claude/skills/VERSION.
_parse_version("v0.1.0") parses to (0, 0, 1, 0) (the leading "v" becomes 0 via
the int() fallback). The gate fires when
from_version <= consumer_seja_version < to_version.
"""
from __future__ import annotations

import re
from pathlib import Path

from_version = "v0.1.0"
to_version = "v0.2.0"

# Patterns and their replacements.  Order matters: more specific patterns
# first so they are not clobbered by the generic fallback.
_REPLACEMENTS: list[tuple[re.Pattern[str], str]] = [
    # /seed --here  ->  /setup --here
    (re.compile(r"/seed\s+--here\b"), "/setup --here"),
    # /seed --workspace  ->  /setup --workspace
    (re.compile(r"/seed\s+--workspace\b"), "/setup --workspace"),
    # /seed --demo  ->  /setup --demo
    (re.compile(r"/seed\s+--demo\b"), "/setup --demo"),
    # /seed --version  ->  /setup --version
    (re.compile(r"/seed\s+--version\b"), "/setup --version"),
    # Bare /seed (word boundary) -> /setup.
    # IMPORTANT: the \b after "d" ensures URLs like /simonedjb/seja are not
    # matched -- \b fires only at end-of-identifier boundaries, and the "j" in
    # "/simonedjb" is immediately adjacent to "d", so no boundary there.
    (re.compile(r"/seed\b"), "/setup"),
]


def _collect_markdown_files(root: Path) -> list[Path]:
    """Return markdown files that might reference /seed."""
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
    """Replace /seed references with /setup across consumer markdown files."""
    files = _collect_markdown_files(root)
    changed_count = 0

    for fpath in files:
        try:
            original = fpath.read_text(encoding="utf-8")
        except OSError:
            continue

        if "/seed" not in original:
            continue

        updated = _apply_replacements(original)

        if updated != original:
            fpath.write_text(updated, encoding="utf-8")
            rel = fpath.relative_to(root).as_posix()
            print(f"OK: Updated /seed references in {rel}")
            changed_count += 1

    if changed_count == 0:
        print("INFO: No /seed references found -- already migrated")
    else:
        print(f"OK: Updated {changed_count} file(s)")


def downgrade(root: Path) -> None:
    """Best-effort reverse: replace /setup back to /seed.

    Provided for completeness; not a first-class flow.  Cannot perfectly
    reverse all replacements since /setup may have been authored by a human
    after the migration.
    """
    _REVERSE: list[tuple[re.Pattern[str], str]] = [
        (re.compile(r"/setup\s+--here\b"), "/seed --here"),
        (re.compile(r"/setup\s+--workspace\b"), "/seed --workspace"),
        (re.compile(r"/setup\s+--demo\b"), "/seed --demo"),
        (re.compile(r"/setup\s+--version\b"), "/seed --version"),
        (re.compile(r"/setup\b"), "/seed"),
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
