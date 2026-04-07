#!/usr/bin/env python3
"""
check_plan_coverage.py -- Plan coverage verification against design-intent requirements.

Extracts requirement IDs (REQ-TYPE-NNN markers) from design-intent-to-be.md,
scans plan files for Traces: metadata, and computes the coverage gap. Reports
uncovered requirements grouped by section and classification.

Exit codes: 0 = full coverage or no requirements, 1 = gaps found, 2 = script error.

Usage
-----
    python .claude/skills/scripts/check_plan_coverage.py [OPTIONS]

Options:
    --root DIR       Repository root (auto-detected if omitted)
    --verbose        Show passing checks and extra detail
    --filter SEVER   Minimum severity to report: error, warning, info (default: info)
    --mode MODE      Enforcement mode: advisory (always exit 0), blocking (exit 1 on
                     security gaps). Default: blocking.

CHECK_PLUGIN_MANIFEST:
  name: Plan Coverage Verification
  stack:
    backend: [any]
    frontend: [any]
  scope: planning
  critical: false
"""
from __future__ import annotations

import argparse
import importlib
import re
import sys
from pathlib import Path
from typing import NamedTuple


# ---------------------------------------------------------------------------
# Repo root discovery
# ---------------------------------------------------------------------------

def _find_repo_root(start: Path | None = None) -> Path:
    """Walk up from start until we find a .claude/ directory."""
    candidate = (start or Path(__file__).resolve().parent)
    while candidate != candidate.parent:
        if (candidate / ".claude").is_dir():
            return candidate
        candidate = candidate.parent
    return Path.cwd()


# ---------------------------------------------------------------------------
# Finding data structure (matches check_design_output.py)
# ---------------------------------------------------------------------------

class Finding(NamedTuple):
    path: str
    line: int
    severity: str  # "error", "warning", "info"
    message: str
    plugin: str


SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


# ---------------------------------------------------------------------------
# project_config loader
# ---------------------------------------------------------------------------

def _load_project_config_get(root: Path):
    """Load project_config.get without polluting sys.path."""
    scripts_dir = str(root / ".claude" / "skills" / "scripts")
    try:
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        mod = importlib.import_module("project_config")
        return mod.get
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Classification mapping
# ---------------------------------------------------------------------------

CLASSIFICATION_MAP: dict[str, str] = {
    "ENT": "technical",
    "PERM": "security",
    "VAL": "security",
    "UX": "ux",
    "MC": "ux",
    "JM": "ux",
    "I18N": "cross-cutting",
    "DELTA": "technical",
}

SECURITY_CLASSIFICATIONS = {"security"}


# ---------------------------------------------------------------------------
# Requirement extraction
# ---------------------------------------------------------------------------

# Matches <!-- REQ-TYPE-NNN --> optionally with trailing whitespace
_REQ_MARKER_RE = re.compile(
    r"<!--\s*(REQ-([A-Z0-9]+)-(\d{3}))\s*-->",
)


class Requirement(NamedTuple):
    id: str           # e.g. "REQ-ENT-001"
    type_prefix: str  # e.g. "ENT"
    number: str       # e.g. "001"
    section: str      # section heading where found
    title: str        # next heading or table row
    classification: str  # derived from type prefix
    line: int         # line number in source file


def extract_requirements(spec_path: Path) -> list[Requirement]:
    """Extract REQ markers from a design-intent file."""
    if not spec_path.is_file():
        return []

    try:
        text = spec_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    lines = text.splitlines()
    requirements: list[Requirement] = []
    current_section = "Unknown"

    # Track current section heading
    section_re = re.compile(r"^#{1,3}\s+(\d+)\.\s+(.+)")

    for i, line in enumerate(lines):
        # Update current section
        sec_match = section_re.match(line)
        if sec_match:
            current_section = f"{sec_match.group(1)}. {sec_match.group(2).strip()}"

        # Check for REQ marker
        for m in _REQ_MARKER_RE.finditer(line):
            req_id = m.group(1)
            type_prefix = m.group(2)
            number = m.group(3)

            # Get the next non-empty, non-comment line as title
            title = _extract_title(lines, i + 1)

            classification = CLASSIFICATION_MAP.get(type_prefix, "technical")

            requirements.append(Requirement(
                id=req_id,
                type_prefix=type_prefix,
                number=number,
                section=current_section,
                title=title,
                classification=classification,
                line=i + 1,
            ))

    return requirements


def _extract_title(lines: list[str], start_idx: int) -> str:
    """Extract the title from lines following a REQ marker."""
    for i in range(start_idx, min(start_idx + 5, len(lines))):
        line = lines[i].strip()
        if not line or line.startswith("<!--"):
            continue
        # Strip markdown heading markers
        if line.startswith("#"):
            line = re.sub(r"^#{1,6}\s*", "", line)
        # Strip table formatting
        if line.startswith("|"):
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if cells:
                line = cells[0]
        return line[:120]  # truncate long titles
    return "(untitled)"


# ---------------------------------------------------------------------------
# Trace extraction from plan files
# ---------------------------------------------------------------------------

_TRACES_RE = re.compile(
    r"-?\s*\*\*Traces\*\*:\s*(.+)",
    re.IGNORECASE,
)

_REQ_ID_RE = re.compile(r"REQ-[A-Z0-9]+-\d{3}")

_PLAN_ID_RE = re.compile(r"plan-(\d{6})")


