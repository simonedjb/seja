#!/usr/bin/env python3
"""
check_design_output.py -- Design output validation with plugin-based scanners.

Scans generated design output files for unsubstituted placeholders, phrasing
rule violations, cross-file inconsistencies, missing field values, and value
propagation mismatches. Each scanner is a plugin function that returns a list
of findings.

Exit codes: 0 = no issues, 1 = issues found, 2 = script error.

Usage
-----
    python .claude/skills/scripts/check_design_output.py [OPTIONS]

Options:
    --root DIR       Repository root (auto-detected if omitted)
    --verbose        Show passing checks and extra detail
    --plugins LIST   Comma-separated plugin names to run (default: all)
    --filter SEVER   Minimum severity to report: error, warning, info (default: info)

CHECK_PLUGIN_MANIFEST:
  name: Design Output Validation
  stack:
    backend: [any]
    frontend: [any]
  scope: design
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
# Finding data structure
# ---------------------------------------------------------------------------

class Finding(NamedTuple):
    path: str
    line: int
    severity: str  # "error", "warning", "info"
    message: str
    plugin: str


SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}

# ---------------------------------------------------------------------------
# project_config loader (avoids sys.path pollution)
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
# Plugin registry
# ---------------------------------------------------------------------------

_PLUGINS: dict[str, tuple[str, object]] = {}


def register_plugin(name: str, description: str):
    """Decorator to register a plugin function."""
    def decorator(func):
        _PLUGINS[name] = (description, func)
        return func
    return decorator


# ---------------------------------------------------------------------------
# Plugin 1: Placeholder scanner
# ---------------------------------------------------------------------------

@register_plugin("placeholder", "Detect unsubstituted {{VARIABLE}} placeholders in project files")
def plugin_placeholder(root: Path, verbose: bool) -> list[Finding]:
    findings: list[Finding] = []
    project_dir = root / "_references" / "project"

    if not project_dir.is_dir():
        if verbose:
            findings.append(Finding(
                "", 0, "info",
                "Skipped placeholder plugin: no _references/project/ directory",
                "placeholder",
            ))
        return findings

    placeholder_re = re.compile(r"\{\{[^}]+\}\}")

    for md_file in sorted(project_dir.glob("*.md")):
        # Skip conventions.md -- it legitimately uses {{...}} for template variables
        if md_file.name == "conventions.md":
            continue

        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        for line_no, line in enumerate(text.splitlines(), 1):
            for m in placeholder_re.finditer(line):
                findings.append(Finding(
                    str(md_file), line_no, "error",
                    f"Unsubstituted placeholder: {m.group()}",
                    "placeholder",
                ))

    if not findings and verbose:
        findings.append(Finding(
            "", 0, "info",
            "No unsubstituted placeholders found in project files",
            "placeholder",
        ))

    return findings


# ---------------------------------------------------------------------------
# Plugin 2: Phrasing rule scanner
# ---------------------------------------------------------------------------

@register_plugin("phrasing-rule", "Check metacommunication sections for I/you phrasing rule violations")
def plugin_phrasing_rule(root: Path, verbose: bool) -> list[Finding]:
    findings: list[Finding] = []

    # --- Scan design-intent-to-be.md (Part II, sections 11-15 only) ---
    ditb = root / "_references" / "project" / "design-intent-to-be.md"
    if ditb.is_file():
        try:
            text = ditb.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = None

        if text is not None:
            in_part_ii = False
            section_heading_re = re.compile(r"^#{1,3}\s+.*\b(1[1-5])\b")
            part_ii_re = re.compile(r"^#{1,3}\s+.*\b(Part\s+II|Metacommunication)\b", re.IGNORECASE)

            for line_no, line in enumerate(text.splitlines(), 1):
                # Detect Part II or sections 11-15
                if part_ii_re.search(line) or section_heading_re.search(line):
                    in_part_ii = True

                if not in_part_ii:
                    continue

                _check_phrasing_line(findings, line, line_no, str(ditb))
    elif verbose:
        findings.append(Finding(
            "", 0, "info",
            "Skipped phrasing-rule for design-intent-to-be.md: file not found",
            "phrasing-rule",
        ))

    # --- Scan metacomm-as-is.md (entire file) ---
    metacomm = root / "_references" / "project" / "metacomm-as-is.md"
    if metacomm.is_file():
        try:
            text = metacomm.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = None

        if text is not None:
            for line_no, line in enumerate(text.splitlines(), 1):
                _check_phrasing_line(findings, line, line_no, str(metacomm))
    elif verbose:
        findings.append(Finding(
            "", 0, "info",
            "Skipped phrasing-rule for metacomm-as-is.md: file not found",
            "phrasing-rule",
        ))

    if not findings and verbose:
        findings.append(Finding(
            "", 0, "info",
            "No phrasing rule violations found",
            "phrasing-rule",
        ))

    return findings


# Module-level compiled regexes for phrasing rule checks
_THIRD_PERSON_RE = re.compile(
    r"\b(the\s+designer|the\s+system|the\s+user)\b",
    re.IGNORECASE,
)
_PASSIVE_RE = re.compile(
    r"\b(is\s+provided|was\s+designed|are\s+offered|will\s+be\s+shown"
    r"|is\s+displayed|is\s+designed|was\s+provided|are\s+displayed"
    r"|is\s+offered|was\s+shown|is\s+shown|was\s+offered"
    r"|are\s+provided|are\s+designed|will\s+be\s+provided"
    r"|will\s+be\s+offered|will\s+be\s+designed|will\s+be\s+displayed)\b",
    re.IGNORECASE,
)
_IMPERATIVE_RE = re.compile(
    r"^(?:[-*]\s+)?(?:#{1,6}\s+)?"
    r"(Enforce|Provide|Ensure|Display|Show|Present|Offer|Include|Apply|Use|Set|Make)\b"
)


def _check_phrasing_line(findings: list[Finding], line: str, line_no: int, file_path: str) -> None:
    """Check a single line for phrasing rule violations."""
    stripped = line.strip()
    if not stripped or stripped.startswith("```"):
        return

    for m in _THIRD_PERSON_RE.finditer(line):
        findings.append(Finding(
            file_path, line_no, "warning",
            f"Third-person reference: '{m.group()}' -- use I/you phrasing instead",
            "phrasing-rule",
        ))

    for m in _PASSIVE_RE.finditer(line):
        findings.append(Finding(
            file_path, line_no, "warning",
            f"Passive voice: '{m.group()}' -- use active I/you phrasing",
            "phrasing-rule",
        ))

    m = _IMPERATIVE_RE.match(stripped)
    if m:
        findings.append(Finding(
            file_path, line_no, "warning",
            f"Imperative mood: line starts with '{m.group(1)}' -- use I/you phrasing",
            "phrasing-rule",
        ))


# ---------------------------------------------------------------------------
# Plugin 3: Cross-file consistency scanner
# ---------------------------------------------------------------------------

@register_plugin("cross-file-consistency", "Check PROJECT_NAME and locale consistency across project files")
def plugin_cross_file_consistency(root: Path, verbose: bool) -> list[Finding]:
    findings: list[Finding] = []
    project_dir = root / "_references" / "project"

    if not project_dir.is_dir():
        if verbose:
            findings.append(Finding(
                "", 0, "info",
                "Skipped cross-file-consistency plugin: no _references/project/ directory",
                "cross-file-consistency",
            ))
        return findings

    # Get PROJECT_NAME from project_config
    cfg_get = _load_project_config_get(root)
    if cfg_get is None:
        project_name = None
    else:
        project_name = cfg_get("PROJECT_NAME")

    if not project_name or "{{" in project_name:
        if verbose:
            findings.append(Finding(
                "", 0, "info",
                "Skipped cross-file-consistency: PROJECT_NAME is unset or a template placeholder",
                "cross-file-consistency",
            ))
        return findings

    # Get locale from conventions
    locale = cfg_get("LOCALE") if cfg_get else None

    # Check all project .md files for consistent PROJECT_NAME and locale references
    project_name_re = re.compile(r"\bPROJECT_NAME\b")

    for md_file in sorted(project_dir.glob("*.md")):
        if md_file.name == "conventions.md":
            continue

        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        # Check for literal "PROJECT_NAME" (unsubstituted variable name) in content
        for line_no, line in enumerate(text.splitlines(), 1):
            # Skip code blocks and table header rows
            if line.strip().startswith("```") or line.strip().startswith("|"):
                continue
            if project_name_re.search(line):
                findings.append(Finding(
                    str(md_file), line_no, "error",
                    f"Unsubstituted PROJECT_NAME reference (expected '{project_name}')",
                    "cross-file-consistency",
                ))

    # Check locale consistency if available
    if locale and locale != "{{LOCALE}}":
        locale_re = re.compile(r"\blocale[:\s]+[\"']?([a-z]{2}(?:-[A-Z]{2})?)[\"']?", re.IGNORECASE)
        for md_file in sorted(project_dir.glob("*.md")):
            if md_file.name == "conventions.md":
                continue
            try:
                text = md_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            for line_no, line in enumerate(text.splitlines(), 1):
                for m in locale_re.finditer(line):
                    found_locale = m.group(1)
                    if found_locale.lower() != locale.lower():
                        findings.append(Finding(
                            str(md_file), line_no, "error",
                            f"Locale mismatch: found '{found_locale}', expected '{locale}'",
                            "cross-file-consistency",
                        ))

    if not findings and verbose:
        findings.append(Finding(
            "", 0, "info",
            "Cross-file consistency checks passed",
            "cross-file-consistency",
        ))

    return findings


# ---------------------------------------------------------------------------
# Plugin 4: Field presence scanner
# ---------------------------------------------------------------------------

@register_plugin("field-presence", "Check conventions.md for remaining template placeholder values")
def plugin_field_presence(root: Path, verbose: bool) -> list[Finding]:
    findings: list[Finding] = []
    conventions = root / "_references" / "project" / "conventions.md"

    if not conventions.is_file():
        if verbose:
            findings.append(Finding(
                "", 0, "info",
                "Skipped field-presence plugin: no project/conventions.md",
                "field-presence",
            ))
        return findings

    try:
        text = conventions.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings

    # Critical fields that should be filled in
    critical_fields = [
        "PROJECT_NAME",
        "PROJECT_DESCRIPTION",
        "BACKEND_DIR",
        "FRONTEND_DIR",
        "BACKEND_FRAMEWORK",
        "FRONTEND_FRAMEWORK",
    ]

    # Parse table rows: | `KEY` | `VALUE` |
    row_re = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|", re.MULTILINE)
    placeholder_re = re.compile(r"\{\{[^}]+\}\}")

    field_values: dict[str, tuple[str, int]] = {}
    for line_no, line in enumerate(text.splitlines(), 1):
        m = row_re.match(line)
        if m:
            field_values[m.group(1)] = (m.group(2), line_no)

    for field in critical_fields:
        if field in field_values:
            value, line_no = field_values[field]
            if placeholder_re.search(value):
                findings.append(Finding(
                    str(conventions), line_no, "warning",
                    f"Critical field '{field}' still contains template placeholder: {value}",
                    "field-presence",
                ))

    if not findings and verbose:
        findings.append(Finding(
            "", 0, "info",
            "All critical convention fields are populated (or conventions.md absent)",
            "field-presence",
        ))

    return findings


# ---------------------------------------------------------------------------
# Plugin 5: Value propagation scanner
# ---------------------------------------------------------------------------

@register_plugin("value-propagation", "Cross-check conventions.md values against standards files")
def plugin_value_propagation(root: Path, verbose: bool) -> list[Finding]:
    findings: list[Finding] = []
    conventions = root / "_references" / "project" / "conventions.md"

    if not conventions.is_file():
        if verbose:
            findings.append(Finding(
                "", 0, "info",
                "Skipped value-propagation plugin: no project/conventions.md",
                "value-propagation",
            ))
        return findings

    # Get framework values from project_config
    cfg_get = _load_project_config_get(root)
    if cfg_get is None:
        backend_fw = None
        frontend_fw = None
    else:
        backend_fw = cfg_get("BACKEND_FRAMEWORK")
        frontend_fw = cfg_get("FRONTEND_FRAMEWORK")

    # Check backend framework propagation
    if backend_fw and "{{" not in backend_fw:
        backend_standards = root / "_references" / "project" / "backend-standards.md"
        if backend_standards.is_file():
            try:
                text = backend_standards.read_text(encoding="utf-8", errors="replace")
                if backend_fw.lower() not in text.lower():
                    findings.append(Finding(
                        str(backend_standards), 0, "warning",
                        f"Backend framework '{backend_fw}' from conventions.md not mentioned in backend-standards.md",
                        "value-propagation",
                    ))
            except OSError:
                pass
        elif verbose:
            findings.append(Finding(
                "", 0, "info",
                "Skipped backend framework propagation check: backend-standards.md not found",
                "value-propagation",
            ))

    # Check frontend framework propagation
    if frontend_fw and "{{" not in frontend_fw:
        frontend_standards = root / "_references" / "project" / "frontend-standards.md"
        if frontend_standards.is_file():
            try:
                text = frontend_standards.read_text(encoding="utf-8", errors="replace")
                if frontend_fw.lower() not in text.lower():
                    findings.append(Finding(
                        str(frontend_standards), 0, "warning",
                        f"Frontend framework '{frontend_fw}' from conventions.md not mentioned in frontend-standards.md",
                        "value-propagation",
                    ))
            except OSError:
                pass
        elif verbose:
            findings.append(Finding(
                "", 0, "info",
                "Skipped frontend framework propagation check: frontend-standards.md not found",
                "value-propagation",
            ))

    if not findings and verbose:
        findings.append(Finding(
            "", 0, "info",
            "Value propagation checks passed (or no applicable values to check)",
            "value-propagation",
        ))

    return findings


# ---------------------------------------------------------------------------
# CLI and runner
# ---------------------------------------------------------------------------

def run_plugins(
    root: Path,
    verbose: bool = False,
    plugin_names: list[str] | None = None,
    min_severity: str = "info",
) -> list[Finding]:
    """Run selected plugins and return all findings."""
    all_findings: list[Finding] = []
    min_sev_order = SEVERITY_ORDER.get(min_severity, 2)

    plugins_to_run = plugin_names if plugin_names else list(_PLUGINS.keys())

    for name in plugins_to_run:
        if name not in _PLUGINS:
            print(f"WARNING: Unknown plugin '{name}', skipping.", file=sys.stderr)
            continue
        desc, func = _PLUGINS[name]
        if verbose:
            print(f"Running plugin: {name} ({desc})", file=sys.stderr)
        try:
            plugin_findings = func(root, verbose)
            all_findings.extend(plugin_findings)
        except Exception as e:
            all_findings.append(Finding("", 0, "error", f"Plugin '{name}' crashed: {e}", name))

    # Filter by severity
    filtered = [f for f in all_findings if SEVERITY_ORDER.get(f.severity, 2) <= min_sev_order]
    return filtered


def format_findings(findings: list[Finding], verbose: bool = False) -> str:
    """Format findings as a human-readable report."""
    if not findings:
        return "Design output validation: PASS (no issues found)"

    lines = ["Design output validation: ISSUES FOUND", ""]

    # Group by plugin
    by_plugin: dict[str, list[Finding]] = {}
    for f in findings:
        by_plugin.setdefault(f.plugin, []).append(f)

    error_count = sum(1 for f in findings if f.severity == "error")
    warning_count = sum(1 for f in findings if f.severity == "warning")
    info_count = sum(1 for f in findings if f.severity == "info")

    lines.append(f"Summary: {error_count} errors, {warning_count} warnings, {info_count} info")
    lines.append("")

    for plugin_name, plugin_findings in sorted(by_plugin.items()):
        lines.append(f"## {plugin_name}")
        for f in sorted(plugin_findings, key=lambda x: SEVERITY_ORDER.get(x.severity, 2)):
            loc = f"{f.path}:{f.line}" if f.path and f.line else (f.path or "(global)")
            lines.append(f"  [{f.severity.upper()}] {loc} -- {f.message}")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Design output validation with plugin-based scanners.",
    )
    parser.add_argument("--root", type=Path, default=None, help="Repository root")
    parser.add_argument("--verbose", action="store_true", help="Show extra detail")
    parser.add_argument("--plugins", type=str, default=None, help="Comma-separated plugin names")
    parser.add_argument("--filter", type=str, default="info", choices=["error", "warning", "info"],
                        help="Minimum severity to report")
    args = parser.parse_args()

    root = args.root or _find_repo_root()
    root = root.resolve()

    plugin_names = [p.strip() for p in args.plugins.split(",")] if args.plugins else None

    try:
        findings = run_plugins(root, args.verbose, plugin_names, args.filter)
    except Exception as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 2

    report = format_findings(findings, args.verbose)
    print(report)

    if any(f.severity == "error" for f in findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
