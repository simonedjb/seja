#!/usr/bin/env python3
"""reflect_stuck_loops — detect sessions where the same skill runs repeatedly on similar briefs.

Scans the telemetry window for sliding windows of 3+ consecutive invocations of
the same skill within ``WINDOW_MINUTES`` minutes, and flags those whose briefs
are textually similar (Jaccard >= ``SIMILARITY_THRESHOLD``). See plan-000295
Step 5 for the full specification.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


WINDOW_MINUTES = 30
SIMILARITY_THRESHOLD = 0.6
_MIN_LOOP_COUNT = 3
_BRIEF_TRUNCATE = 80

_PUNCT_RE = re.compile(r"[^\w\s]")


def _parse_ts(value: str | None) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        # Support the trailing-Z shape used by post-skill.
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None


def _tokenize(text: str) -> set[str]:
    if not text:
        return set()
    normalized = _PUNCT_RE.sub(" ", text.lower())
    return set(t for t in normalized.split() if t)


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = a & b
    union = a | b
    return len(inter) / len(union) if union else 0.0


def _load_briefs_map(briefs_path: Path | None) -> dict[str, str]:
    """Parse ``briefs.md`` and extract an id -> brief-text mapping.

    The file format is line-oriented; each line contains the invocation id
    and brief text separated by pipes. We do a lightweight regex scan and
    fall back to an empty dict if the file is unreadable.
    """
    mapping: dict[str, str] = {}
    if briefs_path is None or not briefs_path.is_file():
        return mapping
    try:
        text = briefs_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return mapping
    # Heuristic: find six-digit ids followed by any separator, then capture
    # the remainder of the line as the brief. The briefs.md file uses an
    # idiom like ``STARTED | <datetime> | <skill> | <id> | <brief>``. We
    # simply take the last ``|``-delimited segment after a 6-digit id.
    for line in text.splitlines():
        if "|" not in line:
            continue
        id_match = re.search(r"\b(\d{6})\b", line)
        if not id_match:
            continue
        tail = line.split("|")[-1].strip()
        if tail:
            # Keep the first occurrence per id (STARTED entry) if present.
            mapping.setdefault(id_match.group(1), tail)
    return mapping


def _brief_for(record: dict, briefs_map: dict[str, str]) -> str:
    b = record.get("brief")
    if isinstance(b, str) and b:
        return b
    rid = record.get("id")
    if isinstance(rid, str) and rid in briefs_map:
        return briefs_map[rid]
    return ""


def analyze(window: list[dict], briefs_map: dict[str, str] | None = None) -> dict:
    """Detect stuck-loop patterns in the telemetry window.

    Args:
        window: telemetry records. Should carry ``timestamp`` and ``skill``
            fields. If the records also carry ``brief``, it is used directly.
        briefs_map: optional id -> brief-text mapping, typically loaded from
            ``BRIEFS_FILE`` by the CLI wrapper.

    Returns:
        A dict with ``stuck_loops``, ``observations``, and ``degraded``.
    """
    empty: dict = {"stuck_loops": [], "observations": [], "degraded": False}
    if not window:
        return empty

    briefs_map = briefs_map or {}

    # Build a projection with parsed timestamps, skills, and briefs.
    projected: list[dict] = []
    for r in window:
        skill = r.get("skill")
        ts = _parse_ts(r.get("timestamp"))
        if not isinstance(skill, str) or ts is None:
            continue
        brief = _brief_for(r, briefs_map)
        projected.append(
            {
                "skill": skill,
                "ts": ts,
                "brief": brief,
                "tokens": _tokenize(brief),
                "id": r.get("id"),
            }
        )

    projected.sort(key=lambda x: x["ts"])

    # Degraded guard: all briefs empty across the projection.
    if projected and not any(p["brief"] for p in projected):
        return {
            **empty,
            "degraded": True,
            "reason": "briefs not loaded or missing",
        }

    # Walk consecutive same-skill runs and look for sliding 3+ windows
    # within the time cap.
    stuck_loops: list[dict] = []
    i = 0
    n = len(projected)
    while i < n:
        j = i
        while j + 1 < n and projected[j + 1]["skill"] == projected[i]["skill"]:
            j += 1
        run = projected[i : j + 1]
        if len(run) >= _MIN_LOOP_COUNT:
            # Find the longest qualifying segment inside this run: starting
            # at some index s, extend as far as possible while (a) the span
            # stays within WINDOW_MINUTES, (b) pairwise Jaccard similarity
            # of briefs stays >= SIMILARITY_THRESHOLD, and (c) size >= 3.
            best_segment: list[dict] | None = None
            best_min_sim: float = 0.0
            for s in range(len(run)):
                segment: list[dict] = [run[s]]
                for e in range(s + 1, len(run)):
                    candidate = segment + [run[e]]
                    span = (
                        candidate[-1]["ts"] - candidate[0]["ts"]
                    ).total_seconds()
                    if span > WINDOW_MINUTES * 60:
                        break
                    sims: list[float] = []
                    ok = True
                    for x in range(len(candidate)):
                        for y in range(x + 1, len(candidate)):
                            sim = _jaccard(
                                candidate[x]["tokens"], candidate[y]["tokens"]
                            )
                            if sim < SIMILARITY_THRESHOLD:
                                ok = False
                                break
                            sims.append(sim)
                        if not ok:
                            break
                    if not ok:
                        break
                    segment = candidate
                    if len(segment) >= _MIN_LOOP_COUNT:
                        min_sim = min(sims) if sims else 1.0
                        if best_segment is None or len(segment) > len(best_segment):
                            best_segment = list(segment)
                            best_min_sim = min_sim
            if best_segment is not None:
                span_minutes = round(
                    (best_segment[-1]["ts"] - best_segment[0]["ts"]).total_seconds()
                    / 60,
                    1,
                )
                stuck_loops.append(
                    {
                        "skill": best_segment[0]["skill"],
                        "count": len(best_segment),
                        "window_minutes": span_minutes,
                        "first_at": best_segment[0]["ts"].strftime(
                            "%Y-%m-%dT%H:%M:%SZ"
                        ),
                        "last_at": best_segment[-1]["ts"].strftime(
                            "%Y-%m-%dT%H:%M:%SZ"
                        ),
                        "briefs": [
                            (p["brief"][:_BRIEF_TRUNCATE]) for p in best_segment
                        ],
                        "min_similarity": round(best_min_sim, 4),
                    }
                )
        i = j + 1

    observations: list[str] = []
    for loop in stuck_loops:
        observations.append(
            f"I notice that you invoked `{loop['skill']}` {loop['count']} times "
            f"in about {loop['window_minutes']} minutes on very similar briefs. "
            f"Here is a question I am holding for you: what did you learn "
            f"between the first and the last invocation, and what might have "
            f"shortened that path?"
        )

    return {
        "stuck_loops": stuck_loops,
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
        description="Detect stuck-loop patterns in a telemetry window."
    )
    parser.add_argument("--window", type=Path, help="Path to a JSONL telemetry window.")
    parser.add_argument(
        "--briefs",
        type=Path,
        default=None,
        help="Optional path to briefs.md. Defaults to BRIEFS_FILE from conventions.",
    )
    if len(argv) == 0:
        parser.print_help()
        return 0
    args = parser.parse_args(argv)
    if args.window is None:
        parser.print_help()
        return 0

    briefs_path = args.briefs
    if briefs_path is None:
        try:
            import project_config  # type: ignore

            briefs_path = project_config.get_path("BRIEFS_FILE")
        except Exception:
            briefs_path = None

    briefs_map = _load_briefs_map(briefs_path)
    window = _load_jsonl(args.window)
    result = analyze(window, briefs_map)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
