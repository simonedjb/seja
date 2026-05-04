#!/usr/bin/env python3
# designer: When /reflect --deep maps out how you actually move between skills,
#   I'm the renderer that turns that movement into a directed graph -- nodes
#   sized by how often you invoked each skill, edges weighted by how often one
#   skill followed another, all painted with the shared Viridis palette. You
#   get a DOT source for Graphviz, a static SVG if the `dot` binary is around,
#   and a self-contained interactive HTML page powered by Cytoscape.js --
#   drag nodes, zoom, pan, and hover for details, no server required.
"""reflect_transition_graph -- directed skill-transition graph visualization.

Invocation: script-invoked, user-cli
Lifecycle: active

Reads a filtered telemetry window (JSON list of records) and produces:
  - a Graphviz DOT source file (.dot)
  - a static SVG rendered via the ``dot`` binary, if available (.svg)
  - a self-contained interactive HTML page powered by Cytoscape.js (.html)

Nodes represent skills, sized by invocation count. Edges represent consecutive
skill transitions, weighted and colored by transition frequency. Self-loops are
included.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from reflect_colors import LIGHT_FILL_SKILLS, SKILL_COLORS

_FALLBACK_COLOR = "#999999"

# Node sizing constants (rounded-rectangle layout).
# Approximate width of one character at 11 px system-ui (sans-serif).
_CHAR_WIDTH_PX: float = 6.5
# Horizontal padding inside the node (left + right combined).
_LABEL_PAD_H: int = 20
# Line height at 11 px font (11 × 1.36 ≈ 15).
_LINE_HEIGHT_PX: int = 15
# Vertical padding inside the node (top + bottom combined).
_LABEL_PAD_V: int = 16
# Width of the most-frequent node; all others scale down proportionally.
_MAX_NODE_WIDTH: int = 180


def _sort_window(window: list[dict]) -> list[dict]:
    """Return the window sorted by timestamp ascending. Records without a
    timestamp sort to the end."""
    return sorted(
        window,
        key=lambda r: (r.get("timestamp") is None, r.get("timestamp") or ""),
    )


def _extract_skills(window: list[dict]) -> list[str]:
    """Pull the skill name from every record that has one."""
    return [r["skill"] for r in window if isinstance(r.get("skill"), str)]


def _node_color(skill: str) -> str:
    """Return the fill color for a skill node."""
    return SKILL_COLORS.get(skill, _FALLBACK_COLOR)


def _font_color(skill: str) -> str:
    """White text by default; dark text for light-fill skills."""
    if skill in LIGHT_FILL_SKILLS:
        return "#333333"
    return "#FFFFFF"


def _escape_dot(text: str) -> str:
    """Escape a string for safe use inside DOT double-quoted labels."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _build_dot(
    skill_counts: Counter,
    pair_counts: Counter,
    title: str,
) -> str:
    """Build a Graphviz DOT string from skill and pair counters."""
    max_count = max(skill_counts.values()) if skill_counts else 1
    max_transitions = max(pair_counts.values()) if pair_counts else 1

    lines: list[str] = []
    lines.append("digraph transitions {")
    lines.append('    rankdir=LR;')
    lines.append('    bgcolor="#FAFAFA";')
    lines.append(f'    label="{_escape_dot(title)}";')
    lines.append('    labelloc=t;')
    lines.append('    fontsize=14;')
    lines.append("")

    # Nodes
    for skill, count in skill_counts.most_common():
        width = max(0.3, count / max_count * 1.6)
        fill = _node_color(skill)
        font = _font_color(skill)
        label = f"{_escape_dot(skill)}\\n({count})"
        lines.append(
            f'    "{_escape_dot(skill)}" '
            f'[shape=circle, style=filled, fillcolor="{fill}", '
            f'fontcolor="{font}", width={width:.2f}, '
            f'label="{label}", fixedsize=true];'
        )

    lines.append("")

    # Edges
    for (src, tgt), count in pair_counts.most_common():
        penwidth = max(0.5, count / max_transitions * 3.5)
        color = SKILL_COLORS.get(tgt, _FALLBACK_COLOR)
        lines.append(
            f'    "{_escape_dot(src)}" -> "{_escape_dot(tgt)}" '
            f'[penwidth={penwidth:.2f}, color="{color}", '
            f'label="{count}"];'
        )

    lines.append("}")
    return "\n".join(lines)


