# SEJA Framework Migrations

Migration scripts that run automatically during framework upgrades to transform
project files between versions.

## Naming convention

```
NNNN_description.py
```

- **NNNN** -- zero-padded sequence number (0001, 0002, ...).
- **description** -- short snake_case label describing the change.

Migrations are sorted by sequence number and executed in order.

## Required exports

Each migration module must export:

| Export | Type | Description |
|---|---|---|
| `from_version` | `str` | Minimum version this migration applies to (inclusive). |
| `to_version` | `str` | Version the project reaches after this migration. |
| `upgrade(root)` | `function(Path) -> None` | Forward migration logic. |
| `downgrade(root)` | `function(Path) -> None` | Reverse migration logic (optional but recommended). |

## Authoring guide

1. **Idempotent** -- `upgrade()` must be safe to run more than once.  Check
   whether the transformation has already been applied before making changes.
2. **Stdlib only** -- use only Python standard-library modules.
3. **Plain ASCII** -- no ANSI escape codes; UTF-8 text is fine.
4. **Path argument** -- `root` is the absolute `Path` to the project root
   (the directory containing `.claude/`).  Resolve all file paths relative to
   it.
5. **Logging** -- print `INFO:`, `OK:`, `WARN:`, or `ERROR:` prefixed lines
   so the migration runner can relay status.
6. **Errors** -- raise an exception on unrecoverable failure; the runner will
   stop the chain and preserve the last successful version.

## Example skeleton

```python
"""0002_example_migration.py"""
from pathlib import Path

from_version = "2.0.0"
to_version = "2.1.0"

def upgrade(root: Path) -> None:
    target = root / "some" / "file.md"
    if not target.is_file():
        return
    text = target.read_text(encoding="utf-8")
    if "new_pattern" in text:
        return  # already migrated
    text = text.replace("old_pattern", "new_pattern")
    target.write_text(text, encoding="utf-8")
    print("OK: Replaced old_pattern with new_pattern in some/file.md")

def downgrade(root: Path) -> None:
    target = root / "some" / "file.md"
    if not target.is_file():
        return
    text = target.read_text(encoding="utf-8")
    text = text.replace("new_pattern", "old_pattern")
    target.write_text(text, encoding="utf-8")
    print("OK: Reverted new_pattern to old_pattern in some/file.md")
```
