#!/usr/bin/env python3
"""
run_preflight_fast.py -- Fast preflight checks for git hooks and CI.

Runs a curated subset of fast validation scripts (<10s total) and returns
a single pass/fail exit code. This is the single entry point for:
  - .githooks/pre-commit (local, blocking)
  - post-skill step 6b (workflow, advisory)
  - GitHub Actions fast gate (CI, blocking)

Exit codes: 0 = all checks pass, 1 = one or more checks failed, 2 = script error.

Note: For CI pipelines that need full coverage and JUnit XML output, prefer
run_all_checks.py -- the CI-independent validation orchestrator. This script
remains the lighter-weight option for git hooks and quick local validation.

Usage
-----
    python .claude/skills/scripts/run_preflight_fast.py
    python .claude/skills/scripts/run_preflight_fast.py --ci
    python .claude/skills/scripts/run_preflight_fast.py --verbose

Flags:
    --ci       Also run framework unit tests (pytest)
    --verbose  Show detailed output from each check
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parents[2]

# Checks to run, in order. Each entry: (display_name, command_args)
FAST_CHECKS: list[tuple[str, list[str]]] = [
    ("conventions", [sys.executable, str(SCRIPTS_DIR / "check_conventions.py")]),
    ("skill-system", [sys.executable, str(SCRIPTS_DIR / "check_skill_system.py")]),
    ("secrets", [sys.executable, str(SCRIPTS_DIR / "check_secrets.py"), "--all"]),
    ("skills-manifest", [sys.executable, str(SCRIPTS_DIR / "generate_skills_manifest.py"), "--check"]),
    ("skill-spec", [sys.executable, str(SCRIPTS_DIR / "check_skill_spec.py")]),
    ("version-changelog-sync", [sys.executable, str(SCRIPTS_DIR / "check_version_changelog_sync.py")]),
    ("design-output", [sys.executable, str(SCRIPTS_DIR / "check_design_output.py")]),
    ("plan-coverage", [sys.executable, str(SCRIPTS_DIR / "check_plan_coverage.py"), "--mode", "blocking"]),
]

SPEC_CHECKS_LOCATIONS = [
    REPO_ROOT / "_references" / "project" / "agent" / "spec-checks.yaml",
    REPO_ROOT / "_references" / "template" / "agent" / "spec-checks.yaml",
]

CI_CHECKS: list[tuple[str, list[str]]] = [
    ("unit-tests", [sys.executable, "-m", "pytest",
                    str(SCRIPTS_DIR / "tests"), "-v", "--tb=short"]),
]


def run_check(name: str, cmd: list[str], verbose: bool) -> bool:
    """Run a single check. Returns True if passed."""
    try:
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=not verbose,
            text=True,
            timeout=60,
        )
        if result.returncode != 0 and not verbose:
            # Print captured stderr/stdout on failure
            if result.stdout:
                print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT: {name} exceeded 60s", file=sys.stderr)
        return False
    except FileNotFoundError:
        print(f"  ERROR: command not found for {name}", file=sys.stderr)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Fast preflight checks")
    parser.add_argument("--ci", action="store_true",
                        help="Also run framework unit tests")
    parser.add_argument("--verbose", action="store_true",
                        help="Show detailed output from each check")
    args = parser.parse_args()

    checks = list(FAST_CHECKS)

    # Add spec-conformance if a spec-checks.yaml exists
    for spec_path in SPEC_CHECKS_LOCATIONS:
        if spec_path.is_file():
            checks.append((
                "spec-conformance",
                [sys.executable, str(SCRIPTS_DIR / "check_spec_conformance.py")],
            ))
            break

    if args.ci:
        checks.extend(CI_CHECKS)

    results: list[tuple[str, bool]] = []
    print("SEJA Preflight (fast)")
    print("=" * 40)

    for name, cmd in checks:
        print(f"  {name} ... ", end="", flush=True)
        passed = run_check(name, cmd, args.verbose)
        status = "PASS" if passed else "FAIL"
        print(status)
        results.append((name, passed))

    print("=" * 40)
    failed = [name for name, passed in results if not passed]
    if failed:
        print(f"FAILED: {', '.join(failed)}")
        return 1

    print(f"ALL PASSED ({len(results)} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