def extract_traces(plans_dir: Path) -> dict[str, list[str]]:
    """Extract REQ ID -> [plan IDs] mapping from all plan files."""
    traces: dict[str, list[str]] = {}

    if not plans_dir.is_dir():
        return traces

    for plan_file in sorted(plans_dir.glob("plan-*.md")):
        plan_id_match = _PLAN_ID_RE.search(plan_file.name)
        plan_id = plan_id_match.group(1) if plan_id_match else plan_file.stem

        try:
            text = plan_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        for line in text.splitlines():
            m = _TRACES_RE.match(line.strip())
            if m:
                trace_text = m.group(1)
                for req_match in _REQ_ID_RE.finditer(trace_text):
                    req_id = req_match.group()
                    traces.setdefault(req_id, []).append(plan_id)

    return traces


# ---------------------------------------------------------------------------
# Coverage computation
# ---------------------------------------------------------------------------

def compute_coverage(
    root: Path,
    verbose: bool = False,
) -> list[Finding]:
    """Compute plan coverage against design-intent requirements."""
    findings: list[Finding] = []

    # Resolve paths via project_config
    cfg_get = _load_project_config_get(root)

    if cfg_get:
        design_intent_var = cfg_get("DESIGN_INTENT_TO_BE")
        plans_dir_var = cfg_get("PLANS_DIR")
    else:
        design_intent_var = "project/design-intent-to-be.md"
        plans_dir_var = "_output/plans"

    # Resolve design-intent path
    spec_path = root / "_references" / design_intent_var
    if not spec_path.is_file():
        if verbose:
            findings.append(Finding(
                "", 0, "info",
                "No design-intent-to-be.md found -- skipping plan coverage check",
                "plan-coverage",
            ))
        return findings

    # Extract requirements
    requirements = extract_requirements(spec_path)

    if not requirements:
        if verbose:
            findings.append(Finding(
                str(spec_path), 0, "info",
                "No REQ markers found in design-intent-to-be.md -- skipping coverage check",
                "plan-coverage",
            ))
        return findings

    # Resolve plans directory
    plans_dir = root / plans_dir_var
    traces = extract_traces(plans_dir)

    # Compute gaps
    total = len(requirements)
    traced_ids = set(traces.keys())
    req_ids = {r.id for r in requirements}
    covered = req_ids & traced_ids
    gaps = req_ids - traced_ids

    coverage_pct = (len(covered) / total * 100) if total > 0 else 100.0

    # Summary finding
    findings.append(Finding(
        str(spec_path), 0, "info",
        f"Plan coverage: {len(covered)}/{total} requirements traced ({coverage_pct:.0f}%)",
        "plan-coverage",
    ))

    # Report gaps grouped by section
    if gaps:
        gap_reqs = [r for r in requirements if r.id in gaps]

        # Group by section
        by_section: dict[str, list[Requirement]] = {}
        for r in gap_reqs:
            by_section.setdefault(r.section, []).append(r)

        for section, reqs in sorted(by_section.items()):
            for r in reqs:
                severity = "error" if r.classification in SECURITY_CLASSIFICATIONS else "warning"
                findings.append(Finding(
                    str(spec_path), r.line, severity,
                    f"Untraced requirement: {r.id} ({r.classification}) -- {r.title}",
                    "plan-coverage",
                ))

    elif verbose:
        findings.append(Finding(
            "", 0, "info",
            "All requirements have plan coverage",
            "plan-coverage",
        ))

    return findings


# ---------------------------------------------------------------------------
# CLI and runner
# ---------------------------------------------------------------------------

def format_findings(findings: list[Finding], verbose: bool = False) -> str:
    """Format findings as a human-readable report."""
    if not findings:
        return "Plan coverage: PASS (no requirements to check)"

    # Check if there are actual issues (not just info)
    has_issues = any(f.severity in ("error", "warning") for f in findings)

    lines = []
    if has_issues:
        lines.append("Plan coverage: GAPS FOUND")
    else:
        lines.append("Plan coverage: PASS")
    lines.append("")

    error_count = sum(1 for f in findings if f.severity == "error")
    warning_count = sum(1 for f in findings if f.severity == "warning")
    info_count = sum(1 for f in findings if f.severity == "info")

    lines.append(f"Summary: {error_count} errors, {warning_count} warnings, {info_count} info")
    lines.append("")

    for f in sorted(findings, key=lambda x: SEVERITY_ORDER.get(x.severity, 2)):
        loc = f"{f.path}:{f.line}" if f.path and f.line else (f.path or "(global)")
        lines.append(f"  [{f.severity.upper()}] {loc} -- {f.message}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Plan coverage verification against design-intent requirements.",
    )
    parser.add_argument("--root", type=Path, default=None, help="Repository root")
    parser.add_argument("--verbose", action="store_true", help="Show extra detail")
    parser.add_argument("--filter", type=str, default="info",
                        choices=["error", "warning", "info"],
                        help="Minimum severity to report")
    parser.add_argument("--mode", type=str, default="blocking",
                        choices=["advisory", "blocking"],
                        help="Enforcement mode: advisory (always exit 0) or blocking (exit 1 on security gaps)")
    args = parser.parse_args()

    root = args.root or _find_repo_root()
    root = root.resolve()

    try:
        findings = compute_coverage(root, args.verbose)
    except Exception as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 2

    # Filter by severity
    min_sev_order = SEVERITY_ORDER.get(args.filter, 2)
    filtered = [f for f in findings if SEVERITY_ORDER.get(f.severity, 2) <= min_sev_order]

    report = format_findings(filtered, args.verbose)
    print(report)

    # Exit code depends on mode
    if args.mode == "advisory":
        return 0

    # Blocking mode: exit 1 only if security-classified gaps exist (errors)
    if any(f.severity == "error" for f in findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
