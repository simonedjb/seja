#!/usr/bin/env python3
# designer: When /reflect --deep needs to know which records match a scope
#   keyword and/or date range, I'm the resolver that searches across briefs,
#   telemetry, and output file tags to build the filtered window -- grouping
#   matches by provenance so you see what matched and why.
"""reflect_deep_scope -- scope resolution and filtering for /reflect --deep.

Invocation: script-invoked, user-cli
Lifecycle: active

Parses briefs.md, telemetry.jsonl, and output file headers to resolve a scope
keyword and/or date range into a filtered set of matching records. Groups
matches by provenance source (skill name, brief text, research tags, output
filename) and returns a structured result with the filtered telemetry window,
briefs window, and match metadata.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass
class ScopeResult:
    """Result of scope resolution across briefs, telemetry, and output tags."""

    telemetry_window: list[dict] = field(default_factory=list)
    briefs_window: list[dict] = field(default_factory=list)
    match_counts: dict[str, int] = field(default_factory=dict)
    matched_ids: set[str] = field(default_factory=set)
    date_range: tuple[datetime, datetime] = field(
        default_factory=lambda: (
            datetime.min.replace(tzinfo=timezone.utc),
            datetime.max.replace(tzinfo=timezone.utc),
        )
    )


# ---------------------------------------------------------------------------
# Date parsing
# ---------------------------------------------------------------------------

_RELATIVE_RE = re.compile(r"^(\d+)d$", re.IGNORECASE)


def parse_since(value: str) -> datetime:
    """Parse a --since value as either a relative ``Nd`` duration or ISO datetime."""
    m = _RELATIVE_RE.match(value.strip())
    if m:
        days = int(m.group(1))
        return datetime.now(timezone.utc) - timedelta(days=days)
    # Try ISO datetime
    text = value.strip()
    # Append UTC if no timezone info
    try:
        dt = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"Cannot parse --since value: {value!r}") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def parse_until(value: str) -> datetime:
    """Parse a --until value as an ISO datetime."""
    text = value.strip()
    try:
        dt = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"Cannot parse --until value: {value!r}") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


# ---------------------------------------------------------------------------
# Briefs parsing
# ---------------------------------------------------------------------------

_DONE_RE = re.compile(
    r"^DONE\s*\|\s*(?P<end>[^|]+)\|\s*STARTED\s*\|\s*(?P<start>[^|]+)\|\s*(?P<skill>[^|]+)"
    r"(?:\|\s*(?P<rest>.*))?$"
)
_STARTED_RE = re.compile(
    r"^STARTED\s*\|\s*(?P<start>[^|]+)\|\s*(?P<skill>[^|]+)"
    r"(?:\|\s*(?P<rest>.*))?$"
)


def _parse_brief_timestamp(raw: str) -> datetime | None:
    """Parse a brief timestamp like ``2026-05-03 16:43 UTC``."""
    raw = raw.strip()
    # Remove trailing " UTC" and treat as UTC
    if raw.upper().endswith(" UTC"):
        raw = raw[:-4].strip()
    try:
        dt = datetime.strptime(raw, "%Y-%m-%d %H:%M")
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _extract_plan_id(text: str) -> str | None:
    """Extract a plan ID from the extra fields of a DONE brief line."""
    if not text:
        return None
    m = re.search(r"PLAN\s*\|\s*(\d+)", text)
    if m:
        return m.group(1)
    return None


def parse_briefs(briefs_path: Path) -> list[dict]:
    """Parse briefs.md into structured records."""
    records: list[dict] = []
    if not briefs_path.is_file():
        return records
    with briefs_path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            # Skip header lines
            if line.startswith("#"):
                continue

            record: dict | None = None
            m_done = _DONE_RE.match(line)
            if m_done:
                start_dt = _parse_brief_timestamp(m_done.group("start"))
                end_dt = _parse_brief_timestamp(m_done.group("end"))
                skill = m_done.group("skill").strip()
                rest = m_done.group("rest") or ""
                # Split rest into remaining pipe-separated fields
                parts = [p.strip() for p in rest.split("|")]
                brief_text = parts[-1] if parts else ""
                plan_id = _extract_plan_id(rest)
                record = {
                    "status": "DONE",
                    "start": start_dt.isoformat() if start_dt else None,
                    "end": end_dt.isoformat() if end_dt else None,
                    "skill": skill,
                    "brief": brief_text,
                    "plan_id": plan_id,
                    "raw": line,
                }
            else:
                m_started = _STARTED_RE.match(line)
                if m_started:
                    start_dt = _parse_brief_timestamp(m_started.group("start"))
                    skill = m_started.group("skill").strip()
                    rest = m_started.group("rest") or ""
                    parts = [p.strip() for p in rest.split("|")]
                    brief_text = parts[-1] if parts else ""
                    plan_id = _extract_plan_id(rest)
                    record = {
                        "status": "STARTED",
                        "start": start_dt.isoformat() if start_dt else None,
                        "end": None,
                        "skill": skill,
                        "brief": brief_text,
                        "plan_id": plan_id,
                        "raw": line,
                    }

            if record is not None:
                records.append(record)
    return records


# ---------------------------------------------------------------------------
# Telemetry parsing
# ---------------------------------------------------------------------------


def parse_telemetry(telemetry_path: Path) -> list[dict]:
    """Parse telemetry.jsonl into a list of dicts."""
    records: list[dict] = []
    if not telemetry_path.is_file():
        return records
    with telemetry_path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


# ---------------------------------------------------------------------------
# Output file tag scanning
# ---------------------------------------------------------------------------


def scan_output_tags(file_path: Path, output_dir: Path) -> list[str]:
    """Read the first 10 lines of an output file looking for a tags: line.

    Returns the list of tag strings, or an empty list if none found.
    """
    # Resolve relative paths against the output_dir parent
    if not file_path.is_absolute():
        file_path = output_dir.parent / file_path
    if not file_path.is_file():
        return []
    try:
        with file_path.open("r", encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh):
                if i >= 10:
                    break
                stripped = line.strip()
                if stripped.lower().startswith("tags:"):
                    tag_text = stripped[5:].strip()
                    return [t.strip() for t in tag_text.split(",") if t.strip()]
    except OSError:
        pass
    return []


# ---------------------------------------------------------------------------
# Date-range filtering
# ---------------------------------------------------------------------------


def _record_timestamp(record: dict) -> datetime | None:
    """Extract a datetime from a telemetry record's timestamp field."""
    ts = record.get("timestamp")
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _brief_start_dt(record: dict) -> datetime | None:
    """Extract a datetime from a brief record's start field."""
    start = record.get("start")
    if not start:
        return None
    try:
        dt = datetime.fromisoformat(start)
    except (ValueError, AttributeError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def filter_by_date(records: list[dict], since: datetime, until: datetime,
                   timestamp_fn) -> list[dict]:
    """Filter records to those within [since, until]."""
    filtered: list[dict] = []
    for rec in records:
        dt = timestamp_fn(rec)
        if dt is None:
            continue
        if since <= dt <= until:
            filtered.append(rec)
    return filtered


# ---------------------------------------------------------------------------
# Scope matching
# ---------------------------------------------------------------------------


def _matches_scope(record: dict, scope: str, tags_cache: dict[str, list[str]],
                   output_dir: Path, is_telemetry: bool) -> set[str]:
    """Check if a record matches the scope keyword.

    Returns a set of provenance sources that matched (may be empty).
    """
    matched: set[str] = set()
    scope_lower = scope.lower()

    # 1. Skill name match (exact, case-insensitive)
    skill = record.get("skill", "")
    if isinstance(skill, str) and skill.strip().lower() == scope_lower:
        matched.add("skill_name")

    # 2. Brief text match (case-insensitive substring)
    brief = record.get("brief", "")
    if isinstance(brief, str) and scope_lower in brief.lower():
        matched.add("brief_text")

    if is_telemetry:
        output_file = record.get("output_file")
        if output_file:
            # 3. Output filename match (case-insensitive substring on filename)
            fname = Path(output_file).name.lower()
            if scope_lower in fname:
                matched.add("output_filename")

            # 4. Research tags match
            if output_file not in tags_cache:
                tags_cache[output_file] = scan_output_tags(
                    Path(output_file), output_dir
                )
            tags = tags_cache[output_file]
            for tag in tags:
                if scope_lower in tag.lower():
                    matched.add("research_tags")
                    break

    return matched


# ---------------------------------------------------------------------------
# Main resolve function
# ---------------------------------------------------------------------------


def resolve_scope(
    scope: str | None,
    since: str | None,
    until: str | None,
    briefs_path: Path,
    telemetry_path: Path,
    output_dir: Path,
) -> ScopeResult:
    """Resolve a scope keyword and/or date range into filtered records.

    Args:
        scope: Optional keyword to match against skill names, brief text,
            research tags, and output filenames.
        since: Optional start bound as ``Nd`` relative duration or ISO datetime.
        until: Optional end bound as ISO datetime.
        briefs_path: Path to briefs.md.
        telemetry_path: Path to telemetry.jsonl.
        output_dir: Root output directory for resolving relative file paths.

    Returns:
        A ScopeResult with filtered windows, match counts, and metadata.
    """
    # Parse date bounds
    since_dt = parse_since(since) if since else datetime.min.replace(tzinfo=timezone.utc)
    until_dt = parse_until(until) if until else datetime.max.replace(tzinfo=timezone.utc)

    # Parse sources
    all_briefs = parse_briefs(briefs_path)
    all_telemetry = parse_telemetry(telemetry_path)

    # Date-range filter
    briefs_in_range = filter_by_date(all_briefs, since_dt, until_dt, _brief_start_dt)
    telemetry_in_range = filter_by_date(all_telemetry, since_dt, until_dt, _record_timestamp)

    # If no scope keyword, return all records in range
    if not scope:
        all_ids = set()
        for rec in telemetry_in_range:
            rec_id = rec.get("id")
            if rec_id:
                all_ids.add(str(rec_id))
        for rec in briefs_in_range:
            plan_id = rec.get("plan_id")
            if plan_id:
                all_ids.add(str(plan_id))

        return ScopeResult(
            telemetry_window=telemetry_in_range,
            briefs_window=briefs_in_range,
            match_counts={
                "total_telemetry": len(telemetry_in_range),
                "total_briefs": len(briefs_in_range),
            },
            matched_ids=all_ids,
            date_range=(since_dt, until_dt),
        )

    # Scope matching with provenance tracking
    tags_cache: dict[str, list[str]] = {}
    matched_telemetry: list[dict] = []
    matched_briefs: list[dict] = []
    provenance_counts: dict[str, int] = {
        "skill_name": 0,
        "brief_text": 0,
        "output_filename": 0,
        "research_tags": 0,
    }
    matched_ids: set[str] = set()

    for rec in telemetry_in_range:
        sources = _matches_scope(rec, scope, tags_cache, output_dir, is_telemetry=True)
        if sources:
            matched_telemetry.append(rec)
            for src in sources:
                provenance_counts[src] = provenance_counts.get(src, 0) + 1
            rec_id = rec.get("id")
            if rec_id:
                matched_ids.add(str(rec_id))

    for rec in briefs_in_range:
        sources = _matches_scope(rec, scope, tags_cache, output_dir, is_telemetry=False)
        if sources:
            matched_briefs.append(rec)
            for src in sources:
                provenance_counts[src] = provenance_counts.get(src, 0) + 1
            plan_id = rec.get("plan_id")
            if plan_id:
                matched_ids.add(str(plan_id))

    return ScopeResult(
        telemetry_window=matched_telemetry,
        briefs_window=matched_briefs,
        match_counts=provenance_counts,
        matched_ids=matched_ids,
        date_range=(since_dt, until_dt),
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _scope_result_to_dict(result: ScopeResult) -> dict:
    """Convert a ScopeResult to a JSON-serializable dict."""
    start_dt, end_dt = result.date_range
    return {
        "telemetry_window": result.telemetry_window,
        "briefs_window": result.briefs_window,
        "match_counts": result.match_counts,
        "matched_ids": sorted(result.matched_ids),
        "date_range": [start_dt.isoformat(), end_dt.isoformat()],
    }


def main() -> int:
    """CLI entry point."""
    # Ensure stdout can handle Unicode on all platforms (Windows cp1252 workaround)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Resolve a scope keyword and/or date range into filtered "
        "briefs and telemetry records."
    )
    parser.add_argument(
        "--scope",
        default=None,
        help="Keyword to match against skill names, brief text, research tags, "
        "and output filenames.",
    )
    parser.add_argument(
        "--since",
        default=None,
        help="Start date filter. Accepts Nd relative duration (e.g. 7d) or "
        "ISO datetime.",
    )
    parser.add_argument(
        "--until",
        default=None,
        help="End date filter as ISO datetime.",
    )
    parser.add_argument(
        "--briefs",
        type=Path,
        default=Path("_output/briefs.md"),
        help="Path to briefs.md (default: _output/briefs.md).",
    )
    parser.add_argument(
        "--telemetry",
        type=Path,
        default=Path("_output/telemetry.jsonl"),
        help="Path to telemetry.jsonl (default: _output/telemetry.jsonl).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("_output"),
        help="Root output directory for resolving relative file paths "
        "(default: _output).",
    )
    args = parser.parse_args()

    result = resolve_scope(
        scope=args.scope,
        since=args.since,
        until=args.until,
        briefs_path=args.briefs,
        telemetry_path=args.telemetry,
        output_dir=args.output_dir,
    )

    output = _scope_result_to_dict(result)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
