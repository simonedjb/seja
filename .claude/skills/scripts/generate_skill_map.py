#!/usr/bin/env python3
"""
generate_skill_map.py -- Generate a Mermaid flowchart from skill-graph.md.

Exit codes: 0 = success, 1 = no relationships found, 2 = script error.

Reads _references/general/skill-graph.md, parses After/Suggest/Reason
triples from markdown tables, categorizes skills by color, and emits a
Mermaid flowchart to _references/general/skill-map.mmd. Optionally runs mmdc for SVG
if available on PATH.

Usage
-----
    python .claude/skills/scripts/generate_skill_map.py [--svg]

Run from the repository root.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from project_config import REPO_ROOT
except ImportError:
    REPO_ROOT = Path(__file__).resolve().parents[3]

SKILL_GRAPH_PATH = REPO_ROOT / "_references" / "general" / "skill-graph.md"
OUTPUT_DIR = REPO_ROOT / "_references" / "general"
OUTPUT_MMD = OUTPUT_DIR / "skill-map.mmd"
OUTPUT_SVG = OUTPUT_DIR / "skill-map.svg"

# Public-docs publication targets. The generator writes the same mermaid
# content into a short markdown wrapper under seja-public/docs/concepts/ so
# readers can see the skill map in context. If the seja-public tree does not
# exist (bare workspace), the public-docs writes are skipped silently.
PUBLIC_DOCS_ROOT = REPO_ROOT / "seja-public" / "docs"
PUBLIC_SKILL_MAP_MD = PUBLIC_DOCS_ROOT / "concepts" / "skill-map.md"
PUBLIC_SKILL_MAP_SVG = PUBLIC_DOCS_ROOT / "concepts" / "skill-map.svg"

# Regex to match markdown table rows: | `/skill` | `/skill` | reason |
_TABLE_ROW_RE = re.compile(
    r"^\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|\s*(.+?)\s*\|$",
    re.MULTILINE,
)

# Skill categories: determines node color in the diagram
SKILL_CATEGORIES: dict[str, str] = {
    "/plan": "planning",
    "/implement": "planning",
    "/explain": "analysis",
    "/advise": "analysis",
    "/check": "analysis",
    "/communication": "utility",
    "/onboarding": "utility",
    "/help": "utility",
    "/qa-log": "utility",
    "/design": "setup",
    "/seed": "setup",
    "/upgrade": "setup",
}

# Mermaid classDef styles -- pastel light-mode palette with dark text.
# WCAG AA contrast is preserved for every fill/text pair. The per-category
# stroke uses a slightly darker variant of the fill to keep nodes visually
# grouped without fighting the soft background.
CLASS_DEFS = {
    "planning": "fill:#cfe4fb,stroke:#6da3d4,color:#1e3a5f",
    "analysis": "fill:#d4efd4,stroke:#74b874,color:#2d5a2d",
    "code": "fill:#fce6c8,stroke:#d9a66b,color:#6b3f1e",
    "utility": "fill:#e6e6e6,stroke:#a8a8a8,color:#404040",
    "setup": "fill:#e3d6f0,stroke:#9b7fc7,color:#4a2f6b",
}

# Mermaid init directive prepended to every generated flowchart. Pinning
# the theme to 'default' forces light-mode colors on GitHub's dark-mode
# viewers, and the font hint keeps the render consistent across platforms
# without loading a custom font.
MERMAID_INIT_DIRECTIVE = (
    "%%{init: {'theme': 'default', "
    "'themeVariables': {'fontFamily': 'system-ui, -apple-system, "
    "Segoe UI, sans-serif'}}}%%"
)

CATEGORY_LABELS = {
    "planning": "Planning",
    "analysis": "Analysis",
    "code": "Code",
    "utility": "Utility",
    "setup": "Setup",
}


def _sanitize_id(skill_name: str) -> str:
    """Convert a skill name like `/check validate` to a safe Mermaid node id."""
    return skill_name.lstrip("/").replace(" ", "_").replace("-", "_")


def _display_label(skill_name: str) -> str:
    """Return a human-readable label for a skill node."""
    return skill_name


def _sanitize_edge_label(text: str) -> str:
    """Remove characters that break mermaid's edge-label parser.

    Mermaid's flowchart grammar treats `(`, `)`, `[`, `]`, `{`, `}`, `|`,
    `"`, and `#` as shape delimiters inside `|...|` edge labels. Replacing
    brackets with dashes keeps the prose readable; stripping quote/pipe
    characters removes the worst parser ambiguities. Newlines and tabs
    collapse to a single space.
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
    return " ".join(cleaned.split())


