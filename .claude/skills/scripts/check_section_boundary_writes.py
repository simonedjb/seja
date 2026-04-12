#!/usr/bin/env python3
"""
check_section_boundary_writes.py -- Reject contiguous write regions that cross
an H2 section boundary in registered files.

Runs as a preflight check (post-skill step 6c via run_preflight_fast.py)
alongside `check_changelog_append_only.py` and `check_human_markers_only.py`.
Where those scripts enforce marker-only / append-only discipline on Human
(markers) files, this script enforces a different invariant on Agent-classified
files with a section-boundary contract: post-skill writes target one H2 domain
section at a time. A single contiguous change run (a maximal sequence of
consecutive `+`/`-` lines in a hunk) must not span two or more H2 sections.

Change-run semantics (plan-000269 Amendment A)
----------------------------------------------
A unified-diff hunk is NOT a single contiguous write region. A hunk can contain
multiple disjoint edit regions separated by context lines, and the hunk header's
line range covers both the edits AND the intervening context. The validator
walks each hunk body line-by-line and groups consecutive `+`/`-` lines into
change runs (context lines terminate a run). Each change run is checked
independently against the section maps. This prevents false-positives where a
hunk's context lines happen to cross an H2 boundary while the actual edits are
confined to one section.

Preamble policy (plan-000269 Amendment C)
-----------------------------------------
The region before the first `## ` heading is treated as an implicit "preamble"
section. Change runs confined entirely within the preamble are allowed. Change
runs that start in the preamble and extend past the first `## ` heading are
violations. `_section_for_line` returns the sentinel `"<preamble>"` for lines
before the first H2, and violation comparison treats `"<preamble>"` as a
distinct section that cannot be merged with any H2.

H2 header insertion / deletion (plan-000269 Amendment B)
--------------------------------------------------------
Section maps are extracted from BOTH the prior and the current file version.
Adding a new H2 heading (pure `+` run whose every `+` line is a `## ` heading)
is allowed: it is recorded as "allowed: H2 header insertion" and bypasses the
boundary check. Removing an H2 heading is a cross-section rewrite masquerading
as a deletion; if any `-` line matches `^##\\s+.+` and that heading is absent
from the current file, the run is rejected as "cross-section rewrite via H2
deletion".

First-write acceptance (plan-000269 Amendment D)
------------------------------------------------
When a registered file is new-in-diff (no prior version at HEAD), the validator
skips silently (same tradeoff as `check_changelog_append_only.py`). The
validator's scope is post-commit regression discipline; first-write scenarios
(e.g., `/design` brownfield template copy, post-skill's first instantiation of
the unified file) are out of scope. A buggy first-write is caught by manual
inspection or by the next commit's diff against the first-write baseline.

Usage
-----
    python .claude/skills/scripts/check_section_boundary_writes.py --staged
    python .claude/skills/scripts/check_section_boundary_writes.py --range HEAD~1..HEAD
    # Testing only (requires SEJA_ALLOW_TEST_DIFF_INPUT=1):
    SEJA_ALLOW_TEST_DIFF_INPUT=1 python .claude/skills/scripts/check_section_boundary_writes.py \\
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


if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]


# Files whose H2 sections must not be crossed by a single contiguous write
# region. Each entry maps a repo-relative POSIX path to a sentinel value (the
# value is reserved for future per-file configuration, e.g., allowlisted
# section pairs); for now all values are None meaning "enforce strict boundary
# between any two H2s". Both template and project paths are registered per the
# dual-path pattern (plan-000267 Amendment 1, plan-000269 Step 2).
SECTION_BOUNDARY_FILES: dict[str, None] = {
    "_references/template/product-design-as-coded.md": None,
    "_references/project/product-design-as-coded.md": None,
    # Legacy path (pre-plan-000271); remove after workspace /upgrade landing or SEJA 2.9.x, whichever first.
    "_references/project/as-coded.md": None,
}


PREAMBLE_SENTINEL = "<preamble>"
_H2_LINE_RE = re.compile(r"^##\s+(.+?)\s*$")


def _find_repo_root() -> Path:
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".claude").is_dir():
            return current
        current = current.parent
    return Path.cwd().resolve()


REPO_ROOT = _find_repo_root()


def _extract_h2_sections(text: str) -> list[tuple[str, int, int]]:
    """Return a list of (heading, start_line, end_line) tuples for each H2 section.

    Line numbers are 1-based to match git diff conventions. `start_line` is the
    line number of the `## Heading` line. `end_line` is the line number of the
    line BEFORE the next `## ` heading, or the last line of the file.

    Lines before the first `## ` heading are NOT included in any section here;
    `_section_for_line` returns the preamble sentinel for them.
    """
    lines = text.splitlines()
    matches: list[tuple[str, int]] = []
    for i, line in enumerate(lines, start=1):
        m = _H2_LINE_RE.match(line)
        if m:
            matches.append((m.group(1), i))
    sections: list[tuple[str, int, int]] = []
    for idx, (heading, start) in enumerate(matches):
        end = matches[idx + 1][1] - 1 if idx + 1 < len(matches) else len(lines)
        sections.append((heading, start, end))
    return sections


def _section_for_line(
    sections: list[tuple[str, int, int]], line_num: int
) -> str:
    """Return the section that contains the given 1-based line number.

    Returns the preamble sentinel for lines before the first `## ` heading.
    """
    for heading, start, end in sections:
        if start <= line_num <= end:
            return heading
    return PREAMBLE_SENTINEL


class ChangeRun:
    """A maximal sequence of consecutive +/- lines within a single hunk."""

    __slots__ = ("added_lines", "removed_lines", "new_starts", "old_starts")

    def __init__(self) -> None:
        # Text of added/removed lines (without the leading +/- marker).
        self.added_lines: list[str] = []
        self.removed_lines: list[str] = []
        # 1-based line numbers for each added line in the NEW file.
        self.new_starts: list[int] = []
        # 1-based line numbers for each removed line in the OLD file.
        self.old_starts: list[int] = []

    def is_empty(self) -> bool:
        return not self.added_lines and not self.removed_lines

    def new_span(self) -> tuple[int, int] | None:
        if not self.new_starts:
            return None
        return (min(self.new_starts), max(self.new_starts))

    def old_span(self) -> tuple[int, int] | None:
        if not self.old_starts:
            return None
        return (min(self.old_starts), max(self.old_starts))


def _parse_hunks(diff_text: str, target_path: str) -> list[tuple[str, list[ChangeRun]]]:
    """Parse the unified diff and return hunks for the target file.

    Returns a list of (hunk_header, change_runs) tuples for every hunk that
    belongs to `target_path`. Only hunks under the matching `diff --git` block
    are returned.
    """
    result: list[tuple[str, list[ChangeRun]]] = []
    lines = diff_text.splitlines()
    i = 0
    n = len(lines)
    in_target = False
    while i < n:
        line = lines[i]
        m_diff = re.match(r"^diff --git a/(\S+) b/(\S+)$", line)
        if m_diff:
            file_b = m_diff.group(2).replace("\\", "/")
            in_target = file_b == target_path
            i += 1
            continue
        if not in_target:
            i += 1
            continue
        m_hunk = re.match(
            r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line
        )
        if not m_hunk:
            i += 1
            continue
        hunk_header = line
        old_start = int(m_hunk.group(1))
        new_start = int(m_hunk.group(3))
        i += 1
        runs: list[ChangeRun] = []
        current_run = ChangeRun()
        current_old = old_start
        current_new = new_start
        while i < n:
            body_line = lines[i]
            if body_line.startswith("@@ ") or body_line.startswith("diff --git "):
                break
            if body_line.startswith("\\"):
                # "\ No newline at end of file" — ignore
                i += 1
                continue
            if not body_line:
                # Empty body line represents a context blank line in the file.
                # Treat as context terminating the run.
                if not current_run.is_empty():
                    runs.append(current_run)
                    current_run = ChangeRun()
                current_old += 1
                current_new += 1
                i += 1
                continue
            marker = body_line[0]
            content = body_line[1:]
            if marker == " ":
                if not current_run.is_empty():
                    runs.append(current_run)
                    current_run = ChangeRun()
                current_old += 1
                current_new += 1
            elif marker == "+":
                current_run.added_lines.append(content)
                current_run.new_starts.append(current_new)
                current_new += 1
            elif marker == "-":
                current_run.removed_lines.append(content)
                current_run.old_starts.append(current_old)
                current_old += 1
            else:
                # Unknown marker — treat as context
                if not current_run.is_empty():
                    runs.append(current_run)
                    current_run = ChangeRun()
                current_old += 1
                current_new += 1
            i += 1
        if not current_run.is_empty():
            runs.append(current_run)
        result.append((hunk_header, runs))
    return result


def _is_h2_line(line: str) -> bool:
    return bool(_H2_LINE_RE.match(line))


def _classify_run(
    run: ChangeRun,
    prior_sections: list[tuple[str, int, int]],
    current_sections: list[tuple[str, int, int]],
    current_h2_headings: set[str],
) -> tuple[str, str | None]:
    """Classify a change run. Returns (status, reason).

    Status is one of:
      - "ok"                -- within a single section
      - "ok-h2-insertion"   -- pure H2 header insertion (Amendment B)
      - "violation"         -- cross-boundary write; `reason` is the human text

    `current_h2_headings` is the set of H2 heading texts currently present in
    the new file (used to detect H2 deletions that were not reintroduced).
    """
    new_span = run.new_span()
    old_span = run.old_span()

    # Amendment B (a): pure H2 header insertion allowance.
    # No `-` lines, at least one added `## ` heading, and every other added
    # line is blank (insertions commonly include blank lines around the new
    # heading).
    if (
        not run.removed_lines
        and run.added_lines
        and any(_is_h2_line(ln) for ln in run.added_lines)
        and all(_is_h2_line(ln) or ln.strip() == "" for ln in run.added_lines)
    ):
        return ("ok-h2-insertion", None)

    # Amendment B (b): cross-section rewrite via H2 deletion.
    for removed in run.removed_lines:
        m = _H2_LINE_RE.match(removed)
        if m and m.group(1) not in current_h2_headings:
            return (
                "violation",
                f"cross-section rewrite via H2 deletion "
                f"(removed '## {m.group(1)}' is absent from current file)",
            )

    # Amendment B (c): check new span against current sections.
    if new_span is not None:
        start_section = _section_for_line(current_sections, new_span[0])
        end_section = _section_for_line(current_sections, new_span[1])
        if start_section != end_section:
            return (
                "violation",
                f"change run in new file spans line {new_span[0]} "
                f"('{start_section}') to line {new_span[1]} ('{end_section}')",
            )

    # Also check old span against prior sections (catches pure deletion runs
    # and mixed runs where the prior span crosses a prior boundary).
    if old_span is not None:
        start_section = _section_for_line(prior_sections, old_span[0])
        end_section = _section_for_line(prior_sections, old_span[1])
        if start_section != end_section:
            return (
                "violation",
                f"change run in prior file spans line {old_span[0]} "
                f"('{start_section}') to line {old_span[1]} ('{end_section}')",
            )

    return ("ok", None)


def _get_prior_file(
    path: str, args: argparse.Namespace
) -> str | None:
    if args.diff_from_file:
        slug = path.replace("/", "__")
        prior_path = (
            Path(args.diff_from_file).parent
            / f"{Path(args.diff_from_file).stem}.{slug}.prior"
        )
        if prior_path.is_file():
            return prior_path.read_text(encoding="utf-8")
        return None

    if args.range:
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
        return None
    return result.stdout


def _get_current_file(path: str, args: argparse.Namespace) -> str | None:
    if args.diff_from_file:
        slug = path.replace("/", "__")
        current_path = (
            Path(args.diff_from_file).parent
            / f"{Path(args.diff_from_file).stem}.{slug}.current"
        )
        if current_path.is_file():
            return current_path.read_text(encoding="utf-8")
        return None

    if args.range:
        head_ref = args.range.split("..")[-1] or "HEAD"
        ref = f"{head_ref}:{path}"
    else:
        ref = f":{path}"

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


def _get_diff_text(args: argparse.Namespace) -> str:
    if args.diff_from_file:
        return Path(args.diff_from_file).read_text(encoding="utf-8")

    if args.range:
        cmd = ["git", "diff", args.range]
    else:
        cmd = ["git", "diff", "--cached"]

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
        return ""
    return result.stdout


def _get_changed_files_from_diff(diff_text: str) -> list[str]:
    files: list[str] = []
    for line in diff_text.splitlines():
        m = re.match(r"^diff --git a/(\S+) b/(\S+)$", line)
        if m:
            files.append(m.group(2).replace("\\", "/"))
    return files


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Reject contiguous write regions that cross an H2 section "
            "boundary in registered Agent-classified files."
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--staged",
        action="store_true",
        help="Check staged changes (default).",
    )
    mode.add_argument(
        "--range",
        help="Check a git ref range, e.g. HEAD~1..HEAD.",
    )
    parser.add_argument(
        "--diff-from-file",
        help=(
            "Read a unified diff from a file (testing only; requires "
            "SEJA_ALLOW_TEST_DIFF_INPUT=1)."
        ),
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print detailed info."
    )
    args = parser.parse_args()

    if not SECTION_BOUNDARY_FILES:
        print(
            "WARNING: no files in SECTION_BOUNDARY_FILES; "
            "check_section_boundary_writes.py is a no-op",
            file=sys.stderr,
        )
        return 0

    if args.diff_from_file and os.environ.get("SEJA_ALLOW_TEST_DIFF_INPUT") != "1":
        print(
            "ERROR: --diff-from-file requires SEJA_ALLOW_TEST_DIFF_INPUT=1 "
            "(testing only)",
            file=sys.stderr,
        )
        return 2

    diff_text = _get_diff_text(args)
    changed_files = _get_changed_files_from_diff(diff_text)

    all_violations: list[dict] = []
    file_count = 0

    for file_path in changed_files:
        normalized = file_path.replace("\\", "/")
        if normalized not in SECTION_BOUNDARY_FILES:
            continue

        file_count += 1

        prior_text = _get_prior_file(normalized, args)
        if prior_text is None:
            if args.verbose:
                print(
                    f"info: {normalized} is new in this commit; "
                    "skipping section-boundary check",
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

        prior_sections = _extract_h2_sections(prior_text)
        current_sections = _extract_h2_sections(current_text)
        current_headings = {heading for heading, _s, _e in current_sections}

        hunks = _parse_hunks(diff_text, normalized)
        for hunk_header, runs in hunks:
            for run in runs:
                status, reason = _classify_run(
                    run, prior_sections, current_sections, current_headings
                )
                if status == "violation":
                    all_violations.append(
                        {
                            "file": normalized,
                            "hunk": hunk_header,
                            "reason": reason,
                        }
                    )

    if all_violations:
        print(
            f"FAIL: {len(all_violations)} section-boundary violation(s) in "
            f"{file_count} file(s). A post-skill write crossed an H2 boundary. "
            "This is a bug -- post-skill should target one section at a time. "
            "File a framework bug.",
            file=sys.stderr,
        )
        for v in all_violations:
            print(f"  file: {v['file']}", file=sys.stderr)
            print(f"  hunk: {v['hunk']}", file=sys.stderr)
            print(f"  reason: {v['reason']}", file=sys.stderr)
            print("", file=sys.stderr)
        return 1

    print(
        f"PASS: no section-boundary crossings detected in {file_count} file(s)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
