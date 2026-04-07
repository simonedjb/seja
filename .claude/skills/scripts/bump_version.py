#!/usr/bin/env python3
"""
bump_version.py -- Update all SEJA version files atomically.

Updates `.claude/skills/VERSION`, `.seja-version`, and validates that
`.claude/CHANGELOG.md` has a matching `## [x.y.z]` heading.

Usage
-----
    python .claude/skills/scripts/bump_version.py --version 2.7.0
    python .claude/skills/scripts/bump_version.py --version 2.7.0 --dry-run

Run from the repository root.
"""
from __future__ import annotations

import argparse
import re
import subprocess
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


def _read_file(path: Path) -> str:
    """Read a file as UTF-8, returning empty string if missing."""
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def bump_version_file(root: Path, version: str, dry_run: bool) -> bool:
    """Update .claude/skills/VERSION. Returns True if changed."""
    path = root / ".claude" / "skills" / "VERSION"
    content = _read_file(path)
    new_content = re.sub(
        r"^(version:\s*).*$",
        rf"\g<1>{version}",
        content,
        count=1,
        flags=re.MULTILINE,
    )
    if content == new_content:
        print(f"  .claude/skills/VERSION: already at {version}")
        return False
    if dry_run:
        print(f"  .claude/skills/VERSION: would update to {version}")
    else:
        path.write_text(new_content, encoding="utf-8")
        print(f"  .claude/skills/VERSION: updated to {version}")
    return True


def bump_seja_version(root: Path, version: str, dry_run: bool) -> bool:
    """Update .seja-version. Returns True if changed."""
    path = root / ".seja-version"
    current = _read_file(path).strip()
    if current == version:
        print(f"  .seja-version: already at {version}")
        return False
    if dry_run:
        print(f"  .seja-version: would update from {current or '(missing)'} to {version}")
    else:
        path.write_text(version, encoding="utf-8")
        print(f"  .seja-version: updated to {version}")
    return True


def check_changelog(root: Path, version: str) -> bool:
    """Check that CHANGELOG.md has a ## [version] heading. Returns True if found."""
    changelog = root / ".claude" / "CHANGELOG.md"
    if not changelog.is_file():
        print(f"  WARNING: .claude/CHANGELOG.md not found")
        return False
    content = changelog.read_text(encoding="utf-8", errors="replace")
    pattern = rf"^## \[{re.escape(version)}\]"
    if re.search(pattern, content, re.MULTILINE):
        print(f"  .claude/CHANGELOG.md: has [{ version}] heading")
        return True
    print(f"  WARNING: .claude/CHANGELOG.md missing [{ version}] heading -- add it manually")
    return False


def run_sync_check(root: Path) -> int:
    """Run check_version_changelog_sync.py as a final gate."""
    script = root / ".claude" / "skills" / "scripts" / "check_version_changelog_sync.py"
    if not script.is_file():
        print("  WARNING: check_version_changelog_sync.py not found, skipping gate")
        return 0
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        cwd=str(root),
    )
    print(f"  Sync check: {result.stdout.strip()}")
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Bump SEJA framework version")
    parser.add_argument("--version", required=True, help="Target version (e.g., 2.7.0)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change")
    args = parser.parse_args()

    version = args.version
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        print(f"ERROR: Invalid version format '{version}'. Expected X.Y.Z")
        return 2

    root = _find_repo_root()
    mode = "DRY RUN" if args.dry_run else "UPDATING"
    print(f"\n{mode}: bumping to {version}\n")

    changed = False
    changed |= bump_version_file(root, version, args.dry_run)
    changed |= bump_seja_version(root, version, args.dry_run)
    changelog_ok = check_changelog(root, version)

    if not args.dry_run:
        print()
        rc = run_sync_check(root)
        if rc != 0:
            return rc

    if not changed and changelog_ok:
        print(f"\nAll files already at {version}. Nothing to do.")
    elif args.dry_run:
        print(f"\nDry run complete. Re-run without --dry-run to apply.")
    else:
        print(f"\nVersion bump to {version} complete.")
        if not changelog_ok:
            print("Remember to add a CHANGELOG entry before committing.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