def parse_relationships(text: str) -> list[tuple[str, str, str]]:
    """Parse After/Suggest/Reason triples from skill-graph.md content."""
    results: list[tuple[str, str, str]] = []
    for match in _TABLE_ROW_RE.finditer(text):
        after = match.group(1).strip()
        suggest = match.group(2).strip()
        reason = match.group(3).strip()
        # Skip header separator rows
        if after.startswith("---") or suggest.startswith("---"):
            continue
        # Skip header labels
        if after == "After" and suggest == "Suggest":
            continue
        results.append((after, suggest, reason))
    return results


def collect_skills(relationships: list[tuple[str, str, str]]) -> list[str]:
    """Collect unique skill names from relationships, sorted."""
    skills: set[str] = set()
    for after, suggest, _ in relationships:
        # Normalize: strip flags/arguments for the node
        skills.add(after.split(" --")[0].split(" ")[0] if " " in after else after)
        skills.add(suggest.split(" --")[0].split(" ")[0] if " " in suggest else suggest)
    return sorted(skills)


def generate_mermaid(relationships: list[tuple[str, str, str]]) -> str:
    """Generate a Mermaid flowchart string from parsed relationships."""
    lines: list[str] = []
    lines.append(MERMAID_INIT_DIRECTIVE)
    lines.append("flowchart TD")
    lines.append("")

    # Collect all unique skills for node definitions
    all_skills = collect_skills(relationships)

    # Define nodes grouped by category
    for category in ("planning", "analysis", "code", "utility", "setup"):
        label = CATEGORY_LABELS[category]
        lines.append(f"    %% {label}")
        for skill in all_skills:
            if SKILL_CATEGORIES.get(skill, "utility") == category:
                node_id = _sanitize_id(skill)
                display = _display_label(skill)
                lines.append(f'    {node_id}["{display}"]')
        lines.append("")

    # Define edges with reason labels
    lines.append("    %% Relationships")
    seen_edges: set[str] = set()
    for after, suggest, reason in relationships:
        # Use base skill name for node id
        after_base = after.split(" --")[0].split(" ")[0] if " " in after else after
        suggest_base = suggest.split(" --")[0].split(" ")[0] if " " in suggest else suggest
        from_id = _sanitize_id(after_base)
        to_id = _sanitize_id(suggest_base)
        edge_key = f"{from_id}-->{to_id}"
        if edge_key in seen_edges:
            continue
        seen_edges.add(edge_key)
        # Sanitize the edge-label text for mermaid, then truncate for
        # readability. Sanitization must happen BEFORE truncation so the
        # replacement rules see the full original text.
        short_reason = _sanitize_edge_label(reason.rstrip("?. "))
        if len(short_reason) > 50:
            short_reason = short_reason[:47] + "..."
        lines.append(f"    {from_id} -->|{short_reason}| {to_id}")
    lines.append("")

    # Class definitions
    lines.append("    %% Styles")
    for category, style in CLASS_DEFS.items():
        lines.append(f"    classDef {category} {style}")
    lines.append("")

    # Apply classes
    for category in ("planning", "analysis", "code", "utility", "setup"):
        members = [
            _sanitize_id(s) for s in all_skills
            if SKILL_CATEGORIES.get(s, "utility") == category
        ]
        if members:
            lines.append(f"    class {','.join(members)} {category}")

    lines.append("")
    return "\n".join(lines)


def _render_text_fallback(relationships: list[tuple[str, str, str]]) -> str:
    """Render the parsed relationships as a text-only bulleted list.

    This is used as an accessibility fallback inside the published
    skill-map.md so screen-reader users and plain-text viewers can still
    understand the workflow connections without rendering the mermaid
    diagram.
    """
    bullets: list[str] = []
    seen: set[tuple[str, str]] = set()
    for after, suggest, reason in relationships:
        key = (after, suggest)
        if key in seen:
            continue
        seen.add(key)
        bullets.append(f"- `{after}` -> `{suggest}`: {reason.rstrip('?. ')}")
    return "\n".join(bullets)


