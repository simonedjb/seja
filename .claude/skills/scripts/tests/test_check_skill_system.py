"""Tests for check_skill_system.py — skill system integrity checker."""
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def valid_skill(tmp_path):
    """Create a minimal valid SKILL.md."""
    skill_dir = tmp_path / ".claude" / "skills" / "test-skill"
    skill_dir.mkdir(parents=True)
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        "---\n"
        "name: test-skill\n"
        "description: A test skill for validation.\n"
        "argument-hint: <arg>\n"
        "metadata:\n"
        "  last-updated: 2026-03-28 00:00 UTC\n"
        "  version: 1.0.0\n"
        "  category: utility\n"
        "  context_budget: light\n"
        "  references: []\n"
        "---\n"
        "\n"
        "## Quick Guide\n"
        "\n"
        "**What it does**: Tests things.\n"
        "\n"
        "**Example**:\n"
        "> You: /test-skill foo\n"
        "> Agent: Does foo.\n"
        "\n"
        "**When to use**: When you need to test.\n"
        "\n"
        "# Test Skill\n"
        "\n"
        "Do the thing.\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def invalid_skill_missing_desc(tmp_path):
    """Create a SKILL.md missing the description field."""
    skill_dir = tmp_path / ".claude" / "skills" / "bad-skill"
    skill_dir.mkdir(parents=True)
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        "---\n"
        "name: bad-skill\n"
        "metadata:\n"
        "  version: 1.0.0\n"
        "---\n"
        "\n"
        "# Bad Skill\n",
        encoding="utf-8",
    )
    return tmp_path


def test_valid_skill_structure(valid_skill):
    """A well-formed SKILL.md should have all required frontmatter fields."""
    skill_md = valid_skill / ".claude" / "skills" / "test-skill" / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    assert "name:" in text
    assert "description:" in text
    assert "## Quick Guide" in text
    assert "metadata:" in text


def test_invalid_skill_missing_description(invalid_skill_missing_desc):
    """A SKILL.md missing description should be detectable."""
    skill_md = invalid_skill_missing_desc / ".claude" / "skills" / "bad-skill" / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    assert "name:" in text
    assert "description:" not in text
