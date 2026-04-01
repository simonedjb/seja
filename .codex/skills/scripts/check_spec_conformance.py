#!/usr/bin/env python3
"""
check_spec_conformance.py -- Validate codebase against structured spec checks.

Reads spec-checks.yaml from the agent-facing specs directory and runs each
check against the codebase. Check types:
  file_exists  -- verify a file or glob pattern exists
  grep_match   -- verify a regex pattern IS found in target files
  grep_absent  -- verify a regex pattern is NOT found in target files
  model_field  -- verify a model file contains a specific field definition
  route_exists -- verify an API route pattern is registered

Exit codes: 0 = all checks pass, 1 = one or more errors found.

Usage
-----
    python .claude/skills/scripts/check_spec_conformance.py
    python .claude/skills/scripts/check_spec_conformance.py --root /path/to/project
    python .claude/skills/scripts/check_spec_conformance.py --verbose
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Import from sibling module
sys.path.insert(0, str(Path(__file__).resolve().parent))
from project_config import REPO_ROOT

# ---------------------------------------------------------------------------
# Check implementations
# ---------------------------------------------------------------------------


def check_file_exists(root: Path, target: str, _pattern: str | None) -> tuple[bool, str]:
    """Check that at least one file matches the target glob."""
    matches = list(root.glob(target))
    if matches:
        return True, f"Found {len(matches)} file(s) matching '{target}'"
    return False, f"No files matching '{target}'"


def check_grep_match(root: Path, target: str, pattern: str | None) -> tuple[bool, str]:
    """Check that the pattern is found in at least one target file."""
    if not pattern:
        return False, "No pattern specified for grep_match check"
    regex = re.compile(pattern)
    target_files = list(root.glob(target))
    if not target_files:
        return False, f"No files matching '{target}' to search"
    for f in target_files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            if regex.search(content):
                return True, f"Pattern found in {f.relative_to(root)}"
        except (OSError, UnicodeDecodeError):
            continue
    return False, f"Pattern '{pattern}' not found in any of {len(target_files)} file(s)"


def check_grep_absent(root: Path, target: str, pattern: str | None) -> tuple[bool, str]:
    """Check that the pattern is NOT found in any target file."""
    if not pattern:
        return False, "No pattern specified for grep_absent check"
    regex = re.compile(pattern)
    target_files = list(root.glob(target))
    if not target_files:
        return True, f"No files matching '{target}' (vacuously true)"
    violations = []
    for f in target_files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            match = regex.search(content)
            if match:
                violations.append(f"{f.relative_to(root)}:{match.start()}")
        except (OSError, UnicodeDecodeError):
            continue
    if violations:
        return False, f"Pattern found in {len(violations)} file(s): {', '.join(violations[:5])}"
    return True, f"Pattern absent from all {len(target_files)} file(s)"


def check_model_field(root: Path, target: str, pattern: str | None) -> tuple[bool, str]:
    """Check that a model file contains the expected field definition."""
    if not pattern:
        return False, "No field name specified for model_field check"
    target_path = root / target
    if not target_path.exists():
        return False, f"Model file '{target}' not found"
    content = target_path.read_text(encoding="utf-8", errors="replace")
    # Look for the field name as a column definition or attribute
    field_re = re.compile(rf"\b{re.escape(pattern)}\b\s*=")
    if field_re.search(content):
        return True, f"Field '{pattern}' found in {target}"
    return False, f"Field '{pattern}' not found in {target}"


def check_route_exists(root: Path, target: str, pattern: str | None) -> tuple[bool, str]:
    """Check that an API route pattern is registered in target files."""
    if not pattern:
        return False, "No route pattern specified for route_exists check"
    target_files = list(root.glob(f"{target}**/*.py")) if (root / target).is_dir() else list(root.glob(target))
    if not target_files:
        return False, f"No files found in '{target}'"
    route_re = re.compile(re.escape(pattern))
    for f in target_files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            if route_re.search(content):
                return True, f"Route '{pattern}' found in {f.relative_to(root)}"
        except (OSError, UnicodeDecodeError):
            continue
    return False, f"Route '{pattern}' not found in any of {len(target_files)} file(s)"


CHECK_HANDLERS = {
    "file_exists": check_file_exists,
    "grep_match": check_grep_match,
    "grep_absent": check_grep_absent,
    "model_field": check_model_field,
    "route_exists": check_route_exists,
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate codebase against spec checks")
    parser.add_argument("--root", type=Path, default=None, help="Project root directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show passing checks too")
    args = parser.parse_args()

    root = Path(args.root) if args.root else REPO_ROOT
    refs_dir = root / "_references"

    # Locate spec-checks.yaml
    spec_checks_path = refs_dir / "project" / "agent" / "spec-checks.yaml"
    if not spec_checks_path.exists():
        print("No spec checks configured (project/agent/spec-checks.yaml not found). Skipping.")
        return 0

    # Load YAML (use simple parser to avoid external dependency)
    try:
        import yaml
    except ImportError:
        # Fallback: try to parse manually or warn
        print("WARNING: PyYAML not installed. Cannot parse spec-checks.yaml.")
        print("Install with: pip install pyyaml")
        return 0

    with open(spec_checks_path, encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    if not spec or "checks" not in spec:
        print("No checks defined in spec-checks.yaml.")
        return 0

    checks = spec["checks"]
    errors = 0
    warnings = 0
    passed = 0

    print(f"Running {len(checks)} spec conformance check(s)...\n")

    for check in checks:
        check_id = check.get("id", "unknown")
        description = check.get("description", "")
        check_type = check.get("type", "")
        target = check.get("target", "")
        pattern = check.get("pattern")
        severity = check.get("severity", "error")
        message = check.get("message", "")

        handler = CHECK_HANDLERS.get(check_type)
        if not handler:
            print(f"  [{check_id}] SKIP -- unknown check type: {check_type}")
            continue

        ok, detail = handler(root, target, pattern)

        if ok:
            passed += 1
            if args.verbose:
                print(f"  [{check_id}] PASS -- {description}: {detail}")
        else:
            label = "ERROR" if severity == "error" else "WARN"
            if severity == "error":
                errors += 1
            else:
                warnings += 1
            print(f"  [{check_id}] {label} -- {message or description}: {detail}")

    print(f"\nResults: {passed} passed, {errors} error(s), {warnings} warning(s)")
    return 1 if errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
