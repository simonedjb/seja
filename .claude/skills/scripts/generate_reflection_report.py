#!/usr/bin/env python3
"""generate_reflection_report — orchestrator for the /reflect skill.

Loads a telemetry window, runs the 5 V1 reflection primitives
(``reflect_sequence_mining``, ``reflect_duration_anomalies``,
``reflect_revision_rate``, ``reflect_stuck_loops``,
``reflect_decision_reversals``), and composes their observations into a
strictly non-prescriptive markdown reflection report under
``${REFLECTIONS_DIR}/reflection-<id>-<slug>.md``. See plan-000295 Step 6 for the
full specification. The orchestrator embeds primitive observation sentences
verbatim and never emits its own "you should", "consider", or other
prescriptive phrasings; the only hand-off signal is the static ``What to do
with this`` paragraph, which points the reader at ``/advise`` for
prescriptive follow-up.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import reflect_decision_reversals
import reflect_duration_anomalies
import reflect_revision_rate
import reflect_sequence_mining
import reflect_stuck_loops


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_RELATIVE_RE = re.compile(r"^(\d+)d$", re.IGNORECASE)
_QUESTION_MARKER = "Here is a question I am holding for you:"
_SLUG_RE = re.compile(r"[^a-z0-9]+")

_SECTION_FALLBACKS: dict[str, str] = {
    "sequence_mining": "No notable sequences this window.",
    "duration_anomalies": "No notable duration anomalies this window.",
    "revision_rate": "No notable revision patterns this window.",
    "stuck_loops": "No stuck loops this window.",
    "decision_reversals": (
        "No decision reversals this window (or decision_points field not yet "
        "populated)."
    ),
}

_SECTION_TITLES: dict[str, str] = {
    "sequence_mining": "Sequences I noticed",
    "duration_anomalies": "Durations I noticed",
    "revision_rate": "Revisions I noticed",
    "stuck_loops": "Stuck loops I noticed",
    "decision_reversals": "Decisions I noticed were reversed",
}

_SECTION_ORDER: list[str] = [
    "sequence_mining",
    "duration_anomalies",
    "revision_rate",
    "stuck_loops",
    "decision_reversals",
]


# ---------------------------------------------------------------------------
# Window loading and filtering
# ---------------------------------------------------------------------------


def _parse_iso(value: str) -> datetime:
    """Parse an ISO-8601 timestamp, accepting the trailing-Z shape."""
    v = value
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"
    dt = datetime.fromisoformat(v)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def load_window(
    telemetry_path: Path,
    since_datetime: datetime,
    skill_filter: str | None = None,
) -> list[dict]:
    """Read ``telemetry_path``, filter by since and optional skill, sort asc.

    Records whose ``timestamp`` field is missing or unparseable are skipped.
    Records whose parsed timestamp is older than ``since_datetime`` are
    skipped. If ``skill_filter`` is not ``None``, records whose ``skill`` does
    not equal the filter are skipped.
    """
    if not telemetry_path.is_file():
        return []
    records: list[tuple[datetime, dict]] = []
    with telemetry_path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(rec, dict):
                continue
            ts_raw = rec.get("timestamp")
            if not isinstance(ts_raw, str) or not ts_raw:
                continue
            try:
                ts = _parse_iso(ts_raw)
            except ValueError:
                continue
            if ts < since_datetime:
                continue
            if skill_filter is not None and rec.get("skill") != skill_filter:
                continue
            records.append((ts, rec))
    records.sort(key=lambda pair: pair[0])
    return [rec for _, rec in records]


def load_full_history(telemetry_path: Path) -> list[dict]:
    """Load every parseable record from the telemetry file (unfiltered).

    Used as the ``historical`` argument for ``reflect_duration_anomalies`` so
    that short windows still get reliable per-skill medians.
    """
    if not telemetry_path.is_file():
        return []
    records: list[dict] = []
    with telemetry_path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(rec, dict):
                records.append(rec)
    return records


# ---------------------------------------------------------------------------
# Briefs map and git range
# ---------------------------------------------------------------------------


def load_briefs_map(briefs_path: Path | None) -> dict[str, str]:
    """Delegate to ``reflect_stuck_loops._load_briefs_map`` for format parity.

    Returns an empty dict when the briefs file is missing or unreadable.
    """
    if briefs_path is None:
        return {}
    try:
        return reflect_stuck_loops._load_briefs_map(briefs_path)
    except Exception:
        return {}


def compute_git_range(window: list[dict]) -> tuple[str, str]:
    """Return ``(earliest_sha, latest_sha)`` from the window's ``git_commit_sha``.

    The window is assumed to be sorted by timestamp ascending. If no record
    carries a SHA, returns ``("", "")``.
    """
    shas: list[str] = []
    for rec in window:
        sha = rec.get("git_commit_sha")
        if isinstance(sha, str) and sha:
            shas.append(sha)
    if not shas:
        return ("", "")
    return (shas[0], shas[-1])


# ---------------------------------------------------------------------------
# Primitive orchestration
# ---------------------------------------------------------------------------


def run_primitives(
    window: list[dict],
    historical: list[dict] | None,
    briefs_map: dict[str, str] | None,
) -> dict[str, dict]:
    """Run every primitive against the window and return keyed results."""
    return {
        "sequence_mining": reflect_sequence_mining.analyze(window),
        "duration_anomalies": reflect_duration_anomalies.analyze(
            window, historical=historical
        ),
        "revision_rate": reflect_revision_rate.analyze(window),
        "stuck_loops": reflect_stuck_loops.analyze(
            window, briefs_map=briefs_map or {}
        ),
        "decision_reversals": reflect_decision_reversals.analyze(window),
    }


# ---------------------------------------------------------------------------
# Report composition
# ---------------------------------------------------------------------------


def _format_utc(dt: datetime) -> str:
    """Format a datetime as ``YYYY-MM-DD HH:MM UTC`` (no Z, no +00:00)."""
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _format_since(dt: datetime) -> str:
    """Format a cutoff datetime for display in the report body."""
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _section_body(primitive_key: str, result: dict) -> str:
    """Render the body of a primitive's section.

    Emits the degraded-reason note when ``degraded == True`` and the fallback
    phrasing when there are no observations. Otherwise joins the primitive's
    ``observations`` list verbatim, one per line, separated by blank lines.
    """
    lines: list[str] = []
    if result.get("degraded"):
        reason = result.get("reason") or "degraded"
        lines.append(f"(Degraded: {reason})")
    observations = result.get("observations") or []
    if observations:
        if lines:
            lines.append("")
        lines.append("\n\n".join(observations))
    elif not lines:
        lines.append(_SECTION_FALLBACKS[primitive_key])
    else:
        lines.append("")
        lines.append(_SECTION_FALLBACKS[primitive_key])
    return "\n".join(lines)


def _extract_questions(results: dict[str, dict]) -> list[str]:
    """Collect all 'Here is a question I am holding for you: ...' fragments.

    Walks every primitive's ``observations`` list, finds the marker, extracts
    the tail, and returns a de-duplicated list preserving first-seen order.
    """
    seen: set[str] = set()
    out: list[str] = []
    for key in _SECTION_ORDER:
        for obs in results.get(key, {}).get("observations", []) or []:
            idx = obs.find(_QUESTION_MARKER)
            if idx == -1:
                continue
            tail = obs[idx + len(_QUESTION_MARKER) :].strip()
            # Drop surrounding whitespace/newlines that the primitive may have
            # wrapped into the sentence.
            tail = " ".join(tail.split())
            if not tail:
                continue
            if tail in seen:
                continue
            seen.add(tail)
            out.append(tail)
    return out


def compose_report(
    reflection_id: str,
    title: str,
    since: datetime,
    now: datetime,
    window: list[dict],
    git_range: tuple[str, str],
    results: dict[str, dict],
    skill_filter: str | None = None,
) -> str:
    """Assemble the full markdown reflection report."""
    now_str = _format_utc(now)
    since_str = _format_since(since)
    count = len(window)
    skills_desc = (
        f"filtered to {skill_filter}" if skill_filter is not None else "all"
    )
    earliest, latest = git_range
    git_range_str = f"{earliest}..{latest}" if (earliest or latest) else ".."

    sections: list[str] = []
    sections.append(f"# Reflection {reflection_id} | {now_str} | {title}")
    sections.append("")
    sections.append("## Window analyzed")
    sections.append("")
    sections.append(f"- From: {since_str}")
    sections.append(f"- To: {now_str}")
    sections.append(f"- Skills: {skills_desc}")
    sections.append(f"- Records: {count}")
    sections.append(f"- Git range: {git_range_str}")
    sections.append("")
    sections.append("## Observations")
    sections.append("")

    for key in _SECTION_ORDER:
        sections.append(f"### {_SECTION_TITLES[key]}")
        sections.append("")
        sections.append(_section_body(key, results.get(key, {})))
        sections.append("")

    sections.append("## Questions I am holding for you")
    sections.append("")
    questions = _extract_questions(results)
    if questions:
        for q in questions:
            sections.append(f"- {q}")
    else:
        sections.append("None this window.")
    sections.append("")

    sections.append("## What to do with this")
    sections.append("")
    sections.append(
        "These are descriptive observations and questions, not prescriptions. "
        "If any of these patterns suggests something you want to investigate "
        "prescriptively, run `/advise` with the specific pattern as your "
        "question -- for example, `/advise Why do I amend /plan drafts 80% of "
        "the time? What should I include in my briefs?`"
    )
    sections.append("")

    sections.append("## Signature")
    sections.append("")
    sections.append("- Generated by `/reflect` v1")
    sections.append(f"- Window: {since_str} to {now_str}")
    sections.append(
        "- Primitives run: sequence_mining, duration_anomalies, "
        "revision_rate, stuck_loops, decision_reversals"
    )
    sections.append(f"- Telemetry records analyzed: {count}")
    sections.append("")

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# CLI entry
# ---------------------------------------------------------------------------


def _slugify(title: str) -> str:
    lowered = title.strip().lower()
    slug = _SLUG_RE.sub("-", lowered).strip("-")
    return slug or "reflection"


def _synthesize_title(window_count: int, results: dict[str, dict]) -> str:
    notable = sum(
        1
        for key in _SECTION_ORDER
        if results.get(key, {}).get("observations")
    )
    days_hint = "reflection"
    return f"{days_hint} - {window_count} records, {notable} notable patterns"


def _resolve_since(since_arg: str, now: datetime) -> datetime:
    """Resolve either an ISO timestamp or a relative ``<N>d`` into a datetime."""
    rel = _RELATIVE_RE.match(since_arg.strip())
    if rel:
        days = int(rel.group(1))
        return now - timedelta(days=days)
    return _parse_iso(since_arg)


def _resolve_paths(
    window_override: Path | None,
) -> tuple[Path, Path | None, Path]:
    """Return (telemetry_path, briefs_path, reflections_dir)."""
    try:
        import project_config  # type: ignore
    except Exception:
        project_config = None  # type: ignore

    if window_override is not None:
        telemetry_path = window_override
    elif project_config is not None:
        output_dir = project_config.get_path("OUTPUT_DIR")
        if output_dir is None:
            telemetry_path = project_config.REPO_ROOT / "_output" / "telemetry.jsonl"
        else:
            telemetry_path = output_dir / "telemetry.jsonl"
    else:
        telemetry_path = Path("_output/telemetry.jsonl")

    briefs_path: Path | None = None
    reflections_dir: Path
    if project_config is not None:
        briefs_path = project_config.get_path("BRIEFS_FILE")
        reflections_dir = (
            project_config.get_path("REFLECTIONS_DIR")
            or project_config.REPO_ROOT / "_output" / "reflections"
        )
    else:
        reflections_dir = Path("_output/reflections")

    return telemetry_path, briefs_path, reflections_dir


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compose a non-prescriptive reflection report from telemetry and "
            "the 5 V1 reflection primitives."
        )
    )
    parser.add_argument(
        "--window",
        type=Path,
        default=None,
        help="Path to the telemetry JSONL file. Default: ${OUTPUT_DIR}/telemetry.jsonl.",
    )
    parser.add_argument(
        "--since",
        type=str,
        default="30d",
        help=(
            "Window cutoff. Either an ISO-8601 datetime "
            "(e.g. 2026-03-12T00:00:00Z) or a relative duration like '30d', "
            "'14d', '7d'. Default: 30d."
        ),
    )
    parser.add_argument(
        "--skill-filter",
        type=str,
        default=None,
        help="Optional skill name to filter the window by.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help=(
            "Explicit output path for the report. If omitted, the report "
            "lands at ${REFLECTIONS_DIR}/reflection-<id>-<slug>.md and "
            "--reflection-id is required."
        ),
    )
    parser.add_argument(
        "--reflection-id",
        type=str,
        default=None,
        help="6-digit reflection ID (callers typically reserve it via reserve_id.py).",
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Short title for the report header.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the composed report to stdout without writing to disk.",
    )

    args = parser.parse_args(argv)

    now = datetime.now(timezone.utc)
    try:
        since = _resolve_since(args.since, now)
    except ValueError as exc:
        print(f"ERROR: could not parse --since {args.since!r}: {exc}", file=sys.stderr)
        return 2

    telemetry_path, briefs_path, reflections_dir = _resolve_paths(args.window)

    window = load_window(telemetry_path, since, skill_filter=args.skill_filter)
    historical = load_full_history(telemetry_path)
    briefs_map = load_briefs_map(briefs_path)

    results = run_primitives(window, historical=historical, briefs_map=briefs_map)
    git_range = compute_git_range(window)

    reflection_id = args.reflection_id or "000000"
    if reflection_id != "000000":
        reflection_id = reflection_id.zfill(6)
    title = args.title or _synthesize_title(len(window), results)

    report = compose_report(
        reflection_id=reflection_id,
        title=title,
        since=since,
        now=now,
        window=window,
        git_range=git_range,
        results=results,
        skill_filter=args.skill_filter,
    )

    if args.dry_run:
        sys.stdout.write(report)
        if not report.endswith("\n"):
            sys.stdout.write("\n")
        return 0

    if args.out is None:
        if args.reflection_id is None:
            print(
                "ERROR: --out is required when --reflection-id is not provided",
                file=sys.stderr,
            )
            return 2
        slug = _slugify(title)
        out_path = reflections_dir / f"reflection-{reflection_id}-{slug}.md"
    else:
        out_path = args.out

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
