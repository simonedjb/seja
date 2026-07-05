"""Tests for check_retired_tokens.py — retired-token guard.

Retired tokens are constructed dynamically (split-literal concatenation) so this
test file's own source contains no static occurrence of them. That keeps the
real-tree guard green even though this file lives under `.claude/`.
"""
import sys

import pytest

import check_retired_tokens

# Built so no static substring of a retired token appears in this source.
TOKEN_CHECK_LOGS = "CHECK_" + "LOGS_DIR"
TOKEN_SKILL_CHECK = "skill" + ":" + "check"


@pytest.fixture
def fake_claude_tree(tmp_path, monkeypatch):
    """Point the guard at a tmp `.claude/` tree instead of the real one."""
    claude_dir = tmp_path / ".claude"
    (claude_dir / "skills").mkdir(parents=True)
    monkeypatch.setattr(check_retired_tokens, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(check_retired_tokens, "CLAUDE_DIR", claude_dir)
    monkeypatch.setattr(sys, "argv", ["check_retired_tokens.py"])
    return claude_dir


def test_clean_tree_exits_zero(fake_claude_tree, capsys):
    """A tree with no retired tokens exits 0."""
    (fake_claude_tree / "skills" / "SKILL.md").write_text(
        "This file references CRITIQUE_LOGS_DIR, the live variable.\n",
        encoding="utf-8",
    )
    rc = check_retired_tokens.main()
    assert rc == 0
    assert "PASS" in capsys.readouterr().out


def test_retired_conventions_var_exits_nonzero(fake_claude_tree, capsys):
    """A file containing the retired conventions variable fails and names file:line."""
    offender = fake_claude_tree / "skills" / "SKILL.md"
    offender.write_text(
        "line one\n"
        f"logs go to {TOKEN_CHECK_LOGS}/foo\n",
        encoding="utf-8",
    )
    rc = check_retired_tokens.main()
    assert rc == 1
    out = capsys.readouterr().out
    assert "skills/SKILL.md:2" in out.replace("\\", "/")
    assert TOKEN_CHECK_LOGS in out


def test_retired_skill_reference_exits_nonzero(fake_claude_tree, capsys):
    """A file containing the retired skill reference fails."""
    offender = fake_claude_tree / "skills" / "call-graph.md"
    offender.write_text(
        f"edge target {TOKEN_SKILL_CHECK} no longer resolves\n",
        encoding="utf-8",
    )
    rc = check_retired_tokens.main()
    assert rc == 1
    out = capsys.readouterr().out
    assert "call-graph.md:1" in out.replace("\\", "/")
    assert TOKEN_SKILL_CHECK in out


def test_scan_file_reports_line_and_token(fake_claude_tree):
    """scan_file returns (line_number, token) tuples."""
    f = fake_claude_tree / "skills" / "notes.md"
    f.write_text(f"clean\n{TOKEN_CHECK_LOGS}\n", encoding="utf-8")
    hits = check_retired_tokens.scan_file(f)
    assert hits == [(2, TOKEN_CHECK_LOGS)]
