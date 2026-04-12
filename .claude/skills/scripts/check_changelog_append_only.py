#!/usr/bin/env python3
"""
check_changelog_append_only.py -- Enforce append-only discipline on designated
sections of Human (markers) files.

Runs as a preflight check (post-skill step 6c via run_preflight_fast.py) alongside
`check_human_markers_only.py`. Where that script enforces "every modified line
matches an allowed marker regex", this one enforces the orthogonal invariant
"historical content in these sections is never mutated or removed".

Two rules, section-specific (per plan-000267 Amendment 2):

  - CHANGELOG sections: strict line-level prefix-preserving extension. Every
    line that existed in the prior version must still exist, in the same order,
    at the same relative position from the start of the section. Only additions
    at the end are allowed. Used for `## CHANGELOG`.

  - Non-CHANGELOG append-only sections (e.g., `## 5. Discovered User Journeys`):
    prose-only prefix-preserving extension. Lines matching any entry in
    ALLOWED_MARKERS (imported from human_markers_registry) are filtered out of
    both prior and current bodies before comparison -- these are managed marker
    lines that apply_marker.py may legally insert above existing headings. The
    residual prose sequences must be prefix-preserving. This allows apply_marker
    to insert <!-- INCORPORATED: plan-NNN | YYYY-MM-DD --> on the line above an
    existing `### JM-E-NNN:` heading without triggering a middle-insertion
    violation, while still rejecting any prose line edit or deletion.

Accepted tradeoff: a malicious commit that deletes the file and recreates it
with different historical content would pass this check silently (file absent
at prior commit -> skipped). This is acceptable because (a) such a commit is
detectable by any git-history review, (b) the validator's scope is local-commit
discipline, not git-history integrity, and (c) the framework's broader threat
model (see _references/general/threat-model.md) treats history rewrites as a
separate trust boundary.

Usage
-----
    python .claude/skills/scripts/check_changelog_append_only.py --staged
    python .claude/skills/scripts/check_changelog_append_only.py --range HEAD~1..HEAD
    # Testing only (requires SEJA_ALLOW_TEST_DIFF_INPUT=1):
    SEJA_ALLOW_TEST_DIFF_INPUT=1 python .claude/skills/scripts/check_changelog_append_only.py \\
        --diff-from-file path/to/synthetic.diff

Exit codes: 0 pass (or no-op empty registry), 1 violation, 2 runtime error.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

from human_markers_registry import ALLOWED_MARKERS


if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]


# Files whose designated sections are append-only. Each entry maps a repo-relative
# POSIX path to a list of H2 section headings whose bodies must only grow (never
# mutate historical lines) between commits. Both template and project paths are
# registered per plan-000267 Amendment 1.
APPEND_ONLY_SECTIONS: dict[str, list[str]] = {
    "_references/template/ux-research-results.md": ["5. Discovered User Journeys", "CHANGELOG"],
    "_references/project/ux-research-results.md": ["5. Discovered User Journeys", "CHANGELOG"],
    "_references/template/product-design-as-intended.md": ["Decisions", "CHANGELOG"],
    "_references/project/product-design-as-intended.md": ["Decisions", "CHANGELOG"],
}


def _find_repo_root() -> Path:
    """Walk up from this script's location to find the repo root (.claude/ marker)."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".claude").is_dir():
            return current
        current = current.parent
    return Path.cwd().resolve()


REPO_ROOT = _find_repo_root()


def _extract_h2_section(text: str, heading: str) -> str:
    """Return the body of an H2 section identified by its exact heading text.

    Splits on '^## <heading>\\s*$' (start) through the next '^## ' or EOF.
    Returns empty string if the heading is not found. The heading is the text
    after '## ' -- e.g., for '## 5. Discovered User Journeys', pass
    '5. Discovered User Journeys'.
    """
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(text)
    return m.group(1) if m else ""


def _normalize_lines(text: str) -> list[str]:
    """Split into lines, rstrip each, collapse runs of 2+ blank lines to 1.

    Cosmetic whitespace edits inside a section are allowed; byte-identical
    newlines are not required.
    """
    raw_lines = [line.rstrip() for line in text.splitlines()]
    normalized: list[str] = []
    prev_blank = False
    for line in raw_lines:
        is_blank = line == ""
        if is_blank and prev_blank:
            continue
        normalized.append(line)
        prev_blank = is_blank
    return normalized


