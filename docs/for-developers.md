# SEJA for Developers

You are comfortable with agentic tools and want to understand how SEJA works under the hood -- the execution pipeline, context management, and how to extend the framework with custom skills, perspectives, or agents.

## Start here

- [SEJA Internals Walkthrough](tutorials/developers-internals-walkthrough.md) -- trace one complete skill invocation from command to git commit

## Architecture

- [Framework File Map](architecture/framework-file-map.md) -- what each directory and file category does
- [Skill Execution Pipeline](architecture/skill-execution-pipeline.md) -- the full pre-skill -> skill -> post-skill lifecycle
- [Context Strategy](architecture/context-strategy.md) -- how the framework manages LLM context constraints
- [Design Rationale](architecture/design-rationale.md) -- why key architectural decisions were made
- [Troubleshooting](architecture/troubleshooting.md) -- diagnosing and fixing framework issues

## Extend the framework

- [Extension Guide](architecture/extension-guide.md) -- step-by-step instructions for adding skills, perspectives, agents, rules
- [Extending the Framework](concepts/extending-the-framework.md) -- conceptual overview of governance and extension points

## Understand the concepts

- [Skills, Agents, and the Pipeline](concepts/skills-agents-pipeline.md) -- conceptual overview of the execution model
- [Context Budget and References](concepts/context-budget-and-references.md) -- how reference loading works

## Workflows

- [Bootstrap a Greenfield Project](recipes/recipe-bootstrap-greenfield.md)
- [Plan and Execute a Change](recipes/recipe-plan-and-execute.md)
- [Run Quality Gates](recipes/recipe-quality-gates.md)

## Quick reference

See the [Glossary](glossary.md) for key terms.
