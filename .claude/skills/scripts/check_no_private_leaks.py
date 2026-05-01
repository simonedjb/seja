#!/usr/bin/env python3
# designer: Before you publish or share a copy of this repository, I
#   look for content marked as private -- files, directories, and
#   fragments between priv-only markers -- and refuse to let the
#   commit through if any of it would escape the boundary. You get a
#   pre-commit gate that catches leaks at your fingertips instead of
#   after the fact.
"""
check_no_private_leaks.py -- Verify no private content leaks to public.

Invocation: agent-invoked, hook-ci
Lifecycle: active

Default (no args): warns if ``seja-public/.claude/`` exists on disk (it should
have been cleaned up after the last publish), then scans the authored prose in
``seja-public/`` (``docs/`` and top-level ``*.md`` files) for:
  (a) Remaining priv-only-start/end markers (strip failure)
  (b) Known private-only patterns in .md files
The ``.claude/`` subtree is no longer mirrored into ``seja-public/`` so the
default invocation does not scan it.

With ``--candidate DIR``: scans the candidate directory's ``.claude/`` for
leaked private content (files, directories, markers, fingerprints). Used by
``pre_publish_smoke.py`` to validate a publish workspace before release.

With ``--files PATH [PATH...]`` or ``--staged``: scans source .md files in
seja-priv *before* sync. For each file, applies the same strip-private-sections
logic as ``tools/sync_to_public.py`` and flags content fingerprints that survive
the strip. This is the pre-commit gate that catches leaks at the developer's
fingertips rather than after sync.

Exit 0 if clean, exit 1 with details if leaks found.
"""
from __future__ import annotations

