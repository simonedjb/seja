# Extending the Framework

## Overview

SEJA is designed to be extended. While the core framework provides a comprehensive set of skills, agents, review perspectives, and rules, every project has unique needs. You can add custom components at four extension points: skills, review perspectives, agents, and rules.

This page gives a brief overview of each extension type and the governance requirements that apply. For step-by-step instructions, see [Extension Guide](../architecture/extension-guide.md).

## Extension points

### Custom skills

Skills are slash commands backed by `SKILL.md` files. You can create new skills to automate project-specific workflows -- for example, a skill that generates release notes in your organization's format, or one that runs a domain-specific validation check.

Each skill needs:
- A `SKILL.md` file in `.claude/skills/<name>/` with YAML frontmatter following the agentskills.io specification.
- A `name` (lowercase, alphanumeric with hyphens, 1-64 characters), a `description` (up to 1024 characters), and `metadata` declaring its context budget, references, and any skipped pre-skill stages.
- A Quick Guide section with a plain-language description, example, and usage scenario.
- A body section with execution instructions.

Skills automatically inherit the pre-skill and post-skill pipeline -- they get brief logging, context loading, as-is alignment, commit handling, and next-step suggestions without any extra work. See [Skills, Agents, and the Execution Pipeline](skills-agents-pipeline.md) for how the pipeline works.

### Custom review perspectives

Review perspectives are domain-specific evaluation lenses. If your project has concerns not covered by the 16 built-in perspectives -- for example, regulatory compliance for a specific industry, or game design heuristics -- you can add custom perspective files.

Each perspective file lives in `_references/general/review-perspectives/` and follows the same structure as built-in perspectives: an Essential section with P0 questions and a Deep-dive section with P1-P4 questions. The perspective needs a short tag (like the existing SEC, UX, or PERF tags) and should be added to the perspective index for two-stage loading. See [Review Perspectives and Communicability](review-perspectives-and-communicability.md) for the perspective system's design.

### Custom agents

Agents are specialized subprocesses that skills delegate to. You can create new agents for domain-specific evaluation or generation tasks -- for example, an agent that reviews machine learning model configurations, or one that generates compliance reports.

Agent prompt files live in `.claude/agents/` and define the agent's role, inputs, evaluation criteria, and output format. Agents fall into the same three roles as built-in agents: evaluators (review one type of artifact through one lens), generators (produce one type of artifact from well-defined inputs), and executors (dynamically constructed for plan step execution).

Generator agents must receive the project constitution as part of their prompt to enforce trust boundaries.

### Custom rules

Rules are path-scoped instruction files that are auto-loaded when Claude works on files matching the rule's scope. They live in `.claude/rules/` and contain guidance specific to certain file patterns -- for example, rules for working with migration files, or rules for editing configuration files.

Each rule file declares its scope in YAML frontmatter (for example, `paths: ["migrations/**"]`) and contains instructions that apply only when files in that scope are being edited.

## Governance requirements

SEJA applies governance checks to prevent uncontrolled growth of framework components:

### Skill count justification

Before creating a new skill, you must demonstrate that its functionality cannot be a mode of an existing skill. The `/check` skill is the model here -- it consolidates 9 different check modes (validate, review, smoke, preflight, health, and others) into a single skill because they share a common execution pattern.

A new skill can justify independent existence when it meets 3 or more of these 4 criteria:
- **Distinct user intent and mental model** -- the user thinks of it as a fundamentally different action.
- **Disjoint reference sets** -- the skill needs different reference files than existing skills.
- **Incompatible execution topology** -- the skill's workflow structure differs significantly from existing skills.
- **Different output strategy** -- the skill produces a fundamentally different type of artifact.

### Agent single-responsibility

Each agent must operate on one type of artifact through one lens. You cannot create an agent that "reviews code AND generates documentation" -- those are two distinct responsibilities that belong in separate agents. This keeps agents focused, testable, and predictable.

### agentskills.io spec compliance

All skill frontmatter must conform to the agentskills.io universal specification. Top-level fields (`name`, `description`, `compatibility`) follow the spec directly. SEJA-specific fields are namespaced under `metadata` to avoid conflicts with future spec fields. Compliance is enforced by the `check_skill_spec.py` validation script.

## The meta-skills deferral

One extension pattern that SEJA explicitly does *not* support yet is **runtime skill generation** -- having agents create new `SKILL.md` files on the fly during execution. While this "Skill Factory" pattern could enable powerful dynamic workflows, it raises significant governance concerns:

- Generated skills could bypass the permission model.
- Generated skills could skip constitution injection.
- Generated skills could declare file-write permissions beyond their parent's scope.

The framework has deferred this capability until prerequisite safeguards are in place: a permission inheritance model, mandatory constitution injection for generated skills, and a constrained "skill template" factory pattern that limits what can be generated. This is a deliberate design decision -- the framework prioritizes safety and predictability over maximum flexibility.

For detailed instructions on creating each type of extension, see [Extension Guide](../architecture/extension-guide.md). For background on why the framework is structured this way, see [What Is SEJA and Why Does It Exist?](what-is-seja.md).
