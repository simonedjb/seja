#!/usr/bin/env python3
# designer: When the harness reference needs to know which public docs
#   already mention each harness file, I'm the scanner that walks your
#   harness source tree and the public docs tree and builds the mapping.
#   You get back a JSON map of harness-path to doc-paths that mention it
#   -- the raw signal the harness-reference generator uses to populate its
#   "Mentioned in" column and to flag surface that is shipping undocumented.
"""
scan_public_docs_for_filenames.py -- Map harness files to public-docs mentions.

Invocation: user-cli
Lifecycle: active

Walks harness files under a seja-priv repo (`.claude/**`, `.claude/references/**`)
and Markdown files under a seja-public docs root, then emits a JSON map of
harness-path -> list of public-docs files that mention the harness file
(by basename or by repo-relative path). This map is consumed by
`generate_harness_reference.py` to populate the "Mentioned in"
column of the generated harness reference.

JSON schema
-----------
{
  "generated_at": "2026-04-11T13:46:00Z",
  "harness_root": "d:/git/labs/seja-priv",
  "public_docs_root": "d:/git/labs/seja-priv/seja-public/docs",
  "harness_files": {
    "<repo-relative harness path>": {
      "basename": "<filename>",
      "mentioned_in": ["<repo-relative public-docs path>", ...]
    }
  }
}

`mentioned_in` is sorted alphabetically and deduplicated. Harness files with
zero mentions are still included with an empty `mentioned_in` list so the
generator can flag orphaned harness surface.

Usage
-----
    python .claude/skills/scripts/scan_public_docs_for_filenames.py \
        --public-docs-root d:/git/labs/seja-priv/seja-public/docs \
        --format json

Flags:
    --harness-root <path>       Auto-detected by walking up to find .claude/
    --public-docs-root <path>   Default: <harness-root>/seja-public/docs
                                (falls back to <harness-root>/../seja/docs).
    --output <path>             Default: stdout ("-" for stdout explicitly)
    --format {json,text}        Default: json
    --verbose                   Progress logging to stderr

Exit codes:
    0  success
    2  script error (I/O failure, missing public-docs-root)
"""

# Rationale for design choices and historical context: see scan_public_docs_for_filenames-rationale.md in this directory.
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo root discovery
# ---------------------------------------------------------------------------

SCRIPTS_DIR = Path(__file__).resolve().parent


def _find_harness_root() -> Path:
    """Walk up from this file until we find a `.claude/` directory."""
    candidate = SCRIPTS_DIR
    while candidate != candidate.parent:
        if (candidate / ".claude").is_dir():
            return candidate
        candidate = candidate.parent
    return Path.cwd()


# ---------------------------------------------------------------------------
# Harness file discovery
# ---------------------------------------------------------------------------

HARNESS_GLOBS_CLAUDE = ("*.md", "*.py", "*.yaml", "*.yml", "*.json")
HARNESS_GLOBS_REFS = ("*.md", "*.yaml", "*.json")

# Harness files whose basename is too generic to attribute a public-docs
# mention by basename alone. When a public doc says e.g. `README.md` it almost
# certainly refers to the project's own README, not `.claude/migrations/README.md`
# or any other harness file with the same basename. For these basenames we
# require a repo-relative path match instead of a basename match.
AMBIGUOUS_BASENAMES: frozenset[str] = frozenset({
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "LICENSE.md",
    "__init__.py",
    "constants.py",
})


def _contains_token(text: str, token: str) -> bool:
    """Return True if `token` appears in `text` with identifier-safe boundaries.

    Prevents false positives like `coding.md` matching `encoding.md` or
    `plan.py` matching `replan.py`: the character preceding the match must
    not be a word character (letters, digits, underscore), and the character
    following the match must not be a word character or a `.` (dotted suffix).
    """
    if not token:
        return False
    start = 0
    while True:
        idx = text.find(token, start)
        if idx == -1:
            return False
        before_ok = idx == 0 or not (text[idx - 1].isalnum() or text[idx - 1] == "_")
        end = idx + len(token)
        after_ok = end == len(text) or not (
            text[end].isalnum() or text[end] == "_" or text[end] == "."
        )
        if before_ok and after_ok:
            return True
        start = idx + 1


