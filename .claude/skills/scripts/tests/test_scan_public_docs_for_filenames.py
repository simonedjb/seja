"""Tests for scan_public_docs_for_filenames.py -- framework-to-public-docs scanner."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

import scan_public_docs_for_filenames as scanner

FIXTURE_ROOT = (
    Path(__file__).resolve().parent / "fixtures" / "scan_public_docs"
)
FRAMEWORK_ROOT = FIXTURE_ROOT / "framework_root"
PUBLIC_DOCS_ROOT = FIXTURE_ROOT / "public_docs_root"

SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "scan_public_docs_for_filenames.py"
)


def _run_scanner(framework_root: Path, public_docs_root: Path) -> dict:
    """Run the scan end-to-end and return the parsed JSON payload."""
    framework_files = scanner.discover_framework_files(framework_root)
    public_docs = scanner.discover_public_docs(public_docs_root)
    mapping = scanner.scan_mentions(
        framework_root,
        public_docs_root,
        framework_files,
        public_docs,
    )
    return {
        "generated_at": "2026-04-11T00:00:00Z",
        "framework_root": framework_root.as_posix(),
        "public_docs_root": public_docs_root.as_posix(),
        "framework_files": mapping,
    }


def test_basic_scan_finds_basename_matches():
    """alpha.py is reported as mentioned in quickstart.md; advanced.md does not list it."""
    payload = _run_scanner(FRAMEWORK_ROOT, PUBLIC_DOCS_ROOT)
    alpha_key = ".claude/skills/scripts/alpha.py"
    assert alpha_key in payload["framework_files"]
    mentions = payload["framework_files"][alpha_key]["mentioned_in"]
    assert "quickstart.md" in mentions
    assert "how-to/advanced.md" not in mentions


def test_basic_scan_finds_relative_path_matches():
    """.claude/skills/foo/SKILL.md is mentioned in quickstart.md (via relative path)."""
    payload = _run_scanner(FRAMEWORK_ROOT, PUBLIC_DOCS_ROOT)
    skill_key = ".claude/skills/foo/SKILL.md"
    assert skill_key in payload["framework_files"]
    mentions = payload["framework_files"][skill_key]["mentioned_in"]
    assert "quickstart.md" in mentions


def test_basename_only_match():
    """coding.md is reported as mentioned in concepts.md even when only the basename appears."""
    payload = _run_scanner(FRAMEWORK_ROOT, PUBLIC_DOCS_ROOT)
    coding_key = "_references/general/coding.md"
    assert coding_key in payload["framework_files"]
    mentions = payload["framework_files"][coding_key]["mentioned_in"]
    assert "concepts.md" in mentions


def test_orphaned_framework_file_in_output():
    """A framework file with zero mentions still appears with an empty list."""
    payload = _run_scanner(FRAMEWORK_ROOT, PUBLIC_DOCS_ROOT)
    orphan_key = "_references/template/conventions.md"
    assert orphan_key in payload["framework_files"]
    assert payload["framework_files"][orphan_key]["mentioned_in"] == []


def test_json_output_schema():
    """Top-level JSON keys and per-entry keys match the documented schema."""
    rendered = scanner.render_json(
        FRAMEWORK_ROOT,
        PUBLIC_DOCS_ROOT,
        _run_scanner(FRAMEWORK_ROOT, PUBLIC_DOCS_ROOT)["framework_files"],
    )
    payload = json.loads(rendered)
    assert set(payload.keys()) == {
        "generated_at",
        "framework_root",
        "public_docs_root",
        "framework_files",
    }
    for entry in payload["framework_files"].values():
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
            "--framework-root",
            str(FRAMEWORK_ROOT),
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
    payload = _run_scanner(FRAMEWORK_ROOT, PUBLIC_DOCS_ROOT)
    for key in payload["framework_files"]:
        assert "__pycache__" not in key, f"found __pycache__ entry: {key}"
        assert not key.startswith(".claude/skills/scripts/tests/"), (
            f"found excluded tests entry: {key}"
        )
