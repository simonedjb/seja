#!/usr/bin/env python3
"""reflect_decision_reversals — surface accepted decisions that were later undone.

Walks the telemetry window for ``decision_points[*]`` entries that represent
acceptances, then matches them against later records that reversed the effect
(either by ``qa_type`` signal or by a textual negating option). Depends on
Plan B's ``decision_points`` field being populated. See plan-000295 Step 5
for the full specification.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


_REJECT_MARKERS = ("reject", "none of these", "defer", "cancel")
_NEGATION_PREFIXES = ("no", "don't", "do not", "revert", "undo")
_MAX_REVERSALS = 10


def _is_accept(chosen: str) -> bool:
    if not isinstance(chosen, str):
        return False
    lowered = chosen.strip().lower()
    if not lowered:
        return False
    return not any(marker in lowered for marker in _REJECT_MARKERS)


def _starts_with_negation(text: str) -> bool:
    if not isinstance(text, str):
        return False
    lowered = text.strip().lower()
    return any(
        lowered == prefix or lowered.startswith(prefix + " ")
        for prefix in _NEGATION_PREFIXES
    )


def _artifact_label(record: dict) -> str:
    """Return a short label (e.g., ``plan-000271``) for a record if possible."""
    skill = record.get("skill") or "skill"
    rid = record.get("id") or "unknown"
    return f"{skill}-{rid}"


def _sort_window(window: list[dict]) -> list[dict]:
    return sorted(window, key=lambda r: (r.get("timestamp") is None, r.get("timestamp") or ""))


def analyze(window: list[dict]) -> dict:
    """Detect accepted-then-reversed decisions inside the window.

    Args:
        window: telemetry records sorted by timestamp ascending (will be sorted
            if not already).

    Returns:
        A dict with ``reversals``, ``observations``, and ``degraded``.
    """
    empty: dict = {"reversals": [], "observations": [], "degraded": False}
    if not window:
        return empty

    # Degraded guard: every record has null or empty decision_points.
    def _has_dp(r: dict) -> bool:
        dp = r.get("decision_points")
        return isinstance(dp, list) and len(dp) > 0

    if not any(_has_dp(r) for r in window):
        return {
            **empty,
            "degraded": True,
            "reason": (
                "decision_points field not populated; requires Plan B "
                "rationale payloads to be captured first"
            ),
        }

    sorted_window = _sort_window(window)

    # Build the list of accept events, each with the index of its source record.
    accepts: list[dict] = []
    for idx, r in enumerate(sorted_window):
        dp = r.get("decision_points")
        if not isinstance(dp, list):
            continue
        for entry in dp:
            if not isinstance(entry, dict):
                continue
            chosen = entry.get("chosen_option")
            prompt = entry.get("prompt")
            if not isinstance(chosen, str) or not isinstance(prompt, str):
                continue
            if _is_accept(chosen):
                accepts.append(
                    {
                        "record_index": idx,
                        "accepted_at": r.get("timestamp"),
                        "skill": r.get("skill"),
                        "id": r.get("id"),
                        "prompt": prompt,
                        "chosen_option": chosen,
                        "record": r,
                    }
                )

    reversals: list[dict] = []
    used_reversal_keys: set[tuple[int, str]] = set()

    for accept in accepts:
        acc_idx = accept["record_index"]
        acc_prompt_lower = accept["prompt"].strip().lower()
        acc_chosen_lower = accept["chosen_option"].strip().lower()
        matched = None
        for later_idx in range(acc_idx + 1, len(sorted_window)):
            later = sorted_window[later_idx]
            # Signal 1: qa_type indicates a decision revise/reject.
            qa_type = later.get("qa_type")
            later_dp = later.get("decision_points") if isinstance(later.get("decision_points"), list) else []
            if qa_type in {"decision-point-revise", "decision-point-reject"}:
                # Require fuzzy textual link through any decision_points prompt.
                for entry in later_dp:
                    if not isinstance(entry, dict):
                        continue
                    later_prompt = entry.get("prompt", "")
                    later_chosen = entry.get("chosen_option", "")
                    if not isinstance(later_prompt, str) or not isinstance(later_chosen, str):
                        continue
                    if (
                        acc_chosen_lower
                        and acc_chosen_lower in later_prompt.lower()
                    ) or (acc_prompt_lower and acc_prompt_lower in later_prompt.lower()):
                        key = (later_idx, later_chosen)
                        if key in used_reversal_keys:
                            continue
                        matched = {
                            "reversed_by": later_chosen or qa_type,
                            "reversed_at": later.get("timestamp"),
                            "reversed_in": _artifact_label(later),
                            "_key": key,
                        }
                        break
                if matched:
                    break

            # Signal 2: later decision_points entry whose prompt mentions the
            # earlier chosen_option AND whose chosen_option begins with a
            # negation word.
            for entry in later_dp:
                if not isinstance(entry, dict):
                    continue
                later_prompt = entry.get("prompt", "")
                later_chosen = entry.get("chosen_option", "")
                if not isinstance(later_prompt, str) or not isinstance(later_chosen, str):
                    continue
                if (
                    acc_chosen_lower
                    and acc_chosen_lower in later_prompt.lower()
                    and _starts_with_negation(later_chosen)
                ):
                    key = (later_idx, later_chosen)
                    if key in used_reversal_keys:
                        continue
                    matched = {
                        "reversed_by": later_chosen,
                        "reversed_at": later.get("timestamp"),
                        "reversed_in": _artifact_label(later),
                        "_key": key,
                    }
                    break
            if matched:
                break

        if matched:
            used_reversal_keys.add(matched.pop("_key"))
            reversals.append(
                {
                    "decision": accept["chosen_option"],
                    "accepted_at": accept["accepted_at"],
                    "accepted_in": _artifact_label(accept["record"]),
                    "reversed_by": matched["reversed_by"],
                    "reversed_at": matched["reversed_at"],
                    "reversed_in": matched["reversed_in"],
                }
            )

    # Sort by accepted_at descending and cap at _MAX_REVERSALS.
    reversals.sort(key=lambda r: r.get("accepted_at") or "", reverse=True)
    reversals = reversals[:_MAX_REVERSALS]

    observations: list[str] = []
    for rev in reversals:
        acc_date = (rev["accepted_at"] or "")[:10]
        rev_date = (rev["reversed_at"] or "")[:10]
        observations.append(
            f"I notice that you accepted `{rev['decision']}` on {acc_date}, "
            f"and then `{rev['reversed_by']}` on {rev_date} undid it. "
            f"Here is a question I am holding for you: what changed between "
            f"those two moments?"
        )

    return {
        "reversals": reversals,
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
        description="Surface decision reversals across a telemetry window."
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