def _is_excluded(rel_path: Path) -> bool:
    """Return True if the relative path contains an excluded component.

    Excludes `__pycache__/`, `.claude/skills/scripts/tests/`, and any `_output/`
    subtree. `tests` is only excluded when it appears under
    `.claude/skills/scripts/` -- we still want to walk top-level test dirs if
    they exist elsewhere (there are none today, but this keeps the rule tight).
    """
    parts = rel_path.parts
    if "__pycache__" in parts:
        return True
    if "_output" in parts:
        return True
    # Exclude .claude/skills/scripts/tests/**
    if (
        len(parts) >= 5
        and parts[0] == ".claude"
        and parts[1] == "skills"
        and parts[2] == "scripts"
        and parts[3] == "tests"
    ):
        return True
    return False


def discover_harness_files(harness_root: Path, verbose: bool = False) -> list[Path]:
    """Walk the harness repo and return repo-relative paths of all harness files."""
    found: list[Path] = []

    claude_dir = harness_root / ".claude"
    if claude_dir.is_dir():
        for pattern in HARNESS_GLOBS_CLAUDE:
            for path in claude_dir.rglob(pattern):
                if not path.is_file():
                    continue
                rel = path.relative_to(harness_root)
                if _is_excluded(rel):
                    continue
                found.append(rel)

    # Scan harness references (general/ and template/ under .claude/references/)
    refs_dir = harness_root / ".claude" / "references"
    if refs_dir.is_dir():
        for pattern in HARNESS_GLOBS_REFS:
            for path in refs_dir.rglob(pattern):
                if not path.is_file():
                    continue
                rel = path.relative_to(harness_root)
                if _is_excluded(rel):
                    continue
                found.append(rel)

    # Scan project-specific references (project-design/)
    project_design_dir = harness_root / "project-design"
    if project_design_dir.is_dir():
        for pattern in HARNESS_GLOBS_REFS:
            for path in project_design_dir.rglob(pattern):
                if not path.is_file():
                    continue
                rel = path.relative_to(harness_root)
                if _is_excluded(rel):
                    continue
                found.append(rel)

    # Sort deterministically and dedupe
    unique = sorted({p.as_posix(): p for p in found}.values(), key=lambda p: p.as_posix())
    if verbose:
        print(f"harness files discovered: {len(unique)}", file=sys.stderr)
    return unique


# ---------------------------------------------------------------------------
# Public-docs discovery
# ---------------------------------------------------------------------------


def discover_public_docs(public_docs_root: Path, verbose: bool = False) -> list[Path]:
    """Walk the public-docs root and return repo-relative paths of Markdown files."""
    found: list[Path] = []
    for path in public_docs_root.rglob("*.md"):
        if not path.is_file():
            continue
        rel = path.relative_to(public_docs_root)
        found.append(rel)
    unique = sorted({p.as_posix(): p for p in found}.values(), key=lambda p: p.as_posix())
    if verbose:
        print(f"public docs discovered: {len(unique)}", file=sys.stderr)
    return unique


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------


