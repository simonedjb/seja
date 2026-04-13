"""Tests for check_docs.py plugins added in plan-000283.

Covers ``framework-reference-coverage`` and ``lifecycle-fact-uniqueness``
plugins plus their module-level helpers. Fixtures live under
``tests/fixtures/check_docs/``. The generator module is stubbed via
``monkeypatch.setitem(sys.modules, ...)`` so tests do not depend on the real
``generate_framework_reference`` behavior.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

import check_docs

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "check_docs"
CLEAN = FIXTURES / "clean_framework"
DRIFT = FIXTURES / "drift_framework"
MISSING = FIXTURES / "missing_reference"
SHORT = FIXTURES / "short_paragraph_fixture"


def _make_generator_stub(render_output: str) -> types.ModuleType:
    """Build a fake ``generate_framework_reference`` module.

    ``discover_all`` returns an empty list and ``render_framework_reference``
    returns ``render_output`` verbatim so the drift check can be controlled.
    """
    mod = types.ModuleType("generate_framework_reference")

    def discover_all(root: Path):  # noqa: ARG001 - signature match
        return []

    def render_framework_reference(artifacts, public_docs_root, generated_at):  # noqa: ARG001
        return render_output

    mod.discover_all = discover_all
    mod.render_framework_reference = render_framework_reference
    return mod


def _stub_generator_matching(monkeypatch: pytest.MonkeyPatch, root: Path) -> None:
    """Stub the generator so its output matches the fixture's reference file.

    Used to force the regen-drift sub-check to report "in sync" for the clean
    fixture regardless of what the real generator would produce.
    """
    reference = root / "seja-public" / "docs" / "reference" / "framework-reference.md"
    text = reference.read_text(encoding="utf-8")
    stub = _make_generator_stub(text)
    monkeypatch.setitem(sys.modules, "generate_framework_reference", stub)


def _stub_generator_diverging(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub the generator so its output never matches (always drift)."""
    stub = _make_generator_stub("intentionally different text")
    monkeypatch.setitem(sys.modules, "generate_framework_reference", stub)


# ---------------------------------------------------------------------------
# plugin_framework_reference_coverage
# ---------------------------------------------------------------------------


