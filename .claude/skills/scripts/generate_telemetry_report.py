#!/usr/bin/env python3
"""
generate_telemetry_report.py -- Aggregate telemetry.jsonl and print a markdown report.

Reads ${OUTPUT_DIR}/telemetry.jsonl, computes usage statistics, and writes a
markdown report to stdout.  Stdlib only (json, collections, datetime, pathlib).

Sections:
  1. Overview (total invocations, date range, unique skills)
  2. Skill frequency table (descending)
  3. Average duration by skill
  4. Outcome rates (success / partial / failed) by skill
  5. Weekly trend sparklines (Unicode block characters)
  6. Context budget distribution (if data present)

Usage
-----
    python .claude/skills/scripts/generate_telemetry_report.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Project config
# ---------------------------------------------------------------------------

sys.path.insert(0, str(Path(__file__).resolve().parent))
from project_config import REPO_ROOT, get  # noqa: E402

# ---------------------------------------------------------------------------
# Sparkline helpers
# ---------------------------------------------------------------------------

_BARS = " " + chr(0x2581) + chr(0x2582) + chr(0x2583) + chr(0x2584) + chr(0x2585) + chr(0x2586) + chr(0x2587) + chr(0x2588)


def _sparkline(values: list[int]) -> str:
    """Return a Unicode block-character sparkline for a list of counts."""
    if not values:
        return ""
    mx = max(values)
    if mx == 0:
        return _BARS[0] * len(values)
    return "".join(_BARS[min(round(v / mx * 8), 8)] for v in values)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def _parse_timestamp(raw: str) -> datetime | None:
    """Parse an ISO-8601 timestamp string, tolerant of trailing Z."""
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _iso_week_key(dt: datetime) -> str:
    """Return 'YYYY-WNN' for the given datetime."""
    iso = dt.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def _load_records(path: Path) -> list[dict]:
    """Read telemetry.jsonl, skipping blank or malformed lines."""
    if not path.is_file():
        return []

    records: list[dict] = []
    skipped = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            obj = json.loads(stripped)
        except json.JSONDecodeError:
            skipped += 1
            continue
        if not isinstance(obj, dict):
            skipped += 1
            continue
        records.append(obj)

    if skipped:
        print(
            f"<!-- WARNING: skipped {skipped} malformed line(s) in telemetry.jsonl -->",
            file=sys.stderr,
        )
    return records


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def _aggregate(records: list[dict]) -> dict:
    """Compute all aggregations from the raw records."""
    skill_counts: Counter = Counter()
    skill_durations: defaultdict[str, list[int]] = defaultdict(list)
    skill_outcomes: defaultdict[str, Counter] = defaultdict(Counter)
    budget_counts: Counter = Counter()
    weekly_counts: defaultdict[str, Counter] = defaultdict(Counter)
    timestamps: list[datetime] = []

    for rec in records:
        skill = rec.get("skill", "unknown")
        skill_counts[skill] += 1

        dur = rec.get("duration_seconds")
        if isinstance(dur, int) and dur >= 0:
            skill_durations[skill].append(dur)

        outcome = rec.get("outcome", "unknown")
        skill_outcomes[skill][outcome] += 1

        budget = rec.get("context_budget")
        if isinstance(budget, str) and budget:
            budget_counts[budget] += 1

        ts = _parse_timestamp(rec.get("timestamp", ""))
        if ts is not None:
            timestamps.append(ts)
            weekly_counts[skill][_iso_week_key(ts)] += 1

    # Determine the full week range
    all_weeks: list[str] = []
    if timestamps:
        mn = min(timestamps)
        mx = max(timestamps)
        # Walk week by week
        cur = mn - timedelta(days=mn.weekday())  # Monday of first week
        end = mx
        while cur <= end:
            all_weeks.append(_iso_week_key(cur))
            cur += timedelta(weeks=1)
        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for w in all_weeks:
            if w not in seen:
                seen.add(w)
                unique.append(w)
        all_weeks = unique

    return {
        "total": len(records),
        "skill_counts": skill_counts,
        "skill_durations": skill_durations,
        "skill_outcomes": skill_outcomes,
        "budget_counts": budget_counts,
        "weekly_counts": weekly_counts,
        "all_weeks": all_weeks,
        "timestamps": timestamps,
    }


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------


def _fmt_duration(seconds: float) -> str:
    """Format seconds as 'Xm Ys'."""
    m, s = divmod(int(seconds), 60)
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def _generate_report(agg: dict) -> str:
    """Build the full markdown report from aggregated data."""
    lines: list[str] = []
    total = agg["total"]
    skill_counts = agg["skill_counts"]
    skill_durations = agg["skill_durations"]
    skill_outcomes = agg["skill_outcomes"]
    budget_counts = agg["budget_counts"]
    weekly_counts = agg["weekly_counts"]
    all_weeks = agg["all_weeks"]
    timestamps = agg["timestamps"]

    # -- Section 1: Overview --
    lines.append("## Telemetry Report")
    lines.append("")
    lines.append("### Overview")
    lines.append("")
    lines.append(f"- **Total invocations**: {total}")
    if timestamps:
        mn = min(timestamps).strftime("%Y-%m-%d")
        mx = max(timestamps).strftime("%Y-%m-%d")
        lines.append(f"- **Date range**: {mn} to {mx}")
    else:
        lines.append("- **Date range**: N/A")
    lines.append(f"- **Unique skills**: {len(skill_counts)}")
    lines.append("")

    # -- Section 2: Skill frequency --
    lines.append("### Skill Frequency")
    lines.append("")
    lines.append("| Skill | Count | % |")
    lines.append("|-------|------:|--:|")
    for skill, count in skill_counts.most_common():
        pct = count / total * 100 if total else 0
        lines.append(f"| {skill} | {count} | {pct:.0f}% |")
    lines.append("")

    # -- Section 3: Average duration --
    lines.append("### Average Duration by Skill")
    lines.append("")
    lines.append("| Skill | Avg | Min | Max | Invocations |")
    lines.append("|-------|----:|----:|----:|------------:|")
    for skill, _ in skill_counts.most_common():
        durs = skill_durations.get(skill, [])
        if durs:
            avg = sum(durs) / len(durs)
            lines.append(
                f"| {skill} | {_fmt_duration(avg)} | {_fmt_duration(min(durs))} | {_fmt_duration(max(durs))} | {len(durs)} |"
            )
        else:
            lines.append(f"| {skill} | -- | -- | -- | 0 |")
    lines.append("")

    # -- Section 4: Outcome rates --
    lines.append("### Outcome Rates")
    lines.append("")
    lines.append("| Skill | Success | Partial | Failed |")
    lines.append("|-------|--------:|--------:|-------:|")
    for skill, _ in skill_counts.most_common():
        outcomes = skill_outcomes[skill]
        sk_total = sum(outcomes.values())
        s = outcomes.get("success", 0)
        p = outcomes.get("partial", 0)
        f = outcomes.get("failed", 0)
        if sk_total:
            lines.append(
                f"| {skill} | {s}/{sk_total} ({s/sk_total*100:.0f}%) | {p}/{sk_total} ({p/sk_total*100:.0f}%) | {f}/{sk_total} ({f/sk_total*100:.0f}%) |"
            )
        else:
            lines.append(f"| {skill} | -- | -- | -- |")
    lines.append("")

    # -- Section 5: Weekly trends --
    if all_weeks:
        lines.append("### Weekly Trends")
        lines.append("")
        lines.append(f"Weeks: {all_weeks[0]} to {all_weeks[-1]}")
        lines.append("")
        lines.append("| Skill | Trend | Weeks |")
        lines.append("|-------|-------|------:|")
        for skill, _ in skill_counts.most_common():
            week_data = weekly_counts.get(skill, {})
            counts = [week_data.get(w, 0) for w in all_weeks]
            spark = _sparkline(counts)
            lines.append(f"| {skill} | {spark} | {len(all_weeks)} |")
        lines.append("")

    # -- Section 6: Context budget distribution --
    if budget_counts:
        lines.append("### Context Budget Distribution")
        lines.append("")
        budget_total = sum(budget_counts.values())
        lines.append("| Budget | Count | % |")
        lines.append("|--------|------:|--:|")
        for budget, count in budget_counts.most_common():
            pct = count / budget_total * 100
            lines.append(f"| {budget} | {count} | {pct:.0f}% |")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    output_dir = get("OUTPUT_DIR", "_output")
    telemetry_path = REPO_ROOT / output_dir / "telemetry.jsonl"

    if not telemetry_path.is_file():
        print("## Telemetry Report\n\nNo telemetry data found.")
        return

    records = _load_records(telemetry_path)
    if not records:
        print("## Telemetry Report\n\nTelemetry file exists but contains no valid records.")
        return

    agg = _aggregate(records)
    print(_generate_report(agg))


if __name__ == "__main__":
    main()
