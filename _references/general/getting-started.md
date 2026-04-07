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
   - `design-intent-to-be.md` -- entity hierarchy, domain model, and designer-to-user communication intentions
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

---

## Theoretical Foundations

SEJA's design and review perspectives draw on Semiotic Engineering (SemEng), a theory of Human-Computer Interaction that views software as computer-mediated human communication between designers and users.

### Component-to-Source Mapping

| SEJA Component | Theoretical Source | Reference |
|---|---|---|
| Metacommunication template (`metacomm-as-is.md`, `metacomm-to-be.md`) | Metacommunication Template + Extended Metacommunication Template | de Souza (2005), Ch. 3; SigniFYIng Message in de Souza et al. (2016), Ch. 3 ss3.1 |
| CEM taxonomy in UX/DX review perspectives | Communicability Evaluation Method (CEM) | de Souza (2005), Ch. 4 pp.123-138; de Souza & Leitao (2009) |
| `/check semiotic-inspection` mode | Semiotic Inspection Method (SIM) | de Souza et al. (2010); SigniFYIng Interaction in de Souza et al. (2016), Ch. 3 ss3.2 |
| Sign classification (static, dynamic, metalinguistic) in UX perspective | SemEng sign classes | de Souza (2005), Ch. 3; de Souza & Leitao (2009) |
| CDN dimensions in API perspective | Cognitive Dimensions of Notations (CDN) Framework | Blackwell & Green (2003); adapted for APIs in SigniFYIng APIs, de Souza et al. (2016), Ch. 3 ss3.4 |
| Intent-effect-failure items in API perspective | SigniFYIng APIs communicability analysis | de Souza et al. (2016), Ch. 3 ss3.4; Afonso (2015) |
| Cross-sign-class quality checks in semiotic-inspection | SigniFYIng Interaction quality dimensions | de Souza et al. (2016), Ch. 3 ss3.2 pp.70-71 |
| Design intent / as-is / established artifact model | Reflective practice (forward/backward SigniFYI usage) | Schon (1983); de Souza et al. (2016), Ch. 3 p.50 |

### Key References

- de Souza, C. S. (2005). *The Semiotic Engineering of Human-Computer Interaction*. MIT Press.
- de Souza, C. S. & Leitao, C. F. (2009). *Semiotic Engineering Methods for Scientific Research in HCI*. Morgan & Claypool.
- de Souza, C. S., Leitao, C. F., Prates, R. O., Bim, S. A. & da Silva, E. J. (2010). Can inspection methods generate valid new knowledge in HCI? *IJHCS*, 68(1-2), 22-40.
- de Souza, C. S., Cerqueira, R. F. G., Afonso, L. M., Brandao, R. R. M. & Ferreira, J. S. J. (2016). *Software Developers as Users: Semiotic Investigations in Human-Centered Software Development*. Springer.
- Blackwell, A. & Green, T. (2003). Notational systems -- the Cognitive Dimensions of Notations framework. In Carroll (Ed.), *HCI Models, Theories, and Frameworks*, pp.103-133.
- Schon, D. A. (1983). *The Reflective Practitioner: How Professionals Think in Action*. Basic Books.