PUBLIC_SKILL_MAP_TEMPLATE = """\
<!-- This file is generated by .claude/skills/scripts/generate_skill_map.py. Do not edit by hand. -->

# Skill map

We generated this diagram to give you a visual anchor for how SEJA skills connect. Each arrow is a "here is what we suggest next" hint we emit at the end of a skill's run, so the graph is as much a map of the workflow as it is of the code. For a text-only reader we also ship a collapsed bullet list of the same relationships below the diagram.

```mermaid
{mermaid}
```

> If your renderer does not support mermaid, the same diagram is also available as an SVG: ![Skill map](skill-map.svg). We regenerate both from the same source whenever `mmdc` is on PATH.

<details>
<summary>Text-only relationship list (accessibility fallback)</summary>

{text_fallback}

</details>
"""


def _write_public_skill_map_md(mermaid_content: str, relationships: list[tuple[str, str, str]]) -> bool:
    """Write the public-docs skill-map.md. Skips silently if seja-public missing."""
    if not PUBLIC_DOCS_ROOT.is_dir():
        return False
    PUBLIC_SKILL_MAP_MD.parent.mkdir(parents=True, exist_ok=True)
    wrapper = PUBLIC_SKILL_MAP_TEMPLATE.format(
        mermaid=mermaid_content.strip(),
        text_fallback=_render_text_fallback(relationships),
    )
    PUBLIC_SKILL_MAP_MD.write_text(wrapper, encoding="utf-8")
    return True


def _try_render_svg(source_mmd: Path, target_svg: Path) -> bool:
    """Shell out to mmdc to render `source_mmd` into `target_svg`.

    Returns True on success, False if mmdc is not on PATH or the render
    failed. Caller decides whether that's an error or a silent skip.
    """
    mmdc = shutil.which("mmdc")
    if not mmdc:
        return False
    target_svg.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [mmdc, "-i", str(source_mmd), "-o", str(target_svg)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"WARNING: mmdc failed for {target_svg}: {result.stderr}", file=sys.stderr)
        return False
    return True


def main() -> int:
    """Main entry point."""
    svg_flag = "--svg" in sys.argv

    if not SKILL_GRAPH_PATH.is_file():
        print(f"ERROR: skill-graph.md not found at {SKILL_GRAPH_PATH}", file=sys.stderr)
        return 2

    text = SKILL_GRAPH_PATH.read_text(encoding="utf-8")
    relationships = parse_relationships(text)

    if not relationships:
        print("ERROR: no relationships found in skill-graph.md", file=sys.stderr)
        return 1

    mermaid_content = generate_mermaid(relationships)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_MMD.write_text(mermaid_content, encoding="utf-8")
    print(f"Generated {OUTPUT_MMD} ({len(relationships)} relationships)")

    # Publish the skill-map page to seja-public/docs/concepts/ when available.
    if _write_public_skill_map_md(mermaid_content, relationships):
        print(f"Generated {PUBLIC_SKILL_MAP_MD}")
    else:
        print(
            f"INFO: {PUBLIC_DOCS_ROOT} not found; skipping public-docs publication",
            file=sys.stderr,
        )

    # Always attempt the public-docs SVG when mmdc is available and the
    # seja-public tree exists. The --svg flag additionally triggers
    # the _references/general/skill-map.svg render for the working copy.
    mmdc_available = shutil.which("mmdc") is not None
    if svg_flag:
        if _try_render_svg(OUTPUT_MMD, OUTPUT_SVG):
            print(f"Generated {OUTPUT_SVG}")
        elif not mmdc_available:
            print("INFO: mmdc not found on PATH; skipping SVG", file=sys.stderr)
    if PUBLIC_DOCS_ROOT.is_dir() and mmdc_available:
        if _try_render_svg(OUTPUT_MMD, PUBLIC_SKILL_MAP_SVG):
            print(f"Generated {PUBLIC_SKILL_MAP_SVG}")
    elif PUBLIC_DOCS_ROOT.is_dir() and not mmdc_available:
        print(
            "INFO: mmdc not found on PATH; public-docs SVG not regenerated",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
