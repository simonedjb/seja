#!/usr/bin/env python3
# designer: When you want to trust your documentation, I run a sweep
#   across every doc file and look for the things that quietly go
#   stale -- dead paths, undocumented commands, drifting terminology,
#   environment variables the docs promise but the code does not set.
#   You get one report that tells you where the docs and the code
#   disagree.
"""
check_docs.py -- Documentation consistency checker with plugin-based scanners.

Invocation: agent-invoked, hook-ci, user-cli
Lifecycle: active

Scans documentation files for staleness, broken references, terminology drift,
and other documentation quality issues. Each scanner is a plugin function that
returns a list of findings.

Exit codes: 0 = no issues, 1 = issues found, 2 = script error.

Usage
-----
    python .claude/skills/critique/check_docs.py [OPTIONS]

Options:
    --root DIR       Repository root (auto-detected if omitted)
    --verbose        Show passing checks and extra detail
    --plugins LIST   Comma-separated plugin names to run (default: all).
                     Known plugins: harness-integrity, path-liveness,
                     env-vars, command-refs, terminology,
                     structural-completeness, harness-reference-coverage,
                     lifecycle-fact-uniqueness, docs-frontmatter,
                     internal-reference-leakage, skill-body-length,
                     quickguide-pointer-compliance,
                     mantra-banner-consistency,
                     script-citation-drift.
    --filter SEVER   Minimum severity to report: error, warning, info (default: info)

Harness reference coverage plugin
----------------------------------
``harness-reference-coverage`` validates ``seja-public/docs/reference/
harness-reference.md`` against four drift classes: coverage (every harness
file walked by the generator must have exactly one row), nonexistent targets
(each row's Path must exist), cross-reference liveness (each Mentioned-in
entry must resolve under ``seja-public/docs/``), and regeneration drift
(compares against a fresh in-memory render from ``generate_harness_reference.py``).
Run it alone with:

    python .claude/skills/critique/check_docs.py --plugins harness-reference-coverage

Lifecycle fact uniqueness plugin
--------------------------------
``lifecycle-fact-uniqueness`` scans paragraphs containing ``**Harness:**``
callouts in ``seja-public/docs/how-to/*.md`` plus paragraphs under
``concepts.md`` section ``## Harness lifecycle`` and flags pairs whose
normalized-token Jaccard overlap is at least 70 percent (with an 8-token
minimum to suppress short-boilerplate noise). Paragraphs under "Before you
start" headings are excluded as prerequisite pointers.
Run it alone with:

    python .claude/skills/critique/check_docs.py --plugins lifecycle-fact-uniqueness

Docs frontmatter plugin
-----------------------
``docs-frontmatter`` walks every ``.md`` file under ``seja-public/docs/``
and verifies each carries a well-formed YAML frontmatter block with the
``diataxis`` and ``freshness`` classification fields used by
the public documentation surface. Required values: ``diataxis`` in
``{tutorial, how-to, reference, explanation}``; ``freshness`` in
``{on-structural-change, release-bound, event-bound, event-frozen}``.
``last-reviewed`` must be an ISO date (YYYY-MM-DD) on non-frozen docs and
must be absent on ``event-frozen`` docs. ``review-by``, if present, must
also be ISO. Unknown fields are allowed for forward compatibility.
Run it alone with:

    python .claude/skills/critique/check_docs.py --plugins docs-frontmatter

Skill body length plugin
------------------------
``skill-body-length`` walks every ``.claude/skills/*/SKILL.md`` file and
measures the agent-facing body line count -- everything from the first
heading after the ``## Arguments`` table through EOF (frontmatter and the
Arguments block are excluded, since those are the Pinned Anchor portions
consumed by pre-skill ref-load, not the executional body). Quick Guide narrative lives in a ``SKILL-quickguide.md``
sibling file and no longer appears in SKILL.md -- the exclusion is
structural rather than heuristic.
It then compares that count against per-tier thresholds derived from the
skill's ``metadata.context_budget`` frontmatter field (default
``standard``): ``light -> 150``, ``standard -> 300``, ``heavy -> 500``.
The plugin detects four drift classes: (1) body-length overrun past the
tier threshold; (2) inlined code-fenced blocks longer than 20 consecutive
lines (candidate for extraction to ``.claude/references/template/``); (3)
``advisory-NNNNNN`` or ``plan-NNNNNN`` citations appearing inside
numbered step bodies (rationale drift signal -- consider moving to a
Rationale footer or a sibling ``SKILL-rationale.md``); (4) more than two
``Same as Mode`` stubs within a single SKILL.md (mode-factoring
candidate). A ``<!-- skill-length-waiver: <reason> -->`` comment in the
body suppresses the length-threshold WARNING only; the other three
signals still fire because they cover orthogonal concerns.
Run it alone with:

    python .claude/skills/critique/check_docs.py --plugins skill-body-length

CHECK_PLUGIN_MANIFEST:
  name: Documentation Consistency
  stack:
    backend: [any]
    frontend: [any]
  scope: docs
  critical: false
"""

# Rationale for design choices and historical context: see check_docs-rationale.md in this directory.
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

# load_quickguide.py lives in the sibling scripts/ directory; add it to the path
# so the bare `from load_quickguide import ...` below resolves correctly when
# this script is invoked directly from its check/ home.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "priv"))

from load_quickguide import load_quickguide as _shared_load_quickguide

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

# Directory names under `.claude/skills/` that are NOT skills and must be
# excluded from the retired-skill scan in `plugin_harness_integrity`.
# - `scripts` and `__pycache__` are tooling, not skills.
# - `_internal` holds inlined worker SKILL.md files for the Dispatch B
#   mode-factoring pattern. Its children are SKILL.md files
#   executed inline by a wrapper, not user-invocable skills, so they must
#   not trigger the "retired without redirect" warning.
_RETIRED_SKILL_SKIP_DIRS = {"scripts", "__pycache__", "_internal"}

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
# Plugin 1: Harness integrity
# ---------------------------------------------------------------------------