def _write_dot(dot_source: str, path: Path) -> None:
    """Write the DOT source to a file."""
    path.write_text(dot_source, encoding="utf-8")


def _render_svg(dot_source: str, path: Path) -> Path | None:
    """Attempt to render SVG via the ``dot`` binary. Returns the output path
    on success, or ``None`` if Graphviz is not installed."""
    try:
        result = subprocess.run(
            ["dot", "-Tsvg"],
            input=dot_source,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        print(
            "WARNING: Graphviz `dot` binary not found; skipping SVG generation.",
            file=sys.stderr,
        )
        return None
    except subprocess.TimeoutExpired:
        print(
            "WARNING: Graphviz `dot` timed out; skipping SVG generation.",
            file=sys.stderr,
        )
        return None

    if result.returncode != 0:
        print(
            f"WARNING: `dot` exited with code {result.returncode}; "
            f"skipping SVG generation. stderr: {result.stderr[:200]}",
            file=sys.stderr,
        )
        return None

    path.write_text(result.stdout, encoding="utf-8")
    return path


def _label_min_width(skill: str, count: int) -> int:
    """Return the minimum node width (px) that fits this node's two-line label.

    Both label lines are measured -- the skill name and the count string --
    and the wider one drives the result.
    """
    max_line = max(len(skill), len(f"({count})"))
    return max(60, round(max_line * _CHAR_WIDTH_PX + _LABEL_PAD_H))


def _node_height() -> int:
    """Return the fixed node height (px) for two lines of label text."""
    return 2 * _LINE_HEIGHT_PX + _LABEL_PAD_V


def _build_cytoscape_elements(
    skill_counts: Counter,
    pair_counts: Counter,
) -> dict:
    """Serialise graph data into a Cytoscape elements dict."""
    max_count = max(skill_counts.values()) if skill_counts else 1
    max_transitions = max(pair_counts.values()) if pair_counts else 1

    node_h = _node_height()

    nodes = []
    for skill, count in skill_counts.most_common():
        label_min = _label_min_width(skill, count)
        scaled = round(count / max_count * _MAX_NODE_WIDTH)
        nodes.append({
            "data": {
                "id": skill,
                "label": f"{skill}\n({count})",
                "color": SKILL_COLORS.get(skill, _FALLBACK_COLOR),
                "fontColor": "#333333" if skill in LIGHT_FILL_SKILLS else "#ffffff",
                "nodeWidth": max(label_min, scaled),
                "nodeHeight": node_h,
                "count": count,
            }
        })

    # Enforce monotonicity: a node with more invocations must be at least as
    # wide as any node with fewer invocations, regardless of label length.
    # Sort ascending by count (stable id tiebreak for determinism), then sweep
    # a running maximum so each node inherits the floor set by lower-count nodes.
    nodes.sort(key=lambda n: (n["data"]["count"], n["data"]["id"]))
    running_max = 0
    for node in nodes:
        node["data"]["nodeWidth"] = max(node["data"]["nodeWidth"], running_max)
        running_max = node["data"]["nodeWidth"]

    edges = []
    for (src, tgt), count in pair_counts.most_common():
        width = max(1.0, round(count / max_transitions * 8, 1))
        edges.append({
            "data": {
                "id": f"{src}--{tgt}",
                "source": src,
                "target": tgt,
                "label": str(count),
                "width": width,
                "color": SKILL_COLORS.get(tgt, _FALLBACK_COLOR),
                "isSelfLoop": src == tgt,
                "count": count,
            }
        })

    return {"nodes": nodes, "edges": edges}


def _build_html(
    skill_counts: Counter,
    pair_counts: Counter,
    title: str,
) -> str:
    """Build a self-contained interactive HTML page using Cytoscape.js."""
    elements = _build_cytoscape_elements(skill_counts, pair_counts)
    elements_json = json.dumps(
        elements["nodes"] + elements["edges"],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{_escape_html(title)}</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: system-ui, sans-serif; margin: 0; background: #FAFAFA;
         display: flex; flex-direction: column; height: 100vh; overflow: hidden; }}
  #header {{ display: flex; align-items: center; justify-content: space-between;
             padding: 0.4rem 0.8rem; border-bottom: 1px solid #ddd; background: #fff; }}
  #title {{ font-size: 1rem; font-weight: 600; color: #333; }}
  #hint {{ font-size: 0.72rem; color: #999; }}
  button {{ font-size: 0.75rem; padding: 0.2rem 0.6rem; cursor: pointer;
            border: 1px solid #ccc; border-radius: 3px; background: #f5f5f5; }}
  button:hover {{ background: #e8e8e8; }}
  #cy {{ flex: 1; }}
  #tip {{ position: fixed; background: rgba(0,0,0,0.78); color: #fff;
          padding: 0.35rem 0.6rem; border-radius: 4px; font-size: 0.78rem;
          pointer-events: none; display: none; max-width: 220px; line-height: 1.4; }}
</style>
</head>
<body>
<div id="header">
  <span id="title">{_escape_html(title)}</span>
  <span>
    <span id="hint">drag · scroll to zoom · hover for details</span>
    &nbsp;
    <button onclick="cy.fit(30)">Reset view</button>
  </span>
</div>
<div id="cy"></div>
<div id="tip"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.29.2/cytoscape.min.js"></script>
<script>
var cy = cytoscape({{
  container: document.getElementById('cy'),
  elements: {elements_json},
  style: [
    {{
      selector: 'node',
      style: {{
        'shape': 'round-rectangle',
        'background-color': 'data(color)',
        'label': 'data(label)',
        'color': 'data(fontColor)',
        'text-valign': 'center',
        'text-halign': 'center',
        'font-size': '11px',
        'text-wrap': 'wrap',
        'text-max-width': 'data(nodeWidth)',
        'width': 'data(nodeWidth)',
        'height': 'data(nodeHeight)',
        'border-width': 2,
        'border-color': 'rgba(255,255,255,0.5)',
      }}
    }},
    {{
      selector: 'node:selected',
      style: {{
        'border-width': 3,
        'border-color': '#222',
        'border-opacity': 1,
      }}
    }},
    {{
      selector: 'edge',
      style: {{
        'width': 'data(width)',
        'line-color': 'data(color)',
        'target-arrow-color': 'data(color)',
        'target-arrow-shape': 'triangle',
        'arrow-scale': 1.2,
        'curve-style': 'bezier',
        'label': 'data(label)',
        'font-size': '9px',
        'color': '#444',
        'text-background-color': '#fff',
        'text-background-opacity': 0.75,
        'text-background-padding': '2px',
        'text-rotation': 'autorotate',
        'opacity': 0.85,
      }}
    }},
    {{
      selector: 'edge[?isSelfLoop]',
      style: {{
        'curve-style': 'loop',
        'loop-direction': '-45deg',
        'loop-sweep': '45deg',
        'text-rotation': '0deg',
      }}
    }},
    {{
      selector: 'edge:selected',
      style: {{ 'opacity': 1, 'line-color': '#222', 'target-arrow-color': '#222' }}
    }},
    {{
      selector: '.faded',
      style: {{ 'opacity': 0.15 }}
    }}
  ],
  layout: {{
    name: 'cose',
    animate: false,
    randomize: false,
    nodeRepulsion: function() {{ return 12000; }},
    idealEdgeLength: function() {{ return 120; }},
    gravity: 0.6,
    padding: 30,
    fit: true,
  }}
}});

// Tooltip
var tip = document.getElementById('tip');
function showTip(x, y, html) {{
  tip.innerHTML = html;
  tip.style.display = 'block';
  tip.style.left = (x + 14) + 'px';
  tip.style.top = (y + 14) + 'px';
}}
function hideTip() {{ tip.style.display = 'none'; }}

cy.on('mouseover', 'node', function(e) {{
  var d = e.target.data();
  showTip(e.originalEvent.clientX, e.originalEvent.clientY,
    '<b>' + d.id + '</b><br>' + d.count + ' invocations');
}});
cy.on('mouseover', 'edge', function(e) {{
  var d = e.target.data();
  var arrow = d.isSelfLoop ? '↺ ' + d.source : d.source + ' → ' + d.target;
  showTip(e.originalEvent.clientX, e.originalEvent.clientY,
    arrow + '<br>' + d.count + ' transition' + (d.count === 1 ? '' : 's'));
}});
cy.on('mousemove', function(e) {{
  if (tip.style.display !== 'none') {{
    tip.style.left = (e.originalEvent.clientX + 14) + 'px';
    tip.style.top  = (e.originalEvent.clientY + 14) + 'px';
  }}
}});
cy.on('mouseout', 'node, edge', hideTip);

// Click-to-highlight neighbourhood
cy.on('tap', 'node', function(e) {{
  var node = e.target;
  cy.elements().addClass('faded');
  node.removeClass('faded');
  node.connectedEdges().removeClass('faded').connectedNodes().removeClass('faded');
}});
cy.on('tap', function(e) {{
  if (e.target === cy) cy.elements().removeClass('faded');
}});
</script>
</body>
</html>"""


def _escape_html(text: str) -> str:
    """Minimal HTML escaping for safe insertion into HTML content."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def generate(
    window: list[dict],
    output_prefix: Path,
    title_scope: str,
    date_range: tuple[datetime, datetime],
) -> dict[str, Path | None]:
    """Generate transition graph artifacts from a telemetry window.

    Args:
        window: list of telemetry records (dicts).
        output_prefix: base path without extension for output files.
        title_scope: human-readable scope label for the graph title.
        date_range: (start, end) datetime pair for the title subtitle.

    Returns:
        A dict with keys ``dot``, ``svg`` (may be None), and ``html``,
        each mapping to the output Path.
    """
    sorted_window = _sort_window(window)
    skills = _extract_skills(sorted_window)

    skill_counts: Counter = Counter(skills)
    pair_counts: Counter = Counter()

    if len(skills) >= 2:
        pairs = [(skills[i], skills[i + 1]) for i in range(len(skills) - 1)]
        pair_counts = Counter(pairs)

    start_str = date_range[0].strftime("%Y-%m-%d")
    end_str = date_range[1].strftime("%Y-%m-%d")
    title = f"Skill Transitions -- {title_scope} ({start_str} to {end_str})"

    dot_source = _build_dot(skill_counts, pair_counts, title)

    dot_path = output_prefix.with_suffix(".dot")
    svg_path = output_prefix.with_suffix(".svg")
    html_path = output_prefix.with_suffix(".html")

    _write_dot(dot_source, dot_path)
    svg_result = _render_svg(dot_source, svg_path)
    html_content = _build_html(skill_counts, pair_counts, title)
    html_path.write_text(html_content, encoding="utf-8")

    return {
        "dot": dot_path,
        "svg": svg_result,
        "html": html_path,
    }


def _load_input(path_str: str | None) -> list[dict]:
    """Load JSON input from a file or stdin."""
    if path_str is None or path_str == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(path_str).read_text(encoding="utf-8")
    return json.loads(raw)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate a directed skill-transition graph from telemetry data."
    )
    parser.add_argument(
        "--input",
        default=None,
        help="Path to a JSON file with telemetry records, or '-' for stdin.",
    )
    parser.add_argument(
        "--output-prefix",
        required=True,
        help="Base path (without extension) for output files.",
    )
    parser.add_argument(
        "--scope",
        default="all",
        help="Human-readable scope label for the graph title.",
    )
    parser.add_argument(
        "--date-range",
        required=True,
        help="Comma-separated ISO date pair: <start>,<end>.",
    )

    args = parser.parse_args(argv)

    window = _load_input(args.input)

    parts = args.date_range.split(",", 1)
    if len(parts) != 2:
        print("ERROR: --date-range must be a comma-separated pair.", file=sys.stderr)
        return 1
    start_dt = datetime.fromisoformat(parts[0].strip())
    end_dt = datetime.fromisoformat(parts[1].strip())

    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)

    result = generate(window, output_prefix, args.scope, (start_dt, end_dt))

    summary = {
        "dot": str(result["dot"]),
        "svg": str(result["svg"]) if result["svg"] else None,
        "html": str(result["html"]),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
