#!/usr/bin/env python3
# designer: When you want a single catalog of every artifact the harness
#   ships -- skills, agents, rules, scripts, migrations, references,
#   templates -- cross-referenced against which ones are actually mentioned
#   in the public docs, I'm the generator that walks the harness roots and
#   produces `harness-reference.md`: a grouped table for the whole catalog
#   plus a second view listing only the user-facing surface.
"""
generate_harness_reference.py -- Generate the SEJA harness reference Markdown.

Invocation: script-invoked, user-cli
Lifecycle: active

Walks harness roots under `.claude/` and `.claude/references/`, extracts a one-line
purpose string and classification for every artifact (skill, agent, rule,
script, migration, config, general reference, perspective, onboarding,
communication, template), joins the result with the "mentioned in public
docs" map produced by `scan_public_docs_for_filenames.py`, and
emits a Markdown file with two views:

  1. **Primary categorized table** grouping artifacts by kind with columns
     `Name | Purpose | Path | Mentioned in`.
  2. **User-facing surface secondary view** listing only artifacts mentioned
     at least once in the public docs.

The generator is read-only on harness sources. Its sole output is a
Markdown string written to `--output` (or stdout). The first actual commit of
the generated file into `seja-public/docs/reference/harness-reference.md`
is deferred to a later wave-2 plan.

Usage
-----
    python .claude/skills/scripts/generate_harness_reference.py \
        --public-docs-root d:/git/labs/seja-priv/seja-public/docs \
        --output -

Flags:
    --harness-root <path>       Auto-detected by walking up to find .claude/
    --public-docs-root <path>   Default: <harness-root>/seja-public/docs
                                (fallback: <harness-root>/../seja/docs).
    --scan-output <path>        Pre-computed scanner output JSON. If set,
                                the scanner subprocess is skipped.
    --output <path>             Default: <public-docs-root>/reference/
                                harness-reference.md. Use "-" for stdout.
    --check                     CI staleness detection. Exit 1 if drift.
    --fixed-date <ISO8601>      Testing only: pin the preamble timestamp.
    --verbose                   Progress logging to stderr.

Exit codes:
    0  success (or in sync with --check)
    1  drift detected in --check mode
    2  script error
"""

# Rationale for design choices and historical context: see generate_harness_reference-rationale.md in this directory.
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
        "Claude Code harness configuration",
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

# Script bucket labels, in render order. First-match bucket rule:
#   1. ``Lifecycle: one-shot``  -> "Archived migrations" (wins over any role).
#   2. role list contains ``user-cli``  -> "User-invocable".
#   3. role list contains ``skill-invoked`` or ``agent-invoked``
#      -> "Skill- or agent-invoked".
#   4. otherwise (only ``hook-ci``/``library``/``test``)  -> "Hook and CI".
_SCRIPT_BUCKETS: tuple[str, ...] = (
    "User-invocable",
    "Skill- or agent-invoked",
    "Hook and CI",
    "Archived migrations",
)

# Map a single invocation role to the bucket it would fall into if it were
# the sole role on a script. Used to resolve "see <other-sub-section>" links
# in the dual-role cross-reference sub-section.
_ROLE_TO_BUCKET: dict[str, str] = {
    "user-cli": "User-invocable",
    "skill-invoked": "Skill- or agent-invoked",
    "agent-invoked": "Skill- or agent-invoked",
    "hook-ci": "Hook and CI",
    "library": "Hook and CI",
    "test": "Hook and CI",
}


def _bucket_name_to_anchor(name: str) -> str:
    """Return a GitHub-style lowercase-hyphen slug for a bucket heading."""
    # GitHub collapses whitespace to a single hyphen and drops punctuation.
    # The four bucket names have no punctuation to strip; only lowercase +
    # space-to-hyphen. "Skill- or agent-invoked" -> "skill--or-agent-invoked"
    # because GitHub keeps the literal hyphen before the space.
    return name.lower().replace(" ", "-")


