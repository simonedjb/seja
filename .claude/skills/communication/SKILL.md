---
name: communication
description: "Generate tailored communication material for a specific audience segment."
argument-hint: <audience> [--format md|html|both] [--all] [--source <advisory-file>]
metadata:
  last-updated: 2026-03-30 00:00:00
  version: 1.1.0
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
> You: /communication clients
> Agent: Reads your project's design vision and produces client-oriented material highlighting value proposition, ROI, and project outcomes. Generates both Markdown and HTML.

**When to use**: You need to present the project to a specific audience and want material that speaks their language — whether it is a technical evaluator or a product client.

# Communication

Generate tailored communication material for a specific stakeholder audience segment.

## Arguments

- `<audience>`: One of `evaluator(s)`, `client(s)`, `end-user(s)`, `academic(s)`, or tags `EVL`, `CLT`, `USR`, `ACD`. Required unless `--all` is used.
- `[--format md|html|both]`: Output format (default: `both`). `md` generates only Markdown, `html` generates only HTML, `both` generates both side by side.
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
│   ├── index.md
│   ├── index.html
│   ├── communication-000012-evaluators.md
│   ├── communication-000012-evaluators.html
│   ├── communication-000013-clients/
│   │   ├── index.md
│   │   ├── index.html
│   │   ├── product-vision.md
│   │   ├── product-vision.html
│   │   ├── status-reporting.md
│   │   └── status-reporting.html
│   ├── communication-000014-end-users.md
│   └── communication-000014-end-users.html
├── 2026-04-15/
│   ├── index.md
│   ├── index.html
│   ├── communication-000021-academics.md
│   ├── communication-000021-academics.html
│   ├── communication-000022-evaluators.md
│   └── communication-000022-evaluators.html
```

When the content for a single audience naturally splits into distinct topics (e.g., a product vision and a status reporting template for clients), create a subfolder named `communication-<id>-<audience-slug>/` containing an `index.md` that links to the individual topic files. All files within the subfolder get both `.md` and `.html` versions. Use a single file when the content forms a cohesive narrative.

The sequential ID is globally unique across all artifact types (6-digit, zero-padded). Reserve it by running `python .claude/skills/scripts/reserve_id.py --type communication --title '<audience-slug>'` before writing any content.

## Batch Mode

When `--all` is provided, generate material for all 4 active audience segments in parallel.

### Batch Execution

1. Run /pre-skill once for the entire batch.
2. Reserve sequential IDs for all 4 audiences upfront by running `python .claude/skills/scripts/reserve_id.py --type communication --title '<audience-slug>'` once per audience.
3. Compute the date folder path: `${COMMUNICATION_DIR}/<YYYY-MM-DD>` (UTC). Create the folder if it does not exist.
4. Load shared context once: project state (step 4 of single mode) is read once in the parent context and passed to each agent via the prompt.
5. Launch one Agent per audience **in parallel** (all in a single message with multiple Agent tool calls). Each agent receives:
   - The resolved audience tag and audience file content
   - The pre-loaded shared project context (conceptual design, style config, etc.)
   - The assigned ID and output file path
   - The full skill instructions for steps 3-7 of single mode
6. After all agents complete, collect results and verify all files (both `.md` and `.html`) were written.
7. Run /post-skill once for the entire batch, staging all generated files in a single commit.

## Skill-specific Instructions

1. Run /pre-skill "communication" $ARGUMENTS to add general instructions to the context window.

2. **Parse arguments and resolve audience:**

   Map aliases to canonical tags:
   - `evaluator` / `evaluators` -> EVL
   - `client` / `clients` -> CLT
   - `end-user` / `end-users` -> USR
   - `academic` / `academics` -> ACD

   If the audience is not provided and `--all` is not set, use the AskUserQuestion tool to ask which audience segment (if AskUserQuestion is not available, present as a numbered text list), with these options:
   - "Evaluator (EVL) -- CTO, tech lead, engineering manager assessing adoption"
   - "Client (CLT) -- Project commissioner, business owner, funding partner of the product"
   - "End User (USR) -- Person using the software built with the framework"
   - "Academic (ACD) -- Researcher in semiotic engineering, HCI, AI-assisted development"

   If in **batch mode** (`--all`), skip to the Batch Execution flow above.

3. **Determine output path:**

   Compute the date folder: `${COMMUNICATION_DIR}/<YYYY-MM-DD>` (current UTC date). Create it if it does not exist.
   Reserve the next global ID by running `python .claude/skills/scripts/reserve_id.py --type communication --title '<audience-slug>'`. Use the returned 6-digit ID.

4. **Load communication content:**

   Based on the resolved audience:
   a. Load the audience file from `general-communication/<audience>.md`
   b. Load the Diataxis mapping from `general-communication/diataxis-mapping.md` for content type guidance
   c. If `--source` is provided, read the source file to be reformatted

5. **Read project state:**

   To make the communication material concrete and project-specific, **default to the codebase** (i.e., `${BACKEND_DIR}` / `${FRONTEND_DIR}` from conventions) as the scan target — not the workspace root. In workspace deployments these point to the actual source code via absolute paths.

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

   ### Self-Review and Refinement
   Before writing the final output, perform an internal review:
   - Consult the Diataxis mapping to identify which content types this material covers and whether any gaps exist for this audience
   - If the review suggests additional sections, missing perspectives, or structural improvements, **incorporate them directly into the content** rather than listing them as next steps
   - The final output must be fully stakeholder-facing — no meta-commentary, internal notes, next steps, or recommendations for the author

   ### Multi-File Decision
   After refinement, assess whether the content should be a single file or multiple files:
   - **Single file**: when the content forms a cohesive narrative under ~2500 words
   - **Multiple files in a subfolder**: when the content covers distinct topics that a stakeholder would want to navigate independently (e.g., a product vision document and a separate status reporting template). Create a subfolder with an `index.md` linking to each topic file.

7. **Output:**

   a. Write the markdown file(s) to the output path determined in step 3. If using a subfolder, create `communication-<id>-<audience-slug>/` with `index.md` and individual topic files. Ensure all cross-references between files use relative markdown links.
   b. Generate HTML based on `--format` (default `both`):
      - `both` or `html`: Run `python .claude/skills/scripts/md_to_html.py <markdown-file>` for every `.md` file. If `project-communication-style.md` exists, pass it via `--style`. For subfolder output, ensure HTML cross-references use relative links with `.html` extensions.
      - `md`: Skip HTML generation.
      - `html`: Generate HTML as above, then remove the intermediate `.md` files — deliver only `.html`.

8. **Date-folder index:**

   After writing the output, check whether the date folder (`${COMMUNICATION_DIR}/<YYYY-MM-DD>`) contains more than one communication artifact (files or subfolders). If it does, create or update an `index.md` at the root of the date folder that lists all artifacts with relative links. The index should include a title (`# Communications — <YYYY-MM-DD>`) and a bullet list with each artifact's ID, audience, and link. Generate the HTML version of the index according to the `--format` flag (same rules as step 7b).

   If the date folder contains only one artifact, skip the index — it adds no navigational value.

9. Run /post-skill <id>.
