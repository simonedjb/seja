---
name: advise
description: "Answer questions about the codebase, architecture, or design decisions, logging Q&A pairs. With --inventory, catalog codebase elements matching a pattern."
argument-hint: "<question or topic> [--inventory <pattern>] [--deep]"
metadata:
  last-updated: 2026-04-01 13:22:00
  version: 1.2.0
  category: analysis
  context_budget: standard
  eager_references:
    - project/conceptual-design-as-is.md
  references:
    - project/conceptual-design-as-is.md
    - project/conceptual-design-to-be.md
    - general/shared-definitions.md
    - general/report-conventions.md
    - general/review-perspectives.md
---

## Quick Guide

**What it does**: Ask any question about the project — architecture, design decisions, trade-offs. The agent researches your codebase, analyzes from multiple perspectives, and gives you actionable recommendations. With `--inventory`, it catalogs all codebase elements matching a pattern (e.g., all API endpoints, all form components).

**Example**:
> You: /advise Should we use a modal or a full page for the new settings flow?
> Agent: Researches the codebase, evaluates from UX, accessibility, and architecture perspectives, and provides a recommendation with pros and cons. Asks if you have follow-up questions.

> You: /advise --inventory List all form components and which pages use them
> Agent: Scans the codebase and produces a structured list of all form components, their locations, and where they are used across the project.

**When to use**: You need guidance on a design decision, want to understand trade-offs, or are unsure about the best approach for something. Use `--inventory` when you need an overview of what exists in the codebase — components, endpoints, models, or any other pattern you want to catalog. Use `--deep` for high-stakes decisions that benefit from a structured debate between named expert archetypes.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<question or topic>` | Yes | The question or topic to get advice on |
| `--inventory <pattern>` | No | Switch to inventory mode: catalog all codebase elements matching the pattern |
| `--deep` | No | Activate structured expert council debate for high-stakes decisions |

# Advise

If there are no arguments, ask the user what they need advice on.

## Mode Detection

If the arguments begin with `--inventory`, run the **Inventory workflow** below instead of the default Advisory workflow. The inventory brief is everything after `--inventory`.

If the arguments contain `--deep`, set the deep-dive flag for the Advisory workflow. Strip `--deep` from the arguments before passing them as the brief. The `--deep` flag activates the expert council debate in step 5.

---

## Inventory Workflow

Output folder: `${INVENTORIES_DIR}` (see project/conventions.md)
Filename pattern: `inventory-<id>-<truncated short title slug>.md` (6-digit zero-padded ID)

If there is no brief after `--inventory`, ask for the brief.

1. Run /pre-skill "advise" $ARGUMENTS[0] to add general instructions to the context window.

2. Reserve the next global ID by running `python .claude/skills/scripts/reserve_id.py --type inventory --title '<short title>'`. Use the returned 6-digit ID.

3. Search the source code for all elements mentioned in the brief, including related enumerations, constants, CSS classes, files, and other relevant elements.

3. Save the information to the output file, adopting a format similar to the existing entries, including:
- *header*: `# Inventory <id> | <prefix><scope> | <current datetime> | <short title>`
- *user brief*, *agent interpretation*, *files* — per _references/general/report-conventions.md
- *inventory*: no predefined structure here

4. Output the inventory id.

5. Run /post-skill <id>.

---

## Advisory Workflow (default)

### Definitions

Output folder: `${ADVISORY_DIR}` (see project/conventions.md)
Filename pattern: `advisory-<id>-<truncated short title slug>.md` (6-digit zero-padded ID)

### Skill-specific Instructions

1. Run /pre-skill "advise" $ARGUMENTS[0] to add general instructions to the context window.

2. Reserve the next global ID by running `python .claude/skills/scripts/reserve_id.py --type advisory --title '<short title>'`. Use the returned 6-digit ID.

3. **Load references on demand**: Before researching, load lazy references as needed from the "Available references" list emitted by pre-skill:
   - Load `project/conceptual-design-to-be.md` when comparing current vs. target design
   - Load `general/shared-definitions.md` when domain terminology is ambiguous
   - Load `general/report-conventions.md` before writing the advisory report
   - Load `general/review-perspectives.md` before evaluating from multiple perspectives

4. Research as needed to understand the user's question thoroughly. You may read the entire codebase, architecture docs, design docs, and any other relevant files to gather information. You may use these tools (without asking for authorization) to collect data and insights: Read, Search, and WebSearch.

5. **Expert analysis** — evaluate the question from multiple perspectives to ensure comprehensive, balanced advice.

   **Standard mode** (no `--deep` flag): Launch the `advisory-reviewer` agent (Agent tool, subagent_type=`advisory-reviewer`) with the question, relevant context files, and review depth. The agent evaluates the question against selected review perspectives and returns a perspective-by-perspective analysis with pros/cons. Use the agent's output as input to step 6.

   **Deep-dive mode** (`--deep` flag): Launch the `council-debate` agent (Agent tool, subagent_type=`council-debate`) with the question, selected council members, and relevant context. The agent assembles a 5-7 member expert council, runs a 2-round structured debate, and returns position statements, cross-examination, and synthesis. Use the agent's synthesis as input to step 6. Request brief-specific roles based on the question's domain (e.g., Agentic AI expert for agent-related questions, Data engineer for data pipeline questions). Council member definitions and debate format details live in `.claude/agents/council-debate.md`.

6. **Perspective synthesis** — Evaluate the question against all applicable engineering and design perspectives from `general/review-perspectives.md`, ensuring comprehensive domain coverage. In deep-dive mode, use the council debate from step 5 as input -- map each expert's positions to the relevant perspectives. For each relevant perspective, justify recommendations with pros and cons. Search the web for established and emerging best practices related to the user's question, and incorporate those into your analysis.

7. Answer the user's question with clear, actionable recommendations.

8. Save a report to the output file, including:
   - *header*: `# Advisory <id> | <prefix><scope> | <current datetime> | <short title>`
   - *user brief*, *agent interpretation*, *files* — per _references/general/report-conventions.md
   - *Q&A log*: the initial question and answer, numbered sequentially (follow-ups will be appended later)
   - *recommendations summary*: a concise list of all actionable recommendations made so far

9. Run /post-skill <id> to mark the brief as DONE and commit the report.

10. Present the recommendations summary and ask the user (text-based, not AskUserQuestion -- this is a mixed open-ended/closed-set decision point where freeform response is preferred):
   - "Do you have follow-up questions or want to explore a different angle?"
   - "Would you like to proceed with any of these recommendations?"
      - **Yes, execute now**: run /plan and then /implement. When spawning a plan via `/plan`, pass the current advisory ID so the plan can record `source: advisory-<id>`.
      - **Yes, but plan only**: run /plan (plan without executing). When spawning a plan via `/plan`, pass the current advisory ID so the plan can record `source: advisory-<id>`.

11. If the user has follow-up questions, continue the Q&A conversation:
    - Answer each follow-up with clear, actionable recommendations.
    - After each answer, ask if they have more questions.
    - When the Q&A concludes, update the report file by appending the additional Q&A pairs and updating the recommendations summary.
    - Commit the updated report.
