#!/usr/bin/env python3
# designer: When you want to see how the harness fits together -- which
#   skill invokes which script, which agent each skill delegates to,
#   which references a skill eager-loads -- I produce the call-graph
#   viewer you navigate in the docs: a filterable, draggable map of
#   every skill, agent, script, rule, and reference, with a side panel
#   that tells you in plain language what each node does for you.
"""
generate_call_graph.py -- Extract the harness's invocation/delegation topology.

Invocation: user-cli
Lifecycle: active

Walks .claude/ and .claude/references/ to discover 8 typed node classes (skill,
skill-internal, agent, script, rule, ref-general, ref-template, ref-project)
and extract 6+ edge types (invokes, delegates, orchestrates, dispatches-inline,
eager-load, lazy-load, imports) from SKILL.md regex patterns and Python AST
analysis. `skill-internal` nodes live under `.claude/skills/_internal/
<wrapper>/<mode>/SKILL.md` and represent Dispatch B inlined worker skills
(see `harness-governance.md` > Mode factoring pattern); `dispatches-inline`
edges link a wrapper skill to its internal workers. Emits:

- .claude/references/general/call-graph.json with deterministic sort (Step 1).
- seja-public/docs/concepts/call-graph.md with three filtered Mermaid overviews,
  per-skill call-tree drill-downs, reverse-index tables for scripts and agents,
  and a <details> text-only accessibility fallback (Step 2).
- seja-public/docs/concepts/call-graph.html + .css + .js -- interactive viewer
  scaffolding using Cytoscape.js from unpkg with SRI placeholders. Step 3
  emits the three-pane layout, pastel-palette node styling, and the default
  cose/cose-bilkent force-directed layout. Step 4 wires sidebar controls
  (filters, layout switcher, edge-label toggle, drag persistence, export,
  save-layout). Step 5 wires the right-anchored side panel: on node click,
  the drawer populates with type badge + name + clickable path + description
  rendered as mini-Markdown + incoming/outgoing edge lists; Pin, Close, Esc,
  and arrow-key navigation are supported; state persists via localStorage.

Node descriptions (Step 5) are sourced in priority order:

  1. quick-guide         -- for skills: body of `SKILL-quickguide.md` (sibling
     file in the skill directory), loaded via the shared `load_quickguide()`
     helper at `.claude/skills/scripts/load_quickguide.py`. Skills that
     lack a Quick Guide sibling return empty.
  2. designer-description -- for non-skills: explicit `designer_description`
     in Markdown frontmatter or `__designer_description__` / `# designer:`
     block in a Python file.
  3. developer-fallback  -- first H1 + lead (Markdown) or first non-blank
     line of the module docstring (Python). Surfaces a "Developer-oriented
     -- awaiting designer rewrite" badge in the side panel.
  4. none                -- empty description.

Exit codes: 0 success, 1 validation failure, 2 script error.

Usage
-----
    python .claude/skills/scripts/generate_call_graph.py [--verbose] [--fixed-date <ISO8601>] [--check]

Run from the repository root.
"""

# Rationale for design choices and historical context: see generate_call_graph-rationale.md in this directory.
from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import json
import re
import string
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Sibling-module import: both files live in .claude/skills/scripts/.
# When generate_call_graph.py is invoked directly, its parent directory is
# on sys.path automatically.
from load_quickguide import load_quickguide as _shared_load_quickguide

# -----------------------------------------------------------------------------
# Conditional-edge prose patterns (edge `when:` annotation)
# -----------------------------------------------------------------------------
#
# Edges gain an optional `when: "--<flag>"` annotation when a delegation is
# gated on a flag in SKILL.md prose. Accepted canonical patterns:
#
#   1. **<Mode> mode** (`--<flag>` flag): ... Launch the `<target>` ...
#   2. If `--<flag>` is present/passed, ... Launch the `<target>`
#   3. If the argument[s]? include[s]? `--<flag>`, ... <delegation>
#   4. When invoked with `--<flag>`, ... <delegation>
#   5. If `--<flag>` was provided, ... <delegation>
#
# Skill authors adding new conditional delegations should write prose that
# matches one of these patterns so the extractor picks up the condition.
# Detection is conservative -- unmatched prose emits an unannotated edge,
# matching today's union-graph behavior.
#
# Scope restriction: annotation attaches
# to existing edges only; does not fabricate edges outside the baseline
# extractor's scope. If a conditional-prose match resolves to a target name
# that has no pre-existing edge emitted by `extract_skill_edges` (e.g. a
# skill->skill candidate rejected by the `/skill-name` invocation-context
# heuristic), the match is silently skipped rather than coining a new edge.
# -----------------------------------------------------------------------------

CDN_URLS = [
    "https://unpkg.com/cytoscape@3.30.4/dist/cytoscape.min.js",
    "https://unpkg.com/layout-base@2.0.1/layout-base.js",
    "https://unpkg.com/cose-base@2.2.0/cose-base.js",
    "https://unpkg.com/cytoscape-fcose@2.2.0/cytoscape-fcose.js",
    "https://unpkg.com/webcola@3.4.0/WebCola/cola.min.js",
    "https://unpkg.com/cytoscape-cola@2.5.1/cytoscape-cola.js",
    "https://unpkg.com/cytoscape-svg@0.4.0/cytoscape-svg.js",
]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parents[2]

OUTPUT_JSON = REPO_ROOT / ".claude" / "references" / "general" / "call-graph.json"
OUTPUT_JSON_PUBLIC = REPO_ROOT / "seja-public" / "docs" / "concepts" / "call-graph.json"
OUTPUT_MD = REPO_ROOT / "seja-public" / "docs" / "concepts" / "call-graph.md"
OUTPUT_HTML = REPO_ROOT / "seja-public" / "docs" / "concepts" / "call-graph.html"
OUTPUT_CSS = REPO_ROOT / "seja-public" / "docs" / "concepts" / "call-graph.css"
OUTPUT_JS = REPO_ROOT / "seja-public" / "docs" / "concepts" / "call-graph.js"

# ---------------------------------------------------------------------------
# Mermaid palette (extends skill-map.mmd with lifecycle/script/agent/rule/ref-*)
# ---------------------------------------------------------------------------

CLASS_DEFS = {
    "planning":     "fill:#b8d5f2,stroke:#6da3d4,color:#1e3a5f",
    "analysis":     "fill:#d4efd4,stroke:#74b874,color:#2d5a2d",
    "code":         "fill:#fce6c8,stroke:#d9a66b,color:#6b3f1e",
    "utility":      "fill:#e6e6e6,stroke:#a8a8a8,color:#404040",
    "setup":        "fill:#e3d6f0,stroke:#9b7fc7,color:#4a2f6b",
    "lifecycle":    "fill:#f5e1d6,stroke:#c28b6a,color:#5c2e1b",
    # `skill_internal` (Dispatch B inlined worker) -- dotted border hints at
    # the non-user-facing nature; fill tint mirrors the neighboring `skill`
    # family so it reads as a skill sub-type rather than a fresh class.
    "skill_internal": "fill:#e8f0f9,stroke:#6da3d4,stroke-dasharray:3 2,color:#1e3a5f",
    "script":       "fill:#d5e3ef,stroke:#7c9ab3,color:#2a3e52",
    "agent":        "fill:#e6d5ed,stroke:#a082b5,color:#3e2852",
    "rule":         "fill:#f8e6a8,stroke:#c9aa4d,color:#5c4617",
    "ref_general":  "fill:#cfe3cf,stroke:#7fa87f,color:#2d4a2d",
    "ref_template": "fill:#d7cce8,stroke:#9687b5,color:#3e3566",
    "ref_project":  "fill:#efcccc,stroke:#b58282,color:#663535",
}

# Skill -> category mapping (matches generate_skill_map.py plus lifecycle).
SKILL_CATEGORY_MAP = {
    "/plan":          "planning",
    "/implement":     "planning",
    "/research":      "analysis",
    "/check":         "analysis",
    "/explain":       "analysis",
    "/communicate":   "utility",
    "/document":      "utility",
    "/help":          "utility",
    "/onboard":       "utility",
    "/pending":       "utility",
    "/qa-log":        "utility",
    "/reflect":       "utility",
    "/design":        "setup",
    "/seed":          "setup",
    "/seja-setup":    "setup",
    "/pre-skill":     "lifecycle",
    "/post-skill":    "lifecycle",
}

# Mermaid init directive -- mirror generate_skill_map.py so the two
# artifacts render with the same typography on GitHub.
MERMAID_INIT_DIRECTIVE = (
    "%%{init: {'theme': 'default', "
    "'themeVariables': {'fontFamily': 'system-ui, -apple-system, "
    "Segoe UI, sans-serif'}}}%%"
)

# Cap diagram edge rendering to keep Mermaid readable. JSON stays lossless.
MAX_EDGES_PER_OVERVIEW = 80

SKILLS_DIR = REPO_ROOT / ".claude" / "skills"
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
SCRIPTS_SUBDIR = REPO_ROOT / ".claude" / "skills" / "scripts"
RULES_DIR = REPO_ROOT / ".claude" / "rules"
REFS_GENERAL_DIR = REPO_ROOT / ".claude" / "references" / "general"
REFS_TEMPLATE_DIR = REPO_ROOT / ".claude" / "references" / "template"
REFS_PROJECT_DIR = REPO_ROOT / "project-design"

# Regex patterns.
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
# Matches any script invocation under .claude/skills/<dir>/script.py so that
# skills that co-locate their scripts (e.g. check/check_docs.py) are detected
# alongside the legacy scripts/ layout.
_SKILL_TO_SCRIPT_RE = re.compile(r"python\s+[.]?\.claude/skills/[^/\s]+/([\w.-]+\.py)")
_SKILL_TO_AGENT_RE = re.compile(
    r"subagent_type\s*[=:]\s*[\x22\x27`]?([A-Za-z][\w-]*)"
)
# Matches any explicit _references/<scope>/<path> or .claude/references/<scope>/<path>
# mention in prose or code. Scope must be one of the three known scopes; extension
# must be a text format. The old _references/ prefix is still matched for
# backward-compat with legacy doc prose that has not been updated yet.
_REF_READ_RE = re.compile(
    r"(?:_references|\.claude/references)/(general|template|project)/([A-Za-z0-9_./-]+\.(?:md|json|ya?ml))"
)
# Known skill names; used to bound the orchestrates regex and avoid matching
# arbitrary forward-slash tokens in prose. Kept as a set literal so edits stay
# explicit -- a novel skill name that does not appear here simply will not be
# linked.
KNOWN_SKILL_NAMES = {
    "pre-skill",
    "post-skill",
    "plan",
    "implement",
    "research",
    "check",
    "document",
    "explain",
    "help",
    "communicate",
    "onboard",
    "reflect",
    "qa-log",
    "pending",
    "seed",
    "design",
    "seja-setup",
}
_SKILL_TO_SKILL_RE = re.compile(
    r"/(" + "|".join(sorted(KNOWN_SKILL_NAMES, key=len, reverse=True)) + r")\b"
)

# Dispatch B inline-worker reference regex. Matches the
# canonical path shape a wrapper's `## Dispatch` section uses to point at an
# internal worker:  `.claude/skills/_internal/<wrapper>/<mode>/SKILL.md`.
# The extractor emits a `dispatches-inline` edge from the enclosing wrapper
# `skill:<wrapper>` to the internal `skill-internal:<wrapper>/<mode>` node
# for every unique (wrapper, mode) match.
_DISPATCHES_INLINE_RE = re.compile(
    r"\.claude/skills/_internal/([a-z][a-z0-9_-]*)/([a-z][a-z0-9_-]*)/SKILL\.md"
)

# Words that, when they appear on the same line before a /skill token, mark the
# token as an invocation rather than a mention. The preceding-character check
# (space) is the primary gate; this list is a secondary confidence signal used
# when the match is at or near the line start.
_INVOCATION_CONTEXT_WORDS = ("run", "invoke", "call", "launch", "via", "shell")

# ---------------------------------------------------------------------------
# Conditional-edge prose patterns
# ---------------------------------------------------------------------------
#
# Each entry compiles to a regex capturing the flag text (without leading
# `--`) in group "flag". The extractor walks each SKILL.md body once per
# pattern and, for every match, inspects the ~200 characters following the
# match for a backtick-quoted target name (agent / script / skill) to attach
# `when: "--<flag>"` to.
#
# See the top-of-file comment block for the canonical pattern contract.

# Size of the look-ahead window scanned after a conditional-prose match
# for a backtick-quoted delegation target.
_CONDITIONAL_CONTEXT_WINDOW = 400

# Flag text is whatever appears after `--` inside backticks. Allow word
# characters, hyphens, and a single space segment (to cover multi-word flags
# like `--framing metacomm` or `--depth deep`). Anchored inside backticks so
# arbitrary inline code does not drift into the capture.
_FLAG_TOKEN = r"--(?P<flag>[A-Za-z][\w-]*(?: [A-Za-z][\w-]*)?)"

CONDITIONAL_PROSE_PATTERNS: list[re.Pattern[str]] = [
    # Pattern 1: `**<Mode> mode** (`--<flag>`[ flag]): ...` or
    # `**<Mode>** (`--<flag>`): ...`
    # The closing parenthesis may directly follow the backtick (`(\`--X\`)`)
    # or be preceded by the literal word "flag" (`(\`--X\` flag)`). The
    # `(?!(?:no|without|absent|omit|omitted|missing)\s+`)` negative
    # look-ahead rejects flag-absence descriptors (e.g. "no `--deep` flag",
    # "without `--deep`", "absent `--deep`", "omit `--deep`", "omitted
    # `--deep`", "missing `--deep`") where a skill describes its *default*
    # mode as the absence of the flag (e.g. `/research`'s Standard mode).
    re.compile(
        r"\*\*[^*\n]+?\*\*\s*\((?!(?:no|without|absent|omit|omitted|missing)\s+`)`"
        + _FLAG_TOKEN
        + r"`(?:\s+flag)?\)",
    ),
    # Pattern 2: "If `--<flag>` is present/passed, ..."
    re.compile(
        r"If\s+`" + _FLAG_TOKEN + r"`\s+is\s+(?:present|passed)\b",
    ),
    # Pattern 3: "If the argument[s] include[s] `--<flag>`, ..."
    re.compile(
        r"If\s+the\s+arguments?\s+includes?\s+`" + _FLAG_TOKEN + r"`",
    ),
    # Pattern 4: "When invoked with `--<flag>`, ..."
    re.compile(
        r"When\s+invoked\s+with\s+`" + _FLAG_TOKEN + r"`",
    ),
    # Pattern 5: "If `--<flag>` was provided, ..."
    re.compile(
        r"If\s+`" + _FLAG_TOKEN + r"`\s+was\s+provided\b",
    ),
]

