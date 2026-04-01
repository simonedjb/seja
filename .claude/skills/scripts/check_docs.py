#!/usr/bin/env python3
"""
check_docs.py -- Documentation consistency checker with plugin-based scanners.

Scans documentation files for staleness, broken references, terminology drift,
and other documentation quality issues. Each scanner is a plugin function that
returns a list of findings.

Exit codes: 0 = no issues, 1 = issues found, 2 = script error.

Usage
-----
    python .claude/skills/scripts/check_docs.py [OPTIONS]

Options:
    --root DIR       Repository root (auto-detected if omitted)
    --verbose        Show passing checks and extra detail
    --plugins LIST   Comma-separated plugin names to run (default: all)
    --filter SEVER   Minimum severity to report: error, warning, info (default: info)

CHECK_PLUGIN_MANIFEST:
  name: Documentation Consistency
  stack:
    backend: [any]
    frontend: [any]
  scope: docs
  critical: false
"""
from __future__ import annotations

import argparse
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
# Plugin 1: Framework integrity
# ---------------------------------------------------------------------------

@register_plugin("framework-integrity", "Validate CLAUDE.md references against filesystem")
def plugin_framework_integrity(root: Path, verbose: bool) -> list[Finding]:
    findings: list[Finding] = []
    claude_md = root / "CLAUDE.md"
    if not claude_md.is_file():
        findings.append(Finding(str(claude_md), 0, "error", "CLAUDE.md not found", "framework-integrity"))
        return findings

    text = claude_md.read_text(encoding="utf-8", errors="replace")

    skills_dir = root / ".claude" / "skills"
    agents_dir = root / ".claude" / "agents"

    # Check skill references: look for /skill-name patterns in CLAUDE.md
    skill_ref_re = re.compile(r"`/(\w[\w-]*)`")
    skill_dirs = {d.name for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").is_file()} if skills_dir.is_dir() else set()
    internal_skills = {"pre-skill", "post-skill"}
    user_skills = skill_dirs - internal_skills

    for line_no, line in enumerate(text.splitlines(), 1):
        for m in skill_ref_re.finditer(line):
            ref_name = m.group(1)
            # Only flag if it looks like a skill name (not a CLI flag)
            if ref_name in skill_dirs:
                continue  # exists, good
            # Check if it could be a skill reference (heuristic: appears in a workflow context)
            if ref_name.replace("-", "") .isalpha() and len(ref_name) > 2:
                if ref_name not in skill_dirs and (skills_dir / ref_name).is_dir():
                    pass  # directory exists but no SKILL.md -- caught below
                elif ref_name not in skill_dirs:
                    # Could be a valid skill reference that's missing
                    pass  # Don't flag -- could be a command, not a skill

    # Check that user-invocable skills have Quick Guide
    for skill_name in sorted(user_skills):
        skill_md = skills_dir / skill_name / "SKILL.md"
        if skill_md.is_file():
            skill_text = skill_md.read_text(encoding="utf-8", errors="replace")
            if "## Quick Guide" not in skill_text:
                findings.append(Finding(
                    str(skill_md), 0, "warning",
                    f"User-invocable skill '{skill_name}' is missing ## Quick Guide section",
                    "framework-integrity",
                ))

    # Check agent references in CLAUDE.md
    agent_ref_re = re.compile(r"`([\w-]+)`\s+agent|launch\s+the\s+`([\w-]+)`")
    agent_files = {p.stem for p in agents_dir.glob("*.md")} if agents_dir.is_dir() else set()

    for line_no, line in enumerate(text.splitlines(), 1):
        for m in agent_ref_re.finditer(line):
            agent_name = m.group(1) or m.group(2)
            if agent_name and agent_name not in agent_files:
                findings.append(Finding(
                    str(claude_md), line_no, "warning",
                    f"Agent reference '{agent_name}' not found in .claude/agents/",
                    "framework-integrity",
                ))

    # Check for retired skills (directories without SKILL.md)
    if skills_dir.is_dir():
        for d in sorted(skills_dir.iterdir()):
            if d.is_dir() and d.name != "scripts" and d.name != "__pycache__":
                if not (d / "SKILL.md").is_file():
                    findings.append(Finding(
                        str(d), 0, "warning",
                        f"Skill directory '{d.name}' has no SKILL.md (retired without redirect?)",
                        "framework-integrity",
                    ))

    return findings


# ---------------------------------------------------------------------------
# Plugin 2: Path liveness
# ---------------------------------------------------------------------------

@register_plugin("path-liveness", "Verify relative paths in .md files resolve to existing files")
def plugin_path_liveness(root: Path, verbose: bool) -> list[Finding]:
    findings: list[Finding] = []

    # Patterns to exclude
    url_re = re.compile(r"https?://|mailto:")
    placeholder_re = re.compile(r"\{\{.*?\}\}|\$\{.*?\}")
    anchor_re = re.compile(r"^#")

    # Markdown link/image patterns
    md_link_re = re.compile(r"!?\[(?:[^\]]*)\]\(([^)]+)\)")

    # Scan .md files in key directories
    scan_dirs = [
        root / ".claude",
        root / "_references",
    ]
    # Also scan root-level .md files
    scan_files = list(root.glob("*.md"))

    for scan_dir in scan_dirs:
        if scan_dir.is_dir():
            scan_files.extend(scan_dir.rglob("*.md"))

    seen = set()
    for md_file in scan_files:
        md_file = md_file.resolve()
        if md_file in seen:
            continue
        seen.add(md_file)

        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        for line_no, line in enumerate(text.splitlines(), 1):
            for m in md_link_re.finditer(line):
                ref_path = m.group(1).strip()

                # Strip anchor fragment
                if "#" in ref_path:
                    ref_path = ref_path.split("#")[0]
                if not ref_path:
                    continue

                # Skip URLs, anchors, placeholders
                if url_re.search(ref_path):
                    continue
                if placeholder_re.search(ref_path):
                    continue
                if anchor_re.match(ref_path):
                    continue

                # Resolve relative to the .md file's directory
                target = (md_file.parent / ref_path).resolve()
                if not target.exists():
                    findings.append(Finding(
                        str(md_file), line_no, "warning",
                        f"Broken link: '{m.group(1).strip()}' does not exist",
                        "path-liveness",
                    ))

    return findings


# ---------------------------------------------------------------------------
# Plugin 3: Environment variable documentation
# ---------------------------------------------------------------------------

@register_plugin("env-vars", "Cross-check documented vs referenced environment variables")
def plugin_env_vars(root: Path, verbose: bool) -> list[Finding]:
    findings: list[Finding] = []

    # Detect stack -- skip for framework-only repos
    try:
        sys.path.insert(0, str(root / ".claude" / "skills" / "scripts"))
        from project_config import get
        backend = get("BACKEND_FRAMEWORK")
        frontend = get("FRONTEND_FRAMEWORK")
    except Exception:
        backend = None
        frontend = None

    valid_stacks = {"django", "flask", "node", "next", "express", "fastapi"}
    if not backend or backend.lower() not in valid_stacks:
        if not frontend or frontend.lower() not in valid_stacks:
            # Framework-only repo, skip this plugin
            if verbose:
                findings.append(Finding(
                    "", 0, "info",
                    "Skipped env-vars plugin: no application stack detected",
                    "env-vars",
                ))
            return findings

    # Collect documented env vars from .md files
    env_doc_re = re.compile(r"`([A-Z][A-Z0-9_]{2,})`")
    documented_vars: set[str] = set()
    md_files = list((root / "_references").rglob("*.md")) if (root / "_references").is_dir() else []
    md_files.extend(root.glob("*.md"))
    for md_file in md_files:
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
            for m in env_doc_re.finditer(text):
                documented_vars.add(m.group(1))
        except OSError:
            continue

    # Collect referenced env vars from code
    code_env_re = re.compile(
        r"""(?:os\.environ\.get|os\.getenv|process\.env\.|getenv)\s*\(?\s*['"]([ A-Z][A-Z0-9_]{2,})['"]"""
    )
    referenced_vars: set[str] = set()
    code_extensions = {".py", ".js", ".ts", ".tsx", ".jsx"}
    for ext in code_extensions:
        for code_file in root.rglob(f"*{ext}"):
            # Skip node_modules, .venv, etc.
            parts = code_file.parts
            if any(p in {"node_modules", ".venv", "venv", "__pycache__", ".git"} for p in parts):
                continue
            try:
                text = code_file.read_text(encoding="utf-8", errors="replace")
                for m in code_env_re.finditer(text):
                    referenced_vars.add(m.group(1))
            except OSError:
                continue

    # Also check .env.example / .env.template
    for env_file_name in [".env.example", ".env.template", ".env.sample"]:
        env_file = root / env_file_name
        if env_file.is_file():
            try:
                text = env_file.read_text(encoding="utf-8", errors="replace")
                for line in text.splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        var_name = line.split("=", 1)[0].strip()
                        if var_name:
                            documented_vars.add(var_name)
            except OSError:
                continue

    # Common framework vars to ignore
    ignore_vars = {
        "PATH", "HOME", "USER", "SHELL", "TERM", "LANG", "PWD",
        "PYTHONPATH", "NODE_ENV", "NODE_PATH", "CI", "DEBUG",
        "REPO_ROOT", "BACKEND_DIR", "FRONTEND_DIR",
    }

    undocumented = referenced_vars - documented_vars - ignore_vars
    unreferenced = documented_vars - referenced_vars - ignore_vars

    for var in sorted(undocumented):
        findings.append(Finding(
            "", 0, "warning",
            f"Environment variable '{var}' is used in code but not documented",
            "env-vars",
        ))

    if verbose:
        for var in sorted(unreferenced):
            findings.append(Finding(
                "", 0, "info",
                f"Environment variable '{var}' is documented but not referenced in code",
                "env-vars",
            ))

    return findings


# ---------------------------------------------------------------------------
# Plugin 4: Command references
# ---------------------------------------------------------------------------

@register_plugin("command-refs", "Cross-check documented CLI commands against build targets")
def plugin_command_refs(root: Path, verbose: bool) -> list[Finding]:
    findings: list[Finding] = []

    # Detect stack -- skip for framework-only repos
    try:
        sys.path.insert(0, str(root / ".claude" / "skills" / "scripts"))
        from project_config import get
        backend = get("BACKEND_FRAMEWORK")
        frontend = get("FRONTEND_FRAMEWORK")
    except Exception:
        backend = None
        frontend = None

    valid_stacks = {"django", "flask", "node", "next", "express", "fastapi"}
    if not backend or backend.lower() not in valid_stacks:
        if not frontend or frontend.lower() not in valid_stacks:
            if verbose:
                findings.append(Finding(
                    "", 0, "info",
                    "Skipped command-refs plugin: no application stack detected",
                    "command-refs",
                ))
            return findings

    # Collect available targets from package.json scripts
    available_commands: dict[str, str] = {}  # command -> source file

    package_json = root / "package.json"
    if package_json.is_file():
        import json
        try:
            pkg = json.loads(package_json.read_text(encoding="utf-8", errors="replace"))
            for script_name in pkg.get("scripts", {}):
                available_commands[f"npm run {script_name}"] = str(package_json)
                available_commands[script_name] = str(package_json)
        except (json.JSONDecodeError, OSError):
            pass

    # Collect from Makefile
    makefile = root / "Makefile"
    if makefile.is_file():
        try:
            text = makefile.read_text(encoding="utf-8", errors="replace")
            make_target_re = re.compile(r"^([a-zA-Z_][\w-]*)\s*:", re.MULTILINE)
            for m in make_target_re.finditer(text):
                available_commands[f"make {m.group(1)}"] = str(makefile)
                available_commands[m.group(1)] = str(makefile)
        except OSError:
            pass

    # Collect from pyproject.toml [project.scripts] / [tool.poetry.scripts]
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        try:
            text = pyproject.read_text(encoding="utf-8", errors="replace")
            # Simple TOML parsing for scripts sections
            in_scripts = False
            for line in text.splitlines():
                if re.match(r"\[(project\.scripts|tool\.poetry\.scripts)\]", line.strip()):
                    in_scripts = True
                    continue
                if in_scripts:
                    if line.strip().startswith("["):
                        in_scripts = False
                        continue
                    m = re.match(r'(\w[\w-]*)\s*=', line.strip())
                    if m:
                        available_commands[m.group(1)] = str(pyproject)
        except OSError:
            pass

    if not available_commands:
        if verbose:
            findings.append(Finding(
                "", 0, "info",
                "No build targets found (no package.json scripts, Makefile, or pyproject.toml)",
                "command-refs",
            ))
        return findings

    # Scan documented commands in .md files (fenced code blocks)
    fenced_re = re.compile(r"^```(?:bash|sh|shell|console)?\s*$", re.IGNORECASE)
    fenced_end_re = re.compile(r"^```\s*$")
    cmd_prefixes = ("npm run ", "yarn ", "pnpm ", "make ", "python ", "flask ", "django-admin ")

    md_files = list((root / "_references").rglob("*.md")) if (root / "_references").is_dir() else []
    md_files.extend(root.glob("*.md"))
    md_files.extend((root / ".claude").rglob("*.md") if (root / ".claude").is_dir() else [])

    documented_commands: list[tuple[str, str, int]] = []  # (command, file, line)
    for md_file in md_files:
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        in_fence = False
        for line_no, line in enumerate(text.splitlines(), 1):
            if not in_fence and fenced_re.match(line.strip()):
                in_fence = True
                continue
            if in_fence and fenced_end_re.match(line.strip()):
                in_fence = False
                continue
            if in_fence:
                cmd = line.strip()
                if cmd.startswith("$"):
                    cmd = cmd[1:].strip()
                if any(cmd.startswith(p) for p in cmd_prefixes):
                    documented_commands.append((cmd, str(md_file), line_no))

    # Check documented commands that reference npm/make targets
    for cmd, file_path, line_no in documented_commands:
        # Extract the target name
        for prefix in ("npm run ", "make "):
            if cmd.startswith(prefix):
                target = cmd[len(prefix):].split()[0] if cmd[len(prefix):] else ""
                full_cmd = f"{prefix}{target}"
                if target and full_cmd not in available_commands and target not in available_commands:
                    findings.append(Finding(
                        file_path, line_no, "warning",
                        f"Documented command '{full_cmd}' not found in build targets",
                        "command-refs",
                    ))

    return findings


# ---------------------------------------------------------------------------
# Plugin 5: Terminology consistency
# ---------------------------------------------------------------------------

@register_plugin("terminology", "Check for variant spellings against shared-definitions.md")
def plugin_terminology(root: Path, verbose: bool) -> list[Finding]:
    findings: list[Finding] = []

    shared_defs = root / "_references" / "general" / "shared-definitions.md"
    if not shared_defs.is_file():
        if verbose:
            findings.append(Finding(
                "", 0, "info",
                "Skipped terminology plugin: no shared-definitions.md found",
                "terminology",
            ))
        return findings

    try:
        defs_text = shared_defs.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings

    # Extract defined terms from **Term** patterns in tables
    term_re = re.compile(r"\*\*([^*]+)\*\*")
    defined_terms: list[str] = []
    for m in term_re.finditer(defs_text):
        term = m.group(1).strip()
        if len(term) > 2 and not term.startswith("("):
            defined_terms.append(term)

    if not defined_terms:
        return findings

    # Build variant patterns for common spelling issues
    # For multi-word terms, check for missing hyphens, wrong case, etc.
    variant_checks: list[tuple[str, re.Pattern, str]] = []
    for term in defined_terms:
        lower = term.lower()
        # Check for hyphenated vs space vs concatenated variants
        if " " in lower:
            parts = lower.split()
            if len(parts) == 2:
                # "soft delete" -> check for "soft-delete", "softdelete"
                hyphenated = f"{parts[0]}-{parts[1]}"
                concatenated = f"{parts[0]}{parts[1]}"
                pattern = re.compile(
                    rf"\b({re.escape(hyphenated)}|{re.escape(concatenated)})\b",
                    re.IGNORECASE,
                )
                variant_checks.append((term, pattern, f"Use '{term}' (two words) instead of variant"))
        elif "-" in lower:
            parts = lower.split("-")
            if len(parts) == 2:
                # "co-location" -> check for "colocation", "co location"
                spaced = f"{parts[0]} {parts[1]}"
                concatenated = f"{parts[0]}{parts[1]}"
                pattern = re.compile(
                    rf"\b({re.escape(spaced)}|{re.escape(concatenated)})\b",
                    re.IGNORECASE,
                )
                variant_checks.append((term, pattern, f"Use '{term}' (hyphenated) instead of variant"))

    if not variant_checks:
        return findings

    # Scan .md files
    scan_dirs = [root / ".claude", root / "_references"]
    scan_files = list(root.glob("*.md"))
    for d in scan_dirs:
        if d.is_dir():
            scan_files.extend(d.rglob("*.md"))

    seen = set()
    for md_file in scan_files:
        md_file = md_file.resolve()
        if md_file in seen or md_file == shared_defs.resolve():
            continue
        seen.add(md_file)

        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        for line_no, line in enumerate(text.splitlines(), 1):
            for term, pattern, msg in variant_checks:
                if pattern.search(line):
                    findings.append(Finding(
                        str(md_file), line_no, "info",
                        f"{msg}: found '{pattern.search(line).group()}'",
                        "terminology",
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
        return "Documentation consistency check: PASS (no issues found)"

    lines = ["Documentation consistency check: ISSUES FOUND", ""]

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
        description="Documentation consistency checker with plugin-based scanners.",
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
    if any(f.severity == "warning" for f in findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
