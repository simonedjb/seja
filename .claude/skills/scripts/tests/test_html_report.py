"""Tests for html_report.py — directive preprocessing and HTML assembly."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from html_report import (
    _preprocess_directives,
    _process_callout,
    _process_card,
    _process_checklist,
    _process_collapsible,
    _process_columns,
    _process_svg,
    _generate_toc,
    convert,
)


# ---- Directive preprocessing tests ----

class TestCollapsible:
    def test_basic(self):
        md = ':::collapsible{title="Details"}\nSome content here.\n:::'
        result = _process_collapsible(md)
        assert '<details>' in result
        assert '<summary>Details</summary>' in result
        assert 'Some content here.' in result
        assert '</details>' in result

    def test_multiline_body(self):
        md = ':::collapsible{title="More"}\nLine 1\n\nLine 2\n:::'
        result = _process_collapsible(md)
        assert 'Line 1' in result
        assert 'Line 2' in result


class TestCallout:
    @pytest.mark.parametrize("ctype", ["info", "tip", "warning", "danger"])
    def test_types(self, ctype):
        md = f':::callout{{type="{ctype}"}}\nAlert text.\n:::'
        result = _process_callout(md)
        assert f'callout-{ctype}' in result
        assert 'Alert text.' in result

    def test_title_label(self):
        md = ':::callout{type="warning"}\nWatch out.\n:::'
        result = _process_callout(md)
        assert 'Warning' in result


class TestSvg:
    def test_passthrough(self):
        svg = '<svg width="100" height="100"><circle cx="50" cy="50" r="40"/></svg>'
        md = f':::svg\n{svg}\n:::'
        result = _process_svg(md)
        assert 'svg-container' in result
        assert svg in result

    def test_preserves_attributes(self):
        md = ':::svg\n<svg viewBox="0 0 200 200"><rect x="10" y="10" width="80" height="80"/></svg>\n:::'
        result = _process_svg(md)
        assert 'viewBox="0 0 200 200"' in result


class TestChecklist:
    def test_basic_items(self):
        md = ':::checklist{id="day-1"}\n- [ ] Task A\n- [ ] Task B\n- [ ] Task C\n:::'
        result = _process_checklist(md)
        assert 'data-checklist-id="day-1"' in result
        assert 'Task A' in result
        assert 'Task B' in result
        assert 'Task C' in result
        assert result.count('checklist-item') == 3

    def test_section_progress_label(self):
        md = ':::checklist{id="week-1"}\n- [ ] Item 1\n- [ ] Item 2\n:::'
        result = _process_checklist(md)
        assert '0 / 2' in result

    def test_section_title_from_id(self):
        md = ':::checklist{id="month-1"}\n- [ ] Item\n:::'
        result = _process_checklist(md)
        assert 'Month 1' in result


class TestColumns:
    def test_two_columns(self):
        md = ':::columns{count=2}\nLeft side\n---\nRight side\n:::'
        result = _process_columns(md)
        assert 'columns-2' in result
        assert 'Left side' in result
        assert 'Right side' in result
        assert result.count('class="column"') == 2

    def test_three_columns(self):
        md = ':::columns{count=3}\nA\n---\nB\n---\nC\n:::'
        result = _process_columns(md)
        assert 'columns-3' in result
        assert result.count('class="column"') == 3


class TestCard:
    def test_basic(self):
        md = ':::card{title="Component X"}\nDescription of X.\n:::'
        result = _process_card(md)
        assert 'class="card"' in result
        assert 'Component X' in result
        assert 'Description of X.' in result


# ---- Combined preprocessing ----

class TestPreprocessDirectives:
    def test_mixed_directives(self):
        md = (
            ':::callout{type="info"}\nNote here.\n:::\n\n'
            ':::collapsible{title="Expand"}\nHidden stuff.\n:::\n\n'
            ':::card{title="Box"}\nCard content.\n:::'
        )
        result = _preprocess_directives(md)
        assert 'callout-info' in result
        assert '<details>' in result
        assert 'class="card"' in result

    def test_plain_text_unchanged(self):
        md = '# Hello\n\nJust regular markdown.\n\n- item 1\n- item 2'
        result = _preprocess_directives(md)
        assert result == md


# ---- ToC generation ----

class TestTocGeneration:
    def test_basic_toc(self):
        html = '<h2 id="intro">Introduction</h2><h3 id="sub">Subsection</h3>'
        toc = _generate_toc(html)
        assert 'toc-sidebar' in toc
        assert '#intro' in toc
        assert '#sub' in toc

    def test_empty_no_headings(self):
        assert _generate_toc('<p>No headings</p>') == ''


# ---- Full conversion ----

class TestConvert:
    def test_self_contained(self):
        md = '# Test\n\nHello world.'
        html = convert(md, profile='report', title='Test')
        assert '<!DOCTYPE html>' in html
        assert '<style>' in html
        assert '<script>' in html
        assert 'Hello world' in html

    def test_no_external_refs(self):
        md = '# Test\n\nContent.'
        html = convert(md, profile='report', title='Test')
        assert 'href="http' not in html
        assert 'src="http' not in html

    def test_profile_report_has_interactive_js(self):
        md = '# Test\n\nContent.'
        html = convert(md, profile='report', title='Test')
        assert 'initCollapsibles' in html

    def test_profile_onboard_has_checklist_js(self):
        md = ':::checklist{id="test"}\n- [ ] Item\n:::'
        html = convert(md, profile='onboard', title='Onboard')
        assert 'initChecklists' in html
        assert 'progress-container' in html
        assert 'data-checklist-prefix' in html

    def test_profile_document_toc(self):
        md = '## Section A\n\nContent A.\n\n## Section B\n\nContent B.'
        html = convert(md, profile='document', title='Docs', toc=True)
        assert 'has-toc' in html
        assert 'toc-sidebar' in html

    def test_title_in_output(self):
        md = '# Hello'
        html = convert(md, profile='report', title='My Report')
        assert '<title>My Report</title>' in html

    def test_lang_attribute(self):
        md = '# Hello'
        html = convert(md, profile='report', title='Test', lang='pt-BR')
        assert 'lang="pt-BR"' in html

    def test_style_css_override(self):
        md = '# Hello'
        html = convert(md, profile='report', title='Test', style_css='body { color: red; }')
        assert 'color: red' in html
        assert 'project style overrides' in html
