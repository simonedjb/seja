#!/usr/bin/env python3
"""
scan_public_docs_for_filenames.py -- Map framework files to public-docs mentions.

Walks framework files under a seja-priv repo (`.claude/**`, `_references/**`)
and Markdown files under a seja-public docs root, then emits a JSON map of
framework-path -> list of public-docs files that mention the framework file
(by basename or by repo-relative path). This map is consumed by
`generate_framework_reference.py` (plan-000281) to populate the "Mentioned in"
column of the generated framework reference.

JSON schema
-----------
{
  "generated_at": "2026-04-11T13:46:00Z",
  "framework_root": "d:/git/labs/seja-priv",
  "public_docs_root": "d:/git/labs/seja-priv/seja-public/docs",
  "framework_files": {
    "<repo-relative framework path>": {
      "basename": "<filename>",
      "mentioned_in": ["<repo-relative public-docs path>", ...]
    }
  }
}

`mentioned_in` is sorted alphabetically and deduplicated. Framework files with
zero mentions are still included with an empty `mentioned_in` list so the
generator can flag orphaned framework surface.

Usage
-----
    python .claude/skills/scripts/scan_public_docs_for_filenames.py \
        --public-docs-root d:/git/labs/seja-priv/seja-public/docs \
        --format json

Flags:
    --framework-root <path>     Auto-detected by walking up to find .claude/
    --public-docs-root <path>   Default: <framework-root>/seja-public/docs
                                (falls back to <framework-root>/../seja/docs).
    --output <path>             Default: stdout ("-" for stdout explicitly)
    --format {json,text}        Default: json
    --verbose                   Progress logging to stderr

Exit codes:
    0  success
    2  script error (I/O failure, missing public-docs-root)
"""
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


def _find_framework_root() -> Path:
    """Walk up from this file until we find a `.claude/` directory."""
    candidate = SCRIPTS_DIR
    while candidate != candidate.parent:
        if (candidate / ".claude").is_dir():
            return candidate
        candidate = candidate.parent
    return Path.cwd()


# ---------------------------------------------------------------------------
# Framework file discovery
# ---------------------------------------------------------------------------

FRAMEWORK_GLOBS_CLAUDE = ("*.md", "*.py", "*.yaml", "*.yml", "*.json")
FRAMEWORK_GLOBS_REFS = ("*.md", "*.yaml", "*.json")


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


def discover_framework_files(framework_root: Path, verbose: bool = False) -> list[Path]:
    """Walk the framework repo and return repo-relative paths of all framework files."""
    found: list[Path] = []

    claude_dir = framework_root / ".claude"
    if claude_dir.is_dir():
        for pattern in FRAMEWORK_GLOBS_CLAUDE:
            for path in claude_dir.rglob(pattern):
                if not path.is_file():
                    continue
                rel = path.relative_to(framework_root)
                if _is_excluded(rel):
                    continue
                found.append(rel)

    refs_dir = framework_root / "_references"
    if refs_dir.is_dir():
        for pattern in FRAMEWORK_GLOBS_REFS:
            for path in refs_dir.rglob(pattern):
                if not path.is_file():
                    continue
                rel = path.relative_to(framework_root)
                if _is_excluded(rel):
                    continue
                found.append(rel)

    # Sort deterministically and dedupe
    unique = sorted({p.as_posix(): p for p in found}.values(), key=lambda p: p.as_posix())
    if verbose:
        print(f"framework files discovered: {len(unique)}", file=sys.stderr)
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
    framework_root: Path,
    public_docs_root: Path,
    framework_files: list[Path],
    public_docs: list[Path],
    verbose: bool = False,
) -> dict[str, dict]:
    """Return the framework_files map with mentioned_in lists populated.

    Each public-docs file is read once and matched against all framework
    paths. A match occurs if the file text contains either the framework
    file's basename OR its repo-relative path (POSIX form). Matches are
    case-sensitive.
    """
    result: dict[str, dict] = {}
    for rel in framework_files:
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

        for framework_rel in framework_files:
            framework_key = framework_rel.as_posix()
            basename = framework_rel.name
            if _contains_token(text, framework_key) or _contains_token(text, basename):
                result[framework_key]["mentioned_in"].add(doc_rel.as_posix())

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
    framework_root: Path,
    public_docs_root: Path,
    framework_files_map: dict[str, dict],
) -> str:
    """Return the JSON payload as a string."""
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "framework_root": framework_root.as_posix(),
        "public_docs_root": public_docs_root.as_posix(),
        "framework_files": framework_files_map,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def render_text(
    framework_root: Path,
    public_docs_root: Path,
    framework_files_map: dict[str, dict],
) -> str:
    """Return a human-readable grouped listing for ad-hoc inspection."""
    lines: list[str] = []
    lines.append(f"framework_root: {framework_root.as_posix()}")
    lines.append(f"public_docs_root: {public_docs_root.as_posix()}")
    lines.append(f"framework_files: {len(framework_files_map)}")
    lines.append("")
    for key in sorted(framework_files_map):
        entry = framework_files_map[key]
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


def _resolve_public_docs_root(framework_root: Path, explicit: str | None) -> Path:
    """Resolve the public-docs root with the in-repo preference."""
    if explicit:
        return Path(explicit).resolve()
    in_repo = framework_root / "seja-public" / "docs"
    if in_repo.is_dir():
        return in_repo.resolve()
    sibling = framework_root.parent / "seja" / "docs"
    return sibling.resolve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Map framework files to public-docs mentions",
    )
    parser.add_argument(
        "--framework-root",
        default=None,
        help="Path to seja-priv framework root (default: auto-detect)",
    )
    parser.add_argument(
        "--public-docs-root",
        default=None,
        help="Path to seja-public docs root "
             "(default: <framework-root>/seja-public/docs, "
             "fallback <framework-root>/../seja/docs)",
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

    framework_root = (
        Path(args.framework_root).resolve()
        if args.framework_root
        else _find_framework_root()
    )
    if not framework_root.is_dir():
        print(
            f"ERROR: framework root does not exist: {framework_root}",
            file=sys.stderr,
        )
        return 2

    public_docs_root = _resolve_public_docs_root(framework_root, args.public_docs_root)
    if not public_docs_root.is_dir():
        print(
            f"ERROR: public-docs root does not exist: {public_docs_root}. "
            f"Pass --public-docs-root explicitly.",
            file=sys.stderr,
        )
        return 2

    if args.verbose:
        print(f"framework_root: {framework_root}", file=sys.stderr)
        print(f"public_docs_root: {public_docs_root}", file=sys.stderr)

    try:
        framework_files = discover_framework_files(framework_root, args.verbose)
        public_docs = discover_public_docs(public_docs_root, args.verbose)
        mapping = scan_mentions(
            framework_root,
            public_docs_root,
            framework_files,
            public_docs,
            args.verbose,
        )
    except OSError as exc:
        print(f"ERROR: I/O failure during scan: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        rendered = render_json(framework_root, public_docs_root, mapping)
    else:
        rendered = render_text(framework_root, public_docs_root, mapping)

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
