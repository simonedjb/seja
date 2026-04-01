---
name: document
description: "Generate or update project documentation based on plan Docs: fields, auto-detection, or explicit type selection."
argument-hint: "<scope> [--plan <id>] [--auto-detect] [--type <readme|contextual-help|api-reference|adr|help-center|changelog>]"
metadata:
  last-updated: 2026-04-01 16:42:22
  version: 1.0.0
  category: utility
  context_budget: standard
  references:
    - general/documentation-quality.md
    - general/report-conventions.md
---

## Quick Guide

**What it does**: Generate or update documentation for your project. Reads plan Docs: fields, detects changes from git history, or targets a specific documentation type. Uses project templates and the documentation-quality writing guide for structured generation.

**Examples**:
> You: /document --plan 000130
> Agent: Reads the plan's Docs: fields and generates the appropriate documentation for each identified need.

> You: /document --auto-detect
> Agent: Analyzes recent git changes, determines which documentation types are needed, and generates them.

> You: /document --type changelog
> Agent: Generates a changelog entry from recent changes using the changelog template.

**When to use**: After implementing a feature or fix that affects user-facing behavior, API contracts, or architectural decisions. Automatically suggested by post-skill for FEATURE and REDESIGN plans.

**See also**: `/explain` -- understand existing system behavior, architecture, data model, or design spec drift.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<scope>` | Yes (unless --plan or --auto-detect) | What to document: a file path, module, feature name, or general topic |
| `--plan <id>` | No | Read Docs: fields from a plan file and generate documentation for each identified need |
| `--auto-detect` | No | Detect documentation needs from recent git changes using heuristics |
| `--type <type>` | No | Force a specific documentation type: readme, contextual-help, api-reference, adr, help-center, or changelog |

# Document

If there are no arguments, ask the user what they need documented.

## Mode Detection

- If `--plan` is present: read the plan file, extract all non-N/A Docs: fields, and generate documentation for each identified need.
- If `--auto-detect` is present: analyze recent git changes and apply the auto-detection heuristic to determine which documentation types are needed.
- If `--type` is present: generate the specified documentation type for the given scope.
- If bare scope only: infer the most appropriate documentation type from the scope content.

---

## Core Workflow

1. Run `/pre-skill "document" $ARGUMENTS[0]` to add general instructions to the context window.

2. Determine scope and documentation type using mode detection logic above. If `--plan`, read the plan file and collect all steps with non-N/A `Docs:` fields into a work list.

3. **Launch generator agent(s):**

   Resolve the template path for each documentation type: check `_references/project/docs/<type>.md` first; fall back to `_references/template/docs/<type>.md`.

   **Single doc type** (bare scope, --type, or --auto-detect with one result):
   Launch the `document-generator` agent (Agent tool, subagent_type=`general-purpose`, using the prompt from `.claude/agents/document-generator.md`) with:
   - `doc_type`: the resolved documentation type
   - `scope`: the scope from arguments or auto-detection
   - `template_path`: the resolved template file path
   - `quality_guide_path`: `_references/general/documentation-quality.md`
   - `project_context`: paths to `_references/project/conventions.md` (or template fallback), `_references/project/conceptual-design-as-is.md`
   - `output_path`: the appropriate project location for this doc type

   **Multiple doc types** (--plan with multiple non-N/A Docs: fields, or --auto-detect with multiple results):
   Launch one `document-generator` agent per doc type **in parallel**. Each agent receives the same structure as above, with its specific doc_type, scope, and output_path.

   After agents return, verify that expected output files exist. Display a result summary (doc types generated, output paths).

4. Run `/post-skill` to log the brief, commit, and suggest next steps.

---

## Auto-Detection Heuristic

| Change pattern | Suggested doc type |
|----------------|-------------------|
| API endpoint files (routes, controllers, schemas) changed | api-reference |
| New UI screen/component added | contextual-help |
| README-referenced features changed | readme |
| Architectural decisions made (plan review log has trade-offs) | adr |
| New user-facing features (FEATURE prefix) | changelog + help-center |
| Module files added/removed | module README (convention from standards) |

---

## Trigger Scoping Note

FEATURE and REDESIGN plans are always prompted for documentation in post-skill. FIX and CHORE plans trigger the documentation prompt only when their steps contain non-N/A Docs: fields.
