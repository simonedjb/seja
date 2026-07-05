"""Tests for design_system.py -- CSS and design token extraction."""
from __future__ import annotations

from pathlib import Path

import pytest

from design_system import extract_css, extract_root_vars, find_design_system


# ---------------------------------------------------------------------------
# extract_css
# ---------------------------------------------------------------------------

class TestExtractCss:

    def test_single_style_block(self, tmp_path: Path):
        html = tmp_path / "single.html"
        html.write_text(
            "<html><head><style>body { color: red; }</style></head></html>",
            encoding="utf-8",
        )
        assert extract_css(html) == "body { color: red; }"

    def test_multiple_style_blocks_joined(self, tmp_path: Path):
        html = tmp_path / "multi.html"
        html.write_text(
            "<style>a { color: blue; }</style>"
            "<style>p { margin: 0; }</style>",
            encoding="utf-8",
        )
        result = extract_css(html)
        assert result == "a { color: blue; }\np { margin: 0; }"

    def test_no_style_block_returns_none(self, tmp_path: Path):
        html = tmp_path / "empty.html"
        html.write_text("<html><body>Hello</body></html>", encoding="utf-8")
        assert extract_css(html) is None

    def test_scoped_style_excluded(self, tmp_path: Path):
        html = tmp_path / "scoped.html"
        html.write_text(
            "<style scoped>.x { display: none; }</style>"
            "<style>body { font-size: 16px; }</style>",
            encoding="utf-8",
        )
        assert extract_css(html) == "body { font-size: 16px; }"

    def test_js_type_style_excluded(self, tmp_path: Path):
        html = tmp_path / "js.html"
        html.write_text(
            '<style type="text/javascript">var x = 1;</style>'
            "<style>h1 { font-weight: bold; }</style>",
            encoding="utf-8",
        )
        assert extract_css(html) == "h1 { font-weight: bold; }"

    def test_all_excluded_returns_none(self, tmp_path: Path):
        html = tmp_path / "only_scoped.html"
        html.write_text(
            "<style scoped>.x { display: none; }</style>",
            encoding="utf-8",
        )
        assert extract_css(html) is None


# ---------------------------------------------------------------------------
# extract_root_vars
# ---------------------------------------------------------------------------

class TestExtractRootVars:

    def test_returns_root_block(self, tmp_path: Path):
        html = tmp_path / "root.html"
        html.write_text(
            "<style>:root { --fg: #000; --bg: #fff; } body { color: var(--fg); }</style>",
            encoding="utf-8",
        )
        assert extract_root_vars(html) == ":root { --fg: #000; --bg: #fff; }"

    def test_no_root_block_returns_none(self, tmp_path: Path):
        html = tmp_path / "noroot.html"
        html.write_text(
            "<style>body { margin: 0; }</style>",
            encoding="utf-8",
        )
        assert extract_root_vars(html) is None

    def test_no_style_returns_none(self, tmp_path: Path):
        html = tmp_path / "plain.html"
        html.write_text("<html><body>No CSS</body></html>", encoding="utf-8")
        assert extract_root_vars(html) is None


# ---------------------------------------------------------------------------
# find_design_system
# ---------------------------------------------------------------------------

class TestFindDesignSystem:

    def test_finds_design_system_file(self, tmp_path: Path):
        pd = tmp_path / "product-design"
        pd.mkdir()
        ds_file = pd / "octo-design-system.html"
        ds_file.write_text("<html></html>", encoding="utf-8")
        assert find_design_system(tmp_path) == ds_file

    def test_returns_none_when_absent(self, tmp_path: Path):
        pd = tmp_path / "product-design"
        pd.mkdir()
        (pd / "overview.md").write_text("# Overview", encoding="utf-8")
        assert find_design_system(tmp_path) is None

    def test_returns_none_when_no_product_design_dir(self, tmp_path: Path):
        assert find_design_system(tmp_path) is None