def scan_mentions(
    harness_root: Path,
    public_docs_root: Path,
    harness_files: list[Path],
    public_docs: list[Path],
    verbose: bool = False,
) -> dict[str, dict]:
    """Return the harness_files map with mentioned_in lists populated.

    Each public-docs file is read once and matched against all harness
    paths. A match occurs if the file text contains either the harness
    file's basename OR its repo-relative path (POSIX form). Matches are
    case-sensitive.
    """
    result: dict[str, dict] = {}
    for rel in harness_files:
        result[rel.as_posix()] = {
            "basename": rel.name,
            "mentioned_in": set(),
        }

    for doc_rel in public_docs:
        doc_path = public_docs_root / doc_rel
        try:
            text = doc_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"WARNING: could not read {doc_path}: {exc}", file=sys.stderr)
            continue

        for harness_rel in harness_files:
            harness_key = harness_rel.as_posix()
            basename = harness_rel.name
            path_hit = _contains_token(text, harness_key)
            basename_hit = (
                basename not in AMBIGUOUS_BASENAMES
                and _contains_token(text, basename)
            )
            if path_hit or basename_hit:
                result[harness_key]["mentioned_in"].add(doc_rel.as_posix())

        if verbose:
            print(f"scanned: {doc_rel.as_posix()}", file=sys.stderr)

    # Convert sets to sorted lists
    for entry in result.values():
        entry["mentioned_in"] = sorted(entry["mentioned_in"])
    return result


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def render_json(
    harness_root: Path,
    public_docs_root: Path,
    harness_files_map: dict[str, dict],
) -> str:
    """Return the JSON payload as a string."""
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "harness_root": harness_root.as_posix(),
        "public_docs_root": public_docs_root.as_posix(),
        "harness_files": harness_files_map,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def render_text(
    harness_root: Path,
    public_docs_root: Path,
    harness_files_map: dict[str, dict],
) -> str:
    """Return a human-readable grouped listing for ad-hoc inspection."""
    lines: list[str] = []
    lines.append(f"harness_root: {harness_root.as_posix()}")
    lines.append(f"public_docs_root: {public_docs_root.as_posix()}")
    lines.append(f"harness_files: {len(harness_files_map)}")
    lines.append("")
    for key in sorted(harness_files_map):
        entry = harness_files_map[key]
        mentions = entry["mentioned_in"]
        if mentions:
            lines.append(f"{key}")
            for m in mentions:
                lines.append(f"    -> {m}")
        else:
            lines.append(f"{key}  (no mentions)")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _resolve_public_docs_root(harness_root: Path, explicit: str | None) -> Path:
    """Resolve the public-docs root with the in-repo preference."""
    if explicit:
        return Path(explicit).resolve()
    in_repo = harness_root / "seja-public" / "docs"
    if in_repo.is_dir():
        return in_repo.resolve()
    sibling = harness_root.parent / "seja" / "docs"
    return sibling.resolve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Map harness files to public-docs mentions",
    )
    parser.add_argument(
        "--harness-root",
        default=None,
        help="Path to seja-priv harness root (default: auto-detect)",
    )
    parser.add_argument(
        "--public-docs-root",
        default=None,
        help="Path to seja-public docs root "
             "(default: <harness-root>/seja-public/docs, "
             "fallback <harness-root>/../seja/docs)",
    )
    parser.add_argument(
        "--output",
        default="-",
        help="Output path (default: stdout)",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Progress logging to stderr",
    )
    args = parser.parse_args(argv)

    harness_root = (
        Path(args.harness_root).resolve()
        if args.harness_root
        else _find_harness_root()
    )
    if not harness_root.is_dir():
        print(
            f"ERROR: harness root does not exist: {harness_root}",
            file=sys.stderr,
        )
        return 2

    public_docs_root = _resolve_public_docs_root(harness_root, args.public_docs_root)
    if not public_docs_root.is_dir():
        print(
            f"ERROR: public-docs root does not exist: {public_docs_root}. "
            f"Pass --public-docs-root explicitly.",
            file=sys.stderr,
        )
        return 2

    if args.verbose:
        print(f"harness_root: {harness_root}", file=sys.stderr)
        print(f"public_docs_root: {public_docs_root}", file=sys.stderr)

    try:
        harness_files = discover_harness_files(harness_root, args.verbose)
        public_docs = discover_public_docs(public_docs_root, args.verbose)
        mapping = scan_mentions(
            harness_root,
            public_docs_root,
            harness_files,
            public_docs,
            args.verbose,
        )
    except OSError as exc:
        print(f"ERROR: I/O failure during scan: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        rendered = render_json(harness_root, public_docs_root, mapping)
    else:
        rendered = render_text(harness_root, public_docs_root, mapping)

    if args.output == "-":
        sys.stdout.write(rendered)
    else:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        if args.verbose:
            print(f"wrote: {output_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