# Python stdlib module names (partial -- only the ones that collide with our
# script stems). We want to skip these when resolving script->script imports.
_STDLIB_SKIPLIST = {
    "os",
    "sys",
    "re",
    "json",
    "ast",
    "pathlib",
    "datetime",
    "argparse",
    "subprocess",
    "shutil",
    "typing",
    "dataclasses",
    "collections",
    "functools",
    "itertools",
    "string",
    "hashlib",
    "io",
    "textwrap",
    "time",
    "urllib",
    "tempfile",
    "traceback",
    "csv",
    "glob",
    "math",
    "random",
    "unittest",
    "pytest",
    "enum",
    "copy",
    "warnings",
    "logging",
}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _read_text(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""
    # Normalize line endings so downstream regex splits on "\n\n" paragraph
    # boundaries (e.g. in _annotate_conditional_edges) work uniformly on
    # Windows-authored (CRLF) or old-Mac-authored (CR) files.
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _strip_frontmatter(text: str) -> tuple[str, str]:
    """Return (frontmatter_text_or_empty, body_without_frontmatter)."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return "", text
    return match.group(1), text[match.end():].lstrip("\n")


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


# ---------------------------------------------------------------------------
# Frontmatter reference-list parsing (stdlib YAML subset)
# ---------------------------------------------------------------------------


def _parse_ref_lists(fm_text: str) -> tuple[list[str], list[str]]:
    """Extract (eager_references, references) from a SKILL.md frontmatter block.

    The frontmatter uses YAML shape:
        metadata:
          eager_references:
            - project/foo.md
          references:
            - project/foo.md
            - general/bar.md

    We parse only the shape SEJA actually uses: a two-space-indented
    `metadata:` map whose children are four-space-indented, with list items
    starting with `    -`. This is stricter than a real YAML parser but avoids
    adding PyYAML.
    """
    eager: list[str] = []
    refs: list[str] = []

    lines = fm_text.splitlines()
    current_key: str | None = None
    # Track whether we are inside `metadata:` top-level block.
    in_metadata = False
    metadata_indent = None

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Top-level key detection. Top-level lines are at column 0.
        if line and not line.startswith(" "):
            key = line.rstrip(":").strip()
            if key == "metadata":
                in_metadata = True
                metadata_indent = 2
                current_key = None
            else:
                in_metadata = False
                current_key = None
            continue

        if not in_metadata:
            continue

        # Inside metadata: detect eager_references / references sub-keys at
        # indent 2, and list items at indent 4.
        if line.startswith("  ") and not line.startswith("   "):
            # Exactly 2-space indent: a metadata child key.
            sub_key = line.strip().rstrip(":")
            if sub_key in ("eager_references", "references"):
                current_key = sub_key
            else:
                current_key = None
            continue

        # List items under eager_references / references. Match a hyphen
        # after any indentation of 3+ spaces.
        if current_key in ("eager_references", "references"):
            m = re.match(r"^\s{3,}-\s+(.+?)\s*$", line)
            if m:
                value = m.group(1).strip().strip('"').strip("'")
                if current_key == "eager_references":
                    eager.append(value)
                else:
                    refs.append(value)

    return eager, refs


def _parse_skill_user_invocable(fm_text: str) -> bool:
    """Extract top-level ``user-invocable`` from SKILL.md frontmatter.

    Defaults to True when the key is absent or malformed. The field is
    deliberately top-level, not under ``metadata``.
    """
    for line in fm_text.splitlines():
        if line.startswith((" ", "\t")):
            continue
        match = re.match(
            r"^user-invocable\s*:\s*(true|false)\s*$",
            line.strip(),
            flags=re.IGNORECASE,
        )
        if match:
            return match.group(1).lower() == "true"
    return True


def _parse_script_invocation_modes(script_text: str) -> set[str]:
    """Parse a script docstring ``Invocation:`` line into normalized modes.

    Example:
      ``Invocation: skill-invoked, user-cli`` -> {"skill-invoked", "user-cli"}
    """
    for raw_line in script_text.splitlines():
        line = raw_line.strip()
        m = re.match(r"^Invocation\s*:\s*(.+)$", line, flags=re.IGNORECASE)
        if not m:
            continue
        raw_modes = m.group(1)
        modes: set[str] = set()
        for part in raw_modes.split(","):
            mode = part.strip().lower()
            if mode:
                modes.add(mode)
        return modes
    return set()


# ---------------------------------------------------------------------------
# Description extraction (Step 5)
# ---------------------------------------------------------------------------
#
# Each node carries a `description` and `description_source`. Sources in
# priority order:
#   1. quick-guide         -- skills: body of `SKILL-quickguide.md` (sibling
#      file in the skill directory), read via the shared `load_quickguide()`
#      helper. The designer-facing narrative lives in the sibling;
#      the `## Quick Guide` H2 no longer appears in SKILL.md.
#   2. designer-description -- non-skills: explicit `designer_description`
#      in Markdown frontmatter or a `__designer_description__` / `# designer:`
#      block in Python files.
#   3. developer-fallback  -- first H1 + lead sentence (Markdown) or first
#      non-blank line of the module docstring (Python).
#   4. none                -- nothing extractable.

def _extract_quick_guide(skill_dir: Path) -> str:
    """Return the Quick Guide body for the skill at ``skill_dir``, or empty.

    Delegates to the shared loader at ``load_quickguide.py``. Returns an
    empty string when the sibling file is missing (the call graph treats
    empty descriptions as "developer-fallback" candidates downstream).
    """
    body = _shared_load_quickguide(skill_dir)
    return body.strip() if body else ""


def _extract_first_h1_and_lead(body: str) -> tuple[str, str]:
    """Return (h1-text, first-sentence-of-first-paragraph) for Markdown body.

    Mirrors the pattern from generate_harness_reference.py. Frontmatter
    must already be stripped.
    """
    h1_match = _H1_RE.search(body)
    if not h1_match:
        return "", ""
    h1 = h1_match.group(1).strip()
    after = body[h1_match.end():]
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
    if paragraph:
        m = re.match(r"(.+?[.!?])(?:\s|$)", paragraph)
        lead = m.group(1) if m else paragraph
    else:
        lead = ""
    return h1, lead


def _parse_frontmatter_designer_description(fm_text: str) -> str:
    """Extract the `designer_description` field value from frontmatter.

    Accepts either an inline string (quoted or bare) or a block-style
    ``|``/``>`` multi-line scalar. Returns empty string if absent.
    """
    if not fm_text:
        return ""
    lines = fm_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^designer_description\s*:\s*(.*)$", line)
        if not m:
            i += 1
            continue
        rest = m.group(1).rstrip()
        # Block-style: designer_description: | or >
        if rest in ("|", ">", "|-", ">-", "|+", ">+"):
            block: list[str] = []
            i += 1
            # The block body is indented deeper than the key (column 0).
            # Accept any indent > 0; stop on dedent to column 0 or new key.
            indent = None
            while i < len(lines):
                bl = lines[i]
                if bl.strip() == "":
                    block.append("")
                    i += 1
                    continue
                # Determine base indent from first non-empty block line.
                if indent is None:
                    stripped_left = bl.lstrip(" ")
                    indent = len(bl) - len(stripped_left)
                    if indent == 0:
                        # Not an indented block body -- bail.
                        break
                    block.append(bl[indent:])
                    i += 1
                    continue
                leading_ws = len(bl) - len(bl.lstrip(" "))
                if leading_ws < indent:
                    break
                block.append(bl[indent:])
                i += 1
            # For `|` preserve newlines; for `>` fold. We only need a plain
            # string -- go with preserving newlines.
            return "\n".join(block).strip()
        # Inline string. Strip quotes if present.
        value = rest.strip()
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        return value.strip()
    return ""


def _extract_python_designer_description(text: str) -> str:
    """Look for a designer_description in a Python source file.

    Three accepted shapes:
      (a) A top-of-file comment block where one or more consecutive lines
          begin with `# designer: ...` (first line) or `#     ...` (cont).
      (b) A module-level assignment ``__designer_description__ = "..."``
          or ``__designer_description__ = '''...'''``.
    Returns empty string if neither is present.
    """
    # (a) Comment block -- scan the first ~40 lines before any non-comment
    # non-blank line.
    lines = text.splitlines()
    comment_block: list[str] = []
    started = False
    for raw in lines[:60]:
        s = raw.strip()
        if s.startswith("# designer:"):
            started = True
            comment_block.append(s[len("# designer:"):].strip())
            continue
        if started and s.startswith("#"):
            comment_block.append(s.lstrip("#").strip())
            continue
        if started:
            break
        if not s or s.startswith("#!") or s.startswith("#"):
            # Keep scanning through initial comments / shebang until we find
            # `# designer:` or hit code.
            continue
        # Hit code before `# designer:` -- no match via (a).
        break
    if comment_block:
        return "\n".join(x for x in comment_block if x is not None).strip()

    # (b) Module-level assignment via AST.
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return ""
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and \
                        target.id == "__designer_description__":
                    value = node.value
                    if isinstance(value, ast.Constant) and isinstance(
                            value.value, str):
                        return value.value.strip()
    return ""


def _extract_python_docstring_lead(text: str) -> str:
    """Return the first non-blank line of the module docstring.

    Strips a redundant `<script>.py -- ` prefix (seen across SEJA scripts).
    Returns empty string if there is no docstring.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return ""
    doc = ast.get_docstring(tree)
    if not doc:
        return ""
    for raw in doc.splitlines():
        line = raw.strip()
        if line:
            # Strip "scriptname.py -- " prefix if present.
            m = re.match(r"^[A-Za-z0-9_]+\.py\s*--\s*(.+)$", line)
            if m:
                return m.group(1).strip()
            return line
    return ""


def _extract_python_docstring_full(text: str) -> str:
    """Return the full module docstring with the `<name>.py -- ` prefix
    stripped from the first line.

    Preserves internal line breaks and blank lines so the side panel can
    render the developer-facing documentation (usage, flags, notes)
    verbatim.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return ""
    doc = ast.get_docstring(tree)
    if not doc:
        return ""
    lines = doc.splitlines()
    # Strip the leading `<name>.py -- ` on the first non-blank line.
    for i, raw in enumerate(lines):
        if raw.strip():
            m = re.match(r"^[A-Za-z0-9_]+\.py\s*--\s*(.+)$", raw.strip())
            if m:
                lines[i] = m.group(1).strip()
            break
    return "\n".join(lines).strip()


def compute_node_description(node: dict) -> tuple[str, str]:
    """Return (description, description_source) for a discovered node.

    See the priority comment at the top of this section.
    """
    path = REPO_ROOT / node["path"]
    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return "", "none"

    ntype = node["type"]

    if ntype == "skill":
        _fm, body = _strip_frontmatter(text)
        qg = _extract_quick_guide(path.parent)
        if qg:
            return qg, "quick-guide"
        # Fallback: H1 + lead.
        h1, lead = _extract_first_h1_and_lead(body)
        combined = (h1 + ("\n\n" + lead if lead else "")).strip() if h1 else lead
        if combined:
            return combined, "developer-fallback"
        return "", "none"

    # Non-skill: prefer designer_description, then developer-fallback.
    if path.suffix == ".md":
        fm_text, body = _strip_frontmatter(text)
        dd = _parse_frontmatter_designer_description(fm_text)
        if dd:
            return dd, "designer-description"
        h1, lead = _extract_first_h1_and_lead(body)
        combined = (h1 + ("\n\n" + lead if lead else "")).strip() if h1 else lead
        if combined:
            return combined, "developer-fallback"
        return "", "none"

    if path.suffix == ".py":
        dd = _extract_python_designer_description(text)
        if dd:
            return dd, "designer-description"
        # Scripts surface their full top-of-file docstring on the side
        # panel so developers can read the block-comment documentation
        # (usage, flags, exit codes) without leaving the graph viewer.
        full = _extract_python_docstring_full(text)
        if full:
            return full, "developer-fallback"
        lead = _extract_python_docstring_lead(text)
        if lead:
            return lead, "developer-fallback"
        return "", "none"

    # ref-template entries include .yaml / .json etc. Try to grab the first
    # non-blank line as a crude fallback.
    for raw in text.splitlines():
        s = raw.strip()
        if s and not s.startswith("#"):
            return s[:200], "developer-fallback"
    return "", "none"


# ---------------------------------------------------------------------------
# Node discovery
# ---------------------------------------------------------------------------


def discover_skills() -> list[dict]:
    if not SKILLS_DIR.is_dir():
        return []
    results: list[dict] = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        # Skip private/underscore-prefixed roots (e.g. `_internal/`) -- those
        # are discovered separately by `discover_internal_skills()` as a
        # distinct node sub-type and must not pollute the user-facing skill
        # enumeration.
        if skill_dir.name.startswith("_"):
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        fm_text, _body = _strip_frontmatter(_read_text(skill_md))
        name = skill_dir.name
        results.append({
            "id": f"skill:{name}",
            "type": "skill",
            "label": f"/{name}",
            "path": _rel(skill_md),
            "user_invocable": _parse_skill_user_invocable(fm_text),
        })
    return results


def discover_internal_skills() -> list[dict]:
    """Discover inlined internal worker skills under `_internal/<wrapper>/<mode>/SKILL.md`.

    These are Dispatch B targets (see `harness-governance.md` > Mode factoring
    pattern): separate `SKILL.md` files that a wrapper reads inline via the
    Read tool. They are NOT user-invocable and live outside the user-facing
    skill enumeration. Emitted as a distinct node sub-type
    (`type="skill-internal"`) with IDs shaped `skill-internal:<wrapper>/<mode>`.

    Only paths of the exact shape
    `.claude/skills/_internal/<wrapper>/<mode>/SKILL.md` are accepted -- two
    intermediate directory levels, no shallower (a bare
    `_internal/<name>/SKILL.md`) and no deeper nesting.
    """
    internal_root = SKILLS_DIR / "_internal"
    if not internal_root.is_dir():
        return []
    results: list[dict] = []
    for skill_md in sorted(internal_root.rglob("SKILL.md")):
        # Relative path inside `_internal/` -- expect exactly
        # `<wrapper>/<mode>/SKILL.md` (three parts, SKILL.md last).
        rel_parts = skill_md.relative_to(internal_root).parts
        if len(rel_parts) != 3 or rel_parts[-1] != "SKILL.md":
            continue
        wrapper, mode, _ = rel_parts
        results.append({
            "id": f"skill-internal:{wrapper}/{mode}",
            "type": "skill-internal",
            "label": f"_internal/{wrapper}/{mode}",
            "path": _rel(skill_md),
        })
    return results


def discover_agents() -> list[dict]:
    if not AGENTS_DIR.is_dir():
        return []
    results: list[dict] = []
    for agent_md in sorted(AGENTS_DIR.glob("*.md")):
        name = agent_md.stem
        results.append({
            "id": f"agent:{name}",
            "type": "agent",
            "label": name,
            "path": _rel(agent_md),
        })
    return results


def discover_scripts() -> list[dict]:
  if not SCRIPTS_SUBDIR.is_dir():
    return []

  # Collect scripts from scripts/ and co-located skill subdirectories
  candidates: list[Path] = list(SCRIPTS_SUBDIR.glob("*.py"))
  for skill_dir in sorted(SKILLS_DIR.iterdir()):
    if skill_dir.is_dir() and skill_dir.name not in ("scripts", "_internal"):
      candidates.extend(skill_dir.glob("*.py"))

  results: list[dict] = []
  for script in sorted(candidates):
    if script.name == "__init__.py":
      continue
    try:
      rel_parts = script.relative_to(SCRIPTS_SUBDIR).parts
    except ValueError:
      rel_parts = ()
    if "priv" in rel_parts or "tests" in rel_parts:
      continue

    # Keep script labels identical to their on-disk filenames. Earlier
    # revisions prefixed user-cli-only scripts with "user-" in the graph UI,
    # which created synthetic names that looked like real files.
    label = script.name

    results.append({
      "id": f"script:{script.name}",
      "type": "script",
      "label": label,
      "path": _rel(script),
    })

  return results


def discover_rules() -> list[dict]:
    if not RULES_DIR.is_dir():
        return []
    results: list[dict] = []
    for rule_md in sorted(RULES_DIR.glob("*.md")):
        stem = rule_md.stem
        results.append({
            "id": f"rule:{stem}",
            "type": "rule",
            "label": stem,
            "path": _rel(rule_md),
        })
    return results


def discover_refs(
    root: Path,
    node_type: str,
    base_key: str,
) -> list[dict]:
    """Walk `root` recursively and emit ref-* nodes.

    `node_type` is the emitted `type` field (e.g. `ref-general`).
    `base_key` is the id prefix before the relative path (e.g. `ref-general`).
    For ref-general we accept only .md files; for ref-template / ref-project we
    accept any file extension (templates include .yaml, .json, .yml).
    """
    if not root.is_dir():
        return []
    results: list[dict] = []
    accept_any_ext = node_type in ("ref-template", "ref-project")
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if not accept_any_ext and path.suffix != ".md":
            continue
        rel_from_base = path.relative_to(root).as_posix()
        node_id = f"{base_key}:{rel_from_base}"
        results.append({
            "id": node_id,
            "type": node_type,
            "label": path.stem if path.suffix == ".md" else path.name,
            "path": _rel(path),
        })
    return results


def discover_all_nodes() -> list[dict]:
    nodes: list[dict] = []
    nodes.extend(discover_skills())
    nodes.extend(discover_internal_skills())
    nodes.extend(discover_agents())
    nodes.extend(discover_scripts())
    nodes.extend(discover_rules())
    nodes.extend(discover_refs(REFS_GENERAL_DIR, "ref-general", "ref-general"))
    nodes.extend(discover_refs(REFS_TEMPLATE_DIR, "ref-template", "ref-template"))
    nodes.extend(discover_refs(REFS_PROJECT_DIR, "ref-project", "ref-project"))
    return nodes


# ---------------------------------------------------------------------------
# Edge extraction -- skill body
# ---------------------------------------------------------------------------


def _build_node_index(nodes: list[dict]) -> dict[str, dict]:
    return {n["id"]: n for n in nodes}


def _resolve_ref_entry(entry: str, nodes: list[dict]) -> str | None:
    """Map a frontmatter reference entry (e.g. 'general/foo.md') to a node id.

    Try ref-general first, then ref-template, then ref-project, matching on
    the node's `path` field's tail after `_references/`.
    """
    entry = entry.strip().lstrip("./")
    if not entry:
        return None
    # Direct id candidates -- the cheap path.
    candidates = [
        f"ref-general:{entry}" if entry.startswith(("review-perspectives/", "onboarding/", "communication/")) or "/" not in entry else f"ref-general:{entry.split('/', 1)[1]}" if entry.startswith("general/") else None,
    ]
    # Fallback: scan nodes whose path ends with ".claude/references/<entry>" or
    # the legacy "_references/<entry>" form (for backward-compat with old prose).
    suffix_new = f".claude/references/{entry}"
    suffix_old = f"_references/{entry}"
    for node in nodes:
        if node["path"].endswith(suffix_new) or node["path"].endswith(suffix_old):
            return node["id"]
    # Also try if entry already carried a full prefix like "general/foo.md".
    if entry.startswith("general/"):
        tail = entry[len("general/"):]
        for node in nodes:
            if node["type"] == "ref-general" and node["id"] == f"ref-general:{tail}":
                return node["id"]
    if entry.startswith("template/"):
        tail = entry[len("template/"):]
        for node in nodes:
            if node["type"] == "ref-template" and node["id"] == f"ref-template:{tail}":
                return node["id"]
    if entry.startswith("project/"):
        tail = entry[len("project/"):]
        for node in nodes:
            if node["type"] == "ref-project" and node["id"] == f"ref-project:{tail}":
                return node["id"]
    _ = candidates  # keep the linter quiet; retained for clarity of intent.
    return None


def _is_invocation_context(line: str, match_start_in_line: int) -> bool:
    """Return True when a /skill token on a line looks like an invocation.

    Heuristic: the preceding non-whitespace word on the same line is one of
    the invocation verbs, or the match is preceded by a simple space. Plain
    mentions ("the /plan skill") should not count -- the preceding word
    "the" is not in the verb list. Match at column 0 is treated as prose
    context and rejected.
    """
    if match_start_in_line == 0:
        return False
    prev_char = line[match_start_in_line - 1]
    if prev_char != " ":
        return False
    # Examine the word immediately before the /.
    before = line[:match_start_in_line].rstrip().split()
    if not before:
        return False
    prev_word = before[-1].lower().strip(".,;:()`*")
    return prev_word in _INVOCATION_CONTEXT_WORDS


def _annotate_conditional_edges(
    body: str,
    source_id: str,
    edges: list[dict],
    nodes: list[dict],
) -> None:
    """Scan `body` for conditional-prose patterns and annotate matching edges.

    For each CONDITIONAL_PROSE_PATTERNS match, look inside the next
    ``_CONDITIONAL_CONTEXT_WINDOW`` characters for a backtick-quoted name
    that resolves to a known node id (agent, script, or skill) reachable
    from ``source_id``. If such a target exists AND the baseline extractor
    already emitted an edge for that (source, type, target), attach
    ``when: "--<flag>"`` to that existing edge (first-match-wins -- do not
    overwrite an existing ``when``).

    **Scope restriction**: conditional
    annotation attaches to existing edges only; it does NOT fabricate edges
    outside the baseline extractor's scope. If a prose match resolves to a
    target that the baseline extractor rejected (e.g. a skill->skill
    `orchestrates` candidate without an invocation-context verb), the match
    is silently skipped. Conditional detection is additive metadata on the
    baseline edge set, not a second extraction pass.

    If a pattern fires but no target name in the window resolves to an
    existing node, the match is silently skipped (prefer false negatives).
    Conditional detection never removes, reclassifies, or creates edges.
    """
    # Build lookup sets for target-name resolution. Keep agent / script /
    # skill only -- conditional `when:` only annotates delegation /
    # orchestration / invocation edges, not reference loads.
    agent_ids = {n["id"] for n in nodes if n["type"] == "agent"}
    script_ids = {n["id"] for n in nodes if n["type"] == "script"}
    skill_ids = {n["id"] for n in nodes if n["type"] == "skill"}

    agent_name_to_id = {nid.split(":", 1)[1]: nid for nid in agent_ids}
    # Script ids already encode the filename (e.g., `script:foo.py`); accept
    # both bare stems and full filenames in backticks.
    script_filename_to_id = {nid.split(":", 1)[1]: nid for nid in script_ids}
    script_stem_to_id = {
        Path(fn).stem: nid for fn, nid in script_filename_to_id.items()
    }
    skill_name_to_id = {nid.split(":", 1)[1]: nid for nid in skill_ids}

    # Cache an edge-lookup dict: (source, type, target) -> edge.
    edge_index: dict[tuple[str, str, str], dict] = {
        (e["source"], e["type"], e["target"]): e for e in edges
    }

    def _resolve_target_in_window(window: str) -> tuple[str, str] | None:
        """Return (target_id, edge_type) for the first backtick-quoted name
        in ``window`` that resolves to a known agent / script / skill.

        Edge-type priority follows the name's node class:
          - agent  -> delegates
          - script -> invokes
          - skill  -> orchestrates
        """
        for m in re.finditer(r"`([A-Za-z0-9][\w\-./]*)`", window):
            name = m.group(1)
            if name in agent_name_to_id:
                return agent_name_to_id[name], "delegates"
            if name in script_filename_to_id:
                return script_filename_to_id[name], "invokes"
            if name in script_stem_to_id:
                return script_stem_to_id[name], "invokes"
            if name in skill_name_to_id and skill_name_to_id[name] != source_id:
                return skill_name_to_id[name], "orchestrates"
        return None

    for pattern in CONDITIONAL_PROSE_PATTERNS:
        for match in pattern.finditer(body):
            flag = match.group("flag")
            when_value = f"--{flag}"
            window_start = match.end()
            window_end = window_start + _CONDITIONAL_CONTEXT_WINDOW
            window = body[window_start:window_end]
            # Constrain the window to the current paragraph. The detection
            # contract is "delegation in the same paragraph", not "anywhere
            # within N characters". A blank-line boundary (double newline)
            # terminates the paragraph; this prevents a `--browse` pattern
            # high on the page from absorbing an unrelated backtick-quoted
            # node name several paragraphs down.
            para_end = window.find("\n\n")
            if para_end != -1:
                window = window[:para_end]
            resolved = _resolve_target_in_window(window)
            if resolved is None:
                continue
            target_id, edge_type = resolved
            key = (source_id, edge_type, target_id)
            existing = edge_index.get(key)
            if existing is None:
                # Scope restriction: do
                # NOT fabricate edges from conditional prose. The baseline
                # extractor's invocation-context heuristics (e.g. the
                # `/skill-name` anchor + invocation verb for orchestrates)
                # are load-bearing; bypassing them via a `target-name`
                # backtick resolver can coin edges that were intentionally
                # omitted. If the baseline did not emit an edge, the
                # conditional match is still detectable as prose but not
                # annotated.
                continue
            # First-match-wins: do not overwrite a previously set `when`.
            if "when" not in existing:
                existing["when"] = when_value


def extract_skill_edges(
    skill_path: Path,
    nodes: list[dict],
    warnings: list[str],
  source_id: str | None = None,
) -> list[dict]:
    """Extract all outgoing edges from a single SKILL.md.

    Returns a list of edge dicts. `nodes` is the discovered node set used to
    validate targets. Unresolved references are appended to `warnings`.
    """
    text = _read_text(skill_path)
    if not text:
        return []
    fm_text, body = _strip_frontmatter(text)
    if source_id is None:
      # User-facing skills live under `.claude/skills/<name>/SKILL.md`.
      # Internal workers may pass an explicit `source_id`.
      skill_name = skill_path.parent.name
      source_id = f"skill:{skill_name}"
    else:
      # Keep the existing self-orchestrate guard semantics for `/skill`
      # tokens by deriving a best-effort local name from the provided id.
      skill_name = source_id.split(":", 1)[1]

    node_ids = {n["id"] for n in nodes}
    edges: list[dict] = []

    # Skill -> script edges.
    for match in _SKILL_TO_SCRIPT_RE.finditer(body):
        target = f"script:{match.group(1)}"
        if target in node_ids:
            edges.append({
                "source": source_id,
                "target": target,
                "type": "invokes",
                "label": "",
            })

    # Skill -> agent edges. Validate against discovered agent set.
    agent_ids = {n["id"] for n in nodes if n["type"] == "agent"}
    delegated: set[str] = set()
    for match in _SKILL_TO_AGENT_RE.finditer(body):
        agent_name = match.group(1)
        target = f"agent:{agent_name}"
        if target in agent_ids and target not in delegated:
            edges.append({
                "source": source_id,
                "target": target,
                "type": "delegates",
                "label": "",
            })
            delegated.add(target)

    # Additional delegation patterns commonly used in SEJA skills that
    # the subagent_type regex misses:
    #   (1) `Launch the `<agent-name>` agent` -- no subagent_type= at all
    #       (used by /check for code-reviewer, /implement for test-runner,
    #       etc.).
    #   (2) `using the prompt from `.claude/agents/<agent-name>.md`` -- used
    #       by generator agents (/onboard, /communicate, /document)
    #       that delegate via a `general-purpose` subagent with a named
    #       prompt file.
    #   (3) `Launch ... `<agent-name>` ...` without the explicit word `agent`
    #       after the backtick target (e.g. table rows that chain agents with
    #       "AND").
    #   (4) `Agent tool call referencing <agent-name>` -- unquoted agent name
    #       in an Agent-tool context (e.g. a compact Dispatch A dispatch block
    #       that names the agent without backtick-quoting it).
    agent_names = [
        n["id"].split(":", 1)[1] for n in nodes if n["type"] == "agent"
    ]
    for agent_name in agent_names:
        target = f"agent:{agent_name}"
        if target in delegated:
            continue
        escaped = re.escape(agent_name)
        # Pattern 1: backtick-quoted name followed by the word "agent".
        pat_launch = re.compile(
            r"`" + escaped + r"`\s+agent\b",
        )
        # Pattern 2: explicit `.claude/agents/<name>.md` path reference.
        pat_path = re.compile(
            r"\.claude/agents/" + escaped + r"\.md\b",
        )
        # Pattern 3: launch verb appears shortly before a backtick-quoted
        # agent token in the same sentence/line.
        pat_launch_verb_name = re.compile(
          r"\bLaunch\b[^\n]{0,220}`" + escaped + r"`",
          flags=re.IGNORECASE,
        )
        # Pattern 4: "Agent tool" context with the unquoted agent name on the
        # same line.  Catches dispatch blocks of the form "Agent tool call
        # referencing explanation-generator" where the agent name is not
        # backtick-quoted but the phrase "Agent tool" is present.
        # NOTE: may produce spurious edges if a line mentions "Agent tool" in
        # explanatory prose AND an agent name in the same sentence (e.g., a
        # comparison comment).  Guard by ensuring agent names registered in the
        # graph are sufficiently specific (hyphenated names like
        # "explanation-generator" reduce the risk vs. short generic tokens).
        pat_agent_tool_ref = re.compile(
          r"\bAgent\s+tool\b[^\n]{0,220}\b" + escaped + r"\b",
          flags=re.IGNORECASE,
        )
        if (
          pat_launch.search(body)
          or pat_path.search(body)
          or pat_launch_verb_name.search(body)
          or pat_agent_tool_ref.search(body)
        ):
            edges.append({
                "source": source_id,
                "target": target,
                "type": "delegates",
                "label": "",
            })
            delegated.add(target)

    # Skill -> skill (orchestrates). Walk line-by-line to apply the
    # invocation-context heuristic.
    #
    # Important: links that appear in AskUserQuestion decision-option prose
    # are recommendations, not immediate runtime orchestration. Those are
    # represented by `suggests` edges from _references/general/skill-graph.md.
    # Skip a small local window after an AskUserQuestion marker so lines like
    # "Execute now -- run /plan" do not become `orchestrates`. Only trigger
    # when the line ends with ":" -- that is the invariant for lines that
    # actually introduce an option list.  Prose mentions of AskUserQuestion
    # as a concept (e.g. "phrase every AskUserQuestion option") do not end
    # with ":" and must not suppress legitimate skill invocations below them.
    ask_window = 0
    for line in body.splitlines():
        stripped = line.strip()
        if "AskUserQuestion" in line and line.rstrip().endswith(":"):
            ask_window = 24
            continue
        if ask_window > 0:
            if stripped.startswith("## ") or stripped.startswith("### ") or stripped == "---":
                ask_window = 0
            else:
                ask_window -= 1
                continue
        for match in _SKILL_TO_SKILL_RE.finditer(line):
            target_skill = match.group(1)
            if target_skill == skill_name:
                continue
            target = f"skill:{target_skill}"
            if target not in node_ids:
                continue
            if not _is_invocation_context(line, match.start()):
                continue
            edges.append({
                "source": source_id,
                "target": target,
                "type": "orchestrates",
                "label": "",
            })

    # Skill -> reference (eager-load / lazy-load).
    eager, all_refs = _parse_ref_lists(fm_text)
    eager_set = set(eager)
    lazy = [r for r in all_refs if r not in eager_set]

    for entry in eager:
        resolved = _resolve_ref_entry(entry, nodes)
        if resolved:
            edges.append({
                "source": source_id,
                "target": resolved,
                "type": "eager-load",
                "label": "",
            })
        else:
            warnings.append(
                f"{source_id} references unresolved ref '{entry}'"
            )

    for entry in lazy:
        resolved = _resolve_ref_entry(entry, nodes)
        if resolved:
            edges.append({
                "source": source_id,
                "target": resolved,
                "type": "lazy-load",
                "label": "",
            })
        else:
            warnings.append(
                f"{source_id} references unresolved ref '{entry}'"
            )

    # Skill -> internal-skill dispatches-inline edges. A
    # wrapper's `## Dispatch` section lists the `_internal/<wrapper>/<mode>/
    # SKILL.md` paths it reads inline via the Read tool. Match only paths
    # whose first path segment after `_internal/` equals the enclosing
    # wrapper's skill name -- a wrapper should not claim dispatches-inline
    # edges to another wrapper's internals.
    dispatched_inline: set[str] = set()
    for match in _DISPATCHES_INLINE_RE.finditer(body):
        wrapper, mode = match.group(1), match.group(2)
        if wrapper != skill_name:
            continue
        target = f"skill-internal:{wrapper}/{mode}"
        if target not in node_ids:
            continue
        if target in dispatched_inline:
            continue
        dispatched_inline.add(target)
        edges.append({
            "source": source_id,
            "target": target,
            "type": "dispatches-inline",
            "label": "",
        })

    # Conditional-edge annotation. Scans the body for a small
    # set of canonical prose patterns that gate a delegation / invocation /
    # orchestration on a flag, and attaches `when: "--<flag>"` to the
    # corresponding edge in-place (or creates the edge when missing). See
    # the top-of-file comment block for the accepted pattern contract.
    _annotate_conditional_edges(body, source_id, edges, nodes)

    return edges


# ---------------------------------------------------------------------------
# Edge extraction -- script AST
# ---------------------------------------------------------------------------


def _import_targets(node: ast.AST) -> list[str]:
    """Return module stems imported by an Import or ImportFrom node."""
    results: list[str] = []
    if isinstance(node, ast.Import):
        for alias in node.names:
            results.append(alias.name.split(".")[0])
    elif isinstance(node, ast.ImportFrom):
        # Relative imports have node.level > 0 and module may be None.
        if node.module:
            results.append(node.module.split(".")[0])
    return results


# Matches the trailing string constant in a Path-division expression such as
# SCRIPTS_DIR / "script.py"  or  SKILLS_DIR / "check" / "script.py".
# Used to detect subprocess command-list arrays built with Path arithmetic
# (the AST walk cannot resolve variable references).
_PATH_DIV_SCRIPT_RE = re.compile(r'/\s+"([\w.-]+\.py)"')


def _subprocess_script_literals(call: ast.Call) -> list[str]:
    """Return any '*.py' string literals in the first arg of a subprocess call.

    Matches subprocess.run / check_output / check_call / Popen.
    """
    func = call.func
    if not isinstance(func, ast.Attribute):
        return []
    if not isinstance(func.value, ast.Name):
        return []
    if func.value.id != "subprocess":
        return []
    if func.attr not in ("run", "check_output", "check_call", "Popen"):
        return []
    if not call.args:
        return []
    first = call.args[0]
    if not isinstance(first, ast.List):
        return []
    results: list[str] = []
    for element in first.elts:
        if isinstance(element, ast.Constant) and isinstance(element.value, str):
            if element.value.endswith(".py"):
                # Accept either bare "foo.py" or path-suffixed "scripts/foo.py".
                results.append(Path(element.value).name)
    return results


def extract_script_edges(
    script_path: Path,
    nodes: list[dict],
) -> list[dict]:
    """Extract imports + invokes edges from a single Python script's AST."""
    text = _read_text(script_path)
    if not text:
        return []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    source_name = script_path.name
    source_id = f"script:{source_name}"

    script_nodes = [n for n in nodes if n["type"] == "script"]
    script_ids = {n["id"] for n in script_nodes}
    # Map from module stem (filename without .py) to node id.
    stem_to_id = {
        Path(n["path"]).stem: n["id"] for n in script_nodes
    }

    edges: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for module_stem in _import_targets(node):
                if module_stem in _STDLIB_SKIPLIST:
                    continue
                target_id = stem_to_id.get(module_stem)
                if target_id is None or target_id == source_id:
                    continue
                key = (target_id, "imports")
                if key in seen:
                    continue
                seen.add(key)
                edges.append({
                    "source": source_id,
                    "target": target_id,
                    "type": "imports",
                    "label": "",
                })
        elif isinstance(node, ast.Call):
            for invoked_name in _subprocess_script_literals(node):
                target_id = f"script:{invoked_name}"
                if target_id not in script_ids or target_id == source_id:
                    continue
                key = (target_id, "invokes")
                if key in seen:
                    continue
                seen.add(key)
                edges.append({
                    "source": source_id,
                    "target": target_id,
                    "type": "invokes",
                    "label": "",
                })

    # Second pass: scan raw source for Path-division patterns like
    # SCRIPTS_DIR / "foo.py" — these appear in command-list arrays where the
    # subprocess.run() call receives a variable, not a literal list, so the AST
    # walk above misses them.
    for invoked_name in _PATH_DIV_SCRIPT_RE.findall(text):
        target_id = f"script:{invoked_name}"
        if target_id not in script_ids or target_id == source_id:
            continue
        key = (target_id, "invokes")
        if key in seen:
            continue
        seen.add(key)
        edges.append({
            "source": source_id,
            "target": target_id,
            "type": "invokes",
            "label": "",
        })

    return edges


def extract_reads_edges(
    source_id: str,
    text: str,
    nodes: list[dict],
) -> list[dict]:
    """Extract generic 'reads' edges from any node's prose or source text.

    Scans *text* for explicit ``_references/<scope>/<path>`` occurrences and
    emits a ``reads`` edge from *source_id* to the matching ref node for each
    unique path found. Works for agents, skills, and scripts alike.
    """
    edges: list[dict] = []
    seen: set[str] = set()
    for match in _REF_READ_RE.finditer(text):
        scope = match.group(1)
        rel_path = match.group(2)
        entry = f"{scope}/{rel_path}"
        resolved = _resolve_ref_entry(entry, nodes)
        if not resolved:
            continue
        if resolved == source_id:
          continue
        if resolved in seen:
            continue
        seen.add(resolved)
        edges.append({
            "source": source_id,
            "target": resolved,
            "type": "reads",
            "label": "",
        })
    return edges


# ---------------------------------------------------------------------------
# Manifest assembly
# ---------------------------------------------------------------------------


def _attach_descriptions(nodes: list[dict]) -> None:
    """Populate `description` and `description_source` on every node in place."""
    for node in nodes:
        desc, source = compute_node_description(node)
        node["description"] = desc
        node["description_source"] = source


def build_manifest(
    nodes: list[dict],
    edges: list[dict],
    warnings: list[str],
    generated_at: str,
) -> dict:
    _attach_descriptions(nodes)
    nodes_sorted = sorted(nodes, key=lambda n: (n["type"], n["id"]))
    # De-duplicate edges by (source, type, target) before sorting. When the
    # same (source, type, target) appears more than once, merge `when` and
    # `conditional` annotations from later occurrences into the first --
    # first-occurrence-wins for `when`, but if the first edge
    # is unannotated and a later one carries `when`, promote it. This keeps
    # conditional-prose detection order-independent.
    edge_index: dict[tuple[str, str, str], dict] = {}
    unique_edges: list[dict] = []
    for edge in edges:
        key = (edge["source"], edge["type"], edge["target"])
        existing = edge_index.get(key)
        if existing is None:
            edge_index[key] = edge
            unique_edges.append(edge)
            continue
        # Merge annotations into the previously-kept edge.
        if "when" not in existing and "when" in edge:
            existing["when"] = edge["when"]
        if "conditional" not in existing and edge.get("conditional"):
            existing["conditional"] = True
    edges_sorted = sorted(
        unique_edges,
        key=lambda e: (e["source"], e["type"], e["target"]),
    )
    warnings_sorted = sorted(set(warnings))
    return {
        "generated": generated_at,
        "node_count": len(nodes_sorted),
        "edge_count": len(edges_sorted),
        "nodes": nodes_sorted,
        "edges": edges_sorted,
        "warnings": warnings_sorted,
    }


def _collect_all_edges(
    nodes: list[dict],
    warnings: list[str],
    verbose: bool,
) -> list[dict]:
    edges: list[dict] = []

    # Skill-originated edges (user-facing and internal workers).
    for node in nodes:
        if node["type"] not in ("skill", "skill-internal"):
            continue
        skill_path = REPO_ROOT / node["path"]
        skill_edges = extract_skill_edges(
            skill_path,
            nodes,
            warnings,
            source_id=node["id"],
        )
        if verbose:
            print(
                f"skill {node['id']}: {len(skill_edges)} outgoing edges",
                file=sys.stderr,
            )
        edges.extend(skill_edges)

    # Script-originated edges.
    for node in nodes:
        if node["type"] != "script":
            continue
        script_path = REPO_ROOT / node["path"]
        script_edges = extract_script_edges(script_path, nodes)
        if verbose and script_edges:
            print(
                f"script {node['id']}: {len(script_edges)} outgoing edges",
                file=sys.stderr,
            )
        edges.extend(script_edges)
        # Also emit reads edges from hardcoded _references/ paths in scripts.
        script_text = _read_text(script_path) or ""
        reads_edges = extract_reads_edges(node["id"], script_text, nodes)
        if verbose and reads_edges:
            print(
                f"script {node['id']}: {len(reads_edges)} reads edges",
                file=sys.stderr,
            )
        edges.extend(reads_edges)

    # Suggest edges sourced from general/skill-graph.json (post-completion
    # hints, distinct from runtime orchestrates edges).
    suggest_edges = read_skill_graph_suggestions(nodes, verbose)
    edges.extend(suggest_edges)

    # Rule auto-attach edges: each rule has a frontmatter `paths:` glob list;
    # emit a `skill -> rule` edge of type `auto-loads` for every SKILL.md
    # whose path matches any glob. Rules auto-attach at edit time based on
    # file-scope, not via skill frontmatter, so this synthetic edge is the
    # only way to surface them on the graph.
    edges.extend(extract_rule_autoload_edges(nodes, verbose))

    # Dynamic ref-load edges: generator agents and /check / /plan load refs
    # from `_references/general/<subdir>/` based on a runtime argument
    # (role, audience, perspective). Those loads don't appear in skill
    # frontmatter, so scan skill and agent bodies for subdirectory mentions
    # and emit `dynamic-load` edges to every file in the referenced
    # subdirectory.
    edges.extend(extract_dynamic_ref_edges(nodes, verbose))

    # Generic 'reads' edges: explicit _references/<scope>/<path> mentions in
    # prose/source across agents, skills, rules, and refs. This includes
    # ref->ref links (cross-reference mentions between reference files), plus
    # "Before starting, read ..."/step-level instructions that are not covered
    # by eager/lazy/dynamic-load extraction.
    reads_node_types = (
      "agent",
      "skill",
      "skill-internal",
      "rule",
      "ref-general",
      "ref-template",
      "ref-project",
    )
    for node in nodes:
        if node["type"] not in reads_node_types:
            continue
        node_path = REPO_ROOT / node["path"]
        text = _read_text(node_path) or ""
        reads_edges = extract_reads_edges(node["id"], text, nodes)
        if verbose and reads_edges:
            print(
                f"{node['type']} {node['id']}: {len(reads_edges)} reads edges",
                file=sys.stderr,
            )
        edges.extend(reads_edges)

    return edges


DYNAMIC_REF_SUBDIRS = ("onboarding", "communication", "review-perspectives")


def extract_dynamic_ref_edges(
    nodes: list[dict], verbose: bool = False
) -> list[dict]:
    # Build a subdir -> [ref-general nodes under it] index once.
    subdir_members: dict[str, list[dict]] = {d: [] for d in DYNAMIC_REF_SUBDIRS}
    for node in nodes:
        if node["type"] != "ref-general":
            continue
        path_norm = node["path"].replace("\\", "/")
        for subdir in DYNAMIC_REF_SUBDIRS:
            if f"/general/{subdir}/" in path_norm:
                subdir_members[subdir].append(node)
                break

    # Subdir mention regex: any `<subdir>/` occurrence preceded by a
    # non-word/non-hyphen boundary (so `review-perspectivesX/` won't match).
    # Trailing context can be a real filename, a glob, or a `<placeholder>`
    # -- we only need the signal that the subdir is referenced.
    subdir_res = {
        d: re.compile(r"(?:^|[^\w-])" + re.escape(d) + r"/")
        for d in DYNAMIC_REF_SUBDIRS
    }

    sources = [n for n in nodes if n["type"] in ("skill", "agent")]
    edges: list[dict] = []
    emitted: set[tuple[str, str]] = set()
    for source in sources:
        source_path = REPO_ROOT / source["path"]
        text = _read_text(source_path)
        if not text:
            continue
        _fm, body = _strip_frontmatter(text)
        for subdir in DYNAMIC_REF_SUBDIRS:
            if not subdir_res[subdir].search(body):
                continue
            for target_node in subdir_members[subdir]:
                key = (source["id"], target_node["id"])
                if key in emitted:
                    continue
                emitted.add(key)
                edges.append({
                    "source": source["id"],
                    "target": target_node["id"],
                    "type": "dynamic-load",
                    "label": subdir,
                })
    if verbose:
        print(
            f"dynamic-load edges from {len(DYNAMIC_REF_SUBDIRS)} subdirs: "
            f"{len(edges)}",
            file=sys.stderr,
        )
    return edges


def extract_rule_autoload_edges(
    nodes: list[dict], verbose: bool = False
) -> list[dict]:
    import fnmatch
    rule_nodes = [n for n in nodes if n["type"] == "rule"]
    skill_nodes = [n for n in nodes if n["type"] == "skill"]
    edges: list[dict] = []
    for rule in rule_nodes:
        rule_path = REPO_ROOT / rule["path"]
        text = _read_text(rule_path)
        if not text:
            continue
        fm_text, _body = _strip_frontmatter(text)
        globs = _parse_rule_paths(fm_text)
        if not globs:
            continue
        for skill in skill_nodes:
            skill_rel = skill["path"].replace("\\", "/")
            if any(fnmatch.fnmatch(skill_rel, g) for g in globs):
                edges.append({
                    "source": skill["id"],
                    "target": rule["id"],
                    "type": "auto-loads",
                    "label": globs[0],
                })
    if verbose:
        print(
            f"auto-loads edges from rule path scopes: {len(edges)}",
            file=sys.stderr,
        )
    return edges


def _parse_rule_paths(fm_text: str) -> list[str]:
    """Extract the `paths:` list from a rule's YAML frontmatter.

    Accepts either a flow list (``paths: [".claude/**"]``) or a block list
    (``paths:`` followed by indented ``- ".claude/**"`` lines).
    """
    if not fm_text:
        return []
    lines = fm_text.splitlines()
    out: list[str] = []
    in_block = False
    for line in lines:
        stripped = line.strip()
        if not in_block:
            m = re.match(r"^paths\s*:\s*(.*)$", line)
            if not m:
                continue
            tail = m.group(1).strip()
            if tail.startswith("[") and tail.endswith("]"):
                for item in tail[1:-1].split(","):
                    item = item.strip().strip('"').strip("'")
                    if item:
                        out.append(item)
                return out
            if tail and not tail.startswith("#"):
                out.append(tail.strip('"').strip("'"))
                return out
            in_block = True
            continue
        if stripped.startswith("- "):
            item = stripped[2:].strip().strip('"').strip("'")
            if item:
                out.append(item)
            continue
        if not stripped or stripped.startswith("#"):
            continue
        # New top-level key ends the paths block.
        if not line.startswith(" "):
            break
    return out


SKILL_GRAPH_JSON = REPO_ROOT / ".claude" / "references" / "general" / "skill-graph.json"


def read_skill_graph_suggestions(
    nodes: list[dict], verbose: bool = False
) -> list[dict]:
    if not SKILL_GRAPH_JSON.is_file():
        if verbose:
            print(
                f"INFO: {SKILL_GRAPH_JSON} not found; skipping suggests edges",
                file=sys.stderr,
            )
        return []
    try:
        payload = json.loads(SKILL_GRAPH_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        if verbose:
            print(
                f"WARNING: could not read {SKILL_GRAPH_JSON}: {exc}",
                file=sys.stderr,
            )
        return []
    skill_ids = {n["id"] for n in nodes if n["type"] == "skill"}
    seen: set[tuple[str, str]] = set()
    first_per_source: set[str] = set()
    out: list[dict] = []
    for entry in payload.get("edges", []):
        source_id = _normalize_skill_ref(entry.get("after", ""))
        target_id = _normalize_skill_ref(entry.get("suggest", ""))
        if source_id is None or target_id is None:
            continue
        if source_id not in skill_ids or target_id not in skill_ids:
            continue
        if source_id == target_id:
            continue
        key = (source_id, target_id)
        if key in seen:
            continue
        seen.add(key)
        reason = (entry.get("reason") or "").strip()
        edge: dict = {
            "source": source_id,
            "target": target_id,
            "type": "suggests",
            "label": reason,
        }
        if source_id not in first_per_source:
            first_per_source.add(source_id)
            edge["primary"] = True
        out.append(edge)
    if verbose:
        print(f"suggests edges from skill-graph.json: {len(out)}", file=sys.stderr)
    return out


def _normalize_skill_ref(ref: str) -> str | None:
    ref = (ref or "").strip()
    if not ref.startswith("/"):
        return None
    # Strip everything after the first space (drops flag variants like
    # "--light", "--roadmap", "spec-drift", "--inventory" that all map to
    # the same base skill node).
    base = ref.split(" ", 1)[0].lstrip("/")
    if not base:
        return None
    return f"skill:{base}"


# ---------------------------------------------------------------------------
# Markdown rendering helpers
# ---------------------------------------------------------------------------


def _sanitize_mermaid_id(node_id: str) -> str:
    """Convert 'skill:research' -> 'skill_research' (Mermaid-safe identifier)."""
    return re.sub(r"[^A-Za-z0-9]", "_", node_id)


def _sanitize_edge_label(text: str) -> str:
    """Strip characters that break Mermaid's edge-label parser.

    Mirrors the pattern from generate_skill_map.py: replace parens/brackets
    with safer punctuation, remove pipes/quotes/hashes, collapse whitespace,
    and truncate to 50 characters with a trailing ellipsis.
    """
    cleaned = (
        text.replace("(", " - ")
            .replace(")", "")
            .replace("[", " - ")
            .replace("]", "")
            .replace("{", "")
            .replace("}", "")
            .replace("|", "/")
            .replace('"', "'")
            .replace("#", "")
    )
    cleaned = " ".join(cleaned.split())
    if len(cleaned) > 50:
        cleaned = cleaned[:47] + "..."
    return cleaned


def _skill_category(label: str) -> str:
    """Return the category key for a skill node label (e.g. '/plan')."""
    return SKILL_CATEGORY_MAP.get(label, "utility")


def _node_category(node: dict) -> str | None:
    """Return the Mermaid classDef category for a node, or None if unclassed."""
    t = node["type"]
    if t == "skill":
        return _skill_category(node["label"])
    if t == "skill-internal":
        return "skill_internal"
    if t == "script":
        return "script"
    if t == "agent":
        return "agent"
    if t == "rule":
        return "rule"
    if t == "ref-general":
        return "ref_general"
    if t == "ref-template":
        return "ref_template"
    if t == "ref-project":
        return "ref_project"
    return None


def _filter_edges_by_type(edges: list[dict], types: set[str]) -> list[dict]:
    return [e for e in edges if e["type"] in types]


def _build_mermaid_overview(
    direction: str,
    nodes_in_scope: list[dict],
    edges: list[dict],
    node_index: dict[str, dict],
) -> str:
    """Render one filtered Mermaid overview.

    `direction` is 'TD' or 'LR'. `nodes_in_scope` are the nodes to emit
    declarations for (even if some have no edges). `edges` are already
    pre-filtered to the edges the overview should show.
    """
    if not edges:
        return "_No edges of this type found._"

    truncated_note = ""
    if len(edges) > MAX_EDGES_PER_OVERVIEW:
        original_count = len(edges)
        edges = edges[:MAX_EDGES_PER_OVERVIEW]
        truncated_note = (
            f"_Showing {MAX_EDGES_PER_OVERVIEW} of {original_count} edges. "
            "See the JSON for the full set._"
        )

    # Collect the node ids actually referenced by the edges plus the
    # in-scope nodes. We only declare nodes that participate in at least
    # one edge to keep the diagram dense with signal.
    referenced_ids: set[str] = set()
    for edge in edges:
        referenced_ids.add(edge["source"])
        referenced_ids.add(edge["target"])

    declared_nodes = [n for n in nodes_in_scope if n["id"] in referenced_ids]

    lines: list[str] = []
    lines.append("```mermaid")
    lines.append(MERMAID_INIT_DIRECTIVE)
    lines.append(f"flowchart {direction}")
    lines.append("")

    for node in declared_nodes:
        safe_id = _sanitize_mermaid_id(node["id"])
        label = node["label"].replace('"', "'")
        lines.append(f'    {safe_id}["{label}"]')
    lines.append("")

    # Edges. Suggest edges (post-completion hints from skill-graph.md) use
    # Mermaid's dashed arrow `-.->` to stay visually distinct from solid
    # runtime-call edges. Conditional edges (those with `when` set) always
    # emit a label; the flag is prepended to any existing label so the
    # reader can see at a glance which flag gates the delegation.
    for edge in edges:
        src = _sanitize_mermaid_id(edge["source"])
        dst = _sanitize_mermaid_id(edge["target"])
        raw_label = edge.get("label") or ""
        when_flag = edge.get("when") or ""
        # `suggests` and `dispatches-inline` both render as dashed arrows.
        # Suggests are post-completion hints (factually non-runtime), while
        # dispatches-inline points a wrapper at its inlined internal worker
        # (distinct from a runtime `orchestrates` call).
        edge_type = edge.get("type")
        if edge_type in ("suggests", "dispatches-inline"):
            arrow = "-.->"
        else:
            arrow = "-->"
        if when_flag:
            sanitized = _sanitize_edge_label(raw_label) if raw_label.strip() else ""
            if sanitized:
                combined = f"{when_flag}: {sanitized}"
            else:
                combined = when_flag
            # Re-run through the truncation path so the combined form stays
            # within Mermaid's edge-label budget. The flag itself is free
            # of parens/pipes/quotes, so sanitization is a no-op beyond
            # whitespace collapsing and the 50-char cap.
            label = _sanitize_edge_label(combined)
            lines.append(f"    {src} {arrow}|{label}| {dst}")
        elif raw_label.strip():
            label = _sanitize_edge_label(raw_label)
            lines.append(f"    {src} {arrow}|{label}| {dst}")
        else:
            lines.append(f"    {src} {arrow} {dst}")
    lines.append("")

    # classDef + class assignments. Only emit classes that have members.
    category_members: dict[str, list[str]] = {}
    for node in declared_nodes:
        cat = _node_category(node)
        if cat is None:
            continue
        category_members.setdefault(cat, []).append(
            _sanitize_mermaid_id(node["id"])
        )

    for cat, members in category_members.items():
        lines.append(f"    classDef {cat} {CLASS_DEFS[cat]}")
    for cat, members in category_members.items():
        if members:
            lines.append(f"    class {','.join(sorted(members))} {cat}")
    lines.append("```")

    block = "\n".join(lines)
    if truncated_note:
        block = block + "\n\n" + truncated_note
    return block


def _build_overview_skill_orchestration(
    nodes: list[dict],
    edges: list[dict],
    node_index: dict[str, dict],
) -> str:
    # Scope includes user-facing skills AND internal-skill worker nodes so
    # the wrapper->internal `dispatches-inline` edges can render alongside
    # the runtime orchestrates/suggests edges in a single overview.
    skill_nodes = [n for n in nodes if n["type"] in ("skill", "skill-internal")]
    skill_ids = {n["id"] for n in skill_nodes}
    # Include runtime `orchestrates` (solid), curatorial `suggests` (dashed,
    # sourced from general/skill-graph.md), and `dispatches-inline` (dashed,
    # wrapper->internal inlined-worker edges) in this overview.
    scoped_edges = [
        e for e in _filter_edges_by_type(
            edges, {"orchestrates", "suggests", "dispatches-inline"}
        )
        if e["source"] in skill_ids and e["target"] in skill_ids
    ]
    # Emit orchestrates first so solid edges render beneath dashed overlays.
    scoped_edges.sort(
        key=lambda e: (0 if e["type"] == "orchestrates" else 1,
                       e["source"], e["target"])
    )
    return _build_mermaid_overview("TD", skill_nodes, scoped_edges, node_index)


def _build_overview_skill_invocations(
    nodes: list[dict],
    edges: list[dict],
    node_index: dict[str, dict],
) -> str:
    in_scope_types = {"skill", "script", "agent"}
    scoped_nodes = [n for n in nodes if n["type"] in in_scope_types]
    scoped_edges = [
        e for e in _filter_edges_by_type(edges, {"invokes", "delegates"})
        if node_index.get(e["source"], {}).get("type") == "skill"
    ]
    scoped_edges.sort(key=lambda e: (e["source"], e["type"], e["target"]))
    return _build_mermaid_overview("LR", scoped_nodes, scoped_edges, node_index)


def _build_overview_skill_references(
    nodes: list[dict],
    edges: list[dict],
    node_index: dict[str, dict],
) -> str:
    in_scope_types = {
        "skill", "agent", "rule", "ref-general", "ref-template", "ref-project",
    }
    scoped_nodes = [n for n in nodes if n["type"] in in_scope_types]
    scoped_edges = _filter_edges_by_type(
        edges, {"eager-load", "lazy-load", "auto-loads", "dynamic-load", "reads"}
    )
    scoped_edges = sorted(
        scoped_edges, key=lambda e: (e["source"], e["type"], e["target"])
    )
    return _build_mermaid_overview("TD", scoped_nodes, scoped_edges, node_index)


def _build_overview_reference_crosslinks(
    nodes: list[dict],
    edges: list[dict],
    node_index: dict[str, dict],
) -> str:
    """Render ref->ref explicit reads links as a focused overview."""
    ref_types = {"ref-general", "ref-template", "ref-project"}
    scoped_nodes = [n for n in nodes if n["type"] in ref_types]
    ref_ids = {n["id"] for n in scoped_nodes}
    scoped_edges = [
        e
        for e in _filter_edges_by_type(edges, {"reads"})
        if e["source"] in ref_ids and e["target"] in ref_ids
    ]
    scoped_edges.sort(key=lambda e: (e["source"], e["target"]))
    return _build_mermaid_overview("TD", scoped_nodes, scoped_edges, node_index)


def _build_per_skill_trees(
    nodes: list[dict],
    edges: list[dict],
    node_index: dict[str, dict],
) -> str:
    """Render the per-skill call-tree drill-down section body (no H2)."""
    skill_nodes = sorted(
        [n for n in nodes if n["type"] == "skill"],
        key=lambda n: n["label"],
    )

    # Pre-index edges by source skill id for O(N) grouping.
    edges_by_source: dict[str, list[dict]] = {}
    for edge in edges:
        edges_by_source.setdefault(edge["source"], []).append(edge)

    sections: list[str] = []
    for skill in skill_nodes:
        out_edges = edges_by_source.get(skill["id"], [])
        lines: list[str] = []
        lines.append(f"### {skill['label']}")
        lines.append("")

        if not out_edges:
            lines.append("_No outgoing edges._")
            lines.append("")
            sections.append("\n".join(lines))
            continue

        # Group by edge type.
        groups: dict[str, list[dict]] = {}
        for edge in out_edges:
            groups.setdefault(edge["type"], []).append(edge)

        # Fixed section order; omit empty groups.
        section_order = [
            ("invokes",           "Calls scripts:"),
            ("delegates",         "Delegates to agents:"),
            ("orchestrates",      "Orchestrates skills:"),
            ("dispatches-inline", "Dispatches to internal workers (inlined):"),
            ("suggests",          "Suggests after (from skill-graph.md):"),
            ("auto-loads",        "Auto-loads rules (via path scope):"),
            ("eager-load",        "Eager-loads refs:"),
            ("lazy-load",         "Lazy-loads refs:"),
            ("dynamic-load",      "Dynamically loads refs (via runtime argument):"),
            ("reads",             "Reads refs (explicit in prose/code):"),
        ]

        first_section = True
        for edge_type, heading in section_order:
            group_edges = groups.get(edge_type)
            if not group_edges:
                continue
            if not first_section:
                lines.append("")
            first_section = False
            lines.append(heading)
            # Sort edges by target label, then id.
            sorted_edges = sorted(
                group_edges,
                key=lambda e: (
                    node_index.get(e["target"], {}).get("label", ""),
                    e["target"],
                ),
            )
            for edge in sorted_edges:
                target_node = node_index.get(edge["target"])
                if target_node is None:
                    display = edge["target"]
                else:
                    if target_node["type"] == "skill":
                        display = target_node["label"]
                    elif target_node["type"] == "skill-internal":
                        display = target_node["label"]
                    elif target_node["type"] == "script":
                        display = target_node["label"]
                    elif target_node["type"] == "agent":
                        display = target_node["label"]
                    elif target_node["type"] == "rule":
                        display = target_node["label"]
                    elif target_node["type"].startswith("ref-"):
                        # Strip the ref-* prefix to show 'general/foo.md' etc.
                        id_tail = edge["target"].split(":", 1)[1]
                        if target_node["type"] == "ref-general":
                            display = f"general/{id_tail}"
                        elif target_node["type"] == "ref-template":
                            display = f"template/{id_tail}"
                        elif target_node["type"] == "ref-project":
                            display = f"project/{id_tail}"
                        else:
                            display = id_tail
                    else:
                        display = target_node["label"]
                raw_label = edge.get("label") or ""
                suffix = ""
                if raw_label.strip():
                    suffix = f" -- {raw_label.strip()}"
                when_flag = edge.get("when") or ""
                when_suffix = f" (when: {when_flag})" if when_flag else ""
                lines.append(f"- `{display}`{suffix}{when_suffix}")
        lines.append("")
        sections.append("\n".join(lines))

    return "\n".join(sections).rstrip() + "\n"


def _build_reverse_index(
    nodes: list[dict],
    edges: list[dict],
    target_type: str,
    heading: str,
    caller_col: str,
) -> str:
    """Render a reverse-index table for all nodes of target_type.

    Rows are sorted by the target node's label. The 'Used by' / 'Delegated by'
    column lists every source node that has an edge into that target, shown
    as '/<skill>' or '<script.py>' -- comma-separated, sorted, de-duplicated.
    """
    target_nodes = sorted(
        [n for n in nodes if n["type"] == target_type],
        key=lambda n: n["label"],
    )

    node_index = {n["id"]: n for n in nodes}

    # Map target-id -> list of source ids.
    incoming: dict[str, list[str]] = {}
    for edge in edges:
        target = node_index.get(edge["target"])
        if target is None or target["type"] != target_type:
            continue
        incoming.setdefault(edge["target"], []).append(edge["source"])

    lines: list[str] = []
    lines.append(f"### {heading}")
    lines.append("")
    # Column name for the target itself depends on target type.
    first_col = "Script" if target_type == "script" else "Agent"
    lines.append(f"| {first_col} | Path | {caller_col} |")
    lines.append("|---|---|---|")

    for node in target_nodes:
        callers = incoming.get(node["id"], [])
        rendered_callers: list[str] = []
        for src in sorted(set(callers)):
            src_node = node_index.get(src)
            if src_node is None:
                rendered_callers.append(f"`{src}`")
                continue
            if src_node["type"] == "skill":
                rendered_callers.append(f"`{src_node['label']}`")
            elif src_node["type"] == "script":
                rendered_callers.append(f"`{src_node['label']}`")
            else:
                rendered_callers.append(f"`{src_node['label']}`")
        callers_cell = ", ".join(rendered_callers) if rendered_callers else "_(unused)_"
        lines.append(
            f"| `{node['label']}` | `{node['path']}` | {callers_cell} |"
        )
    lines.append("")
    return "\n".join(lines)


def _build_text_fallback(edges: list[dict]) -> str:
    """Render the <details> accessibility text fallback block body."""
    groups: dict[str, list[dict]] = {}
    for edge in edges:
        groups.setdefault(edge["type"], []).append(edge)

    # Fixed order (stable). Only emit a subsection if the group has edges.
    group_order = [
        "invokes", "delegates", "orchestrates", "dispatches-inline", "suggests",
      "auto-loads", "eager-load", "lazy-load", "dynamic-load", "reads", "imports",
    ]

    lines: list[str] = []
    lines.append("<details>")
    lines.append("<summary>Text-only relationship list (accessibility fallback)</summary>")
    lines.append("")
    lines.append("Edges grouped by type, each line showing `source -> target: label`.")
    lines.append("")

    for group in group_order:
        group_edges = groups.get(group)
        if not group_edges:
            continue
        lines.append(f"### {group}")
        lines.append("")
        sorted_edges = sorted(
            group_edges,
            key=lambda e: (e["source"], e["target"]),
        )
        for edge in sorted_edges:
            raw_label = edge.get("label") or ""
            label_suffix = f": {raw_label.strip()}" if raw_label.strip() else ":"
            when_flag = edge.get("when") or ""
            when_suffix = f" (when: {when_flag})" if when_flag else ""
            lines.append(
                f"- `{edge['source']}` -> `{edge['target']}`{label_suffix}{when_suffix}"
            )
        lines.append("")
    lines.append("</details>")
    return "\n".join(lines)


MARKDOWN_PREAMBLE = """\
---
diataxis: reference
freshness: release-bound
last-reviewed: {last_reviewed}
---

<!-- This file is generated by .claude/skills/scripts/generate_call_graph.py. Do not edit by hand. -->

# SEJA harness call graph

This is the live invocation topology: which skills call which scripts, which agents they delegate to, which other skills they orchestrate, and which references they load. The skill-orchestration overview also includes **suggests** edges (dashed, sourced from `general/skill-graph.md`) representing post-completion hints emitted by `/post-skill`; these are not runtime calls. See also:

- [`skill-map.md`](skill-map.md) -- post-completion *suggestions* (curatorial, what we recommend next).
- [`../reference/harness-reference.md`](../reference/harness-reference.md) -- flat catalog of every harness component.

Conditional edges (dashed stroke with a flag label, e.g. `--deep`) come from option-gated prose in a skill's source; they fire only when the named flag is passed.
"""


def render_markdown(manifest: dict, generated_at: str, fixed_date: str | None) -> str:
    """Render the full call-graph.md document as a string."""
    nodes = manifest["nodes"]
    edges = manifest["edges"]
    node_index = {n["id"]: n for n in nodes}

    if fixed_date:
        last_reviewed = fixed_date[:10]
    else:
        last_reviewed = generated_at[:10]

    parts: list[str] = []
    parts.append(MARKDOWN_PREAMBLE.format(last_reviewed=last_reviewed))

    # Section 1: overviews.
    parts.append("## Skill orchestration\n")
    parts.append(_build_overview_skill_orchestration(nodes, edges, node_index))
    parts.append("")

    parts.append("## Skill invocations\n")
    parts.append(_build_overview_skill_invocations(nodes, edges, node_index))
    parts.append("")

    parts.append("## Skill reference loads\n")
    parts.append(_build_overview_skill_references(nodes, edges, node_index))
    parts.append("")

    parts.append("## Reference cross-links\n")
    parts.append(_build_overview_reference_crosslinks(nodes, edges, node_index))
    parts.append("")

    # Section 2: per-skill call trees.
    parts.append("## Per-skill call trees\n")
    parts.append(_build_per_skill_trees(nodes, edges, node_index))

    # Section 3: reverse indices.
    parts.append("## Reverse indices\n")
    parts.append(_build_reverse_index(
        nodes, edges, "script",
        heading="Scripts: used by",
        caller_col="Used by",
    ))
    parts.append(_build_reverse_index(
        nodes, edges, "agent",
        heading="Agents: delegated by",
        caller_col="Delegated by",
    ))

    # Section 4: accessibility text fallback.
    parts.append(_build_text_fallback(edges))
    parts.append("")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# HTML / CSS / JS templates (Step 3 scaffolding)
# ---------------------------------------------------------------------------
#
# Emitted verbatim into seja-public/docs/concepts/call-graph.{html,css,js}.
# Uses stdlib `string.Template` for timestamp substitution. NO Jinja2.
# SRI hashes are placeholders -- see the comment at the top of call-graph.html
# for the refresh procedure. Interactive controls exist as disabled placeholders
# in the sidebar; they will be wired in Steps 4-5.

HTML_TEMPLATE = string.Template("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SEJA harness call graph</title>
<!--
  Generated $generated_at by .claude/skills/scripts/generate_call_graph.py.
  Do not edit by hand.

  CDN versions and integrity hashes pinned below. To refresh SRI hashes run
  `python .claude/skills/scripts/generate_call_graph.py --refresh-sri`, or
  manually:
    for url in \\
      https://unpkg.com/cytoscape@3.30.4/dist/cytoscape.min.js \\
      https://unpkg.com/layout-base@2.0.1/layout-base.js \\
      https://unpkg.com/cose-base@2.2.0/cose-base.js \\
      https://unpkg.com/cytoscape-fcose@2.2.0/cytoscape-fcose.js \\
      https://unpkg.com/webcola@3.4.0/WebCola/cola.min.js \\
      https://unpkg.com/cytoscape-cola@2.5.1/cytoscape-cola.js \\
      https://unpkg.com/cytoscape-svg@0.4.0/cytoscape-svg.js ; do
      echo "$$url"
      curl -sL "$$url" | openssl dgst -sha384 -binary | openssl base64 -A
      echo
    done
  Then replace the sha384-PLACEHOLDER values in the <script> tags below.
  Placeholders are intentional for Step 3 scaffolding; refresh is tracked as
  a follow-up maintenance task rather than blocking this step on a network
  fetch we cannot perform reliably from the generator context.
-->
<link rel="stylesheet" href="call-graph.css">
<script src="https://unpkg.com/cytoscape@3.30.4/dist/cytoscape.min.js"
        integrity="sha384-H3uzGzTfGHUAumB8+s4GEdfFwzAceN9wCCndN8AXubWKFIPuBSWKKtWDx7RhSf/z" crossorigin="anonymous"></script>
<script src="https://unpkg.com/layout-base@2.0.1/layout-base.js"
        integrity="sha384-5E2lB9AIGE6LRCnOOSTnZRlYZFZ01iMeN2fw97Z1r4Z/kXALxKw2AC+ZzQqoeDsG" crossorigin="anonymous"></script>
<script src="https://unpkg.com/cose-base@2.2.0/cose-base.js"
        integrity="sha384-RswRBkrMsPUYpJLbZ1CVA08zbNzAkykE2oGJTujBwfjWNdfxv2WVjLJNqv1LhAOp" crossorigin="anonymous"></script>
<script src="https://unpkg.com/cytoscape-fcose@2.2.0/cytoscape-fcose.js"
        integrity="sha384-uk5Wbjq1+KqUdHO30w7N7GrEGdzBhaJeW9o/ANF6v9+yx3M/cBmoX51C000JNCUf" crossorigin="anonymous"></script>
<script src="https://unpkg.com/webcola@3.4.0/WebCola/cola.min.js"
        integrity="sha384-o4yPeUKY7q5q4fuMcFuJWSBJPJgSHtssnfVZvjNRGOEuBwT8zxXnzyGJcy5Ojpeo" crossorigin="anonymous"></script>
<script src="https://unpkg.com/cytoscape-cola@2.5.1/cytoscape-cola.js"
        integrity="sha384-hS0F3AnUYl+EBC3wCT4+d6MKdLR27UlifwZZYJi5oRCNhKA1ptaEWExH6BqyfMeW" crossorigin="anonymous"></script>
<script src="https://unpkg.com/cytoscape-svg@0.4.0/cytoscape-svg.js"
        integrity="sha384-bOfT/gjvLn+2+GkQyPN3ooyaZ1sk6KnoCaqOev0BTeIkn6kZQBm9sZTkTosZqOmy" crossorigin="anonymous"></script>
</head>
<body>
<header class="top-bar">
  <h1>SEJA harness call graph</h1>
  <nav class="top-links" aria-label="Related views">
    <a href="call-graph.md">Markdown view</a>
    <a href="../reference/harness-reference.md">Harness reference</a>
    <a href="skill-map.md">Skill map (suggestions)</a>
  </nav>
  <div class="top-search" aria-label="Node search controls">
    <label for="node-search-input">Search nodes</label>
    <input id="node-search-input" type="search" placeholder="Type to match node labels..." autocomplete="off">
    <button type="button" id="node-search-clear" aria-label="Clear node search">Clear</button>
  </div>
  <div class="export-buttons">
    <button type="button" id="export-svg" aria-label="Export current graph view as SVG">Export SVG</button>
    <button type="button" id="export-png" aria-label="Export current graph view as PNG">Export PNG</button>
  </div>
</header>
<main class="app">
  <aside class="sidebar" aria-label="Graph controls">
    <section class="legend">
      <h2>Legend</h2>
      <ul class="legend-list">
        <li><span class="swatch swatch-skill"></span>Skill</li>
        <li><span class="swatch swatch-skill-internal"></span>Skill (internal, inlined)</li>
        <li><span class="swatch swatch-agent"></span>Agent</li>
        <li><span class="swatch swatch-script"></span>Script</li>
        <li><span class="swatch swatch-rule"></span>Rule</li>
        <li><span class="swatch swatch-ref-general"></span>Ref (general)</li>
        <li><span class="swatch swatch-ref-template"></span>Ref (template)</li>
        <li><span class="swatch swatch-ref-project"></span>Ref (project)</li>
        <li><span class="swatch swatch-edge-suggests"></span>Suggests (post-completion hint)</li>
        <li><span class="swatch swatch-edge-dispatches-inline"></span>Dispatches inline (wrapper -&gt; internal)</li>
        <li><span class="swatch swatch-edge-dynamic-load"></span>Dynamic load (via runtime argument)</li>
        <li><span class="swatch swatch-edge-reads"></span>Reads (explicit ref read in prose/code)</li>
        <li><span class="swatch swatch-edge-conditional"></span>Conditional edge (fires under flag)</li>
      </ul>
    </section>
    <section class="filters" aria-label="Node type filters">
      <details class="filter-collapsible" open>
        <summary class="filter-collapsible-heading">Filter by node type</summary>
        <label><input type="checkbox" class="filter-type" value="skill" checked> Skill</label>
        <label><input type="checkbox" class="filter-type" value="skill-internal" checked> Internal skills</label>
        <label><input type="checkbox" class="filter-type" value="agent" checked> Agent</label>
        <label><input type="checkbox" class="filter-type" value="script" checked> Script</label>
        <label><input type="checkbox" class="filter-type" value="rule" checked> Rule</label>
        <label><input type="checkbox" class="filter-type" value="ref-general" checked> Ref (general)</label>
        <label><input type="checkbox" class="filter-type" value="ref-template" checked> Ref (template)</label>
        <label><input type="checkbox" class="filter-type" value="ref-project" checked> Ref (project)</label>
        <div class="filter-buttons">
          <button type="button" id="filter-all">Select all</button>
          <button type="button" id="filter-none">Deselect all</button>
        </div>
        <label class="filter-missing"><input type="checkbox" id="filter-hide-disconnected"> Hide disconnected nodes</label>
        <label class="filter-missing"><input type="checkbox" id="filter-hide-internal-skills" aria-label="Hide internal skills"> Hide internal skills (pre-skill, post-skill)</label>
        <div class="filter-buttons filter-presets">
          <button type="button" id="filter-preset-user-facing" aria-label="Show only user-facing slash-command skills">User-facing view</button>
          <button type="button" id="filter-preset-full" aria-label="Restore the full call graph view">Full view</button>
        </div>
      </details>
    </section>
    <section class="filters filter-edge-types" aria-label="Edge type filters">
      <details class="filter-collapsible" open>
        <summary class="filter-collapsible-heading">Filter by edge type</summary>
        <div class="filter-subgroup" aria-label="Calls and delegations">
          <span class="filter-subgroup-label">Calls / delegations</span>
          <label><input type="checkbox" class="filter-edge-type" value="invokes" checked> invokes (skill -> script)</label>
          <label><input type="checkbox" class="filter-edge-type" value="delegates" checked> delegates (skill -> agent)</label>
          <label><input type="checkbox" class="filter-edge-type" value="orchestrates" checked> orchestrates (skill -> skill)</label>
          <label><input type="checkbox" class="filter-edge-type" value="dispatches-inline" checked> dispatches-inline (wrapper -> internal)</label>
        </div>
        <div class="filter-subgroup" aria-label="Reference loads">
          <span class="filter-subgroup-label">Ref loads</span>
          <label><input type="checkbox" class="filter-edge-type" value="eager-load" checked> eager-load</label>
          <label><input type="checkbox" class="filter-edge-type" value="lazy-load" checked> lazy-load</label>
          <label><input type="checkbox" class="filter-edge-type" value="auto-loads" checked> auto-loads (rules, via path scope)</label>
          <label><input type="checkbox" class="filter-edge-type" value="dynamic-load" checked> dynamic-load (dotted, runtime arg)</label>
          <label><input type="checkbox" class="filter-edge-type" value="reads" checked> reads (explicit ref read in prose/code)</label>
        </div>
        <div class="filter-subgroup" aria-label="Other edge types">
          <span class="filter-subgroup-label">Other</span>
          <label><input type="checkbox" class="filter-edge-type" value="suggests" checked> suggests (dashed, skill-graph.md)</label>
          <label><input type="checkbox" class="filter-edge-type" value="imports" checked> imports (script -> script)</label>
          <label><input type="checkbox" id="filter-conditional-show" checked> conditional (amber, fires only under flag)</label>
        </div>
        <div class="filter-buttons">
          <button type="button" id="edge-filter-all">Select all</button>
          <button type="button" id="edge-filter-none">Deselect all</button>
        </div>
      </details>
    </section>
    <section class="layout-controls" aria-label="Layout selection">
      <h2>Layout</h2>
      <label><input type="radio" name="layout" value="fcose" checked> fcose (force-directed, general)</label>
      <label><input type="radio" name="layout" value="cola"> cola (constraint-force, downward flow)</label>
      <label><input type="radio" name="layout" value="concentric"> concentric (radial by type)</label>
      <div class="layout-buttons">
        <button type="button" id="layout-fit" aria-label="Zoom to fit currently visible graph elements">Zoom to fit</button>
        <button type="button" id="layout-reset" aria-label="Reset layout to algorithmic positions">Reset layout</button>
        <button type="button" id="layout-save" aria-label="Download current node positions as JSON">Download layout</button>
        <button type="button" id="layout-load" aria-label="Load node positions from a previously downloaded JSON file">Load layout</button>
        <input type="file" id="layout-load-input" accept="application/json,.json" hidden>
      </div>
    </section>
  </aside>
  <div id="cy" class="cy-canvas" role="region" aria-label="Call graph"></div>
  <aside id="match-panel" class="match-panel" hidden aria-hidden="true" aria-label="Matched nodes">
    <header class="match-panel-header">
      <h2>Matched nodes</h2>
      <span id="match-count" class="match-count">0</span>
    </header>
    <p id="match-panel-empty" class="match-empty">Type in "Search nodes" to highlight matching labels.</p>
    <ul id="match-list" class="match-list" aria-label="Search results"></ul>
  </aside>
  <aside id="side-panel" class="side-panel" hidden aria-hidden="true" aria-label="Node details">
    <header class="side-panel-header">
      <span id="side-panel-type-badge" class="type-badge">Node</span>
      <h2 id="side-panel-title" class="side-panel-title">Select a node</h2>
      <div class="side-panel-controls">
        <button type="button" id="side-panel-pin" class="side-panel-btn"
                aria-pressed="false" aria-label="Pin side panel open">Pin</button>
        <button type="button" id="side-panel-close" class="side-panel-btn side-panel-close"
                aria-label="Close side panel">&times;</button>
      </div>
    </header>
    <div class="side-panel-body">
      <p class="side-panel-path-wrap">
        <a id="side-panel-path" href="#" target="_blank" rel="noopener"
           class="side-panel-path">&nbsp;</a>
      </p>
      <div id="side-panel-description" class="side-panel-description"></div>
      <div id="side-panel-fallback-badge" class="fallback-badge" hidden>
        Developer-oriented &mdash; awaiting designer rewrite
      </div>
      <section id="side-panel-incoming" class="side-panel-section">
        <h3>Incoming edges</h3>
        <ul class="edge-list" id="side-panel-incoming-list"></ul>
      </section>
      <section id="side-panel-outgoing" class="side-panel-section">
        <h3>Outgoing edges</h3>
        <div id="side-panel-outgoing-groups"></div>
      </section>
    </div>
  </aside>
</main>
<script src="call-graph.js"></script>
</body>
</html>
""")


CSS_TEMPLATE = string.Template("""/*
 * SEJA harness call graph viewer styles.
 * Generated $generated_at by .claude/skills/scripts/generate_call_graph.py.
 * Do not edit by hand.
 *
 * Pastel palette matches the Mermaid palette in call-graph.md and skill-map.mmd
 * so the two artifacts stay visually consistent across rendering surfaces.
 */

* { box-sizing: border-box; }

html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  font-size: 14px;
  color: #222;
  background: #fafafa;
}

/* ------------------------------------------------------------------ */
/* Top bar                                                             */
/* ------------------------------------------------------------------ */

.top-bar {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 10px 20px;
  background: #ffffff;
  border-bottom: 1px solid #e0e0e0;
  flex-wrap: wrap;
}

.top-bar h1 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e3a5f;
}

.top-links {
  display: flex;
  gap: 16px;
  flex: 1;
}

.top-links a {
  color: #4a6a8a;
  text-decoration: none;
  font-size: 13px;
}

.top-links a:hover {
  text-decoration: underline;
}

.top-search {
  display: flex;
  align-items: center;
  gap: 8px;
}

.top-search label {
  font-size: 12px;
  color: #4a6a8a;
  white-space: nowrap;
}

.top-search input {
  width: 260px;
  max-width: 42vw;
  padding: 5px 8px;
  border: 1px solid #c9d5e2;
  border-radius: 4px;
  font: inherit;
  font-size: 13px;
}

.top-search input:focus {
  outline: 2px solid #6da3d4;
  outline-offset: 1px;
}

.export-buttons {
  display: flex;
  gap: 8px;
}

/* ------------------------------------------------------------------ */
/* Three-pane layout                                                   */
/* ------------------------------------------------------------------ */

.app {
  display: flex;
  height: calc(100vh - 48px);
  min-height: 0;
}

.sidebar {
  width: 260px;
  flex-shrink: 0;
  padding: 16px;
  background: #ffffff;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
}

.cy-canvas {
  flex: 1;
  min-width: 0;
  background: #fafafa;
  position: relative;
}

.match-panel {
  width: 280px;
  flex-shrink: 0;
  background: #ffffff;
  border-left: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.match-panel[hidden] {
  display: none;
}

.match-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid #ececec;
}

.match-panel-header h2 {
  margin: 0;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #666;
}

.match-count {
  font-size: 12px;
  font-weight: 600;
  color: #1e3a5f;
}

.match-empty {
  margin: 10px 14px;
  color: #7c8794;
  font-size: 12px;
}

.match-list {
  list-style: none;
  margin: 0;
  padding: 8px;
  overflow-y: auto;
  flex: 1;
}

.match-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.match-item:hover,
.match-item.match-hovered {
  background: #f0f6fc;
}

.match-item.match-selected {
  background: #e7f0fb;
  outline: 1px solid #a8c7e8;
}

.match-node-swatch {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  border: 1px solid transparent;
  flex-shrink: 0;
}

.match-node-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.match-node-type {
  font-size: 10px;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.side-panel {
  width: 0;
  flex-shrink: 0;
  background: #ffffff;
  border-left: 1px solid #e0e0e0;
  overflow-y: auto;
  transition: width 200ms ease-in-out;
}

.side-panel:not([hidden]) {
  width: 320px;
}

/* ------------------------------------------------------------------ */
/* Sidebar sections                                                    */
/* ------------------------------------------------------------------ */

.sidebar section {
  margin-bottom: 20px;
}

.sidebar h2 {
  margin: 0 0 8px 0;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #666;
}

.filter-collapsible {
  border: none;
}

.filter-collapsible-heading {
  margin: 0 0 8px 0;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #666;
  cursor: pointer;
  list-style: none;
  display: flex;
  align-items: center;
  gap: 5px;
  user-select: none;
}

.filter-collapsible-heading::before {
  content: "\\25BE";
  font-size: 10px;
  transition: transform 0.15s ease;
  display: inline-block;
}

.filter-collapsible:not([open]) .filter-collapsible-heading::before {
  transform: rotate(-90deg);
}

.sidebar label {
  display: block;
  padding: 3px 0;
  font-size: 13px;
  cursor: pointer;
}

.sidebar label input {
  margin-right: 6px;
}

.filter-buttons {
  margin-top: 8px;
  display: flex;
  gap: 6px;
}

.filter-buttons.filter-presets {
  margin-top: 6px;
}

.filter-subgroup {
  margin-top: 8px;
}
.filter-subgroup:first-child {
  margin-top: 0;
}
.filter-subgroup-label {
  display: block;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #78829a;
  margin-bottom: 3px;
}

.layout-buttons {
  margin-top: 8px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.filter-missing {
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px dashed #e0e0e0;
  font-size: 12px;
  color: #555;
}

.sidebar label:has(input:checked) {
  color: #1e3a5f;
  font-weight: 500;
}

.sidebar input[type="radio"]:checked + *,
.sidebar input[type="checkbox"]:checked + * {
  /* reserved for future icon-based active markers */
}

/* ------------------------------------------------------------------ */
/* Legend                                                              */
/* ------------------------------------------------------------------ */

.legend-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.legend-list li {
  display: flex;
  align-items: center;
  padding: 3px 0;
  font-size: 13px;
}

.swatch {
  display: inline-block;
  width: 12px;
  height: 12px;
  margin-right: 8px;
  border: 1px solid transparent;
  border-radius: 2px;
}

.swatch-skill        { background: #b8d5f2; border-color: #6da3d4; }
.swatch-skill-internal {
  background: #e8f0f9;
  border-color: #6da3d4;
  border-style: dashed;
}
.swatch-agent        { background: #e6d5ed; border-color: #a082b5; }
.swatch-script       { background: #d5e3ef; border-color: #7c9ab3; }
.swatch-rule         { background: #f8e6a8; border-color: #c9aa4d; }
.swatch-ref-general  { background: #cfe3cf; border-color: #7fa87f; }
.swatch-ref-template { background: #d7cce8; border-color: #9687b5; }
.swatch-ref-project  { background: #efcccc; border-color: #b58282; }
.swatch-edge-suggests {
  background: transparent;
  border: 0;
  border-top: 2px dashed #9a9a9a;
  height: 0;
  width: 16px;
  display: inline-block;
  vertical-align: middle;
  margin-right: 4px;
}
.swatch-edge-dispatches-inline {
  background: transparent;
  border: 0;
  border-top: 2px dashed #6da3d4;
  height: 0;
  width: 16px;
  display: inline-block;
  vertical-align: middle;
  margin-right: 4px;
}
.swatch-edge-dynamic-load {
  background: transparent;
  border: 0;
  border-top: 2px dotted #8a7fb5;
  height: 0;
  width: 16px;
  display: inline-block;
  vertical-align: middle;
  margin-right: 4px;
}
.swatch-edge-reads {
  background: transparent;
  border: 0;
  border-top: 2px solid #5aaa82;
  height: 0;
  width: 16px;
  display: inline-block;
  vertical-align: middle;
  margin-right: 4px;
}
.swatch-edge-conditional {
  background: transparent;
  border: 0;
  border-top: 2px dashed #7a7a7a;
  height: 0;
  width: 16px;
  display: inline-block;
  vertical-align: middle;
  margin-right: 4px;
}

/* ------------------------------------------------------------------ */
/* Buttons + disabled state                                            */
/* ------------------------------------------------------------------ */

button {
  font: inherit;
  padding: 4px 10px;
  border: 1px solid #c0c0c0;
  background: #f7f7f7;
  border-radius: 3px;
  cursor: pointer;
}

button:hover:not(:disabled) {
  background: #eee;
}

button:disabled,
input:disabled + *,
input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.sidebar label:has(input:disabled) {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ------------------------------------------------------------------ */
/* Responsive: collapse sidebar below 1024px                           */
/* ------------------------------------------------------------------ */

@media (max-width: 1023px) {
  .app {
    flex-direction: column;
  }
  .top-search {
    width: 100%;
  }
  .top-search input {
    flex: 1;
    max-width: none;
  }
  .sidebar {
    width: 100%;
    max-height: 180px;
    border-right: none;
    border-bottom: 1px solid #e0e0e0;
  }
  .match-panel {
    width: 100%;
    max-height: 220px;
    border-left: none;
    border-top: 1px solid #e0e0e0;
  }
  .side-panel:not([hidden]) {
    width: 100%;
  }
}

/* ------------------------------------------------------------------ */
/* Print styles                                                        */
/* ------------------------------------------------------------------ */

@media print {
  .sidebar,
  .side-panel,
  .export-buttons {
    display: none !important;
  }
  .top-bar {
    border-bottom: 1px solid #999;
  }
  .app {
    height: auto;
  }
  .cy-canvas {
    width: 100%;
    min-height: 80vh;
  }
}

/* ------------------------------------------------------------------ */
/* Side panel (Step 5)                                                 */
/* ------------------------------------------------------------------ */

.side-panel {
  display: flex;
  flex-direction: column;
}

.side-panel[hidden] {
  display: none;
}

.side-panel-header {
  position: sticky;
  top: 0;
  background: #ffffff;
  border-bottom: 1px solid #e0e0e0;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  z-index: 2;
}

.side-panel-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #1e3a5f;
  flex: 1;
  min-width: 0;
  word-break: break-word;
}

.side-panel-controls {
  display: flex;
  gap: 6px;
  margin-left: auto;
}

.side-panel-btn {
  font: inherit;
  font-size: 12px;
  padding: 3px 8px;
  border: 1px solid #c0c0c0;
  background: #f7f7f7;
  border-radius: 3px;
  cursor: pointer;
}

.side-panel-btn:hover {
  background: #eee;
}

.side-panel-btn[aria-pressed="true"] {
  background: #b8d5f2;
  border-color: #6da3d4;
  color: #1e3a5f;
}

.side-panel-close {
  font-size: 16px;
  line-height: 1;
  padding: 2px 8px;
}

.side-panel-body {
  padding: 12px 16px;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}

.type-badge {
  display: inline-block;
  padding: 3px 9px;
  border: 1px solid transparent;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.type-badge.type-skill        { background: #b8d5f2; border-color: #6da3d4; color: #1e3a5f; }
.type-badge.type-skill-internal {
  background: #e8f0f9;
  border-color: #6da3d4;
  border-style: dashed;
  color: #1e3a5f;
}
.type-badge.type-agent        { background: #e6d5ed; border-color: #a082b5; color: #3e2852; }
.type-badge.type-script       { background: #d5e3ef; border-color: #7c9ab3; color: #2a3e52; }
.type-badge.type-rule         { background: #f8e6a8; border-color: #c9aa4d; color: #5c4617; }
.type-badge.type-ref-general  { background: #cfe3cf; border-color: #7fa87f; color: #2d4a2d; }
.type-badge.type-ref-template { background: #d7cce8; border-color: #9687b5; color: #3e3566; }
.type-badge.type-ref-project  { background: #efcccc; border-color: #b58282; color: #663535; }

.side-panel-path-wrap {
  margin: 0 0 12px 0;
  font-size: 12px;
}

.side-panel-path {
  color: #4a6a8a;
  text-decoration: none;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  word-break: break-all;
}

.side-panel-path:hover {
  text-decoration: underline;
}

.side-panel-description {
  font-size: 13px;
  line-height: 1.5;
  color: #222;
}

.side-panel-description h4 {
  margin: 14px 0 4px 0;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #666;
}

.side-panel-description h4:first-child {
  margin-top: 0;
}

.side-panel-description p {
  margin: 0 0 10px 0;
}

.side-panel-description ul {
  margin: 0 0 10px 0;
  padding-left: 20px;
}

.side-panel-description code {
  background: #f3f3f3;
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 12px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}

.side-panel-description pre {
  background: #f3f3f3;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
}

.side-panel-description pre code {
  background: transparent;
  padding: 0;
}

.side-panel-description blockquote {
  border-left: 3px solid #b8d5f2;
  background: #f7fbff;
  margin: 0 0 10px 0;
  padding: 6px 10px;
  color: #1e3a5f;
  font-size: 12px;
}

.side-panel-description details {
  margin: 8px 0;
}

.side-panel-description summary {
  cursor: pointer;
  color: #4a6a8a;
  font-size: 12px;
}

.fallback-badge {
  display: inline-block;
  margin: 10px 0 14px 0;
  padding: 4px 10px;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 3px;
  color: #5c4617;
  font-size: 11px;
  font-style: italic;
}

.side-panel-section {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px dashed #e0e0e0;
}

.side-panel-section h3 {
  margin: 0 0 6px 0;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #666;
}

.edge-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.edge-list li {
  padding: 4px 6px;
  font-size: 12px;
  cursor: pointer;
  border-radius: 3px;
  display: flex;
  gap: 6px;
  align-items: baseline;
}

.edge-list li:hover {
  background: #f0f6fc;
}

.edge-list .edge-type-tag {
  font-size: 10px;
  text-transform: uppercase;
  color: #888;
  letter-spacing: 0.03em;
  flex-shrink: 0;
}

.edge-list .edge-empty {
  color: #999;
  font-style: italic;
  cursor: default;
}

.edge-list .edge-empty:hover {
  background: transparent;
}

#side-panel-outgoing-groups details {
  margin: 4px 0;
}

#side-panel-outgoing-groups summary {
  cursor: pointer;
  padding: 3px 0;
  font-size: 12px;
  color: #444;
  font-weight: 500;
}

/* Responsive: full-width drawer below 1024px */
@media (max-width: 1023px) {
  .side-panel:not([hidden]) {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    width: 100%;
    z-index: 20;
    box-shadow: -2px 0 10px rgba(0, 0, 0, 0.15);
  }
}

@media print {
  .side-panel {
    display: none !important;
  }
}
""")


JS_TEMPLATE = string.Template(r"""// SEJA harness call graph -- interactive viewer.
// Generated $generated_at by .claude/skills/scripts/generate_call_graph.py.
// Do not edit by hand.
//
// Step 4 wires the sidebar controls scaffolded in Step 3: per-type filter
// checkboxes (with select-all / deselect-all and a "missing designer copy"
// filter), edge-label toggle, layout switcher (cose/dagre/concentric),
// manual drag + position persistence, reset-layout, save-layout JSON
// download, SVG export (via cytoscape-svg) and PNG export (via cy.png).
// State persists across reloads via localStorage. No global pollution
// beyond window.__cy (already exposed in Step 3).

(async function () {
  if (window.cytoscapeFcose) cytoscape.use(window.cytoscapeFcose);
  if (window.cytoscapeCola) cytoscape.use(window.cytoscapeCola);
  if (window.cytoscapeSvg) cytoscape.use(window.cytoscapeSvg);

  // -----------------------------------------------------------------
  // localStorage key helpers
  // -----------------------------------------------------------------
  const LS_FILTER_PREFIX = 'callGraph:filter:';
  const LS_LAYOUT = 'callGraph:layout';
  const LS_POS_PREFIX = 'callGraph:pos:';
  const LS_HIDE_DISCONNECTED = 'callGraph:filter-hide-disconnected';
  const LS_HIDE_INTERNAL_SKILLS = 'callGraph:filter-hide-internal-skills';
  const LS_EDGE_FILTER_PREFIX = 'callGraph:edge-filter:';
  // New key (callGraph:filter-conditional-show) replaces the legacy
  // callGraph:filter-conditional-only key from the inverted-semantics filter.
  // Default semantic: checked = show conditional edges (matches every other
  // edge-type checkbox in the filter group). Fresh key bypasses any stuck
  // 'true' from the legacy filter that would have hidden conditional edges.
  const LS_CONDITIONAL_SHOW = 'callGraph:filter-conditional-show';

  function lsGet(key, fallback) {
    try {
      const v = window.localStorage.getItem(key);
      return v === null ? fallback : v;
    } catch (_e) {
      return fallback;
    }
  }

  function lsSet(key, value) {
    try {
      window.localStorage.setItem(key, value);
    } catch (_e) {
      /* quota or disabled storage -- ignore */
    }
  }

  function lsRemove(key) {
    try {
      window.localStorage.removeItem(key);
    } catch (_e) {
      /* ignore */
    }
  }

  function lsListKeys(prefix) {
    const keys = [];
    try {
      for (let i = 0; i < window.localStorage.length; i++) {
        const k = window.localStorage.key(i);
        if (k && k.indexOf(prefix) === 0) keys.push(k);
      }
    } catch (_e) {
      /* ignore */
    }
    return keys;
  }

  // -----------------------------------------------------------------
  // Load graph data
  // -----------------------------------------------------------------
  let data;
  try {
    const response = await fetch('./call-graph.json');
    if (!response.ok) throw new Error('fetch failed: ' + response.status);
    data = await response.json();
  } catch (err) {
    document.getElementById('cy').textContent =
      'Could not load call-graph.json: ' + err.message;
    return;
  }

  const elements = [
    ...data.nodes.map(function (n) {
      return {
        data: {
          id: n.id,
          label: n.label,
          type: n.type,
          path: n.path,
          user_invocable: n.user_invocable,
          description_source: n.description_source || 'developer-fallback'
        }
      };
    }),
    ...data.edges.map(function (e) {
      // Populate `when` (flag label) and `conditional` only on edges that are
      // actually conditional -- when omitted entirely, the `[conditional]`
      // attribute-defined selector in the style array cleanly discriminates.
      // Earlier versions set `conditional: false` on every edge and relied on
      // the `[?conditional]` truthy selector, which proved unreliable in
      // Cytoscape 3.30.4 for boolean-typed data. Attribute-presence is a
      // stronger contract.
      const when = e.when || '';
      const isConditional = !!(e.conditional || when);
      const data = {
        id: e.source + '|' + e.type + '|' + e.target,
        source: e.source,
        target: e.target,
        type: e.type,
        label: e.label || ''
      };
      if (isConditional) {
        data.when = when;
        data.conditional = true;
      }
      if (e.primary) { data.primary = true; }
      return { data: data };
    })
  ];

  const typeColors = {
    'skill':          { bg: '#b8d5f2', border: '#6da3d4', color: '#1e3a5f' },
    // Internal (Dispatch B) worker skills -- lighter tint, dashed border.
    'skill-internal': { bg: '#e8f0f9', border: '#6da3d4', color: '#1e3a5f' },
    'agent':          { bg: '#e6d5ed', border: '#a082b5', color: '#3e2852' },
    'script':         { bg: '#d5e3ef', border: '#7c9ab3', color: '#2a3e52' },
    'rule':           { bg: '#f8e6a8', border: '#c9aa4d', color: '#5c4617' },
    'ref-general':    { bg: '#cfe3cf', border: '#7fa87f', color: '#2d4a2d' },
    'ref-template':   { bg: '#d7cce8', border: '#9687b5', color: '#3e3566' },
    'ref-project':    { bg: '#efcccc', border: '#b58282', color: '#663535' }
  };

  const nodeStyle = Object.entries(typeColors).map(function (entry) {
    const type = entry[0];
    const c = entry[1];
    const style = {
      'background-color': c.bg,
      'border-color': c.border,
      'border-width': 1.5,
      'color': c.color,
      'label': 'data(label)',
      'font-size': 10,
      'text-valign': 'center',
      'text-halign': 'center',
      'width': 'label',
      'height': 'label',
      'padding': 8,
      'shape': 'round-rectangle'
    };
    // Dashed border on internal-worker skill nodes so they stand apart
    // from user-facing skills at a glance (Cytoscape borders default to solid).
    if (type === 'skill-internal') {
      style['border-style'] = 'dashed';
    }
    return {
      selector: 'node[type = "' + type + '"]',
      style: style
    };
  });

  // -----------------------------------------------------------------
  // Layout options
  // -----------------------------------------------------------------
  const layoutOptions = {
    'fcose': {
      // Successor to cose-bilkent, same author (Bilkent). Better quality
      // and faster than cose-bilkent at 200+ nodes; handles hub-and-spoke
      // topologies more cleanly. Falls back to built-in cose if the
      // extension did not register.
      name: (window.cytoscapeFcose ? 'fcose' : 'cose'),
      animate: 'end',
      animationDuration: 400,
      fit: true,
      padding: 40,
      quality: 'default',
      nodeRepulsion: 4500,
      idealEdgeLength: 100,
      edgeElasticity: 0.45,
      nestingFactor: 0.1,
      gravity: 0.25,
      numIter: 2500,
      randomize: false
    },
    'cola': {
      // Constraint-based force layout (WebCola). With `flow: {axis: 'y'}`
      // it produces a soft downward hierarchy -- the top-to-bottom
      // readability that dagre promised but without dagre's cluttered
      // rendering on dense graphs. Falls back to built-in cose if the
      // extension did not register.
      name: (window.cytoscapeCola ? 'cola' : 'cose'),
      animate: true,
      animationDuration: 400,
      fit: true,
      padding: 40,
      maxSimulationTime: 3000,
      nodeSpacing: 20,
      edgeLength: 100,
      flow: { axis: 'y', minSeparation: 40 },
      avoidOverlap: true
    },
    'concentric': {
      name: 'concentric',
      animate: 'end',
      animationDuration: 400,
      fit: true,
      padding: 40,
      concentric: function (node) {
        // Outer rings = lower priority; skills are innermost.
        const typeOrder = {
          'skill': 5,
          'skill-internal': 5,
          'agent': 4,
          'script': 3,
          'rule': 2,
          'ref-general': 1,
          'ref-template': 1,
          'ref-project': 1
        };
        return typeOrder[node.data('type')] || 0;
      },
      levelWidth: function () { return 1; },
      minNodeSpacing: 12,
      spacingFactor: 0.6,
      avoidOverlap: true
    }
  };

  // Restore last layout choice (default 'fcose'). Legacy `cose` / `dagre`
  // values from pre-swap localStorage fall back to 'fcose'.
  const initialLayout = lsGet(LS_LAYOUT, 'fcose');
  const validLayout = layoutOptions[initialLayout] ? initialLayout : 'fcose';

  const cy = cytoscape({
    container: document.getElementById('cy'),
    boxSelectionEnabled: true,
    elements: elements,
    style: [
      ...nodeStyle,
      {
        selector: 'edge',
        style: {
          'width': 1,
          'line-color': '#b0b0b0',
          'target-arrow-color': '#b0b0b0',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          'arrow-scale': 0.8,
          'font-size': 8,
          'color': '#555',
          'text-background-color': '#ffffff',
          'text-background-opacity': 0.8,
          'text-background-padding': 2
        }
      },
      {
        // Secondary suggests edges (post-completion hints, non-first per source)
        // render dotted so they read as background context behind the primary hint.
        selector: 'edge[type = "suggests"]',
        style: {
          'line-style': 'dotted',
          'line-color': '#9a9a9a',
          'target-arrow-color': '#9a9a9a',
          'opacity': 0.65
        }
      },
      {
        // Primary suggests edge (first in reading order from skill-graph.json
        // for each source skill) renders dashed — more prominent than secondary.
        selector: 'edge[type = "suggests"][?primary]',
        style: {
          'line-style': 'dashed',
          'opacity': 0.80
        }
      },
      {
        // Dispatches-inline edges (wrapper -> internal worker -- Dispatch B
        // per the mode factoring pattern) are dashed and tinted with the
        // skill-family border color so the wrapper->internal relationship
        // reads as a skill relationship rather than a suggestion. Distinct
        // from the generic `suggests` gray and the `dynamic-load` purple.
        selector: 'edge[type = "dispatches-inline"]',
        style: {
          'line-style': 'dashed',
          'line-color': '#6da3d4',
          'target-arrow-color': '#6da3d4',
          'opacity': 0.85
        }
      },
      {
        // Dynamic-load edges (refs loaded by skill/agent at runtime based
        // on an argument, e.g. role, audience, perspective) are dotted and
        // tinted soft purple so they are distinct from dashed suggests.
        selector: 'edge[type = "dynamic-load"]',
        style: {
          'line-style': 'dotted',
          'line-color': '#8a7fb5',
          'target-arrow-color': '#8a7fb5',
          'opacity': 0.8
        }
      },
      {
        // Reads edges (explicit _references/ path mentioned in prose or code)
        // are solid and tinted teal-green so they are clearly distinct from
        // the skill-orchestration navy/gray, the ref-load purple, and
        // the conditional amber.
        selector: 'edge[type = "reads"]',
        style: {
          'line-style': 'solid',
          'line-color': '#5aaa82',
          'target-arrow-color': '#5aaa82',
          'opacity': 0.7
        }
      },
      {
        // Conditional edges (fire only under a named flag) are dashed with a
        // tighter dash pattern, a bolder width, an amber stroke, and an
        // always-visible flag pill. The amber/orange palette is unique among
        // edge classes (suggests = pale gray, dynamic-load = soft purple, all
        // others = neutral gray) so the reader can spot the 1-2 conditional
        // edges among 300+ without hunting. Uses `[conditional]` attribute-
        // defined selector rather than `[?conditional]` truthy selector
        // because the data mapping only sets the attribute on actually-
        // conditional edges -- attribute-presence is a stronger contract than
        // truthiness on boolean-typed data in Cytoscape 3.30.4.
        selector: 'edge[conditional]',
        style: {
          'line-style': 'dashed',
          'line-dash-pattern': [6, 2],
          'line-color': '#d97706',
          'target-arrow-color': '#d97706',
          'width': 2.5,
          'label': 'data(when)',
          'font-size': 11,
          'font-weight': 'bold',
          'color': '#7c2d12',
          'text-background-color': '#fef3c7',
          'text-background-opacity': 1,
          'text-background-padding': 3,
          'text-background-shape': 'roundrectangle',
          'text-border-color': '#d97706',
          'text-border-width': 1,
          'text-border-opacity': 1
        }
      },
      {
        // Focus mode: nodes/edges outside the clicked node's 1-hop
        // neighborhood are faded. Opacity is set to keep non-neighbors
        // clearly secondary but still legible (text-opacity higher than
        // node-opacity so labels read against the fainter shapes).
        selector: '.faded',
        style: {
          'opacity': 0.40,
          'text-opacity': 0.55
        }
      },
      {
        // Search matches are ring-highlighted so they remain readable
        // while still standing out from non-matches.
        selector: 'node.search-match',
        style: {
          'border-width': 3,
          'border-color': '#2a9d8f',
          'overlay-color': '#2a9d8f',
          'overlay-opacity': 0.1,
          'overlay-padding': 4
        }
      },
      {
        // Hover sync between sidebar list rows and canvas nodes.
        selector: 'node.search-hovered',
        style: {
          'border-width': 4,
          'border-color': '#e76f51',
          'overlay-color': '#e76f51',
          'overlay-opacity': 0.14,
          'overlay-padding': 6
        }
      },
      {
        // Selected nodes get a thicker, distinctly-coloured border so the
        // selection is unambiguous regardless of node type or background.
        selector: 'node:selected',
        style: {
          'border-width': 3.5,
          'border-color': '#1e6fb5',
          'overlay-color': '#1e6fb5',
          'overlay-opacity': 0.12,
          'overlay-padding': 4
        }
      }
    ],
    wheelSensitivity: 0.25
  });

  window.__cy = cy;

  const searchInput = document.getElementById('node-search-input');
  const searchClearBtn = document.getElementById('node-search-clear');
  const matchPanel = document.getElementById('match-panel');
  const matchPanelEmpty = document.getElementById('match-panel-empty');
  const matchList = document.getElementById('match-list');
  const matchCount = document.getElementById('match-count');

  let searchTerm = '';
  let matchedNodeIds = new Set();
  let hoveredMatchNodeId = null;
  const matchListItemByNodeId = {};

  function setMatchPanelOpen(isOpen) {
    if (!matchPanel) return;
    matchPanel.hidden = !isOpen;
    matchPanel.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
  }

  // Track the currently active layout name (logical key, not the
  // cytoscape-extension name). Needed for position persistence keys.
  let currentLayout = validLayout;

  // -----------------------------------------------------------------
  // Position persistence
  // -----------------------------------------------------------------
  function posKey(layoutName, nodeId) {
    return LS_POS_PREFIX + layoutName + ':' + nodeId;
  }

  function applySavedPositions(layoutName) {
    cy.nodes().forEach(function (node) {
      const raw = lsGet(posKey(layoutName, node.id()), null);
      if (!raw) return;
      try {
        const pos = JSON.parse(raw);
        if (typeof pos.x === 'number' && typeof pos.y === 'number') {
          node.position({ x: pos.x, y: pos.y });
        }
      } catch (_e) {
        /* bad JSON -- ignore */
      }
    });
  }

  function clearSavedPositions(layoutName) {
    const prefix = LS_POS_PREFIX + layoutName + ':';
    lsListKeys(prefix).forEach(function (k) { lsRemove(k); });
  }

  function runLayout(layoutName) {
    const opts = layoutOptions[layoutName];
    if (!opts) return;
    currentLayout = layoutName;
    const layout = cy.layout(opts);
    layout.one('layoutstop', function () {
      applySavedPositions(layoutName);
      cy.fit(undefined, 40);
    });
    layout.run();
  }

  // Persist node positions on drag end.
  cy.on('dragfreeon', 'node', function (evt) {
    const node = evt.target;
    const pos = node.position();
    lsSet(
      posKey(currentLayout, node.id()),
      JSON.stringify({ x: pos.x, y: pos.y })
    );
  });

  function setHoveredMatchNode(nodeId) {
    if (hoveredMatchNodeId === nodeId) return;

    if (hoveredMatchNodeId) {
      const prevEl = cy.getElementById(hoveredMatchNodeId);
      if (prevEl && !prevEl.empty()) prevEl.removeClass('search-hovered');
      const prevRow = matchListItemByNodeId[hoveredMatchNodeId];
      if (prevRow) prevRow.classList.remove('match-hovered');
    }

    hoveredMatchNodeId = null;

    if (!nodeId || !matchedNodeIds.has(nodeId)) return;

    const nodeEl = cy.getElementById(nodeId);
    if (nodeEl && !nodeEl.empty()) nodeEl.addClass('search-hovered');
    const row = matchListItemByNodeId[nodeId];
    if (row) row.classList.add('match-hovered');
    hoveredMatchNodeId = nodeId;
  }

  function updateMatchSelection() {
    Object.keys(matchListItemByNodeId).forEach(function (nodeId) {
      const row = matchListItemByNodeId[nodeId];
      if (!row) return;
      row.classList.toggle('match-selected', nodeId === currentPanelNodeId);
    });
  }

  function applyNodeSearch() {
    const query = String(searchTerm || '').trim().toLowerCase();

    matchedNodeIds = new Set();
    cy.nodes().removeClass('search-match search-hovered');

    Object.keys(matchListItemByNodeId).forEach(function (k) {
      delete matchListItemByNodeId[k];
    });
    matchList.innerHTML = '';

    if (!query) {
      setMatchPanelOpen(false);
      matchCount.textContent = '0';
      matchPanelEmpty.textContent = 'Type in "Search nodes" to highlight matching labels.';
      matchPanelEmpty.hidden = false;
      setHoveredMatchNode(null);
      return;
    }

    setMatchPanelOpen(true);

    const matchedNodes = [];
    sortedNodes.forEach(function (node) {
      const nodeEl = cy.getElementById(node.id);
      if (!nodeEl || nodeEl.empty()) return;
      if (nodeEl.style('display') === 'none') return;
      const hay = ((node.label || '') + ' ' + node.id).toLowerCase();
      if (hay.indexOf(query) === -1) return;
      matchedNodes.push(node);
      matchedNodeIds.add(node.id);
      nodeEl.addClass('search-match');
    });

    matchCount.textContent = String(matchedNodes.length);
    if (!matchedNodes.length) {
      matchPanelEmpty.textContent = 'No visible nodes match "' + query + '".';
      matchPanelEmpty.hidden = false;
      setHoveredMatchNode(null);
      return;
    }

    matchPanelEmpty.hidden = true;

    matchedNodes.forEach(function (node) {
      const item = document.createElement('li');
      item.className = 'match-item';
      item.setAttribute('role', 'button');
      item.setAttribute('tabindex', '0');
      item.dataset.nodeId = node.id;

      const swatch = document.createElement('span');
      swatch.className = 'match-node-swatch swatch swatch-' + node.type;

      const label = document.createElement('span');
      label.className = 'match-node-label';
      label.textContent = node.label || node.id;

      const type = document.createElement('span');
      type.className = 'match-node-type';
      type.textContent = (TYPE_LABELS[node.type] || node.type);

      item.appendChild(swatch);
      item.appendChild(label);
      item.appendChild(type);

      item.addEventListener('mouseenter', function () {
        setHoveredMatchNode(node.id);
      });
      item.addEventListener('mouseleave', function () {
        setHoveredMatchNode(null);
      });
      item.addEventListener('click', function () {
        openPanel(node.id);
        focusNeighborhood(node.id);
      });
      item.addEventListener('keydown', function (evt) {
        if (evt.key === 'Enter' || evt.key === ' ') {
          evt.preventDefault();
          openPanel(node.id);
          focusNeighborhood(node.id);
        }
      });

      matchList.appendChild(item);
      matchListItemByNodeId[node.id] = item;
    });

    updateMatchSelection();
    setHoveredMatchNode(null);
  }

  if (searchInput) {
    searchInput.addEventListener('input', function () {
      searchTerm = searchInput.value || '';
      applyNodeSearch();
    });
  }

  if (searchClearBtn) {
    searchClearBtn.addEventListener('click', function () {
      searchTerm = '';
      if (searchInput) searchInput.value = '';
      applyNodeSearch();
      if (searchInput) searchInput.focus();
    });
  }

  cy.on('mouseover', 'node', function (evt) {
    const nodeId = evt.target.id();
    if (matchedNodeIds.has(nodeId)) {
      setHoveredMatchNode(nodeId);
    }
  });

  cy.on('mouseout', 'node', function (evt) {
    const nodeId = evt.target.id();
    if (hoveredMatchNodeId === nodeId) {
      setHoveredMatchNode(null);
    }
  });

  // -----------------------------------------------------------------
  // Filter checkboxes per node type
  // -----------------------------------------------------------------
  const filterCheckboxes = Array.from(
    document.querySelectorAll('input.filter-type')
  );

  function isPrimaryEdgeTypeCheckbox(cb) {
    // Keep conditional visibility independent from edge-type bulk toggles.
    return cb && cb.id !== 'filter-conditional-show';
  }

  function updateNodeVisibility() {
    const enabledTypes = new Set(
      filterCheckboxes
        .filter(function (cb) { return cb.checked; })
        .map(function (cb) { return cb.value; })
    );
    const enabledEdgeTypes = new Set(
      Array.prototype.slice.call(
        document.querySelectorAll('input.filter-edge-type')
      ).filter(function (cb) {
        return isPrimaryEdgeTypeCheckbox(cb) && cb.checked;
      })
       .map(function (cb) { return cb.value; })
    );
    const hideDisconnected = document.getElementById('filter-hide-disconnected');
    const hideDisconnectedActive = hideDisconnected && hideDisconnected.checked;
    const hideInternalSkills = document.getElementById('filter-hide-internal-skills');
    const hideInternalSkillsActive = hideInternalSkills && hideInternalSkills.checked;
    // Positive-semantics conditional filter: checkbox lives in the "Other"
    // subgroup of "Filter by edge type" and reads "show conditional edges".
    // Default checked. Hide condition: !shown && edge has `conditional`.
    const conditionalShow = document.getElementById('filter-conditional-show');
    const conditionalEdgesShown = !conditionalShow || conditionalShow.checked;

    cy.batch(function () {
      const visibleByType = new Map();
      cy.nodes().forEach(function (node) {
        const type = node.data('type');
        let visible = enabledTypes.has(type);
        if (
          visible &&
          hideInternalSkillsActive &&
          type === 'skill' &&
          node.data('user_invocable') === false
        ) {
          visible = false;
        }
        visibleByType.set(node.id(), visible);
      });

      if (hideDisconnectedActive) {
        // A node is "disconnected" relative to the current filter set when
        // none of its incident edges (of an enabled edge type) have both
        // endpoints in the provisionally-visible set. Hide those.
        const degree = new Map();
        cy.edges().forEach(function (edge) {
          if (!enabledEdgeTypes.has(edge.data('type'))) return;
          if (!conditionalEdgesShown && edge.data('conditional')) return;
          const s = edge.source().id();
          const t = edge.target().id();
          if (visibleByType.get(s) && visibleByType.get(t)) {
            degree.set(s, (degree.get(s) || 0) + 1);
            degree.set(t, (degree.get(t) || 0) + 1);
          }
        });
        cy.nodes().forEach(function (node) {
          if (visibleByType.get(node.id()) && !degree.get(node.id())) {
            visibleByType.set(node.id(), false);
          }
        });
      }

      cy.nodes().forEach(function (node) {
        node.style(
          'display',
          visibleByType.get(node.id()) ? 'element' : 'none'
        );
      });

      cy.edges().forEach(function (edge) {
        const srcHidden = edge.source().style('display') === 'none';
        const tgtHidden = edge.target().style('display') === 'none';
        const typeDisabled = !enabledEdgeTypes.has(edge.data('type'));
        const conditionalHidden = !conditionalEdgesShown && edge.data('conditional');
        edge.style(
          'display',
          (srcHidden || tgtHidden || typeDisabled || conditionalHidden) ? 'none' : 'element'
        );
      });
    });

    applyNodeSearch();
  }

  function fitToVisible() {
    const visible = cy.elements().filter(function (el) {
      return el.style('display') !== 'none';
    });
    if (visible.length === 0) return;
    cy.animate(
      { fit: { eles: visible, padding: 40 } },
      { duration: 300, easing: 'ease-in-out-quad' }
    );
  }

  function restoreFilterState() {
    filterCheckboxes.forEach(function (cb) {
      const stored = lsGet(LS_FILTER_PREFIX + cb.value, null);
      if (stored !== null) {
        cb.checked = stored === 'true';
      }
      cb.setAttribute('aria-checked', cb.checked ? 'true' : 'false');
    });
    const hideDisc = document.getElementById('filter-hide-disconnected');
    if (hideDisc) {
      const stored = lsGet(LS_HIDE_DISCONNECTED, 'false');
      hideDisc.checked = stored === 'true';
      hideDisc.setAttribute('aria-checked', hideDisc.checked ? 'true' : 'false');
    }
    const hideInternal = document.getElementById('filter-hide-internal-skills');
    if (hideInternal) {
      const stored = lsGet(LS_HIDE_INTERNAL_SKILLS, 'false');
      hideInternal.checked = stored === 'true';
      hideInternal.setAttribute(
        'aria-checked',
        hideInternal.checked ? 'true' : 'false'
      );
    }
    const condShow = document.getElementById('filter-conditional-show');
    if (condShow) {
      // Default 'true' (checked, conditional edges visible) when the key is
      // absent. The legacy LS_CONDITIONAL_ONLY key is intentionally NOT read
      // so a stuck 'true' from the inverted-semantics filter cannot bleed
      // through and silently hide conditional edges on first load.
      const stored = lsGet(LS_CONDITIONAL_SHOW, 'true');
      condShow.checked = stored === 'true';
      condShow.setAttribute('aria-checked', condShow.checked ? 'true' : 'false');
    }
    Array.prototype.slice.call(
      document.querySelectorAll('input.filter-edge-type')
    ).forEach(function (cb) {
      if (!isPrimaryEdgeTypeCheckbox(cb)) return;
      const stored = lsGet(LS_EDGE_FILTER_PREFIX + cb.value, null);
      if (stored !== null) {
        cb.checked = stored === 'true';
      }
      cb.setAttribute('aria-checked', cb.checked ? 'true' : 'false');
    });
  }

  filterCheckboxes.forEach(function (cb) {
    cb.addEventListener('change', function () {
      lsSet(LS_FILTER_PREFIX + cb.value, cb.checked ? 'true' : 'false');
      cb.setAttribute('aria-checked', cb.checked ? 'true' : 'false');
      updateNodeVisibility();
    });
  });

  const filterAllBtn = document.getElementById('filter-all');
  if (filterAllBtn) {
    filterAllBtn.addEventListener('click', function () {
      filterCheckboxes.forEach(function (cb) {
        cb.checked = true;
        cb.setAttribute('aria-checked', 'true');
        lsSet(LS_FILTER_PREFIX + cb.value, 'true');
      });
      updateNodeVisibility();
    });
  }

  const filterNoneBtn = document.getElementById('filter-none');
  if (filterNoneBtn) {
    filterNoneBtn.addEventListener('click', function () {
      filterCheckboxes.forEach(function (cb) {
        cb.checked = false;
        cb.setAttribute('aria-checked', 'false');
        lsSet(LS_FILTER_PREFIX + cb.value, 'false');
      });
      updateNodeVisibility();
    });
  }

  const hideDisconnectedCheckbox = document.getElementById('filter-hide-disconnected');
  if (hideDisconnectedCheckbox) {
    hideDisconnectedCheckbox.addEventListener('change', function () {
      lsSet(LS_HIDE_DISCONNECTED, hideDisconnectedCheckbox.checked ? 'true' : 'false');
      hideDisconnectedCheckbox.setAttribute(
        'aria-checked',
        hideDisconnectedCheckbox.checked ? 'true' : 'false'
      );
      updateNodeVisibility();
      fitToVisible();
    });
  }

  const hideInternalSkillsCheckbox = document.getElementById('filter-hide-internal-skills');
  if (hideInternalSkillsCheckbox) {
    hideInternalSkillsCheckbox.addEventListener('change', function () {
      lsSet(
        LS_HIDE_INTERNAL_SKILLS,
        hideInternalSkillsCheckbox.checked ? 'true' : 'false'
      );
      hideInternalSkillsCheckbox.setAttribute(
        'aria-checked',
        hideInternalSkillsCheckbox.checked ? 'true' : 'false'
      );
      updateNodeVisibility();
      fitToVisible();
    });
  }

  const userFacingPresetBtn = document.getElementById('filter-preset-user-facing');
  if (userFacingPresetBtn) {
    userFacingPresetBtn.addEventListener('click', function () {
      filterCheckboxes.forEach(function (cb) {
        const checked = cb.value === 'skill';
        cb.checked = checked;
        cb.setAttribute('aria-checked', checked ? 'true' : 'false');
        lsSet(LS_FILTER_PREFIX + cb.value, checked ? 'true' : 'false');
      });
      if (hideInternalSkillsCheckbox) {
        hideInternalSkillsCheckbox.checked = true;
        hideInternalSkillsCheckbox.setAttribute('aria-checked', 'true');
        lsSet(LS_HIDE_INTERNAL_SKILLS, 'true');
      }
      updateNodeVisibility();
      fitToVisible();
    });
  }

  const fullPresetBtn = document.getElementById('filter-preset-full');
  if (fullPresetBtn) {
    fullPresetBtn.addEventListener('click', function () {
      filterCheckboxes.forEach(function (cb) {
        cb.checked = true;
        cb.setAttribute('aria-checked', 'true');
        lsSet(LS_FILTER_PREFIX + cb.value, 'true');
      });
      if (hideInternalSkillsCheckbox) {
        hideInternalSkillsCheckbox.checked = false;
        hideInternalSkillsCheckbox.setAttribute('aria-checked', 'false');
        lsSet(LS_HIDE_INTERNAL_SKILLS, 'false');
      }
      updateNodeVisibility();
      fitToVisible();
    });
  }

  const conditionalShowCheckbox = document.getElementById('filter-conditional-show');
  if (conditionalShowCheckbox) {
    conditionalShowCheckbox.addEventListener('change', function () {
      lsSet(LS_CONDITIONAL_SHOW, conditionalShowCheckbox.checked ? 'true' : 'false');
      conditionalShowCheckbox.setAttribute(
        'aria-checked',
        conditionalShowCheckbox.checked ? 'true' : 'false'
      );
      updateNodeVisibility();
    });
  }

  // Edge-type filter checkboxes + select-all / deselect-all buttons.
  const edgeTypeCheckboxes = Array.prototype.slice.call(
    document.querySelectorAll('input.filter-edge-type')
  ).filter(function (cb) {
    return isPrimaryEdgeTypeCheckbox(cb);
  });
  edgeTypeCheckboxes.forEach(function (cb) {
    cb.addEventListener('change', function () {
      lsSet(LS_EDGE_FILTER_PREFIX + cb.value, cb.checked ? 'true' : 'false');
      cb.setAttribute('aria-checked', cb.checked ? 'true' : 'false');
      updateNodeVisibility();
    });
  });

  const edgeFilterAllBtn = document.getElementById('edge-filter-all');
  if (edgeFilterAllBtn) {
    edgeFilterAllBtn.addEventListener('click', function () {
      edgeTypeCheckboxes.forEach(function (cb) {
        cb.checked = true;
        cb.setAttribute('aria-checked', 'true');
        lsSet(LS_EDGE_FILTER_PREFIX + cb.value, 'true');
      });
      if (conditionalShowCheckbox) {
        conditionalShowCheckbox.checked = true;
        conditionalShowCheckbox.setAttribute('aria-checked', 'true');
        lsSet(LS_CONDITIONAL_SHOW, 'true');
      }
      updateNodeVisibility();
    });
  }
  const edgeFilterNoneBtn = document.getElementById('edge-filter-none');
  if (edgeFilterNoneBtn) {
    edgeFilterNoneBtn.addEventListener('click', function () {
      edgeTypeCheckboxes.forEach(function (cb) {
        cb.checked = false;
        cb.setAttribute('aria-checked', 'false');
        lsSet(LS_EDGE_FILTER_PREFIX + cb.value, 'false');
      });
      if (conditionalShowCheckbox) {
        conditionalShowCheckbox.checked = false;
        conditionalShowCheckbox.setAttribute('aria-checked', 'false');
        lsSet(LS_CONDITIONAL_SHOW, 'false');
      }
      updateNodeVisibility();
    });
  }

  // -----------------------------------------------------------------
  // Layout switcher
  // -----------------------------------------------------------------
  const layoutRadios = Array.from(
    document.querySelectorAll('input[name="layout"]')
  );

  function syncLayoutRadioAria() {
    layoutRadios.forEach(function (radio) {
      radio.setAttribute('aria-checked', radio.checked ? 'true' : 'false');
    });
  }

  // Restore last layout selection in the radios.
  layoutRadios.forEach(function (radio) {
    radio.checked = (radio.value === currentLayout);
  });
  syncLayoutRadioAria();

  layoutRadios.forEach(function (radio) {
    radio.addEventListener('change', function () {
      if (!radio.checked) return;
      lsSet(LS_LAYOUT, radio.value);
      syncLayoutRadioAria();
      runLayout(radio.value);
    });
  });

  const layoutFitBtn = document.getElementById('layout-fit');
  if (layoutFitBtn) {
    layoutFitBtn.addEventListener('click', function () {
      fitToVisible();
    });
  }

  // Reset-layout: clear saved positions for current layout, re-run.
  const layoutResetBtn = document.getElementById('layout-reset');
  if (layoutResetBtn) {
    layoutResetBtn.addEventListener('click', function () {
      clearSavedPositions(currentLayout);
      runLayout(currentLayout);
    });
  }

  // -----------------------------------------------------------------
  // Save layout (download JSON)
  // -----------------------------------------------------------------
  function formatDateForFilename(d) {
    const yyyy = d.getUTCFullYear();
    const mm = String(d.getUTCMonth() + 1).padStart(2, '0');
    const dd = String(d.getUTCDate()).padStart(2, '0');
    return yyyy + '-' + mm + '-' + dd;
  }

  function triggerDownload(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 0);
  }

  const layoutSaveBtn = document.getElementById('layout-save');
  if (layoutSaveBtn) {
    layoutSaveBtn.addEventListener('click', function () {
      const positions = {};
      cy.nodes().forEach(function (node) {
        const p = node.position();
        positions[node.id()] = { x: p.x, y: p.y };
      });
      const payload = {
        layout: currentLayout,
        saved: new Date().toISOString(),
        positions: positions
      };
      const blob = new Blob(
        [JSON.stringify(payload, null, 2)],
        { type: 'application/json' }
      );
      const filename = 'call-graph-layout-' + currentLayout + '-' +
        formatDateForFilename(new Date()) + '.json';
      triggerDownload(blob, filename);
    });
  }

  // -----------------------------------------------------------------
  // Load layout (upload JSON)
  // -----------------------------------------------------------------
  const layoutLoadBtn = document.getElementById('layout-load');
  const layoutLoadInput = document.getElementById('layout-load-input');
  if (layoutLoadBtn && layoutLoadInput) {
    layoutLoadBtn.addEventListener('click', function () {
      layoutLoadInput.value = '';  // allow re-selecting the same file
      layoutLoadInput.click();
    });
    layoutLoadInput.addEventListener('change', function () {
      const file = layoutLoadInput.files && layoutLoadInput.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = function () {
        let payload;
        try {
          payload = JSON.parse(reader.result);
        } catch (err) {
          window.alert('Could not parse layout file as JSON: ' + err.message);
          return;
        }
        const positions = payload && payload.positions;
        if (!positions || typeof positions !== 'object') {
          window.alert('Layout file is missing a "positions" object.');
          return;
        }
        let applied = 0;
        let missing = 0;
        cy.batch(function () {
          Object.keys(positions).forEach(function (nodeId) {
            const node = cy.getElementById(nodeId);
            if (node && !node.empty()) {
              const p = positions[nodeId];
              if (p && typeof p.x === 'number' && typeof p.y === 'number') {
                node.position({ x: p.x, y: p.y });
                // Persist to localStorage under the CURRENT layout key so
                // the loaded arrangement survives a reload even if the
                // user later re-runs or switches layouts.
                lsSet(posKey(currentLayout, nodeId), JSON.stringify(p));
                applied += 1;
              }
            } else {
              missing += 1;
            }
          });
        });
        cy.fit(undefined, 40);
        let msg = 'Loaded ' + applied + ' node position' +
          (applied === 1 ? '' : 's') + ' from ' + file.name + '.';
        if (missing > 0) {
          msg += ' ' + missing + ' node id' +
            (missing === 1 ? '' : 's') +
            ' in the file did not match the current graph (skipped).';
        }
        if (payload.layout && payload.layout !== currentLayout) {
          msg += ' Note: the file was saved under the "' + payload.layout +
            '" layout; positions have been applied on top of the current "' +
            currentLayout + '" layout.';
        }
        if (window.console) console.info(msg);
      };
      reader.onerror = function () {
        window.alert('Could not read layout file.');
      };
      reader.readAsText(file);
    });
  }

  // -----------------------------------------------------------------
  // Export SVG / PNG
  // -----------------------------------------------------------------
  const exportSvgBtn = document.getElementById('export-svg');
  if (exportSvgBtn) {
    exportSvgBtn.addEventListener('click', function () {
      if (typeof cy.svg !== 'function') {
        window.alert('SVG export requires the cytoscape-svg extension.');
        return;
      }
      const svgStr = cy.svg({ full: true, scale: 2 });
      const blob = new Blob([svgStr], { type: 'image/svg+xml' });
      triggerDownload(blob, 'call-graph-' + currentLayout + '.svg');
    });
  }

  const exportPngBtn = document.getElementById('export-png');
  if (exportPngBtn) {
    exportPngBtn.addEventListener('click', function () {
      const dataUrl = cy.png({ full: true, scale: 2, bg: '#ffffff' });
      const a = document.createElement('a');
      a.href = dataUrl;
      a.download = 'call-graph-' + currentLayout + '.png';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    });
  }

  // -----------------------------------------------------------------
  // Side panel (Step 5) -- node descriptions, edges, pin/close/esc/arrows.
  // -----------------------------------------------------------------
  const LS_PANEL_OPEN = 'callGraph:panel:open';
  const LS_PANEL_PINNED = 'callGraph:panel:pinned';
  const LS_PANEL_LAST_NODE = 'callGraph:panel:lastNode';

  // Cache: id -> node data (faster than Array.find on every click).
  const nodeById = {};
  data.nodes.forEach(function (n) { nodeById[n.id] = n; });

  // Index edges by source / target id for O(1) lookup.
  const incomingByTarget = {};
  const outgoingBySource = {};
  data.edges.forEach(function (e) {
    (incomingByTarget[e.target] = incomingByTarget[e.target] || []).push(e);
    (outgoingBySource[e.source] = outgoingBySource[e.source] || []).push(e);
  });

  // Nodes sorted alphabetically by (type, label) for arrow-key cycling.
  const sortedNodes = data.nodes.slice().sort(function (a, b) {
    if (a.type !== b.type) return a.type < b.type ? -1 : 1;
    const al = (a.label || a.id).toLowerCase();
    const bl = (b.label || b.id).toLowerCase();
    if (al !== bl) return al < bl ? -1 : 1;
    return 0;
  });

  const TYPE_LABELS = {
    'skill': 'Skill',
    'skill-internal': 'Skill (internal)',
    'agent': 'Agent',
    'script': 'Script',
    'rule': 'Rule',
    'ref-general': 'Ref (general)',
    'ref-template': 'Ref (template)',
    'ref-project': 'Ref (project)'
  };

  const EDGE_GROUP_ORDER = [
    'invokes', 'delegates', 'orchestrates', 'dispatches-inline',
    'eager-load', 'lazy-load', 'imports'
  ];

  const EDGE_GROUP_LABELS = {
    'invokes': 'Calls scripts',
    'delegates': 'Delegates to agents',
    'orchestrates': 'Orchestrates skills',
    'dispatches-inline': 'Dispatches to internal workers',
    'eager-load': 'Eager-loads refs',
    'lazy-load': 'Lazy-loads refs',
    'imports': 'Imports modules'
  };

  const panel = document.getElementById('side-panel');
  const panelTitle = document.getElementById('side-panel-title');
  const panelBadge = document.getElementById('side-panel-type-badge');
  const panelPath = document.getElementById('side-panel-path');
  const panelDesc = document.getElementById('side-panel-description');
  const panelFallback = document.getElementById('side-panel-fallback-badge');
  const panelIncomingList = document.getElementById('side-panel-incoming-list');
  const panelOutgoingGroups = document.getElementById('side-panel-outgoing-groups');
  const pinBtn = document.getElementById('side-panel-pin');
  const closeBtn = document.getElementById('side-panel-close');

  let pinned = lsGet(LS_PANEL_PINNED, 'false') === 'true';
  let currentPanelNodeId = null;

  function escapeHtml(s) {
    return String(s || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // -----------------------------------------------------------------
  // Minimal Markdown renderer (~40 LOC).
  //
  // Handles: paragraphs, **bold**, *italic*, `inline code`, fenced
  // ```code``` blocks, blockquotes (`> text`), lists (`- item`).
  // Intentionally small; it is not meant to be CommonMark-compliant.
  // -----------------------------------------------------------------
  function renderInline(s) {
    // Escape first; then re-insert formatting spans.
    let out = escapeHtml(s);
    // Inline code backticks first to avoid interfering with bold/italic.
    out = out.replace(/`([^`]+)`/g, function (_m, code) {
      return '<code>' + code + '</code>';
    });
    out = out.replace(/\*\*([^*]+)\*\*/g, '<strong>$$1</strong>');
    out = out.replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g,
      function (_m, pre, txt) { return pre + '<em>' + txt + '</em>'; });
    return out;
  }

  function renderMarkdown(md) {
    if (!md) return '';
    const src = String(md).replace(/\r\n/g, '\n');
    const html = [];
    const lines = src.split('\n');
    let i = 0;
    while (i < lines.length) {
      const line = lines[i];
      // Fenced code block
      if (/^\s*```/.test(line)) {
        const buf = [];
        i++;
        while (i < lines.length && !/^\s*```/.test(lines[i])) {
          buf.push(escapeHtml(lines[i]));
          i++;
        }
        if (i < lines.length) i++; // consume closing fence
        html.push('<pre><code>' + buf.join('\n') + '</code></pre>');
        continue;
      }
      // Blank line separates blocks
      if (!line.trim()) { i++; continue; }
      // Blockquote run
      if (/^\s*>/.test(line)) {
        const buf = [];
        while (i < lines.length && /^\s*>/.test(lines[i])) {
          buf.push(lines[i].replace(/^\s*>\s?/, ''));
          i++;
        }
        html.push('<blockquote>' + renderInline(buf.join('\n').trim())
          .replace(/\n/g, '<br>') + '</blockquote>');
        continue;
      }
      // List run
      if (/^\s*-\s+/.test(line)) {
        const items = [];
        while (i < lines.length && /^\s*-\s+/.test(lines[i])) {
          items.push('<li>' + renderInline(lines[i].replace(/^\s*-\s+/, '')) + '</li>');
          i++;
        }
        html.push('<ul>' + items.join('') + '</ul>');
        continue;
      }
      // Paragraph run: consume until blank line.
      const buf = [line];
      i++;
      while (i < lines.length && lines[i].trim() &&
             !/^\s*```/.test(lines[i]) && !/^\s*>/.test(lines[i]) &&
             !/^\s*-\s+/.test(lines[i])) {
        buf.push(lines[i]);
        i++;
      }
      html.push('<p>' + renderInline(buf.join(' ')) + '</p>');
    }
    return html.join('\n');
  }

  // -----------------------------------------------------------------
  // Quick Guide parser: split a skill description into What/Example/When.
  // Uses heuristic matching on the inline bold markers. Returns null if
  // the structure does not match; caller falls back to raw rendering.
  // -----------------------------------------------------------------
  function parseQuickGuide(text) {
    if (!text) return null;
    const src = String(text).replace(/\r\n/g, '\n');
    const re = /\*\*([^*]+?)\*\*\s*:?/g;
    const markers = [];
    let m;
    while ((m = re.exec(src)) !== null) {
      markers.push({ label: m[1].trim(), start: m.index, afterLabel: m.index + m[0].length });
    }
    if (markers.length < 2) return null;
    function labelMatches(lbl, expected) {
      return lbl.toLowerCase().indexOf(expected) !== -1;
    }
    const findIdx = function (expected) {
      for (let k = 0; k < markers.length; k++) {
        if (labelMatches(markers[k].label, expected)) return k;
      }
      return -1;
    };
    const whatIdx = findIdx('what');
    const exampleIdx = findIdx('example');
    const whenIdx = findIdx('when');
    if (whatIdx < 0 || whenIdx < 0) return null;
    const sliceBetween = function (startMarker, endIdx) {
      const end = endIdx >= 0 ? markers[endIdx].start : src.length;
      return src.slice(startMarker.afterLabel, end).trim();
    };
    const what = sliceBetween(markers[whatIdx],
      exampleIdx >= 0 ? exampleIdx : whenIdx);
    const example = exampleIdx >= 0
      ? sliceBetween(markers[exampleIdx], whenIdx) : '';
    const when = sliceBetween(markers[whenIdx], -1);
    if (!what && !when) return null;
    return { what: what, example: example, when: when };
  }

  // -----------------------------------------------------------------
  // Panel population
  // -----------------------------------------------------------------
  function renderEdgeListItem(edge, otherEndId, label) {
    const li = document.createElement('li');
    const tag = document.createElement('span');
    tag.className = 'edge-type-tag';
    tag.textContent = edge.type;
    const text = document.createElement('span');
    text.textContent = label;
    li.appendChild(tag);
    li.appendChild(text);
    li.setAttribute('role', 'button');
    li.setAttribute('tabindex', '0');
    li.addEventListener('click', function () { openPanel(otherEndId); });
    li.addEventListener('keydown', function (evt) {
      if (evt.key === 'Enter' || evt.key === ' ') {
        evt.preventDefault();
        openPanel(otherEndId);
      }
    });
    return li;
  }

  function populateIncoming(nodeId) {
    panelIncomingList.innerHTML = '';
    const edges = incomingByTarget[nodeId] || [];
    if (!edges.length) {
      const li = document.createElement('li');
      li.className = 'edge-empty';
      li.textContent = 'No incoming edges.';
      panelIncomingList.appendChild(li);
      return;
    }
    edges.slice().sort(function (a, b) {
      const al = (nodeById[a.source] && nodeById[a.source].label) || a.source;
      const bl = (nodeById[b.source] && nodeById[b.source].label) || b.source;
      return al < bl ? -1 : al > bl ? 1 : 0;
    }).forEach(function (e) {
      const src = nodeById[e.source];
      const label = src ? src.label : e.source;
      panelIncomingList.appendChild(renderEdgeListItem(e, e.source, label));
    });
  }

  function populateOutgoing(nodeId) {
    panelOutgoingGroups.innerHTML = '';
    const edges = outgoingBySource[nodeId] || [];
    if (!edges.length) {
      const empty = document.createElement('p');
      empty.className = 'edge-empty';
      empty.style.cssText = 'color:#999;font-style:italic;font-size:12px;margin:4px 0;';
      empty.textContent = 'No outgoing edges.';
      panelOutgoingGroups.appendChild(empty);
      return;
    }
    const grouped = {};
    edges.forEach(function (e) {
      (grouped[e.type] = grouped[e.type] || []).push(e);
    });
    EDGE_GROUP_ORDER.forEach(function (type) {
      const group = grouped[type];
      if (!group || !group.length) return;
      const details = document.createElement('details');
      details.open = true;
      const summary = document.createElement('summary');
      summary.textContent = (EDGE_GROUP_LABELS[type] || type) +
        ' (' + group.length + ')';
      details.appendChild(summary);
      const ul = document.createElement('ul');
      ul.className = 'edge-list';
      group.slice().sort(function (a, b) {
        const al = (nodeById[a.target] && nodeById[a.target].label) || a.target;
        const bl = (nodeById[b.target] && nodeById[b.target].label) || b.target;
        return al < bl ? -1 : al > bl ? 1 : 0;
      }).forEach(function (e) {
        const tgt = nodeById[e.target];
        const label = tgt ? tgt.label : e.target;
        ul.appendChild(renderEdgeListItem(e, e.target, label));
      });
      details.appendChild(ul);
      panelOutgoingGroups.appendChild(details);
    });
  }

  function renderDescription(node) {
    panelDesc.innerHTML = '';
    const source = node.description_source || 'none';
    const text = node.description || '';

    if (source === 'none' || !text) {
      const p = document.createElement('p');
      p.className = 'edge-empty';
      p.style.cssText = 'color:#999;font-style:italic;';
      p.textContent = 'No description available for this node.';
      panelDesc.appendChild(p);
      return;
    }

    let htmlStr;
    if (source === 'quick-guide' && node.type === 'skill') {
      const parts = parseQuickGuide(text);
      if (parts) {
        const pieces = [];
        if (parts.what) {
          pieces.push('<h4>What this skill does for you</h4>' +
            renderMarkdown(parts.what));
        }
        if (parts.example) {
          pieces.push('<h4>Example</h4>' + renderMarkdown(parts.example));
        }
        if (parts.when) {
          pieces.push('<h4>When to use</h4>' + renderMarkdown(parts.when));
        }
        htmlStr = pieces.join('\n');
      } else {
        htmlStr = renderMarkdown(text);
      }
    } else {
      htmlStr = renderMarkdown(text);
    }

    // "Show more" collapser: if the HTML string is large, split after the
    // first <p>/<h4>+<p> block. Threshold = char length or line count.
    const approxLines = text.split('\n').length;
    if (approxLines > 12 || text.length > 600) {
      // Find first closing </p> or </blockquote> to split on.
      const container = document.createElement('div');
      container.innerHTML = htmlStr;
      const children = Array.from(container.children);
      if (children.length > 2) {
        const firstTwo = children.slice(0, 2);
        const rest = children.slice(2);
        firstTwo.forEach(function (el) { panelDesc.appendChild(el); });
        const details = document.createElement('details');
        const summary = document.createElement('summary');
        summary.textContent = 'Show more';
        details.appendChild(summary);
        rest.forEach(function (el) { details.appendChild(el); });
        panelDesc.appendChild(details);
        return;
      }
    }
    panelDesc.innerHTML = htmlStr;
  }

  function openPanel(nodeId) {
    const node = nodeById[nodeId];
    if (!node) return;
    currentPanelNodeId = nodeId;
    updateMatchSelection();

    // Type badge.
    const typeClass = 'type-' + node.type;
    panelBadge.className = 'type-badge ' + typeClass;
    panelBadge.textContent = TYPE_LABELS[node.type] || node.type;

    // Title.
    panelTitle.textContent = node.label || node.id;

    // Clickable path.
    const href = '../../../' + (node.path || '');
    panelPath.setAttribute('href', href);
    panelPath.textContent = node.path || '';

    // Description.
    renderDescription(node);

    // Fallback badge: "Developer-oriented -- awaiting designer rewrite".
    // Shown only when the description was extracted via the developer
    // fallback (first H1 + lead / docstring) rather than designer copy.
    if ((node.description_source || 'none') === 'developer-fallback') {
      panelFallback.textContent =
        'Developer-oriented \u2014 awaiting designer rewrite';
      panelFallback.hidden = false;
    } else {
      panelFallback.hidden = true;
    }

    // Edges.
    populateIncoming(nodeId);
    populateOutgoing(nodeId);

    // Open.
    panel.hidden = false;
    panel.setAttribute('aria-hidden', 'false');
    lsSet(LS_PANEL_OPEN, 'true');
    lsSet(LS_PANEL_LAST_NODE, nodeId);

    // Select in cytoscape (visually) without triggering another tap.
    try {
      cy.nodes().unselect();
      const target = cy.getElementById(nodeId);
      if (target && target.length) target.select();
    } catch (_e) { /* ignore */ }
  }

  function closePanel(keepSelection) {
    panel.hidden = true;
    panel.setAttribute('aria-hidden', 'true');
    lsSet(LS_PANEL_OPEN, 'false');
    currentPanelNodeId = null;
    updateMatchSelection();
    if (!pinned) {
      if (!keepSelection) {
        try { cy.nodes().unselect(); } catch (_e) { /* ignore */ }
      }
      clearFocus();
    }
  }

  function setPinned(value) {
    pinned = Boolean(value);
    lsSet(LS_PANEL_PINNED, pinned ? 'true' : 'false');
    if (pinBtn) {
      pinBtn.setAttribute('aria-pressed', pinned ? 'true' : 'false');
      pinBtn.textContent = pinned ? 'Pinned' : 'Pin';
    }
  }

  function focusNeighborhood(nodeId) {
    const focused = cy.getElementById(nodeId);
    if (!focused || focused.empty()) return;
    // closedNeighborhood returns the node itself, all connected edges,
    // and all 1-hop neighbor nodes.
    const neighborhood = focused.closedNeighborhood();
    cy.batch(function () {
      cy.elements().removeClass('faded');
      cy.elements().difference(neighborhood).addClass('faded');
    });
  }

  function clearFocus() {
    cy.batch(function () { cy.elements().removeClass('faded'); });
  }

  // Track Ctrl/Cmd key state independently — reading ctrlKey from
  // Cytoscape's synthetic evt.originalEvent is unreliable in Firefox.
  let _multiSelectActive = false;
  function _setMultiSelect(on) {
    _multiSelectActive = on;
    // Switch Cytoscape's selection model so it doesn't deselect everything
    // on the next tap while the modifier is held.
    cy.selectionType(on ? 'additive' : 'single');
    // selectionType('single') can reset boxSelectionEnabled to false in some
    // Cytoscape builds — re-assert it so Shift+drag always works.
    cy.boxSelectionEnabled(true);
  }
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Control' || e.key === 'Meta') _setMultiSelect(true);
  });
  document.addEventListener('keyup', function (e) {
    if (e.key === 'Control' || e.key === 'Meta') _setMultiSelect(false);
  });
  window.addEventListener('blur', function () { _setMultiSelect(false); });

  cy.on('tap', 'node', function (evt) {
    const node = evt.target;
    if (_multiSelectActive) {
      // Selection is handled by Cytoscape's additive mode; just skip the
      // panel / focus changes so the multi-selection stays intact.
      return;
    }
    const nodeId = node.data('id');
    openPanel(nodeId);
    focusNeighborhood(nodeId);
  });

  // When multiple nodes are selected, close the details pane and clear all
  // dimming — neither applies to a set of nodes.
  // keepSelection=true prevents closePanel from calling cy.nodes().unselect(),
  // which would immediately wipe the multi-selection we're building.
  cy.on('select unselect', 'node', function () {
    if (cy.$$('node:selected').length > 1) {
      clearFocus();
      if (!pinned) closePanel(true);
    }
  });

  // Background tap (empty canvas) clears focus and, if not pinned, closes
  // the panel. Distinguish from node taps by checking evt.target === cy.
  cy.on('tap', function (evt) {
    if (evt.target === cy) {
      clearFocus();
      if (!pinned) closePanel();
    }
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', function () { closePanel(); });
  }
  if (pinBtn) {
    pinBtn.addEventListener('click', function () { setPinned(!pinned); });
  }

  document.addEventListener('keydown', function (evt) {
    if (evt.key === 'Escape') {
      if (pinned) {
        try { cy.nodes().unselect(); } catch (_e) { /* ignore */ }
      } else {
        closePanel();
      }
      return;
    }
    if (!pinned || panel.hidden) return;
    if (evt.key !== 'ArrowUp' && evt.key !== 'ArrowDown') return;
    if (!currentPanelNodeId) return;
    const cur = nodeById[currentPanelNodeId];
    if (!cur) return;
    const sameType = sortedNodes.filter(function (n) {
      return n.type === cur.type;
    });
    const idx = sameType.findIndex(function (n) {
      return n.id === currentPanelNodeId;
    });
    if (idx < 0) return;
    const delta = evt.key === 'ArrowDown' ? 1 : -1;
    const nextIdx = (idx + delta + sameType.length) % sameType.length;
    evt.preventDefault();
    openPanel(sameType[nextIdx].id);
    focusNeighborhood(sameType[nextIdx].id);
  });

  // Restore panel state on load.
  setPinned(pinned);
  const panelWasOpen = lsGet(LS_PANEL_OPEN, 'false') === 'true';
  const lastNode = lsGet(LS_PANEL_LAST_NODE, null);
  if (panelWasOpen && lastNode && nodeById[lastNode]) {
    openPanel(lastNode);
    focusNeighborhood(lastNode);
  }

  // -----------------------------------------------------------------
  // Initial render
  // -----------------------------------------------------------------
  restoreFilterState();
  updateNodeVisibility();
  runLayout(currentLayout);
})();
""")


def render_html(generated_at: str) -> str:
    """Render the call-graph.html document as a string."""
    return HTML_TEMPLATE.substitute(generated_at=generated_at)


def render_css(generated_at: str) -> str:
    """Render the call-graph.css stylesheet as a string."""
    return CSS_TEMPLATE.substitute(generated_at=generated_at)


def render_js(generated_at: str) -> str:
    """Render the call-graph.js viewer script as a string."""
    return JS_TEMPLATE.substitute(generated_at=generated_at)


# ---------------------------------------------------------------------------
# Content computation (shared between write path and --check)
# ---------------------------------------------------------------------------


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def compute_outputs(
    fixed_date: str | None = None,
    verbose: bool = False,
) -> tuple[dict[Path, str], dict, list[str]]:
    """Run the full parse pass and return the would-be content for all 5 artifacts.

    Returns ``(outputs, manifest, warnings)`` where ``outputs`` maps each output
    path to its full string content, ``manifest`` is the JSON-serializable data
    structure, and ``warnings`` is the list of suspicious-reference warnings
    accumulated during edge extraction.

    No filesystem writes are performed.
    """
    nodes = discover_all_nodes()
    warnings: list[str] = []
    edges = _collect_all_edges(nodes, warnings, verbose)
    generated_at = fixed_date or _utc_now()
    manifest = build_manifest(nodes, edges, warnings, generated_at)

    json_payload = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    outputs: dict[Path, str] = {
        OUTPUT_JSON: json_payload,
        OUTPUT_JSON_PUBLIC: json_payload,
        OUTPUT_MD: render_markdown(manifest, generated_at, fixed_date),
        OUTPUT_HTML: render_html(generated_at),
        OUTPUT_CSS: render_css(generated_at),
        OUTPUT_JS: render_js(generated_at),
    }
    return outputs, manifest, warnings


# ---------------------------------------------------------------------------
# --check mode helpers
# ---------------------------------------------------------------------------


def _strip_volatile_lines(content: str, path: Path) -> str:
    """Strip timestamp-rotating lines so --check comparisons are stable.

    Each artifact has a per-run timestamp that MUST be ignored during drift
    detection -- otherwise every run would report false drift:

    - JSON: the top-level ``"generated": "..."`` field.
    - Markdown: the ``last-reviewed:`` frontmatter key AND a ``<!-- Generated
      ... -->`` HTML comment in the preamble.
    - HTML: a ``Generated ...`` line inside the page-header multi-line
      ``<!-- ... -->`` comment (indented by two spaces; not a single-line
      comment).
    - CSS: a ``* Generated ...`` line inside the top-of-file ``/* ... */``
      block.
    - JS: a ``// Generated ...`` single-line comment near the top.
    """
    normalized = content.replace("\r\n", "\n")
    if path in (OUTPUT_JSON, OUTPUT_JSON_PUBLIC):
        return re.sub(r'^\s*"generated":\s*"[^"]*",?\s*\n', "", normalized, flags=re.MULTILINE)
    if path == OUTPUT_MD:
        stripped = re.sub(r"^last-reviewed:.*\n", "", normalized, flags=re.MULTILINE)
        stripped = re.sub(r"^<!-- Generated .*? -->\n", "", stripped, flags=re.MULTILINE)
        return stripped
    if path == OUTPUT_HTML:
        # Match both the single-line `<!-- Generated ... -->` form and the
        # indented `  Generated ...` line inside a multi-line HTML comment.
        stripped = re.sub(r"^<!-- Generated .*? -->\n", "", normalized, flags=re.MULTILINE)
        stripped = re.sub(r"^\s*Generated .*?generate_call_graph\.py\.\n", "", stripped, flags=re.MULTILINE)
        return stripped
    if path == OUTPUT_CSS:
        return re.sub(r"^\s*\*\s*Generated .*?generate_call_graph\.py\.\n", "", normalized, flags=re.MULTILINE)
    if path == OUTPUT_JS:
        return re.sub(r"^//\s*Generated .*?generate_call_graph\.py\.\n", "", normalized, flags=re.MULTILINE)
    return normalized


def run_check(strict: bool = False, verbose: bool = False) -> int:
    """Compute outputs in-memory, compare to on-disk, validate edge targets.

    Returns an exit code: 0 on pass, 1 on drift / unresolved / (strict)
    suspicious references, 2 on script error.
    """
    try:
        outputs, manifest, warnings = compute_outputs(fixed_date=None, verbose=verbose)
    except OSError as exc:
        print(f"ERROR: compute_outputs failed: {exc}", file=sys.stderr)
        return 2

    exit_code = 0
    drift_count = 0
    unresolved_count = 0
    suspicious_count = 0

    # Step 3: drift detection -- compare each artifact to its on-disk counterpart.
    for path, expected in outputs.items():
        if not path.is_file():
            print(f"DRIFT: {path} does not exist", file=sys.stderr)
            drift_count += 1
            exit_code = 1
            continue
        actual = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        expected_lf = expected.replace("\r\n", "\n")
        if actual == expected_lf:
            continue
        # Timestamp-volatile lines rotate per run; strip before comparing.
        actual_normalized = _strip_volatile_lines(actual, path)
        expected_normalized = _strip_volatile_lines(expected_lf, path)
        if actual_normalized != expected_normalized:
            print(
                f"DRIFT: {path} differs from generator output",
                file=sys.stderr,
            )
            drift_count += 1
            exit_code = 1

    # Step 4: edge target resolution -- every edge's target must be a known node.
    node_ids = {n["id"] for n in manifest["nodes"]}
    source_paths = {n["id"]: n["path"] for n in manifest["nodes"]}
    for edge in manifest["edges"]:
        if edge["target"] not in node_ids:
            src_path = source_paths.get(edge["source"], edge["source"])
            print(
                f"UNRESOLVED: {src_path} references {edge['target']} which does not exist",
                file=sys.stderr,
            )
            if verbose:
                print(
                    f"  edge: {edge['source']} -{edge['type']}-> {edge['target']}",
                    file=sys.stderr,
                )
            unresolved_count += 1
            exit_code = 1

    # Step 5: suspicious-reference pass -- the 20 known project/* warnings.
    for warning in manifest["warnings"]:
        if strict:
            print(f"SUSPICIOUS: {warning}", file=sys.stderr)
            suspicious_count += 1
            exit_code = 1
        elif verbose:
            print(f"INFO: {warning}", file=sys.stderr)

    # Summary line.
    node_count = len(manifest["nodes"])
    edge_count = len(manifest["edges"])
    if exit_code == 0:
        print(
            f"CHECK PASS: {node_count} nodes, {edge_count} edges, "
            f"0 drift, 0 unresolved"
        )
    else:
        print(
            f"CHECK FAIL: {drift_count} drift, {unresolved_count} unresolved, "
            f"{suspicious_count} suspicious",
            file=sys.stderr,
        )
    return exit_code


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _compute_sri_hash(url: str, timeout: float = 30.0) -> str:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        body = resp.read()
    digest = hashlib.sha384(body).digest()
    return "sha384-" + base64.b64encode(digest).decode("ascii")


def refresh_sri(verbose: bool = False) -> int:
    global HTML_TEMPLATE
    source_path = Path(__file__).resolve()
    source = source_path.read_text(encoding="utf-8")
    updated_source = source
    updated_template_text = HTML_TEMPLATE.template
    changed = 0
    for url in CDN_URLS:
        try:
            new_hash = _compute_sri_hash(url)
        except Exception as exc:
            print(f"ERROR: could not fetch {url}: {exc}", file=sys.stderr)
            return 2
        if verbose:
            print(f"  {url}")
            print(f"    {new_hash}")
        pattern = re.compile(
            r'(src="' + re.escape(url) + r'"[^>]*?integrity=")[^"]*(")',
            re.DOTALL,
        )
        if not pattern.search(updated_source):
            print(
                f"WARNING: no integrity= line found for {url} in {source_path}",
                file=sys.stderr,
            )
            continue
        new_source = pattern.sub(r"\1" + new_hash + r"\2", updated_source)
        if new_source != updated_source:
            changed += 1
            updated_source = new_source
        updated_template_text = pattern.sub(
            r"\1" + new_hash + r"\2", updated_template_text
        )
    if updated_source != source:
        source_path.write_text(updated_source, encoding="utf-8", newline="\n")
    HTML_TEMPLATE = string.Template(updated_template_text)
    print(f"Refreshed {changed} SRI hashes in {source_path.name}.")
    if verbose:
        print("Regenerating artifacts with new hashes...")
    outputs, manifest, _warnings = compute_outputs(fixed_date=None, verbose=False)
    if not manifest["nodes"]:
        print("ERROR: no nodes discovered during post-refresh regeneration", file=sys.stderr)
        return 1
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Regenerated {len(outputs)} artifacts.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the SEJA harness call graph JSON.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Log every parsed edge, every ref-load, and every unresolved reference.",
    )
    parser.add_argument(
        "--fixed-date",
        default=None,
        help="Pin the generated timestamp (ISO8601) for deterministic output.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Verify on-disk output matches generator output and all edges "
            "resolve. Exit 1 on drift or unresolved references."
        ),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "In --check mode, also fail on suspicious references in the "
            "warnings list (20 known project/* refs)."
        ),
    )
    parser.add_argument(
        "--refresh-sri",
        action="store_true",
        help=(
            "Fetch each CDN asset in CDN_URLS, compute its sha384 SRI hash, "
            "and rewrite this script's HTML_TEMPLATE integrity= values in place. "
            "Then regenerate artifacts. Requires network access."
        ),
    )
    args = parser.parse_args(argv)

    if args.refresh_sri:
        return refresh_sri(verbose=args.verbose)

    if args.check:
        return run_check(strict=args.strict, verbose=args.verbose)

    try:
        outputs, manifest, _warnings = compute_outputs(
            fixed_date=args.fixed_date,
            verbose=args.verbose,
        )
    except OSError as exc:
        print(f"ERROR: content generation failed: {exc}", file=sys.stderr)
        return 2

    if not manifest["nodes"]:
        print("ERROR: no nodes discovered", file=sys.stderr)
        return 1

    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")

    if args.verbose:
        type_counts: dict[str, int] = {}
        for node in manifest["nodes"]:
            type_counts[node["type"]] = type_counts.get(node["type"], 0) + 1
        edge_counts: dict[str, int] = {}
        for edge in manifest["edges"]:
            edge_counts[edge["type"]] = edge_counts.get(edge["type"], 0) + 1
        print(
            f"wrote: {OUTPUT_JSON} "
            f"({manifest['node_count']} nodes, {manifest['edge_count']} edges, "
            f"{len(manifest['warnings'])} warnings)",
            file=sys.stderr,
        )
        print(f"wrote: {OUTPUT_MD}", file=sys.stderr)
        print(f"wrote: {OUTPUT_HTML}", file=sys.stderr)
        print(f"wrote: {OUTPUT_CSS}", file=sys.stderr)
        print(f"wrote: {OUTPUT_JS}", file=sys.stderr)
        print(f"node types: {type_counts}", file=sys.stderr)
        print(f"edge types: {edge_counts}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
