#!/usr/bin/env python3
"""
generate_framework_reference.py -- Generate the SEJA framework reference Markdown.

Walks framework roots under `.claude/` and `_references/`, extracts a one-line
purpose string and classification for every artifact (skill, agent, rule,
script, migration, config, general reference, perspective, onboarding,
communication, template), joins the result with the "mentioned in public
docs" map produced by `scan_public_docs_for_filenames.py` (plan-000280), and
emits a Markdown file with two views:

  1. **Primary categorized table** grouping artifacts by kind with columns
     `Name | Purpose | Path | Mentioned in`.
  2. **User-facing surface secondary view** listing only artifacts mentioned
     at least once in the public docs.

The generator is read-only on framework sources. Its sole output is a
Markdown string written to `--output` (or stdout). The first actual commit of
the generated file into `seja-public/docs/reference/framework-reference.md`
is deferred to a later wave-2 plan.

Usage
-----
    python .claude/skills/scripts/generate_framework_reference.py \
        --public-docs-root d:/git/labs/seja-priv/seja-public/docs \
        --output -

Flags:
    --framework-root <path>     Auto-detected by walking up to find .claude/
    --public-docs-root <path>   Default: <framework-root>/seja-public/docs
                                (fallback: <framework-root>/../seja/docs).
    --scan-output <path>        Pre-computed scanner output JSON. If set,
                                the scanner subprocess is skipped.
    --output <path>             Default: <public-docs-root>/reference/
                                framework-reference.md. Use "-" for stdout.
    --check                     CI staleness detection. Exit 1 if drift.
    --fixed-date <ISO8601>      Testing only: pin the preamble timestamp.
    --verbose                   Progress logging to stderr.

Exit codes:
    0  success (or in sync with --check)
    1  drift detected in --check mode
    2  script error
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants and helpers
# ---------------------------------------------------------------------------

SCRIPTS_DIR = Path(__file__).resolve().parent
SCANNER_SCRIPT = SCRIPTS_DIR / "scan_public_docs_for_filenames.py"

# Hardcoded lookup table for config files that lack docstrings.
CONFIG_FILES: dict[str, str] = {
    ".claude/skills/scripts/check_plugin_registry.json":
        "Registry of check_docs.py plugin scanners",
    ".claude/skills/skills-manifest.json":
        "Generated L1 skills manifest (from generate_skills_manifest.py)",
    ".claude/config.json":
        "Claude Code framework configuration",
}

KIND_ORDER = [
    "Skills",
    "Agents",
    "Rules",
    "Scripts",
    "Migrations",
    "Configs",
    "General references",
    "Perspectives",
    "Onboarding",
    "Communication",
    "Templates",
]

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_TOPLEVEL_FIELD_RE = re.compile(r"^(\w[\w-]*):\s*(.*)$", re.MULTILINE)
_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
_HTML_COMMENT_RE = re.compile(r"<!--\s*(.*?)\s*-->", re.DOTALL)
# Matches a redundant "<name>.py -- " / "<name> -- " / "<name>: " prefix that
# nearly every SEJA script repeats at the start of its module docstring. The
# ".py" suffix is optional because some scripts write the bare stem (e.g.
# "project_config -- Central configuration"). Handles ASCII double-hyphen,
# em-dash, single hyphen, and colon as separators. Requires a valid Python
# identifier at the start to keep accidental sentence-start matches
# unlikely, and requires at least one whitespace after the separator so
# "foo--bar" style run-ons do not get stripped.
_SCRIPT_NAME_PREFIX_RE = re.compile(
    r"^[A-Za-z_][\w]*(?:\.py)?\s*(?:--|\u2014|-|:)\s+",
)


@dataclass
class FrameworkArtifact:
    """A single framework artifact with extracted purpose and mentions."""

    kind: str
    name: str
    purpose: str
    path: str
    mentioned_in: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Shared extraction helpers
# ---------------------------------------------------------------------------


def _read_yaml_frontmatter(path: Path) -> dict[str, str] | None:
    """Return top-level scalar fields from a Markdown file's YAML frontmatter."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return None
    fm_text = match.group(1)
    fields_out: dict[str, str] = {}
    for m in _TOPLEVEL_FIELD_RE.finditer(fm_text):
        # Only accept lines at column 0 (top-level scalars).
        line_start = m.start()
        # Back-check: the match must be at start of line with no leading spaces.
        if line_start > 0 and fm_text[line_start - 1] != "\n":
            continue
        if m.group(0).startswith(" "):
            continue
        key = m.group(1)
        value = m.group(2).strip().strip('"').strip("'")
        fields_out[key] = value
    return fields_out


