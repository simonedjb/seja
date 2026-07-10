#!/usr/bin/env python3
'''
html_report.py — Convert extended Markdown to rich, self-contained HTML.

Invocation: user-cli
Lifecycle: active

Preprocesses :::directive blocks (collapsible, callout, svg, checklist,
columns, card) then converts via python-markdown to a single HTML file
with all CSS and JS inlined.  Reads the same communication-style.md as
md_to_html.py for brand consistency.

Profiles select which CSS/JS bundles to inline:
  report      collapsible sections, callouts, SVG, syntax highlighting
  onboard     interactive checklists with localStorage, progress bar
  document    ToC sidebar navigation, progressive disclosure
  communicate cards, columns, callout boxes

Usage
-----
    python .claude/skills/scripts/html_report.py <input.md> [options]

    --style <path>      Path to communication-style.md
    --output <path>     Output HTML path (default: input stem + .html)
    --profile <name>    Feature profile: report | onboard | document | communicate
    --title <string>    Override document title
    --toc               Generate table-of-contents sidebar navigation
    --lang <code>       HTML lang attribute (default: en-US)
    --verbose           Show conversion details
'''
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = SCRIPT_DIR / 'html_assets'
REPO_ROOT = SCRIPT_DIR.parents[2]

sys.path.insert(0, str(SCRIPT_DIR))
try:
    from md_to_html import parse_style_file, DEFAULT_CSS, _default_lang
except ImportError:
    parse_style_file = None
    DEFAULT_CSS = ""
    def _default_lang() -> str:
        return "en-US"

DEFAULT_STYLE_PATH = REPO_ROOT / 'product-design' / 'communication-style.md'

PROFILE_CSS: dict[str, list[str]] = {
    'report':      ['base.css', 'report.css', 'syntax-highlight.css'],
    'onboard':     ['base.css', 'report.css', 'onboard.css'],
    'document':    ['base.css', 'report.css', 'document.css', 'syntax-highlight.css'],
    'communicate': ['base.css', 'report.css', 'communicate.css'],
}

PROFILE_JS: dict[str, list[str]] = {
    'report':      ['interactive.js'],
    'onboard':     ['interactive.js', 'checklist.js'],
    'document':    ['interactive.js'],
    'communicate': ['interactive.js'],
}

CALLOUT_ICONS: dict[str, str] = {
    'info':    'ℹ️',
    'tip':     '\U0001F4A1',
    'warning': '⚠️',
    'danger':  '❌',
}


# ---------------------------------------------------------------------------
# Asset loading
# ---------------------------------------------------------------------------

def _load_asset(filename: str) -> str:
    path = ASSETS_DIR / filename
    if path.is_file():
        return path.read_text(encoding='utf-8')
    return ''


def _build_css(profile: str, style_css: str | None = None) -> str:
    parts: list[str] = []
    for f in PROFILE_CSS.get(profile, PROFILE_CSS['report']):
        parts.append(_load_asset(f))
    if style_css:
        parts.append(f'/* project style overrides */\n{style_css}')
    return '\n'.join(parts)


def _build_js(profile: str) -> str:
    parts: list[str] = []
    for f in PROFILE_JS.get(profile, PROFILE_JS['report']):
        parts.append(_load_asset(f))
    return '\n'.join(parts)


# ---------------------------------------------------------------------------
# Directive preprocessing
# ---------------------------------------------------------------------------

def _preprocess_directives(text: str) -> str:
    text = _process_collapsible(text)
    text = _process_callout(text)
    text = _process_svg(text)
    text = _process_checklist(text)
    text = _process_columns(text)
    text = _process_card(text)
    return text


def _process_collapsible(text: str) -> str:
    pattern = re.compile(
        r'^:::collapsible\{title="([^"]+)"\}\s*\n'
        r'(.*?)\n'
        r'^:::\s*$',
        re.MULTILINE | re.DOTALL,
    )

    def repl(m: re.Match) -> str:
        title = m.group(1)
        body = m.group(2).strip()
        return (
            f'<details>\n<summary>{title}</summary>\n'
            f'<div class="collapsible-content">\n\n{body}\n\n</div>\n</details>'
        )

    return pattern.sub(repl, text)