def _script_roles(artifact: "HarnessArtifact") -> list[str]:
    """Return the invocation role list for a Scripts/Tools artifact.

    The ``invocation`` string is preserved verbatim from the docstring
    (comma-space separated). This helper splits and lowercases so bucket
    assignment and dual-role detection can branch on membership.
    """
    return [token.strip().lower() for token in artifact.invocation.split(",")]


def _assign_script_bucket(artifact: "HarnessArtifact") -> str:
    """Return the bucket name for a Scripts/Tools artifact.

    Implements the bucket mapping (first match wins):
    lifecycle-one-shot beats role-based buckets; ``user-cli`` beats
    ``skill-invoked``/``agent-invoked``; and everything else (``hook-ci``,
    ``library``, ``test``) falls into "Hook and CI".
    """
    if artifact.lifecycle == "one-shot":
        return "Archived migrations"
    roles = _script_roles(artifact)
    if "user-cli" in roles:
        return "User-invocable"
    if "skill-invoked" in roles or "agent-invoked" in roles:
        return "Skill- or agent-invoked"
    return "Hook and CI"

# Path (relative to the public-docs root) of the file this generator produces.
# Removing it from `mentioned_in` lists prevents circular self-citations from
# inflating the `User-facing surface` view (otherwise every artifact mentioned
# in the generated reference would appear there, including pure-data rows whose
# only "mention" is being cataloged here).
SELF_OUTPUT_REL: str = "reference/harness-reference.md"

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
# Matches a line that is *only* a bare filename (e.g. ``0001_foo.py`` or
# ``generate_bar``). Some module docstrings open with the filename on its own
# line, then put the human description on line 2. The character class is
# ``[\w]+`` (not ``[A-Za-z_][\w]*``) because real cases start with a digit
# (e.g. ``0001_split_quickstart_to_seed_design_upgrade.py``); a letter-leading
# class would silently miss the migrations this skip targets.
_FILENAME_ONLY_LINE_RE = re.compile(r"^[\w]+(?:\.py)?$")

# Header-field regex for the docstring-declared Invocation / Lifecycle fields
# (script-header convention). Case-sensitive, multiline; first match per
# field wins. Pinned in ```.claude/references/general/script-header-convention.md```.
_SCRIPT_HEADER_FIELD_RE = re.compile(
    r"^(Invocation|Lifecycle):\s*(.+)$",
    re.MULTILINE,
)

# Enums pinned by the script-header convention. Lowercased tokens are compared
# against these sets after stripping; any token outside the set yields the
# sentinel ``("invalid", "invalid")`` tuple so ``--check`` can surface offenders
# in a later step without changing this step's behavior.
_INVOCATION_ENUM: frozenset[str] = frozenset({
    "user-cli",
    "skill-invoked",
    "agent-invoked",
    "script-invoked",
    "hook-ci",
    "library",
    "test",
})
_LIFECYCLE_ENUM: frozenset[str] = frozenset({
    "active",
    "one-shot",
    "deprecated",
})


@dataclass
class HarnessArtifact:
    """A single harness artifact with extracted purpose and mentions.

    ``invocation`` and ``lifecycle`` carry the docstring-header-declared
    classification for Python scripts. They default to
    ``"unspecified"`` for every non-script kind and for scripts that lack the
    header. The grouped Scripts renderer adds the Invocation/Lifecycle columns.
    """

    kind: str
    name: str
    purpose: str
    path: str
    mentioned_in: list[str] = field(default_factory=list)
    invocation: str = "unspecified"
    lifecycle: str = "unspecified"


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
    column. If the first non-blank line is just a bare filename (e.g.
    ``0001_foo.py``), skip it and use the second non-blank line so the
    Purpose column surfaces real description text instead of the filename.
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
    non_blank: list[str] = []
    for raw_line in doc.splitlines():
        candidate = raw_line.strip()
        if not candidate:
            continue
        non_blank.append(candidate)
        if len(non_blank) == 2:
            break
    if not non_blank:
        return ""
    chosen = (
        non_blank[1]
        if _FILENAME_ONLY_LINE_RE.fullmatch(non_blank[0]) and len(non_blank) >= 2
        else non_blank[0]
    )
    return _SCRIPT_NAME_PREFIX_RE.sub("", chosen)


