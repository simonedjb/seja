#!/usr/bin/env python3
"""
check_version_changelog_sync.py — Verify VERSION file matches latest CHANGELOG heading.

Exit codes: 0 = in sync, 1 = version mismatch, 2 = script error.

Reads the version from `.claude/skills/VERSION` and compares it against the
first `## [x.y.z]` heading in `.claude/CHANGELOG.md`. Fails if they differ,
preventing version drift between the two files.

Usage
-----
    python .claude/skills/scripts/check_version_changelog_sync.py

Run from the repository root.

CHECK_PLUGIN_MANIFEST:
  name: Version-Changelog Sync
  stack:
    backend: [any]
    frontend: [any]
  scope: metadata
  critical: false
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def _find_repo_root() -> Path:
    """Walk up from script location to find the repo root."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".claude").is_dir():
            return current
        current = current.parent
    return Path.cwd().resolve()


def read_version_file(root: Path) -> str | None:
    """Read version from .claude/skills/VERSION."""
    version_file = root / ".claude" / "skills" / "VERSION"
    if not version_file.is_file():
        return None
    text = version_file.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if line.startswith("version:"):
            return line.split(":", 1)[1].strip()
    return None


def read_changelog_version(root: Path) -> str | None:
    """Extract the first [x.y.z] version from CHANGELOG.md headings."""
    changelog = root / ".claude" / "CHANGELOG.md"
    if not changelog.is_file():
        return None
    text = changelog.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"^## \[(\d+\.\d+\.\d+)\]", text, re.MULTILINE)
    return match.group(1) if match else None


def main() -> int:
    root = _find_repo_root()

    version = read_version_file(root)
    if version is None:
        print("ERROR: .claude/skills/VERSION not found or missing version field")
        return 2

    changelog_version = read_changelog_version(root)
    if changelog_version is None:
        print("ERROR: .claude/CHANGELOG.md not found or no [x.y.z] heading found")
        return 2

    if version == changelog_version:
        print(f"OK: VERSION ({version}) matches CHANGELOG ({changelog_version})")
        return 0

    print(
        f"FAIL: VERSION file says {version} but CHANGELOG latest is {changelog_version}. "
        f"Update .claude/skills/VERSION to match."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
