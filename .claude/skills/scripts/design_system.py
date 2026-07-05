#!/usr/bin/env python3
# designer: When a project ships a design system as an HTML file with CSS
#   custom properties and style blocks, I'm the extraction layer that reads
#   those tokens out so generators like md_to_html and generate_spo can
#   adopt them without each one reinventing its own HTML parser.
"""
design_system — Extract CSS and design tokens from HTML design system files.

Invocation: library
Lifecycle: active

Provides three functions for downstream generators:

  extract_css(html_path)        All <style> block contents joined.
  extract_root_vars(html_path)  The first :root { ... } block.
  find_design_system(root)      Glob for *design-system.html under product-design/.
"""
from __future__ import annotations

import re
from pathlib import Path

_STYLE_RE = re.compile(
    r"<style(?:\s[^>]*)?>(.+?)</style>",
    re.DOTALL | re.IGNORECASE,
)

_STYLE_EXCLUDE_RE = re.compile(
    r'\b(?:scoped|type\s*=\s*["\']text/javascript["\'])',
    re.IGNORECASE,
)

_ROOT_RE = re.compile(
    r":root\s*\{[^}]*\}",
    re.DOTALL,
)


def extract_css(html_path: Path) -> str | None:
    """Concatenate all <style> block contents, excluding scoped / JS variants."""
    text = html_path.read_text(encoding="utf-8")
    blocks: list[str] = []
    for m in _STYLE_RE.finditer(text):
        tag_span = text[m.start(): text.index(">", m.start()) + 1]
        if _STYLE_EXCLUDE_RE.search(tag_span):
            continue
        blocks.append(m.group(1).strip())
    return "\n".join(blocks) if blocks else None


def extract_root_vars(html_path: Path) -> str | None:
    """Return the first :root { ... } block from the file's CSS, or None."""
    css = extract_css(html_path)
    if css is None:
        return None
    m = _ROOT_RE.search(css)
    return m.group(0) if m else None


def find_design_system(project_root: Path) -> Path | None:
    """Glob for product-design/*design-system.html under *project_root*."""
    matches = sorted(project_root.glob("product-design/*design-system.html"))
    return matches[0] if matches else None