def _strip_frontmatter(text: str) -> str:
    """Return the body of a Markdown file without its YAML frontmatter."""
    match = _FRONTMATTER_RE.match(text)
    if match:
        return text[match.end():].lstrip("\n")
    return text


def _read_module_docstring_first_line(path: Path) -> str:
    """Return the first non-blank line of a Python module docstring.

    Uses ``ast.get_docstring`` so the extractor correctly handles shebang
    lines, encoding declarations, and ``from __future__`` imports. Reads the
    source with ``utf-8-sig`` to transparently strip any BOM -- ``ast.parse``
    refuses to parse a BOM-tagged source otherwise. Strips the redundant
    ``<name>.py -- `` (or em-dash / colon) prefix that most SEJA docstrings
    repeat, since the caller already displays the script name in a separate
    column.
    """
    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return ""
    doc = ast.get_docstring(tree)
    if not doc:
        return ""
    for raw_line in doc.splitlines():
        candidate = raw_line.strip()
        if not candidate:
            continue
        return _SCRIPT_NAME_PREFIX_RE.sub("", candidate)
    return ""


def _read_first_h1_and_lead(path: Path) -> tuple[str, str]:
    """Return (h1-text, first-sentence-of-first-paragraph) for a Markdown file.

    If the file has no H1 heading in the first 50 lines (e.g., spec templates
    that open with an HTML comment block), fall back to the first HTML
    comment's text as the "lead" sentence so the Purpose column still
    surfaces something meaningful without requiring the template prose to be
    restructured. ``h1`` is returned empty in the fallback case; the caller's
    ``_compose_h1_lead`` combines the two correctly either way.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "", ""
    body = _strip_frontmatter(text)
    h1_match = _H1_RE.search(body)
    if not h1_match:
        # Fallback: extract the first HTML comment's first non-blank line
        # from the first 50 lines of the file. This gives Purpose coverage
        # to templates (project-spec.md, roadmap-spec.md) that open with a
        # comment block and have no H1 heading.
        head = "\n".join(body.splitlines()[:50])
        comment_match = _HTML_COMMENT_RE.search(head)
        if not comment_match:
            return "", ""
        comment_body = comment_match.group(1).strip()
        for raw_line in comment_body.splitlines():
            candidate = raw_line.strip()
            if candidate:
                return "", candidate
        return "", ""
    h1 = h1_match.group(1).strip()
    after = body[h1_match.end():]
    # Find first non-blank, non-heading paragraph
    paragraph_lines: list[str] = []
    for line in after.splitlines():
        stripped = line.strip()
        if not stripped:
            if paragraph_lines:
                break
            continue
        if stripped.startswith("#"):
            if paragraph_lines:
                break
            continue
        if stripped.startswith("|") or stripped.startswith(">"):
            if paragraph_lines:
                break
            continue
        paragraph_lines.append(stripped)
    paragraph = " ".join(paragraph_lines)
    # First sentence: split on ". " or end of string.
    if paragraph:
        match = re.match(r"(.+?[.!?])(?:\s|$)", paragraph)
        lead = match.group(1) if match else paragraph
    else:
        lead = ""
    return h1, lead


def _truncate(text: str, limit: int = 120) -> str:
    """Truncate text to `limit` characters with an ellipsis marker."""
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _compose_h1_lead(h1: str, lead: str, limit: int = 120) -> str:
    """Combine H1 + lead sentence into a single purpose string."""
    if h1 and lead:
        combined = f"{h1} -- {lead}"
    elif h1:
        combined = h1
    else:
        combined = lead
    return _truncate(combined, limit)


def _escape_pipes(text: str) -> str:
    """Escape Markdown table pipe characters."""
    return text.replace("|", "\\|")


# ---------------------------------------------------------------------------
# Discovery functions
# ---------------------------------------------------------------------------


def discover_skills(root: Path) -> list[FrameworkArtifact]:
    """Return FrameworkArtifact entries for all SKILL.md files."""
    skills_dir = root / ".claude" / "skills"
    if not skills_dir.is_dir():
        return []
    results: list[FrameworkArtifact] = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        fm = _read_yaml_frontmatter(skill_md) or {}
        name = fm.get("name", skill_dir.name)
        purpose = fm.get("description", "")
        rel = skill_md.relative_to(root).as_posix()
        results.append(
            FrameworkArtifact(
                kind="Skills",
                name=f"/{name}",
                purpose=purpose,
                path=rel,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_agents(root: Path) -> list[FrameworkArtifact]:
    agents_dir = root / ".claude" / "agents"
    if not agents_dir.is_dir():
        return []
    results: list[FrameworkArtifact] = []
    for agent_md in sorted(agents_dir.glob("*.md")):
        fm = _read_yaml_frontmatter(agent_md) or {}
        purpose = fm.get("description", "")
        if not purpose:
            body = _strip_frontmatter(
                agent_md.read_text(encoding="utf-8", errors="replace")
            )
            for line in body.splitlines():
                if line.strip():
                    purpose = line.strip()
                    break
        rel = agent_md.relative_to(root).as_posix()
        results.append(
            FrameworkArtifact(
                kind="Agents",
                name=agent_md.stem,
                purpose=_truncate(purpose),
                path=rel,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_rules(root: Path) -> list[FrameworkArtifact]:
    rules_dir = root / ".claude" / "rules"
    if not rules_dir.is_dir():
        return []
    results: list[FrameworkArtifact] = []
    for rule_md in sorted(rules_dir.glob("*.md")):
        fm = _read_yaml_frontmatter(rule_md) or {}
        purpose = fm.get("description", "")
        if not purpose:
            h1, lead = _read_first_h1_and_lead(rule_md)
            purpose = _compose_h1_lead(h1, lead)
        rel = rule_md.relative_to(root).as_posix()
        results.append(
            FrameworkArtifact(
                kind="Rules",
                name=rule_md.stem,
                purpose=_truncate(purpose),
                path=rel,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_scripts(root: Path) -> list[FrameworkArtifact]:
    scripts_dir = root / ".claude" / "skills" / "scripts"
    if not scripts_dir.is_dir():
        return []
    results: list[FrameworkArtifact] = []
    for script in sorted(scripts_dir.glob("*.py")):
        if script.name == "__init__.py":
            continue
        rel = script.relative_to(root)
        if "tests" in rel.parts or "__pycache__" in rel.parts:
            continue
        purpose = _read_module_docstring_first_line(script)
        results.append(
            FrameworkArtifact(
                kind="Scripts",
                name=script.name,
                purpose=_truncate(purpose),
                path=rel.as_posix(),
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_migrations(root: Path) -> list[FrameworkArtifact]:
    migrations_dir = root / ".claude" / "migrations"
    if not migrations_dir.is_dir():
        return []
    results: list[FrameworkArtifact] = []
    for migration in sorted(migrations_dir.iterdir()):
        if migration.name == "__init__.py" or not migration.is_file():
            continue
        if migration.suffix == ".py":
            purpose = _read_module_docstring_first_line(migration)
        elif migration.suffix == ".md":
            h1, lead = _read_first_h1_and_lead(migration)
            purpose = _compose_h1_lead(h1, lead)
        else:
            continue
        rel = migration.relative_to(root).as_posix()
        results.append(
            FrameworkArtifact(
                kind="Migrations",
                name=migration.name,
                purpose=_truncate(purpose),
                path=rel,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_configs(root: Path) -> list[FrameworkArtifact]:
    results: list[FrameworkArtifact] = []
    for rel_path, purpose in CONFIG_FILES.items():
        full = root / rel_path
        if not full.is_file():
            continue
        results.append(
            FrameworkArtifact(
                kind="Configs",
                name=full.name,
                purpose=purpose,
                path=rel_path,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_general_references(root: Path) -> list[FrameworkArtifact]:
    general_dir = root / "_references" / "general"
    if not general_dir.is_dir():
        return []
    results: list[FrameworkArtifact] = []
    for ref_md in sorted(general_dir.glob("*.md")):
        h1, lead = _read_first_h1_and_lead(ref_md)
        purpose = _compose_h1_lead(h1, lead)
        rel = ref_md.relative_to(root).as_posix()
        results.append(
            FrameworkArtifact(
                kind="General references",
                name=ref_md.stem,
                purpose=purpose,
                path=rel,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_perspectives(root: Path) -> list[FrameworkArtifact]:
    persp_dir = root / "_references" / "general" / "review-perspectives"
    if not persp_dir.is_dir():
        return []
    results: list[FrameworkArtifact] = []
    for persp_md in sorted(persp_dir.glob("*.md")):
        fm = _read_yaml_frontmatter(persp_md) or {}
        name = fm.get("name") or persp_md.stem
        h1, _ = _read_first_h1_and_lead(persp_md)
        purpose = _truncate(h1 or name)
        rel = persp_md.relative_to(root).as_posix()
        results.append(
            FrameworkArtifact(
                kind="Perspectives",
                name=name,
                purpose=purpose,
                path=rel,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_onboarding(root: Path) -> list[FrameworkArtifact]:
    onb_dir = root / "_references" / "general" / "onboarding"
    if not onb_dir.is_dir():
        return []
    results: list[FrameworkArtifact] = []
    for onb_md in sorted(onb_dir.glob("*.md")):
        h1, lead = _read_first_h1_and_lead(onb_md)
        purpose = _compose_h1_lead(h1, lead)
        rel = onb_md.relative_to(root).as_posix()
        results.append(
            FrameworkArtifact(
                kind="Onboarding",
                name=onb_md.stem,
                purpose=purpose,
                path=rel,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_communication(root: Path) -> list[FrameworkArtifact]:
    comm_dir = root / "_references" / "general" / "communication"
    if not comm_dir.is_dir():
        return []
    results: list[FrameworkArtifact] = []
    for comm_md in sorted(comm_dir.glob("*.md")):
        h1, lead = _read_first_h1_and_lead(comm_md)
        purpose = _compose_h1_lead(h1, lead)
        rel = comm_md.relative_to(root).as_posix()
        results.append(
            FrameworkArtifact(
                kind="Communication",
                name=comm_md.stem,
                purpose=purpose,
                path=rel,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_templates(root: Path) -> list[FrameworkArtifact]:
    tmpl_dir = root / "_references" / "template"
    if not tmpl_dir.is_dir():
        return []
    results: list[FrameworkArtifact] = []
    for tmpl_md in sorted(tmpl_dir.rglob("*.md")):
        h1, lead = _read_first_h1_and_lead(tmpl_md)
        purpose = _compose_h1_lead(h1, lead)
        rel = tmpl_md.relative_to(root).as_posix()
        # Distinguish top-level vs nested templates in the display name.
        nested = tmpl_md.relative_to(tmpl_dir).as_posix()
        name = nested[:-3] if nested.endswith(".md") else tmpl_md.stem
        results.append(
            FrameworkArtifact(
                kind="Templates",
                name=name,
                purpose=purpose,
                path=rel,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_all(root: Path) -> list[FrameworkArtifact]:
    """Return the full list of framework artifacts across every kind."""
    artifacts: list[FrameworkArtifact] = []
    artifacts.extend(discover_skills(root))
    artifacts.extend(discover_agents(root))
    artifacts.extend(discover_rules(root))
    artifacts.extend(discover_scripts(root))
    artifacts.extend(discover_migrations(root))
    artifacts.extend(discover_configs(root))
    artifacts.extend(discover_general_references(root))
    artifacts.extend(discover_perspectives(root))
    artifacts.extend(discover_onboarding(root))
    artifacts.extend(discover_communication(root))
    artifacts.extend(discover_templates(root))
    return artifacts


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _render_mention_cell(mentions: list[str]) -> str:
    if not mentions:
        return ""
    return ", ".join(f"`{m}`" for m in mentions)


def render_primary_table(artifacts: list[FrameworkArtifact]) -> str:
    """Render the primary categorized table grouped by kind."""
    by_kind: dict[str, list[FrameworkArtifact]] = {}
    for a in artifacts:
        by_kind.setdefault(a.kind, []).append(a)

    lines: list[str] = []
    for kind in KIND_ORDER:
        entries = sorted(by_kind.get(kind, []), key=lambda a: a.name)
        if not entries:
            continue
        lines.append(f"## {kind}")
        lines.append("")
        lines.append("| Name | Purpose | Path | Mentioned in |")
        lines.append("|---|---|---|---|")
        for a in entries:
            name_cell = _escape_pipes(a.name)
            purpose_cell = _escape_pipes(a.purpose)
            path_cell = f"`{a.path}`"
            mention_cell = _render_mention_cell(a.mentioned_in)
            lines.append(
                f"| {name_cell} | {purpose_cell} | {path_cell} | {mention_cell} |"
            )
        lines.append("")
    return "\n".join(lines)


def render_user_facing_surface(
    artifacts: list[FrameworkArtifact],
    public_docs_root: str,
) -> str:
    """Render the user-facing surface secondary view."""
    mentioned = [a for a in artifacts if a.mentioned_in]
    mentioned.sort(key=lambda a: a.name)

    lines: list[str] = []
    lines.append("## User-facing surface")
    lines.append("")
    lines.append(
        f"Framework artifacts mentioned at least once in `{public_docs_root}`."
    )
    lines.append("")
    lines.append("| Name | Kind | Path | First mention |")
    lines.append("|---|---|---|---|")
    for a in mentioned:
        first_mention = a.mentioned_in[0] if a.mentioned_in else ""
        lines.append(
            f"| {_escape_pipes(a.name)} | {a.kind} | `{a.path}` | `{first_mention}` |"
        )
    lines.append("")
    return "\n".join(lines)


def render_framework_reference(
    artifacts: list[FrameworkArtifact],
    public_docs_root: str,
    generated_at: str,
) -> str:
    """Compose the full Markdown document (preamble + primary + surface)."""
    preamble = (
        "<!--\n"
        "This file is generated by .claude/skills/scripts/generate_framework_reference.py.\n"
        "Do not edit by hand. To regenerate:\n"
        "    python .claude/skills/scripts/generate_framework_reference.py \\\n"
        f"        --public-docs-root {public_docs_root} \\\n"
        f"        --output {public_docs_root}/reference/framework-reference.md\n"
        "-->\n\n"
        "# SEJA framework reference\n\n"
        f"Generated {generated_at} from seja-priv framework state.\n\n"
    )
    primary = render_primary_table(artifacts)
    surface = render_user_facing_surface(artifacts, public_docs_root)
    return preamble + primary + "\n" + surface


# ---------------------------------------------------------------------------
# Scanner integration
# ---------------------------------------------------------------------------


def _load_scan_output(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"could not read scan output {path}: {exc}") from exc


def _invoke_scanner(framework_root: Path, public_docs_root: Path) -> dict:
    if not SCANNER_SCRIPT.is_file():
        raise RuntimeError(
            f"scanner script not found at {SCANNER_SCRIPT}; "
            "either install plan-000280 or pass --scan-output explicitly"
        )
    result = subprocess.run(
        [
            sys.executable,
            str(SCANNER_SCRIPT),
            "--framework-root",
            str(framework_root),
            "--public-docs-root",
            str(public_docs_root),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"scanner subprocess failed (exit {result.returncode}): {result.stderr}"
        )
    return json.loads(result.stdout)


def _apply_mentions(
    artifacts: list[FrameworkArtifact],
    scan_payload: dict,
) -> None:
    """Populate each artifact's `mentioned_in` list from the scanner payload."""
    framework_files = scan_payload.get("framework_files", {})
    for a in artifacts:
        entry = framework_files.get(a.path)
        if entry is not None:
            a.mentioned_in = list(entry.get("mentioned_in", []))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _find_framework_root() -> Path:
    candidate = SCRIPTS_DIR
    while candidate != candidate.parent:
        if (candidate / ".claude").is_dir():
            return candidate
        candidate = candidate.parent
    return Path.cwd()


