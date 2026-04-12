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
    --plugins LIST   Comma-separated plugin names to run (default: all).
                     Known plugins: framework-integrity, path-liveness,
                     env-vars, command-refs, terminology,
                     structural-completeness, framework-reference-coverage,
                     lifecycle-fact-uniqueness.
    --filter SEVER   Minimum severity to report: error, warning, info (default: info)

Framework reference coverage plugin
-----------------------------------
``framework-reference-coverage`` validates ``seja-public/docs/reference/
framework-reference.md`` against four drift classes: coverage (every framework
file walked by the generator must have exactly one row), nonexistent targets
(each row's Path must exist), cross-reference liveness (each Mentioned-in
entry must resolve under ``seja-public/docs/``), and regeneration drift
(compares against a fresh in-memory render from ``generate_framework_reference.py``).
Run it alone with:

    python .claude/skills/scripts/check_docs.py --plugins framework-reference-coverage

Lifecycle fact uniqueness plugin
--------------------------------
``lifecycle-fact-uniqueness`` scans paragraphs containing ``**Framework:**``
callouts in ``seja-public/docs/how-to/*.md`` plus paragraphs under
``concepts.md`` section ``## Framework lifecycle`` and flags pairs whose
normalized-token Jaccard overlap is at least 60 percent (with an 8-token
minimum to suppress short-boilerplate noise). Run it alone with:

    python .claude/skills/scripts/check_docs.py --plugins lifecycle-fact-uniqueness

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
    placeholder_re = re.compile(r"\{\{.*?\}\}|\$\{.*?\}|<[a-z][a-z0-9_-]*>")
    anchor_re = re.compile(r"^#")
    fenced_re = re.compile(r"^```")

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

        in_fence = False
        for line_no, line in enumerate(text.splitlines(), 1):
            if fenced_re.match(line.strip()):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
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

        _inline_code_re = re.compile(r"`[^`]*`")
        _fenced_re = re.compile(r"^```")
        in_fence = False
        for line_no, line in enumerate(text.splitlines(), 1):
            if _fenced_re.match(line.strip()):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            # Strip inline code spans before checking terminology
            clean_line = _inline_code_re.sub("``", line)
            for term, pattern, msg in variant_checks:
                if pattern.search(clean_line):
                    findings.append(Finding(
                        str(md_file), line_no, "info",
                        f"{msg}: found '{pattern.search(clean_line).group()}'",
                        "terminology",
                    ))

    return findings


# ---------------------------------------------------------------------------
# Plugin 6: Structural completeness
# ---------------------------------------------------------------------------

@register_plugin("structural-completeness", "Check project docs contain required headings from templates")
def plugin_structural_completeness(root: Path, verbose: bool) -> list[Finding]:
    findings: list[Finding] = []

    template_docs_dir = root / "_references" / "template" / "docs"
    project_docs_dir = root / "_references" / "project" / "docs"

    if not project_docs_dir.is_dir():
        findings.append(Finding(
            "", 0, "info",
            "No project documentation directory found (expected in framework-only repos)",
            "structural-completeness",
        ))
        return findings

    if not template_docs_dir.is_dir():
        findings.append(Finding(
            str(template_docs_dir), 0, "info",
            "No template documentation directory found, skipping structural check",
            "structural-completeness",
        ))
        return findings

    heading_re = re.compile(r"^(#{2,3})\s+(.+)$")
    placeholder_re_h = re.compile(r"\{\{")

    # Build required headings per template
    for template_file in sorted(template_docs_dir.glob("*.md")):
        required_headings: list[str] = []
        try:
            text = template_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        for line in text.splitlines():
            m = heading_re.match(line)
            if m:
                heading_text = m.group(2).strip()
                if not placeholder_re_h.search(heading_text):
                    required_headings.append(heading_text)

        if not required_headings:
            continue

        # Map template -> project doc
        project_file = project_docs_dir / template_file.name
        if not project_file.is_file():
            if verbose:
                findings.append(Finding(
                    str(project_file), 0, "info",
                    f"Project doc '{template_file.name}' not found (no matching template instance)",
                    "structural-completeness",
                ))
            continue

        # Extract headings from project doc
        try:
            project_text = project_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        project_headings: set[str] = set()
        for line in project_text.splitlines():
            m = heading_re.match(line)
            if m:
                project_headings.add(m.group(2).strip())

        # Report missing headings
        for heading in required_headings:
            if heading not in project_headings:
                findings.append(Finding(
                    str(project_file), 0, "warning",
                    f"Missing required heading '{heading}' (defined in template/{template_file.name})",
                    "structural-completeness",
                ))

    return findings


# ---------------------------------------------------------------------------
# Plugin 7: Framework reference coverage
# ---------------------------------------------------------------------------


def _build_framework_file_set(root: Path) -> set[str]:
    """Return repo-relative POSIX paths for every framework source file.

    Mirrors the roots that ``generate_framework_reference.py`` walks. Used by
    the coverage sub-check of ``framework-reference-coverage`` to determine
    which files should be represented in the generated reference table.
    """
    files: set[str] = set()

    # Skills: one SKILL.md per skill directory.
    skills_dir = root / ".claude" / "skills"
    if skills_dir.is_dir():
        for skill_md in skills_dir.glob("*/SKILL.md"):
            files.add(skill_md.relative_to(root).as_posix())

    # Agents.
    agents_dir = root / ".claude" / "agents"
    if agents_dir.is_dir():
        for agent_md in agents_dir.glob("*.md"):
            files.add(agent_md.relative_to(root).as_posix())

    # Rules.
    rules_dir = root / ".claude" / "rules"
    if rules_dir.is_dir():
        for rule_md in rules_dir.glob("*.md"):
            files.add(rule_md.relative_to(root).as_posix())

    # Scripts (top-level .py files under .claude/skills/scripts, non-private).
    scripts_dir = root / ".claude" / "skills" / "scripts"
    if scripts_dir.is_dir():
        for script in scripts_dir.glob("*.py"):
            if script.name.startswith("_"):
                continue
            files.add(script.relative_to(root).as_posix())

    # Migrations.
    migrations_dir = root / ".claude" / "migrations"
    if migrations_dir.is_dir():
        for mig in migrations_dir.glob("*.md"):
            files.add(mig.relative_to(root).as_posix())

    # General references (non-recursive to avoid double-counting
    # perspectives/onboarding/communication which are discovered separately).
    general_dir = root / "_references" / "general"
    if general_dir.is_dir():
        for ref in general_dir.glob("*.md"):
            files.add(ref.relative_to(root).as_posix())

    # Perspectives.
    perspectives_dir = general_dir / "review-perspectives"
    if perspectives_dir.is_dir():
        for p in perspectives_dir.glob("*.md"):
            files.add(p.relative_to(root).as_posix())

    # Onboarding.
    onboarding_dir = general_dir / "onboarding"
    if onboarding_dir.is_dir():
        for o in onboarding_dir.glob("*.md"):
            files.add(o.relative_to(root).as_posix())

    # Communication.
    communication_dir = general_dir / "communication"
    if communication_dir.is_dir():
        for c in communication_dir.glob("*.md"):
            files.add(c.relative_to(root).as_posix())

    # Templates (recursive).
    template_dir = root / "_references" / "template"
    if template_dir.is_dir():
        for t in template_dir.rglob("*.md"):
            files.add(t.relative_to(root).as_posix())

    return files


