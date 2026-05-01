"""Tests for generate_harness_reference.py -- harness reference generator."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

import generate_harness_reference as gen

FIXTURE_ROOT = (
    Path(__file__).resolve().parent / "fixtures" / "generate_harness_reference"
)
HARNESS_ROOT = FIXTURE_ROOT / "harness_root"
SCAN_OUTPUT = FIXTURE_ROOT / "scan_output.json"
EXPECTED_OUTPUT = FIXTURE_ROOT / "expected_output.md"

SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "generate_harness_reference.py"
)


# ---------------------------------------------------------------------------
# Discovery tests
# ---------------------------------------------------------------------------


def test_discover_skills_extracts_description():
    skills = gen.discover_skills(HARNESS_ROOT)
    assert len(skills) == 1
    demo = skills[0]
    assert demo.name == "/demo"
    assert demo.purpose == "demo skill for tests"
    assert demo.kind == "Skills"
    assert demo.path == ".claude/skills/demo/SKILL.md"


def test_discover_scripts_skips_tests_dir():
    scripts = gen.discover_scripts(HARNESS_ROOT)
    names = [s.name for s in scripts]
    assert "alpha.py" in names
    assert not any("test_alpha" in n for n in names)
    # Exactly one script should be discovered (alpha.py); tests/* excluded.
    assert names == ["alpha.py"]


def test_discover_agents_uses_frontmatter_description():
    agents = gen.discover_agents(HARNESS_ROOT)
    assert len(agents) == 1
    agent = agents[0]
    assert agent.name == "demo-agent"
    assert agent.purpose == "demo agent for tests"


def test_discover_rules_falls_back_to_h1():
    rules = gen.discover_rules(HARNESS_ROOT)
    assert len(rules) == 1
    rule = rules[0]
    assert rule.name == "demo-rule"
    # Frontmatter has no `description`, so purpose should be derived from H1 + lead.
    assert "Demo Rule" in rule.purpose
    assert "demo files" in rule.purpose


def test_discover_general_references_uses_h1_and_lead():
    refs = gen.discover_general_references(HARNESS_ROOT)
    assert len(refs) == 1
    ref = refs[0]
    assert ref.name == "coding-standards"
    assert "Coding Standards" in ref.purpose
    assert "Small, focused functions" in ref.purpose


# ---------------------------------------------------------------------------
# Rendering tests
# ---------------------------------------------------------------------------


def _load_artifacts_with_mentions() -> list[gen.HarnessArtifact]:
    artifacts = gen.discover_all(HARNESS_ROOT)
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
        "--harness-root",
        str(HARNESS_ROOT),
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
        f"  python {SCRIPT_PATH} --harness-root {HARNESS_ROOT} "
        f"--scan-output {SCAN_OUTPUT} --fixed-date 2026-01-01T00:00:00Z "
        f"--output {EXPECTED_OUTPUT}"
    )


def test_cli_check_mode_detects_drift(tmp_path):
    golden = tmp_path / "harness-reference.md"
    golden.write_text("this is a mutated file\n", encoding="utf-8")
    result = _run_cli(
        "--harness-root",
        str(HARNESS_ROOT),
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
    golden = tmp_path / "harness-reference.md"
    # Regenerate the file via the CLI so the on-disk copy has matching
    # line endings for the current platform.
    write_result = _run_cli(
        "--harness-root",
        str(HARNESS_ROOT),
        "--scan-output",
        str(SCAN_OUTPUT),
        "--fixed-date",
        "2026-01-01T00:00:00Z",
        "--output",
        str(golden),
    )
    assert write_result.returncode == 0, write_result.stderr

    result = _run_cli(
        "--harness-root",
        str(HARNESS_ROOT),
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
    # Use a harness root that has no seja-public/docs subdirectory and no
    # sibling ../seja/docs, so public-docs resolution fails.
    empty_root = tmp_path / "empty_harness"
    (empty_root / ".claude").mkdir(parents=True)
    result = _run_cli(
        "--harness-root",
        str(empty_root),
        "--output",
        "-",
    )
    assert result.returncode == 2
    assert "public-docs root" in result.stderr


# ---------------------------------------------------------------------------
# Bug-fix regression tests (plan-000456)
# ---------------------------------------------------------------------------


def test_docstring_with_bare_filename_first_line_returns_description(tmp_path):
    # regression test for migrations 0001/0002 (digit-leading) and for ordinary scripts (identifier-leading)
    # Sub-assertion A: digit-leading migration-style filename on line 1.
    digit_module = tmp_path / "0099_example.py"
    digit_module.write_text(
        '"""\n0099_example.py\n\nDoes the thing.\n"""\n',
        encoding="utf-8",
    )
    assert (
        gen._read_module_docstring_first_line(digit_module) == "Does the thing."
    )

    # Sub-assertion B: identifier-leading script-style filename on line 1.
    ident_module = tmp_path / "generate_foo.py"
    ident_module.write_text(
        '"""\ngenerate_foo.py\n\nDoes the other thing.\n"""\n',
        encoding="utf-8",
    )
    assert (
        gen._read_module_docstring_first_line(ident_module)
        == "Does the other thing."
    )


def test_self_reference_is_filtered_from_mentioned_in():
    """`reference/harness-reference.md` is removed from each artifact's mentioned_in."""
    artifact = gen.HarnessArtifact(
        kind="Skills",
        name="/demo",
        purpose="demo",
        path=".claude/skills/demo/SKILL.md",
    )
    scan_payload = {
        "harness_files": {
            ".claude/skills/demo/SKILL.md": {
                "basename": "SKILL.md",
                "mentioned_in": [
                    "reference/harness-reference.md",
                    "concepts.md",
                ],
            },
        },
    }
    gen._apply_mentions([artifact], scan_payload)
    assert artifact.mentioned_in == ["concepts.md"]


