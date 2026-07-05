"""Tests for md_to_html.py -- design system HTML dispatch and auto-detect."""
from __future__ import annotations

from pathlib import Path

import pytest

import md_to_html
from md_to_html import DEFAULT_CSS, parse_style_file


# ---------------------------------------------------------------------------
# HTML dispatch in parse_style_file
# ---------------------------------------------------------------------------

class TestHtmlDispatch:

    def test_html_with_style_block_returns_extracted_css(self, tmp_path: Path):
        html = tmp_path / "ds.html"
        html.write_text(
            "<html><head><style>body { color: navy; }</style></head></html>",
            encoding="utf-8",
        )
        result = parse_style_file(html)
        assert result["css"] == "body { color: navy; }"

    def test_html_without_style_block_falls_through_to_default(self, tmp_path: Path):
        html = tmp_path / "empty.html"
        html.write_text("<html><body>No styles</body></html>", encoding="utf-8")
        result = parse_style_file(html)
        assert result["css"] == DEFAULT_CSS

    def test_html_dispatch_preserves_other_defaults(self, tmp_path: Path):
        html = tmp_path / "ds.html"
        html.write_text("<style>h1 { margin: 0; }</style>", encoding="utf-8")
        result = parse_style_file(html)
        assert result["header"] == ""
        assert result["footer"] == ""
        assert result["engine"] == "python-markdown"
        assert result["pandoc_args"] == []


# ---------------------------------------------------------------------------
# ImportError fallback
# ---------------------------------------------------------------------------

class TestImportErrorFallback:

    def test_none_sentinel_falls_through_to_default(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(md_to_html, "_ds_extract_css", None)
        html = tmp_path / "ds.html"
        html.write_text("<style>p { padding: 1em; }</style>", encoding="utf-8")
        result = parse_style_file(html)
        assert result["css"] == DEFAULT_CSS


# ---------------------------------------------------------------------------
# Auto-detect fallback (main's logic tested piecewise)
# ---------------------------------------------------------------------------

class TestAutoDetect:

    def test_auto_detect_finds_design_system(self, tmp_path: Path, monkeypatch):
        pd = tmp_path / "product-design"
        pd.mkdir()
        ds = pd / "acme-design-system.html"
        ds.write_text(
            "<style>:root { --brand: coral; } nav { display: flex; }</style>",
            encoding="utf-8",
        )

        monkeypatch.setattr(md_to_html, "REPO_ROOT", tmp_path)

        style_path = tmp_path / "product-design" / "communication-style.md"
        style = parse_style_file(style_path)
        assert style["css"] == DEFAULT_CSS

        from design_system import find_design_system as _ds_find
        ds_path = _ds_find(tmp_path)
        assert ds_path is not None

        style = parse_style_file(ds_path)
        assert ":root { --brand: coral; }" in style["css"]
        assert "nav { display: flex; }" in style["css"]

    def test_no_style_source_returns_default(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(md_to_html, "REPO_ROOT", tmp_path)

        style_path = tmp_path / "product-design" / "communication-style.md"
        style = parse_style_file(style_path)
        assert style["css"] == DEFAULT_CSS

        from design_system import find_design_system as _ds_find
        assert _ds_find(tmp_path) is None


# ---------------------------------------------------------------------------
# Regression guard: .md-backed behaviour unchanged
# ---------------------------------------------------------------------------

class TestMarkdownStyleRegression:

    def test_md_style_file_extracts_css(self, tmp_path: Path):
        style_md = tmp_path / "communication-style.md"
        style_md.write_text(
            "## Visual Style\n\n```css\n"
            ".custom { font-size: 14px; }\n"
            "```\n",
            encoding="utf-8",
        )
        result = parse_style_file(style_md)
        assert result["css"] == ".custom { font-size: 14px; }"

    def test_md_style_file_extracts_header_and_footer(self, tmp_path: Path):
        style_md = tmp_path / "communication-style.md"
        style_md.write_text(
            "## Content Framing\n\n"
            "```html\n<header>Top</header>\n```\n\n"
            "```html\n<footer>Bottom</footer>\n```\n",
            encoding="utf-8",
        )
        result = parse_style_file(style_md)
        assert result["header"] == "<header>Top</header>"
        assert result["footer"] == "<footer>Bottom</footer>"

    def test_md_style_file_extracts_engine(self, tmp_path: Path):
        style_md = tmp_path / "communication-style.md"
        style_md.write_text(
            "## HTML Conversion\n\nengine: pandoc\n",
            encoding="utf-8",
        )
        result = parse_style_file(style_md)
        assert result["engine"] == "pandoc"
