#!/usr/bin/env python3
"""Summarize SEJA artifacts by ID or path for embedding in reflection reports."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from project_config import REPO_ROOT, get_path

_HEADER_RE = re.compile(
    r"^#\s+(?:DONE\s*\|[^|]*\|)?\s*(?:Plan|Advisory|Reflection|Inventory|Proposal|Explained|Check)"
    r"\s+(\d{6})\s*\|\s*([^|]*?)\s*\|\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+UTC)\s*\|\s*(.+?)(?:\s*\|.*)?$",
    re.IGNORECASE,
)

_SCAN_DIRS = [
    "plans", "advisory-logs", "reflections", "inventories",
    "proposals", "explained-behaviors", "explained-code",
    "explained-data-model", "explained-architecture",
    "behavior-evolution", "check-logs",
]


def _resolve_path(ref: str) -> Path | None:
    """Resolve an artifact reference (ID like 'plan-000295' or bare '000295') to a file."""
    bare_id = re.sub(r"^(?:plan|advisory|reflection|inventory|proposal|check)-", "", ref)
    bare_id = bare_id.strip()
    output_dir = get_path("OUTPUT_DIR")
    for subdir in _SCAN_DIRS:
        d = output_dir / subdir
        if not d.is_dir():
            continue
        for f in d.iterdir():
            if f.suffix == ".md" and bare_id in f.name:
                return f
    p = Path(ref)
    if p.is_file():
        return p
    full = REPO_ROOT / ref
    if full.is_file():
        return full
    return None


def _extract_section(lines: list[str], heading_prefix: str, max_chars: int = 300) -> str:
    """Extract the first paragraph after a heading matching the prefix."""
    collecting = False
    buf: list[str] = []
    for line in lines:
        if line.startswith("#") and heading_prefix.lower() in line.lower():
            collecting = True
            continue
        if collecting:
            if line.startswith("#"):
                break
            stripped = line.strip()
            if stripped:
                buf.append(stripped)
            elif buf:
                break
    text = " ".join(buf)
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + "..."
    return text


def summarize(artifact_refs: list[str]) -> list[dict]:
    """Return a list of summary dicts for each artifact reference."""
    results = []
    for ref in artifact_refs:
        path = _resolve_path(ref)
        if path is None:
            results.append({"id": ref, "error": "not found"})
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            results.append({"id": ref, "error": f"could not read {path}"})
            continue
        lines = text.splitlines()
        header_match = _HEADER_RE.match(lines[0]) if lines else None
        entry: dict = {
            "id": header_match.group(1) if header_match else ref,
            "type": _infer_type(path),
            "path": str(path.relative_to(REPO_ROOT)),
            "title": header_match.group(4).strip() if header_match else path.stem,
            "datetime": header_match.group(3) if header_match else "",
            "brief_excerpt": _extract_section(lines, "## User brief")
                or _extract_section(lines, "## Brief")
                or _extract_section(lines, "## What"),
            "interpretation_excerpt": _extract_section(lines, "## Agent interpretation")
                or _extract_section(lines, "## Problem"),
        }
        results.append(entry)
    return results


def _infer_type(path: Path) -> str:
    name = path.parent.name
    mapping = {
        "plans": "plan", "advisory-logs": "advisory", "reflections": "reflection",
        "inventories": "inventory", "proposals": "proposal", "check-logs": "check",
    }
    return mapping.get(name, "artifact")


def as_markdown_block(summaries: list[dict]) -> str:
    """Format summaries as a markdown bullet list for embedding in reports."""
    lines = []
    for s in summaries:
        if "error" in s:
            lines.append(f"- **{s['id']}** -- {s['error']}")
            continue
        lines.append(
            f"- [{s['type']}-{s['id']}]({s['path']}) | {s['datetime']} | {s['title']}"
        )
        if s.get("brief_excerpt"):
            lines.append(f"  - **Brief**: {s['brief_excerpt']}")
        if s.get("interpretation_excerpt"):
            lines.append(f"  - **Interpretation**: {s['interpretation_excerpt']}")
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: summarize_artifacts.py <id-or-path> [<id-or-path> ...]", file=sys.stderr)
        return 2
    refs = sys.argv[1:]
    summaries = summarize(refs)
    print(as_markdown_block(summaries))
    return 0


if __name__ == "__main__":
    sys.exit(main())
