"""Tests for pending.py."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = SCRIPTS_DIR / "pending.py"

sys.path.insert(0, str(SCRIPTS_DIR))


MINIMAL_CONVENTIONS = """\
# Project Conventions

## Paths

| Variable | Value | Description |
|----------|-------|-------------|
| `OUTPUT_DIR` | `_output` | Output dir |

## Periodic Triggers

| Trigger | Interval (days) | Action type | Description |
|---------|-----------------|-------------|-------------|
| Periodic curation | 30 | periodic-curation | Review items ready to promote |
| Spec-drift check | 14 | spec-drift-check | Run /explain spec-drift |

## Source Directories
"""


CONVENTIONS_WITH_REFLECT = """\
# Project Conventions

## Paths

| Variable | Value | Description |
|----------|-------|-------------|
| `OUTPUT_DIR` | `_output` | Output dir |

## Periodic Triggers

| Trigger | Interval (days) | Action type | Description |
|---------|-----------------|-------------|-------------|
| Reflection on practice | 30 | reflect-on-practice | Review patterns from the last 30 days via /reflect |

## Source Directories
"""


def _run_pending(
    fake_repo: Path, *args: str, conventions: str | None = None
) -> subprocess.CompletedProcess:
    """Invoke pending.py in a fake repo with OUTPUT_DIR set to _output."""
    (fake_repo / ".claude").mkdir(exist_ok=True)
    output_dir = fake_repo / "_output"
    output_dir.mkdir(exist_ok=True)

    # Write minimal conventions.md in project/ if provided
    proj_dir = fake_repo / "_references" / "project"
    proj_dir.mkdir(parents=True, exist_ok=True)
    if conventions is not None:
        (proj_dir / "conventions.md").write_text(conventions, encoding="utf-8")
    else:
        # Minimal conventions with OUTPUT_DIR
        (proj_dir / "conventions.md").write_text(
            "# Conv\n\n## Paths\n\n| Variable | Value | Description |\n"
            "|----------|-------|-------------|\n"
            "| `OUTPUT_DIR` | `_output` | Output dir |\n",
            encoding="utf-8",
        )

    runner = fake_repo / "_runner.py"
    runner.write_text(
        "import sys\n"
        "from pathlib import Path\n"
        f"sys.path.insert(0, {str(SCRIPTS_DIR)!r})\n"
        "import project_config\n"
        f"project_config.REPO_ROOT = Path({str(fake_repo)!r})\n"
        "project_config._config = None\n"  # force reparse
        "import pending\n"
        f"pending.REPO_ROOT = Path({str(fake_repo)!r})\n"
        f"sys.argv = [{str(SCRIPT_PATH)!r}] + {list(args)!r}\n"
        "sys.exit(pending.main())\n",
        encoding="utf-8",
    )
    return subprocess.run(
        [sys.executable, str(runner)],
        cwd=str(fake_repo),
        capture_output=True,
        text=True,
        env=dict(os.environ),
    )


def _read_ledger(fake_repo: Path) -> list[dict]:
    ledger = fake_repo / "_output" / "pending.jsonl"
    if not ledger.is_file():
        return []
    return [json.loads(ln) for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_add_creates_file(tmp_path):
    r = _run_pending(tmp_path, "add", "--type", "mark-implemented",
                     "--source", "plan-000001", "--description", "test1")
    assert r.returncode == 0, r.stderr
    assert (tmp_path / "_output" / "pending.jsonl").is_file()
    assert r.stdout.strip() == "pa-000001"


def test_add_assigns_sequential_ids(tmp_path):
    _run_pending(tmp_path, "add", "--type", "t", "--source", "s1", "--description", "d1")
    r2 = _run_pending(tmp_path, "add", "--type", "t", "--source", "s2", "--description", "d2")
    assert r2.stdout.strip() == "pa-000002"


def test_list_empty(tmp_path):
    r = _run_pending(tmp_path, "list", "--json")
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "[]"


def test_list_pending_after_add(tmp_path):
    _run_pending(tmp_path, "add", "--type", "t", "--source", "s", "--description", "d")
    r = _run_pending(tmp_path, "list", "--json")
    assert r.returncode == 0, r.stderr
    items = json.loads(r.stdout)
    assert len(items) == 1
    assert items[0]["status"] == "pending"


def test_done_transition(tmp_path):
    _run_pending(tmp_path, "add", "--type", "t", "--source", "s", "--description", "d")
    r = _run_pending(tmp_path, "done", "pa-000001")
    assert r.returncode == 0, r.stderr
    r2 = _run_pending(tmp_path, "list", "--status", "done", "--json")
    items = json.loads(r2.stdout)
    assert len(items) == 1
    assert items[0]["status"] == "done"


def test_snooze_transition(tmp_path):
    _run_pending(tmp_path, "add", "--type", "t", "--source", "s", "--description", "d")
    future = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d")
    r = _run_pending(tmp_path, "snooze", "pa-000001", "--until", future)
    assert r.returncode == 0, r.stderr
    r2 = _run_pending(tmp_path, "list", "--status", "snoozed", "--json")
    items = json.loads(r2.stdout)
    assert len(items) == 1


def test_due_after_snooze_expires(tmp_path):
    _run_pending(tmp_path, "add", "--type", "t", "--source", "s", "--description", "d")
    past = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    _run_pending(tmp_path, "snooze", "pa-000001", "--until", past)
    r = _run_pending(tmp_path, "list", "--status", "pending", "--json")
    items = json.loads(r.stdout)
    # Snoozed items whose snooze_until has passed auto-expire to pending
    assert len(items) == 1


def test_dismiss_transition(tmp_path):
    _run_pending(tmp_path, "add", "--type", "t", "--source", "s", "--description", "d")
    r = _run_pending(tmp_path, "dismiss", "pa-000001", "--reason", "not needed")
    assert r.returncode == 0, r.stderr
    r2 = _run_pending(tmp_path, "list", "--status", "dismissed", "--json")
    items = json.loads(r2.stdout)
    assert len(items) == 1
    assert items[0]["status"] == "dismissed"


def test_forbidden_transition_dismissed_to_done(tmp_path):
    _run_pending(tmp_path, "add", "--type", "t", "--source", "s", "--description", "d")
    _run_pending(tmp_path, "dismiss", "pa-000001", "--reason", "x")
    r = _run_pending(tmp_path, "done", "pa-000001")
    assert r.returncode == 1
    assert "forbidden transition" in r.stderr


def test_cleanup_auto_dismisses_old_items(tmp_path):
    # Add an item, then manually rewrite ledger with an old created_at
    _run_pending(tmp_path, "add", "--type", "t", "--source", "s", "--description", "d")
    ledger = tmp_path / "_output" / "pending.jsonl"
    records = _read_ledger(tmp_path)
    old_dt = datetime.now(timezone.utc) - timedelta(days=100)
    records[0]["created_at"] = old_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    ledger.write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
        encoding="utf-8",
    )
    r = _run_pending(tmp_path, "cleanup")
    assert r.returncode == 0, r.stderr
    r2 = _run_pending(tmp_path, "list", "--status", "dismissed", "--json")
    items = json.loads(r2.stdout)
    assert len(items) == 1
    assert items[0].get("reason", "").startswith("auto-dismissed")


def test_reducer_last_write_wins(tmp_path):
    _run_pending(tmp_path, "add", "--type", "t", "--source", "s", "--description", "orig")
    future = (datetime.now(timezone.utc) + timedelta(days=10)).strftime("%Y-%m-%d")
    _run_pending(tmp_path, "snooze", "pa-000001", "--until", future)
    r = _run_pending(tmp_path, "list", "--status", "all", "--json")
    items = json.loads(r.stdout)
    assert len(items) == 1
    assert items[0]["status"] == "snoozed"
    assert items[0]["snooze_until"] == future


def test_periodic_check_creates_entries_on_first_run(tmp_path):
    r = _run_pending(tmp_path, "periodic-check", conventions=MINIMAL_CONVENTIONS)
    assert r.returncode == 0, r.stderr
    r2 = _run_pending(tmp_path, "list", "--status", "all", "--json",
                      conventions=MINIMAL_CONVENTIONS)
    items = json.loads(r2.stdout)
    types = {i["type"] for i in items}
    assert "periodic-curation" in types
    assert "spec-drift-check" in types


def test_periodic_check_respects_interval(tmp_path):
    _run_pending(tmp_path, "periodic-check", conventions=MINIMAL_CONVENTIONS)
    _run_pending(tmp_path, "periodic-check", conventions=MINIMAL_CONVENTIONS)
    r = _run_pending(tmp_path, "list", "--status", "all", "--json",
                     conventions=MINIMAL_CONVENTIONS)
    items = json.loads(r.stdout)
    # Should still be exactly 2 (one per trigger) -- second run should skip
    assert len(items) == 2


def test_periodic_check_recreates_after_interval_elapses(tmp_path):
    _run_pending(tmp_path, "periodic-check", conventions=MINIMAL_CONVENTIONS)
    # Mark both as done with old closed_at
    _run_pending(tmp_path, "done", "pa-000001", conventions=MINIMAL_CONVENTIONS)
    _run_pending(tmp_path, "done", "pa-000002", conventions=MINIMAL_CONVENTIONS)
    # Rewrite ledger to set closed_at to 40 days ago
    ledger = tmp_path / "_output" / "pending.jsonl"
    old_iso = (datetime.now(timezone.utc) - timedelta(days=40)).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = ledger.read_text(encoding="utf-8").splitlines()
    new_lines = []
    for ln in lines:
        if not ln.strip():
            continue
        rec = json.loads(ln)
        if rec.get("status") == "done":
            rec["closed_at"] = old_iso
        new_lines.append(json.dumps(rec, sort_keys=True))
    ledger.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    _run_pending(tmp_path, "periodic-check", conventions=MINIMAL_CONVENTIONS)
    r = _run_pending(tmp_path, "list", "--status", "pending", "--json",
                     conventions=MINIMAL_CONVENTIONS)
    items = json.loads(r.stdout)
    # After recreating, should have 2 new pending items (one per trigger whose
    # last closure is older than interval)
    types = {i["type"] for i in items}
    # Spec-drift-check interval is 14 days, and periodic-curation is 30 days;
    # both <40 days ago, so both recreate.
    assert "spec-drift-check" in types
    assert "periodic-curation" in types


def test_cold_repo_silent(tmp_path):
    # No periodic triggers section present
    r = _run_pending(tmp_path, "periodic-check", conventions="# No triggers here\n")
    assert r.returncode == 0
    r2 = _run_pending(tmp_path, "list", "--json", conventions="# No triggers here\n")
    assert r2.returncode == 0
    assert r2.stdout.strip() == "[]"


def test_status_subcommand_happy_path(tmp_path):
    _run_pending(tmp_path, "add", "--type", "t1", "--source", "plan-1", "--description", "one")
    _run_pending(tmp_path, "add", "--type", "t2", "--source", "plan-2", "--description", "two")
    r = _run_pending(tmp_path, "status", "--json", "--overdue-days", "14")
    assert r.returncode == 0, r.stderr
    payload = json.loads(r.stdout)
    assert payload["count"] == 2
    assert payload["overdue_count"] == 0
    assert len(payload["top_3"]) == 2
    assert payload["top_3"][0]["source"] == "plan-1"


# ---------------------------------------------------------------------------
# reflect-on-practice periodic trigger (stamp-based dispatch)
# ---------------------------------------------------------------------------


def _reflect_stamp(fake_repo: Path) -> Path:
    return fake_repo / "_output" / ".reflect-on-practice-stamp"


def test_reflect_on_practice_first_run_creates_action_and_stamp(tmp_path):
    r = _run_pending(
        tmp_path, "periodic-check", "--json", conventions=CONVENTIONS_WITH_REFLECT
    )
    assert r.returncode == 0, r.stderr
    payload = json.loads(r.stdout)
    assert payload["warnings"] == []
    created_types = {item["type"] for item in payload["created"]}
    assert "reflect-on-practice" in created_types
    # Stamp file should exist after a clean run
    assert _reflect_stamp(tmp_path).is_file()
    # Ledger should contain the new pending action
    ledger = _read_ledger(tmp_path)
    reflect_items = [r for r in ledger if r.get("type") == "reflect-on-practice"]
    assert len(reflect_items) == 1
    assert reflect_items[0]["source"] == "periodic-trigger"
    assert reflect_items[0]["status"] == "pending"
    assert "/reflect" in reflect_items[0]["description"]


def test_reflect_on_practice_inside_interval_skips(tmp_path):
    # Prime the stamp by running once
    _run_pending(
        tmp_path, "periodic-check", "--json", conventions=CONVENTIONS_WITH_REFLECT
    )
    # Set stamp to 5 days ago (inside the 30-day interval)
    stamp = _reflect_stamp(tmp_path)
    assert stamp.is_file()
    five_days_ago = (datetime.now() - timedelta(days=5)).timestamp()
    os.utime(stamp, (five_days_ago, five_days_ago))
    # Dismiss the first item so the no-duplicate-open-pending guard doesn't
    # mask the interval logic we're testing.
    _run_pending(tmp_path, "dismiss", "pa-000001", "--reason", "t",
                 conventions=CONVENTIONS_WITH_REFLECT)
    # Run again
    r = _run_pending(
        tmp_path, "periodic-check", "--json", conventions=CONVENTIONS_WITH_REFLECT
    )
    assert r.returncode == 0, r.stderr
    payload = json.loads(r.stdout)
    created_types = {item["type"] for item in payload["created"]}
    assert "reflect-on-practice" not in created_types
    # Ledger should still contain only the one original action
    ledger = _read_ledger(tmp_path)
    reflect_items = [r for r in ledger if r.get("type") == "reflect-on-practice"]
    # One creation + one dismissal event, but only one unique id
    ids = {r.get("id") for r in reflect_items}
    assert ids == {"pa-000001"}


def test_reflect_on_practice_after_interval_creates(tmp_path):
    _run_pending(
        tmp_path, "periodic-check", "--json", conventions=CONVENTIONS_WITH_REFLECT
    )
    # Dismiss the first item so the no-duplicate guard allows a new creation
    _run_pending(tmp_path, "dismiss", "pa-000001", "--reason", "t",
                 conventions=CONVENTIONS_WITH_REFLECT)
    # Set stamp to 35 days ago (beyond the 30-day interval)
    stamp = _reflect_stamp(tmp_path)
    thirty_five_days_ago = (datetime.now() - timedelta(days=35)).timestamp()
    os.utime(stamp, (thirty_five_days_ago, thirty_five_days_ago))
    r = _run_pending(
        tmp_path, "periodic-check", "--json", conventions=CONVENTIONS_WITH_REFLECT
    )
    assert r.returncode == 0, r.stderr
    payload = json.loads(r.stdout)
    created_types = {item["type"] for item in payload["created"]}
    assert "reflect-on-practice" in created_types
    # Stamp should be refreshed (mtime newer than 35 days ago)
    new_mtime = stamp.stat().st_mtime
    assert new_mtime > thirty_five_days_ago + 60  # updated well past the old value


def test_reflect_on_practice_stamp_write_failure_degrades_gracefully(tmp_path):
    # Simulate stamp-write failure by replacing the stamp path with a
    # read-only directory so write_text raises OSError.
    output_dir = tmp_path / "_output"
    output_dir.mkdir(exist_ok=True)
    stamp_path = output_dir / ".reflect-on-practice-stamp"
    # Create the stamp path as a directory -- writing to it as a file will fail
    stamp_path.mkdir()
    r = _run_pending(
        tmp_path, "periodic-check", "--json", conventions=CONVENTIONS_WITH_REFLECT
    )
    # Exit 0 even though stamp write failed
    assert r.returncode == 0, r.stderr
    payload = json.loads(r.stdout)
    # Warning about stamp write failure
    warnings_text = " ".join(payload["warnings"])
    assert "reflect-on-practice" in warnings_text
    # Pending action should still have been created (stamp failure is non-fatal)
    ledger = _read_ledger(tmp_path)
    reflect_items = [r for r in ledger if r.get("type") == "reflect-on-practice"]
    assert len(reflect_items) == 1


def test_status_subcommand_stamp_throttling(tmp_path):
    # First call creates stamps
    _run_pending(tmp_path, "add", "--type", "t", "--source", "s", "--description", "d")
    _run_pending(tmp_path, "status", "--json")
    cleanup_stamp = tmp_path / "_output" / ".pending-cleanup-stamp"
    assert cleanup_stamp.is_file()
    # Set stamp mtime to 1 hour ago -- cleanup should NOT run (24h throttle)
    one_hour_ago = (datetime.now() - timedelta(hours=1)).timestamp()
    os.utime(cleanup_stamp, (one_hour_ago, one_hour_ago))
    mtime_before = cleanup_stamp.stat().st_mtime
    _run_pending(tmp_path, "status", "--json")
    mtime_after = cleanup_stamp.stat().st_mtime
    assert abs(mtime_after - mtime_before) < 1.0  # unchanged

    # Set stamp to 25 hours ago -- cleanup SHOULD run
    twenty_five_hours_ago = (datetime.now() - timedelta(hours=25)).timestamp()
    os.utime(cleanup_stamp, (twenty_five_hours_ago, twenty_five_hours_ago))
    _run_pending(tmp_path, "status", "--json")
    mtime_after2 = cleanup_stamp.stat().st_mtime
    assert mtime_after2 > twenty_five_hours_ago + 10  # updated