def _read_script_invocation_and_lifecycle(path: Path) -> tuple[str, str]:
    """Return (invocation, lifecycle) extracted from a Python script docstring.

    Parses the module docstring via ``ast.get_docstring`` (the same entry
    point as :func:`_read_module_docstring_first_line`) and scans it for the
    first ``Invocation:`` and ``Lifecycle:`` header lines using the regex
    pinned in ```.claude/references/general/script-header-convention.md```. Values are
    validated against the two enums declared in the same convention doc.

    Return values:

    - ``("<invocation-string>", "<lifecycle-string>")`` on success. The
      ``invocation`` string is the original comma-separated value (preserved
      verbatim after strip) so downstream rendering can display it directly;
      enum validation is performed on the split+lowered tokens but the result
      is not retained here.
    - ``("unspecified", "unspecified")`` when either field is absent, or when
      the script has no docstring at all. (Either-field-missing fails closed
      to this sentinel -- partial headers are treated as absent.)
    - ``("invalid", "invalid")`` when a value is present but fails enum
      validation. ``--check`` can surface these in a later step; this step
      does not change ``--check`` behavior.
    """
    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return "unspecified", "unspecified"
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return "unspecified", "unspecified"
    doc = ast.get_docstring(tree)
    if not doc:
        return "unspecified", "unspecified"

    invocation_raw: str | None = None
    lifecycle_raw: str | None = None
    for match in _SCRIPT_HEADER_FIELD_RE.finditer(doc):
        key = match.group(1)
        value = match.group(2).strip()
        if key == "Invocation" and invocation_raw is None:
            invocation_raw = value
        elif key == "Lifecycle" and lifecycle_raw is None:
            lifecycle_raw = value
        if invocation_raw is not None and lifecycle_raw is not None:
            break

    if invocation_raw is None or lifecycle_raw is None:
        return "unspecified", "unspecified"

    invocation_tokens = [t.strip().lower() for t in invocation_raw.split(",")]
    if not invocation_tokens or any(not t for t in invocation_tokens):
        return "invalid", "invalid"
    if any(t not in _INVOCATION_ENUM for t in invocation_tokens):
        return "invalid", "invalid"
    lifecycle_token = lifecycle_raw.strip().lower()
    if lifecycle_token not in _LIFECYCLE_ENUM:
        return "invalid", "invalid"

    return invocation_raw, lifecycle_raw


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


