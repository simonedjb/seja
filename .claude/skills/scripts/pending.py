#!/usr/bin/env python3
"""
pending.py -- Pending actions ledger for SEJA.

Manages `_output/pending.jsonl`, a JSONL append-only log of human actions
surfaced by skills and post-skill. Agents append new records and transition
events; a reducer applies last-write-wins to derive current state.

This is the first SEJA script to use argparse subparsers. Subcommands:
  add, done, snooze, dismiss, list, due, cleanup, periodic-check, status

Usage
-----
    python .claude/skills/scripts/pending.py add --type mark-implemented \\
        --source plan-000265 --description "Confirm impl for R-P-001"
    python .claude/skills/scripts/pending.py list --status pending --json
    python .claude/skills/scripts/pending.py status --overdue-days 14 --json

Exit codes: 0 success, 1 forbidden transition or validation error, 2 runtime
error (e.g. OUTPUT_DIR not configured).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from project_config import REPO_ROOT, get_path, get_pending_file


if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]


_ID_RE = re.compile(r"pa-(\d{6})")
_STAMP_CLEANUP = ".pending-cleanup-stamp"
_STAMP_PERIODIC = ".pending-periodic-stamp"


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(s: str) -> datetime:
    # Accepts both trailing Z and +00:00
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s).astimezone(timezone.utc)


def _parse_date(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Ledger I/O
# ---------------------------------------------------------------------------


def _ledger_path() -> Path | None:
    return get_pending_file()


def _require_ledger_path() -> Path:
    p = _ledger_path()
    if p is None:
        print("ERROR: OUTPUT_DIR not configured", file=sys.stderr)
        sys.exit(2)
    return p


def _read_lines(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            # Skip malformed lines (don't fail open, but don't crash)
            continue
    return out


def _append(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.is_file() else ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    existing += json.dumps(record, sort_keys=True) + "\n"
    path.write_text(existing, encoding="utf-8", newline="\n")


def _next_id(records: list[dict]) -> str:
    max_n = 0
    for r in records:
        rid = r.get("id", "")
        m = _ID_RE.fullmatch(rid)
        if m:
            n = int(m.group(1))
            if n > max_n:
                max_n = n
    return f"pa-{max_n + 1:06d}"


# ---------------------------------------------------------------------------
# Reducer
# ---------------------------------------------------------------------------


FORBIDDEN_TRANSITIONS = {
    # from_status: set of forbidden next statuses
    "dismissed": {"pending", "snoozed", "done"},
    "done": {"pending", "snoozed"},
}


def _reduce(records: list[dict]) -> dict[str, dict]:
    """Apply last-write-wins per id. Raises ValueError on forbidden transitions."""
    state: dict[str, dict] = {}
    for rec in records:
        rid = rec.get("id")
        if not rid:
            continue
        if rid not in state:
            # First sighting: must look like a creation record
            state[rid] = dict(rec)
            continue
        prev = state[rid]
        prev_status = prev.get("status", "pending")
        new_status = rec.get("status", prev_status)
        # Forbidden-transition checks
        if prev_status == "dismissed" and new_status != "dismissed":
            raise ValueError(
                f"forbidden transition for {rid}: dismissed -> {new_status}"
            )
        if prev_status == "done" and new_status in ("pending", "snoozed"):
            raise ValueError(
                f"forbidden transition for {rid}: done -> {new_status}"
            )
        # snoozed -> pending only if snooze expired (auto-expire handled at read time)
        if prev_status == "snoozed" and new_status == "pending":
            snooze_until = prev.get("snooze_until")
            if snooze_until:
                try:
                    if _parse_date(snooze_until) > _utcnow():
                        raise ValueError(
                            f"forbidden transition for {rid}: snoozed -> pending "
                            f"before snooze_until={snooze_until}"
                        )
                except ValueError as exc:
                    raise
        # Apply update (merge)
        merged = dict(prev)
        merged.update(rec)
        state[rid] = merged
    return state


def _effective_status(rec: dict) -> str:
    """Return the effective status, auto-expiring snoozed->pending if elapsed."""
    status = rec.get("status", "pending")
    if status == "snoozed":
        snooze_until = rec.get("snooze_until")
        if snooze_until:
            try:
                if _parse_date(snooze_until) <= _utcnow():
                    return "pending"
            except ValueError:
                pass
    return status


def _age_days(rec: dict) -> int:
    created = rec.get("created_at")
    if not created:
        return 0
    try:
        return max(0, (_utcnow() - _parse_iso(created)).days)
    except ValueError:
        return 0


# ---------------------------------------------------------------------------
# Subcommand implementations
# ---------------------------------------------------------------------------


def cmd_add(args: argparse.Namespace) -> int:
    path = _require_ledger_path()
    records = _read_lines(path)
    new_id = _next_id(records)
    now = _iso(_utcnow())
    rec = {
        "id": new_id,
        "type": args.type,
        "created_at": now,
        "source": args.source,
        "description": args.description,
        "status": "snoozed" if args.snooze_until else "pending",
        "snooze_until": args.snooze_until,
        "last_reminded_at": None,
    }
    _append(path, rec)
    print(new_id)
    return 0


def cmd_done(args: argparse.Namespace) -> int:
    path = _require_ledger_path()
    records = _read_lines(path)
    try:
        state = _reduce(records)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.id not in state:
        print(f"ERROR: {args.id} not found", file=sys.stderr)
        return 1
    prev = state[args.id]
    prev_status = prev.get("status", "pending")
    if prev_status == "dismissed":
        print(f"ERROR: forbidden transition for {args.id}: dismissed -> done", file=sys.stderr)
        return 1
    rec = {
        "id": args.id,
        "status": "done",
        "closed_at": _iso(_utcnow()),
    }
    _append(path, rec)
    return 0


def cmd_snooze(args: argparse.Namespace) -> int:
    path = _require_ledger_path()
    records = _read_lines(path)
    try:
        state = _reduce(records)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.id not in state:
        print(f"ERROR: {args.id} not found", file=sys.stderr)
        return 1
    prev_status = state[args.id].get("status", "pending")
    if prev_status in ("dismissed", "done"):
        print(f"ERROR: forbidden transition for {args.id}: {prev_status} -> snoozed", file=sys.stderr)
        return 1
    rec = {
        "id": args.id,
        "status": "snoozed",
        "snooze_until": args.until,
    }
    _append(path, rec)
    return 0


def cmd_dismiss(args: argparse.Namespace) -> int:
    path = _require_ledger_path()
    records = _read_lines(path)
    try:
        state = _reduce(records)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.id not in state:
        print(f"ERROR: {args.id} not found", file=sys.stderr)
        return 1
    rec = {
        "id": args.id,
        "status": "dismissed",
        "closed_at": _iso(_utcnow()),
        "reason": args.reason,
    }
    _append(path, rec)
    return 0


def _filter_and_sort(
    state: dict[str, dict],
    status_filter: str | None,
    source_filter: str | None,
    type_filter: str | None,
    overdue_days: int | None,
) -> list[dict]:
    items: list[dict] = []
    for rid, rec in state.items():
        eff = _effective_status(rec)
        if status_filter and status_filter != "all":
            if eff != status_filter:
                continue
        if source_filter and rec.get("source") != source_filter:
            continue
        if type_filter and rec.get("type") != type_filter:
            continue
        if overdue_days is not None and eff == "pending":
            if _age_days(rec) < overdue_days:
                continue
        items.append(rec)
    items.sort(key=lambda r: r.get("created_at", ""))
    return items


def cmd_list(args: argparse.Namespace) -> int:
    path = _ledger_path()
    if path is None or not path.is_file():
        if args.json:
            print("[]")
        return 0
    records = _read_lines(path)
    try:
        state = _reduce(records)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    status = args.status if args.status != "all" else None
    items = _filter_and_sort(
        state, status, args.source, args.type, args.overdue_days
    )
    if args.json:
        print(json.dumps(items, sort_keys=True))
        return 0
    if not items:
        print("(no pending actions)")
        return 0
    for rec in items:
        eff = _effective_status(rec)
        print(f"{rec['id']} [{eff}] {rec.get('type', '')} "
              f"source={rec.get('source', '')} age={_age_days(rec)}d "
              f"{rec.get('description', '')}")
    return 0


def cmd_due(args: argparse.Namespace) -> int:
    path = _ledger_path()
    if path is None or not path.is_file():
        return 0
    records = _read_lines(path)
    try:
        state = _reduce(records)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    due_items: list[dict] = []
    for rec in state.values():
        eff = _effective_status(rec)
        if eff == "pending":
            due_items.append(rec)
    for rec in sorted(due_items, key=lambda r: r.get("created_at", "")):
        print(f"{rec['id']} {rec.get('type', '')} {rec.get('description', '')}")
    return 0


def cmd_cleanup(args: argparse.Namespace) -> int:
    path = _require_ledger_path()
    records = _read_lines(path)
    try:
        state = _reduce(records)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    threshold = 90
    for rec in state.values():
        eff = _effective_status(rec)
        if eff not in ("pending", "snoozed"):
            continue
        if _age_days(rec) < threshold:
            continue
        dismiss_rec = {
            "id": rec["id"],
            "status": "dismissed",
            "closed_at": _iso(_utcnow()),
            "reason": "auto-dismissed: aged out",
        }
        _append(path, dismiss_rec)
    return 0


# ---------------------------------------------------------------------------
# Periodic-check: reads Periodic Triggers table from conventions.md
# ---------------------------------------------------------------------------


_PERIODIC_HEADER_RE = re.compile(r"^## Periodic Triggers\s*$")
_TRIGGER_ROW_RE = re.compile(
    r"^\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*`?([^`|]+?)`?\s*\|\s*([^|]+?)\s*\|$"
)


def _conventions_text() -> str | None:
    # Prefer project, fall back to template
    for rel in (
        Path("_references/project/conventions.md"),
        Path("_references/template/conventions.md"),
    ):
        p = REPO_ROOT / rel
        if p.is_file():
            return p.read_text(encoding="utf-8")
    return None


def _parse_periodic_triggers(text: str) -> list[dict]:
    """Return list of {name, interval_days, action_type}."""
    lines = text.splitlines()
    idx = None
    for i, ln in enumerate(lines):
        if _PERIODIC_HEADER_RE.match(ln):
            idx = i
            break
    if idx is None:
        return []
    triggers: list[dict] = []
    header_seen = False
    for ln in lines[idx + 1:]:
        if ln.startswith("## "):
            break
        if not ln.strip().startswith("|"):
            continue
        m = _TRIGGER_ROW_RE.match(ln.strip())
        if not m:
            continue
        name = m.group(1).strip()
        if name.lower() in ("trigger", "---------") or set(name) <= {"-", " "}:
            continue
        if not header_seen:
            # First matching row might be header "Trigger | Interval ..."
            # We only accept rows where interval is digits
            pass
        try:
            interval = int(m.group(2))
        except ValueError:
            continue
        action_type = m.group(3).strip()
        triggers.append({
            "name": name,
            "interval_days": interval,
            "action_type": action_type,
            "description": m.group(4).strip(),
        })
    return triggers


def _get_periodic_trigger_interval(action_type: str, default: int) -> int:
    """Return the configured interval (in days) for a given periodic action type.

    Reads the Periodic Triggers table from conventions.md (project, falling back
    to template). Returns `default` if the table or row cannot be parsed.
    """
    text = _conventions_text()
    if not text:
        return default
    triggers = _parse_periodic_triggers(text)
    for t in triggers:
        if t.get("action_type") == action_type:
            try:
                return int(t.get("interval_days", default))
            except (TypeError, ValueError):
                return default
    return default


def cmd_periodic_check(args: argparse.Namespace) -> int:
    warnings: list[str] = []
    created: list[dict] = []
    as_json = bool(getattr(args, "json", False))

    def _emit(rc: int) -> int:
        if as_json:
            payload = {
                "created": [
                    {
                        "id": r.get("id", ""),
                        "type": r.get("type", ""),
                        "description": r.get("description", ""),
                    }
                    for r in created
                ],
                "warnings": warnings,
            }
            print(json.dumps(payload, sort_keys=True))
        return rc

    text = _conventions_text()
    if not text:
        return _emit(0)
    if "## Periodic Triggers" not in text:
        return _emit(0)
    triggers = _parse_periodic_triggers(text)
    if not triggers:
        return _emit(0)
    path = _require_ledger_path()
    records = _read_lines(path)
    try:
        state = _reduce(records)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        warnings.append(f"reduce failed: {exc}")
        return _emit(1)
    now = _utcnow()
    for t in triggers:
        action_type = t["action_type"]
        interval = timedelta(days=t["interval_days"])
        stamp_name = f".{action_type}-stamp"
        stamp = _stamp_path(stamp_name)

        # Skip if there is an open (pending/snoozed) item of this type
        matching = [r for r in state.values() if r.get("type") == action_type]
        has_open = any(
            _effective_status(r) in ("pending", "snoozed") for r in matching
        )
        if has_open:
            continue

        # Stamp-based interval gate: create when stamp is stale or missing.
        # Falls back to ledger-based closed_at check when no stamp exists.
        should_create = False
        if _stamp_is_stale(stamp, interval):
            should_create = True
        elif not matching:
            should_create = True
        else:
            latest = max(matching, key=lambda r: r.get("created_at", ""))
            eff = _effective_status(latest)
            if eff in ("done", "dismissed"):
                closed_at = latest.get("closed_at")
                if closed_at:
                    try:
                        age = (now - _parse_iso(closed_at)).days
                        if age >= t["interval_days"]:
                            should_create = True
                    except ValueError:
                        pass
        if should_create:
            records = _read_lines(path)  # re-read to get fresh id
            new_id = _next_id(records)
            rec = {
                "id": new_id,
                "type": action_type,
                "created_at": _iso(now),
                "source": "periodic-trigger",
                "description": t["description"],
                "status": "pending",
                "snooze_until": None,
                "last_reminded_at": None,
            }
            _append(path, rec)
            state[new_id] = rec
            created.append(rec)
            # Touch the stamp; warn on failure
            try:
                _touch_stamp_strict(stamp)
            except OSError as exc:
                warnings.append(
                    f"{action_type} stamp write failed: {exc}"
                )
    return _emit(0)


# ---------------------------------------------------------------------------
# status (composite) -- per A8
# ---------------------------------------------------------------------------


def _stamp_path(name: str) -> Path | None:
    output_dir = get_path("OUTPUT_DIR")
    if output_dir is None:
        return None
    return output_dir / name


def _stamp_is_stale(stamp: Path | None, max_age: timedelta) -> bool:
    if stamp is None:
        return False
    if not stamp.is_file():
        return True
    try:
        mtime = datetime.fromtimestamp(stamp.stat().st_mtime, tz=timezone.utc)
    except OSError:
        return True
    return (_utcnow() - mtime) >= max_age


def _touch_stamp(stamp: Path | None) -> None:
    if stamp is None:
        return
    try:
        stamp.parent.mkdir(parents=True, exist_ok=True)
        stamp.write_text(_iso(_utcnow()), encoding="utf-8")
    except OSError:
        pass


def _touch_stamp_strict(stamp: Path | None) -> None:
    """Like _touch_stamp but raises OSError on failure."""
    if stamp is None:
        return
    stamp.parent.mkdir(parents=True, exist_ok=True)
    stamp.write_text(_iso(_utcnow()), encoding="utf-8")


def cmd_status(args: argparse.Namespace) -> int:
    warnings: list[str] = []

    # If OUTPUT_DIR cannot be resolved, skip cleanup/periodic-check entirely and
    # emit an empty payload with a warning. This prevents the pre-skill hot path
    # from bricking the framework when a project's conventions.md is malformed.
    if _ledger_path() is None:
        payload = {
            "count": 0,
            "overdue_count": 0,
            "top_3": [],
            "warnings": ["OUTPUT_DIR not configured; pending-check is a no-op"],
        }
        print(json.dumps(payload, sort_keys=True))
        return 0

    cleanup_stamp = _stamp_path(_STAMP_CLEANUP)
    periodic_stamp = _stamp_path(_STAMP_PERIODIC)

    # Conditional cleanup (24h throttle). Catch BaseException (not Exception) so
    # that a nested SystemExit from _require_ledger_path or similar is captured
    # as a warning rather than crashing the pre-skill hot path.
    if _stamp_is_stale(cleanup_stamp, timedelta(hours=24)):
        try:
            rc = cmd_cleanup(argparse.Namespace())
            if rc == 0:
                _touch_stamp(cleanup_stamp)
            else:
                warnings.append("cleanup returned non-zero")
        except BaseException as exc:  # noqa: BLE001 -- intentional catch-all
            warnings.append(f"cleanup failed: {exc}")

    # Conditional periodic-check (1h throttle). Same BaseException catch rationale.
    if _stamp_is_stale(periodic_stamp, timedelta(hours=1)):
        try:
            rc = cmd_periodic_check(argparse.Namespace())
            if rc == 0:
                _touch_stamp(periodic_stamp)
            else:
                warnings.append("periodic-check returned non-zero")
        except BaseException as exc:  # noqa: BLE001 -- intentional catch-all
            warnings.append(f"periodic-check failed: {exc}")

    # Reduce ledger
    path = _ledger_path()
    if path is None or not path.is_file():
        payload = {
            "count": 0,
            "overdue_count": 0,
            "top_3": [],
            "warnings": warnings,
        }
        print(json.dumps(payload, sort_keys=True))
        return 0
    records = _read_lines(path)
    try:
        state = _reduce(records)
    except ValueError as exc:
        warnings.append(f"reduce failed: {exc}")
        payload = {
            "count": 0,
            "overdue_count": 0,
            "top_3": [],
            "warnings": warnings,
        }
        print(json.dumps(payload, sort_keys=True))
        return 0

    pending_items = [r for r in state.values() if _effective_status(r) == "pending"]
    pending_items.sort(key=lambda r: r.get("created_at", ""))
    overdue_days = args.overdue_days if args.overdue_days is not None else 14
    overdue_items = [r for r in pending_items if _age_days(r) >= overdue_days]

    top_3 = []
    for rec in pending_items[:3]:
        top_3.append({
            "type": rec.get("type", ""),
            "source": rec.get("source", ""),
            "age_days": _age_days(rec),
            "description": rec.get("description", ""),
        })

    payload = {
        "count": len(pending_items),
        "overdue_count": len(overdue_items),
        "top_3": top_3,
        "warnings": warnings,
    }
    print(json.dumps(payload, sort_keys=True))
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pending actions ledger for SEJA.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Add a new pending action.")
    p_add.add_argument("--type", required=True)
    p_add.add_argument("--source", required=True)
    p_add.add_argument("--description", required=True)
    p_add.add_argument("--snooze-until", dest="snooze_until")
    p_add.set_defaults(func=cmd_add)

    p_done = sub.add_parser("done", help="Mark an action as done.")
    p_done.add_argument("id")
    p_done.set_defaults(func=cmd_done)

    p_snooze = sub.add_parser("snooze", help="Snooze an action until a date.")
    p_snooze.add_argument("id")
    p_snooze.add_argument("--until", required=True)
    p_snooze.set_defaults(func=cmd_snooze)

    p_dismiss = sub.add_parser("dismiss", help="Dismiss an action.")
    p_dismiss.add_argument("id")
    p_dismiss.add_argument("--reason")
    p_dismiss.set_defaults(func=cmd_dismiss)

    p_list = sub.add_parser("list", help="List actions.")
    p_list.add_argument(
        "--status",
        choices=["pending", "snoozed", "done", "dismissed", "all"],
        default="pending",
    )
    p_list.add_argument("--overdue-days", type=int, dest="overdue_days")
    p_list.add_argument("--source")
    p_list.add_argument("--type")
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_due = sub.add_parser("due", help="List actions that are due.")
    p_due.set_defaults(func=cmd_due)

    p_cleanup = sub.add_parser("cleanup", help="Auto-dismiss aged items.")
    p_cleanup.set_defaults(func=cmd_cleanup)

    p_periodic = sub.add_parser("periodic-check", help="Create periodic entries.")
    p_periodic.add_argument("--json", action="store_true")
    p_periodic.set_defaults(func=cmd_periodic_check)

    p_status = sub.add_parser("status", help="Composite status (pre-skill).")
    p_status.add_argument("--overdue-days", type=int, dest="overdue_days")
    p_status.add_argument("--json", action="store_true")
    p_status.set_defaults(func=cmd_status)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
