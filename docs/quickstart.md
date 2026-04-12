# Quickstart

This page gets you from zero to a running SEJA project in about 20
minutes, with no prior framework knowledge required. For the full
narrated version of this flow, with framework callouts and role
sidebars, see [how-to/greenfield-collocated.md](how-to/greenfield-collocated.md).

## The three commands

Run these three commands in order. Each is explained in the worked
example below. Nothing else needs to happen on this first screen:
you can start typing now and read the "why" afterwards.

```bash
/seed hello-seja
```

```bash
/design
```

```bash
/upgrade
```

## Worked example: hello-seja

We will walk you through a concrete run so you see a real result
before you leave this page. The project is a small personal task
tracker. The domain is "personal tasks and reminders". The stack
is Python plus SQLite. The mode is greenfield (new project, no
prior code to migrate).

### Step 1: `/seed hello-seja`

From an empty parent directory, you run:

```bash
/seed hello-seja
```

You will see SEJA copy its framework files into `hello-seja/.claude/`
and `hello-seja/_references/`. When the seed finishes, you have a
new SEJA-ready project directory containing the skills, rules, and
reference scaffolding the framework needs to operate. You then run
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
files under `_references/project/`, customized with your answers.

To confirm the files exist, you run:

```bash
ls _references/project/
```

You should see four markdown files listed. If you see them, the
design step worked and you can move on.

### Step 3: `/upgrade`

You do not need to run this on day one. It is here so you know
how to keep the framework fresh later, once a newer version of
SEJA has been published. When you do run it, you type:

```bash
/upgrade
```

SEJA pulls the latest framework files from the foundational repo
without touching anything under `_references/project/` or `_output/`.
Your design decisions and your plan and execution history stay
exactly where you left them. You can run `/upgrade` as often as
you like; it is non-destructive by construction.

## What just happened

You now have a SEJA project with four files under `_references/project/`:

- `conventions.md` captures your project directory layout and the
  framework variables the agents read at the start of every skill.
- `constitution.md` holds the immutable principles for this project,
  read-only for the framework agents after you approve it.
- `standards.md` captures your engineering standards for backend,
  frontend, testing, and i18n, so the agents know what "good" means
  in your codebase.
- `product-design-as-intended.md` is your working design intent, the
  file you will edit by hand as the project evolves and the file
  every planning session reads first.

The framework reads these four files at the start of every skill
invocation. You do not need to memorize the whole file inventory
yet: you have a running project, and that is enough for now.

## Now read concepts.md

You are ready for the conceptual model. The rest of the public
docs assume you have run the three commands above and want to
understand what SEJA is doing under the hood. Read
[concepts.md](concepts.md) next. It walks you through the framework
lifecycle, the sign system, and the profile-by-pattern matrix, so
you can decide which how-to to read first when you plan your first
real feature.