def discover_skills(root: Path) -> list[HarnessArtifact]:
    """Return HarnessArtifact entries for all SKILL.md files."""
    skills_dir = root / ".claude" / "skills"
    if not skills_dir.is_dir():
        return []
    results: list[HarnessArtifact] = []
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
            HarnessArtifact(
                kind="Skills",
                name=f"/{name}",
                purpose=purpose,
                path=rel,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_agents(root: Path) -> list[HarnessArtifact]:
    agents_dir = root / ".claude" / "agents"
    if not agents_dir.is_dir():
        return []
    results: list[HarnessArtifact] = []
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
            HarnessArtifact(
                kind="Agents",
                name=agent_md.stem,
                purpose=_truncate(purpose),
                path=rel,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_rules(root: Path) -> list[HarnessArtifact]:
    rules_dir = root / ".claude" / "rules"
    if not rules_dir.is_dir():
        return []
    results: list[HarnessArtifact] = []
    for rule_md in sorted(rules_dir.glob("*.md")):
        fm = _read_yaml_frontmatter(rule_md) or {}
        purpose = fm.get("description", "")
        if not purpose:
            h1, lead = _read_first_h1_and_lead(rule_md)
            purpose = _compose_h1_lead(h1, lead)
        rel = rule_md.relative_to(root).as_posix()
        results.append(
            HarnessArtifact(
                kind="Rules",
                name=rule_md.stem,
                purpose=_truncate(purpose),
                path=rel,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_scripts(root: Path) -> list[HarnessArtifact]:
    scripts_dir = root / ".claude" / "skills" / "scripts"
    skills_dir = root / ".claude" / "skills"
    if not scripts_dir.is_dir():
        return []
    # Collect scripts from scripts/ and co-located skill subdirectories
    candidates: list[Path] = list(scripts_dir.glob("*.py"))
    for skill_dir in sorted(skills_dir.iterdir()):
        if skill_dir.is_dir() and skill_dir.name not in ("scripts", "_internal"):
            candidates.extend(skill_dir.glob("*.py"))
    results: list[HarnessArtifact] = []
    for script in sorted(candidates):
        if script.name == "__init__.py":
            continue
        rel = script.relative_to(root)
        if "tests" in rel.parts or "__pycache__" in rel.parts:
            continue
        purpose = _read_module_docstring_first_line(script)
        invocation, lifecycle = _read_script_invocation_and_lifecycle(script)
        results.append(
            HarnessArtifact(
                kind="Scripts",
                name=script.name,
                purpose=_truncate(purpose),
                path=rel.as_posix(),
                invocation=invocation,
                lifecycle=lifecycle,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_tools(root: Path) -> list[HarnessArtifact]:
    """Return HarnessArtifact entries for priv-only maintainer tools.

    Walks ``tools/*.py`` (non-recursive) and reuses the same docstring
    extractor as :func:`discover_scripts`. These are private to harness
    development (not synced to public ``seja``) but belong in the harness
    reference so maintainers can see them alongside the skill scripts. Their
    rendering belongs in the Scripts sub-tables.

    The returned artifacts carry ``kind="Tools"`` -- a kind deliberately not
    present in :data:`KIND_ORDER`, so they do not render in this step. Step 4
    will fold tools into the Scripts section (either via a dedicated sub-table
    or a promoted-kind key) and update the renderer accordingly.
    """
    tools_dir = root / "tools"
    if not tools_dir.is_dir():
        return []
    results: list[HarnessArtifact] = []
    for script in sorted(tools_dir.glob("*.py")):
        if script.name == "__init__.py":
            continue
        rel = script.relative_to(root)
        purpose = _read_module_docstring_first_line(script)
        invocation, lifecycle = _read_script_invocation_and_lifecycle(script)
        results.append(
            HarnessArtifact(
                kind="Tools",
                name=script.name,
                purpose=_truncate(purpose),
                path=rel.as_posix(),
                invocation=invocation,
                lifecycle=lifecycle,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_migrations(root: Path) -> list[HarnessArtifact]:
    migrations_dir = root / ".claude" / "migrations"
    if not migrations_dir.is_dir():
        return []
    results: list[HarnessArtifact] = []
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
            HarnessArtifact(
                kind="Migrations",
                name=migration.name,
                purpose=_truncate(purpose),
                path=rel,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_configs(root: Path) -> list[HarnessArtifact]:
    results: list[HarnessArtifact] = []
    for rel_path, purpose in CONFIG_FILES.items():
        full = root / rel_path
        if not full.is_file():
            continue
        results.append(
            HarnessArtifact(
                kind="Configs",
                name=full.name,
                purpose=purpose,
                path=rel_path,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_general_references(root: Path) -> list[HarnessArtifact]:
    general_dir = root / ".claude" / "references" / "general"
    if not general_dir.is_dir():
        return []
    results: list[HarnessArtifact] = []
    for ref_md in sorted(general_dir.glob("*.md")):
        h1, lead = _read_first_h1_and_lead(ref_md)
        purpose = _compose_h1_lead(h1, lead)
        rel = ref_md.relative_to(root).as_posix()
        results.append(
            HarnessArtifact(
                kind="General references",
                name=ref_md.stem,
                purpose=purpose,
                path=rel,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_perspectives(root: Path) -> list[HarnessArtifact]:
    persp_dir = root / ".claude" / "references" / "general" / "review-perspectives"
    if not persp_dir.is_dir():
        return []
    results: list[HarnessArtifact] = []
    for persp_md in sorted(persp_dir.glob("*.md")):
        fm = _read_yaml_frontmatter(persp_md) or {}
        name = fm.get("name") or persp_md.stem
        h1, _ = _read_first_h1_and_lead(persp_md)
        purpose = _truncate(h1 or name)
        rel = persp_md.relative_to(root).as_posix()
        results.append(
            HarnessArtifact(
                kind="Perspectives",
                name=name,
                purpose=purpose,
                path=rel,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_onboarding(root: Path) -> list[HarnessArtifact]:
    onb_dir = root / ".claude" / "references" / "general" / "onboarding"
    if not onb_dir.is_dir():
        return []
    results: list[HarnessArtifact] = []
    for onb_md in sorted(onb_dir.glob("*.md")):
        h1, lead = _read_first_h1_and_lead(onb_md)
        purpose = _compose_h1_lead(h1, lead)
        rel = onb_md.relative_to(root).as_posix()
        results.append(
            HarnessArtifact(
                kind="Onboarding",
                name=onb_md.stem,
                purpose=purpose,
                path=rel,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_communication(root: Path) -> list[HarnessArtifact]:
    comm_dir = root / ".claude" / "references" / "general" / "communication"
    if not comm_dir.is_dir():
        return []
    results: list[HarnessArtifact] = []
    for comm_md in sorted(comm_dir.glob("*.md")):
        h1, lead = _read_first_h1_and_lead(comm_md)
        purpose = _compose_h1_lead(h1, lead)
        rel = comm_md.relative_to(root).as_posix()
        results.append(
            HarnessArtifact(
                kind="Communication",
                name=comm_md.stem,
                purpose=purpose,
                path=rel,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_templates(root: Path) -> list[HarnessArtifact]:
    tmpl_dir = root / ".claude" / "references" / "template"
    if not tmpl_dir.is_dir():
        return []
    results: list[HarnessArtifact] = []
    for tmpl_md in sorted(tmpl_dir.rglob("*.md")):
        h1, lead = _read_first_h1_and_lead(tmpl_md)
        purpose = _compose_h1_lead(h1, lead)
        rel = tmpl_md.relative_to(root).as_posix()
        # Distinguish top-level vs nested templates in the display name.
        nested = tmpl_md.relative_to(tmpl_dir).as_posix()
        name = nested[:-3] if nested.endswith(".md") else tmpl_md.stem
        results.append(
            HarnessArtifact(
                kind="Templates",
                name=name,
                purpose=purpose,
                path=rel,
            )
        )
    results.sort(key=lambda a: a.name)
    return results


def discover_all(root: Path) -> list[HarnessArtifact]:
    """Return the full list of harness artifacts across every kind."""
    artifacts: list[HarnessArtifact] = []
    artifacts.extend(discover_skills(root))
    artifacts.extend(discover_agents(root))
    artifacts.extend(discover_rules(root))
    artifacts.extend(discover_scripts(root))
    artifacts.extend(discover_tools(root))
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


def _render_scripts_section(artifacts: list[HarnessArtifact]) -> list[str]:
    """Render the ``## Scripts`` H2 with grouped H3 sub-tables.

    Collects every artifact whose ``kind`` is ``"Scripts"`` or ``"Tools"``
    (the 5 ``tools/*.py`` maintainer scripts participate alongside the
    harness scripts). Each row is assigned to exactly one of four buckets
    per the mapping in :func:`_assign_script_bucket`. Each bucket renders
    as an H3 sub-section containing a Markdown table with the new column
    shape

        ``| Name | Purpose | Invoked by | Lifecycle | Path | Mentioned in |``

    Rows inside each sub-section are alphabetized by ``name``. The
    ``Invoked by`` cell shows all roles (comma-space-separated, same
    spelling as the docstring header), not just the primary bucket role.

    After the four sub-sections, a fifth H3 sub-section ``Dual-role
    cross-reference`` lists every row whose role list has more than one
    entry. The sub-section is omitted entirely when no multi-role rows
    exist.
    """
    scripts_and_tools = [a for a in artifacts if a.kind in ("Scripts", "Tools")]
    by_bucket: dict[str, list[HarnessArtifact]] = {b: [] for b in _SCRIPT_BUCKETS}
    for art in scripts_and_tools:
        by_bucket[_assign_script_bucket(art)].append(art)

    lines: list[str] = []
    lines.append("## Scripts")
    lines.append("")
    for bucket in _SCRIPT_BUCKETS:
        entries = sorted(by_bucket[bucket], key=lambda a: a.name)
        lines.append(f"### {bucket}")
        lines.append("")
        if not entries:
            lines.append("_No entries._")
            lines.append("")
            continue
        lines.append("| Name | Purpose | Invoked by | Lifecycle | Path | Mentioned in |")
        lines.append("|---|---|---|---|---|---|")
        for a in entries:
            name_cell = _escape_pipes(a.name)
            purpose_cell = _escape_pipes(a.purpose)
            invoked_cell = _escape_pipes(a.invocation)
            lifecycle_cell = _escape_pipes(a.lifecycle)
            path_cell = f"`{a.path}`"
            mention_cell = _render_mention_cell(a.mentioned_in)
            lines.append(
                f"| {name_cell} | {purpose_cell} | {invoked_cell} "
                f"| {lifecycle_cell} | {path_cell} | {mention_cell} |"
            )
        lines.append("")

    # Dual-role cross-reference sub-section: one bullet per multi-role row.
    dual_role = sorted(
        (a for a in scripts_and_tools if len(_script_roles(a)) > 1),
        key=lambda a: a.name,
    )
    if dual_role:
        lines.append("### Dual-role cross-reference")
        lines.append("")
        for art in dual_role:
            primary = _assign_script_bucket(art)
            roles = _script_roles(art)
            # Identify the "other" buckets: buckets that the non-primary roles
            # would map into if they were the only role. Preserve role order
            # and skip duplicates.
            other_buckets: list[str] = []
            for role in roles:
                mapped = _ROLE_TO_BUCKET.get(role)
                if mapped is None or mapped == primary:
                    continue
                if mapped not in other_buckets:
                    other_buckets.append(mapped)
            # The "also classified as" text lists the remaining roles in the
            # order they appear in the docstring, minus the role that
            # matched the primary bucket (first-match-wins on primary).
            primary_role_consumed = False
            other_roles: list[str] = []
            for role in roles:
                if not primary_role_consumed and _ROLE_TO_BUCKET.get(role) == primary:
                    primary_role_consumed = True
                    continue
                other_roles.append(role)
            other_roles_text = ", ".join(other_roles) if other_roles else ""
            # Link target: first "other bucket" by role order. If a row has
            # roles mapping to multiple different buckets (e.g. check_docs.py
            # with roles {agent-invoked, hook-ci, user-cli} -> primary
            # User-invocable, others map to Skill- or agent-invoked AND Hook
            # and CI), render one "see" link per distinct other bucket.
            see_links = "; ".join(
                f"see [{bname}](#{_bucket_name_to_anchor(bname)})"
                for bname in other_buckets
            )
            lines.append(
                f"- **{art.name}** (primary: {primary}) -- also classified as: "
                f"{other_roles_text}; {see_links}"
            )
        lines.append("")
    return lines


def render_primary_table(artifacts: list[HarnessArtifact]) -> str:
    """Render the primary categorized table grouped by kind.

    The ``Scripts`` H2 is special-cased: it renders four H3 sub-sections
    bucketed by invocation role (plus a fifth ``Dual-role cross-reference``
    sub-section when applicable) via :func:`_render_scripts_section`. Every
    other kind uses the flat ``Name | Purpose | Path | Mentioned in`` table.
    """
    by_kind: dict[str, list[HarnessArtifact]] = {}
    for a in artifacts:
        by_kind.setdefault(a.kind, []).append(a)

    lines: list[str] = []
    for kind in KIND_ORDER:
        if kind == "Scripts":
            lines.extend(_render_scripts_section(artifacts))
            continue
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
    artifacts: list[HarnessArtifact],
    public_docs_root: str,
) -> str:
    """Render the user-facing surface secondary view."""
    mentioned = [a for a in artifacts if a.mentioned_in]
    mentioned.sort(key=lambda a: a.name)

    lines: list[str] = []
    lines.append("## User-facing surface")
    lines.append("")
    lines.append(
        f"Harness artifacts mentioned at least once in `{public_docs_root}`."
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


def render_harness_reference(
    artifacts: list[HarnessArtifact],
    public_docs_root: str,
    generated_at: str,
) -> str:
    """Compose the full Markdown document (preamble + primary + surface)."""
    # `last-reviewed:` is the YYYY-MM-DD prefix of `generated_at`; both the
    # ISO8601 form produced at runtime and the `--fixed-date` override start
    # with a date-only prefix, so the slice works for either shape.
    last_reviewed = generated_at[:10]
    preamble = (
        "---\n"
        "diataxis: reference\n"
        "freshness: release-bound\n"
        f"last-reviewed: {last_reviewed}\n"
        "---\n\n"
        "<!--\n"
        "This file is generated by .claude/skills/scripts/generate_harness_reference.py.\n"
        "Do not edit by hand. To regenerate:\n"
        "    python .claude/skills/scripts/generate_harness_reference.py \\\n"
        f"        --public-docs-root {public_docs_root} \\\n"
        f"        --output {public_docs_root}/reference/harness-reference.md\n"
        "-->\n\n"
        "# SEJA harness reference\n\n"
        f"Generated {generated_at} from seja-priv harness state.\n\n"
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


def _invoke_scanner(harness_root: Path, public_docs_root: Path) -> dict:
    if not SCANNER_SCRIPT.is_file():
        raise RuntimeError(
            f"scanner script not found at {SCANNER_SCRIPT}; "
            "either provide the public-docs scanner or pass --scan-output explicitly"
        )
    result = subprocess.run(
        [
            sys.executable,
            str(SCANNER_SCRIPT),
            "--harness-root",
            str(harness_root),
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
    artifacts: list[HarnessArtifact],
    scan_payload: dict,
) -> None:
    """Populate each artifact's `mentioned_in` list from the scanner payload."""
    harness_files = scan_payload.get("harness_files", {})
    for a in artifacts:
        entry = harness_files.get(a.path)
        if entry is not None:
            a.mentioned_in = list(entry.get("mentioned_in", []))
            a.mentioned_in = [m for m in a.mentioned_in if m != SELF_OUTPUT_REL]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _find_harness_root() -> Path:
    candidate = SCRIPTS_DIR
    while candidate != candidate.parent:
        if (candidate / ".claude").is_dir():
            return candidate
        candidate = candidate.parent
    return Path.cwd()


def _resolve_public_docs_root(harness_root: Path, explicit: str | None) -> Path | None:
    if explicit:
        return Path(explicit).resolve()
    in_repo = harness_root / "seja-public" / "docs"
    if in_repo.is_dir():
        return in_repo.resolve()
    sibling = harness_root.parent / "seja" / "docs"
    if sibling.is_dir():
        return sibling.resolve()
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the SEJA harness reference Markdown",
    )
    parser.add_argument("--harness-root", default=None)
    parser.add_argument("--public-docs-root", default=None)
    parser.add_argument("--scan-output", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fixed-date", default=None)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    harness_root = (
        Path(args.harness_root).resolve()
        if args.harness_root
        else _find_harness_root()
    )
    if not harness_root.is_dir():
        print(
            f"ERROR: harness root does not exist: {harness_root}",
            file=sys.stderr,
        )
        return 2

    public_docs_root = _resolve_public_docs_root(harness_root, args.public_docs_root)
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
        print(f"harness_root: {harness_root}", file=sys.stderr)
        print(f"public_docs_root: {public_docs_root}", file=sys.stderr)

    # Discover artifacts
    try:
        artifacts = discover_all(harness_root)
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
            scan_payload = _invoke_scanner(harness_root, public_docs_root)
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
    # harness root so rendered output is stable across machines; fall back
    # to the absolute path only when the public docs root lives outside the
    # harness tree (e.g., sibling `../seja/docs` checkout).
    if public_docs_root is not None:
        try:
            display_root = public_docs_root.relative_to(harness_root).as_posix()
        except ValueError:
            display_root = public_docs_root.as_posix()
    else:
        display_root = scan_payload.get("public_docs_root", "")

    rendered = render_harness_reference(artifacts, display_root, generated_at)

    # --check mode
    if args.check:
        # Precondition: every Scripts/Tools artifact must carry a valid
        # docstring header. Unannotated files (``invocation == "unspecified"``)
        # abort with a clear pointer to the convention doc -- this guards
        # against in-commit slippage where a newly-added script merges without
        # the two-line header. Invalid values (enum violations) are surfaced
        # separately below so operators can distinguish "missing entirely" from
        # "typo'd enum token".
        scripts_and_tools = [a for a in artifacts if a.kind in ("Scripts", "Tools")]
        unannotated = [a for a in scripts_and_tools if a.invocation == "unspecified"]
        if unannotated:
            print(
                "ERROR: Cannot tighten --check -- the following harness scripts "
                "are unannotated:",
                file=sys.stderr,
            )
            for a in unannotated:
                print(f"  {a.path}", file=sys.stderr)
            print(
                "Annotate them per .claude/references/general/script-header-convention.md, "
                "then rerun.",
                file=sys.stderr,
            )
            return 1
        # Enum-violation check: any script whose header parsed but failed
        # validation carries the sentinel ``invocation=lifecycle="invalid"``.
        # Emit one line per offender per field so operators see both at once.
        invalid_rows = [a for a in scripts_and_tools if a.invocation == "invalid"]
        if invalid_rows:
            for a in invalid_rows:
                print(
                    f"ERROR: {a.path} has invocation={a.invocation}",
                    file=sys.stderr,
                )
                print(
                    f"ERROR: {a.path} has lifecycle={a.lifecycle}",
                    file=sys.stderr,
                )
            return 1

        if not args.output or args.output == "-":
            if public_docs_root is None:
                print(
                    "ERROR: cannot default --output without --public-docs-root",
                    file=sys.stderr,
                )
                return 2
            output_path = (public_docs_root / "reference" / "harness-reference.md").resolve()
        else:
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
        #
        # The preamble carries a ``Generated <ISO8601>`` line that changes
        # on every invocation. When ``--check`` runs after preflight has
        # already spent a few seconds on earlier checks, the on-disk file's
        # timestamp lags the fresh render by one or more seconds -- producing
        # spurious DRIFT. Normalize the ``Generated ...`` line (and the
        # ``last-reviewed: YYYY-MM-DD`` line, which derives from the same
        # timestamp) before comparison so ``--check`` surfaces only
        # content-level drift, mirroring how ``check_docs.py`` sub-check 4
        # uses the on-disk timestamp when re-rendering for drift detection.
        def _strip_generated_stamps(s: str) -> str:
            s = s.replace("\r\n", "\n")
            s = re.sub(
                r"^Generated \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z",
                "Generated <timestamp>",
                s,
                count=1,
                flags=re.MULTILINE,
            )
            s = re.sub(
                r"^last-reviewed: \d{4}-\d{2}-\d{2}$",
                "last-reviewed: <date>",
                s,
                count=1,
                flags=re.MULTILINE,
            )
            return s

        if _strip_generated_stamps(on_disk) == _strip_generated_stamps(rendered):
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
        output_arg = str(public_docs_root / "reference" / "harness-reference.md")

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
