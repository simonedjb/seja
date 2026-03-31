---
name: quickstart
description: "[RETIRED] Replaced by /seed + /design + /upgrade. Use /seed to copy the framework, /design to configure it, /upgrade to update it."
metadata:
  last-updated: 2026-03-31 16:30:00
  version: 1.0.0
  category: utility
  context_budget: light
  references: []
---

## Quick Guide

**This skill has been retired.** Use the following skills instead:

- `/seed` — Copy the SEJA framework into a new or existing project
- `/design` — Configure the framework (stack, conventions, domain model, standards)
- `/upgrade` — Update framework files to the latest version

# Quickstart (Retired)

This skill has been split into three focused skills:

- **`/seed`** — copies the SEJA framework into a new or existing project (runs from the seed repo). Handles greenfield, existing codebase, and workspace creation scenarios.
- **`/design`** — configures the framework for the project: stack, conventions, conceptual design, metacommunication, and standards (runs from the target project). Also handles ongoing design updates.
- **`/upgrade`** — upgrades framework files from the seed repo without touching project-specific files (runs from the target project). Replaces the old Mode 4.

## Migration

| Old workflow | New workflow |
|-------------|-------------|
| `/quickstart <target>` (Mode 1/2) | `/seed <target>`, then open `<target>` and run `/design` |
| `/quickstart --generate-spec` (Mode 3) | `/design --generate-spec` (from target project) |
| `/quickstart --upgrade` (Mode 4) | `/upgrade` (from target project) |
| `/quickstart --workspace` (Mode 5) | `/seed <target> --workspace` |

## Skill Boundaries

> **`/seed`** copies the framework. **`/design`** defines WHAT to build and WHY. **`/make-plan`** defines HOW to build it and WHY those "hows."

See advisory-000103 for the design rationale.
