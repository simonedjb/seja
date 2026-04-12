#!/usr/bin/env python3
"""
check_no_private_leaks.py -- Verify seja-public/ contains no private content.

Scans the seja-public/ directory for:
  (a) Remaining priv-only-start/end markers (strip failure)
  (b) Files that should not exist in the public copy
  (c) Known private-only patterns in .md files

Exit 0 if clean, exit 1 with details if leaks found.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from project_config import REPO_ROOT

PUBLIC_DIR = REPO_ROOT / "seja-public"

# Files that must never appear in seja-public
PRIVATE_FILES = {
    "generate_changelog_data.py",
}

# Directories that must never appear in seja-public
PRIVATE_DIRS = {
    "priv",
    "project",
}

# Patterns that indicate private content leaked into .md files
# Each tuple: (pattern_regex, description, file_glob)
PRIVATE_PATTERNS: list[tuple[str, str, str]] = [
    (r"<!-- priv-only-start -->", "priv-only marker not stripped", "**/*.md"),
    (r"<!-- priv-only-end -->", "priv-only marker not stripped", "**/*.md"),
]

# Content-fingerprint patterns for SKILL.md files only.
# These catch unmarked private content that leaked through without priv-only markers.
# Only scan SKILL.md -- .py scripts legitimately reference these terms.
SKILL_CONTENT_PATTERNS: list[tuple[str, str]] = [
    (r"--framework", "framework-exclusive flag in public skill docs"),
    (r"seja-public/", "reference to sync target in public skill docs"),
    (r"sync_to_public", "reference to sync mechanism in public skill docs"),
    (r"generate_changelog_data", "reference to private script in public skill docs"),
]


def check_markers(public_dir: Path) -> list[str]:
    """Check for remaining priv-only markers in .md files.

    Ignores markers inside fenced code blocks (``` or ~~~).
    """
    issues: list[str] = []
    marker_re = re.compile(r"<!-- priv-only-(start|end) -->")
    for md_file in sorted(public_dir.rglob("*.md")):
        try:
            content = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in _lines_outside_fences(content):
            if marker_re.search(line):
                rel = md_file.relative_to(public_dir)
                issues.append(f"  {rel}:{i} -- priv-only marker not stripped")
    return issues


def check_private_files(public_dir: Path) -> list[str]:
    """Check for files that should not exist in the public copy."""
    issues: list[str] = []
    for f in sorted(public_dir.rglob("*")):
        if not f.is_file():
            continue
        if f.name in PRIVATE_FILES:
            rel = f.relative_to(public_dir)
            issues.append(f"  {rel} -- private-only file should not exist in public")
    return issues


def check_private_dirs(public_dir: Path) -> list[str]:
    """Check for directories that should not exist in the public copy."""
    issues: list[str] = []
    for d in sorted(public_dir.rglob("*")):
        if not d.is_dir():
            continue
        if d.name in PRIVATE_DIRS:
            rel = d.relative_to(public_dir)
            issues.append(f"  {rel}/ -- private-only directory should not exist in public")
    return issues


def _lines_outside_fences(content: str):
    """Yield (line_number, line) for lines NOT inside fenced code blocks."""
    fence_re = re.compile(r"^(`{3,}|~{3,})")
    in_fence = False
    for i, line in enumerate(content.splitlines(), 1):
        if fence_re.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield i, line


def check_private_patterns(public_dir: Path) -> list[str]:
    """Check for known private-only patterns in .md files.

    Ignores matches inside fenced code blocks.
    """
    issues: list[str] = []
    for pattern_str, description, file_glob in PRIVATE_PATTERNS:
        pattern = re.compile(pattern_str)
        for md_file in sorted(public_dir.rglob(file_glob)):
            if not md_file.is_file():
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for i, line in _lines_outside_fences(content):
                if pattern.search(line):
                    rel = md_file.relative_to(public_dir)
                    issues.append(f"  {rel}:{i} -- {description}")
    return issues


def check_skill_content_fingerprints(public_dir: Path) -> list[str]:
    """Check SKILL.md files for inherently private keywords.

    Catches unmarked private content that leaked through without priv-only markers.
    Only scans SKILL.md files -- .py scripts legitimately reference these terms.
    Ignores matches inside fenced code blocks.
    """
    issues: list[str] = []
    for pattern_str, description in SKILL_CONTENT_PATTERNS:
        pattern = re.compile(pattern_str)
        for skill_file in sorted(public_dir.rglob("SKILL.md")):
            try:
                content = skill_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for i, line in _lines_outside_fences(content):
                if pattern.search(line):
                    rel = skill_file.relative_to(public_dir)
                    issues.append(f"  {rel}:{i} -- {description}")
    return issues


def main() -> int:
    if not PUBLIC_DIR.is_dir():
        print(f"SKIP: {PUBLIC_DIR} does not exist")
        return 0

    all_issues: list[str] = []
    all_issues.extend(check_markers(PUBLIC_DIR))
    all_issues.extend(check_private_files(PUBLIC_DIR))
    all_issues.extend(check_private_dirs(PUBLIC_DIR))
    # Private patterns overlap with markers; only run if markers check passed
    if not all_issues:
        all_issues.extend(check_private_patterns(PUBLIC_DIR))
    # Content fingerprints catch unmarked private content in SKILL.md files
    all_issues.extend(check_skill_content_fingerprints(PUBLIC_DIR))

    if all_issues:
        print("Private content leak check: ISSUES FOUND\n")
        for issue in all_issues:
            print(issue)
        print(f"\n{len(all_issues)} issue(s) found.")
        return 1

    print("Private content leak check: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
