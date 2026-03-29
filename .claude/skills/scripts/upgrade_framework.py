#!/usr/bin/env python3
"""
upgrade_framework.py — Upgrade a project using the SEJA-Claude framework to a
newer version by replacing framework files while preserving project-specific data.

Usage:
    python upgrade_framework.py --from <source_path> [--target <project_path>] [--dry-run]

Source can be a directory (unpacked quickstart kit) or a .zip file.
The script is idempotent — safe to run multiple times.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

from project_config import diff_conventions

# Old-layout path for references (v1)
_OLD_REFS_REL = Path(".claude", "skills", "references")

# New-layout path for agent resources (v2)
_AGENT_RESOURCES_REL = Path(".agent-resources")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def find_project_root() -> Path:
    """Walk up from CWD to find the directory containing .claude/."""
    current = Path.cwd().resolve()
    while current != current.parent:
        if (current / ".claude").is_dir():
            return current
        current = current.parent
    return Path.cwd().resolve()


def read_version(root: Path) -> str | None:
    """Parse version string from a VERSION file under .claude/skills/."""
    version_file = root / ".claude" / "skills" / "VERSION"
    if not version_file.is_file():
        return None
    text = version_file.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if line.startswith("version:"):
            return line.split(":", 1)[1].strip()
    return None


def detect_layout(target: Path) -> str:
    """Detect framework layout in target codebase or workspace.

    Returns: 'new', 'old', or 'fresh'
    """
    if (target / _AGENT_RESOURCES_REL).is_dir():
        # Check it actually has files
        ar_dir = target / _AGENT_RESOURCES_REL
        if any(ar_dir.iterdir()):
            return "new"
    old_refs = target / _OLD_REFS_REL
    if old_refs.is_dir() and any(old_refs.iterdir()):
        return "old"
    return "fresh"


def collect_source_files(source: Path) -> list[Path]:
    """Collect all framework files from source directory."""
    files: list[Path] = []
    claude_dir = source / ".claude"
    ar_dir = source / ".agent-resources"

    # Skills
    skills_dir = claude_dir / "skills"
    if skills_dir.is_dir():
        for skill_dir in sorted(skills_dir.iterdir()):
            if skill_dir.is_dir() and skill_dir.name != "scripts":
                skill_file = skill_dir / "SKILL.md"
                if skill_file.is_file():
                    files.append(skill_file)

    # Scripts
    scripts_dir = claude_dir / "skills" / "scripts"
    if scripts_dir.is_dir():
        for f in sorted(scripts_dir.iterdir()):
            if f.is_file() and f.suffix == ".py":
                files.append(f)

    # Agents
    agents_dir = claude_dir / "agents"
    if agents_dir.is_dir():
        for f in sorted(agents_dir.iterdir()):
            if f.is_file() and f.suffix == ".md":
                files.append(f)

    # Rules
    rules_dir = claude_dir / "rules"
    if rules_dir.is_dir():
        for f in sorted(rules_dir.iterdir()):
            if f.is_file() and f.suffix == ".md":
                files.append(f)

    # Agent resources — general-* and template-* (not project-*)
    if ar_dir.is_dir():
        for entry in sorted(ar_dir.iterdir()):
            if entry.is_file():
                name = entry.name
                if name.startswith("project-"):
                    continue
                if name.endswith(".md") or name.endswith(".json"):
                    files.append(entry)
            elif entry.is_dir() and entry.name.startswith("general-"):
                for sub in sorted(entry.iterdir()):
                    if sub.is_file() and sub.suffix == ".md":
                        files.append(sub)

    # Metadata
    for meta_name in ("skills/VERSION", "CHEATSHEET.md", "CHANGELOG.md"):
        meta_file = claude_dir / meta_name
        if meta_file.is_file():
            files.append(meta_file)

    return files


def is_preserved(rel_path: str) -> bool:
    """Check if a relative path should be preserved (never overwritten)."""
    parts = Path(rel_path).parts
    filename = parts[-1] if parts else ""

    # project-*.md in .agent-resources/
    if filename.startswith("project-") and filename.endswith(".md"):
        return True
    # settings files
    if filename in ("settings.json", "settings.local.json"):
        return True
    # _output directory
    if parts and parts[0] == "_output":
        return True
    # CLAUDE.md at root
    if rel_path == "CLAUDE.md":
        return True

    return False


def scan_old_path_references(target: Path) -> list[tuple[str, int, str]]:
    """Scan project-*.md and CLAUDE.md for old layout path references.

    Returns list of (file_rel_path, line_number, line_text) tuples.
    """
    old_path = ".claude/skills/references/"
    hits: list[tuple[str, int, str]] = []
    files_to_scan: list[Path] = []

    # project-*.md in .agent-resources/
    ar_dir = target / _AGENT_RESOURCES_REL
    if ar_dir.is_dir():
        for f in sorted(ar_dir.iterdir()):
            if f.is_file() and f.name.startswith("project-") and f.name.endswith(".md"):
                files_to_scan.append(f)

    # CLAUDE.md at root
    claude_md = target / "CLAUDE.md"
    if claude_md.is_file():
        files_to_scan.append(claude_md)

    for fpath in files_to_scan:
        try:
            lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        rel = fpath.relative_to(target).as_posix()
        for i, line in enumerate(lines, 1):
            if old_path in line:
                hits.append((rel, i, line.strip()))

    return hits


# ---------------------------------------------------------------------------
# Main upgrade logic
# ---------------------------------------------------------------------------


def run_upgrade(
    source_root: Path,
    target: Path,
    dry_run: bool,
) -> None:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    # --- Report accumulators ---
    report_backup: list[str] = []
    report_version: list[str] = []
    report_migration: list[str] = []
    report_updated: list[str] = []
    report_preserved: list[str] = []
    report_convention_gaps: list[str] = []
    report_manual: list[str] = []

    prefix = "[DRY-RUN] " if dry_run else ""

    # --- Layout detection ---
    layout = detect_layout(target)
    print(f"INFO: {prefix}Detected layout: {layout}")

    # --- Version reading ---
    source_version = read_version(source_root) or "unknown"
    target_version = read_version(target)
    if target_version:
        report_version.append(f"Upgrading from {target_version} to {source_version}")
    else:
        report_version.append(
            f"No VERSION found in target — treating as v1.0.0. Upgrading to {source_version}"
        )
    print(f"INFO: {report_version[0]}")

    # --- Backup ---
    claude_backup = target / f".claude-backup-{timestamp}"
    if not dry_run:
        shutil.copytree(target / ".claude", claude_backup)
        report_backup.append(f"Backed up .claude/ → {claude_backup.name}/")
        print(f"OK: {report_backup[-1]}")
    else:
        report_backup.append(f"Would back up .claude/ → .claude-backup-{timestamp}/")
        print(f"INFO: {prefix}{report_backup[-1]}")

    if layout == "new":
        ar_backup = target / f".agent-resources-backup-{timestamp}"
        if not dry_run:
            shutil.copytree(target / _AGENT_RESOURCES_REL, ar_backup)
            report_backup.append(f"Backed up .agent-resources/ → {ar_backup.name}/")
            print(f"OK: {report_backup[-1]}")
        else:
            report_backup.append(
                f"Would back up .agent-resources/ → .agent-resources-backup-{timestamp}/"
            )
            print(f"INFO: {prefix}{report_backup[-1]}")

    # --- Old layout migration ---
    if layout == "old":
        old_refs_dir = target / _OLD_REFS_REL
        ar_dir = target / _AGENT_RESOURCES_REL

        if not dry_run:
            ar_dir.mkdir(parents=True, exist_ok=True)

        # Move files from old refs to .agent-resources/
        if old_refs_dir.is_dir():
            for entry in sorted(old_refs_dir.iterdir()):
                if entry.is_file() and (entry.suffix == ".md" or entry.suffix == ".json"):
                    dest = ar_dir / entry.name
                    if not dry_run:
                        shutil.move(str(entry), str(dest))
                    report_migration.append(
                        f"Moved {_OLD_REFS_REL.as_posix()}/{entry.name} → "
                        f"{_AGENT_RESOURCES_REL.as_posix()}/{entry.name}"
                    )
                    print(f"OK: {prefix}{report_migration[-1]}")
                elif entry.is_dir():
                    # Subdirectories (e.g., general-review-perspectives/)
                    dest_dir = ar_dir / entry.name
                    if not dry_run:
                        if dest_dir.exists():
                            shutil.rmtree(dest_dir)
                        shutil.move(str(entry), str(dest_dir))
                    report_migration.append(
                        f"Moved {_OLD_REFS_REL.as_posix()}/{entry.name}/ → "
                        f"{_AGENT_RESOURCES_REL.as_posix()}/{entry.name}/"
                    )
                    print(f"OK: {prefix}{report_migration[-1]}")

            # Remove old refs directory if empty
            if not dry_run:
                try:
                    old_refs_dir.rmdir()
                    report_migration.append(
                        f"Removed empty {_OLD_REFS_REL.as_posix()}/"
                    )
                    print(f"OK: {report_migration[-1]}")
                except OSError:
                    report_migration.append(
                        f"WARN: {_OLD_REFS_REL.as_posix()}/ not empty after migration"
                    )
                    print(f"WARN: {report_migration[-1]}")
            else:
                report_migration.append(
                    f"Would remove {_OLD_REFS_REL.as_posix()}/ (if empty)"
                )
                print(f"INFO: {prefix}{report_migration[-1]}")

    elif layout == "fresh":
        # Ensure .agent-resources/ exists for fresh projects
        ar_dir = target / _AGENT_RESOURCES_REL
        if not dry_run:
            ar_dir.mkdir(parents=True, exist_ok=True)
        report_migration.append("Fresh project — created .agent-resources/")
        print(f"INFO: {prefix}{report_migration[-1]}")

    # --- Overwrite framework files from source ---
    source_files = collect_source_files(source_root)
    if not source_files:
        print("ERROR: No framework files found in source.")
        sys.exit(1)

    for src_file in source_files:
        rel = src_file.relative_to(source_root).as_posix()

        if is_preserved(rel):
            report_preserved.append(rel)
            print(f"SKIP: {prefix}{rel} (preserved)")
            continue

        dest = target / rel
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src_file), str(dest))

        report_updated.append(rel)
        print(f"OK: {prefix}Updated {rel}")

    # --- Preserved files summary ---
    # Check for settings files and CLAUDE.md
    for check_rel in (".claude/settings.json", ".claude/settings.local.json", "CLAUDE.md"):
        check_path = target / check_rel
        if check_path.is_file() and check_rel not in report_preserved:
            report_preserved.append(check_rel)

    # _output directory
    if (target / "_output").is_dir():
        if "_output/" not in report_preserved:
            report_preserved.append("_output/ (entire directory)")

    # project-*.md files in .agent-resources/
    ar_dir = target / _AGENT_RESOURCES_REL
    if ar_dir.is_dir():
        for f in sorted(ar_dir.iterdir()):
            if f.is_file() and f.name.startswith("project-") and f.name.endswith(".md"):
                rel = f.relative_to(target).as_posix()
                if rel not in report_preserved:
                    report_preserved.append(rel)

    # --- Convention schema diff ---
    project_conv = target / _AGENT_RESOURCES_REL / "project-conventions.md"
    template_conv = target / _AGENT_RESOURCES_REL / "template-conventions.md"

    if project_conv.is_file() and template_conv.is_file():
        diff = diff_conventions(project_conv, template_conv)

        if diff["missing_in_project"]:
            report_convention_gaps.append(
                f"Variables in template missing from project-conventions.md: "
                f"{', '.join(diff['missing_in_project'])}"
            )
        if diff["extra_in_project"]:
            report_convention_gaps.append(
                f"Variables in project-conventions.md not in template: "
                f"{', '.join(diff['extra_in_project'])}"
            )
        if not diff["missing_in_project"] and not diff["extra_in_project"]:
            report_convention_gaps.append("Convention variables are in sync.")
    elif project_conv.is_file():
        report_convention_gaps.append(
            "WARN: template-conventions.md not found — cannot compare."
        )
    else:
        report_convention_gaps.append(
            "INFO: No project-conventions.md found — diff skipped."
        )

    # --- Path reference scan (old layout migration only) ---
    if layout == "old":
        old_refs = scan_old_path_references(target)
        if old_refs:
            report_manual.append(
                "Old path references found (need manual update to .agent-resources/):"
            )
            for fpath, lineno, line_text in old_refs:
                report_manual.append(f"  {fpath}:{lineno}: {line_text}")
        else:
            report_manual.append("No old path references found — migration clean.")

    # CLAUDE.md always flagged for review
    if (target / "CLAUDE.md").is_file():
        report_manual.append(
            "Review CLAUDE.md — root project instructions may need updates to "
            "reflect new framework version."
        )

    # --- Summary report ---
    print()
    print("=" * 60)
    print(f"  UPGRADE SUMMARY {'(DRY RUN)' if dry_run else ''}")
    print("=" * 60)

    def _section(title: str, items: list[str]) -> None:
        print(f"\n--- {title} ---")
        if items:
            for item in items:
                print(f"  {item}")
        else:
            print("  (none)")

    _section("Backup", report_backup)
    _section("Version", report_version)
    _section("Migration", report_migration)
    _section("Files Updated", report_updated)
    _section("Files Preserved", report_preserved)
    _section("Convention Gaps", report_convention_gaps)
    _section("Manual Steps Needed", report_manual)

    print()
    if dry_run:
        print("INFO: Dry run complete — no files were modified.")
    else:
        print(f"OK: Upgrade complete. Backup stored in {claude_backup.name}/")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upgrade a SEJA-Claude framework project to a newer version.",
        epilog=(
            "Example:\n"
            "  python upgrade_framework.py --from ../seja-public/\n"
            "  python upgrade_framework.py --from ./kit/ --target ./my-project --dry-run"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--from",
        dest="source",
        required=True,
        help="Source of new framework files: a directory or .zip file",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Project directory to upgrade (default: auto-detect repo root)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes",
    )

    args = parser.parse_args()

    # Resolve source
    source_path = Path(args.source).resolve()
    temp_dir = None

    if source_path.is_file() and source_path.suffix == ".zip":
        # Extract zip to temporary directory
        temp_dir = tempfile.mkdtemp(prefix="seja-upgrade-")
        print(f"INFO: Extracting {source_path.name} to temporary directory...")
        with zipfile.ZipFile(source_path, "r") as zf:
            zf.extractall(temp_dir)
        source_root = Path(temp_dir)
        # Check if zip contents are nested in a subdirectory
        entries = list(source_root.iterdir())
        if len(entries) == 1 and entries[0].is_dir():
            source_root = entries[0]
        # If zip has .claude/ at root level, use that root
        if not (source_root / ".claude").is_dir():
            # Try one level deeper
            for child in source_root.iterdir():
                if child.is_dir() and (child / ".claude").is_dir():
                    source_root = child
                    break
    elif source_path.is_dir():
        source_root = source_path
        # Navigate to root with .claude/ if needed
        if not (source_root / ".claude").is_dir():
            for child in source_root.iterdir():
                if child.is_dir() and (child / ".claude").is_dir():
                    source_root = child
                    break
    else:
        print(f"ERROR: Source path does not exist or is not a directory/zip: {source_path}")
        sys.exit(1)

    if not (source_root / ".claude").is_dir():
        print(f"ERROR: Source does not contain a .claude/ directory: {source_root}")
        sys.exit(1)

    # Resolve target
    if args.target:
        target = Path(args.target).resolve()
    else:
        target = find_project_root()

    if not (target / ".claude").is_dir():
        print(f"ERROR: Target does not contain a .claude/ directory: {target}")
        sys.exit(1)

    print(f"INFO: Source: {source_root}")
    print(f"INFO: Target: {target}")
    print()

    try:
        run_upgrade(source_root, target, args.dry_run)
    finally:
        # Clean up temp directory if we created one
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
