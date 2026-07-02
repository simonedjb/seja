#!/usr/bin/env python3
# designer: After /plan generates a plan inline from a roadmap, I update the
#   roadmap file's Plan column for the matching work-item row from plan-TBD to
#   the real reserved plan ID -- targeted by work-item slug so the edit is
#   always unambiguous even when the table has many plan-TBD cells.
"""
update_roadmap_plan_id.py -- Backfill a plan ID into a roadmap Wave Summary row.

Invocation: skill-invoked
Lifecycle: active

Finds the Wave Summary table row whose ID column matches --work-item-id and
replaces its first `plan-TBD` cell with --plan-id. Operates on any roadmap
file produced by /plan --roadmap (roadmap-summary.md template shape).

Usage
-----
    python .claude/skills/scripts/update_roadmap_plan_id.py \\
        --roadmap-file _output/roadmap/roadmap-000042-my-project.md \\
        --work-item-id user-model \\
        --plan-id plan-000123

Exit codes: 0 success, 1 work-item not found or plan-TBD already replaced.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Backfill a plan ID into a roadmap row.")
    p.add_argument("--roadmap-file", required=True, help="Path to the roadmap summary .md file.")
    p.add_argument("--work-item-id", required=True, help="ID column slug of the target row (e.g. user-model).")
    p.add_argument("--plan-id", required=True, help="Reserved plan ID to write (e.g. plan-000123).")
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    roadmap_path = Path(args.roadmap_file)

    if not roadmap_path.exists():
        print(f"ERROR: roadmap file not found: {roadmap_path}", file=sys.stderr)
        return 1

    lines = roadmap_path.read_text(encoding="utf-8").splitlines(keepends=True)
    slug = args.work_item_id.strip()
    updated = False

    for i, line in enumerate(lines):
        # Match pipe-delimited table rows; ID is the second cell (index 1 after split).
        if not line.strip().startswith("|"):
            continue
        cells = line.split("|")
        # cells[0] == '' (before first pipe), cells[1] == row number, cells[2] == ID
        if len(cells) < 4:
            continue
        row_id = cells[2].strip()
        if row_id != slug:
            continue
        if "plan-TBD" not in line:
            print(f"ERROR: row '{slug}' found but contains no plan-TBD (already filled?)", file=sys.stderr)
            return 1
        lines[i] = line.replace("plan-TBD", args.plan_id, 1)
        updated = True
        break

    if not updated:
        print(f"ERROR: work-item-id '{slug}' not found in {roadmap_path}", file=sys.stderr)
        return 1

    roadmap_path.write_text("".join(lines), encoding="utf-8")
    print(f"Updated row '{slug}' -> {args.plan_id} in {roadmap_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