def test_clean_framework_has_no_findings(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_generator_matching(monkeypatch, CLEAN)
    findings = check_docs.plugin_framework_reference_coverage(CLEAN, verbose=False)
    warnings = [f for f in findings if f.severity == "warning"]
    errors = [f for f in findings if f.severity == "error"]
    assert not warnings, f"unexpected warnings: {[f.message for f in warnings]}"
    assert not errors, f"unexpected errors: {[f.message for f in errors]}"


def test_coverage_flags_missing_file(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_generator_diverging(monkeypatch)
    findings = check_docs.plugin_framework_reference_coverage(DRIFT, verbose=False)
    coverage_hits = [
        f for f in findings
        if f.severity == "warning"
        and "ghost-agent.md" in f.message
        and "not mentioned" in f.message
    ]
    assert len(coverage_hits) == 1, (
        f"expected exactly one coverage warning for ghost-agent.md; got "
        f"{[f.message for f in findings]}"
    )


def test_nonexistent_target_is_flagged(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_generator_diverging(monkeypatch)
    findings = check_docs.plugin_framework_reference_coverage(DRIFT, verbose=False)
    hits = [
        f for f in findings
        if f.severity == "warning"
        and "deleted-rule.md" in f.message
        and "nonexistent file" in f.message
    ]
    assert len(hits) == 1, (
        f"expected one nonexistent-target warning for deleted-rule.md; got "
        f"{[f.message for f in findings]}"
    )


def test_cross_ref_missing_public_doc_is_flagged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _stub_generator_diverging(monkeypatch)
    findings = check_docs.plugin_framework_reference_coverage(DRIFT, verbose=False)
    hits = [
        f for f in findings
        if f.severity == "warning"
        and "missing.md" in f.message
        and "nonexistent public doc" in f.message
    ]
    assert len(hits) == 1, (
        f"expected one cross-ref warning for missing.md; got "
        f"{[f.message for f in findings]}"
    )


def test_missing_reference_file_degrades_gracefully(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _stub_generator_diverging(monkeypatch)
    findings = check_docs.plugin_framework_reference_coverage(MISSING, verbose=False)
    assert len(findings) == 1
    assert findings[0].severity == "info"
    assert "not found" in findings[0].message


def test_plugin_framework_reference_coverage_is_registered() -> None:
    assert "framework-reference-coverage" in check_docs._PLUGINS
    desc, func = check_docs._PLUGINS["framework-reference-coverage"]
    assert callable(func)
    assert "framework-reference" in desc.lower()


# ---------------------------------------------------------------------------
# plugin_lifecycle_fact_uniqueness
# ---------------------------------------------------------------------------


def test_clean_how_tos_have_no_findings() -> None:
    findings = check_docs.plugin_lifecycle_fact_uniqueness(CLEAN, verbose=False)
    warnings = [f for f in findings if f.severity == "warning"]
    assert not warnings, (
        f"clean how-tos should not trigger warnings; got "
        f"{[f.message for f in warnings]}"
    )


def test_duplicated_paragraphs_trigger_warning() -> None:
    findings = check_docs.plugin_lifecycle_fact_uniqueness(DRIFT, verbose=False)
    warnings = [f for f in findings if f.severity == "warning"]
    assert warnings, "drift fixture should trigger at least one warning"
    matches = [
        f for f in warnings
        if ("one.md" in f.path and "two.md" in f.message)
        or ("two.md" in f.path and "one.md" in f.message)
        or ("one.md" in f.message and "two.md" in f.message)
    ]
    assert matches, (
        f"expected a warning naming both one.md and two.md; got "
        f"{[(f.path, f.message) for f in warnings]}"
    )


def test_short_paragraphs_below_token_minimum_are_ignored() -> None:
    findings = check_docs.plugin_lifecycle_fact_uniqueness(SHORT, verbose=False)
    warnings = [f for f in findings if f.severity == "warning"]
    assert not warnings, (
        f"short paragraphs below the 8-token minimum should not be flagged; "
        f"got {[f.message for f in warnings]}"
    )


def test_missing_how_to_directory_degrades_gracefully() -> None:
    findings = check_docs.plugin_lifecycle_fact_uniqueness(MISSING, verbose=False)
    assert len(findings) == 1
    assert findings[0].severity == "info"
    assert "how-to" in findings[0].message


def test_plugin_lifecycle_fact_uniqueness_is_registered() -> None:
    assert "lifecycle-fact-uniqueness" in check_docs._PLUGINS
    desc, func = check_docs._PLUGINS["lifecycle-fact-uniqueness"]
    assert callable(func)
    assert "lifecycle" in desc.lower()


def test_before_you_start_paragraphs_excluded() -> None:
    """Paragraphs under 'Before you start' are prerequisite pointers, not
    duplicated facts. The plugin should exclude them from comparison even
    when they are identical across files (advisory-000359 R1)."""
    findings = check_docs.plugin_lifecycle_fact_uniqueness(DRIFT, verbose=False)
    warnings = [f for f in findings if f.severity == "warning"]
    before_warnings = [
        f for f in warnings if "Before you start" in f.message
    ]
    assert not before_warnings, (
        f"'Before you start' paragraphs should be excluded; got "
        f"{[f.message for f in before_warnings]}"
    )


def test_moderate_overlap_below_threshold_not_flagged(tmp_path: Path) -> None:
    """Paragraphs with 60-69% Jaccard overlap should not be flagged after
    the threshold was raised from 0.60 to 0.70 (advisory-000359 R2)."""
    how_to = tmp_path / "seja-public" / "docs" / "how-to"
    how_to.mkdir(parents=True)
    # Two paragraphs sharing ~65% tokens but not identical.
    (how_to / "alpha.md").write_text(
        "# Alpha\n\n## Step 1: Do the thing\n\n"
        "**Framework:** the harness records applied markers, flips status "
        "fields, propagates established dates, and writes journey lifecycle "
        "rotation events into the changelog ledger deterministically.\n",
        encoding="utf-8",
    )
    (how_to / "beta.md").write_text(
        "# Beta\n\n## Step 1: Do the thing\n\n"
        "**Framework:** the harness records applied markers, flips status "
        "fields, propagates validation timestamps, and writes entity "
        "permission updates into the audit trail deterministically.\n",
        encoding="utf-8",
    )
    findings = check_docs.plugin_lifecycle_fact_uniqueness(tmp_path, verbose=False)
    warnings = [f for f in findings if f.severity == "warning"]
    assert not warnings, (
        f"moderate overlap (~65%) should not trigger at 0.70 threshold; got "
        f"{[f.message for f in warnings]}"
    )


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------


def test_cli_dispatch_runs_both_plugins_by_name(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    """Invoke check_docs.main() with --plugins listing both new plugins.

    The clean fixture must exit 0 (after the generator stub aligns the
    regen-drift sub-check) and the drift fixture must exit 1.
    """
    # Clean fixture: stub so drift check reports "in sync".
    _stub_generator_matching(monkeypatch, CLEAN)
    monkeypatch.setattr(
        sys, "argv",
        [
            "check_docs.py",
            "--root", str(CLEAN),
            "--plugins", "framework-reference-coverage,lifecycle-fact-uniqueness",
        ],
    )
    rc_clean = check_docs.main()
    capsys.readouterr()
    assert rc_clean == 0, f"clean fixture expected exit 0, got {rc_clean}"

    # Drift fixture: force divergence so all drift classes fire.
    _stub_generator_diverging(monkeypatch)
    monkeypatch.setattr(
        sys, "argv",
        [
            "check_docs.py",
            "--root", str(DRIFT),
            "--plugins", "framework-reference-coverage,lifecycle-fact-uniqueness",
        ],
    )
    rc_drift = check_docs.main()
    capsys.readouterr()
    assert rc_drift == 1, f"drift fixture expected exit 1, got {rc_drift}"
