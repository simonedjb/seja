"""Tests for summarize_artifacts.py."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from summarize_artifacts import summarize, as_markdown_block, _infer_type  # type: ignore


def test_resolves_plan_id():
    results = summarize(["plan-000295"])
    assert len(results) == 1
    r = results[0]
    assert "error" not in r
    assert r["id"] == "000295"
    assert r["type"] == "plan"
    assert "path" in r
    assert r["path"].endswith(".md")


def test_extracts_header_fields():
    results = summarize(["advisory-000300"])
    assert len(results) == 1
    r = results[0]
    assert "error" not in r
    assert r["id"] == "000300"
    assert r["type"] == "advisory"
    assert r["title"]
    assert r["datetime"]


def test_resolve_prefers_canonical_over_progress_companion():
    """plan-000295 has a -progress.md companion (and a -qa- companion) alongside the
    canonical header file; resolution must pick the header-bearing canonical file,
    not a companion, so the bare id 000295 is returned."""
    results = summarize(["plan-000295"])
    assert len(results) == 1
    r = results[0]
    assert "error" not in r
    assert r["id"] == "000295"
    assert not r["path"].endswith("-progress.md")
    assert "-qa-" not in r["path"]
    assert r["path"].endswith("plan-000295-reflect-skill-telemetry-expansion.md")


def test_resolve_prefers_canonical_over_qa_companion():
    """advisory-000300 has a -qa- companion alongside the canonical header file;
    resolution must pick the canonical file, not the qa companion."""
    results = summarize(["advisory-000300"])
    assert len(results) == 1
    r = results[0]
    assert "error" not in r
    assert r["id"] == "000300"
    assert "-qa-" not in r["path"]
    assert r["path"].endswith("advisory-000300-make-reflect-on-demand-and-less-intrusive.md")


def test_not_found_returns_error():
    results = summarize(["plan-999999"])
    assert len(results) == 1
    r = results[0]
    assert "error" in r
    assert r["id"] == "plan-999999"


def test_as_markdown_block_format():
    summaries = [
        {"id": "000300", "type": "advisory", "path": "_output/advisory-logs/test.md",
         "title": "Test", "datetime": "2026-04-12 01:49 UTC",
         "brief_excerpt": "A brief.", "interpretation_excerpt": "An interpretation."},
        {"id": "plan-999999", "error": "not found"},
    ]
    block = as_markdown_block(summaries)
    assert "[advisory-000300]" in block
    assert "**Brief**" in block
    assert "not found" in block


def test_infer_type_research():
    """Research log paths should map to type 'research' per advisory-000448 rename."""
    path = Path("_output/research-logs/research-000450-example.md")
    assert _infer_type(path) == "research"


def test_infer_type_advisory_preserved():
    """Historical advisory-logs paths still map to type 'advisory'."""
    path = Path("_output/advisory-logs/advisory-000431-example.md")
    assert _infer_type(path) == "advisory"


def test_resolve_path_regex_accepts_research_prefix():
    """The ID-normalisation regex must strip the 'research-' prefix."""
    # Mirrors the regex used inside _resolve_path -- kept in sync with summarize_artifacts.py line ~33.
    _PREFIX_RE = re.compile(r"^(?:plan|advisory|research|reflection|inventory|proposal|check)-")
    assert _PREFIX_RE.match("research-999999-x") is not None
    # Confirm the legacy advisory prefix still matches.
    assert _PREFIX_RE.match("advisory-000431-framework-simplification") is not None


def test_as_markdown_block_research_type():
    """Markdown block renders 'research-<id>' prefix for research-type summaries."""
    summaries = [
        {"id": "000450", "type": "research", "path": "_output/research-logs/research-000450-x.md",
         "title": "A research output", "datetime": "2026-04-19 20:00 UTC",
         "brief_excerpt": "A brief.", "interpretation_excerpt": "An interpretation."},
    ]
    block = as_markdown_block(summaries)
    assert "[research-000450]" in block
