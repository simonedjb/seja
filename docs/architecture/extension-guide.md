# Extension Guide

This page provides step-by-step instructions for extending the SEJA framework with new skills, review perspectives, agents, and rules. Each section covers the technical requirements, governance criteria, and registration steps.

For a conceptual introduction to these components, see [Skills, Agents, and the Pipeline](../concepts/skills-agents-pipeline.md).

---

## Adding a New Skill

### 1. Governance Gate

Before creating a new skill, justify that its functionality cannot be delivered as a mode of an existing skill. The `/check` consolidation (9 modes in one skill) is the model for skills that share a common execution pattern.

A new skill must meet **3 or more** of these 4 criteria to justify independent existence:

- **(a) Distinct user intent and mental model** -- the user thinks of this as a fundamentally different action, not a variant of an existing one.
- **(b) Disjoint reference sets** -- the skill loads a different set of reference files from any existing skill.
- **(c) Incompatible execution topology** -- the skill's execution flow (sequential, parallel, interactive, batch) differs from existing skills that could host it.
- **(d) Different output strategy** -- the skill produces a different type of output artifact in a different location.

Document this justification when proposing the skill. The current count is 15 skills (13 user-facing + 2 internal lifecycle hooks).

### 2. Create the SKILL.md File

Create a new directory and file at `.claude/skills/<name>/SKILL.md`. The skill name must:

- Be 1-64 characters long
- Use only lowercase alphanumeric characters and hyphens
- Not conflict with existing skill names

### 3. Write the YAML Frontmatter

