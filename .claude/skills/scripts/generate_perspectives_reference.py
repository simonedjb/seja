#!/usr/bin/env python3
"""
generate_perspectives_reference.py -- Generate the review-perspectives catalog.

Walks `_references/general/review-perspectives/*.md`, extracts the tag
(filename stem uppercased), a human name (from optional frontmatter, first
H1, or the uppercased tag), a one-line purpose (from optional frontmatter
`purpose`, or the first non-heading text snippet), and an optional tier,
then renders a single Markdown table alphabetized by tag.

If the perspectives directory is empty or absent, the output is a
placeholder document and the script exits 0 (graceful degradation).

Usage
-----
    python .claude/skills/scripts/generate_perspectives_reference.py \
        --output seja-public/docs/reference/perspectives.md

Flags:
    --output <path>           Default: <framework-root>/seja-public/docs/
                              reference/perspectives.md. Use "-" for stdout.
    --framework-root <path>   Auto-detected by walking up to find .claude/.
    --check                   CI staleness detection. Exit 1 if drift.
    --fixed-date <ISO8601>    Testing only: pin the preamble timestamp.
    --verbose                 Progress logging to stderr.

Exit codes:
    0  success (or in sync with --check)
    1  drift detected in --check mode
    2  script error
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Reuse the frontmatter reader from generate_framework_reference so we
# stay consistent with how the rest of the framework parses YAML blocks.
from generate_framework_reference import (  # noqa: E402
    _read_first_h1_and_lead,
    _read_yaml_frontmatter,
    _truncate,
)


_H1_DASH_RE = re.compile(r"^[A-Z0-9]+\s*[-\u2013\u2014]+\s*(.+?)\s*$")


def _find_framework_root(start: Path | None = None) -> Path:
    candidate = (start or SCRIPTS_DIR).resolve()
    while candidate != candidate.parent:
        if (candidate / ".claude").is_dir():
            return candidate
        candidate = candidate.parent
    return Path.cwd()


def _escape_pipes(text: str) -> str:
    return text.replace("|", "\\|")


def _extract_name_from_h1(h1: str, tag: str) -> str:
    """Given a H1 like `SEC -- Security` or `SEC \u2014 Security`, return `Security`."""
    if not h1:
        return tag
    match = _H1_DASH_RE.match(h1)
    if match:
        return match.group(1).strip()
    return h1.strip() or tag


def _first_list_item_or_paragraph(path: Path) -> str:
    """Return the first meaningful text after the H1 and any section headings.

    Strips leading list markers (`-`, `*`, `[P0]` style tags) so that list-only
    files (like the existing review-perspective checklists) still yield a
    usable purpose string.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    # Drop frontmatter
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    lines = text.splitlines()
    # Skip blank lines, H1/H2/H3, section markers
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        # Strip list markers and bracketed tags.
        cleaned = re.sub(r"^[-*]\s*", "", line)
        cleaned = re.sub(r"^\[[^\]]+\]\s*", "", cleaned)
        cleaned = cleaned.strip()
        if not cleaned:
            continue
        # Extract first sentence.
        match = re.match(r"(.+?[.!?])(?:\s|$)", cleaned)
        return match.group(1) if match else cleaned
    return ""


def collect_perspectives(framework_root: Path, verbose: bool = False) -> list[dict[str, str]]:
    """Return a list of perspective metadata dicts alphabetized by tag."""
    persp_dir = framework_root / "_references" / "general" / "review-perspectives"
    if not persp_dir.is_dir():
        return []
    results: list[dict[str, str]] = []
    for persp_md in sorted(persp_dir.glob("*.md")):
        tag = persp_md.stem.upper()
        fm = _read_yaml_frontmatter(persp_md) or {}
        h1, _lead = _read_first_h1_and_lead(persp_md)
        name = fm.get("name") or _extract_name_from_h1(h1, tag)
        purpose = fm.get("purpose") or _first_list_item_or_paragraph(persp_md)
        tier = fm.get("tier", "")
        entry = {
            "tag": tag,
            "name": name,
            "purpose": _truncate(purpose, 120) if purpose else "",
            "tier": tier,
        }
        results.append(entry)
        if verbose:
            print(f"  added: {tag} - {name}", file=sys.stderr)
    results.sort(key=lambda e: e["tag"])
    return results


def render_perspectives_reference(
    perspectives: list[dict[str, str]],
    generated_at: str,
) -> str:
    """Compose the full Markdown perspectives catalog."""
    preamble = (
        "<!--\n"
        "This file is generated by .claude/skills/scripts/generate_perspectives_reference.py.\n"
        "Do not edit by hand. To regenerate:\n"
        "    python .claude/skills/scripts/generate_perspectives_reference.py \\\n"
        "        --output seja-public/docs/reference/perspectives.md\n"
        "-->\n\n"
        "# SEJA review perspectives catalog\n\n"
    )

    if not perspectives:
        return (
            preamble
            + "No review perspectives defined in this framework checkout.\n"
        )

    preamble += (
        f"Generated {generated_at} from `_references/general/review-perspectives/`. "
        "`/plan` and `/check review` consult these perspectives during the "
        "review phase; each one evaluates code or a plan through a specific "
        "lens.\n\n"
        "| Tag | Name | Purpose | Tier |\n"
        "|---|---|---|---|\n"
    )
    rows: list[str] = []
    for entry in perspectives:
        tag_cell = f"`{_escape_pipes(entry['tag'])}`"
        name_cell = _escape_pipes(entry["name"])
        purpose_cell = _escape_pipes(entry["purpose"]) if entry["purpose"] else "-"
        tier_cell = _escape_pipes(entry["tier"]) if entry["tier"] else "-"
        rows.append(f"| {tag_cell} | {name_cell} | {purpose_cell} | {tier_cell} |")
    return preamble + "\n".join(rows) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the SEJA review-perspectives catalog",
    )
    parser.add_argument("--framework-root", default=None)
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
        print(f"ERROR: framework root does not exist: {framework_root}", file=sys.stderr)
        return 2

    if args.verbose:
        print(f"framework_root: {framework_root}", file=sys.stderr)

    perspectives = collect_perspectives(framework_root, verbose=args.verbose)

    if args.fixed_date:
        generated_at = args.fixed_date
    else:
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    rendered = render_perspectives_reference(perspectives, generated_at)

    if args.check:
        if not args.output or args.output == "-":
            print("ERROR: --check requires an --output file path", file=sys.stderr)
            return 2
        output_path = Path(args.output).resolve()
        if not output_path.is_file():
            print(f"DRIFT: output file does not exist: {output_path}", file=sys.stderr)
            return 1
        on_disk = output_path.read_text(encoding="utf-8")
        if on_disk.replace("\r\n", "\n") == rendered.replace("\r\n", "\n"):
            if args.verbose:
                print(f"OK: {output_path} is up to date.", file=sys.stderr)
            return 0
        print(f"DRIFT: {output_path} differs from generator output", file=sys.stderr)
        return 1

    output_arg = args.output
    if output_arg is None:
        output_arg = str(
            framework_root / "seja-public" / "docs" / "reference" / "perspectives.md"
        )

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
