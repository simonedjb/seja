# FRAMEWORK -- DOCUMENTATION QUALITY GUIDE

> Canonical writing standards for all documentation in SEJA projects. Referenced by documentation templates in `template/docs/` and validated by `check_docs.py`.

## Quality Attributes

Five measurable attributes that define documentation quality:

### 1. Accuracy
Documentation matches current system behavior. If the system changes, the documentation must change in the same release. Stale documentation is worse than no documentation -- it actively misleads.

### 2. Completeness Within Declared Scope
Every documentation page must declare its scope (what it covers). Within that scope, no gaps. If your API reference lists 8 of 12 endpoints, that is worse than no API reference -- developers will trust the incomplete list and miss the unlisted endpoints. The solution: either document everything in scope, or explicitly state what is excluded and why.

### 3. Consistency
Terminology, formatting, and structure are uniform across all documentation. Use the same term for the same concept everywhere (see `general/shared-definitions.md`). Follow the same heading hierarchy, table format, and callout style.

### 4. Scannability
Users find answers in under 30 seconds. Achieved through:
- Descriptive headings (not "Overview" -- say what the overview is about)
- Tables for structured data (not prose paragraphs listing options)
- Bold lead-ins for list items
- Short paragraphs (3-5 sentences max)
- Code blocks for commands and examples

### 5. Maintainability
Documentation can be updated without heroic effort. Achieved through:
- Automated validation (path liveness, terminology consistency, structural completeness)
- Freshness policies per documentation type (see template frontmatter)
- Single source of truth (don't duplicate content -- reference it)
- Template-based structure (new pages follow existing patterns)

---

## Writing Principles

Five rules for writing documentation content:

### 1. Imperative Mood for Steps
Write steps as commands: "Click Save" not "The user should click Save" or "You can click Save." This is shorter, clearer, and translates better.

### 2. Bold Lead-ins for List Items
In how-to content, start each list item with a bold phrase summarizing the action:
- **Create the file** -- run `touch config.yml` in the project root
- **Add the key** -- open the file and add `api_key: YOUR_KEY`

### 3. Expected Outcomes Alongside Actions
After every action step, state what the user should see:
- "Click Save -- the confirmation toast appears in the top-right corner"
- "Run `npm test` -- all tests pass with 0 failures"

### 4. Two Callout Types Only
Limit callouts to exactly two types to prevent callout fatigue:
- **Tip**: Helpful shortcuts or best practices that save time
- **Warning**: Actions that cannot be undone or have significant consequences

Do not use Note, Info, Important, Caution, or Danger -- these distinctions are lost on readers.

### 5. Write for Global Audience
All documentation must be translatable:
- Simple sentence structures (subject-verb-object)
- No idioms ("out of the box", "under the hood")
- No cultural references or humor
- Avoid contractions in formal docs (use "do not" instead of "don't")
- Use standard date format (YYYY-MM-DD) not locale-specific formats

---

## Diataxis Framework

Every documentation page belongs to exactly one of four types. If a page serves two purposes, split it.

| Type | Purpose | Tone | Structure |
|------|---------|------|-----------|
| **Tutorial** | Learning-oriented | "Follow along with me" | Numbered steps with guaranteed outcome |
| **How-to** | Task-oriented | "Do this to achieve X" | Steps with decision points and alternatives |
| **Reference** | Information-oriented | "Here are the facts" | Tables, lists, exhaustive and dry |
| **Explanation** | Understanding-oriented | "Here is why" | Narrative prose, context, trade-offs |

Each documentation template declares its Diataxis type in YAML frontmatter (`diataxis: tutorial | how-to | reference | explanation`).

---

## Progressive Disclosure

Show the most-needed information first. Make deeper detail available without forcing users through it.

**At page level**: Core content before edge cases. The 3-question contextual help pattern (What / How / Verify) is the primary layer; constraints, failure modes, and impact are the secondary layer.

**At section level**: Summary before details. Start sections with a one-sentence summary, then expand.

**At doc-set level**: Getting-started before architecture deep-dives. README links to a recommended reading order.