def _line_matches_marker(line: str) -> bool:
    """Return True if the line matches any marker regex from ALLOWED_MARKERS."""
    stripped = line.strip()
    if not stripped:
        return False
    for spec in ALLOWED_MARKERS.values():
        if re.fullmatch(spec["line_regex"], stripped):
            return True
    return False


def _filter_markers(lines: list[str]) -> list[str]:
    """Return lines with all marker lines removed (prose-only filter)."""
    return [line for line in lines if not _line_matches_marker(line)]


def _is_prefix_preserving(prior: list[str], current: list[str]) -> tuple[bool, str]:
    """Check whether `current` is a prefix-preserving extension of `prior`.

    Returns (ok, reason). `ok` is True iff every line in `prior` appears in
    `current` in the same order starting from index 0, with any new lines only
    appended at the end.
    """
    if len(current) < len(prior):
        return False, (
            f"current section has {len(current)} lines, prior had {len(prior)} "
            "-- lines removed"
        )
    for i, prior_line in enumerate(prior):
        if i >= len(current):
            return False, f"prior line {i + 1} missing from current section"
        if current[i] != prior_line:
            return False, (
                f"line {i + 1} changed: prior={prior_line!r} "
                f"current={current[i]!r}"
            )
    return True, ""


def _check_section(
    file_path: str,
    section_heading: str,
    prior_body: str,
    current_body: str,
) -> list[dict]:
    """Validate a single section against the appropriate rule. Returns violations."""
    violations: list[dict] = []

    prior_lines = _normalize_lines(prior_body)
    current_lines = _normalize_lines(current_body)

    is_changelog = section_heading == "CHANGELOG"

    if is_changelog:
        # Strict line-level prefix-preserving extension
        ok, reason = _is_prefix_preserving(prior_lines, current_lines)
        if not ok:
            violations.append({
                "file": file_path,
                "section": section_heading,
                "rule": "strict",
                "reason": reason,
            })
    else:
        # Prose-only: filter out marker lines from both, then compare residual
        prior_prose = _filter_markers(prior_lines)
        current_prose = _filter_markers(current_lines)
        ok, reason = _is_prefix_preserving(prior_prose, current_prose)
        if not ok:
            violations.append({
                "file": file_path,
                "section": section_heading,
                "rule": "prose-only",
                "reason": reason,
            })

    return violations


