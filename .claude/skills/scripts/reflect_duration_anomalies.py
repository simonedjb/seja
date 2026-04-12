#!/usr/bin/env python3
"""reflect_duration_anomalies — surface skill runs whose duration is anomalously long.

For each record in the window, compute the historical median ``duration_seconds``
across all records with the same ``skill`` name (drawn from an optional separate
historical JSONL, otherwise from the window itself). Flag records whose current
duration is >= 2x the historical median, provided the historical sample size is
>= 3. See plan-000295 Step 5 for the full specification.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path


_DURATION_RATIO_THRESHOLD = 2.0
_HISTORICAL_MIN_SAMPLE_SIZE = 3


def _valid_duration(record: dict) -> bool:
    d = record.get("duration_seconds")
    return isinstance(d, (int, float)) and d > 0


def analyze(window: list[dict], historical: list[dict] | None = None) -> dict:
    """Flag records whose ``duration_seconds`` is anomalous for their skill.

    Args:
        window: telemetry records to scan for anomalies.
        historical: optional wider dataset used to compute per-skill medians.
            Defaults to ``window`` when omitted.

    Returns:
        A dict with ``anomalies``, ``observations``, and ``degraded``.
    """
    empty: dict = {"anomalies": [], "observations": [], "degraded": False}
    if not window:
        return empty

    # Degraded guard: no record in the window has a numeric duration.
    if not any(_valid_duration(r) for r in window):
        return {
            **empty,
            "degraded": True,
            "reason": "no duration data",
        }

    source = historical if historical is not None else window
    per_skill_durations: dict[str, list[float]] = defaultdict(list)
    for r in source:
        if not isinstance(r.get("skill"), str):
            continue
        if _valid_duration(r):
            per_skill_durations[r["skill"]].append(float(r["duration_seconds"]))

    medians: dict[str, float] = {}
    sample_sizes: dict[str, int] = {}
    for skill, durations in per_skill_durations.items():
        sample_sizes[skill] = len(durations)
        if durations:
            medians[skill] = float(statistics.median(durations))

    anomalies: list[dict] = []
    for r in window:
        if not isinstance(r.get("skill"), str) or not _valid_duration(r):
            continue
        skill = r["skill"]
        median = medians.get(skill)
        sample = sample_sizes.get(skill, 0)
        if median is None or median <= 0:
            continue
        if sample < _HISTORICAL_MIN_SAMPLE_SIZE:
            continue
        duration = float(r["duration_seconds"])
        ratio = duration / median
        if ratio >= _DURATION_RATIO_THRESHOLD:
            anomalies.append(
                {
                    "skill": skill,
                    "id": r.get("id"),
                    "duration_seconds": duration,
                    "historical_median": median,
                    "ratio": round(ratio, 2),
                    "historical_sample_size": sample,
                }
            )

    observations: list[str] = []
    for a in anomalies:
        observations.append(
            f"I notice that `{a['skill']}` (id `{a['id']}`) took "
            f"{int(a['duration_seconds'])} seconds, about {a['ratio']}x your "
            f"historical median of {int(a['historical_median'])} seconds. "
            f"Here is a question I am holding for you: what was different "
            f"about that session?"
        )

    return {
        "anomalies": anomalies,
        "observations": observations,
        "degraded": False,
    }


def _load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    if not path.is_file():
        return records
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def _main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Surface duration anomalies in a telemetry window."
    )
    parser.add_argument("--window", type=Path, help="Path to a JSONL telemetry window.")
    parser.add_argument(
        "--historical",
        type=Path,
        default=None,
        help="Optional JSONL with the full history used to compute medians.",
    )
    if len(argv) == 0:
        parser.print_help()
        return 0
    args = parser.parse_args(argv)
    if args.window is None:
        parser.print_help()
        return 0
    window = _load_jsonl(args.window)
    historical = _load_jsonl(args.historical) if args.historical else None
    result = analyze(window, historical)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
