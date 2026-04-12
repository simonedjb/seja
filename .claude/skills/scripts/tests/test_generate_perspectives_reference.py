"""Tests for generate_perspectives_reference.py -- review-perspectives catalog."""
import subprocess
import sys
from pathlib import Path

import pytest

import generate_perspectives_reference as gen

SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "generate_perspectives_reference.py"
)


# ---------------------------------------------------------------------------
# Fixture builder
# ---------------------------------------------------------------------------


def _write_perspective(root: Path, stem: str, body: str) -> None:
    persp_dir = root / "_references" / "general" / "review-perspectives"
    persp_dir.mkdir(parents=True, exist_ok=True)
    (persp_dir / f"{stem}.md").write_text(body, encoding="utf-8")


@pytest.fixture
def tmp_framework(tmp_path: Path) -> Path:
    (tmp_path / ".claude").mkdir()
    _write_perspective(
        tmp_path,
        "sec",
        "# SEC -- Security\n"
        "\n"
        "## Essential\n"
        "\n"
        "- [P0] Does this change introduce or widen an attack surface?\n",
    )
    _write_perspective(
        tmp_path,
        "perf",
        "# PERF -- Performance\n"
        "\n"
        "- [P0] Are there N+1 queries or unbounded loops?\n",
    )
    _write_perspective(
        tmp_path,
        "arch",
        "# ARCH -- Architecture\n"
        "\n"
        "Follows the established layer boundaries.\n",
    )
    return tmp_path


@pytest.fixture
def tmp_framework_empty(tmp_path: Path) -> Path:
    (tmp_path / ".claude").mkdir()
    return tmp_path


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------


def test_emits_one_row_per_perspective_file(tmp_framework: Path):
    perspectives = gen.collect_perspectives(tmp_framework)
    assert len(perspectives) == 3
    tags = [p["tag"] for p in perspectives]
    assert tags == ["ARCH", "PERF", "SEC"]


def test_alphabetizes_by_tag(tmp_framework: Path):
    perspectives = gen.collect_perspectives(tmp_framework)
    rendered = gen.render_perspectives_reference(perspectives, "2026-04-11T00:00:00Z")
    assert rendered.index("`ARCH`") < rendered.index("`PERF`") < rendered.index("`SEC`")


def test_extracts_name_from_h1_after_dash(tmp_framework: Path):
    perspectives = gen.collect_perspectives(tmp_framework)
    by_tag = {p["tag"]: p for p in perspectives}
    assert by_tag["SEC"]["name"] == "Security"
    assert by_tag["PERF"]["name"] == "Performance"
    assert by_tag["ARCH"]["name"] == "Architecture"


def test_extracts_purpose_from_first_list_item(tmp_framework: Path):
    perspectives = gen.collect_perspectives(tmp_framework)
    by_tag = {p["tag"]: p for p in perspectives}
    assert "attack surface" in by_tag["SEC"]["purpose"]
    assert "N+1 queries" in by_tag["PERF"]["purpose"]
    # ARCH uses a paragraph (not a list), which should also work.
    assert "layer boundaries" in by_tag["ARCH"]["purpose"]


def test_missing_perspectives_directory_emits_placeholder(tmp_framework_empty: Path):
    perspectives = gen.collect_perspectives(tmp_framework_empty)
    assert perspectives == []
    rendered = gen.render_perspectives_reference(perspectives, "2026-04-11T00:00:00Z")
    assert "No review perspectives defined" in rendered


def test_golden_file_match_with_fixed_date(tmp_framework: Path):
    perspectives = gen.collect_perspectives(tmp_framework)
    rendered = gen.render_perspectives_reference(perspectives, "2026-04-11T00:00:00Z")
    assert "# SEJA review perspectives catalog" in rendered
    assert "Generated 2026-04-11T00:00:00Z" in rendered
    assert "| `ARCH` | Architecture |" in rendered


def test_check_mode_detects_drift(tmp_framework: Path, tmp_path: Path):
    output_path = tmp_path / "perspectives.md"
    output_path.write_text("stale\n", encoding="utf-8")
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
    output_path = tmp_path / "perspectives.md"
    gen.main(
        [
            "--framework-root",
            str(tmp_framework),
            "--output",
            str(output_path),
            "--fixed-date",
            "2026-04-11T00:00:00Z",
        ]
    )
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
    assert "# SEJA review perspectives catalog" in result.stdout
    assert "`SEC`" in result.stdout