_REF_TABLE_PATH_CELL_RE = re.compile(r"`([^`]+)`")
_REF_H2_RE = re.compile(r"^##\s+(.+?)\s*$")


def _parse_framework_reference_rows(text: str) -> list[dict]:
    """Parse ``framework-reference.md`` into row dicts.

    Returns a list of ``{"kind", "name", "path", "mentioned_in"}`` dicts.
    Only the primary categorized table (H2 sections with four-column rows) is
    parsed; the user-facing surface table is intentionally skipped to avoid
    double-counting rows during the coverage sub-check.
    """
    rows: list[dict] = []
    current_kind: str | None = None
    in_primary_section = True
    saw_header_separator = False

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        h2_match = _REF_H2_RE.match(line)
        if h2_match:
            heading = h2_match.group(1).strip()
            if heading.lower().startswith("user-facing surface"):
                in_primary_section = False
                current_kind = None
                continue
            in_primary_section = True
            current_kind = heading
            saw_header_separator = False
            continue

        if not in_primary_section or current_kind is None:
            continue

        stripped = line.strip()
        if not stripped.startswith("|"):
            continue

        # Separator row like "|---|---|---|---|".
        if set(stripped) <= set("|-: "):
            saw_header_separator = True
            continue
        if not saw_header_separator:
            # Header row like "| Name | Purpose | Path | Mentioned in |".
            continue

        cells = [c.strip() for c in stripped.split("|")]
        if len(cells) >= 2 and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]
        if len(cells) < 4:
            continue

        name_cell, _purpose_cell, path_cell, mentioned_cell = cells[:4]

        path_match = _REF_TABLE_PATH_CELL_RE.search(path_cell)
        path_value = path_match.group(1) if path_match else path_cell

        mentions: list[str] = []
        for m in _REF_TABLE_PATH_CELL_RE.finditer(mentioned_cell):
            mentions.append(m.group(1))

        rows.append({
            "kind": current_kind,
            "name": name_cell,
            "path": path_value,
            "mentioned_in": mentions,
        })

    return rows


