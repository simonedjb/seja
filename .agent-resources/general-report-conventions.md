# FRAMEWORK - REPORT CONVENTIONS

When a skill produces a report file in `${OUTPUT_DIR}` (see project-conventions.md), apply these conventions for common sub-fields:

- *id*: a unique, sequential number, zero-padded to 6 characters, globally unique across all artifact types, reserved atomically via `reserve_id.py`.
- *current datetime*: in the format YYYY-MM-DD hh:mm:ss in the UTC timezone.
- *prefix* (when applicable): one of [FEATURE, REDESIGN, FIX, REFACTOR, DOCUMENT, TEST, CHORE], depending on the brief.
- *scope* (when applicable): one of [-B for backend, -F for frontend, -X for cross-cutting, -O for other].
- *short title*: a brief descriptive title.
- *user brief*: user-provided feature or request description.
- *agent interpretation*: processed description, generated after interpreting the user-provided description.
- *source* (optional): `source: <type>-<id>` -- the artifact that triggered this one (e.g., `source: advisory-000042`).
- *spawned* (optional): `spawned: <type>-<id>[, ...]` -- artifacts created from this one (updated by post-skill).
- *files*: files relevant to the skill output.

Truncate sluggified short titles as needed. If not overwriting a file, proceed without asking for authorization.

Reserve the id by calling `python .claude/skills/scripts/reserve_id.py --type <type> --title '<title>'` before writing any content.

If any clarification question is asked of the user (excluding authorization-seeking questions), include the agent's question and user's answer in the report.

NEVER replace existing plan text. Instead, mark it as revoked or superseded, provide a rationale, create an identifier for the revoked fragment and append the replacement text to the file, referencing the revoked fragment.

## Report Filenames

All report and plan files under `${OUTPUT_DIR}` must have lowercase filenames.

## File Encoding

All files created by scripts, skills, or agents must be saved as **UTF-8 without BOM**. This applies to report and plan files under `${OUTPUT_DIR}`, generated code, configuration files, and any other output.

- Do not use platform-specific encodings (e.g., Windows-1252, ISO-8859-1, Shift-JIS).
- Accented and special characters (e.g., ã, é, ç, ü) must be properly encoded as UTF-8 and used naturally where appropriate (e.g., Portuguese text). Never output mojibake or escaped sequences.
- When writing files programmatically, explicitly specify `encoding='utf-8'`.

## Character Restrictions

All files created by scripts, skills, or agents must contain **no ANSI escape sequences**, no non-printable control characters (except newline `\n` and tab `\t`), and no typographic substitution characters.

- **Prohibited ANSI codes**: escape codes such as `\x1b[...` (color codes, cursor movement, bold/underline formatting). These are terminal-only formatting and corrupt Markdown readability.
- **Pattern to detect**: any occurrence matching the regex `\x1b\[[\d;]*[A-Za-z]` indicates ANSI contamination.
- **Prohibited typographic characters**: em-dashes (`U+2014`), en-dashes (`U+2013`), curly/smart quotes (`U+2018`, `U+2019`, `U+201C`, `U+201D`), and other non-ASCII punctuation substitutions. Use plain ASCII equivalents instead: hyphens (`-`) or double-hyphens (`--`), straight quotes (`'`, `"`).
- **Script output**: when capturing output from helper scripts (e.g., `count_loc.py`, `check_frontend_test_coverage.py`) into a file, strip ANSI codes before writing. In Python: `re.sub(r'\x1b\[[\d;]*[A-Za-z]', '', text)`.
- **Validation**: if any generated file contains ANSI sequences or prohibited typographic characters, it must be cleaned before committing.