import argparse
import re
import subprocess
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
# Rules files (.claude/rules/*.md) may legitimately reference these terms
# (e.g., release-process.md explains the manual sync under A2), so they are
# intentionally excluded from this check.
SKILL_CONTENT_PATTERNS: list[tuple[str, str]] = [
    (r"--harness", "harness-exclusive flag in public skill docs"),
    (r"seja-public/", "reference to sync target in public skill docs"),
    (r"sync_to_public", "reference to sync mechanism in public skill docs"),
    (r"generate_changelog_data", "reference to private script in public skill docs"),
    (r"seja-priv", "reference to private repo in public skill docs"),
    (r"scripts/priv", "reference to private scripts dir in public skill docs"),
    (r"strip_private_sections", "reference to private sync function in public skill docs"),
    (r"pre_publish_smoke", "reference to private smoke-test tool in public skill docs"),
    (r"monthly-dogfood", "reference to private dogfood playbook in public skill docs"),
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


# Stripper regexes mirror those in tools/sync_to_public.py. Kept inline so
# check_no_private_leaks.py is self-contained and can run from seja-public/
# (where tools/ is not synced). Golden tests in tools/tests/ guard the canonical
# stripper; if the regexes diverge, those tests and the content fingerprints
# below will catch the mismatch.
_PRIV_SECTION_RE = re.compile(
    r"^[ \t]*<!-- priv-only-start -->.*?^[ \t]*<!-- priv-only-end -->\n?",
    re.MULTILINE | re.DOTALL,
)
_FENCED_CODE_BLOCK_RE = re.compile(
    r"^(`{3,}|~{3,}).*?\n.*?^\1\s*$",
    re.MULTILINE | re.DOTALL,
)

# Paths under seja-priv that --staged should ignore. These are private by
# convention (the sync tool already excludes them) or are generated artifacts
# that legitimately contain private terminology.
_STAGED_EXCLUDE_PREFIXES = (
    "project/",
    "_output/",
    ".claude/skills/scripts/priv/",
    "seja-public/",
)


def _strip_private_sections(content: str) -> str:
    """Remove priv-only sections, preserving markers inside fenced code blocks."""
    placeholders: list[str] = []

    def _protect(m: re.Match) -> str:
        placeholders.append(m.group(0))
        return f"\x00FENCED{len(placeholders) - 1}\x00"

    protected = _FENCED_CODE_BLOCK_RE.sub(_protect, content)
    stripped = _PRIV_SECTION_RE.sub("", protected)
    for i, block in enumerate(placeholders):
        stripped = stripped.replace(f"\x00FENCED{i}\x00", block)
    return stripped


def _get_staged_md_files() -> list[Path]:
    """Return staged .md files, filtered to the shared (syncable) subset."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    files: list[Path] = []
    for line in result.stdout.splitlines():
        rel = line.strip()
        if not rel or not rel.endswith(".md"):
            continue
        if any(rel.startswith(prefix) for prefix in _STAGED_EXCLUDE_PREFIXES):
            continue
        abs_path = REPO_ROOT / rel
        if abs_path.is_file():
            files.append(abs_path)
    return files


def check_files_pre_sync(files: list[Path]) -> list[str]:
    """Check each source .md file as it would appear after sync.

    Applies the same strip-private-sections transform as sync_to_public.py,
    then scans the stripped output for (a) residual priv-only markers
    (indicates malformed/unbalanced markers) and (b) SKILL_CONTENT_PATTERNS
    matches (indicates unmarked private terminology).
    """
    issues: list[str] = []
    marker_re = re.compile(r"<!-- priv-only-(start|end) -->")
    compiled_patterns = [
        (re.compile(p), desc) for p, desc in SKILL_CONTENT_PATTERNS
    ]

    for source in files:
        try:
            raw = source.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        stripped = _strip_private_sections(raw)
        try:
            rel = source.relative_to(REPO_ROOT)
        except ValueError:
            rel = source

        for i, line in _lines_outside_fences(stripped):
            if marker_re.search(line):
                issues.append(
                    f"  {rel}:{i} -- priv-only marker survives strip "
                    f"(malformed or unbalanced)"
                )

        # Fingerprints only apply to SKILL.md files (other files may legitimately
        # reference the terms; see SKILL_CONTENT_PATTERNS docstring).
        if source.name == "SKILL.md":
            for pattern, description in compiled_patterns:
                for i, line in _lines_outside_fences(stripped):
                    if pattern.search(line):
                        issues.append(
                            f"  {rel}:{i} -- {description} "
                            f"(pattern escaped priv-only markers)"
                        )
    return issues


def _collect_prose_md(public_dir: Path) -> list[Path]:
    """Return authored prose .md files in the public tree.

    Collects top-level *.md and docs/**/*.md -- the files that are
    authored directly in seja-public/. Excludes .claude/ (no longer
    mirrored) and any other stale subtrees.
    """
    files: list[Path] = []
    # Top-level .md files (CHANGELOG.md, README.md, etc.)
    files.extend(sorted(public_dir.glob("*.md")))
    # docs/ subtree
    docs_dir = public_dir / "docs"
    if docs_dir.is_dir():
        files.extend(sorted(docs_dir.rglob("*.md")))
    return files


def _check_prose_markers(files: list[Path], base_dir: Path) -> list[str]:
    """Check authored prose files for priv-only markers."""
    issues: list[str] = []
    marker_re = re.compile(r"<!-- priv-only-(start|end) -->")
    for md_file in files:
        try:
            content = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in _lines_outside_fences(content):
            if marker_re.search(line):
                rel = md_file.relative_to(base_dir)
                issues.append(f"  {rel}:{i} -- priv-only marker not stripped")
    return issues


def _scan_candidate(candidate_dir: Path) -> list[str]:
    """Full leak scan of a candidate publish directory.

    Used by ``--candidate`` mode. Checks the candidate's ``.claude/``
    subtree for markers, private files, private dirs, private patterns,
    and SKILL.md content fingerprints -- the same checks that the old
    default path ran against ``seja-public/``.
    """
    all_issues: list[str] = []
    all_issues.extend(check_markers(candidate_dir))
    all_issues.extend(check_private_files(candidate_dir))
    all_issues.extend(check_private_dirs(candidate_dir))
    if not all_issues:
        all_issues.extend(check_private_patterns(candidate_dir))
    all_issues.extend(check_skill_content_fingerprints(candidate_dir))
    return all_issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--files", nargs="+", metavar="PATH",
        help="Check specific source .md files (pre-sync). Applies strip "
             "before scanning for residual markers and fingerprints.",
    )
    mode.add_argument(
        "--staged", action="store_true",
        help="Check staged .md files (pre-commit gate). Equivalent to "
             "--files with the staged subset auto-discovered via git.",
    )
    mode.add_argument(
        "--candidate", metavar="DIR",
        help="Scan a candidate publish directory for leaked private "
             "content. Used by pre_publish_smoke.py to validate a "
             "publish workspace before release.",
    )
    args = parser.parse_args(argv)

    if args.files or args.staged:
        if args.staged:
            files = _get_staged_md_files()
            if not files:
                print("Private content leak check: no shared .md files staged")
                return 0
        else:
            files = [Path(f).resolve() for f in args.files]
        issues = check_files_pre_sync(files)
        if issues:
            print(f"Private content leak check (pre-sync): ISSUES FOUND in {len(files)} file(s)\n")
            for issue in issues:
                print(issue)
            print(f"\n{len(issues)} issue(s) found.")
            print("\nFix by wrapping private content in <!-- priv-only-start -->")
            print("/ <!-- priv-only-end --> markers, or by removing the leak.")
            return 1
        print(f"Private content leak check (pre-sync): PASS ({len(files)} file(s) scanned)")
        return 0

    if args.candidate:
        candidate = Path(args.candidate).resolve()
        if not candidate.is_dir():
            print(f"SKIP: candidate directory {candidate} does not exist")
            return 0
        issues = _scan_candidate(candidate)
        if issues:
            print("Private content leak check (candidate): ISSUES FOUND\n")
            for issue in issues:
                print(issue)
            print(f"\n{len(issues)} issue(s) found.")
            return 1
        print(f"Private content leak check (candidate): PASS")
        return 0

    # Default mode: scan authored prose in seja-public/ for priv-only
    # markers and private patterns. The .claude/ subtree is no longer
    # mirrored into seja-public/ (plan-000533 step 1), so we only scan
    # docs/ and top-level *.md files.
    if not PUBLIC_DIR.is_dir():
        print(f"SKIP: {PUBLIC_DIR} does not exist")
        return 0

    warnings: list[str] = []
    claude_dir = PUBLIC_DIR / ".claude"
    if claude_dir.is_dir():
        warnings.append(
            f"WARNING: {claude_dir} exists on disk. It should have been "
            f"cleaned up after the last publish. The publish pipeline no "
            f"longer mirrors .claude/ into seja-public/."
        )

    all_issues: list[str] = []
    # Scan authored prose (docs/ and top-level *.md) for markers.
    # Skip .claude/ -- it is no longer mirrored.
    prose_files = _collect_prose_md(PUBLIC_DIR)
    all_issues.extend(_check_prose_markers(prose_files, PUBLIC_DIR))

    for w in warnings:
        print(w)
    if all_issues:
        if warnings:
            print()
        print("Private content leak check: ISSUES FOUND\n")
        for issue in all_issues:
            print(issue)
        print(f"\n{len(all_issues)} issue(s) found.")
        return 1

    if warnings:
        # Warnings are non-fatal but deserve attention.
        print("\nPrivate content leak check: PASS (with warnings)")
        return 0

    print("Private content leak check: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
