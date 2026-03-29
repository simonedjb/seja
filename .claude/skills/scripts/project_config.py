#!/usr/bin/env python3
"""
project_config — Central configuration for SEJA helper scripts.

Parses project-conventions.md and exposes all variables via get/get_path/get_list.
Falls back to template-conventions.md when project-conventions.md is absent.

Usage from sibling scripts:
    from project_config import REPO_ROOT, get, get_path, get_list

    backend_dir = get_path("BACKEND_DIR")
    subpackages = get_list("BACKEND_SUBPACKAGES", ["api", "models", "services"])
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo root discovery
# ---------------------------------------------------------------------------

_CONVENTIONS_REL = Path(".agent-resources", "project-conventions.md")
_TEMPLATE_REL = Path(".agent-resources", "template-conventions.md")
_ROW_RE = re.compile(
    r"^\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|", re.MULTILINE
)
_VAR_REF_RE = re.compile(r"\$\{([^}]+)\}")
_MAX_RESOLVE_PASSES = 10


def _find_repo_root() -> Path:
    """Walk up from the script's location until we find a .claude/ directory."""
    candidate = Path(__file__).resolve().parent
    while candidate != candidate.parent:
        if (candidate / ".claude").is_dir():
            return candidate
        candidate = candidate.parent
    return Path.cwd()


REPO_ROOT = _find_repo_root()

# ---------------------------------------------------------------------------
# Config parsing (lazy, cached at module level)
# ---------------------------------------------------------------------------

_config: dict[str, str] | None = None
_warned_missing = False


def _parse_config() -> dict[str, str]:
    """Read project-conventions.md, extract variable rows, resolve refs."""
    global _warned_missing

    conventions = REPO_ROOT / _CONVENTIONS_REL
    if not conventions.is_file():
        template = REPO_ROOT / _TEMPLATE_REL
        if template.is_file():
            if not _warned_missing:
                print(
                    f"INFO: project-conventions.md not found; using template-conventions.md as fallback",
                    file=sys.stderr,
                )
                _warned_missing = True
            conventions = template
        else:
            if not _warned_missing:
                print(
                    f"WARNING: neither project-conventions.md nor template-conventions.md found",
                    file=sys.stderr,
                )
                _warned_missing = True
            return {}

    text = conventions.read_text(encoding="utf-8", errors="replace")
    raw: dict[str, str] = {}
    for m in _ROW_RE.finditer(text):
        raw[m.group(1)] = m.group(2)

    # Resolve ${VAR} references iteratively
    resolved = dict(raw)
    for _ in range(_MAX_RESOLVE_PASSES):
        changed = False
        for key, value in resolved.items():
            new_value = _VAR_REF_RE.sub(
                lambda m: resolved.get(m.group(1), m.group(0)), value
            )
            if new_value != value:
                resolved[key] = new_value
                changed = True
        if not changed:
            break

    return resolved


def _ensure_config() -> dict[str, str]:
    """Return cached config, parsing on first call."""
    global _config
    if _config is None:
        _config = _parse_config()
    return _config


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get(key: str, default: str | None = None) -> str | None:
    """Get a resolved string value by variable name."""
    return _ensure_config().get(key, default)


def get_path(key: str, default: str | None = None) -> Path | None:
    """Get a resolved value as a Path relative to REPO_ROOT."""
    value = get(key, default)
    if value is None:
        return None
    return REPO_ROOT / value


def get_list(key: str, default: list[str] | None = None) -> list[str]:
    """Split a comma-separated value into a list of stripped strings."""
    value = get(key)
    if value is None:
        return default if default is not None else []
    return [item.strip() for item in value.split(",")]


def diff_conventions(project_path: str | Path, template_path: str | Path) -> dict:
    """Compare a project-conventions file against a template-conventions file.

    Parses both files using _ROW_RE and returns a dict with:
      - missing_in_project: variable names in template but not in project
      - extra_in_project: variable names in project but not in template
      - value_differences: list of dicts with key, project_value, template_value
    """
    project_path = Path(project_path)
    template_path = Path(template_path)

    def _parse_rows(path: Path) -> dict[str, str]:
        if not path.is_file():
            return {}
        text = path.read_text(encoding="utf-8", errors="replace")
        return {m.group(1): m.group(2) for m in _ROW_RE.finditer(text)}

    project_vars = _parse_rows(project_path)
    template_vars = _parse_rows(template_path)

    project_keys = set(project_vars)
    template_keys = set(template_vars)

    value_differences = [
        {
            "key": key,
            "project_value": project_vars[key],
            "template_value": template_vars[key],
        }
        for key in sorted(project_keys & template_keys)
        if project_vars[key] != template_vars[key]
    ]

    return {
        "missing_in_project": sorted(template_keys - project_keys),
        "extra_in_project": sorted(project_keys - template_keys),
        "value_differences": value_differences,
    }


# ---------------------------------------------------------------------------
# Standalone mode
# ---------------------------------------------------------------------------


def _main() -> None:
    """Print all resolved config variables."""
    config = _ensure_config()
    if not config:
        print("No configuration loaded (project-conventions.md missing or empty).")
        return

    print(f"REPO_ROOT: {REPO_ROOT}\n")
    max_key_len = max(len(k) for k in config)
    for key in sorted(config):
        print(f"  {key:<{max_key_len}}  =  {config[key]}")


if __name__ == "__main__":
    _main()