_GENERATED_TIMESTAMP_RE = re.compile(
    r"Generated\s+(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)"
)


@register_plugin(
    "framework-reference-coverage",
    "Validate framework-reference.md covers every framework file exactly once and matches fresh generator output",
)
def plugin_framework_reference_coverage(root: Path, verbose: bool) -> list[Finding]:
    """Validate ``seja-public/docs/reference/framework-reference.md``.

    Four sub-checks:
      1. Coverage -- every framework file walked by ``_build_framework_file_set``
         must appear in exactly one row of the primary categorized table.
         Missing files and duplicate rows are flagged as ``warning``.
      2. Nonexistent targets -- each row's ``Path`` column must resolve to a
         file that exists under ``root``.
      3. Cross-reference liveness -- each row's ``Mentioned in`` entries must
         resolve to existing files under ``seja-public/docs/``.
      4. Regeneration drift -- lazily import ``generate_framework_reference``
         and render a fresh reference with the same pinned timestamp found in
         the committed file; flag ``warning`` on any mismatch.

    Graceful degradation emits a single ``info`` finding when the reference
    file is absent or the generator module is not importable.
    """
    findings: list[Finding] = []
    plugin_name = "framework-reference-coverage"

    reference_path = (
        root / "seja-public" / "docs" / "reference" / "framework-reference.md"
    )
    if not reference_path.is_file():
        findings.append(Finding(
            str(reference_path), 0, "info",
            f"framework-reference.md not found at {reference_path.as_posix()}; "
            "run the generator first: "
            "python .claude/skills/scripts/generate_framework_reference.py",
            plugin_name,
        ))
        return findings

    try:
        reference_text = reference_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        findings.append(Finding(
            str(reference_path), 0, "error",
            f"could not read framework-reference.md: {exc}",
            plugin_name,
        ))
        return findings

    rows = _parse_framework_reference_rows(reference_text)
    framework_files = _build_framework_file_set(root)

    # Sub-check 1: coverage.
    path_to_rows: dict[str, list[dict]] = {}
    for row in rows:
        path_to_rows.setdefault(row["path"], []).append(row)

    referenced_paths = set(path_to_rows.keys())
    missing_from_reference = sorted(framework_files - referenced_paths)
    for missing in missing_from_reference:
        findings.append(Finding(
            str(reference_path), 0, "warning",
            f"framework file '{missing}' is not mentioned in framework-reference.md; "
            "regenerate with: python .claude/skills/scripts/generate_framework_reference.py",
            plugin_name,
        ))

    for path_value, dup_rows in sorted(path_to_rows.items()):
        if len(dup_rows) > 1:
            findings.append(Finding(
                str(reference_path), 0, "warning",
                f"framework file '{path_value}' appears in {len(dup_rows)} rows of "
                "framework-reference.md; the reference should contain exactly one row per file",
                plugin_name,
            ))

    # Sub-check 2: nonexistent targets.
    for row in rows:
        target = root / row["path"]
        if not target.exists():
            findings.append(Finding(
                str(reference_path), 0, "warning",
                f"framework-reference.md row points to nonexistent file '{row['path']}'; "
                "the file may have been renamed or deleted",
                plugin_name,
            ))

    # Sub-check 3: cross-reference liveness.
    public_docs_root = root / "seja-public" / "docs"
    for row in rows:
        for mention in row["mentioned_in"]:
            if not mention:
                continue
            candidate = public_docs_root / mention
            if candidate.exists():
                continue
            if public_docs_root.is_dir():
                hits = list(public_docs_root.rglob(Path(mention).name))
                if hits:
                    continue
            findings.append(Finding(
                str(reference_path), 0, "warning",
                f"framework-reference.md row for '{row['name']}' references "
                f"nonexistent public doc '{mention}'",
                plugin_name,
            ))

    # Sub-check 4: regeneration drift. Lazy import so older checkouts without
    # the generator still run sub-checks 1-3.
    try:
        import importlib
        generator = importlib.import_module("generate_framework_reference")
    except Exception:
        findings.append(Finding(
            str(reference_path), 0, "info",
            "generate_framework_reference.py not found; coverage + target + "
            "cross-ref sub-checks ran but regen-drift check is skipped",
            plugin_name,
        ))
        return findings

    ts_match = _GENERATED_TIMESTAMP_RE.search(reference_text)
    if not ts_match:
        if verbose:
            findings.append(Finding(
                str(reference_path), 0, "info",
                "framework-reference.md has no 'Generated <timestamp>' line; "
                "regen-drift check skipped",
                plugin_name,
            ))
        return findings
    fixed_date = ts_match.group(1)

    try:
        artifacts = generator.discover_all(root)
        public_docs_display = public_docs_root.as_posix()
        # Match the CLI's code path: populate cross-reference mentions via the
        # scanner before rendering. Without this, the plugin's fresh output has
        # empty `Mentioned in` cells while the on-disk file has populated cells
        # (because the CLI ran the scanner), producing permanent false positives.
        try:
            scan_payload = generator._invoke_scanner(root, public_docs_root)
            generator._apply_mentions(artifacts, scan_payload)
        except Exception:
            # Scanner unavailable: fall back to empty mentions. The comparison
            # will still catch non-mention drift, and the scanner failure mode
            # is reported by the generator's own error channel when invoked.
            pass
        fresh_text = generator.render_framework_reference(
            artifacts, public_docs_display, fixed_date
        )
    except Exception as exc:
        findings.append(Finding(
            str(reference_path), 0, "warning",
            f"could not regenerate framework-reference.md for drift check: {exc}",
            plugin_name,
        ))
        return findings

    if fresh_text.strip() != reference_text.strip():
        findings.append(Finding(
            str(reference_path), 0, "warning",
            "framework-reference.md is stale; regenerate with: "
            "python .claude/skills/scripts/generate_framework_reference.py",
            plugin_name,
        ))

    return findings