def _process_callout(text: str) -> str:
    pattern = re.compile(
        r'^:::callout\{type="([^"]+)"\}\s*\n'
        r'(.*?)\n'
        r'^:::\s*$',
        re.MULTILINE | re.DOTALL,
    )

    def repl(m: re.Match) -> str:
        ctype = m.group(1)
        body = m.group(2).strip()
        icon = CALLOUT_ICONS.get(ctype, '')
        label = ctype.capitalize()
        return (
            f'<div class="callout callout-{ctype}">\n'
            f'<div class="callout-title">{icon} {label}</div>\n\n'
            f'{body}\n\n</div>'
        )

    return pattern.sub(repl, text)


def _process_svg(text: str) -> str:
    pattern = re.compile(
        r'^:::svg\s*\n(.*?)\n^:::\s*$',
        re.MULTILINE | re.DOTALL,
    )

    def repl(m: re.Match) -> str:
        svg_content = m.group(1).strip()
        return f'<div class="svg-container">\n{svg_content}\n</div>'

    return pattern.sub(repl, text)


def _process_checklist(text: str) -> str:
    pattern = re.compile(
        r'^:::checklist\{id="([^"]+)"\}\s*\n'
        r'(.*?)\n'
        r'^:::\s*$',
        re.MULTILINE | re.DOTALL,
    )

    def repl(m: re.Match) -> str:
        section_id = m.group(1)
        body = m.group(2).strip()
        items = re.findall(r'^- \[[ x]\]\s+(.+)$', body, re.MULTILINE)

        html_items: list[str] = []
        for i, item_text in enumerate(items):
            html_items.append(
                f'<div class="checklist-item">'
                f'<input type="checkbox" id="cb-{section_id}-{i}">'
                f'<label for="cb-{section_id}-{i}">{item_text}</label>'
                f'</div>'
            )

        return (
            f'<div class="checklist-section" data-checklist-id="{section_id}">\n'
            f'<div class="checklist-section-header">'
            f'<strong>{section_id.replace("-", " ").title()}</strong>'
            f'<span class="checklist-section-progress">0 / {len(items)}</span>'
            f'</div>\n'
            + '\n'.join(html_items)
            + '\n</div>'
        )

    return pattern.sub(repl, text)


def _process_columns(text: str) -> str:
    pattern = re.compile(
        r'^:::columns\{count=(\d+)\}\s*\n'
        r'(.*?)\n'
        r'^:::\s*$',
        re.MULTILINE | re.DOTALL,
    )

    def repl(m: re.Match) -> str:
        count = m.group(1)
        body = m.group(2).strip()
        parts = re.split(r'^---+\s*$', body, flags=re.MULTILINE)
        col_html: list[str] = []
        for part in parts:
            col_html.append(f'<div class="column">\n\n{part.strip()}\n\n</div>')
        return (
            f'<div class="columns columns-{count}">\n'
            + '\n'.join(col_html)
            + '\n</div>'
        )

    return pattern.sub(repl, text)


def _process_card(text: str) -> str:
    pattern = re.compile(
        r'^:::card\{title="([^"]+)"\}\s*\n'
        r'(.*?)\n'
        r'^:::\s*$',
        re.MULTILINE | re.DOTALL,
    )

    def repl(m: re.Match) -> str:
        title = m.group(1)
        body = m.group(2).strip()
        return (
            f'<div class="card">\n'
            f'<div class="card-title">{title}</div>\n\n'
            f'{body}\n\n</div>'
        )

    return pattern.sub(repl, text)


# ---------------------------------------------------------------------------
# ToC generation
# ---------------------------------------------------------------------------

def _generate_toc(html: str) -> str:
    headings = re.findall(r'<h([2-4])\s+id="([^"]+)"[^>]*>(.*?)</h\1>', html)
    if not headings:
        return ''

    toc_items: list[str] = []
    for level, hid, text in headings:
        clean_text = re.sub(r'<[^>]+>', '', text)
        indent = '  ' * (int(level) - 2)
        toc_items.append(f'{indent}<li><a href="#{hid}">{clean_text}</a></li>')

    return '<nav class="toc-sidebar"><ul>\n' + '\n'.join(toc_items) + '\n</ul></nav>'


# ---------------------------------------------------------------------------
# HTML assembly
# ---------------------------------------------------------------------------

TEMPLATE = """\
<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
{css}
  </style>
</head>
<body{body_attrs}>
{header}
{toc}
<div class="main-content">
{progress}
{content}
</div>
{footer}
<script>
{js}
</script>
</body>
</html>
"""

