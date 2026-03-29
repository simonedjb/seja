#!/usr/bin/env python3
"""
check_validation_constants_sync.py — Detect drift between backend and frontend
validation constants in dialogos.

Checks performed
================
  1. Parse backend/app/utils/validation_constants.py for all named constants.
  2. Parse frontend/src/utils/constants.ts for the VALIDATION object entries.
  3. Map known pairs and compare values.
  4. Report mismatches and constants present on one side but not the other.

Usage
-----
    python .claude/skills/scripts/check_validation_constants_sync.py

Run from the repository root (dialogos/).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from project_config import REPO_ROOT, get_path

BACKEND_CONSTANTS = (
    get_path("BACKEND_UTILS_DIR") or REPO_ROOT / "backend" / "app" / "utils"
) / "validation_constants.py"
FRONTEND_CONSTANTS = (
    get_path("FRONTEND_UTILS_DIR") or REPO_ROOT / "frontend" / "src" / "utils"
) / "constants.ts"

# Known mapping from backend constant names to frontend VALIDATION keys.
# Backend uses SCREAMING_SNAKE with _LENGTH/_MIN_LENGTH/_MAX_LENGTH suffixes;
# frontend uses shorter keys without _LENGTH.
KNOWN_PAIRS = {
    "LOGIN_MIN_LENGTH":              "LOGIN_MIN",
    "LOGIN_MAX_LENGTH":              "LOGIN_MAX",
    "PASSWORD_MIN_LENGTH":           "PASSWORD_MIN",
    "NAME_MAX_LENGTH":               "NAME_MAX",
    "GROUP_NAME_MAX_LENGTH":         "GROUP_TITLE_MAX",
    "THEME_TITLE_MAX_LENGTH":        "TITLE_MAX",
    "DISCUSSION_TITLE_MAX_LENGTH":   "DISCUSSION_TITLE_MAX",
    "DISCUSSION_DESCRIPTION_MAX_LENGTH": "DISCUSSION_DESCRIPTION_MAX",
    "CUSTOM_RELATION_MAX_LENGTH":    "CUSTOM_RELATION_MAX",
    "EMAIL_MAX_LENGTH":              "EMAIL_MAX",
}

# Regex to match  CONSTANT_NAME = <number>  in Python
_PY_CONST = re.compile(r"^([A-Z][A-Z0-9_]+)\s*=\s*(\d+)", re.MULTILINE)

# Regex to match  KEY: <number>,  inside the VALIDATION object in TS
_TS_CONST = re.compile(r"([A-Z][A-Z0-9_]+)\s*:\s*(\d+)")


def parse_backend() -> dict[str, int]:
    """Return {CONSTANT_NAME: value} from the backend constants file."""
    text = BACKEND_CONSTANTS.read_text(encoding="utf-8")
    return {m.group(1): int(m.group(2)) for m in _PY_CONST.finditer(text)}


def parse_frontend() -> dict[str, int]:
    """Return {KEY: value} from the frontend VALIDATION object."""
    text = FRONTEND_CONSTANTS.read_text(encoding="utf-8")
    # Find the VALIDATION block
    match = re.search(r"export\s+const\s+VALIDATION\s*=\s*Object\.freeze\(\{(.*?)\}\)", text, re.DOTALL)
    if not match:
        return {}
    block = match.group(1)
    return {m.group(1): int(m.group(2)) for m in _TS_CONST.finditer(block)}


def main() -> None:
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("# Validation Constants Sync Check\n")

    if not BACKEND_CONSTANTS.exists():
        print(f"ERROR: Backend constants file not found: {BACKEND_CONSTANTS}")
        sys.exit(1)
    if not FRONTEND_CONSTANTS.exists():
        print(f"ERROR: Frontend constants file not found: {FRONTEND_CONSTANTS}")
        sys.exit(1)

    be = parse_backend()
    fe = parse_frontend()

    errors = []

    # Check known pairs
    for be_name, fe_name in sorted(KNOWN_PAIRS.items()):
        be_val = be.get(be_name)
        fe_val = fe.get(fe_name)

        if be_val is None:
            errors.append(f"Backend constant {be_name} not found (expected for {fe_name})")
        elif fe_val is None:
            errors.append(f"Frontend constant VALIDATION.{fe_name} not found (expected for {be_name})")
        elif be_val != fe_val:
            errors.append(
                f"VALUE MISMATCH: {be_name}={be_val} (backend) vs "
                f"VALIDATION.{fe_name}={fe_val} (frontend)"
            )
        else:
            print(f"  OK  {be_name} = {be_val}  <->  VALIDATION.{fe_name} = {fe_val}")

    # Check for backend constants without a known frontend pair
    mapped_be = set(KNOWN_PAIRS.keys())
    for name in sorted(be.keys()):
        if name not in mapped_be:
            errors.append(
                f"Backend constant {name}={be[name]} has no known frontend mapping "
                f"(add to KNOWN_PAIRS if a frontend counterpart exists)"
            )

    # Check for frontend constants without a known backend pair
    mapped_fe = set(KNOWN_PAIRS.values())
    for name in sorted(fe.keys()):
        if name not in mapped_fe:
            errors.append(
                f"Frontend VALIDATION.{name}={fe[name]} has no known backend mapping "
                f"(add to KNOWN_PAIRS if a backend counterpart exists)"
            )

    print()
    if errors:
        print(f"## Issues ({len(errors)})\n")
        for msg in errors:
            print(f"- X {msg}")
        print(f"\nFAIL: {len(errors)} issue(s) found")
        sys.exit(1)
    else:
        print("PASS: All validation constants are in sync")


if __name__ == "__main__":
    main()