# ---------------------------------------------------------------------------
# Plugin 8: Lifecycle fact uniqueness
# ---------------------------------------------------------------------------

# Stopwords dropped from the Jaccard normalization. Short English function
# words are the main source of false-positive overlap on short callouts.
_LIFECYCLE_STOPWORDS: frozenset[str] = frozenset({
    "the", "a", "an", "and", "or", "but", "to", "of", "in", "on",
    "at", "by", "for", "with", "from", "is", "are", "was", "were",
    "be", "been", "it", "this", "that", "these", "those", "you",
    "your", "i", "my", "we", "our",
})

# Minimum tokens in the smaller set for a pair to be compared. Short
# boilerplate like "**Framework:** see concepts.md" has ~3 tokens after
# normalization; 8 is the empirical knee before noise dominates.
_LIFECYCLE_TOKEN_MINIMUM = 8

# Jaccard threshold (0-1). 0.6 matches the advisory wording and is the value
# the plan explicitly pins.
_LIFECYCLE_JACCARD_THRESHOLD = 0.6

_MD_SYNTAX_STRIP_RE = re.compile(r"[`*\[\]()\\]")
_PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n+")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def _normalize_paragraph_tokens(raw_text: str) -> set[str]:
    """Normalize a Markdown paragraph into a set of Jaccard tokens.

    Lowercases, strips Markdown syntax (backticks, asterisks, brackets,
    parens, backslashes), collapses whitespace, drops stopwords, drops
    tokens shorter than 3 characters, and returns the remaining words as a
    set so Jaccard overlap is a pure set operation.
    """
    lowered = raw_text.lower()
    no_syntax = _MD_SYNTAX_STRIP_RE.sub(" ", lowered)
    tokens = no_syntax.split()
    out: set[str] = set()
    for tok in tokens:
        cleaned = tok.strip(".,;:!?\"'")
        if len(cleaned) < 3:
            continue
        if cleaned in _LIFECYCLE_STOPWORDS:
            continue
        out.add(cleaned)
    return out


def _jaccard_overlap(a: set[str], b: set[str]) -> float:
    """Return the Jaccard index of two sets (0.0 when either is empty)."""
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    if union == 0:
        return 0.0
    return intersection / union


