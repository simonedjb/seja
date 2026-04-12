"""Tests for generate_changelog_data.py -- framework changelog data extraction."""
from __future__ import annotations

import json
import subprocess
import textwrap
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import generate_changelog_data as gen


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_changelog(tmp_path: Path) -> Path:
    """Create a minimal changelog file for testing."""
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(
        textwrap.dedent("""\
            # SEJA-Claude Changelog

            ## [2.8.4] -- 2026-04-11 12:00 UTC

            ### Added
            - Something new

            ## [2.8.3] -- 2026-04-10 23:55 UTC

            ### Added
            - Something older
        """),
        encoding="utf-8",
    )
    return changelog


@pytest.fixture
def tmp_changelog_no_version(tmp_path: Path) -> Path:
    """Create a changelog with no version heading."""
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("# Changelog\n\nNo versions yet.\n", encoding="utf-8")
    return changelog


# ---------------------------------------------------------------------------
# find_baseline_commit
# ---------------------------------------------------------------------------


def test_find_baseline_parses_latest_version(tmp_changelog, monkeypatch):
    """find_baseline_commit extracts the first (latest) version heading."""
    fake_result = MagicMock()
    fake_result.stdout = "abc1234def5678\n"

    monkeypatch.setattr(
        gen.subprocess, "run",
        lambda *a, **kw: fake_result,
    )

    version, sha = gen.find_baseline_commit(tmp_changelog)
    assert version == "2.8.4"
    assert sha == "abc1234def5678"


def test_find_baseline_raises_on_no_version(tmp_changelog_no_version, monkeypatch):
    """find_baseline_commit raises ValueError when no version heading exists."""
    with pytest.raises(ValueError, match="No version heading"):
        gen.find_baseline_commit(tmp_changelog_no_version)


def test_find_baseline_raises_on_no_git_history(tmp_changelog, monkeypatch):
    """find_baseline_commit raises ValueError when git log returns empty."""
    fake_result = MagicMock()
    fake_result.stdout = ""

    monkeypatch.setattr(
        gen.subprocess, "run",
        lambda *a, **kw: fake_result,
    )

    with pytest.raises(ValueError, match="No git history"):
        gen.find_baseline_commit(tmp_changelog)


# ---------------------------------------------------------------------------
# get_commits_since
# ---------------------------------------------------------------------------


def test_get_commits_since_parses_tab_separated(monkeypatch):
    """get_commits_since returns list of {hash, subject} dicts."""
    fake_result = MagicMock()
    fake_result.stdout = (
        "abc1234\tplan-000310: add companion workspace\n"
        "def5678\tfix: stamp-based interval gating\n"
        "ghi9012\tchore: remove completed plan files\n"
    )
    monkeypatch.setattr(gen.subprocess, "run", lambda *a, **kw: fake_result)

    commits = gen.get_commits_since("baseline123")
    assert len(commits) == 3
    assert commits[0] == {"hash": "abc1234", "subject": "plan-000310: add companion workspace"}
    assert commits[2] == {"hash": "ghi9012", "subject": "chore: remove completed plan files"}


def test_get_commits_since_handles_empty(monkeypatch):
    """get_commits_since returns empty list when no commits."""
    fake_result = MagicMock()
    fake_result.stdout = ""
    monkeypatch.setattr(gen.subprocess, "run", lambda *a, **kw: fake_result)

    commits = gen.get_commits_since("baseline123")
    assert commits == []


# ---------------------------------------------------------------------------
# get_file_changes
# ---------------------------------------------------------------------------


def test_get_file_changes_added(monkeypatch):
    """get_file_changes with filter A returns added file paths."""
    fake_result = MagicMock()
    fake_result.stdout = "new_file.py\nanother_file.md\n"
    monkeypatch.setattr(gen.subprocess, "run", lambda *a, **kw: fake_result)

    files = gen.get_file_changes("baseline123", "A")
    assert files == ["new_file.py", "another_file.md"]


def test_get_file_changes_renamed(monkeypatch):
    """get_file_changes with filter R parses rename tab format."""
    fake_result = MagicMock()
    fake_result.stdout = "R100\told_name.md\tnew_name.md\n"
    monkeypatch.setattr(gen.subprocess, "run", lambda *a, **kw: fake_result)

    files = gen.get_file_changes("baseline123", "R")
    assert files == ["old_name.md -> new_name.md"]


def test_get_file_changes_empty(monkeypatch):
    """get_file_changes returns empty list when no changes."""
    fake_result = MagicMock()
    fake_result.stdout = ""
    monkeypatch.setattr(gen.subprocess, "run", lambda *a, **kw: fake_result)

    files = gen.get_file_changes("baseline123", "D")
    assert files == []


# ---------------------------------------------------------------------------
# group_commits
# ---------------------------------------------------------------------------


def test_group_commits_by_prefix():
    """group_commits groups commits by their prefix."""
    commits = [
        {"hash": "a", "subject": "plan-000310: something"},
        {"hash": "b", "subject": "plan-000310: another thing"},
        {"hash": "c", "subject": "fix: a bug"},
        {"hash": "d", "subject": "advisory-000311: audit"},
        {"hash": "e", "subject": "random commit message"},
    ]
    groups = gen.group_commits(commits)
    group_map = {g["prefix"]: g["commits"] for g in groups}

    assert "plan-000310" in group_map
    assert len(group_map["plan-000310"]) == 2
    assert "fix:" in group_map
    assert len(group_map["fix:"]) == 1
    assert "advisory-000311" in group_map
    assert "other" in group_map
    assert len(group_map["other"]) == 1


