"""Tests for generate_framework_reference.py -- framework reference generator."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

import generate_framework_reference as gen

FIXTURE_ROOT = (
    Path(__file__).resolve().parent / "fixtures" / "generate_framework_reference"
)
FRAMEWORK_ROOT = FIXTURE_ROOT / "framework_root"
SCAN_OUTPUT = FIXTURE_ROOT / "scan_output.json"
EXPECTED_OUTPUT = FIXTURE_ROOT / "expected_output.md"

SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "generate_framework_reference.py"
)


# ---------------------------------------------------------------------------
# Discovery tests
# ---------------------------------------------------------------------------


def test_discover_skills_extracts_description():
    skills = gen.discover_skills(FRAMEWORK_ROOT)
    assert len(skills) == 1
    demo = skills[0]
    assert demo.name == "/demo"
    assert demo.purpose == "demo skill for tests"
    assert demo.kind == "Skills"
    assert demo.path == ".claude/skills/demo/SKILL.md"


def test_discover_scripts_skips_tests_dir():
    scripts = gen.discover_scripts(FRAMEWORK_ROOT)
    names = [s.name for s in scripts]
    assert "alpha.py" in names
    assert not any("test_alpha" in n for n in names)
    # Exactly one script should be discovered (alpha.py); tests/* excluded.
    assert names == ["alpha.py"]


def test_discover_agents_uses_frontmatter_description():
    agents = gen.discover_agents(FRAMEWORK_ROOT)
    assert len(agents) == 1
    agent = agents[0]
    assert agent.name == "demo-agent"
    assert agent.purpose == "demo agent for tests"


def test_discover_rules_falls_back_to_h1():
    rules = gen.discover_rules(FRAMEWORK_ROOT)
    assert len(rules) == 1
    rule = rules[0]
    assert rule.name == "demo-rule"
    # Frontmatter has no `description`, so purpose should be derived from H1 + lead.
    assert "Demo Rule" in rule.purpose
    assert "demo files" in rule.purpose


def test_discover_general_references_uses_h1_and_lead():
    refs = gen.discover_general_references(FRAMEWORK_ROOT)
    assert len(refs) == 1
    ref = refs[0]
    assert ref.name == "coding-standards"
    assert "Coding Standards" in ref.purpose
    assert "Small, focused functions" in ref.purpose


# ---------------------------------------------------------------------------
# Rendering tests
# ---------------------------------------------------------------------------


def _load_artifacts_with_mentions() -> list[gen.FrameworkArtifact]:
    artifacts = gen.discover_all(FRAMEWORK_ROOT)
    scan_payload = json.loads(SCAN_OUTPUT.read_text(encoding="utf-8"))
    gen._apply_mentions(artifacts, scan_payload)
    return artifacts


def test_render_primary_table_has_all_kinds():
    artifacts = _load_artifacts_with_mentions()
    rendered = gen.render_primary_table(artifacts)
    # Every kind present in the fixture should have a section header.
    for expected_kind in (
        "Skills",
        "Agents",
        "Rules",
        "Scripts",
        "General references",
        "Perspectives",
        "Templates",
    ):
        assert f"## {expected_kind}" in rendered, (
            f"missing section header for {expected_kind}"
        )
    # Kinds with zero artifacts in the fixture should be absent.
    assert "## Migrations" not in rendered
    assert "## Configs" not in rendered
    assert "## Onboarding" not in rendered
    assert "## Communication" not in rendered


def test_render_user_facing_surface_filters_orphans():
    artifacts = _load_artifacts_with_mentions()
    rendered = gen.render_user_facing_surface(artifacts, "fixture-docs")
    # Artifacts with mentions should appear.
    assert "/demo" in rendered
    assert "alpha.py" in rendered
    assert "coding-standards" in rendered
    # Orphans (no mentions) should NOT appear in the user-facing surface.
    assert "demo-agent" not in rendered
    assert "demo-rule" not in rendered
    assert "SEC" not in rendered
    assert "conventions" not in rendered


# ---------------------------------------------------------------------------
# CLI end-to-end tests
# ---------------------------------------------------------------------------


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
    )


def test_cli_golden_file_match():
    result = _run_cli(
        "--framework-root",
        str(FRAMEWORK_ROOT),
        "--scan-output",
        str(SCAN_OUTPUT),
        "--fixed-date",
        "2026-01-01T00:00:00Z",
        "--output",
        "-",
    )
    assert result.returncode == 0, result.stderr
    expected = EXPECTED_OUTPUT.read_text(encoding="utf-8")
    assert result.stdout == expected, (
        "golden file mismatch. To regenerate the golden file run:\n"
        f"  python {SCRIPT_PATH} --framework-root {FRAMEWORK_ROOT} "
        f"--scan-output {SCAN_OUTPUT} --fixed-date 2026-01-01T00:00:00Z "
        f"--output {EXPECTED_OUTPUT}"
    )


def test_cli_check_mode_detects_drift(tmp_path):
    golden = tmp_path / "framework-reference.md"
    golden.write_text("this is a mutated file\n", encoding="utf-8")
    result = _run_cli(
        "--framework-root",
        str(FRAMEWORK_ROOT),
        "--scan-output",
        str(SCAN_OUTPUT),
        "--fixed-date",
        "2026-01-01T00:00:00Z",
        "--output",
        str(golden),
        "--check",
    )
    assert result.returncode == 1
    assert "DRIFT" in result.stderr


def test_cli_check_mode_passes_on_match(tmp_path):
    golden = tmp_path / "framework-reference.md"
    # Regenerate the file via the CLI so the on-disk copy has matching
    # line endings for the current platform.
    write_result = _run_cli(
        "--framework-root",
        str(FRAMEWORK_ROOT),
        "--scan-output",
        str(SCAN_OUTPUT),
        "--fixed-date",
        "2026-01-01T00:00:00Z",
        "--output",
        str(golden),
    )
    assert write_result.returncode == 0, write_result.stderr

    result = _run_cli(
        "--framework-root",
        str(FRAMEWORK_ROOT),
        "--scan-output",
        str(SCAN_OUTPUT),
        "--fixed-date",
        "2026-01-01T00:00:00Z",
        "--output",
        str(golden),
        "--check",
    )
    assert result.returncode == 0, result.stderr


def test_missing_scan_output_and_missing_public_docs_errors(tmp_path):
    """Script exits 2 when neither --scan-output nor a valid public-docs-root exist."""
    # Use a framework root that has no seja-public/docs subdirectory and no
    # sibling ../seja/docs, so public-docs resolution fails.
    empty_root = tmp_path / "empty_framework"
    (empty_root / ".claude").mkdir(parents=True)
    result = _run_cli(
        "--framework-root",
        str(empty_root),
        "--output",
        "-",
    )
    assert result.returncode == 2
    assert "public-docs root" in result.stderr
