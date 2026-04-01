# Codex Onboarding Guide: Starting a New Project with `.codex`

*For product designers new to AI-assisted development*

---

## Part 0 - Start Here

The **SEJA repository** is the starting point for a new Codex-powered project. Clone it from GitHub (`git clone https://github.com/simonedjb/seja.git`) or download it as a ZIP (Code > Download ZIP), copy the framework files into a new repository, and then let Codex customize it for your project.

If you have seen older SEJA material before, pause here for one important update: the Codex toolkit was **consolidated**. A number of older separate skills were folded into a smaller set of more capable ones. The guide below reflects the current framework, not the older 26-skill layout.

### 0.1 What Is In the Kit?

The SEJA repository contains **145 project-independent framework files**:

| Category | Count | What it means |
|----------|-------|---------------|
| Skill definitions | 16 | The actual reusable workflows in `.codex/skills/<name>/SKILL.md` |
| User-facing skills | 14 | The skills you will normally invoke yourself; `$pre-skill` and `$post-skill` are internal lifecycle hooks |
| Skill UI metadata | 14 | `agents/openai.yaml` files that help Codex hosts present each skill cleanly |
| General references | 12 | Shared standards, constraints, report conventions, onboarding indexes, communication references, and framework-wide guidance |
| Review perspective files | 16 | Individual engineering and design review lenses |
| Onboarding profile files | 8 | Role-family and level profiles used by `$onboarding` |
| Communication profile files | 5 | Audience-specific communication references |
| Templates | 31 | Reusable `template/*.md` and `template/*.json` files used during `$design` |
| Agent definitions | 5 | Specialized delegated agents such as `code-reviewer` and `test-runner` |
| Rule definitions | 7 | Path-scoped coding guidance used automatically by Codex |
| Scripts | 29 | Validation, indexing, packaging, migration, and support scripts |
| Framework metadata | 4 | `.codex/README.md`, `.codex/CHEATSHEET.md`, `.codex/CHANGELOG.md`, and `.codex/skills/VERSION` |

### 0.2 What Changed From Older Versions?

If you encounter an older screenshot, note, or workshop artifact, the command names may differ.

| Older pattern | Current pattern | Why it matters |
|---------------|-----------------|----------------|
| `$validate`, `$review-code`, `$smoke-test`, `$preflight`, `$plan-user-test` | `$check validate`, `$check review`, `$check smoke`, `$check preflight`, `$check test-plan` | Most quality-related workflows now live under one skill |
| `$metacomm` | `$plan --framing metacomm` | Design-intent planning is now part of planning, not a separate skill |
| `$roadmap` | `$plan --roadmap` | Roadmap generation was folded into planning |
| `$inventory` | `$advise --inventory` | Inventory is now a mode of advisory work |

For a first-time designer, this is good news: there are fewer names to memorize.

### 0.3 Your First 15 Minutes

1. Create a new repository and initialize git.
2. Run `$seed <target>` to copy the framework files (`.codex/` and `_references/`) from the SEJA repository into the repository root.
3. Start Codex from that root folder.
4. Run `$design` to configure project-specific files.
5. Answer the questions in product language, not implementation jargon.
6. When design finishes, choose "Review specs now" to walk through each generated file -- treat them like a design brief.
7. Then choose "Generate roadmap" to create a development roadmap from your specs, or use `$plan` for your first feature.

That sequence gives Codex enough project context while keeping you focused on product intent.

---

## Part 1 - What Codex Is, In Designer Terms

Codex is not just a chatbot that suggests code. It is an **AI coding agent** that can inspect the project, edit files, run commands, and explain what it did.

For a product designer, the most useful mental model is:

- You bring the product goal, user perspective, and design constraints.
- Codex helps translate that intent into plans, code changes, tests, and project documentation.
- You stay responsible for direction and judgment.
- Codex handles a lot of the mechanical effort of tracing files, making edits, and checking for regressions.

You do **not** need to know every implementation detail before getting value from the toolkit. A strong prompt can be plain-language product thinking such as:

> "When a new user opens the dashboard for the first time, I want the next step to feel obvious and low-stress."

That is enough to start a planning conversation.

---

## Part 2 - The Project Structure You Will Work With

After unzipping the kit and running `$seed` followed by `$design`, the project normally looks like this:

```text
your-project/
|-- AGENTS.md
|-- _references/
|   |-- general/            (universal conventions, perspectives, onboarding)
|   |-- template/           (templates instantiated by $design)
|   `-- project/            (project-specific standards, generated per-project)
|-- .codex/
|   |-- README.md
|   |-- CHEATSHEET.md
|   |-- CHANGELOG.md
|   |-- agents/
|   |-- rules/
|   `-- skills/
`-- _output/
```

Here is the practical meaning of each layer:

| Layer | Why you should care |
|-------|---------------------|
| `AGENTS.md` | The top-level operating guide Codex reads first |
| `_references/project/*.md` | The project-specific knowledge base created by `$design` |
| `.codex/skills/` | Reusable workflows you can invoke with `$...` |
| `.codex/rules/` | Automatic guidance applied when Codex edits matching files |
| `.codex/agents/` | Specialized delegated agents used by some workflows |
| `_output/` | Plans, advisory logs, onboarding docs, Q&A logs, and related generated artifacts |

The important beginner insight is this: after setup, you will spend much more time using `AGENTS.md`, `project/*.md`, and a handful of skills than browsing the raw framework internals.

---

## Part 3 - Bootstrapping a New Project

### 3.1 Copy the Framework Files

Run `$seed <target>` to copy `.codex/` and `_references/` from the SEJA repository so they land directly in the project root.

### 3.2 Start Codex From the Project Root

Codex should be launched from the same folder that contains `AGENTS.md` and `.codex/`. That ensures it sees the project guidance immediately.

### 3.3 Run Design

Use:

```text
$design
```

If this is your first AI-assisted project, choose the **interactive** path. It is slower for a few minutes, but it produces much better project guidance.

### 3.4 What Design Will Produce

Design turns the portable kit into a project-specific workspace. It will typically:

- generate `AGENTS.md`
- create `_references/project/*.md` files from templates
- tailor rules and agents to your stack
- prepare smoke-test scaffolding when your stack needs it
- create an output area for plans, advisory notes, and logs

### 3.5 How Designers Should Answer the Questions

You do not need to answer like an engineer. Prefer answers that describe:

- who the users are
- what the product does
- what the main workflows are
- which constraints matter most
- what quality standards are non-negotiable

Good example:

> "This product helps graduate students organize research notes and discuss papers collaboratively. The first-run experience needs to feel calm, trustworthy, and low-friction."

Less helpful example:

> "Use React because it is modern."

The first answer gives Codex product intent. The second is only a tool choice.

---

## Part 4 - The Skills You Will Actually Use

The current Codex toolkit has **14 user-facing skills**, but as a new designer you can start with a much smaller working set.

### 4.1 Best First Skills

| Skill | Use it when |
|-------|-------------|
| `$help` | You do not know which workflow to use |
| `$seed` / `$design` | You are setting up or configuring a project |
| `$plan` | You want a plan before implementation |
| `$explain` | You want the system or code explained in plain language |
| `$check` | You want to validate, review, smoke-test, or preflight |
| `$communication` | You need material for clients, evaluators, end users, or academics |
| `$onboarding` | You want a tailored onboarding plan for a teammate |

### 4.2 The Full Current User-Facing Set

- `$advise`
- `$check`
- `$communication`
- `$implement`
- `$explain`
- `$generate-script`
- `$help`
- `$plan`
- `$onboarding`
- `$qa-log`
- `$seed`
- `$design`
- `$upgrade`
- `$update-tests`

### 4.3 The Easiest Way To Remember Them

Think in clusters:

- **Understand**: `$help`, `$explain`, `$advise`
- **Plan and build**: `$plan`, `$implement`
- **Check quality**: `$check`, `$update-tests`
- **Support the team**: `$communication`, `$onboarding`, `$qa-log`
- **Set up the framework**: `$seed`, `$design`, `$upgrade`

---

## Part 5 - Day-to-Day Workflows for Designers

### 5.1 Plan Before Building

This is the safest and most educational default:

```text
$plan Add a first-run onboarding flow that helps a new user create their first project without reading documentation.
```

Codex will inspect the project, write a plan, and give you something concrete to review before code changes begin.

### 5.2 Express Design Intent Directly

When the brief is primarily about what the interface should communicate, use metacomm framing:

```text
$plan --framing metacomm When a user opens the dashboard, I want the most important next step to feel obvious and reassuring.
```

This is especially useful for product designers because it starts from communicative intent instead of implementation detail. Your metacommunication message is recorded **verbatim** -- the framework preserves your exact wording because precise phrasing carries design intent that paraphrasing would distort.

### 5.3 Ask For Explanations Without Pretending To Know The Code

```text
$explain behavior Walk me through what happens from sign-up to first successful project creation.
$explain architecture Why is the system organized this way?
$explain code How does the dashboard loading flow work?
$explain data-model Describe the permissions model.
```

If something feels confusing, ask. That is faster and safer than guessing.

### 5.4 Get Advice Or Inventory What Already Exists

```text
$advise Should the settings flow be a modal or a full page?
$advise --inventory List all onboarding-related UI flows and where they live.
```

Use the advisory mode for trade-offs. Use the inventory mode when you need a map of what is already in the project.

### 5.5 Build Small, Reviewable Changes

For a modest change that is already well scoped:

```text
$plan Add a clearer empty state to the dashboard when a user has no projects yet.
```

Then review the plan and run `$implement <id>`.

---

## Part 6 - Quality Checks You Should Actually Run

The biggest consolidation in the current framework is the **`$check` skill**. Most “is this good?” workflows now live there.

### 6.1 The Core Commands

```text
$check validate
$check review staged
$check smoke api
$check preflight
$check test-plan Test the new first-run onboarding flow.
```

### 6.2 What Each Mode Means

| Command | What it does |
|---------|--------------|
| `$check validate` | Runs validation scripts such as consistency and convention checks |
| `$check review staged` | Reviews staged code changes across engineering and design perspectives |
| `$check smoke api` | Runs smoke tests to see whether major flows still work |
| `$check preflight` | Combines validation and review before a commit or merge |
| `$check test-plan ...` | Produces a manual user test plan from a recent change or feature brief |

### 6.3 The Recommended Designer Routine

1. Use `$plan` for the change.
2. Let Codex implement or help implement it.
3. Run `$check validate`.
4. Run `$check review staged`.
5. Run `$check smoke ...` when the feature affects live behavior.
6. If other humans will verify the result, run `$check test-plan ...`.

This routine keeps design intent, code quality, and user-facing behavior tied together.

---

## Part 7 - Communication and Team Support

Two workflows are especially valuable for designers working with other people.

### 7.1 Communication

Use `$communication` when you need the same project described differently for different audiences.

```text
$communication clients
$communication evaluators
$communication end-users
$communication --all
```

This is useful when your design work has to travel beyond the product team.

### 7.2 Onboarding

Use `$onboarding` when a new teammate joins.

```text
$onboarding shaper L2 Alice
$onboarding builder L1 Bob --area frontend
```

A product designer is usually a **shaper** in this framework. The onboarding skill generates a structured, role-aware plan instead of leaving the new person to learn everything ad hoc.

---

## Part 8 - Prompting Tips for Product Designers

The best prompts usually include four things:

- who the user is
- what they are trying to do
- what feels wrong or incomplete now
- what success should feel like

Examples:

Good:

> "Help me plan a first-run experience for researchers creating their first study. I want the flow to feel calm and guided, not bureaucratic."

Good:

> "Review this dashboard change with extra attention to accessibility and whether the primary action is visually obvious on mobile."

Less useful:

> "Improve the UX."

That shorter prompt is too vague. Codex works much better when you describe the user situation and the intended effect.

---

## Part 9 - Common Pitfalls

### Pitfall 1: Treating Codex Like A Magic Box

Codex is powerful, but you still need to review plans, diffs, and quality checks.

### Pitfall 2: Executing Without Reviewing the Plan

When you are still learning the codebase or the framework, always review the plan before running `$implement`.

### Pitfall 3: Using Old Command Names

If an older note says `$validate` or `$metacomm`, translate it to the current consolidated command set.

### Pitfall 4: Skipping Project Guidance Updates

If the product changes, keep `AGENTS.md` and the `project/*.md` files current. Codex can only follow the guidance that exists.

### Pitfall 5: Thinking You Need To Sound Technical

You do not. Plain-language product intent is often the highest-value input a designer can provide.

---

## Part 10 - Quick Reference

### Start a New Project

```text
$seed <target>
$design
```

### Plan A Feature

```text
$plan Add a better first-run dashboard state for new users.
```

### Plan From Design Intent

```text
$plan --framing metacomm When a user lands here, the next step should feel obvious and low-stress.
```

### Execute A Saved Plan

```text
$implement <plan-id>
```

### Ask For Advice

```text
$advise Should this be a modal or a full page?
```

### Inventory Existing Patterns

```text
$advise --inventory List all invitation-related flows.
```

### Explain The System

```text
$explain behavior Walk me through the checkout flow.
```

### Check Quality

```text
$check validate
$check review staged
$check smoke api
$check preflight
```

### Generate A Manual Test Plan

```text
$check test-plan Test the new onboarding flow for first-time users on mobile.
```

### Create Stakeholder Material

```text
$communication clients
```

### Onboard A New Teammate

```text
$onboarding shaper L2 Alice
```

### If You Are Unsure What To Do Next

```text
$help
$help --browse
```

---

## Final Recommendation

If you are a product designer using AI-assisted development for the first time, keep your first week simple:

1. Set up one project with `$seed` and `$design`.
2. Always review the plan before running `$implement`.
3. Ask for explanations whenever the code or terminology feels opaque.
4. Use `$check` as your safety net before trusting a change.
5. Keep describing the product in user-centered language.

That is enough to become productive without pretending to be a full-time engineer.
