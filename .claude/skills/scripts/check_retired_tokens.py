#!/usr/bin/env python3
# designer: When a name is retired from the harness -- a config variable or a
#   skill reference that no longer exists -- I make sure no live file still
#   mentions it. You find out about a stale reference to a dead token before it
#   ships, pointed straight at the file and line that still carries it.
"""
check_retired_tokens.py — Guard against retired tokens lingering in live harness files.

Invocation: agent-invoked, hook-ci
Lifecycle: active

Greps live harness files (scope: `.claude/`) for a small, curated denylist of
tokens that have been fully retired from the harness. Any occurrence in a live
file is a regression: the token was renamed/removed but a reference was left
behind. The check exits non-zero and lists every `file:line` hit.

Denylist curation intent
------------------------
The denylist holds ONLY fully-retired, config-variable-style tokens (e.g. an
old conventions.md variable name, or a dead `skill:<name>` reference). When you
retire such a name, add it here so the guard prevents it from creeping back.

Deliberately OUT OF SCOPE: path-prefix tokens that carry backward-compat or
migration semantics — such as the old `_references/` layout prefix — are NOT
retirable via this guard. They legitimately persist in the upgrade/migration
toolchain, in backward-compat matchers, and in legacy-layout detection tests
and fixtures (60+ live occurrences under `.claude/`). This guard is a naive
substring matcher with no such semantic awareness, so it targets only
fully-retired tokens where any occurrence is unambiguously wrong.

Scope & exclusions
------------------
Scans every file under `.claude/`. Excludes this guard's OWN file so its
denylist literals do not self-trip.

Exit codes: 0 = no retired token found in live files, 1 = one or more hits.

Usage
-----
    python .claude/skills/scripts/check_retired_tokens.py
    python .claude/skills/scripts/check_retired_tokens.py --verbose

CHECK_PLUGIN_MANIFEST:
  name: RetiredTokens
  stack:
    backend: [any]
    frontend: [any]
  scope: conventions
  critical: false
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Import from sibling module
sys.path.insert(0, str(Path(__file__).resolve().parent))
from project_config import REPO_ROOT

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CLAUDE_DIR = REPO_ROOT / ".claude"

# This file — excluded from scanning so its denylist literals do not self-trip.
SELF_PATH = Path(__file__).resolve()

# Curated denylist of fully-retired tokens. Add a token here when you retire a
# name (see "Denylist curation intent" in the module docstring).
RETIRED_TOKENS: list[str] = [
    "CHECK_LOGS_DIR",  # retired conventions variable; replaced by CRITIQUE_LOGS_DIR
    "skill:check",     # retired call-graph reference; the skill is now `critique`
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def collect_scan_files() -> list[Path]:
    """Collect live files under `.claude/`, excluding this guard's own file.

    `__pycache__` is skipped: compiled `.pyc` bytecode is a build artifact, not
    a live source file, and can retain stale string constants from pre-cleanup
    source until regenerated.
    """
    files: list[Path] = []
    if not CLAUDE_DIR.is_dir():
        return files
    for path in sorted(CLAUDE_DIR.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts:
            continue
        if path.resolve() == SELF_PATH:
            continue
        files.append(path)
    return files


def scan_file(file_path: Path) -> list[tuple[int, str]]:
    """Scan a file for retired tokens. Returns [(line_number, token), ...]."""
    hits: list[tuple[int, str]] = []
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return hits
    for i, line in enumerate(text.splitlines(), start=1):
        for token in RETIRED_TOKENS:
            if token in line:
                hits.append((i, token))
    return hits


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guard against retired tokens lingering in live `.claude/` files"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="List every scanned file, not just the hits",
    )
    args = parser.parse_args()

    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("# Retired Token Guard\n")
    print(f"Denylist: {', '.join(RETIRED_TOKENS)}\n")

    scan_files = collect_scan_files()
    if args.verbose:
        print(f"Files scanned: {len(scan_files)}\n")

    findings: list[str] = []
    for file_path in scan_files:
        for line_no, token in scan_file(file_path):
            rel = file_path.relative_to(REPO_ROOT)
            findings.append(f"  {rel}:{line_no}: retired token `{token}`")

    if findings:
        print("## Retired tokens found\n")
        for msg in findings:
            print(msg)
        print()
        print(f"FAIL: {len(findings)} retired-token reference(s) in live files")
        return 1

    print(f"PASS: no retired tokens in {len(scan_files)} scanned file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
