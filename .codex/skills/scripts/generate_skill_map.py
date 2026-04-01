#!/usr/bin/env python3
"""
generate_skill_map.py -- Generate a Mermaid flowchart from skill-graph.md.

Exit codes: 0 = success, 1 = no relationships found, 2 = script error.

Reads _references/general/skill-graph.md, parses After/Suggest/Reason
triples from markdown tables, categorizes skills by color, and emits a
Mermaid flowchart to _output/skill-map.mmd. Optionally runs mmdc for SVG
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
OUTPUT_DIR = REPO_ROOT / "_output"
OUTPUT_MMD = OUTPUT_DIR / "skill-map.mmd"
OUTPUT_SVG = OUTPUT_DIR / "skill-map.svg"

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

# Mermaid classDef styles (plain ASCII-safe colors)
CLASS_DEFS = {
    "planning": "fill:#4a90d9,stroke:#2c5f8a,color:#ffffff",
    "analysis": "fill:#5cb85c,stroke:#3d7a3d,color:#ffffff",
    "code": "fill:#e89832,stroke:#b07025,color:#ffffff",
    "utility": "fill:#999999,stroke:#666666,color:#ffffff",
    "setup": "fill:#8e6bbf,stroke:#5e4580,color:#ffffff",
}

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
        # Truncate long reasons for readability
        short_reason = reason.rstrip("?. ")
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

    # Optionally render SVG
    if svg_flag:
        mmdc = shutil.which("mmdc")
        if mmdc:
            result = subprocess.run(
                [mmdc, "-i", str(OUTPUT_MMD), "-o", str(OUTPUT_SVG)],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print(f"Generated {OUTPUT_SVG}")
            else:
                print(f"WARNING: mmdc failed: {result.stderr}", file=sys.stderr)
        else:
            print("INFO: mmdc not found on PATH; skipping SVG generation", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
