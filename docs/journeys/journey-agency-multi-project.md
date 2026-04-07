# Journey: Agency -- Multiple Client Projects

## Who this is for

An agency, consultancy, or freelancer managing multiple client projects, who wants consistent quality across all projects while keeping the foundational framework, each client's codebase, and output artifacts physically separated.

## Why this journey

Agencies need consistent quality across client projects while keeping each project's design history and configuration independent. The workspace pattern -- where the framework lives in a separate git repo pointing at the client codebase -- solves this by giving each project its own conventions, design specs, and output artifacts without modifying the client's code.

When the foundational framework is updated, `/upgrade` pulls changes into each workspace independently. The context budget system supports absolute paths, so workspaces can point at codebases anywhere on disk.

For the concepts behind this workflow, see [Context Budget and References](../concepts/context-budget-and-references.md) and [Extending the Framework](../concepts/extending-the-framework.md).

## What you'll accomplish

A single foundational SEJA framework and independent *ClientName* workspaces per client codebase, with consistent conventions and the ability to upgrade all workspaces when the foundational framework evolves.

## Prerequisites

- Claude Code installed
- The foundational SEJA framework available (as a cloned repo or downloaded ZIP)
- Familiarity with git

## Step-by-step walkthrough

### Step 1: Share the foundational framework

Share the foundational SEJA framework by pointing team members to the SEJA repository. They can clone it or download it as a ZIP from GitHub. The repository contains all skills, references, templates, and scripts -- ready to seed any number of client workspaces.

Expected output: team members have a local copy of the foundational framework.

### Step 2: Set up a workspace per client codebase

For each client codebase, use `/seed --workspace` (or `create_workspace.py`) to create a *ClientName* workspace from the foundational framework. This automates: creating the directory, running `git init`, copying framework files, setting up `_output/`, and configuring absolute paths to the client codebase. The workspace is its own git repo -- tracking framework configuration, conceptual design, plans, advisories, and all output artifacts independently of the *ClientName* codebase:

```
d:\workspaces\client-a\      <-- ClientA workspace (its own git repo)
  .claude/                   <-- copied from foundational framework
  _references\           <-- copied + project-specific files generated
  _output\                    <-- plans, advisories, briefs (version-controlled here)
d:\git\client-a-project\     <-- ClientA codebase (added via --add-dir)
```

See the [workspace setup recipe](../recipes/recipe-workspace-setup.md) for detailed instructions.

### Step 3: Bootstrap each client workspace

In each *ClientName* workspace, run `/seed .` then `/design` and walk through the questionnaire for that specific client's codebase. Set absolute paths in `project/conventions.md`: `OUTPUT_DIR` should point inside the workspace (e.g., `D:/workspaces/client-a/_output`) so output artifacts are version-controlled alongside the framework configuration. `BACKEND_DIR` and `FRONTEND_DIR` point at the *ClientName* codebase. Start the agent from the workspace with the generated launcher script or your host's equivalent additional-directory workflow.

Expected output: all `project/*.md` files generated for the client project.

### Step 4: Generate client-facing material

Use `/communication EVL` (for evaluators/CTOs) or `/communication CLT` (for clients/budget owners) to generate tailored material about the project. Each audience segment gets content structured for their specific questions.

Expected output: communication files in the output directory.

### Step 5: Maintain consistency across workspaces

All client workspaces originate from the same foundational SEJA framework. When the foundational framework is updated, pull the latest version of the foundational framework repository and run `/upgrade` on each workspace. The upgrade preserves all project-specific files while updating framework files.

Expected output: updated framework files in each workspace with project-specific files intact.

### Step 6: Scale the team per client codebase

When a client codebase needs more people, use `/onboarding <role> <level>` to generate tailored onboarding plans. Each new team member gets their own *ClientName* workspace pointing to the shared client codebase.

Expected output: a role-specific onboarding plan in the output directory.

## What to do next

- [Set up a project workspace](../recipes/recipe-workspace-setup.md) (essential for this journey)
- [Bootstrap a greenfield codebase](../recipes/recipe-bootstrap-greenfield.md)
- [Generate stakeholder material](../recipes/recipe-stakeholder-material.md)
- [Upgrade the foundational framework](../recipes/recipe-upgrade-framework.md)
- For the full framework reference, see the [onboarding guide](../claude-onboarding-guide.md).