The frontmatter follows the [agentskills.io](https://agentskills.io) universal specification. Top-level fields conform to the spec; SEJA-specific fields are namespaced under `metadata` to avoid conflicts.

Required fields:

```yaml
---
name: my-new-skill
description: "One-line description of what this skill does."
argument-hint: "<required-arg> [--optional-flag]"
compatibility: "Designed for Claude Code with SEJA framework"
metadata:
  last-updated: 2026-04-06 12:00 UTC
  version: 1.0.0
  category: analysis|planning|utility
  context_budget: light|standard|heavy
  references:
    - general/some-reference.md
    - project/some-project-file.md
  eager_references:
    - general/some-reference.md
---
```

Key metadata fields:

- `context_budget` -- determines how much context the pre-skill pipeline loads. See [Context Strategy](context-strategy.md).
- `references` -- list of reference file paths (relative to `_references/`) that this skill may need.
- `eager_references` -- subset of `references` to load upfront. Remaining refs become lazy (demand-pull mode). Omit this field entirely for eager-only loading.
- `skip_stages` -- list of non-critical pre-skill stage IDs to skip (allowed values: `help`, `orphan-check`, `compaction-check`, `constitution`).

### 4. Write the Skill Body

After the frontmatter, write the skill's instructions as Markdown. Include a `## Quick Guide` section with a designer-friendly description, example usage, and a usage scenario. This section is displayed when users run `/my-new-skill --help`.

The skill body has access to all references loaded during pre-skill and can request lazy references on demand. Skills may spawn subagents by referencing prompt files in `.claude/agents/`.

### 5. Validate

Run `python .claude/skills/scripts/check_skill_spec.py` to validate the SKILL.md frontmatter against the agentskills.io spec. Fix any reported issues.

### 6. Register

Register the new skill in `skills-manifest.json`. You can either edit the file manually or regenerate it by running `python .claude/skills/scripts/generate_skills_manifest.py`, which discovers all SKILL.md files and produces the manifest.

### 7. Update Framework Structure

Update the skill count and inventory in `.claude/rules/framework-structure.md` to reflect the addition.

---

## Adding a New Review Perspective

### 1. Create the Perspective File

Create a new file at `_references/general/review-perspectives/<tag>.md`, where `<tag>` is a short uppercase identifier (e.g., `PERF`, `SEC`, `A11Y`).

### 2. Structure the Content

Each perspective file contains two sections:

**Essential section** -- 3 to 7 P0 (critical/blocking) questions. These are always evaluated during reviews.

```markdown
## Essential

- [P0] Is the API contract backward-compatible with existing clients?
- [P0] Are breaking changes documented in the changelog?
- [P0] Does the error response format follow the project standard?
```

**Deep-dive section** -- 8 to 12 questions classified P1 through P4, sorted by priority within the section. These are loaded for thorough reviews or when the perspective is the primary focus.

```markdown
## Deep-dive

- [P1] Are pagination defaults appropriate for the expected data volume?
- [P2] Does the API support filtering and sorting consistently?
- [P3] Are rate limiting headers included in responses?
- [P4] Is the API discoverable via HATEOAS links or an OpenAPI spec?
```

Priority classifications:
- **[P0]** -- Critical/blocking. Must be addressed before merge.
- **[P1]** -- High priority. Should be addressed in the same release.
- **[P2]** -- Medium priority. Address in a follow-up if not feasible now.
- **[P3]** -- Low priority. Nice to have.
- **[P4]** -- Informational. Awareness item, no action required.

### 3. Register in the Index

Add the new perspective to `_references/general/review-perspectives-index.md`. This is the compact index used by the two-stage loading protocol. Include the tag, name, and a one-line scope description.

### 4. Update Counts

Update the perspective count in `.claude/rules/framework-structure.md`. The current count is 16 perspectives (11 engineering + 5 design).

### 5. Regenerate the Essential Summary

Run `python .claude/skills/scripts/generate_essential_perspectives_summary.py` to update the auto-generated Essential summary file.

---

## Adding a New Agent

### 1. Governance Gate

New agents must justify that their domain is distinct from all existing agents. Agents follow a strict single-responsibility principle organized by role:

- **Evaluator** -- reviews one type of artifact through one lens. Does not modify project files. Each evaluator has a distinct artifact type: code diffs (`code-reviewer`), plans (`plan-reviewer`), design decisions (`advisory-reviewer`), structured debates (`council-debate`), validation results (`standards-checker`), test suites (`test-runner`), migrations (`migration-validator`).
- **Generator** -- produces one type of artifact from well-defined inputs. Invoked by thin-skill wrappers, not directly by users. Each generator has a distinct output type: communication material (`communication-generator`), onboarding plans (`onboarding-generator`), documentation (`document-generator`).
- **Executor** -- dynamically constructed by `/implement` auto mode. Not standalone prompt files.

Do not merge agents or add cross-cutting responsibilities to existing agents. The current count is 10 agents (7 evaluator + 3 generator).

### 2. Create the Agent Prompt File

Create a new file at `.claude/agents/<name>.md`. The filename should clearly indicate the agent's role and domain (e.g., `code-reviewer.md`, `communication-generator.md`).

### 3. Define the Agent's Scope

The prompt file should specify:

- What artifact type the agent operates on
- What lens or criteria it applies
- What output format it produces
- What references it needs (if any)

### 4. Trust Boundary Enforcement

**Generator agents must receive the project constitution** as part of their prompt. This ensures generated artifacts respect the project's immutable principles. The thin-skill wrapper that invokes the generator is responsible for injecting the constitution.

Evaluator agents operate in a read-only advisory capacity and do not require constitution injection, but they must respect the permission boundaries defined in `permissions.md`.

### 5. Update Framework Structure

Update the agent count and inventory in `.claude/rules/framework-structure.md`.

---

## Adding a New Rule

### 1. Create the Rule File

Create a new file at `.claude/rules/<name>.md`. Rule files are Markdown documents with YAML frontmatter.

### 2. Define the Path Scope

Rules are path-scoped: they are auto-loaded by Claude whenever the user (or an agent) edits files matching the rule's glob pattern. The pattern is declared in the `paths` field of the YAML frontmatter:

```yaml
---
paths:
  - "backend/**"
  - "src/api/**"
---
```

When Claude opens or edits a file matching any of these patterns, the rule's content is automatically injected into context. This provides automatic standards enforcement without requiring skills to explicitly load the rule.

### 3. Write the Rule Content

The body of the rule file contains the standards, conventions, and constraints that apply to files in the rule's scope. Keep rules focused -- each rule should cover a single domain (e.g., backend code, frontend code, test files, migrations).

Existing rules and their scopes:

| Rule | Pattern |
|------|---------|
| `framework-structure.md` | `.claude/**` |
| `backend.md` | Backend source files |
| `frontend.md` | Frontend source files |
| `tests.md` | Test files |
| `migrations.md` | Migration files |
| `i18n.md` | Internationalization files |
| `e2e.md` | End-to-end test files |

### 4. Update Framework Structure

Update the rule count in `.claude/rules/framework-structure.md`. The current count is 7 rule files.

---

## Checklist Summary

### New Skill
- [ ] Justify 3/4 governance criteria
- [ ] Create `.claude/skills/<name>/SKILL.md` with valid frontmatter
- [ ] Include `## Quick Guide` section
- [ ] Validate with `check_skill_spec.py`
- [ ] Register in `skills-manifest.json`
- [ ] Update `framework-structure.md`

### New Review Perspective
- [ ] Create `_references/general/review-perspectives/<tag>.md`
- [ ] Include Essential (3-7 P0) and Deep-dive (8-12 P1-P4) sections
- [ ] Add to `review-perspectives-index.md`
- [ ] Regenerate Essential summary
- [ ] Update `framework-structure.md`

### New Agent
- [ ] Justify distinct domain
- [ ] Create `.claude/agents/<name>.md`
- [ ] Choose role: evaluator or generator
- [ ] Ensure constitution injection for generators
- [ ] Update `framework-structure.md`

### New Rule
- [ ] Create `.claude/rules/<name>.md`
- [ ] Define `paths:` glob pattern in frontmatter
- [ ] Write focused, single-domain content
- [ ] Update `framework-structure.md`
