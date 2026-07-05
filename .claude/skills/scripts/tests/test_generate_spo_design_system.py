"""Tests for generate_spo.py design system loading and CSS injection."""
from __future__ import annotations

from pathlib import Path

import pytest

import generate_spo as spo
from design_system import find_design_system


# ---------------------------------------------------------------------------
# _load_design_system
# ---------------------------------------------------------------------------

class TestLoadDesignSystem:

    def test_extracts_root_css_and_font_imports(self, tmp_path: Path):
        html = tmp_path / "ds.html"
        html.write_text(
            "<style>\n"
            "@import url('https://fonts.googleapis.com/css2?family=Inter');\n"
            ":root { --primary: #1a2b3c; --bg: #fff; }\n"
            "body { font-family: var(--primary); }\n"
            "</style>",
            encoding="utf-8",
        )
        result = spo._load_design_system(html)
        assert result is not None
        assert ":root" in result["root_css"]
        assert "--primary: #1a2b3c" in result["root_css"]
        assert len(result["font_imports"]) == 1
        assert "fonts.googleapis.com" in result["font_imports"][0]

    def test_returns_none_when_no_style_block(self, tmp_path: Path):
        html = tmp_path / "empty.html"
        html.write_text("<html><body>No styles</body></html>", encoding="utf-8")
        assert spo._load_design_system(html) is None

    def test_returns_none_when_no_root_block(self, tmp_path: Path):
        html = tmp_path / "noroot.html"
        html.write_text(
            "<style>body { margin: 0; }</style>",
            encoding="utf-8",
        )
        assert spo._load_design_system(html) is None


# ---------------------------------------------------------------------------
# Auto-detect integration (lightweight -- find_design_system tested in Step 4)
# ---------------------------------------------------------------------------

class TestAutoDetect:

    def test_find_design_system_locates_file(self, tmp_path: Path):
        pd = tmp_path / "product-design"
        pd.mkdir()
        ds_file = pd / "foo-design-system.html"
        ds_file.write_text("<html></html>", encoding="utf-8")
        assert find_design_system(tmp_path) == ds_file


# ---------------------------------------------------------------------------
# generate_html with design_system injection
# ---------------------------------------------------------------------------

_MINIMAL_DATA = {
    "meta": {
        "title": "Test",
        "locale": "en-US",
        "version_labels": {},
        "tracker_type": "",
        "languages": ["en-US"],
        "facets": [],
        "mode": "project",
    },
    "layers": [],
    "personas": [],
    "quality_criteria": [],
    "cards": [],
}


class TestGenerateHtmlDesignSystem:

    def test_injects_root_block_and_font_import(self):
        ds = {
            "root_css": ":root { --test-color: red; }",
            "font_imports": [
                "https://fonts.googleapis.com/css2?family=TestFont",
            ],
        }
        html = spo.generate_html(_MINIMAL_DATA, design_system=ds)
        assert ":root { --test-color: red; }" in html
        assert "@import url('https://fonts.googleapis.com/css2?family=TestFont');" in html

    def test_font_import_appears_before_root_block(self):
        ds = {
            "root_css": ":root { --x: 1; }",
            "font_imports": ["https://fonts.googleapis.com/css2?family=A"],
        }
        html = spo.generate_html(_MINIMAL_DATA, design_system=ds)
        import_pos = html.index("@import url(")
        root_pos = html.index(":root { --x: 1; }")
        assert import_pos < root_pos

    def test_no_injection_when_design_system_is_none(self):
        html = spo.generate_html(_MINIMAL_DATA, design_system=None)
        assert "@import url(" not in html


# ---------------------------------------------------------------------------
# ImportError fallback
# ---------------------------------------------------------------------------

class TestImportErrorFallback:

    def test_returns_none_when_ds_root_vars_is_none(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(spo, "_ds_root_vars", None)
        html = tmp_path / "ds.html"
        html.write_text(
            "<style>:root { --a: 1; }</style>",
            encoding="utf-8",
        )
        assert spo._load_design_system(html) is None
