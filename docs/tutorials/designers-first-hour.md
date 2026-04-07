# Your First Hour with SEJA

This tutorial walks you through a complete SEJA cycle in about 15 minutes. You will set up a demo project, describe your design intent, generate a plan, and see the result. By the end you will have experienced the core loop that every SEJA session follows.

**Prerequisite**: Read [How to Think About Working with SEJA](designers-mental-model.md) first. You need Claude Code installed -- that is all.

---

## Step 1: Set up the demo project

**Command**:

```
/seed . --demo
```

**Why**: The demo mode gives you a working project without needing to answer setup questions yet. It pre-fills a sample product so you can see real output immediately.

**Expected output** (abbreviated):

```text
Copying framework files...
Creating demo project configuration...
Files created:
  .claude/          -- skills, agents, and rules
  _references/      -- project design specs and standards
  _output/          -- where plans, reports, and logs go
Demo project ready. Run /design to review or customize.
```

You now have a fully configured SEJA project. The demo product is a task management app -- a familiar domain that makes the rest of the tutorial easy to follow.

---

## Step 2: Explore what was created

**Command**:

```
/explain architecture
```

**Why**: Before changing anything, understand what exists. The agent reads your project files and produces a visual summary.

**Expected output** (abbreviated):

```text
## Architecture Overview

The demo project is a task management app with:
- Backend: Flask + SQLAlchemy + PostgreSQL
- Frontend: React + TypeScript
- Key entities: User, Task, Tag
[Mermaid diagram showing entity relationships]
```

Take a moment to read the summary. Notice that you did not write any of this -- the agent assembled it from the project specs that `/seed --demo` created. This is the shared understanding the agent will use for every future interaction.

---

## Step 3: Plan a change

**Command**:

```
/plan Add a greeting message on the home page that welcomes the user by name
```

**Why**: Plans separate thinking from doing. You review the approach before any code changes.

**Expected output** (abbreviated):

```text
# Plan 000001 | FEATURE-F | ...

## Steps
### Step 1: Add greeting component
Create a WelcomeGreeting component that displays the user's name...
- Files: src/components/WelcomeGreeting.tsx (create)

### Step 2: Integrate into home page
Import and render the greeting component...
- Files: src/pages/Home.tsx (modify)

### Step 3: Add tests
...
```

Read the plan. If something seems wrong, tell the agent -- for example: "Step 1 should also handle the case where the user has no name set." The agent will revise the plan. This is where your design judgment matters most: shaping the approach before implementation begins.

---

## Step 4: Execute the plan

**Command**:

```
/implement 000001
```

**Why**: The agent follows the plan step by step. Each step is verified before moving to the next.

**Expected output** (abbreviated):

```text
Executing plan 000001...
Step 1/3: Add greeting component... done
Step 2/3: Integrate into home page... done
Step 3/3: Add tests... done
All steps completed. Running quality checks...
```

You do not need to watch every line of output. The agent commits to following the plan you approved. If a step fails, it will stop and explain what went wrong so you can decide how to proceed.

---

## Step 5: Check the result

**Command**:

```
/check review
```

**Why**: The framework reviews changes from multiple perspectives -- accessibility, security, UX -- so you don't have to think of everything.

**Expected output** (abbreviated):

```text
Review (Light)
- UX: Adopted -- greeting provides immediate personalization
- A11Y: Adopted -- component uses semantic HTML with proper heading level
- SEC: N/A -- no security-sensitive changes
```

Each perspective gives a verdict: **Adopted** (looks good), **Flagged** (needs attention), or **N/A** (not relevant to this change). If anything is flagged, the review explains why and suggests a fix.

---

## What you learned

You just completed a full SEJA cycle using five skills:

1. **`/seed`** -- set up the project structure
2. **`/explain`** -- understand what exists
3. **`/plan`** -- describe a change and review the approach
4. **`/implement`** -- execute the approved plan
5. **`/check`** -- verify the result from multiple perspectives

These skills form a cycle: **design -> plan -> implement -> check -> explain**. Real projects repeat this loop for every change, large or small. Your role as a designer is strongest at the plan and check stages, where design intent and quality judgment drive the outcome.

### Next steps

- [Solo Designer -- New Product](../journeys/journey-solo-designer-greenfield.md) -- follow a journey guide for a real project
- [Glossary](../glossary.md) -- look up terms you encountered
- [Recipes](../recipes/) -- find step-by-step instructions for specific tasks
- [Troubleshooting](designers-troubleshooting.md) -- solutions if something goes wrong
