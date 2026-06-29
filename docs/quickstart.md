---
diataxis: tutorial
freshness: release-bound
last-reviewed: 2026-05-05
---

# Quickstart

This page gets you from zero to a running SEJA project in about 20
minutes, with no prior SEJA knowledge required. For the full
narrated version of this flow, with harness callouts and role
sidebars, see [how-to/greenfield-collocated.md](how-to/greenfield-collocated.md).

Installation and upgrades share a single entry point: `/seja-setup`
is the unified install/upgrade command and dispatches by project
state -- it installs the harness when the target is empty, and
upgrades harness files in place when it detects an existing
SEJA project.

## The three commands

Run these three commands in order. Each is explained in the worked
example below. Nothing else needs to happen on this first screen:
you can start typing now and read the "why" afterwards.

```bash
/seja-setup hello-seja
```

```bash
/design
```

```bash
/seja-setup --upgrade
```

## Worked example: hello-seja

We will walk you through a concrete run so you see a real result
before you leave this page. The project is a small personal task
tracker. The domain is "personal tasks and reminders". The stack
is Python plus SQLite. The mode is greenfield (new project, no
prior code to migrate).

### Step 1: `/seja-setup hello-seja`

From an empty parent directory, you run:

```bash
/seja-setup hello-seja
```

You will see SEJA copy its harness files into `hello-seja/.claude/`
and `hello-seja/.claude/references/`. When the setup finishes, you have a
new SEJA-ready project directory containing the skills, rules, and
reference scaffolding the harness needs to operate. You then run
`cd hello-seja` and move on to the next command.

### Step 2: `/design`

From inside `hello-seja`, you run:

```bash
/design
```

You will be asked a short sequence of questions about your project.
For this worked example, you answer them as if you are building a
personal task tracker: the project name is `hello-seja`, the domain
is `personal tasks and reminders`, the stack is `Python + SQLite`,
and the mode is `greenfield`. SEJA then generates four project
files under `product-design/`, customized with your answers.

To confirm the files exist, you run:

```bash
ls product-design/
```

You should see four markdown files listed. If you see them, the
design step worked and you can move on.

### Step 3: `/seja-setup --upgrade`

You do not need to run this on day one. It is here so you know
how to keep the harness fresh later, once a newer version of
SEJA has been published. When you do run it, you type:

```bash
/seja-setup --upgrade
```

SEJA pulls the latest harness files from the foundational repo
without touching anything under `product-design/` or `_output/`.
Your design decisions and your plan and execution history stay
exactly where you left them. You can run `/seja-setup --upgrade` as
often as you like; it is non-destructive by construction.

If you want to pin to a specific SEJA release for reproducibility,
`/seja-setup` accepts `--version <tag>` (e.g. `v0.1.0`) in both
install and upgrade modes; see [how-to/upgrade.md -- Pinning to a specific release](how-to/upgrade.md#pinning-to-a-specific-release).

## What just happened

You now have a SEJA project with four files under `product-design/`:

- `conventions.md` captures your project directory layout and the
  harness variables the agents read at the start of every skill.
- `constitution.md` holds the immutable principles for this project,
  read-only for the harnessed agents after you approve it.
- `standards.md` captures your engineering standards for backend,
  frontend, testing, and i18n, so the agents know what "good" means
  in your codebase.
- `product-design-as-intended.md` is your working design intent, the
  file you will edit by hand as the project evolves and the file
  every planning session reads first.

The harness reads these four files at the start of every skill
invocation. You do not need to memorize the whole file inventory
yet: you have a running project, and that is enough for now.

## The canonical loop: what happens on iteration 2 and beyond

Once the project is designed, every subsequent change follows the
same seven-step loop. Walk through it once here so you recognise
the shape when you meet it in a real change. Check comes before
document and communicate -- validate before you communicate.

1. **`/research`** (or **`/explain`** as the alternative entry) --
   investigate what you are about to change. Start here on every
   iteration-2+ change, before you touch any intent or plan. Use
   `/research` for Q&A and recommendations; use `/explain` when
   you need a deeper narrative on behavior, code, data model, or
   architecture.

2. **`/design`** | **`/plan`** -- branch based on what research
   surfaced. Run `/design` when the intent itself needs to change
   (new decision, revised journey, updated standard). Run `/plan`
   when the intent is stable and you only need a plan to implement
   against it.

3. **`/implement`** -- execute the plan. SEJA runs the numbered
   steps, tracking progress and handling errors as it goes.

4. **`/critique`** -- validate before you communicate. Run the
   appropriate mode (`validate`, `review`, `preflight`, `smoke`,
   or `health`) to confirm the change is sound. This gate is
   deliberately placed before documentation so you never document
   something that fails its own checks.

5. **`/document`** | **`/communicate`** -- record the change and,
   when appropriate, share it. `/document` updates user and
   developer documentation based on the plan's Docs fields or
   auto-detected changes. `/communicate` generates tailored
   stakeholder material for a specific audience.

6. **`/reflect`** -- close the cycle. `/reflect` surfaces patterns
   across recent skill runs and anchors a short reflection on the
   artifacts you just produced. This is the cycle-closing step; it
   is what turns a sequence of commands into learning you can reuse
   on the next iteration.

When specs and as-coded state fall out of alignment, run
`/explain spec-drift` to compare them and surface what needs to
change; it feeds back into `/design` or `/plan` naturally.

## Now read concepts.md

You are ready for the conceptual model. The rest of the public
docs assume you have run the three commands above and want to
understand what SEJA is doing under the hood. Read
[concepts.md](concepts.md) next. It walks you through the harness
lifecycle, the sign system, and the profile-by-pattern matrix, so
you can decide which how-to to read first when you plan your first
real feature.