# ---------------------------------------------------------------------------
# _read_script_invocation_and_lifecycle unit tests (plan-000457 Step 7)
# ---------------------------------------------------------------------------


def _write_script(tmp_path: Path, name: str, body: str) -> Path:
    """Helper: write a toy .py file under tmp_path and return the path."""
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return p


def test_invocation_lifecycle_valid_single_role(tmp_path):
    path = _write_script(
        tmp_path,
        "m.py",
        '"""Purpose line.\n\nInvocation: user-cli\nLifecycle: active\n"""\n',
    )
    assert gen._read_script_invocation_and_lifecycle(path) == ("user-cli", "active")


def test_invocation_lifecycle_valid_multi_valued_preserves_spacing(tmp_path):
    path = _write_script(
        tmp_path,
        "m.py",
        '"""Purpose line.\n\nInvocation: skill-invoked, user-cli\nLifecycle: active\n"""\n',
    )
    # The original value must be preserved verbatim (comma + space), not reformatted.
    assert gen._read_script_invocation_and_lifecycle(path) == (
        "skill-invoked, user-cli",
        "active",
    )


def test_invocation_lifecycle_missing_invocation_returns_unspecified(tmp_path):
    path = _write_script(
        tmp_path,
        "m.py",
        '"""Purpose line.\n\nLifecycle: active\n"""\n',
    )
    assert gen._read_script_invocation_and_lifecycle(path) == (
        "unspecified",
        "unspecified",
    )


def test_invocation_lifecycle_missing_lifecycle_returns_unspecified(tmp_path):
    path = _write_script(
        tmp_path,
        "m.py",
        '"""Purpose line.\n\nInvocation: user-cli\n"""\n',
    )
    assert gen._read_script_invocation_and_lifecycle(path) == (
        "unspecified",
        "unspecified",
    )


def test_invocation_lifecycle_invalid_invocation_returns_invalid(tmp_path):
    path = _write_script(
        tmp_path,
        "m.py",
        '"""Purpose line.\n\nInvocation: user-cli-broken\nLifecycle: active\n"""\n',
    )
    assert gen._read_script_invocation_and_lifecycle(path) == ("invalid", "invalid")


def test_invocation_lifecycle_invalid_lifecycle_returns_invalid(tmp_path):
    path = _write_script(
        tmp_path,
        "m.py",
        '"""Purpose line.\n\nInvocation: user-cli\nLifecycle: banana\n"""\n',
    )
    assert gen._read_script_invocation_and_lifecycle(path) == ("invalid", "invalid")