@register_plugin("harness-integrity", "Validate CLAUDE.md references against filesystem")
def plugin_harness_integrity(root: Path, verbose: bool) -> list[Finding]:
    findings: list[Finding] = []
    claude_md = root / "CLAUDE.md"
    if not claude_md.is_file():
        findings.append(Finding(str(claude_md), 0, "error", "CLAUDE.md not found", "harness-integrity"))
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

    # Check that user-invocable skills have a SKILL-quickguide.md sibling
    # (Quick Guide narrative lives in a sibling file; this scan now routes
    # through the shared loader).
    for skill_name in sorted(user_skills):
        skill_dir = skills_dir / skill_name
        if not (skill_dir / "SKILL.md").is_file():
            continue
        if _shared_load_quickguide(skill_dir) is None:
            findings.append(Finding(
                str(skill_dir / "SKILL-quickguide.md"), 0, "warning",
                f"User-invocable skill '{skill_name}' is missing SKILL-quickguide.md sibling",
                "harness-integrity",
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
                    "harness-integrity",
                ))

    # Check for retired skills (directories without SKILL.md)
    if skills_dir.is_dir():
        for d in sorted(skills_dir.iterdir()):
            if d.is_dir() and d.name not in _RETIRED_SKILL_SKIP_DIRS:
                if not (d / "SKILL.md").is_file():
                    findings.append(Finding(
                        str(d), 0, "warning",
                        f"Skill directory '{d.name}' has no SKILL.md (retired without redirect?)",
                        "harness-integrity",
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
        root / ".claude" / "references",
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

    # Detect stack -- skip for harness-only repos
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
            # Harness-only repo, skip this plugin
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
    _ref_scan_dirs_env = [root / ".claude" / "references", root / "product-design"]
    md_files = [p for d in _ref_scan_dirs_env if d.is_dir() for p in d.rglob("*.md")]
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

    # Detect stack -- skip for harness-only repos
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

    _ref_scan_dirs_cmd = [root / ".claude" / "references", root / "product-design"]
    md_files = [p for d in _ref_scan_dirs_cmd if d.is_dir() for p in d.rglob("*.md")]
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

    shared_defs = root / ".claude" / "references" / "general" / "shared-definitions.md"
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
    scan_dirs = [root / ".claude", root / ".claude" / "references", root / "product-design"]
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

    template_docs_dir = root / ".claude" / "references" / "template" / "docs"
    project_docs_dir = root / "product-design" / "docs"

    if not project_docs_dir.is_dir():
        findings.append(Finding(
            "", 0, "info",
            "No project documentation directory found (expected in harness-only repos)",
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
# Plugin 7: Harness reference coverage
# ---------------------------------------------------------------------------


def _build_harness_file_set(root: Path) -> set[str]:
    """Return repo-relative POSIX paths for every harness source file.

    Mirrors the roots that ``generate_harness_reference.py`` walks. Used by
    the coverage sub-check of ``harness-reference-coverage`` to determine
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
    general_dir = root / ".claude" / "references" / "general"
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
    template_dir = root / ".claude" / "references" / "template"
    if template_dir.is_dir():
        for t in template_dir.rglob("*.md"):
            files.add(t.relative_to(root).as_posix())

    return files


_REF_TABLE_PATH_CELL_RE = re.compile(r"`([^`]+)`")
_REF_H2_RE = re.compile(r"^##\s+(.+?)\s*$")
_REF_H3_RE = re.compile(r"^###\s+(.+?)\s*$")


def _parse_harness_reference_rows(text: str) -> list[dict]:
    """Parse ``harness-reference.md`` into row dicts.

    Returns a list of ``{"kind", "name", "path", "mentioned_in"}`` dicts.
    Only the primary categorized table (H2 sections with four-column rows) is
    parsed; the user-facing surface table is intentionally skipped to avoid
    double-counting rows during the coverage sub-check.
    """
    rows: list[dict] = []
    current_kind: str | None = None
    in_primary_section = True
    in_xref_subsection = False
    saw_header_separator = False

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        h2_match = _REF_H2_RE.match(line)
        if h2_match:
            heading = h2_match.group(1).strip()
            if heading.lower().startswith("user-facing surface"):
                in_primary_section = False
                current_kind = None
                in_xref_subsection = False
                continue
            in_primary_section = True
            current_kind = heading
            in_xref_subsection = False
            saw_header_separator = False
            continue

        # H3 sub-sections under ``## Scripts``
        # reset header-separator state so each sub-table's own header row is
        # correctly skipped. The Dual-role cross-reference sub-section renders
        # bullet lines, not a table -- flag it so the pipe-aware row parser
        # does not accidentally treat the bullets as data rows.
        h3_match = _REF_H3_RE.match(line)
        if h3_match:
            h3_heading = h3_match.group(1).strip()
            in_xref_subsection = h3_heading.lower().startswith(
                "dual-role cross-reference"
            )
            saw_header_separator = False
            continue

        if not in_primary_section or current_kind is None:
            continue

        if in_xref_subsection:
            continue

        stripped = line.strip()
        if not stripped.startswith("|"):
            continue

        # Separator row like "|---|---|---|---|".
        if set(stripped) <= set("|-: "):
            saw_header_separator = True
            continue
        if not saw_header_separator:
            # Header row like "| Name | Purpose | Path | Mentioned in |" (or
            # the 6-column Scripts variant).
            continue

        cells = [c.strip() for c in stripped.split("|")]
        if len(cells) >= 2 and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]
        if len(cells) < 4:
            continue

        # The Scripts section uses a 6-column shape:
        #     | Name | Purpose | Invoked by | Lifecycle | Path | Mentioned in |
        # Every other H2 kind keeps the original 4-column shape:
        #     | Name | Purpose | Path | Mentioned in |
        if len(cells) >= 6:
            name_cell = cells[0]
            path_cell = cells[4]
            mentioned_cell = cells[5]
        else:
            name_cell = cells[0]
            path_cell = cells[2]
            mentioned_cell = cells[3]

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
    "harness-reference-coverage",
    "Validate harness-reference.md covers every harness file exactly once and matches fresh generator output",
)
def plugin_harness_reference_coverage(root: Path, verbose: bool) -> list[Finding]:
    """Validate ``seja-public/docs/reference/harness-reference.md``.

    Four sub-checks:
      1. Coverage -- every harness file walked by ``_build_harness_file_set``
         must appear in exactly one row of the primary categorized table.
         Missing files and duplicate rows are flagged as ``warning``.
      2. Nonexistent targets -- each row's ``Path`` column must resolve to a
         file that exists under ``root``.
      3. Cross-reference liveness -- each row's ``Mentioned in`` entries must
         resolve to existing files under ``seja-public/docs/``.
      4. Regeneration drift -- lazily import ``generate_harness_reference``
         and render a fresh reference with the same pinned timestamp found in
         the committed file; flag ``warning`` on any mismatch.

    Graceful degradation emits a single ``info`` finding when the reference
    file is absent or the generator module is not importable.
    """
    findings: list[Finding] = []
    plugin_name = "harness-reference-coverage"

    reference_path = (
        root / "seja-public" / "docs" / "reference" / "harness-reference.md"
    )
    if not reference_path.is_file():
        findings.append(Finding(
            str(reference_path), 0, "info",
            f"harness-reference.md not found at {reference_path.as_posix()}; "
            "run the generator first: "
            "python .claude/skills/scripts/priv/generate_harness_reference.py",
            plugin_name,
        ))
        return findings

    try:
        reference_text = reference_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        findings.append(Finding(
            str(reference_path), 0, "error",
            f"could not read harness-reference.md: {exc}",
            plugin_name,
        ))
        return findings

    rows = _parse_harness_reference_rows(reference_text)
    harness_files = _build_harness_file_set(root)

    # Sub-check 1: coverage.
    path_to_rows: dict[str, list[dict]] = {}
    for row in rows:
        path_to_rows.setdefault(row["path"], []).append(row)

    referenced_paths = set(path_to_rows.keys())
    missing_from_reference = sorted(harness_files - referenced_paths)
    for missing in missing_from_reference:
        findings.append(Finding(
            str(reference_path), 0, "warning",
            f"harness file '{missing}' is not mentioned in harness-reference.md; "
            "regenerate with: python .claude/skills/scripts/priv/generate_harness_reference.py",
            plugin_name,
        ))

    for path_value, dup_rows in sorted(path_to_rows.items()):
        if len(dup_rows) > 1:
            findings.append(Finding(
                str(reference_path), 0, "warning",
                f"harness file '{path_value}' appears in {len(dup_rows)} rows of "
                "harness-reference.md; the reference should contain exactly one row per file",
                plugin_name,
            ))

    # Sub-check 2: nonexistent targets.
    for row in rows:
        target = root / row["path"]
        if not target.exists():
            findings.append(Finding(
                str(reference_path), 0, "warning",
                f"harness-reference.md row points to nonexistent file '{row['path']}'; "
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
                f"harness-reference.md row for '{row['name']}' references "
                f"nonexistent public doc '{mention}'",
                plugin_name,
            ))

    # Sub-check 4: regeneration drift. Lazy import so older checkouts without
    # the generator still run sub-checks 1-3.
    try:
        import importlib
        generator = importlib.import_module("generate_harness_reference")
    except Exception:
        findings.append(Finding(
            str(reference_path), 0, "info",
            "generate_harness_reference.py not found; coverage + target + "
            "cross-ref sub-checks ran but regen-drift check is skipped",
            plugin_name,
        ))
        return findings

    ts_match = _GENERATED_TIMESTAMP_RE.search(reference_text)
    if not ts_match:
        if verbose:
            findings.append(Finding(
                str(reference_path), 0, "info",
                "harness-reference.md has no 'Generated <timestamp>' line; "
                "regen-drift check skipped",
                plugin_name,
            ))
        return findings
    fixed_date = ts_match.group(1)

    try:
        artifacts = generator.discover_all(root)
        # Match the CLI's display-root logic: prefer a path relative to the
        # harness root so rendered output is stable across machines.
        try:
            public_docs_display = public_docs_root.resolve().relative_to(
                root.resolve()
            ).as_posix()
        except ValueError:
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
        fresh_text = generator.render_harness_reference(
            artifacts, public_docs_display, fixed_date
        )
    except Exception as exc:
        findings.append(Finding(
            str(reference_path), 0, "warning",
            f"could not regenerate harness-reference.md for drift check: {exc}",
            plugin_name,
        ))
        return findings

    if fresh_text.strip() != reference_text.strip():
        findings.append(Finding(
            str(reference_path), 0, "warning",
            "harness-reference.md is stale; regenerate with: "
            "python .claude/skills/scripts/priv/generate_harness_reference.py",
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
# boilerplate like "**Harness:** see concepts.md" has ~3 tokens after
# normalization; 8 is the empirical knee before noise dominates.
_LIFECYCLE_TOKEN_MINIMUM = 8

# Jaccard threshold (0-1). 0.6 matches the advisory wording and is the value
# the plan explicitly pins.
_LIFECYCLE_JACCARD_THRESHOLD = 0.7

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


def _extract_harness_callout_paragraphs(
    file_path: Path,
    exclude_anchors: frozenset[str] = frozenset(),
) -> list[tuple[str, str, str, set[str]]]:
    """Return ``(source_file, anchor_hint, raw_text, normalized_tokens)``
    tuples for every paragraph in ``file_path`` containing the literal
    ``**Harness:**`` substring.

    Paragraphs whose ``anchor_hint`` matches any entry in
    ``exclude_anchors`` (case-insensitive) are skipped.
    """
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    source = file_path.name
    exclude_lower = {a.lower() for a in exclude_anchors}
    results: list[tuple[str, str, str, set[str]]] = []
    for anchor_hint, paragraph in _paragraphs_with_headings(text):
        if "**Harness:**" not in paragraph:
            continue
        if anchor_hint.lower() in exclude_lower:
            continue
        tokens = _normalize_paragraph_tokens(paragraph)
        results.append((source, anchor_hint, paragraph, tokens))
    return results


def _extract_concepts_lifecycle_paragraphs(
    file_path: Path,
) -> list[tuple[str, str, str, set[str]]]:
    """Return normalized paragraph tuples under ``## Harness lifecycle`` in
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
        if anchor_hint.lower().startswith("harness lifecycle"):
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
    """Detect near-duplicate ``**Harness:**`` callouts across how-to files.

    For every paragraph in ``seja-public/docs/how-to/*.md`` containing a
    ``**Harness:**`` callout, plus every paragraph under
    ``seja-public/docs/concepts.md`` section ``## Harness lifecycle``,
    computes pairwise Jaccard overlap on normalized token sets (see
    ``_normalize_paragraph_tokens``). Pairs with overlap ``>= 0.7`` and at
    least ``_LIFECYCLE_TOKEN_MINIMUM`` tokens in the smaller set are flagged
    as ``warning`` findings whose message names both paragraph locations.

    Paragraphs under "Before you start" headings are excluded as
    prerequisite pointers. The threshold is set to 0.7 to avoid flagging contextual
    inline reminders that share moderate overlap with each other.

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
        for source, anchor, raw, tokens in _extract_harness_callout_paragraphs(
            how_to_md, exclude_anchors=frozenset({"before you start"}),
        ):
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
                "fact to concepts.md section Harness lifecycle and link both callouts",
                plugin_name,
            ))

    return findings


# ---------------------------------------------------------------------------
# Plugin 9: Docs frontmatter
# ---------------------------------------------------------------------------

_DIATAXIS_VALUES: frozenset[str] = frozenset({
    "tutorial", "how-to", "reference", "explanation",
})
_FRESHNESS_VALUES: frozenset[str] = frozenset({
    "on-structural-change", "release-bound", "event-bound", "event-frozen",
})
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_FRONTMATTER_KEY_RE = re.compile(r"^([A-Za-z][\w-]*)\s*:\s*(.*?)\s*$")


def _parse_simple_frontmatter(text: str) -> tuple[dict[str, tuple[str, int]] | None, int | None]:
    """Parse a simple flat YAML frontmatter block from the start of ``text``.

    Returns ``(fields, end_line)`` where ``fields`` maps key -> (value, line_no)
    for each recognized ``key: value`` line, and ``end_line`` is the 1-based
    line number of the closing ``---`` fence. Returns ``(None, None)`` when
    the file does not open with a ``---`` fence.

    The parser is intentionally minimal (no nested structures, no lists, no
    quoted-value handling beyond trivial trimming). Public-docs frontmatter
    is flat with at most five keys, matching this shape.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, None
    fields: dict[str, tuple[str, int]] = {}
    for idx in range(1, len(lines)):
        line = lines[idx]
        if line.strip() == "---":
            return fields, idx + 1  # 1-based line number of closing fence
        m = _FRONTMATTER_KEY_RE.match(line)
        if m:
            key = m.group(1)
            value = m.group(2)
            # Strip surrounding quotes if any (trivial cases only).
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            fields[key] = (value, idx + 1)
    # No closing fence found.
    return None, None


@register_plugin(
    "docs-frontmatter",
    "Validate diataxis/freshness frontmatter on every seja-public/docs/*.md file",
)
def plugin_docs_frontmatter(root: Path, verbose: bool) -> list[Finding]:
    """Verify each public doc carries well-formed Diataxis/freshness metadata.

    Walks ``seja-public/docs/`` recursively. For every ``.md`` file, parses
    the opening YAML frontmatter block and enforces:

      * block is present (file must start with a ``---`` fence and close it);
      * ``diataxis`` is present with a value in ``_DIATAXIS_VALUES``;
      * ``freshness`` is present with a value in ``_FRESHNESS_VALUES``;
      * ``last-reviewed`` is a ``YYYY-MM-DD`` date when
        ``freshness != event-frozen``, and is absent when
        ``freshness == event-frozen``;
      * ``review-by``, when present, is also ``YYYY-MM-DD``.

    Unknown keys are accepted for forward compatibility. Findings carry the
    file path, the line number of the offending key (or ``1`` when the block
    itself is missing), and a human-readable message.

    Graceful degradation: emits a single ``info`` finding when the public
    docs directory does not exist (e.g., on an unsynced private-only
    checkout).
    """
    findings: list[Finding] = []
    plugin_name = "docs-frontmatter"

    public_docs = root / "seja-public" / "docs"
    if not public_docs.is_dir():
        findings.append(Finding(
            str(public_docs), 0, "info",
            f"public docs directory not found at {public_docs.as_posix()}; "
            "skipping frontmatter validation",
            plugin_name,
        ))
        return findings

    for md_file in sorted(public_docs.rglob("*.md")):
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            findings.append(Finding(
                str(md_file), 0, "error",
                f"could not read file: {exc}",
                plugin_name,
            ))
            continue

        fields, _end_line = _parse_simple_frontmatter(text)
        if fields is None:
            findings.append(Finding(
                str(md_file), 1, "warning",
                "missing or malformed YAML frontmatter block (must start and "
                "end with '---' on their own lines)",
                plugin_name,
            ))
            continue

        # diataxis
        diataxis_entry = fields.get("diataxis")
        if diataxis_entry is None:
            findings.append(Finding(
                str(md_file), 1, "warning",
                "frontmatter missing required 'diataxis' field; expected one "
                "of tutorial|how-to|reference|explanation",
                plugin_name,
            ))
        else:
            value, line_no = diataxis_entry
            if value not in _DIATAXIS_VALUES:
                findings.append(Finding(
                    str(md_file), line_no, "warning",
                    f"frontmatter 'diataxis: {value}' is not a recognized "
                    "quadrant; expected one of "
                    "tutorial|how-to|reference|explanation",
                    plugin_name,
                ))

        # freshness
        freshness_entry = fields.get("freshness")
        freshness_value: str | None = None
        if freshness_entry is None:
            findings.append(Finding(
                str(md_file), 1, "warning",
                "frontmatter missing required 'freshness' field; expected one "
                "of on-structural-change|release-bound|event-bound|event-frozen",
                plugin_name,
            ))
        else:
            freshness_value, line_no = freshness_entry
            if freshness_value not in _FRESHNESS_VALUES:
                findings.append(Finding(
                    str(md_file), line_no, "warning",
                    f"frontmatter 'freshness: {freshness_value}' is not a "
                    "recognized tier; expected one of "
                    "on-structural-change|release-bound|event-bound|event-frozen",
                    plugin_name,
                ))

        # last-reviewed: required iff freshness != event-frozen
        last_reviewed_entry = fields.get("last-reviewed")
        if freshness_value == "event-frozen":
            if last_reviewed_entry is not None:
                _, line_no = last_reviewed_entry
                findings.append(Finding(
                    str(md_file), line_no, "warning",
                    "frontmatter 'last-reviewed' must be absent on "
                    "event-frozen docs (the freeze event pins the review date)",
                    plugin_name,
                ))
        else:
            # freshness missing or non-frozen -> last-reviewed must be ISO date.
            if last_reviewed_entry is None:
                # Only require it if freshness itself is a recognized non-frozen
                # value; otherwise the freshness finding is the primary issue.
                if freshness_value in _FRESHNESS_VALUES:
                    findings.append(Finding(
                        str(md_file), 1, "warning",
                        "frontmatter missing required 'last-reviewed' field "
                        f"(required when freshness={freshness_value})",
                        plugin_name,
                    ))
            else:
                value, line_no = last_reviewed_entry
                if not _ISO_DATE_RE.match(value):
                    findings.append(Finding(
                        str(md_file), line_no, "warning",
                        f"frontmatter 'last-reviewed: {value}' is not an ISO "
                        "date (expected YYYY-MM-DD)",
                        plugin_name,
                    ))

        # review-by: optional; if present, must be ISO date.
        review_by_entry = fields.get("review-by")
        if review_by_entry is not None:
            value, line_no = review_by_entry
            if not _ISO_DATE_RE.match(value):
                findings.append(Finding(
                    str(md_file), line_no, "warning",
                    f"frontmatter 'review-by: {value}' is not an ISO date "
                    "(expected YYYY-MM-DD)",
                    plugin_name,
                ))

    return findings


# ---------------------------------------------------------------------------
# Plugin 10: Internal reference leakage
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
        (re.compile(r"research-\d{6}"), "Specific research ID"),
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
        root / ".claude" / "references",
        root / "product-design",
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
# Plugin 11: Skill body length
# ---------------------------------------------------------------------------

# Per-tier body-line thresholds (inclusive ceilings). Tiers map to the
# ``metadata.context_budget`` frontmatter field on a SKILL.md. Values are
# calibrated against the post-compression baseline so the plugin reflects
# the harness as it ships today.
_SKILL_BODY_THRESHOLDS: dict[str, int] = {
    "light": 150,
    "standard": 300,
    "heavy": 500,
}

# Minimum number of consecutive lines inside a fenced code block that
# counts as an inlined template worth extracting. Empirical knee: shorter
# blocks are typically single-command examples that belong inline.
_SKILL_INLINED_FENCE_MIN_LINES = 20

# Upper tolerance for ``Same as Mode`` stubs per SKILL.md. Above this, the
# duplication is structural rather than incidental and the skill is a
# Common Steps factoring candidate.
_SKILL_SAME_AS_MODE_LIMIT = 2

_SKILL_WAIVER_RE = re.compile(
    r"<!--\s*skill-length-waiver\s*:\s*(?P<reason>.*?)\s*-->",
    re.IGNORECASE,
)
_SKILL_CITATION_RE = re.compile(r"\b(advisory-\d{6}|plan-\d{6})\b")
_SKILL_STEP_HEADING_RE = re.compile(r"^###\s+Step\s+\d+", re.IGNORECASE)
_SKILL_STEP_NUMBERED_RE = re.compile(r"^\d+[a-z]?\.\s+")
_SKILL_FENCE_OPEN_RE = re.compile(r"^```")
_SKILL_HEADING_RE = re.compile(r"^#{1,6}\s+\S")
_SKILL_ARGUMENTS_RE = re.compile(r"^##\s+Arguments\s*$", re.IGNORECASE)
_SKILL_SAME_AS_MODE_RE = re.compile(r"same\s+as\s+mode", re.IGNORECASE)


def _parse_skill_frontmatter(text: str) -> tuple[int, str]:
    """Return ``(frontmatter_end_line_idx, context_budget_value)``.

    ``frontmatter_end_line_idx`` is the 0-based index of the line AFTER the
    closing ``---`` fence (i.e. the first line that is no longer part of
    the frontmatter). Returns ``0`` when the file does not open with a
    ``---`` fence. ``context_budget_value`` is the string value of the
    ``context_budget`` key under ``metadata:`` -- defaults to
    ``"standard"`` when the file has no frontmatter or the key is absent.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return 0, "standard"

    end_idx = 0
    in_metadata = False
    context_budget = "standard"
    for idx in range(1, len(lines)):
        line = lines[idx]
        stripped_full = line.strip()
        if stripped_full == "---":
            end_idx = idx + 1
            break
        # Track whether we have entered the top-level ``metadata:`` block.
        # We look for the key at column zero (no leading whitespace).
        if line.rstrip() == "metadata:" or line.rstrip().startswith("metadata:"):
            in_metadata = line.startswith("metadata:")
            continue
        # A new top-level key (non-indented, contains a colon) closes the
        # metadata block we were tracking.
        if in_metadata and line and not line[0].isspace() and ":" in line:
            in_metadata = False
        if in_metadata:
            m = re.match(r"^\s+context_budget\s*:\s*(\S+)\s*$", line)
            if m:
                value = m.group(1).strip().strip("'\"")
                if value in _SKILL_BODY_THRESHOLDS:
                    context_budget = value
    return end_idx, context_budget


def _find_skill_body_start(text: str, frontmatter_end: int) -> int:
    """Return the 0-based line index where the agent-facing body starts.

    Heuristic: locate ``## Arguments``; if found,
    scan forward until the Arguments table terminates (blank line after the
    table rows), then walk until the first ``#`` heading of any level. If
    there is no ``## Arguments`` section, the body starts at the first
    heading after the frontmatter.
    """
    lines = text.splitlines()
    n = len(lines)

    arguments_idx: int | None = None
    for idx in range(frontmatter_end, n):
        if _SKILL_ARGUMENTS_RE.match(lines[idx]):
            arguments_idx = idx
            break

    if arguments_idx is None:
        # Fall back to the first heading after the frontmatter.
        for idx in range(frontmatter_end, n):
            if _SKILL_HEADING_RE.match(lines[idx]):
                return idx
        return frontmatter_end

    # Walk forward through the Arguments table until a blank line closes it
    # (Markdown tables end at the first blank line).
    idx = arguments_idx + 1
    saw_table_row = False
    while idx < n:
        line = lines[idx]
        if line.strip() == "":
            if saw_table_row:
                idx += 1
                break
            idx += 1
            continue
        if line.lstrip().startswith("|"):
            saw_table_row = True
        idx += 1

    # Walk until the first heading of any level.
    while idx < n:
        if _SKILL_HEADING_RE.match(lines[idx]):
            return idx
        idx += 1
    return idx


def _scan_skill_body_for_signals(
    skill_path: Path,
    body_lines: list[str],
    body_start_line_no: int,
) -> list[Finding]:
    """Scan the agent-facing body for inlined-template, citation, and
    ``Same as Mode`` drift signals. Returns a list of ``Finding`` tuples
    (ready to be appended directly -- the caller supplies the plugin name
    via the ``Finding`` constructor).

    ``body_start_line_no`` is the 1-based line number in the source file
    that corresponds to ``body_lines[0]``; used to report accurate source
    locations.
    """
    plugin_name = "skill-body-length"
    findings: list[Finding] = []

    # (1) Inlined code-fenced blocks > threshold.
    in_fence = False
    fence_start_idx: int | None = None
    for idx, line in enumerate(body_lines):
        if _SKILL_FENCE_OPEN_RE.match(line):
            if not in_fence:
                in_fence = True
                fence_start_idx = idx
            else:
                # Closing fence.
                assert fence_start_idx is not None
                span = idx - fence_start_idx - 1  # lines strictly inside
                if span > _SKILL_INLINED_FENCE_MIN_LINES:
                    line_no = body_start_line_no + fence_start_idx
                    findings.append(Finding(
                        str(skill_path), line_no, "warning",
                        f"inlined code-fenced block of {span} lines "
                        f"(>{_SKILL_INLINED_FENCE_MIN_LINES}); consider "
                        "extracting to .claude/references/template/",
                        plugin_name,
                    ))
                in_fence = False
                fence_start_idx = None

    # (2) Rationale citations inside numbered step bodies. A numbered step
    # body is the run of lines following a ``### Step N`` heading or a
    # ``N.`` / ``Na.`` numbered-list line, up to the next blank line (for
    # list items) or the next heading (for ``### Step`` headings).
    in_fence = False
    in_step_body = False
    step_kind: str | None = None  # "heading" or "list"
    for idx, line in enumerate(body_lines):
        if _SKILL_FENCE_OPEN_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        if _SKILL_STEP_HEADING_RE.match(line):
            in_step_body = True
            step_kind = "heading"
            continue
        if _SKILL_STEP_NUMBERED_RE.match(line):
            in_step_body = True
            step_kind = "list"
            # The numbered line itself is part of the step body -- fall
            # through to the citation check below.
        elif in_step_body:
            if step_kind == "list" and line.strip() == "":
                in_step_body = False
                step_kind = None
                continue
            if step_kind == "heading" and _SKILL_HEADING_RE.match(line):
                # A new heading ends the previous ``### Step`` body. The
                # new heading may itself be another ``### Step``, so do
                # not emit here; let the heading handler above re-enter.
                if _SKILL_STEP_HEADING_RE.match(line):
                    in_step_body = True
                    step_kind = "heading"
                else:
                    in_step_body = False
                    step_kind = None
                continue

        if in_step_body:
            m = _SKILL_CITATION_RE.search(line)
            if m:
                line_no = body_start_line_no + idx
                findings.append(Finding(
                    str(skill_path), line_no, "warning",
                    f"rationale citation in step body ({m.group(1)}); "
                    "consider moving to a Rationale footer or "
                    "SKILL-rationale.md sibling",
                    plugin_name,
                ))

    # (3) ``Same as Mode`` stubs above tolerance. Count matches across all
    # body lines (outside fences); emit one summary WARNING when over.
    in_fence = False
    count = 0
    for line in body_lines:
        if _SKILL_FENCE_OPEN_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if _SKILL_SAME_AS_MODE_RE.search(line):
            count += 1
    if count > _SKILL_SAME_AS_MODE_LIMIT:
        findings.append(Finding(
            str(skill_path), 0, "warning",
            f"{count} \"Same as Mode\" stubs detected; consider Common "
            "Steps factoring",
            plugin_name,
        ))

    return findings


@register_plugin(
    "skill-body-length",
    "Measure agent-facing SKILL.md body against per-tier thresholds and flag inlined templates, rationale drift, and mode stubs",
)
def plugin_skill_body_length(root: Path, verbose: bool) -> list[Finding]:
    """Validate agent-facing SKILL.md body length and drift signals.

    For every ``.claude/skills/*/SKILL.md``: parse the YAML frontmatter to
    extract ``metadata.context_budget`` (default ``standard``); locate the
    agent-facing body (everything from the first heading after the
    ``## Arguments`` table through EOF); compare the body line count
    against the per-tier threshold in ``_SKILL_BODY_THRESHOLDS`` and emit
    a WARNING on overrun; then scan the body for inlined code-fenced
    blocks longer than ``_SKILL_INLINED_FENCE_MIN_LINES``, for
    ``advisory-NNNNNN`` / ``plan-NNNNNN`` citations inside numbered step
    bodies, and for more than ``_SKILL_SAME_AS_MODE_LIMIT`` ``Same as
    Mode`` stubs per file -- each as its own WARNING. A body-level
    ``<!-- skill-length-waiver: <reason> -->`` comment suppresses the
    length-threshold WARNING only; the other signals still fire.

    Graceful degradation: emits a single ``info`` finding when the skills
    directory is absent.
    """
    findings: list[Finding] = []
    plugin_name = "skill-body-length"

    skills_dir = root / ".claude" / "skills"
    if not skills_dir.is_dir():
        findings.append(Finding(
            str(skills_dir), 0, "info",
            f"skills directory not found at {skills_dir.as_posix()}; "
            "skipping skill body length check",
            plugin_name,
        ))
        return findings

    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        try:
            text = skill_md.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            findings.append(Finding(
                str(skill_md), 0, "error",
                f"could not read SKILL.md: {exc}",
                plugin_name,
            ))
            continue

        frontmatter_end, context_budget = _parse_skill_frontmatter(text)
        lines = text.splitlines()
        body_start = _find_skill_body_start(text, frontmatter_end)
        body_lines = lines[body_start:]
        body_line_count = len(body_lines)
        body_start_line_no = body_start + 1  # 1-based for Finding reports

        has_waiver = any(
            _SKILL_WAIVER_RE.search(line) for line in body_lines
        )

        threshold = _SKILL_BODY_THRESHOLDS.get(context_budget, _SKILL_BODY_THRESHOLDS["standard"])
        if body_line_count > threshold and not has_waiver:
            findings.append(Finding(
                str(skill_md), body_start_line_no, "warning",
                f"body line count ({body_line_count}) exceeds "
                f"{context_budget} tier threshold ({threshold})",
                plugin_name,
            ))

        findings.extend(
            _scan_skill_body_for_signals(skill_md, body_lines, body_start_line_no)
        )

        if verbose:
            findings.append(Finding(
                str(skill_md), body_start_line_no, "info",
                f"body line count={body_line_count} tier={context_budget} "
                f"threshold={threshold}"
                + (" waiver-present" if has_waiver else ""),
                plugin_name,
            ))

    return findings


# ---------------------------------------------------------------------------
# Plugin 12: Quickguide pointer compliance
# ---------------------------------------------------------------------------

# Pointer line shape (structural match, not exact string):
#   (a) begins with "> " (blockquote)
#   (b) contains the literal token "SKILL-quickguide.md"
#   (c) appears within the first 15 non-blank lines of the SKILL.md body
#       (after frontmatter)
#   (d) is not inside a fenced code block
_QUICKGUIDE_SIBLING_FILENAME = "SKILL-quickguide.md"
_QUICKGUIDE_POINTER_WINDOW = 15


def _has_quickguide_pointer(text: str) -> bool:
    """Return True when the SKILL.md body carries a structurally valid
    pointer line to the sibling SKILL-quickguide.md within the window.
    """
    # Strip YAML frontmatter so the pointer window is measured against the
    # body, not the header.
    lines = text.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                start = idx + 1
                break
    in_fence = False
    seen_non_blank = 0
    for raw in lines[start:]:
        stripped = raw.strip()
        # Track fenced-code-block state.
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if not stripped:
            continue
        seen_non_blank += 1
        if seen_non_blank > _QUICKGUIDE_POINTER_WINDOW:
            return False
        if in_fence:
            continue
        # Blockquote line containing the token.
        if stripped.startswith("> ") and _QUICKGUIDE_SIBLING_FILENAME in stripped:
            return True
    return False


@register_plugin(
    "quickguide-pointer-compliance",
    "Assert every skill with a SKILL-quickguide.md sibling carries the pointer line in SKILL.md",
)
def plugin_quickguide_pointer_compliance(
    root: Path, verbose: bool
) -> list[Finding]:
    """For every skill directory where ``SKILL-quickguide.md`` exists, the
    adjacent ``SKILL.md`` must carry a pointer line (structural shape
    defined above). Protects designer discoverability of the sibling.
    """
    findings: list[Finding] = []
    plugin_name = "quickguide-pointer-compliance"

    skills_dir = root / ".claude" / "skills"
    if not skills_dir.is_dir():
        return findings

    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        sibling = skill_dir / "SKILL-quickguide.md"
        if not sibling.is_file():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        try:
            text = skill_md.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            findings.append(Finding(
                str(skill_md), 0, "error",
                f"could not read SKILL.md: {exc}",
                plugin_name,
            ))
            continue
        if not _has_quickguide_pointer(text):
            findings.append(Finding(
                str(skill_md), 0, "error",
                f"SKILL.md for '{skill_dir.name}' is missing the "
                f"SKILL-quickguide.md pointer (blockquote line containing "
                f"'{_QUICKGUIDE_SIBLING_FILENAME}' within the first "
                f"{_QUICKGUIDE_POINTER_WINDOW} non-blank body lines, "
                f"outside fenced blocks)",
                plugin_name,
            ))

    return findings


# ---------------------------------------------------------------------------
# Plugin 13: Mantra banner consistency
# ---------------------------------------------------------------------------

_MANTRA_BANNER_RE = re.compile(
    r'^>\s+\*\*`/seja-setup`\*\*\s+scaffolds\s+topology-WHAT'
)

_MANTRA_SKILL_DIRS = ["seja-setup", "design", "plan"]


@register_plugin(
    "mantra-banner-consistency",
    "Assert lifecycle-separation mantra banner is byte-identical across "
    "seja-setup, design, plan SKILL.md files",
)
def plugin_mantra_banner_consistency(
    root: Path, verbose: bool
) -> list[Finding]:
    """Check that the mantra banner line is byte-identical across the 3
    SKILL.md files that carry it (seja-setup, design, plan).
    """
    findings: list[Finding] = []
    plugin_name = "mantra-banner-consistency"

    skills_dir = root / ".claude" / "skills"
    if not skills_dir.is_dir():
        return findings

    canonical_text: str | None = None
    canonical_source: str = ""

    for skill_name in _MANTRA_SKILL_DIRS:
        skill_md = skills_dir / skill_name / "SKILL.md"
        if not skill_md.is_file():
            findings.append(Finding(
                str(skill_md), 0, "error",
                f"SKILL.md for '{skill_name}' not found",
                plugin_name,
            ))
            continue
        try:
            lines = skill_md.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            findings.append(Finding(
                str(skill_md), 0, "error",
                f"could not read SKILL.md: {exc}",
                plugin_name,
            ))
            continue

        banner_line: str | None = None
        banner_lineno = 0
        for idx, line in enumerate(lines, 1):
            if _MANTRA_BANNER_RE.match(line):
                banner_line = line
                banner_lineno = idx
                break

        if banner_line is None:
            findings.append(Finding(
                str(skill_md), 0, "error",
                f"mantra banner not found in '{skill_name}/SKILL.md'",
                plugin_name,
            ))
            continue

        if canonical_text is None:
            canonical_text = banner_line
            canonical_source = f"{skill_name}/SKILL.md"
        elif banner_line != canonical_text:
            findings.append(Finding(
                str(skill_md), banner_lineno, "error",
                f"mantra banner in '{skill_name}/SKILL.md' differs from "
                f"canonical source '{canonical_source}'",
                plugin_name,
            ))

    # Note: seja-public/.claude/ no longer exists on disk (split model,
    # plan-000533 step 1).  Mirror consistency is validated at publish time
    # via pre_publish_smoke.py --candidate against the ephemeral temp clone.

    return findings


# ---------------------------------------------------------------------------
# Plugin 14: Script citation drift
# ---------------------------------------------------------------------------

_SCRIPT_CITATION_DRIFT_RE = re.compile(
    r"\b(?:plan|advisory|research)-\d{6}\b"
)
_SCRIPT_TRANSITION_ANCHOR_RE = re.compile(
    r"\bTRANSITION\s+\(?plan-\d{6}\)?\b",
    re.IGNORECASE,
)
_SCRIPT_RATIONALE_POINTER_RE = re.compile(
    r"Rationale for design choices and historical context: see "
    r"(?P<name>[A-Za-z0-9_]+-rationale\.md) in this directory\."
)


def _script_citation_scan_candidates(root: Path) -> list[Path]:
    """Return production script files subject to script-citation drift scan."""
    scripts_dir = root / ".claude" / "skills" / "scripts"
    if not scripts_dir.is_dir():
        return []

    candidates: list[Path] = []
    for py_file in sorted(scripts_dir.rglob("*.py")):
        rel_parts = py_file.relative_to(scripts_dir).parts
        if any(part in {"tests", "priv", "__pycache__"} for part in rel_parts):
            continue
        if py_file.name.startswith("test_"):
            continue
        candidates.append(py_file)
    return candidates


def _has_script_rationale_sibling(script_path: Path) -> bool:
    return script_path.with_name(f"{script_path.stem}-rationale.md").is_file()


def _has_script_rationale_pointer(script_path: Path, text: str) -> bool:
    expected = f"{script_path.stem}-rationale.md"
    for match in _SCRIPT_RATIONALE_POINTER_RE.finditer(text):
        if match.group("name") == expected:
            return True
    return False


@register_plugin(
    "script-citation-drift",
    "Flag private artifact citations in production script bodies unless extracted to a sibling rationale file",
)
def plugin_script_citation_drift(root: Path, verbose: bool) -> list[Finding]:
    """Ensure production script artifact citations live in sibling rationale files.

    The scanner is intentionally warning-level: existing scripts keep working,
    but maintainers get a clear signal to create `<script>-rationale.md` and
    replace inline citation prose. Tests and `scripts/priv/` stay out of scope
    because they intentionally use concrete IDs as fixtures or migration notes.
    """
    findings: list[Finding] = []
    plugin_name = "script-citation-drift"

    candidates = _script_citation_scan_candidates(root)
    if not candidates:
        if verbose:
            findings.append(Finding(
                str(root / ".claude" / "skills" / "scripts"), 0, "info",
                "no production scripts found for script citation drift scan",
                plugin_name,
            ))
        return findings

    for script_path in candidates:
        try:
            text = script_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            findings.append(Finding(
                str(script_path), 0, "error",
                f"could not read script: {exc}",
                plugin_name,
            ))
            continue

        has_sibling = _has_script_rationale_sibling(script_path)
        has_pointer = _has_script_rationale_pointer(script_path, text)

        if has_sibling and not has_pointer:
            findings.append(Finding(
                str(script_path), 0, "warning",
                f"{script_path.name} has a rationale sibling but is missing "
                "the standard module-level pointer",
                plugin_name,
            ))

        if has_sibling:
            continue

        for line_no, line in enumerate(text.splitlines(), 1):
            if _SCRIPT_TRANSITION_ANCHOR_RE.search(line):
                continue
            match = _SCRIPT_CITATION_DRIFT_RE.search(line)
            if match:
                findings.append(Finding(
                    str(script_path), line_no, "warning",
                    f"private artifact citation {match.group(0)} should move "
                    f"to {script_path.stem}-rationale.md with a self-contained "
                    "summary",
                    plugin_name,
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
