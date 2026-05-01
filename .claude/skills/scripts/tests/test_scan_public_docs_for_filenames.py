"""Tests for scan_public_docs_for_filenames.py -- harness-to-public-docs scanner."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

import scan_public_docs_for_filenames as scanner

FIXTURE_ROOT = (
    Path(__file__).resolve().parent / "fixtures" / "scan_public_docs"
)
HARNESS_ROOT = FIXTURE_ROOT / "harness_root"
PUBLIC_DOCS_ROOT = FIXTURE_ROOT / "public_docs_root"

SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "scan_public_docs_for_filenames.py"
)


def _run_scanner(harness_root: Path, public_docs_root: Path) -> dict:
    """Run the scan end-to-end and return the parsed JSON payload."""
    harness_files = scanner.discover_harness_files(harness_root)
    public_docs = scanner.discover_public_docs(public_docs_root)
    mapping = scanner.scan_mentions(
        harness_root,
        public_docs_root,
        harness_files,
        public_docs,
    )
    return {
        "generated_at": "2026-04-11T00:00:00Z",
        "harness_root": harness_root.as_posix(),
        "public_docs_root": public_docs_root.as_posix(),
        "harness_files": mapping,
    }


def test_basic_scan_finds_basename_matches():
    """alpha.py is reported as mentioned in quickstart.md; advanced.md does not list it."""
    payload = _run_scanner(HARNESS_ROOT, PUBLIC_DOCS_ROOT)
    alpha_key = ".claude/skills/scripts/alpha.py"
    assert alpha_key in payload["harness_files"]
    mentions = payload["harness_files"][alpha_key]["mentioned_in"]
    assert "quickstart.md" in mentions
    assert "how-to/advanced.md" not in mentions


def test_basic_scan_finds_relative_path_matches():
    """.claude/skills/foo/SKILL.md is mentioned in quickstart.md (via relative path)."""
    payload = _run_scanner(HARNESS_ROOT, PUBLIC_DOCS_ROOT)
    skill_key = ".claude/skills/foo/SKILL.md"
    assert skill_key in payload["harness_files"]
    mentions = payload["harness_files"][skill_key]["mentioned_in"]
    assert "quickstart.md" in mentions


def test_basename_only_match():
    """coding.md is reported as mentioned in concepts.md even when only the basename appears."""
    payload = _run_scanner(HARNESS_ROOT, PUBLIC_DOCS_ROOT)
    coding_key = ".claude/references/general/coding.md"
    assert coding_key in payload["harness_files"]
    mentions = payload["harness_files"][coding_key]["mentioned_in"]
    assert "concepts.md" in mentions


def test_orphaned_harness_file_in_output():
    """A harness file with zero mentions still appears with an empty list."""
    payload = _run_scanner(HARNESS_ROOT, PUBLIC_DOCS_ROOT)
    orphan_key = ".claude/references/template/conventions.md"
    assert orphan_key in payload["harness_files"]
    assert payload["harness_files"][orphan_key]["mentioned_in"] == []


def test_json_output_schema():
    """Top-level JSON keys and per-entry keys match the documented schema."""
    rendered = scanner.render_json(
        HARNESS_ROOT,
        PUBLIC_DOCS_ROOT,
        _run_scanner(HARNESS_ROOT, PUBLIC_DOCS_ROOT)["harness_files"],
    )
    payload = json.loads(rendered)
    assert set(payload.keys()) == {
        "generated_at",
        "harness_root",
        "public_docs_root",
        "harness_files",
    }
    for entry in payload["harness_files"].values():
        assert set(entry.keys()) == {"basename", "mentioned_in"}
        assert isinstance(entry["basename"], str)
        assert isinstance(entry["mentioned_in"], list)


def test_missing_public_docs_root_errors(tmp_path):
    """Script exits with code 2 and prints a clear error when --public-docs-root is missing."""
    missing = tmp_path / "does-not-exist"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--harness-root",
            str(HARNESS_ROOT),
            "--public-docs-root",
            str(missing),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "public-docs root does not exist" in result.stderr


def test_excludes_pycache_and_tests():
    """`.claude/skills/scripts/tests/` and `__pycache__/` never appear in output."""
    payload = _run_scanner(HARNESS_ROOT, PUBLIC_DOCS_ROOT)
    for key in payload["harness_files"]:
        assert "__pycache__" not in key, f"found __pycache__ entry: {key}"
        assert not key.startswith(".claude/skills/scripts/tests/"), (
            f"found excluded tests entry: {key}"
        )


# ---------------------------------------------------------------------------
# Bug-fix regression tests (plan-000456)
# ---------------------------------------------------------------------------


def test_ambiguous_basename_does_not_match_on_basename_alone(tmp_path):
    """Ambiguous basenames (e.g. README.md) require a path-prefixed match."""
    # Build a synthetic harness layout with two nested README.md files. We
    # avoid placing one at the harness root because for a root file the
    # repo-relative path is identical to the basename, which makes the
    # path-vs-basename distinction unobservable.
    harness_root = tmp_path / "fw"
    (harness_root / ".claude" / "migrations").mkdir(parents=True)
    (harness_root / ".claude" / "migrations" / "README.md").write_text(
        "# migrations readme\n", encoding="utf-8"
    )
    (harness_root / ".claude" / "skills").mkdir(parents=True)
    (harness_root / ".claude" / "skills" / "README.md").write_text(
        "# skills readme\n", encoding="utf-8"
    )

    public_docs_root = tmp_path / "docs"
    public_docs_root.mkdir()
    # Doc that mentions only the bare basename `README.md` -- ambiguous.
    bare_doc = public_docs_root / "something.md"
    bare_doc.write_text(
        "See the README.md for setup details.\n", encoding="utf-8"
    )

    harness_files = [
        Path(".claude/migrations/README.md"),
        Path(".claude/skills/README.md"),
    ]
    public_docs = [Path("something.md")]
    mapping = scanner.scan_mentions(
        harness_root,
        public_docs_root,
        harness_files,
        public_docs,
    )
    # Basename-only match is suppressed for both ambiguous entries.
    assert mapping[".claude/migrations/README.md"]["mentioned_in"] == []
    assert mapping[".claude/skills/README.md"]["mentioned_in"] == []

    # Sub-assertion: the path-based match still fires when the doc cites the
    # repo-relative path verbatim.
    path_doc = public_docs_root / "verbatim.md"
    path_doc.write_text(
        "See `.claude/migrations/README.md` for migration history.\n",
        encoding="utf-8",
    )
    public_docs = [Path("something.md"), Path("verbatim.md")]
    mapping = scanner.scan_mentions(
        harness_root,
        public_docs_root,
        harness_files,
        public_docs,
    )
    assert "verbatim.md" in mapping[".claude/migrations/README.md"]["mentioned_in"]
    # The skills README still has no mention -- nobody cites its repo-relative
    # path; the ambiguous basename match remains suppressed.
    assert mapping[".claude/skills/README.md"]["mentioned_in"] == []