def test_invocation_lifecycle_header_with_prose_between(tmp_path):
    # A sub-heading or regular paragraph between the purpose line and the header
    # fields should not defeat extraction: the regex is multiline, first-match-wins.
    path = _write_script(
        tmp_path,
        "m.py",
        (
            '"""Purpose line.\n'
            "\n"
            "## Comments\n"
            "\n"
            "Some explanatory prose about the script.\n"
            "\n"
            "Invocation: hook-ci\n"
            "Lifecycle: active\n"
            '"""\n'
        ),
    )
    assert gen._read_script_invocation_and_lifecycle(path) == ("hook-ci", "active")


def test_invocation_lifecycle_no_docstring_returns_unspecified(tmp_path):
    path = _write_script(
        tmp_path,
        "m.py",
        "def foo():\n    return 1\n",
    )
    # No docstring at all; must not raise and must return the sentinel tuple.
    assert gen._read_script_invocation_and_lifecycle(path) == (
        "unspecified",
        "unspecified",
    )


# ---------------------------------------------------------------------------
# Grouped Scripts rendering integration test (plan-000457 Step 7)
# ---------------------------------------------------------------------------


def _make_script_artifact(
    name: str,
    invocation: str,
    lifecycle: str,
    purpose: str = "toy script",
) -> gen.HarnessArtifact:
    return gen.HarnessArtifact(
        kind="Scripts",
        name=name,
        purpose=purpose,
        path=f".claude/skills/scripts/{name}",
        invocation=invocation,
        lifecycle=lifecycle,
    )


def test_grouped_scripts_rendering_covers_all_sub_sections_and_dual_role():
    """Integration test: render_harness_reference produces 4 sub-sections and
    a Dual-role cross-reference with correct bucket placement.

    This test builds ``HarnessArtifact`` instances directly (skipping
    discovery) to keep the diff minimal and isolate the rendering contract.
    """
    artifacts = [
        _make_script_artifact("alpha_user.py", "user-cli", "active"),
        _make_script_artifact("beta_migration.py", "user-cli", "one-shot"),
        _make_script_artifact("gamma_helper.py", "skill-invoked", "active"),
        _make_script_artifact("delta_hook.py", "hook-ci", "active"),
        _make_script_artifact(
            "epsilon_dual.py", "skill-invoked, user-cli", "active"
        ),
    ]
    rendered = gen.render_harness_reference(
        artifacts,
        public_docs_root="fixture-docs",
        generated_at="2026-01-01T00:00:00Z",
    )

    # All four Scripts sub-headings present, in fixed order.
    expected_order = [
        "### User-invocable",
        "### Skill- or agent-invoked",
        "### Hook and CI",
        "### Archived migrations",
    ]
    indices = [rendered.index(h) for h in expected_order]
    assert indices == sorted(indices), (
        f"sub-heading order violated: {expected_order} found at {indices}"
    )

    # Dual-role cross-reference sub-heading present.
    assert "### Dual-role cross-reference" in rendered

    # Header row has 6 columns including Invoked by and Lifecycle.
    assert (
        "| Name | Purpose | Invoked by | Lifecycle | Path | Mentioned in |"
        in rendered
    )

    # Each single-role toy ends up in its expected bucket.
    #   user-cli/active    -> User-invocable
    #   user-cli/one-shot  -> Archived migrations (lifecycle-one-shot wins)
    #   skill-invoked      -> Skill- or agent-invoked
    #   hook-ci            -> Hook and CI
    ui_start = rendered.index("### User-invocable")
    sai_start = rendered.index("### Skill- or agent-invoked")
    hc_start = rendered.index("### Hook and CI")
    am_start = rendered.index("### Archived migrations")
    xref_start = rendered.index("### Dual-role cross-reference")

    assert ui_start < sai_start < hc_start < am_start < xref_start

    ui_section = rendered[ui_start:sai_start]
    sai_section = rendered[sai_start:hc_start]
    hc_section = rendered[hc_start:am_start]
    am_section = rendered[am_start:xref_start]
    xref_section = rendered[xref_start:]

    assert "alpha_user.py" in ui_section
    assert "epsilon_dual.py" in ui_section  # primary bucket for dual-role
    assert "gamma_helper.py" in sai_section
    assert "delta_hook.py" in hc_section
    assert "beta_migration.py" in am_section

    # Dual-role bullet: epsilon appears, primary is User-invocable, with a
    # link back to Skill- or agent-invoked (the other bucket).
    assert "**epsilon_dual.py**" in xref_section
    assert "primary: User-invocable" in xref_section
    assert "see [Skill- or agent-invoked](#skill--or-agent-invoked)" in xref_section
