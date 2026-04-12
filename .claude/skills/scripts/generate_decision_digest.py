#!/usr/bin/env python3
"""
generate_decision_digest.py -- Generate a machine-readable decision digest.

Scans two sources for design decisions:
  1. D-NNN entries in _references/project/product-design-as-intended.md (## Decisions)
  2. HIGH/MEDIUM recommendations in _output/advisory-logs/advisory-*.md

Outputs _output/decision-digest.jsonl with one JSON line per decision.

Usage
-----
    python .claude/skills/scripts/generate_decision_digest.py
    python .claude/skills/scripts/generate_decision_digest.py --verbose

Run from the repository root.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from project_config import REPO_ROOT, get_path

OUTPUT_DIR = get_path("OUTPUT_DIR") or REPO_ROOT / "_output"
ADVISORY_DIR = get_path("ADVISORY_DIR") or OUTPUT_DIR / "advisory-logs"
DIGEST_FILE = OUTPUT_DIR / "decision-digest.jsonl"

# D-NNN entry pattern in product-design-as-intended.md
_D_NNN_RE = re.compile(r"^###\s+(D-\d+):\s*(.+)$", re.MULTILINE)

# Recommendation pattern in advisory logs
_REC_LINE_RE = re.compile(
    r"^\d+\.\s+\*\*\[(\w+)\]\*\*\s+(.+)$", re.MULTILINE
)

# Advisory header pattern
_ADVISORY_HEADER_RE = re.compile(
    r"^#\s+Advisory\s+(\d+)\s*\|.*?\|\s*(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}\s+UTC\s*\|\s*(.+)$",
    re.MULTILINE,
)

# Tags line pattern
_TAGS_RE = re.compile(r"^tags:\s*(.+)$", re.MULTILINE)


def _slugify_tags(title: str) -> list[str]:
    """Derive tags from a title slug."""
    words = re.split(r"[-_\s|]+", title.lower().strip())
    stop = {"the", "a", "an", "and", "or", "for", "to", "in", "of", "on", "is", "with"}
    return [w for w in words if w and w not in stop and len(w) > 2][:5]


def scan_d_nnn_entries(verbose: bool = False) -> list[dict]:
    """Scan product-design-as-intended.md for D-NNN Decision entries."""
    intent_file = REPO_ROOT / "_references" / "project" / "product-design-as-intended.md"
    if not intent_file.is_file():
        if verbose:
            print("  No product-design-as-intended.md found, skipping D-NNN scan")
        return []

    text = intent_file.read_text(encoding="utf-8", errors="replace")

    # Find ## Decisions section
    decisions_start = text.find("## Decisions")
    if decisions_start == -1:
        if verbose:
            print("  No ## Decisions section found")
        return []

    decisions_text = text[decisions_start:]
    entries = []

    for m in _D_NNN_RE.finditer(decisions_text):
        d_id = m.group(1)
        title = m.group(2).strip()

        # Extract the block until next ### or end
        block_start = m.end()
        next_heading = _D_NNN_RE.search(decisions_text, block_start)
        block = decisions_text[block_start : next_heading.start() if next_heading else len(decisions_text)]

        # Try to find a Decision: line
        decision_match = re.search(r"\*\*Decision\*\*:\s*(.+)", block)
        decision_stmt = decision_match.group(1).strip() if decision_match else title

        # Try to find source advisory
        source_match = re.search(r"advisory-(\d+)", block)
        source_id = f"advisory-{source_match.group(1)}" if source_match else None

        # Try to find date
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", block)
        date = date_match.group(1) if date_match else None

        entry = {
            "id": d_id,
            "source_type": "d-nnn",
            "source_id": source_id,
            "decision_statement": decision_stmt[:200],
            "rationale_summary": None,
            "tags": _slugify_tags(title),
            "date": date,
            "d_nnn_id": d_id,
            "priority": None,
        }
        entries.append(entry)
        if verbose:
            print(f"  D-NNN: {d_id} -- {title[:60]}")

    return entries


def scan_advisory_recommendations(verbose: bool = False) -> list[dict]:
    """Scan advisory logs for HIGH/MEDIUM recommendations."""
    if not ADVISORY_DIR.is_dir():
        if verbose:
            print(f"  Advisory directory not found: {ADVISORY_DIR}")
        return []

    entries = []
    advisory_files = sorted(ADVISORY_DIR.glob("advisory-*.md"))

    for fpath in advisory_files:
        text = fpath.read_text(encoding="utf-8", errors="replace")

        # Parse header
        header_match = _ADVISORY_HEADER_RE.search(text)
        if not header_match:
            continue

        adv_id = header_match.group(1)
        adv_date = header_match.group(2)
        adv_title = header_match.group(3).strip()

        # Parse tags if present
        tags_match = _TAGS_RE.search(text)
        if tags_match:
            tags = [t.strip() for t in tags_match.group(1).split(",")]
        else:
            tags = _slugify_tags(adv_title)

        # Find recommendations section
        rec_section = None
        for heading in ["## Recommendations Summary", "### Recommendations"]:
            idx = text.find(heading)
            if idx != -1:
                rec_section = text[idx:]
                # Truncate at next ## heading
                next_h2 = re.search(r"\n## ", rec_section[len(heading):])
                if next_h2:
                    rec_section = rec_section[: len(heading) + next_h2.start()]
                break

        if not rec_section:
            continue

        rec_idx = 0
        for m in _REC_LINE_RE.finditer(rec_section):
            priority_raw = m.group(1).lower()
            if priority_raw not in ("high", "medium"):
                continue

            rec_text = m.group(2).strip()
            rec_idx += 1

            entry = {
                "id": f"adv-{adv_id}-{rec_idx}",
                "source_type": "advisory",
                "source_id": f"advisory-{adv_id}",
                "decision_statement": rec_text[:200],
                "rationale_summary": None,
                "tags": tags,
                "date": adv_date,
                "d_nnn_id": None,
                "priority": priority_raw,
            }
            entries.append(entry)
            if verbose:
                print(f"  Advisory {adv_id} [{priority_raw}]: {rec_text[:60]}")

    return entries


def deduplicate(d_nnn_entries: list[dict], advisory_entries: list[dict]) -> list[dict]:
    """Deduplicate: if a D-NNN entry references the same advisory as a recommendation, keep only the D-NNN."""
    d_nnn_sources = {e["source_id"] for e in d_nnn_entries if e["source_id"]}
    filtered_advisory = [
        e for e in advisory_entries if e["source_id"] not in d_nnn_sources
    ]
    return d_nnn_entries + filtered_advisory


def generate_digest(verbose: bool = False) -> int:
    """Generate decision-digest.jsonl. Returns count of records written."""
    d_nnn = scan_d_nnn_entries(verbose=verbose)
    advisory = scan_advisory_recommendations(verbose=verbose)
    all_entries = deduplicate(d_nnn, advisory)

    if not all_entries:
        if verbose:
            print("No decisions found")
        return 0

    DIGEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DIGEST_FILE.open("w", encoding="utf-8") as f:
        for entry in all_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Generated {DIGEST_FILE.relative_to(REPO_ROOT)} with {len(all_entries)} records.")
    return len(all_entries)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a machine-readable decision digest from D-NNN entries and advisory recommendations"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show each entry being processed"
    )
    args = parser.parse_args()

    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    count = generate_digest(verbose=args.verbose)
    if count == 0:
        print("No decisions found -- digest file not created")


if __name__ == "__main__":
    main()
