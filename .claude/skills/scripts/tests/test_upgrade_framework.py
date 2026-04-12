"""Tests for upgrade_framework._regenerate_reference_files (plan-000291)."""
from __future__ import annotations

import stat
import sys
from pathlib import Path

import pytest

import upgrade_framework


def _make_scripts_dir(target: Path) -> Path:
    scripts_dir = target / ".claude" / "skills" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    return scripts_dir


def _write_generator(scripts_dir: Path, name: str, body: str) -> Path:
    script = scripts_dir / name
    script.write_text(body, encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return script


def _sentinel_generator_body(sentinel_rel_path: str) -> str:
    return (
        "import sys\n"
        "from pathlib import Path\n"
        "sentinel = Path.cwd() / r'" + sentinel_rel_path + "'\n"
        "sentinel.parent.mkdir(parents=True, exist_ok=True)\n"
        "sentinel.write_text('generated', encoding='utf-8')\n"
        "sys.exit(0)\n"
    )


def test_regenerate_reference_files_invokes_present_generators(tmp_path, capsys):
    scripts_dir = _make_scripts_dir(tmp_path)
    _write_generator(scripts_dir, "generate_framework_reference.py",
                     _sentinel_generator_body("seja-public/docs/reference/framework-reference.md"))
    _write_generator(scripts_dir, "generate_skills_reference.py",
                     _sentinel_generator_body("seja-public/docs/reference/skills.md"))
    _write_generator(scripts_dir, "generate_perspectives_reference.py",
                     _sentinel_generator_body("seja-public/docs/reference/perspectives.md"))

    report: list[str] = []
    upgrade_framework._regenerate_reference_files(tmp_path, dry_run=False, report_updated=report)

    assert (tmp_path / "seja-public/docs/reference/framework-reference.md").is_file()
    assert (tmp_path / "seja-public/docs/reference/skills.md").is_file()
    assert (tmp_path / "seja-public/docs/reference/perspectives.md").is_file()
    assert len(report) == 3
    assert all("Regenerated" in line for line in report)


def test_regenerate_reference_files_skips_missing_generators(tmp_path, capsys):
    scripts_dir = _make_scripts_dir(tmp_path)
    _write_generator(scripts_dir, "generate_framework_reference.py",
                     _sentinel_generator_body("seja-public/docs/reference/framework-reference.md"))
    # skills + perspectives generators intentionally missing

    report: list[str] = []
    upgrade_framework._regenerate_reference_files(tmp_path, dry_run=False, report_updated=report)

    captured = capsys.readouterr()
    assert "Skipped skills reference" in captured.out
    assert "Skipped perspectives reference" in captured.out
    assert len(report) == 1
    assert "framework-reference" in report[0]


def test_regenerate_reference_files_dry_run_logs_without_executing(tmp_path, capsys):
    scripts_dir = _make_scripts_dir(tmp_path)
    _write_generator(scripts_dir, "generate_framework_reference.py",
                     _sentinel_generator_body("seja-public/docs/reference/framework-reference.md"))
    _write_generator(scripts_dir, "generate_skills_reference.py",
                     _sentinel_generator_body("seja-public/docs/reference/skills.md"))
    _write_generator(scripts_dir, "generate_perspectives_reference.py",
                     _sentinel_generator_body("seja-public/docs/reference/perspectives.md"))

    report: list[str] = []
    upgrade_framework._regenerate_reference_files(tmp_path, dry_run=True, report_updated=report)

    assert not (tmp_path / "seja-public/docs/reference/framework-reference.md").exists()
    assert not (tmp_path / "seja-public/docs/reference/skills.md").exists()
    assert not (tmp_path / "seja-public/docs/reference/perspectives.md").exists()
    assert report == []
    captured = capsys.readouterr()
    assert captured.out.count("Would regenerate") == 3


def test_regenerate_reference_files_continues_on_generator_failure(tmp_path, capsys):
    scripts_dir = _make_scripts_dir(tmp_path)
    # Generator exits non-zero
    _write_generator(scripts_dir, "generate_framework_reference.py",
                     "import sys\nsys.stderr.write('boom\\n')\nsys.exit(1)\n")
    _write_generator(scripts_dir, "generate_skills_reference.py",
                     _sentinel_generator_body("seja-public/docs/reference/skills.md"))
    _write_generator(scripts_dir, "generate_perspectives_reference.py",
                     _sentinel_generator_body("seja-public/docs/reference/perspectives.md"))

    report: list[str] = []
    upgrade_framework._regenerate_reference_files(tmp_path, dry_run=False, report_updated=report)

    captured = capsys.readouterr()
    assert "framework-reference regeneration failed" in captured.out
    # The other two generators still ran
    assert (tmp_path / "seja-public/docs/reference/skills.md").is_file()
    assert (tmp_path / "seja-public/docs/reference/perspectives.md").is_file()
    assert len(report) == 2
    assert not any("framework-reference" == line.replace("Regenerated ", "") for line in report)


def test_regenerate_reference_files_handles_timeout(tmp_path, capsys, monkeypatch):
    scripts_dir = _make_scripts_dir(tmp_path)
    # Generator sleeps longer than the monkeypatched timeout
    _write_generator(
        scripts_dir, "generate_framework_reference.py",
        "import time\ntime.sleep(5)\n",
    )

    # Monkeypatch subprocess.run to raise TimeoutExpired for the first call,
    # simulating a generator that exceeds the timeout without actually waiting.
    import subprocess as _subprocess
    real_run = _subprocess.run

    def fake_run(cmd, *args, **kwargs):
        if "generate_framework_reference.py" in " ".join(str(c) for c in cmd):
            raise _subprocess.TimeoutExpired(cmd=cmd, timeout=1)
        return real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(upgrade_framework.subprocess, "run", fake_run)

    report: list[str] = []
    upgrade_framework._regenerate_reference_files(tmp_path, dry_run=False, report_updated=report)

    captured = capsys.readouterr()
    assert "timed out" in captured.out
    # The helper did not raise and report remains empty for the timed-out generator
    assert not any("framework-reference" in line for line in report)
