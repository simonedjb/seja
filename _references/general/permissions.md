# FRAMEWORK - PERMISSIONS

- Don't ask for confirmation before reading any folder or file in the project.
- Don't ask for confirmation before executing git status, git log, git diff commands.
- Don't ask for confirmation before changing the directory within the project structure.
- Don't ask for confirmation before creating new source files.
- Don't ask for confirmation before appending content to any file in `${OUTPUT_DIR}/**` (see project/conventions.md), including briefs.md.
- Don't ask for confirmation before creating non-executable temporary files.
- Don't ask for confirmation before any read-only operation.
- Don't ask for confirmation before running backend or frontend tests.
- Don't ask for confirmation before creating, reading, or writing the session scratchpad file (`${SESSION_NOTES_FILE}`).
- Do not use `Edit` or `Write` on files classified as `Human (markers)` in the File Maintainer Classification table (see `_references/general/shared-definitions.md`). Use `python .claude/skills/scripts/apply_marker.py` instead. The `check_human_markers_only.py` verifier will reject non-marker hunks during post-skill commit.
- Ask for clarifications whenever appropriate.