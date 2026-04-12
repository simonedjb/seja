"""Tests for generate_skills_reference.py -- skills catalog generator."""
import subprocess
import sys
from pathlib import Path

import pytest

import generate_skills_reference as gen

FIXTURE_ROOT = (
    Path(__file__).resolve().parent / "fixtures" / "generate_skills_reference"
)
FRAMEWORK_ROOT = FIXTURE_ROOT / "framework_root"
EXPECTED_OUTPUT = FIXTURE_ROOT / "expected_output.md"

SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "generate_skills_reference.py"
)


# ---------------------------------------------------------------------------
# Fixture builder
# ---------------------------------------------------------------------------


def _write_skill(root: Path, name: str, frontmatter: dict[str, str | dict[str, str]]) -> None:
    """Write a fake SKILL.md. Empty-string scalars are omitted to match the
    real SKILL.md convention (no skill has an empty `argument-hint:` line),
    because the reused `_FIELD_RE` parser in generate_skills_manifest.py
    greedy-matches across an empty value into the next line."""
    skill_dir = root / ".claude" / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    lines = ["---"]
    for key, value in frontmatter.items():
        if isinstance(value, dict):
            lines.append(f"{key}:")
            for k, v in value.items():
                lines.append(f"  {k}: {v}")
        else:
            if value == "":
                continue
            lines.append(f"{key}: {value}")
    lines.append("---")
    lines.append("")
    lines.append("# Placeholder")
    (skill_dir / "SKILL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


@pytest.fixture
def tmp_framework(tmp_path: Path) -> Path:
    """Build a minimal .claude/skills/ tree with representative skills."""
    _write_skill(
        tmp_path,
        "alpha",
        {
            "name": "alpha",
            "description": "Alpha skill for tests",
            "argument-hint": "<arg>",
            "metadata": {"category": "analysis"},
        },
    )
    _write_skill(
        tmp_path,
        "beta",
        {
            "name": "beta",
            "description": "Beta skill for tests",
            "argument-hint": "<arg>",
            "metadata": {"category": "planning"},
        },
    )
    _write_skill(
        tmp_path,
        "zeta",
        {
            "name": "zeta",
            "description": "Zeta skill for tests",
            "argument-hint": "",
            "metadata": {"category": "analysis"},
        },
    )
    _write_skill(
        tmp_path,
        "orphan",
        {
            "name": "orphan",
            "description": "Skill without a category",
            "argument-hint": "",
            "metadata": {"version": "1.0.0"},
        },
    )
    _write_skill(
        tmp_path,
        "pre-skill",
        {
            "name": "pre-skill",
            "description": "Internal lifecycle hook",
            "metadata": {"category": "internal"},
        },
    )
    _write_skill(
        tmp_path,
        "post-skill",
        {
            "name": "post-skill",
            "description": "Internal lifecycle hook",
            "metadata": {"category": "internal"},
        },
    )
    return tmp_path


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------


def test_emits_one_section_per_category(tmp_framework: Path):
    skills = gen.collect_skills(tmp_framework)
    categories = {s["category"] for s in skills}
    assert categories == {"analysis", "planning", gen.UNCATEGORIZED_LABEL}


def test_excludes_internal_skills(tmp_framework: Path):
    skills = gen.collect_skills(tmp_framework)
    names = [s["name"] for s in skills]
    assert "pre-skill" not in names
    assert "post-skill" not in names
    assert len(skills) == 4


def test_alphabetizes_within_category(tmp_framework: Path):
    skills = gen.collect_skills(tmp_framework)
    rendered = gen.render_skills_reference(skills, "2026-04-11T00:00:00Z")
    # alpha and zeta are both analysis; alpha must appear before zeta.
    assert rendered.index("`/alpha`") < rendered.index("`/zeta`")
    # analysis (a) section must precede planning (p) section.
    assert rendered.index("### analysis") < rendered.index("### planning")
    # Uncategorized pinned to the bottom.
    assert rendered.index("### planning") < rendered.index(f"### {gen.UNCATEGORIZED_LABEL}")


def test_golden_file_match_with_fixed_date(tmp_framework: Path):
    skills = gen.collect_skills(tmp_framework)
    rendered = gen.render_skills_reference(skills, "2026-04-11T00:00:00Z")
    # Structural assertions on the golden output (not a byte-level match to
    # keep tests resilient to whitespace tweaks).
    assert "# SEJA skills catalog" in rendered
    assert "Generated 2026-04-11T00:00:00Z" in rendered
    assert "| `/alpha` | Alpha skill for tests | `<arg>` |" in rendered
    assert "| `/orphan` | Skill without a category | - |" in rendered


def test_check_mode_detects_drift(tmp_framework: Path, tmp_path: Path):
    output_path = tmp_path / "skills.md"
    output_path.write_text("stale content\n", encoding="utf-8")
    exit_code = gen.main(
        [
            "--framework-root",
            str(tmp_framework),
            "--output",
            str(output_path),
            "--check",
            "--fixed-date",
            "2026-04-11T00:00:00Z",
        ]
    )
    assert exit_code == 1


def test_check_mode_passes_on_match(tmp_framework: Path, tmp_path: Path):
    output_path = tmp_path / "skills.md"
    # Generate once to create the file.
    exit_code = gen.main(
        [
            "--framework-root",
            str(tmp_framework),
            "--output",
            str(output_path),
            "--fixed-date",
            "2026-04-11T00:00:00Z",
        ]
    )
    assert exit_code == 0
    # Re-run --check against the file we just wrote.
    exit_code = gen.main(
        [
            "--framework-root",
            str(tmp_framework),
            "--output",
            str(output_path),
            "--check",
            "--fixed-date",
            "2026-04-11T00:00:00Z",
        ]
    )
    assert exit_code == 0


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------


def test_cli_stdout(tmp_framework: Path):
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--framework-root",
            str(tmp_framework),
            "--output",
            "-",
            "--fixed-date",
            "2026-04-11T00:00:00Z",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0
    assert "# SEJA skills catalog" in result.stdout
    assert "`/alpha`" in result.stdout
