"""Tests for check_no_private_leaks.py.

Covers:
- --files / --staged (pre-sync) mode: scan source .md files as they would
  appear after strip_private_sections, then flag residual markers or
  fingerprints that escaped markup.
- Default mode: warns if seja-public/.claude/ exists; scans only authored
  prose (docs/ and top-level *.md) for priv-only markers.
- --candidate mode: full leak scan of a candidate publish directory.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import check_no_private_leaks as checker  # noqa: E402


def _write_skill(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def test_files_mode_clean_skill(tmp_path: Path) -> None:
    skill = _write_skill(
        tmp_path, "clean",
        "---\nname: clean\n---\n# Clean Skill\n\nJust public content here.\n",
    )
    assert checker.check_files_pre_sync([skill]) == []


def test_files_mode_marked_private_passes(tmp_path: Path) -> None:
    skill = _write_skill(
        tmp_path, "marked",
        "---\nname: marked\n---\n# Marked Skill\n"
        "<!-- priv-only-start -->\n"
        "Run `python tools/pre_publish_smoke.py` before push.\n"
        "<!-- priv-only-end -->\n"
        "\nPublic content.\n",
    )
    # Fingerprint is inside priv-only markers — should be stripped.
    assert checker.check_files_pre_sync([skill]) == []


def test_files_mode_unmarked_fingerprint_fails(tmp_path: Path) -> None:
    skill = _write_skill(
        tmp_path, "leaky",
        "---\nname: leaky\n---\n# Leaky Skill\n\n"
        "Run `python tools/pre_publish_smoke.py` before push.\n",
    )
    issues = checker.check_files_pre_sync([skill])
    assert len(issues) == 1
    assert "pre_publish_smoke" in issues[0] or "smoke-test" in issues[0]


def test_files_mode_malformed_marker_fails(tmp_path: Path) -> None:
    # Marker only on start line; no matching end. Stripper leaves it in place,
    # and the pre-sync check catches the residual marker.
    skill = _write_skill(
        tmp_path, "malformed",
        "---\nname: malformed\n---\n# Malformed\n\n"
        "<!-- priv-only-start -->\n"
        "This section is never closed.\n",
    )
    issues = checker.check_files_pre_sync([skill])
    assert any("priv-only marker survives strip" in i for i in issues)


def test_files_mode_fingerprint_inside_fenced_block_passes(tmp_path: Path) -> None:
    # Documentation example inside ``` fence should not trip the check.
    skill = _write_skill(
        tmp_path, "doc_example",
        "---\nname: doc_example\n---\n# Example\n\n"
        "```bash\n"
        "python tools/pre_publish_smoke.py\n"
        "```\n",
    )
    assert checker.check_files_pre_sync([skill]) == []


def test_files_mode_non_skill_file_ignores_fingerprints(tmp_path: Path) -> None:
    # Rules and runbook files legitimately reference private terms and should
    # NOT trigger SKILL_CONTENT_PATTERNS checks.
    rules = tmp_path / "release-process.md"
    rules.write_text(
        "# Release Process\n\nRun `python tools/pre_publish_smoke.py` "
        "before pushing.\n",
        encoding="utf-8",
    )
    assert checker.check_files_pre_sync([rules]) == []


def test_cli_files_mode_exits_nonzero_on_leak(tmp_path: Path) -> None:
    skill = _write_skill(
        tmp_path, "cli_leak",
        "---\nname: cli_leak\n---\n# CLI Leak\n\n"
        "Run `python tools/pre_publish_smoke.py` before push.\n",
    )
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "check_no_private_leaks.py"),
         "--files", str(skill)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 1
    assert "ISSUES FOUND" in result.stdout


# ── Default mode tests ──────────────────────────────────────────────


def _make_public_dir(tmp_path: Path) -> Path:
    """Create a minimal seja-public/-like directory for default mode tests."""
    pub = tmp_path / "seja-public"
    pub.mkdir()
    return pub


def test_default_mode_passes_no_claude_dir(tmp_path: Path, monkeypatch) -> None:
    """Default mode passes when .claude/ does not exist and prose is clean."""
    pub = _make_public_dir(tmp_path)
    (pub / "README.md").write_text("# Public readme\n", encoding="utf-8")
    monkeypatch.setattr(checker, "PUBLIC_DIR", pub)
    assert checker.main([]) == 0


def test_default_mode_warns_claude_dir_exists(
    tmp_path: Path, monkeypatch, capsys,
) -> None:
    """Default mode emits WARNING when .claude/ exists on disk."""
    pub = _make_public_dir(tmp_path)
    (pub / ".claude").mkdir()
    (pub / ".claude" / "SKILL.md").write_text("# stale\n", encoding="utf-8")
    (pub / "README.md").write_text("# Public readme\n", encoding="utf-8")
    monkeypatch.setattr(checker, "PUBLIC_DIR", pub)
    rc = checker.main([])
    out = capsys.readouterr().out
    assert rc == 0  # warning is non-fatal
    assert "WARNING" in out
    assert ".claude" in out
    assert "PASS (with warnings)" in out


def test_default_mode_ignores_markers_inside_stale_claude(
    tmp_path: Path, monkeypatch,
) -> None:
    """Priv-only markers inside stale .claude/ do NOT fail default mode."""
    pub = _make_public_dir(tmp_path)
    claude = pub / ".claude" / "skills" / "check"
    claude.mkdir(parents=True)
    (claude / "SKILL.md").write_text(
        "<!-- priv-only-start -->\nSecret\n<!-- priv-only-end -->\n",
        encoding="utf-8",
    )
    (pub / "README.md").write_text("# Clean readme\n", encoding="utf-8")
    monkeypatch.setattr(checker, "PUBLIC_DIR", pub)
    # Should pass (with warning about .claude existing), NOT fail on
    # the markers inside .claude/.
    rc = checker.main([])
    assert rc == 0


def test_default_mode_detects_marker_in_docs(
    tmp_path: Path, monkeypatch, capsys,
) -> None:
    """Default mode catches priv-only markers in docs/ .md files."""
    pub = _make_public_dir(tmp_path)
    docs = pub / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text(
        "# Guide\n\n<!-- priv-only-start -->\nSecret\n<!-- priv-only-end -->\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(checker, "PUBLIC_DIR", pub)
    rc = checker.main([])
    out = capsys.readouterr().out
    assert rc == 1
    assert "ISSUES FOUND" in out
    assert "priv-only marker" in out


def test_default_mode_detects_marker_in_toplevel_md(
    tmp_path: Path, monkeypatch, capsys,
) -> None:
    """Default mode catches priv-only markers in top-level *.md files."""
    pub = _make_public_dir(tmp_path)
    (pub / "CHANGELOG.md").write_text(
        "# Changelog\n\n<!-- priv-only-start -->\nPrivate note\n"
        "<!-- priv-only-end -->\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(checker, "PUBLIC_DIR", pub)
    rc = checker.main([])
    out = capsys.readouterr().out
    assert rc == 1
    assert "ISSUES FOUND" in out


def test_default_mode_skips_missing_public_dir(
    tmp_path: Path, monkeypatch, capsys,
) -> None:
    """Default mode returns 0 (SKIP) when PUBLIC_DIR does not exist."""
    monkeypatch.setattr(checker, "PUBLIC_DIR", tmp_path / "nonexistent")
    rc = checker.main([])
    out = capsys.readouterr().out
    assert rc == 0
    assert "SKIP" in out


# ── Candidate mode tests ────────────────────────────────────────────


def test_candidate_mode_clean(tmp_path: Path, capsys) -> None:
    """--candidate passes on a clean directory."""
    candidate = tmp_path / "publish-workspace"
    candidate.mkdir()
    claude = candidate / ".claude" / "skills" / "check"
    claude.mkdir(parents=True)
    (claude / "SKILL.md").write_text(
        "---\nname: check\n---\n# Check\n\nPublic only.\n",
        encoding="utf-8",
    )
    rc = checker.main(["--candidate", str(candidate)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "PASS" in out


def test_candidate_mode_detects_private_dir(tmp_path: Path, capsys) -> None:
    """--candidate catches private directories in the candidate tree."""
    candidate = tmp_path / "publish-workspace"
    priv = candidate / ".claude" / "skills" / "scripts" / "priv"
    priv.mkdir(parents=True)
    (priv / "secret.py").write_text("# private\n", encoding="utf-8")
    rc = checker.main(["--candidate", str(candidate)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "ISSUES FOUND" in out
    assert "priv" in out


def test_candidate_mode_detects_markers(tmp_path: Path, capsys) -> None:
    """--candidate catches priv-only markers in candidate .md files."""
    candidate = tmp_path / "publish-workspace"
    skill_dir = candidate / ".claude" / "skills" / "plan"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "# Plan\n\n<!-- priv-only-start -->\nSecret\n<!-- priv-only-end -->\n",
        encoding="utf-8",
    )
    rc = checker.main(["--candidate", str(candidate)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "priv-only marker" in out


def test_candidate_mode_detects_fingerprints(tmp_path: Path, capsys) -> None:
    """--candidate catches SKILL_CONTENT_PATTERNS in candidate SKILL.md."""
    candidate = tmp_path / "publish-workspace"
    skill_dir = candidate / ".claude" / "skills" / "check"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: check\n---\n# Check\n\n"
        "Run python tools/pre_publish_smoke.py before push.\n",
        encoding="utf-8",
    )
    rc = checker.main(["--candidate", str(candidate)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "ISSUES FOUND" in out


def test_candidate_mode_skips_nonexistent_dir(
    tmp_path: Path, capsys,
) -> None:
    """--candidate returns 0 (SKIP) for a nonexistent directory."""
    rc = checker.main(["--candidate", str(tmp_path / "nope")])
    out = capsys.readouterr().out
    assert rc == 0
    assert "SKIP" in out


# ── Helper function unit tests ──────────────────────────────────────


def test_collect_prose_md_only_toplevel_and_docs(tmp_path: Path) -> None:
    """_collect_prose_md returns top-level *.md and docs/**/*.md only."""
    (tmp_path / "README.md").write_text("# R\n", encoding="utf-8")
    docs = tmp_path / "docs" / "concepts"
    docs.mkdir(parents=True)
    (docs / "guide.md").write_text("# G\n", encoding="utf-8")
    # .claude/ should be excluded
    stale = tmp_path / ".claude" / "skills"
    stale.mkdir(parents=True)
    (stale / "SKILL.md").write_text("# S\n", encoding="utf-8")
    result = checker._collect_prose_md(tmp_path)
    names = [p.name for p in result]
    assert "README.md" in names
    assert "guide.md" in names
    assert "SKILL.md" not in names


def test_check_prose_markers_clean(tmp_path: Path) -> None:
    """_check_prose_markers returns empty on clean files."""
    f = tmp_path / "clean.md"
    f.write_text("# Clean\n\nNo markers here.\n", encoding="utf-8")
    assert checker._check_prose_markers([f], tmp_path) == []


def test_check_prose_markers_detects(tmp_path: Path) -> None:
    """_check_prose_markers catches markers."""
    f = tmp_path / "leaky.md"
    f.write_text(
        "# Leaky\n\n<!-- priv-only-start -->\nSecret\n<!-- priv-only-end -->\n",
        encoding="utf-8",
    )
    issues = checker._check_prose_markers([f], tmp_path)
    assert len(issues) == 2  # both start and end markers
    assert all("priv-only marker" in i for i in issues)
