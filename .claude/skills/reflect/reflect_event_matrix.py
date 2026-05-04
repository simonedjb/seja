#!/usr/bin/env python3
# designer: When /reflect --deep renders a timeline of what happened and when,
#   I'm the event matrix builder that lays every skill invocation on a temporal
#   axis with width proportional to duration, packing up to three lanes per
#   skill so overlapping sessions stay visible instead of hiding behind each
#   other -- producing a Vega-Lite spec, a static SVG, and a self-contained
#   HTML page that all share the same Viridis color language.
"""reflect_event_matrix -- Vega-Lite event matrix for /reflect --deep.

Invocation: script-invoked, user-cli
Lifecycle: active

Takes a filtered telemetry window (list of dicts) and produces three output
files: a Vega-Lite v5 JSON spec (.vl.json), a static SVG rendering (.svg via
vl2svg CLI if available), and a self-contained interactive HTML page (.html)
with CDN-loaded Vega libraries.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

from reflect_colors import COLOR_DOMAIN, COLOR_RANGE, SKILL_ORDER, color_key


# ---------------------------------------------------------------------------
# Mode extraction
# ---------------------------------------------------------------------------

_MODE_FLAGS = ("--deep", "--inventory", "--roadmap", "--light")


def extract_mode(brief: str) -> str:
    """Detect a mode flag substring inside the brief text.

    Returns the first matching flag (e.g. ``--deep``) or ``"default"`` when
    no flag is found.
    """
    if not brief:
        return "default"
    for flag in _MODE_FLAGS:
        if flag in brief:
            return flag
    return "default"


# ---------------------------------------------------------------------------
# Duration helpers
# ---------------------------------------------------------------------------

_DEFAULT_DURATION_MIN = 5.0

# Gap compression: gaps wider than this threshold are collapsed to a stub.
_GAP_THRESHOLD_HOURS: float = 24.0
# Compressed-axis width (minutes) assigned to each collapsed gap.
_GAP_PLACEHOLDER_MIN: float = 120.0


def duration_minutes(record: dict) -> float:
    """Return the duration of a telemetry record in minutes.

    Falls back to a 5-minute default when the field is absent or zero.
    """
    raw = record.get("duration_seconds")
    if raw is None or raw == 0:
        return _DEFAULT_DURATION_MIN
    try:
        val = float(raw)
    except (TypeError, ValueError):
        return _DEFAULT_DURATION_MIN
    return val / 60.0 if val > 0 else _DEFAULT_DURATION_MIN


# ---------------------------------------------------------------------------
# Lane packing
# ---------------------------------------------------------------------------

_MAX_LANES = 3


def assign_lanes(events: list[dict]) -> list[dict]:
    """Assign a ``lane`` key (0, 1, or 2) to each event dict.

    Events are grouped by skill name. Within each group they are sorted by
    start time and greedily packed into the lowest available lane where the
    new event's start is >= every existing event's end in that lane. If all
    three lanes overlap the event is placed in lane 0 (stacking).

    Returns a new list with the ``lane`` key added to each dict. The
    original dicts are mutated in place for simplicity (callers build them
    fresh for this function).
    """
    groups: dict[str, list[dict]] = {}
    for ev in events:
        groups.setdefault(ev["skill"], []).append(ev)

    for group in groups.values():
        group.sort(key=lambda e: e["start"])
        lane_ends: list[list[str]] = [[] for _ in range(_MAX_LANES)]
        for ev in group:
            placed = False
            for lane_idx in range(_MAX_LANES):
                if all(ev["start"] >= end for end in lane_ends[lane_idx]):
                    ev["lane"] = lane_idx
                    lane_ends[lane_idx].append(ev["end"])
                    placed = True
                    break
            if not placed:
                ev["lane"] = 0
                lane_ends[0].append(ev["end"])

    return events


# ---------------------------------------------------------------------------
# Gap detection and timeline compression
# ---------------------------------------------------------------------------

def _find_gaps(events: list[dict]) -> list[dict]:
    """Return gaps > _GAP_THRESHOLD_HOURS between consecutive event end→start pairs.

    Events must already be sorted by ``start``.  Each returned dict has:
    ``real_start`` (datetime – prior event's end),
    ``real_end``   (datetime – next event's start),
    ``gap_hours``  (float).
    """
    gaps: list[dict] = []
    for i in range(len(events) - 1):
        cur_end = datetime.fromisoformat(events[i]["end"])
        nxt_start = datetime.fromisoformat(events[i + 1]["start"])
        gap_h = (nxt_start - cur_end).total_seconds() / 3600
        if gap_h > _GAP_THRESHOLD_HOURS:
            if not gaps or gaps[-1]["real_end"] != nxt_start:
                gaps.append({
                    "real_start": cur_end,
                    "real_end": nxt_start,
                    "gap_hours": gap_h,
                })
    return gaps


def _compress_timeline(
    events: list[dict],
) -> tuple[list[dict], list[dict], list[dict]]:
    """Compress the timeline by collapsing gaps > _GAP_THRESHOLD_HOURS.

    Adds ``cx_start`` and ``cx_end`` (compressed minutes from window start) to
    every event dict in place.

    Returns:
        events        – same list, augmented with ``cx_start`` / ``cx_end``.
        gap_lines     – ``[{cx_pos, gap_hours, gap_label}, ...]`` (empty if no gaps).
        session_labels – ``[{cx_pos, label}, ...]`` one entry per session.
    """
    if not events:
        return events, [], []

    sorted_evs = sorted(events, key=lambda e: e["start"])
    gaps = _find_gaps(sorted_evs)
    window_start = datetime.fromisoformat(sorted_evs[0]["start"])

    def _real_min(dt: datetime) -> float:
        return (dt - window_start).total_seconds() / 60.0

    def _saving_before(dt: datetime) -> float:
        """Cumulative minutes removed by all gaps whose end precedes dt."""
        total = 0.0
        for g in gaps:
            if g["real_end"] <= dt:
                gap_min = (g["real_end"] - g["real_start"]).total_seconds() / 60.0
                total += gap_min - _GAP_PLACEHOLDER_MIN
        return total

    for ev in sorted_evs:
        start_dt = datetime.fromisoformat(ev["start"])
        end_dt = datetime.fromisoformat(ev["end"])
        saving = _saving_before(start_dt)
        ev["cx_start"] = _real_min(start_dt) - saving
        ev["cx_end"] = ev["cx_start"] + (end_dt - start_dt).total_seconds() / 60.0

    if not gaps:
        session_labels = [{"cx_pos": 0.0, "label": window_start.strftime("%Y-%m-%d")}]
        return events, [], session_labels

    gap_lines: list[dict] = []
    for g in gaps:
        cx = _real_min(g["real_start"]) - _saving_before(g["real_start"])
        gh = g["gap_hours"]
        days, hrs = int(gh // 24), round(gh % 24)
        if days and hrs:
            label = f"{days}d {hrs}h"
        elif days:
            label = f"{days}d"
        else:
            label = f"{hrs}h"
        gap_lines.append({"cx_pos": cx, "gap_hours": gh, "gap_label": label})

    session_starts = [window_start] + [g["real_end"] for g in gaps]
    session_labels = [
        {"cx_pos": _real_min(ss) - _saving_before(ss), "label": ss.strftime("%Y-%m-%d")}
        for ss in session_starts
    ]

    return events, gap_lines, session_labels


# ---------------------------------------------------------------------------
# Build enriched event list
# ---------------------------------------------------------------------------

def build_events(window: list[dict]) -> list[dict]:
    """Transform raw telemetry records into enriched event dicts.

    Each output dict has: skill, mode, color_key, start (ISO), end (ISO),
    duration_min, id, brief.
    """
    events: list[dict] = []
    for rec in window:
        skill = rec.get("skill", "pending")
        if not isinstance(skill, str):
            skill = "pending"
        brief = rec.get("brief", "")
        mode = extract_mode(brief)
        ts = rec.get("timestamp")
        if not ts:
            continue
        dur = duration_minutes(rec)
        try:
            start_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            continue
        end_dt = start_dt + timedelta(minutes=dur)
        events.append({
            "skill": skill,
            "mode": mode,
            "color_key": color_key(skill, mode),
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat(),
            "duration_min": round(dur, 1),
            "id": rec.get("id", ""),
            "brief": brief,
        })
    return events


# ---------------------------------------------------------------------------
# Vega-Lite spec construction
# ---------------------------------------------------------------------------

def build_vegalite_spec(
    events: list[dict],
    title_scope: str,
    date_range: tuple[str, str],
) -> dict:
    """Construct a Vega-Lite v5 JSON spec for the event matrix."""
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": f"Event Matrix -- {title_scope} ({date_range[0]} to {date_range[1]})",
        "width": 800,
        "height": 300,
        "data": {"values": events},
        "mark": {"type": "bar", "cornerRadiusEnd": 2},
        "encoding": {
            "x": {
                "field": "start",
                "type": "temporal",
                "title": "Time",
            },
            "x2": {"field": "end"},
            "y": {
                "field": "skill",
                "type": "nominal",
                "title": "Skill",
                "sort": SKILL_ORDER,
            },
            "yOffset": {
                "field": "lane",
                "type": "ordinal",
            },
            "color": {
                "field": "color_key",
                "type": "nominal",
                "title": "Skill / Mode",
                "scale": {
                    "domain": COLOR_DOMAIN,
                    "range": COLOR_RANGE,
                },
                "legend": {"title": "Skill / Mode"},
            },
            "tooltip": [
                {"field": "start", "type": "temporal", "title": "Start"},
                {"field": "end", "type": "temporal", "title": "End"},
                {"field": "skill", "type": "nominal", "title": "Skill"},
                {"field": "mode", "type": "nominal", "title": "Mode"},
                {"field": "duration_min", "type": "quantitative", "title": "Duration (min)"},
                {"field": "id", "type": "nominal", "title": "ID"},
                {"field": "brief", "type": "nominal", "title": "Brief"},
            ],
        },
    }


def _build_vegalite_spec_gapped(
    events: list[dict],
    gap_lines: list[dict],
    session_labels: list[dict],
    title_scope: str,
    date_range: tuple[str, str],
) -> dict:
    """Layered Vega-Lite spec with compressed x-axis and gap indicators.

    Uses a quantitative ``cx_start``/``cx_end`` axis (compressed minutes from
    the window start) instead of a temporal one.

    Session dates are rendered via ``axis.values`` + ``axis.labelExpr`` so they
    appear in the normal axis-label row below the chart rather than floating
    over the bars.  Labels for sessions narrower than 60 compressed minutes are
    suppressed to prevent them spilling into adjacent session areas.

    Gap duration labels float above the chart in a dedicated 20 px top-padding
    strip, centred on the dashed rule, using ``clip: false`` so they are not
    clipped to the plot area.
    """
    # Suppress date labels for sessions that are too narrow to label cleanly.
    _MIN_LABEL_WIDTH_MIN = 60.0
    max_cx = max((ev["cx_end"] for ev in events), default=0.0)
    visible_labels = []
    for i, sl in enumerate(session_labels):
        session_end = gap_lines[i]["cx_pos"] if i < len(gap_lines) else max_cx
        if session_end - sl["cx_pos"] >= _MIN_LABEL_WIDTH_MIN:
            visible_labels.append(sl)

    # Build axis.labelExpr as a nested ternary — Vega expressions do not support
    # object literal syntax {}, so a dict lookup would silently fail to compile.
    axis_tick_values = [round(sl["cx_pos"]) for sl in visible_labels]
    if visible_labels:
        parts = " : ".join(
            f"datum.value == {round(sl['cx_pos'])} ? '{sl['label']}'"
            for sl in visible_labels
        )
        label_expr = parts + " : ''"
    else:
        label_expr = "''"

    bars_layer: dict = {
        "data": {"values": events},
        "mark": {"type": "bar", "cornerRadiusEnd": 2},
        "encoding": {
            "x": {
                "field": "cx_start",
                "type": "quantitative",
                "scale": {"nice": False, "padding": 8},
                "axis": {
                    "title": None,
                    "values": axis_tick_values,
                    "labelExpr": label_expr,
                    "ticks": False,
                    "domain": False,
                    "grid": False,
                    "labelFontSize": 9,
                    "labelColor": "#555555",
                    "labelAlign": "left",
                },
            },
            "x2": {"field": "cx_end"},
            "y": {
                "field": "skill",
                "type": "nominal",
                "title": "Skill",
                "sort": SKILL_ORDER,
            },
            "yOffset": {"field": "lane", "type": "ordinal"},
            "color": {
                "field": "color_key",
                "type": "nominal",
                "title": "Skill / Mode",
                "scale": {"domain": COLOR_DOMAIN, "range": COLOR_RANGE},
                "legend": {"title": "Skill / Mode"},
            },
            "tooltip": [
                {"field": "start", "type": "temporal", "title": "Start"},
                {"field": "end", "type": "temporal", "title": "End"},
                {"field": "skill", "type": "nominal", "title": "Skill"},
                {"field": "mode", "type": "nominal", "title": "Mode"},
                {"field": "duration_min", "type": "quantitative", "title": "Duration (min)"},
                {"field": "id", "type": "nominal", "title": "ID"},
                {"field": "brief", "type": "nominal", "title": "Brief"},
            ],
        },
    }

    gap_rules_layer: dict = {
        "data": {"values": gap_lines},
        "mark": {
            "type": "rule",
            "stroke": "#aaaaaa",
            "strokeDash": [5, 4],
            "strokeWidth": 1.5,
        },
        "encoding": {
            "x": {"field": "cx_pos", "type": "quantitative"},
            "tooltip": [
                {"field": "gap_label", "type": "nominal", "title": "Gap"},
                {"field": "gap_hours", "type": "quantitative", "title": "Hours"},
            ],
        },
    }

    # Gap duration labels float above the plot area in the top-padding strip.
    # clip: false allows text to render outside the plot bounds.
    gap_text_layer: dict = {
        "data": {"values": gap_lines},
        "mark": {
            "type": "text",
            "clip": False,
            "angle": 0,
            "align": "center",
            "baseline": "bottom",
            "fontSize": 9,
            "fill": "#aaaaaa",
        },
        "encoding": {
            "x": {"field": "cx_pos", "type": "quantitative"},
            "text": {"field": "gap_label", "type": "nominal"},
            "y": {"value": -4},
        },
    }

    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": f"Event Matrix -- {title_scope} ({date_range[0]} to {date_range[1]})",
        "padding": {"top": 20, "right": 5, "bottom": 5, "left": 5},
        "width": 800,
        "height": 300,
        "layer": [bars_layer, gap_rules_layer, gap_text_layer],
    }


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

def write_vl_json(spec: dict, path: Path) -> Path:
    """Write the Vega-Lite spec to a ``.vl.json`` file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(spec, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def render_svg(vl_json_path: Path, svg_path: Path) -> Path | None:
    """Attempt to render SVG via the ``vl2svg`` CLI tool.

    Returns the SVG path on success, or ``None`` with a warning on failure.
    """
    try:
        result = subprocess.run(
            ["vl2svg", str(vl_json_path), str(svg_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and svg_path.exists():
            return svg_path
        print(f"WARNING: vl2svg exited with code {result.returncode}", file=sys.stderr)
        if result.stderr:
            print(f"  {result.stderr.strip()}", file=sys.stderr)
        return None
    except FileNotFoundError:
        print("WARNING: vl2svg not found -- skipping SVG generation", file=sys.stderr)
        return None
    except subprocess.TimeoutExpired:
        print("WARNING: vl2svg timed out -- skipping SVG generation", file=sys.stderr)
        return None


_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
<style>body {{ font-family: sans-serif; margin: 2rem; }}</style>
</head>
<body>
<div id="vis"></div>
<script>
  var spec = {spec_json};
  vegaEmbed("#vis", spec, {{mode: "vega-lite"}}).catch(console.error);
</script>
</body>
</html>
"""


def _escape_html(text: str) -> str:
    """Minimal HTML escaping for safe insertion into HTML content."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def write_html(spec: dict, path: Path, title: str) -> Path:
    """Write a self-contained HTML page with the Vega-Lite spec inlined."""
    path.parent.mkdir(parents=True, exist_ok=True)
    html = _HTML_TEMPLATE.format(
        spec_json=json.dumps(spec, indent=2, ensure_ascii=False),
    )
    path.write_text(html, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Public programmatic interface
# ---------------------------------------------------------------------------

def generate(
    window: list[dict],
    output_prefix: Path,
    title_scope: str,
    date_range: tuple[datetime, datetime],
) -> dict[str, Path | None]:
    """Generate all event matrix output files.

    Parameters
    ----------
    window:
        List of telemetry record dicts.
    output_prefix:
        Path prefix without extension (e.g. ``reflections/reflection-42-event-matrix``).
    title_scope:
        Human-readable scope label for the chart title.
    date_range:
        Start and end datetimes for the chart title.

    Returns
    -------
    dict with keys ``vl_json``, ``svg`` (may be None), ``html``.
    """
    events = build_events(window)
    events.sort(key=lambda e: e["start"])

    events, gap_lines, session_labels = _compress_timeline(events)
    events = assign_lanes(events)

    dr_strs = (
        date_range[0].strftime("%Y-%m-%d"),
        date_range[1].strftime("%Y-%m-%d"),
    )

    if gap_lines:
        spec = _build_vegalite_spec_gapped(
            events, gap_lines, session_labels, title_scope, dr_strs
        )
    else:
        spec = build_vegalite_spec(events, title_scope, dr_strs)

    vl_path = Path(str(output_prefix) + ".vl.json")
    svg_path = Path(str(output_prefix) + ".svg")
    html_path = Path(str(output_prefix) + ".html")

    write_vl_json(spec, vl_path)
    svg_result = render_svg(vl_path, svg_path)
    write_html(spec, html_path, title_scope)

    return {
        "vl_json": vl_path,
        "svg": svg_result,
        "html": html_path,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point for CLI invocation."""
    parser = argparse.ArgumentParser(
        description="Generate event matrix visualization from a telemetry window.",
    )
    parser.add_argument(
        "--input",
        default="-",
        help="Path to a JSON file with the telemetry window, or '-' for stdin.",
    )
    parser.add_argument(
        "--output-prefix",
        required=True,
        help="Output path prefix without extension (e.g. 'out/event-matrix').",
    )
    parser.add_argument(
        "--scope",
        default="all",
        help="Human-readable scope label for the chart title.",
    )
    parser.add_argument(
        "--date-range",
        required=True,
        help="Comma-separated ISO date pair: <start>,<end>.",
    )
    args = parser.parse_args()

    # Reconfigure stdout for UTF-8 on Windows
    sys.stdout.reconfigure(encoding="utf-8")

    # Read input
    if args.input == "-":
        window = json.load(sys.stdin)
    else:
        with open(args.input, encoding="utf-8") as f:
            window = json.load(f)

    # Parse date range
    parts = args.date_range.split(",", 1)
    if len(parts) != 2:
        print("ERROR: --date-range must be <start>,<end>", file=sys.stderr)
        sys.exit(1)
    dr_start = datetime.fromisoformat(parts[0].strip())
    dr_end = datetime.fromisoformat(parts[1].strip())

    result = generate(
        window=window,
        output_prefix=Path(args.output_prefix),
        title_scope=args.scope,
        date_range=(dr_start, dr_end),
    )

    summary = {
        "vl_json": str(result["vl_json"]),
        "svg": str(result["svg"]) if result["svg"] else None,
        "html": str(result["html"]),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
