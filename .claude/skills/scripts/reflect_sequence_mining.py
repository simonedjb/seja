#!/usr/bin/env python3
"""reflect_sequence_mining — first-order and second-order skill transition frequencies.

Analyzes a telemetry window to surface the most common skill-transition patterns:
pairs of consecutive skill invocations (first order) and triples (second order).
Produces ranked lists plus ready-to-embed observation sentences for the
`/reflect` report. See plan-000295 Step 5 for the full specification.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def _sort_window(window: list[dict]) -> list[dict]:
    """Return the window sorted by timestamp ascending. Records without a
    timestamp sort to the end."""
    return sorted(window, key=lambda r: (r.get("timestamp") is None, r.get("timestamp") or ""))


def _extract_skills(window: list[dict]) -> list[str]:
    """Pull the skill name out of every record, filtering out records with
    no `skill` field (e.g., malformed reflection-outcome stubs)."""
    return [r["skill"] for r in window if isinstance(r.get("skill"), str)]


def analyze(window: list[dict]) -> dict:
    """Compute first-order and second-order skill transition frequencies.

    Args:
        window: list of telemetry records (dicts, JSON-parsed).

    Returns:
        A dict with keys ``sequences``, ``top_5_first_order``, ``top_5_second_order``,
        ``observations``, and ``degraded``. See the module docstring and plan-000295
        Step 5 for the exact shape.
    """
    empty: dict = {
        "sequences": [],
        "top_5_first_order": [],
        "top_5_second_order": [],
        "observations": [],
        "degraded": False,
    }
    if not window or len(window) < 2:
        return {
            **empty,
            "degraded": True,
            "reason": "insufficient records for sequence analysis",
        }

    sorted_window = _sort_window(window)
    skills = _extract_skills(sorted_window)
    if len(skills) < 2:
        return {
            **empty,
            "degraded": True,
            "reason": "insufficient records for sequence analysis",
        }

    first_pairs = [(skills[i], skills[i + 1]) for i in range(len(skills) - 1)]
    second_triples = [
        (skills[i], skills[i + 1], skills[i + 2]) for i in range(len(skills) - 2)
    ]

    first_counts = Counter(first_pairs)
    second_counts = Counter(second_triples)
    total_first = len(first_pairs)
    total_second = len(second_triples)

    def _entry(pattern_tuple: tuple, count: int, total: int, order: int) -> dict:
        return {
            "pattern": list(pattern_tuple),
            "order": order,
            "count": count,
            "fraction": round(count / total, 4) if total else 0.0,
        }

    def _top_entry(pattern_tuple: tuple, count: int, total: int) -> dict:
        return {
            "pattern": list(pattern_tuple),
            "count": count,
            "fraction": round(count / total, 4) if total else 0.0,
        }

    sequences: list[dict] = []
    for pattern, count in first_counts.most_common():
        sequences.append(_entry(pattern, count, total_first, 1))
    for pattern, count in second_counts.most_common():
        sequences.append(_entry(pattern, count, total_second, 2))

    top_5_first = [
        _top_entry(p, c, total_first) for p, c in first_counts.most_common(5)
    ]
    top_5_second = [
        _top_entry(p, c, total_second) for p, c in second_counts.most_common(5)
    ]

    # Observations — noise floor at count >= 3. Use the first-order top hit
    # and the strongest second-order pattern if available.
    observations: list[str] = []
    for pattern, count in first_counts.most_common():
        if count < 3:
            break
        prev_skill, next_skill = pattern
        observations.append(
            f"I notice that after `{prev_skill}`, you most often invoke "
            f"`{next_skill}` ({count} of {total_first} times). "
            f"Here is a question I am holding for you: what does `{next_skill}` "
            f"give you that the natural next step for `{prev_skill}` in the "
            f"skill-graph would not?"
        )
    for pattern, count in second_counts.most_common():
        if count < 3:
            break
        a, b, c = pattern
        observations.append(
            f"I notice the triple `{a}` -> `{b}` -> `{c}` recurred {count} times "
            f"out of {total_second} possible triples. "
            f"Here is a question I am holding for you: is this a healthy rhythm, "
            f"or a loop you would like to break?"
        )

    return {
        "sequences": sequences,
        "top_5_first_order": top_5_first,
        "top_5_second_order": top_5_second,
        "observations": observations,
        "degraded": False,
    }


def _load_window(path: Path) -> list[dict]:
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
        description="Run sequence mining over a telemetry window."
    )
    parser.add_argument("--window", type=Path, help="Path to a JSONL telemetry window.")
    if len(argv) == 0:
        parser.print_help()
        return 0
    args = parser.parse_args(argv)
    if args.window is None:
        parser.print_help()
        return 0
    window = _load_window(args.window)
    result = analyze(window)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