def _paragraphs_with_headings(text: str) -> list[tuple[str, str]]:
    """Split Markdown text into paragraphs paired with their nearest heading.

    Returns ``[(anchor_hint, paragraph_text), ...]`` in document order. The
    anchor hint is the nearest preceding heading's text (stripped of ``#``
    characters); paragraphs before any heading get an empty anchor.
    """
    out: list[tuple[str, str]] = []
    current_heading = ""
    buffer: list[str] = []

    def flush() -> None:
        if not buffer:
            return
        paragraph = "\n".join(buffer).strip()
        buffer.clear()
        if paragraph:
            out.append((current_heading, paragraph))

    for line in text.splitlines():
        heading_match = _HEADING_RE.match(line)
        if heading_match:
            flush()
            current_heading = heading_match.group(2).strip()
            continue
        if not line.strip():
            flush()
            continue
        buffer.append(line)
    flush()
    return out


def _extract_framework_callout_paragraphs(
    file_path: Path,
) -> list[tuple[str, str, str, set[str]]]:
    """Return ``(source_file, anchor_hint, raw_text, normalized_tokens)``
    tuples for every paragraph in ``file_path`` containing the literal
    ``**Framework:**`` substring.
    """
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    source = file_path.name
    results: list[tuple[str, str, str, set[str]]] = []
    for anchor_hint, paragraph in _paragraphs_with_headings(text):
        if "**Framework:**" not in paragraph:
            continue
        tokens = _normalize_paragraph_tokens(paragraph)
        results.append((source, anchor_hint, paragraph, tokens))
    return results


def _extract_concepts_lifecycle_paragraphs(
    file_path: Path,
) -> list[tuple[str, str, str, set[str]]]:
    """Return normalized paragraph tuples under ``## Framework lifecycle`` in
    ``concepts.md``. These are the canonical definitions that how-to callouts
    should link to rather than duplicate.
    """
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    source = file_path.name
    results: list[tuple[str, str, str, set[str]]] = []
    inside_section = False
    section_heading = ""

    for anchor_hint, paragraph in _paragraphs_with_headings(text):
        if anchor_hint.lower().startswith("framework lifecycle"):
            if not inside_section:
                inside_section = True
                section_heading = anchor_hint
            tokens = _normalize_paragraph_tokens(paragraph)
            results.append((source, section_heading, paragraph, tokens))
            continue
        if inside_section and anchor_hint and anchor_hint != section_heading:
            # Left the target section; stop collecting.
            inside_section = False

    return results


