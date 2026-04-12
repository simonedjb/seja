#!/usr/bin/env python3
"""reflect_revision_rate — per-skill rate of user-revised outputs.

Scans the telemetry window for records whose ``user_revised_output`` field has
been populated (post-skill always writes ``null``; the ``/reflect`` skill is
the lazy computer that fills this in). Groups by skill and reports the
revision rate, flagging skills with a rate >= 0.5 over at least 4 scored
runs. See plan-000295 Step 5 for the full specification.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


_RATE_FLAG_THRESHOLD = 0.5
_MIN_SCORED_RUNS = 4


def analyze(window: list[dict]) -> dict:
    """Compute per-skill rate of ``user_revised_output == True``.

    Records whose ``user_revised_output`` is ``None`` are excluded from both
    numerator and denominator of a skill's rate.

    Args:
        window: telemetry records.

    Returns:
        A dict with ``per_skill``, ``high_revision_skills``, ``observations``,
        and ``degraded``.
    """
    empty: dict = {
        "per_skill": [],
        "high_revision_skills": [],
        "observations": [],
        "degraded": False,
    }
    if not window:
        return empty

    # Degraded guard: no record in the window has ever had user_revised_output
    # populated. /reflect has not back-filled it yet.
    if all(r.get("user_revised_output") is None for r in window):
        return {
            **empty,
            "degraded": True,
            "reason": (
                "user_revised_output not yet computed for this window; "
                "/reflect computes it lazily"
            ),
        }

    grouped: dict[str, list[bool]] = defaultdict(list)
    for r in window:
        if not isinstance(r.get("skill"), str):
            continue
        value = r.get("user_revised_output")
        if value is None:
            continue
        grouped[r["skill"]].append(bool(value))

    per_skill: list[dict] = []
    for skill in sorted(grouped):
        flags = grouped[skill]
        total = len(flags)
        revised = sum(1 for f in flags if f)
        rate = revised / total if total else 0.0
        per_skill.append(
            {
                "skill": skill,
                "total": total,
                "revised": revised,
                "rate": round(rate, 4),
            }
        )

    high = [
        entry
        for entry in per_skill
        if entry["total"] >= _MIN_SCORED_RUNS and entry["rate"] >= _RATE_FLAG_THRESHOLD
    ]

    observations: list[str] = []
    for entry in high:
        pct = int(round(entry["rate"] * 100))
        observations.append(
            f"I notice that you revised the output of `{entry['skill']}` in "
            f"{entry['revised']} of your last {entry['total']} invocations "
            f"({pct}%). Here is a question I am holding for you: what might I "
            f"be missing in how I draft for this skill?"
        )

    return {
        "per_skill": per_skill,
        "high_revision_skills": high,
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
        description="Compute per-skill user-revision rates over a telemetry window."
    )
    parser.add_argument("--window", type=Path, help="Path to a JSONL telemetry window.")
    if len(argv) == 0:
        parser.print_help()
        return 0
    args = parser.parse_args(argv)
    if args.window is None:
        parser.print_help()
        return 0
    window = _load_jsonl(args.window)
    result = analyze(window)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