def test_group_commits_empty():
    """group_commits returns empty list for no commits."""
    assert gen.group_commits([]) == []


# ---------------------------------------------------------------------------
# suggest_version
# ---------------------------------------------------------------------------


def test_suggest_version_minor_for_plans():
    """suggest_version bumps minor when plans are present."""
    groups = [{"prefix": "plan-000310", "commits": []}]
    assert gen.suggest_version("2.8.4", groups, []) == "2.9.0"


def test_suggest_version_minor_for_features():
    """suggest_version bumps minor when feat: commits are present."""
    groups = [{"prefix": "feat:", "commits": []}]
    assert gen.suggest_version("2.8.4", groups, []) == "2.9.0"


def test_suggest_version_minor_for_new_skills():
    """suggest_version bumps minor when new SKILL.md files are added."""
    groups = [{"prefix": "chore:", "commits": []}]
    files_added = [".claude/skills/reflect/SKILL.md"]
    assert gen.suggest_version("2.8.4", groups, files_added) == "2.9.0"


def test_suggest_version_patch_for_fixes_only():
    """suggest_version bumps patch when only fixes and chores."""
    groups = [
        {"prefix": "fix:", "commits": []},
        {"prefix": "chore:", "commits": []},
    ]
    assert gen.suggest_version("2.8.4", groups, []) == "2.8.5"


# ---------------------------------------------------------------------------
# count helpers (integration with filesystem)
# ---------------------------------------------------------------------------


def test_count_scripts_counts_py_files(tmp_path, monkeypatch):
    """count_scripts counts .py files in .claude/skills/scripts/."""
    scripts_dir = tmp_path / ".claude" / "skills" / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "alpha.py").write_text("pass")
    (scripts_dir / "beta.py").write_text("pass")
    (scripts_dir / "tests").mkdir()
    (scripts_dir / "tests" / "test_alpha.py").write_text("pass")

    monkeypatch.setattr(gen, "REPO_ROOT", tmp_path)
    assert gen.count_scripts() == 2  # excludes tests/ subdirectory files


def test_count_test_functions(tmp_path, monkeypatch):
    """count_test_functions counts def test_ functions across test files."""
    tests_dir = tmp_path / ".claude" / "skills" / "scripts" / "tests"
    tests_dir.mkdir(parents=True)
    (tests_dir / "test_one.py").write_text(
        "def test_a():\n    pass\n\ndef test_b():\n    pass\n"
    )
    (tests_dir / "test_two.py").write_text(
        "def test_c():\n    pass\n"
    )

    monkeypatch.setattr(gen, "REPO_ROOT", tmp_path)
    assert gen.count_test_functions() == 3


def test_count_skills(tmp_path, monkeypatch):
    """count_skills counts SKILL.md files."""
    skills_dir = tmp_path / ".claude" / "skills"
    (skills_dir / "plan").mkdir(parents=True)
    (skills_dir / "plan" / "SKILL.md").write_text("---\nname: plan\n---")
    (skills_dir / "check").mkdir(parents=True)
    (skills_dir / "check" / "SKILL.md").write_text("---\nname: check\n---")

    monkeypatch.setattr(gen, "REPO_ROOT", tmp_path)
    assert gen.count_skills() == 2


def test_count_agents(tmp_path, monkeypatch):
    """count_agents counts .md files in .claude/agents/."""
    agents_dir = tmp_path / ".claude" / "agents"
    agents_dir.mkdir(parents=True)
    (agents_dir / "code-reviewer.md").write_text("# Agent")
    (agents_dir / "plan-reviewer.md").write_text("# Agent")

    monkeypatch.setattr(gen, "REPO_ROOT", tmp_path)
    assert gen.count_agents() == 2


# ---------------------------------------------------------------------------
# JSON output structure
# ---------------------------------------------------------------------------


def test_json_output_has_required_keys(tmp_changelog, monkeypatch):
    """generate_changelog_data returns all required top-level keys."""
    # Mock all git calls
    call_count = {"n": 0}

    def fake_run(*args, **kwargs):
        call_count["n"] += 1
        result = MagicMock()
        cmd = args[0] if args else kwargs.get("args", [])
        if isinstance(cmd, list) and "log" in cmd and "--format=%H" in cmd:
            result.stdout = "abc1234\n"
        elif isinstance(cmd, list) and "log" in cmd:
            result.stdout = "abc\tplan-000310: something\n"
        elif isinstance(cmd, list) and "diff" in cmd:
            result.stdout = ""
        else:
            result.stdout = ""
        return result

    monkeypatch.setattr(gen.subprocess, "run", fake_run)
    monkeypatch.setattr(gen, "REPO_ROOT", tmp_changelog.parent)

    # Create minimal framework structure
    scripts_dir = tmp_changelog.parent / ".claude" / "skills" / "scripts"
    scripts_dir.mkdir(parents=True)

    data = gen.generate_changelog_data(tmp_changelog)

    required_keys = {
        "since_version", "since_commit", "commit_count",
        "commit_groups", "counts", "files_added",
        "files_deleted", "files_renamed", "suggested_version",
    }
    assert required_keys == set(data.keys())
    assert data["since_version"] == "2.8.4"
    assert isinstance(data["commit_groups"], list)
    assert isinstance(data["counts"], dict)