@register_plugin(
    "lifecycle-fact-uniqueness",
    "Flag duplicated lifecycle fact paragraphs across how-to files and concepts.md",
)
def plugin_lifecycle_fact_uniqueness(root: Path, verbose: bool) -> list[Finding]:
    """Detect near-duplicate ``**Framework:**`` callouts across how-to files.

    For every paragraph in ``seja-public/docs/how-to/*.md`` containing a
    ``**Framework:**`` callout, plus every paragraph under
    ``seja-public/docs/concepts.md`` section ``## Framework lifecycle``,
    computes pairwise Jaccard overlap on normalized token sets (see
    ``_normalize_paragraph_tokens``). Pairs with overlap ``>= 0.6`` and at
    least ``_LIFECYCLE_TOKEN_MINIMUM`` tokens in the smaller set are flagged
    as ``warning`` findings whose message names both paragraph locations.

    The 8-token minimum avoids false positives on short boilerplate callouts
    like ``**Framework:** see concepts.md``. The 0.6 threshold matches the
    advisory's stated ``>= 60% textual overlap`` criterion.

    Graceful degradation: emits a single ``info`` finding when the how-to
    directory is absent.
    """
    findings: list[Finding] = []
    plugin_name = "lifecycle-fact-uniqueness"

    how_to_dir = root / "seja-public" / "docs" / "how-to"
    if not how_to_dir.is_dir():
        findings.append(Finding(
            str(how_to_dir), 0, "info",
            f"how-to directory not found at {how_to_dir.as_posix()}; "
            "skipping lifecycle fact uniqueness check",
            plugin_name,
        ))
        return findings

    concepts_file = root / "seja-public" / "docs" / "concepts.md"

    # Gather paragraphs from how-to files (source_key "how-to/<name>").
    paragraphs: list[tuple[str, str, str, set[str]]] = []
    for how_to_md in sorted(how_to_dir.glob("*.md")):
        for source, anchor, raw, tokens in _extract_framework_callout_paragraphs(how_to_md):
            source_key = f"how-to/{source}"
            paragraphs.append((source_key, anchor, raw, tokens))

    if concepts_file.is_file():
        for source, anchor, raw, tokens in _extract_concepts_lifecycle_paragraphs(concepts_file):
            paragraphs.append((source, anchor, raw, tokens))
    elif verbose:
        findings.append(Finding(
            str(concepts_file), 0, "info",
            "concepts.md not found; lifecycle overlap check runs on how-to files alone",
            plugin_name,
        ))

    # Pairwise comparison. Deduplicate via a `seen` set of ordered pair keys.
    seen: set[tuple[tuple[str, str], tuple[str, str]]] = set()
    for i, (src_a, anchor_a, _raw_a, tokens_a) in enumerate(paragraphs):
        for j in range(i + 1, len(paragraphs)):
            src_b, anchor_b, _raw_b, tokens_b = paragraphs[j]
            if (src_a, anchor_a) == (src_b, anchor_b):
                continue
            if min(len(tokens_a), len(tokens_b)) < _LIFECYCLE_TOKEN_MINIMUM:
                continue
            overlap = _jaccard_overlap(tokens_a, tokens_b)
            if overlap < _LIFECYCLE_JACCARD_THRESHOLD:
                continue

            key_a = (src_a, anchor_a)
            key_b = (src_b, anchor_b)
            ordered = tuple(sorted((key_a, key_b)))
            if ordered in seen:
                continue
            seen.add(ordered)

            pct = int(round(overlap * 100))
            first, second = ordered
            first_src, first_anchor = first
            second_src, second_anchor = second
            findings.append(Finding(
                str(root / "seja-public" / "docs" / first_src), 0, "warning",
                f"lifecycle fact paragraph under '{first_anchor}' overlaps {pct}% with "
                f"paragraph under '{second_anchor}' in '{second_src}'; move the shared "
                "fact to concepts.md section Framework lifecycle and link both callouts",
                plugin_name,
            ))

    return findings


# ---------------------------------------------------------------------------
# Plugin 7: Internal reference leakage
# ---------------------------------------------------------------------------

@register_plugin("internal-reference-leakage", "Detect internal development references in public documentation")
def plugin_internal_reference_leakage(root: Path, verbose: bool) -> list[Finding]:
    """Scan documentation files for internal plan IDs, advisory IDs,
    internal phase labels, and SEJA version numbers that should not
    appear in public-facing documentation."""
    findings: list[Finding] = []

    # Patterns that indicate internal development references
    _patterns = [
        (re.compile(r"plan-\d{6}"), "Specific plan ID"),
        (re.compile(r"advisory-\d{6}"), "Specific advisory ID"),
        (re.compile(r"Phase\s+3[ab]\b"), "Internal development phase label"),
        (re.compile(r"SEJA\s+\d+\.\d+\.\d+"), "Internal SEJA version number"),
    ]

    # Files that legitimately contain these patterns (format examples, etc.)
    _allowlisted_files = {
        "shared-definitions.md",     # format syntax examples
        "plan-and-execute.md",       # example plan filenames
    }

    _fenced_re = re.compile(r"^```")
    _example_re = re.compile(r"e\.g\.,|for example|example:", re.IGNORECASE)

    # Scan .md files in documentation directories
    scan_dirs = [
        root / ".claude",
        root / "_references",
        root / "docs",
    ]

    seen: set[Path] = set()
    for scan_dir in scan_dirs:
        if not scan_dir.is_dir():
            continue
        for md_file in sorted(scan_dir.rglob("*.md")):
            if md_file in seen:
                continue
            seen.add(md_file)

            # Skip _output/ directories (internal artifacts)
            rel = md_file.relative_to(root)
            if "_output" in rel.parts:
                continue

            # Skip allowlisted files
            if md_file.name in _allowlisted_files:
                continue

            try:
                text = md_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            in_fence = False
            for line_no, line in enumerate(text.splitlines(), 1):
                if _fenced_re.match(line.strip()):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue

                # Skip lines that are explicit examples
                if _example_re.search(line):
                    continue

                for pattern, label in _patterns:
                    m = pattern.search(line)
                    if m:
                        findings.append(Finding(
                            str(md_file), line_no, "warning",
                            f"{label}: '{m.group()}'",
                            "internal-reference-leakage",
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
