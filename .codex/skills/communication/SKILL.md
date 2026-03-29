---
name: communication
description: "Generate tailored communication material for a specific audience segment."
argument-hint: <audience> [--format md|html] [--all] [--source <advisory-file>]
metadata:
  last-updated: 2026-03-28 19:30:00
  version: 1.0.0
  category: utility
  context_budget: standard
  references:
    - general-communication.md
    - project-conceptual-design-as-is.md
    - general-shared-definitions.md
    - general-report-conventions.md
---

## Quick Guide

**What it does**: Generates tailored communication material for a specific audience — evaluators, clients, end users, or academics. Each audience gets content in their language, focused on what matters to them.

**Example**:
> You: $communication clients
> Agent: Reads your project's design vision and produces client-oriented material highlighting value proposition, ROI, and project outcomes. Available in Markdown or HTML.

**When to use**: You need to present the project to a specific audience and want material that speaks their language — whether it is a technical evaluator or a product client.

# Communication

Generate tailored communication material for a specific stakeholder audience segment.

## Arguments

- `<audience>`: One of `evaluator(s)`, `client(s)`, `end-user(s)`, `academic(s)`, or tags `EVL`, `CLT`, `USR`, `ACD`. Required unless `--all` is used.
- `[--format md|html]`: Output format (default: `md`). When `html`, generates a styled standalone HTML file alongside the markdown using `md_to_html.py`.
- `[--all]`: Generate material for all active audience segments (EVL, CLT, USR, ACD) in parallel via batch mode.
- `[--source <file>]`: Path to an existing advisory report or markdown file to reformat for the target audience.
- `[--deep]`: Include Deep-dive content sections in addition to Essential sections.

If the audience is missing and `--all` is not set, present an interactive menu.

## Definitions

Output folder: `${COMMUNICATION_DIR}/<YYYY-MM-DD>` where `<YYYY-MM-DD>` is the current UTC date.
Filename pattern: `communication-<id>-<audience-slug>.<ext>`

All material generated on the same date shares the same date folder. Material generated on different dates lives in different folders, creating a versioned history.

Example directory structure:
```
${COMMUNICATION_DIR}/
├── 2026-03-28/
│   ├── communication-000012-evaluators.md
│   ├── communication-000012-evaluators.html
│   ├── communication-000013-clients.md
│   └── communication-000014-end-users.md
├── 2026-04-15/
│   ├── communication-000021-academics.md
│   └── communication-000022-evaluators.md
```

The sequential ID is globally unique across all artifact types (6-digit, zero-padded). Reserve it by running `python .codex/skills/scripts/reserve_id.py --type communication --title '<audience-slug>'` before writing any content.

## Batch Mode

When `--all` is provided, generate material for all 4 active audience segments in parallel.

### Batch Execution

1. Run $pre-skill once for the entire batch.
2. Reserve sequential IDs for all 4 audiences upfront by running `python .codex/skills/scripts/reserve_id.py --type communication --title '<audience-slug>'` once per audience.
3. Compute the date folder path: `${COMMUNICATION_DIR}/<YYYY-MM-DD>` (UTC). Create the folder if it does not exist.
4. Load shared context once: project state (step 4 of single mode) is read once in the parent context and passed to each agent via the prompt.
5. Launch one Agent per audience **in parallel** (all in a single message with multiple `spawn_agent` calls). Each agent receives:
   - The resolved audience tag and audience file content
   - The pre-loaded shared project context (conceptual design, style config, etc.)
   - The assigned ID and output file path
   - The full skill instructions for steps 3-7 of single mode
6. After all agents complete, collect results and verify all files were written.
7. Run $post-skill once for the entire batch, staging all generated files in a single commit.

## Skill-specific Instructions

1. Run $pre-skill "communication" $ARGUMENTS to add general instructions to the context window.

2. **Parse arguments and resolve audience:**

   Map aliases to canonical tags:
   - `evaluator` / `evaluators` -> EVL
   - `client` / `clients` -> CLT
   - `end-user` / `end-users` -> USR
   - `academic` / `academics` -> ACD

   If the audience is not provided and `--all` is not set, use the ask the user directly tool to ask which audience segment (if ask the user directly is not available, present as a numbered text list), with these options:
   - "Evaluator (EVL) -- CTO, tech lead, engineering manager assessing adoption"
   - "Client (CLT) -- Project commissioner, business owner, funding partner of the product"
   - "End User (USR) -- Person using the software built with the framework"
   - "Academic (ACD) -- Researcher in semiotic engineering, HCI, AI-assisted development"

   If in **batch mode** (`--all`), skip to the Batch Execution flow above.

3. **Determine output path:**

   Compute the date folder: `${COMMUNICATION_DIR}/<YYYY-MM-DD>` (current UTC date). Create it if it does not exist.
   Reserve the next global ID by running `python .codex/skills/scripts/reserve_id.py --type communication --title '<audience-slug>'`. Use the returned 6-digit ID.

4. **Load communication content:**

   Based on the resolved audience:
   a. Load the audience file from `general-communication/<audience>.md`
   b. Load the Diataxis mapping from `general-communication/diataxis-mapping.md` for content type guidance
   c. If `--source` is provided, read the source file to be reformatted

5. **Read project state:**

   To make the communication material concrete and project-specific:
   a. Read `project-conceptual-design-as-is.md` for current system overview, mission, value proposition.
   b. Read `project-conventions.md` for project identity and key variables.
   c. If available, read `project-communication-style.md` for tone/depth overrides and branding. If it does not exist, use defaults from `template-communication-style.md`.

6. **Generate the communication material:**

   The output must include the following sections:

   ### Header
   `# Communication <id> | <audience-tag> | <current datetime> | <audience name>`

   ### Project Overview (Layer 0 — Universal Foundation)
   Drawn from conceptual design:
   - Project identity: name, mission, current phase
   - Value proposition: what problem the project solves and for whom
   - Key differentiators: what sets the project apart

   ### Audience-Specific Content (Layer 1)
   Drawn from the loaded audience file:
   - Generate all **Essential** content sections from the audience file, made concrete with project-specific information
   - If `--deep` is set, also generate **Deep-dive** content sections
   - Apply the audience file's **Tone Guidance** throughout

   ### Source Reformatting (if `--source` provided)
   Instead of generating fresh content:
   - Read the source file and identify key information, findings, and recommendations
   - Rewrite the content for the target audience using the audience file's tone guidance and content structure
   - Preserve all substantive information while adjusting framing, depth, and vocabulary
   - Add a "Source" attribution line referencing the original file

   ### Diataxis Classification
   At the end of the document, classify the generated content:
   - Which Diataxis content type(s) this material covers (Tutorial, How-to, Explanation, Reference)
   - Suggested next pieces to generate for this audience (from the Diataxis mapping)

7. **Output:**

   a. Write the markdown file to the output path determined in step 3.
   b. If `--format html`: Run `python .codex/skills/scripts/md_to_html.py <markdown-file>` to generate a styled HTML file alongside it. If `project-communication-style.md` exists, pass it via `--style`.

8. Run $post-skill <id>.