def _get_prior_file(
    path: str, args: argparse.Namespace
) -> str | None:
    """Return the prior version of `path` from git history, or None if absent.

    For --staged mode, returns the HEAD version. For --range mode, returns the
    version at the start of the range. For --diff-from-file mode, reads a
    companion prior file from `<diff-from-file>.<path-slug>.prior` if it exists.
    """
    if args.diff_from_file:
        # Testing mode: the test fixture writes a prior version alongside the
        # diff file. The slug is the path with / replaced by __.
        slug = path.replace("/", "__")
        prior_path = Path(args.diff_from_file).parent / f"{Path(args.diff_from_file).stem}.{slug}.prior"
        if prior_path.is_file():
            return prior_path.read_text(encoding="utf-8")
        return None

    if args.range:
        # Use the base of the range (before the ..)
        base_ref = args.range.split("..")[0]
    else:
        base_ref = "HEAD"

    try:
        result = subprocess.run(
            ["git", "show", f"{base_ref}:{path}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except FileNotFoundError:
        print("ERROR: git not found in PATH", file=sys.stderr)
        sys.exit(2)
    if result.returncode != 0:
        # File absent at prior commit (new file) -- silent skip per spec
        return None
    return result.stdout


def _get_current_file(path: str, args: argparse.Namespace) -> str | None:
    """Return the current (staged or range-end) version of `path`, or None if absent.

    For --staged mode, returns the staged version (git show :<path>).
    For --range mode, returns the version at the end of the range.
    For --diff-from-file mode, reads a companion current file.
    """
    if args.diff_from_file:
        slug = path.replace("/", "__")
        current_path = Path(args.diff_from_file).parent / f"{Path(args.diff_from_file).stem}.{slug}.current"
        if current_path.is_file():
            return current_path.read_text(encoding="utf-8")
        return None

    if args.range:
        # End of the range
        head_ref = args.range.split("..")[-1] or "HEAD"
        ref = f"{head_ref}:{path}"
    else:
        ref = f":{path}"  # Staged version

    try:
        result = subprocess.run(
            ["git", "show", ref],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except FileNotFoundError:
        print("ERROR: git not found in PATH", file=sys.stderr)
        sys.exit(2)
    if result.returncode != 0:
        return None
    return result.stdout


def _get_changed_files(args: argparse.Namespace) -> list[str]:
    """Return the list of files changed in the staged or range diff."""
    if args.diff_from_file:
        # Testing mode: parse the diff text for file headers
        diff_text = Path(args.diff_from_file).read_text(encoding="utf-8")
        files: list[str] = []
        for line in diff_text.splitlines():
            m = re.match(r"^diff --git a/(\S+) b/(\S+)$", line)
            if m:
                files.append(m.group(2).replace("\\", "/"))
        return files

    if args.range:
        cmd = ["git", "diff", "--name-only", args.range]
    else:
        cmd = ["git", "diff", "--cached", "--name-only"]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except FileNotFoundError:
        print("ERROR: git not found in PATH", file=sys.stderr)
        sys.exit(2)
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enforce append-only discipline on designated sections of Human (markers) files."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true", help="Check staged changes (default).")
    mode.add_argument("--range", help="Check a git ref range, e.g. HEAD~1..HEAD.")
    parser.add_argument(
        "--diff-from-file",
        help="Read a unified diff from a file (testing only; requires SEJA_ALLOW_TEST_DIFF_INPUT=1).",
    )
    parser.add_argument("--verbose", action="store_true", help="Print detailed info.")
    args = parser.parse_args()

    # Loud no-op on empty registry
    if not APPEND_ONLY_SECTIONS:
        print(
            "WARNING: no files in APPEND_ONLY_SECTIONS; check_changelog_append_only.py is a no-op",
            file=sys.stderr,
        )
        return 0

    # Test hatch env-var gate
    if args.diff_from_file and os.environ.get("SEJA_ALLOW_TEST_DIFF_INPUT") != "1":
        print(
            "ERROR: --diff-from-file requires SEJA_ALLOW_TEST_DIFF_INPUT=1 (testing only)",
            file=sys.stderr,
        )
        return 2

    changed_files = _get_changed_files(args)

    all_violations: list[dict] = []
    section_count = 0
    file_count = 0

    for file_path in changed_files:
        normalized = file_path.replace("\\", "/")
        if normalized not in APPEND_ONLY_SECTIONS:
            continue

        file_count += 1
        sections = APPEND_ONLY_SECTIONS[normalized]

        prior_text = _get_prior_file(normalized, args)
        if prior_text is None:
            # New file in this commit -- no prior version to diff against
            if args.verbose:
                print(
                    f"info: {normalized} is new in this commit; skipping append-only check",
                    file=sys.stderr,
                )
            continue

        current_text = _get_current_file(normalized, args)
        if current_text is None:
            if args.verbose:
                print(
                    f"info: {normalized} not readable at current ref; skipping",
                    file=sys.stderr,
                )
            continue

        for section_heading in sections:
            section_count += 1
            prior_body = _extract_h2_section(prior_text, section_heading)
            current_body = _extract_h2_section(current_text, section_heading)

            if not prior_body and not current_body:
                if args.verbose:
                    print(
                        f"info: section '## {section_heading}' not present in {normalized}",
                        file=sys.stderr,
                    )
                continue

            violations = _check_section(
                normalized, section_heading, prior_body, current_body
            )
            all_violations.extend(violations)

    if all_violations:
        print(
            f"FAIL: {len(all_violations)} append-only violation(s) in "
            f"{file_count} Human (markers) file(s)",
            file=sys.stderr,
        )
        for v in all_violations:
            print(f"  file: {v['file']}", file=sys.stderr)
            print(f"  section: ## {v['section']} (rule: {v['rule']})", file=sys.stderr)
            print(f"  reason: {v['reason']}", file=sys.stderr)
            print("", file=sys.stderr)
        return 1

    print(
        f"PASS: append-only discipline preserved in {section_count} sections "
        f"across {file_count} file(s)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
