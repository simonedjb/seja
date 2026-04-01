# Getting Started with SEJA

Three onboarding paths depending on your situation. Pick one and follow the steps.

## Prerequisites

- Claude Code installed and working (`claude --version`)
- A git repository (or a target directory where one will be created)

---

## Path 1: Demo Mode (5 minutes)

Best for users who want to see SEJA in action before committing to a project.

1. Run `/seed <target> --demo` to create a demo project with pre-filled design files.
2. Open `WALKTHROUGH.md` in the seeded project root.
3. Follow the guided tour through `/advise`, `/plan`, `/implement`, and `/check`.

**Expected output:** A demo project (TaskFlow) with pre-filled conventions, domain model, constitution, and metacommunication specs. The walkthrough guides you through each core skill with concrete examples.

**When done:** Run `/design` in the demo project to replace the demo configuration with your own, or discard the project and start fresh with Path 2.

---

## Path 2: New Project (20 minutes)

Best for users starting a greenfield project from scratch.

1. Run `/seed <target>` to copy the framework into a new directory.
2. Open a Claude Code session in the target directory.
3. Run `/design` and answer the questionnaire -- it covers project identity, stack choices, domain model, permissions, and metacommunication.
4. Review the generated specs in `_references/project/`:
   - `conventions.md` -- project identity and directory layout
   - `constitution.md` -- immutable quality principles
   - `conceptual-design-to-be.md` -- entity hierarchy and domain model
   - `metacomm-to-be.md` -- designer-to-user communication intentions
5. Optionally run `/plan --roadmap` to generate a full development roadmap.

**Expected output:** A fully configured project with conventions, domain model, standards files, and a generated `CLAUDE.md` tailored to your stack.

---

## Path 3: Existing Codebase Workspace (15 minutes)

Best for users adding SEJA alongside an existing project without modifying its structure.

1. Run `/seed <target> --workspace` to create a separate workspace directory.
2. Open a Claude Code session in the workspace directory (use the generated launcher script to include your codebase).
3. Configure `_references/project/conventions.md` with your codebase paths and stack details.
4. Run `/design` to define your domain model, standards, and metacommunication.
5. Start with `/advise` to ask questions grounded in your codebase context.

**Expected output:** A workspace alongside your codebase with its own git history, design specs, and SEJA framework -- keeping your codebase untouched.

---

## What's Next?

After completing any path:

- Run `/help --browse` to explore all available skills interactively.
- Run `/check health` to verify your framework setup is complete and consistent.
- Run `/plan` to create your first implementation plan.
- Run `/explain` to understand architecture, data models, or spec drift.
- See `general/skill-graph.md` for how skills connect and common multi-skill workflows.