def _resolve_public_docs_root(framework_root: Path, explicit: str | None) -> Path | None:
    if explicit:
        return Path(explicit).resolve()
    in_repo = framework_root / "seja-public" / "docs"
    if in_repo.is_dir():
        return in_repo.resolve()
    sibling = framework_root.parent / "seja" / "docs"
    if sibling.is_dir():
        return sibling.resolve()
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the SEJA framework reference Markdown",
    )
    parser.add_argument("--framework-root", default=None)
    parser.add_argument("--public-docs-root", default=None)
    parser.add_argument("--scan-output", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fixed-date", default=None)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    framework_root = (
        Path(args.framework_root).resolve()
        if args.framework_root
        else _find_framework_root()
    )
    if not framework_root.is_dir():
        print(
            f"ERROR: framework root does not exist: {framework_root}",
            file=sys.stderr,
        )
        return 2

    public_docs_root = _resolve_public_docs_root(framework_root, args.public_docs_root)
    if public_docs_root is None and args.scan_output is None:
        print(
            "ERROR: public-docs root could not be resolved and --scan-output was "
            "not provided. Pass --public-docs-root or --scan-output.",
            file=sys.stderr,
        )
        return 2

    if public_docs_root is not None and not public_docs_root.is_dir() and args.scan_output is None:
        print(
            f"ERROR: public-docs root does not exist: {public_docs_root}",
            file=sys.stderr,
        )
        return 2

    if args.verbose:
        print(f"framework_root: {framework_root}", file=sys.stderr)
        print(f"public_docs_root: {public_docs_root}", file=sys.stderr)

    # Discover artifacts
    try:
        artifacts = discover_all(framework_root)
    except OSError as exc:
        print(f"ERROR: discovery failure: {exc}", file=sys.stderr)
        return 2

    # Populate mentions
    try:
        if args.scan_output:
            scan_payload = _load_scan_output(Path(args.scan_output).resolve())
        else:
            if public_docs_root is None:
                print(
                    "ERROR: --public-docs-root is required when --scan-output is not provided",
                    file=sys.stderr,
                )
                return 2
            scan_payload = _invoke_scanner(framework_root, public_docs_root)
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    _apply_mentions(artifacts, scan_payload)

    # Resolve timestamp
    if args.fixed_date:
        generated_at = args.fixed_date
    else:
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Resolve public_docs_root display string. Prefer a path relative to the
    # framework root so rendered output is stable across machines; fall back
    # to the absolute path only when the public docs root lives outside the
    # framework tree (e.g., sibling `../seja/docs` checkout).
    if public_docs_root is not None:
        try:
            display_root = public_docs_root.relative_to(framework_root).as_posix()
        except ValueError:
            display_root = public_docs_root.as_posix()
    else:
        display_root = scan_payload.get("public_docs_root", "")

    rendered = render_framework_reference(artifacts, display_root, generated_at)

    # --check mode
    if args.check:
        if not args.output or args.output == "-":
            print(
                "ERROR: --check requires an --output file path",
                file=sys.stderr,
            )
            return 2
        output_path = Path(args.output).resolve()
        if not output_path.is_file():
            print(
                f"DRIFT: output file does not exist: {output_path}",
                file=sys.stderr,
            )
            return 1
        on_disk = output_path.read_text(encoding="utf-8")
        # Normalize line endings so Windows checkouts with CRLF on disk
        # still compare equal against LF-rendered generator output.
        if on_disk.replace("\r\n", "\n") == rendered.replace("\r\n", "\n"):
            if args.verbose:
                print(f"OK: {output_path} is up to date.", file=sys.stderr)
            return 0
        print(
            f"DRIFT: {output_path} differs from generator output",
            file=sys.stderr,
        )
        return 1

    # Write or stdout
    output_arg = args.output
    if output_arg is None:
        if public_docs_root is None:
            print(
                "ERROR: cannot default --output without --public-docs-root",
                file=sys.stderr,
            )
            return 2
        output_arg = str(public_docs_root / "reference" / "framework-reference.md")

    if output_arg == "-":
        sys.stdout.write(rendered)
    else:
        output_path = Path(output_arg).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        if args.verbose:
            print(f"wrote: {output_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