PROGRESS_BAR = """\
<div class="progress-container">
  <div class="progress-bar-outer">
    <div class="progress-bar-inner"></div>
  </div>
  <div class="progress-label">0 of 0 complete (0%)</div>
</div>
"""


def convert(
    md_text: str,
    *,
    profile: str = 'report',
    title: str = 'Report',
    lang: str = 'en-US',
    toc: bool = False,
    style_css: str | None = None,
    header_html: str = '',
    footer_html: str = '',
    checklist_prefix: str = 'seja-onboard',
    verbose: bool = False,
) -> str:
    if verbose:
        print(f'  Profile: {profile}')
        print(f'  Directives: preprocessing...')

    processed = _preprocess_directives(md_text)

    try:
        import markdown
        extensions = ['tables', 'fenced_code', 'toc', 'meta', 'attr_list']
        try:
            import pygments  # noqa: F401
            extensions.append('codehilite')
        except ImportError:
            pass
        html_body = markdown.markdown(
            processed,
            extensions=extensions,
            extension_configs={'toc': {'permalink': False, 'toc_depth': '2-4'}},
        )
    except ImportError:
        print('ERROR: python-markdown not installed. pip install markdown')
        sys.exit(1)

    css = _build_css(profile, style_css)
    js = _build_js(profile)

    toc_html = _generate_toc(html_body) if toc else ''

    body_attrs = ''
    if toc:
        body_attrs = ' class="has-toc"'
    if profile == 'onboard':
        body_attrs += f' data-checklist-prefix="{checklist_prefix}"'

    progress_html = PROGRESS_BAR if profile == 'onboard' else ''

    html = TEMPLATE.format(
        lang=lang,
        title=title,
        css=css,
        body_attrs=body_attrs,
        header=header_html,
        toc=toc_html,
        progress=progress_html,
        content=html_body,
        footer=footer_html,
        js=js,
    )

    if verbose:
        print(f'  HTML size: {len(html)} bytes')

    return html


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description='Convert extended Markdown to rich, self-contained HTML.',
    )
    parser.add_argument(
        'input', type=Path,
        help='Path to the input markdown file',
    )
    parser.add_argument(
        '--style', type=Path, default=DEFAULT_STYLE_PATH,
        help='Path to communication-style.md',
    )
    parser.add_argument(
        '--output', type=Path, default=None,
        help='Output HTML path (default: input stem + .html)',
    )
    parser.add_argument(
        '--profile', choices=['report', 'onboard', 'document', 'communicate'],
        default='report',
        help='Feature profile (default: report)',
    )
    parser.add_argument(
        '--title', default=None,
        help='Override document title',
    )
    parser.add_argument(
        '--toc', action='store_true',
        help='Generate table-of-contents sidebar navigation',
    )
    parser.add_argument(
        '--lang', default=None,
        help='HTML lang attribute (default: en-US)',
    )
    parser.add_argument(
        '--checklist-prefix', default='seja-onboard',
        help='localStorage key prefix for checklists (default: seja-onboard)',
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Show conversion details',
    )
    args = parser.parse_args()

    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    input_path: Path = args.input.resolve()
    if not input_path.is_file():
        print(f'ERROR: Input file not found: {input_path}')
        sys.exit(1)

    output_path: Path = (
        args.output.resolve()
        if args.output
        else input_path.with_suffix('.html')
    )

    title = args.title or input_path.stem.replace('-', ' ').replace('_', ' ').title()
    lang = args.lang or _default_lang()

    if args.verbose:
        print(f'Input:   {input_path}')
        print(f'Output:  {output_path}')
        print(f'Profile: {args.profile}')
        print(f'Title:   {title}')
        print(f'Lang:    {lang}')

    style_css: str | None = None
    header_html = ''
    footer_html = ''

    if parse_style_file and args.style.is_file():
        style = parse_style_file(args.style, verbose=args.verbose)
        style_css = style.get('css')
        header_html = style.get('header', '')
        footer_html = style.get('footer', '')

    md_text = input_path.read_text(encoding='utf-8')

    html = convert(
        md_text,
        profile=args.profile,
        title=title,
        lang=lang,
        toc=args.toc,
        style_css=style_css,
        header_html=header_html,
        footer_html=footer_html,
        checklist_prefix=args.checklist_prefix,
        verbose=args.verbose,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding='utf-8')

    print(f'OK: {output_path}')
    if args.verbose:
        size_kb = output_path.stat().st_size / 1024
        print(f'  Size: {size_kb:.1f} KB')


if __name__ == '__main__':
    main()
