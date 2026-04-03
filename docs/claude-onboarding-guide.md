# Claude Onboarding Guide: Starting a New Project with Claude Code

*For product designers new to AI-assisted development*

---

## Part 0 -- Getting the Starter Kit

Before anything else, you need the **SEJA repository**. Clone it from GitHub or download it as a ZIP file -- it contains all the portable skills, references, templates, agents, and validation scripts you'll need.

### 0.1 What's in the Repository?

The SEJA repository contains approximately 185 framework files organized in the `.claude/` and `_references/` directory structures:

| Category | Count | Description |
|----------|-------|-------------|
| Skill definitions | 15 | Slash commands (13 user-facing + 2 internal lifecycle hooks): `/plan`, `/implement`, `/advise`, `/check`, `/explain`, `/document`, `/help`, etc. |
| General references | 21 | Reusable standards (review perspectives index, coding standards, report conventions, onboarding index, communication index, skill graph, batch execution patterns, etc.) |
| Per-perspective files | 16 | Individual review perspective files with Essential/Deep-dive tiers, priority-classified P0-P4 (in `general/review-perspectives/`) |
| Per-onboarding files | 8 | Role families (builders, shapers, guardians) and expertise levels (L1-L5) for tailored onboarding plans (in `general/onboarding/`) |
| Per-communication files | 5 | Audience segment profiles (evaluators, clients, end users, academics) and Diataxis mapping (in `general/communication/`) |
| Template references | 51 | Templates for generating project-specific standards, rules, agents, specs, CI, documentation, and smoke-test scaffolding (in `_references/template/`) |
| Agent definitions | 10 | Specialized sub-agents: 7 evaluators (code reviewer, plan reviewer, advisory reviewer, council debate, standards checker, test runner, migration validator) + 3 generators (communication, onboarding, documentation) |
| Rule definitions | 7 | Path-scoped coding rules (backend, frontend, i18n, migrations, tests, e2e, framework-structure) |
| Validation scripts | 39 | Python scripts for quality checks, analysis, smoke testing, and index generation (i18n, auth, migrations, secrets, coverage, briefs, etc.) |
| Framework metadata | 4 | `CLAUDE.md`, `.claude/CHEATSHEET.md`, `.claude/CHANGELOG.md`, and `.claude/skills/VERSION` |

### 0.2 How to Get It

Clone the SEJA repository from GitHub:

```bash
git clone https://github.com/simonedjb/seja.git
```

Or download it as a ZIP from GitHub (Code > Download ZIP).

### 0.3 Next Steps

Now that you know what's in the kit, proceed to **Part 1** to understand how Claude Code works, or jump straight to **Part 3** to set up your project.

If this is your very first AI-assisted project, read **Section 0.4** below first.

### 0.4 If This Is Your First AI-Assisted Project

You do not need to become an engineer before using this toolkit well. The most effective beginner mindset is:

- describe the product problem, user goal, and constraints in plain language
- let Claude propose implementation details, then review them carefully
- prefer `/plan` then `/implement` (two-step) while you are still learning how the framework behaves
- ask Claude to explain unfamiliar code or terminology instead of guessing

If you can clearly say "who is the user, what are they trying to do, what feels wrong now, and what should feel better," you already have enough to start.

**A note for product designers specifically:** your strongest contribution is user goals and communicative intent, not implementation specs. You do not need to know how the code works before adding value. The `/explain` and `/advise` skills are safe to use freely before any code changes happen -- use them to build your understanding of the project and explore options. When you are ready to plan something, `/plan --framing metacomm` is especially suited to designers: it starts from what you want the interface to *say* to users, rather than what you want it to *do* technically.

---

## Key Terms

These terms appear throughout this guide. Definitions are brief here — each is explained in detail in the section indicated.

| Term | Meaning | Details in |
|------|---------|------------|
| **Agent** | An AI assistant that takes actions (reads files, edits code, runs commands), not just answers questions | Part 1 |
| **Skill** | A reusable workflow invoked with `/skill-name` — like a macro or command | Part 2 |
| **Brief** | Your description of what you want done, given to a skill like `/plan` | Part 4 |
| **Reference** | A Markdown file in `_references/` that encodes project standards or templates | Part 2 |
| **Metacommunication** | A message from the designer to the user, expressed through the interface; written as "I (designer) tell you (user)…" | Part 4.4 |
| **Review perspective** | One of 16 engineering and design lenses (e.g., security, performance, accessibility) used to evaluate plans and code | Part 5 |
| **Semiotic engineering** | A theory of human-computer interaction that treats software as designer-to-user communication; SEJA applies it to agentic development | README |
| **Design intent** | The target-state description of what the product should be, captured in `design-intent-to-be.md` | Part 3, Step 5 |
| **Workspace** | A standalone git repo holding framework files and design artifacts, separate from the product codebase | README |

---

## Part 1 -- What Is Claude Code?

### 1.1 The Big Picture

Claude Code is a **command-line AI assistant** that lives in your terminal (or in VS Code). Think of it as a very capable colleague sitting beside you who can:

- Read and understand your entire codebase
- Write, edit, and refactor code
- Run tests, searches, and scripts
- Follow project-specific rules and conventions you define
- Remember patterns across conversations

**Key concept:** Claude Code is not a chatbot. It is an *agent* -- it can take actions (read files, write code, run commands) in addition to answering questions. You guide it with natural language, but it works with real files on your machine.

For product designers, this means you can stay focused on intent, workflow, content, and interaction quality while Claude handles much of the mechanical work of reading files, tracing dependencies, and proposing code changes. You are still the decision-maker; Claude is the hands-on implementation partner.

### 1.2 How It Works

```
You (natural language) --> Claude Code --> Tools (Read, Edit, Bash, etc.)
                                |                      |
                                |                      v
                                |              Your project files
                                |
                                v
                          Response + actions
```

When you type a request, Claude Code:
1. Reads your project context (CLAUDE.md, rules, references)
2. Decides which tools to use
3. Executes actions (reads files, writes code, runs tests)
4. Reports results back to you

### 1.3 What Makes It Different from ChatGPT/Copilot

| Aspect | ChatGPT / Copilot | Claude Code |
|--------|-------------------|-------------|
| Context | Sees only what you paste | Reads your entire codebase |
| Actions | Generates text only | Reads, writes, edits files; runs commands |
| Memory | Forgets between sessions | CLAUDE.md + rules persist across sessions |
| Customization | Generic | Project-specific skills, rules, and references |
| Quality control | None built-in | Review perspectives, validation scripts, agents |

---

## Part 2 -- The Skill System Architecture

The skill system is a **portable framework** that makes Claude Code behave consistently and follow your project's standards. It consists of several layers:

### 2.1 Directory Structure

```
your-project/
├── CLAUDE.md                          <- Project overview (always loaded)
├── .claude/
│   ├── settings.json                  <- Permissions, hooks
│   ├── skills/                        <- Slash commands
│   │   ├── advise/SKILL.md
│   │   ├── check/SKILL.md
│   │   ├── communication/SKILL.md
│   │   ├── design/SKILL.md
│   │   ├── document/SKILL.md
│   │   ├── explain/SKILL.md
│   │   ├── help/SKILL.md
│   │   ├── implement/SKILL.md
│   │   ├── onboarding/SKILL.md
│   │   ├── plan/SKILL.md
│   │   ├── qa-log/SKILL.md
│   │   ├── seed/SKILL.md
│   │   ├── upgrade/SKILL.md
│   │   ├── pre-skill/SKILL.md         <- internal lifecycle hook
│   │   ├── post-skill/SKILL.md        <- internal lifecycle hook
│   │   └── scripts/                   <- Validation scripts
│   ├── rules/                         <- Path-scoped auto-rules
│   └── agents/                        <- Specialized sub-agents
└── _output/                            <- Generated artifacts
    ├── briefs.md                      <- Execution log
    ├── generated-plans/
    ├── generated-roadmaps/
    ├── advisory-logs/
    ├── qa-logs/
    ├── explained-behaviors/
    ├── generated-user-tests/
    └── ...
```

### 2.2 Layer-by-Layer Explanation

#### CLAUDE.md -- The Project's Identity Card

This file is **always loaded** when Claude Code starts. It tells Claude:
- What your project is (stack, architecture)
- How to build and run it
- Key conventions to follow
- Where to find more detailed references

**Analogy:** If Claude Code is a new team member, CLAUDE.md is the one-page project brief you'd hand them on day one.

#### Skills -- Your Slash Commands

Skills are predefined workflows you invoke with `/skill-name`. Each skill is a `SKILL.md` file that instructs Claude how to perform a specific task. The framework includes 13 user-facing skills (listed below) plus 2 internal lifecycle hooks (`/pre-skill`, `/post-skill`) that are called automatically by other skills.

| Skill | What It Does | When to Use |
|-------|-------------|-------------|
| `/advise` | Expert Q&A with multi-perspective analysis; `--inventory` mode catalogs codebase elements | "What's the best approach for X?", "List all API endpoints" |
| `/check` | Unified quality gate with 9 modes: `validate`, `review`, `smoke`, `preflight`, `health`, `test-plan`, `docs`, `telemetry`, `semiotic-inspection` | Before committing, before merging, after changes |
| `/communication` | Generates audience-tailored stakeholder material (evaluators, clients, end users, academics) | Communicating about the project to external audiences |
| `/design` | Configures project-specific files via questionnaire or spec file; `--generate-spec` for a blank spec skeleton | Customizing framework for your project after `/seed` |
| `/document` | Generates or updates project documentation based on plan Docs: fields or auto-detected changes | After implementation to generate user/developer docs |
| `/explain` | Explains behavior, code, data model, architecture, or spec drift with diagrams | "How does authentication work?", "Have my specs diverged?" |
| `/help` | Contextual help for any skill; `--browse` for interactive selection | "What does /check do?", overview of all skills |
| `/implement` | Executes a previously created plan | After reviewing a plan from `/plan` |
| `/onboarding` | Generates tailored onboarding plan for a new team member | New hire joining the project |
| `/plan` | Creates a detailed plan without executing; `--framing metacomm` for design intent; `--roadmap` for product roadmaps | When you want to review before acting, design-driven planning, multi-feature roadmaps |
| `/qa-log` | Logs the current Q&A session to a file | Capturing advisory or design discussions |
| `/seed` | Copies the SEJA framework into a new or existing project; `--workspace` to create a project workspace; `--demo` for a guided hello-world experience | Starting a brand-new project, creating a workspace |
| `/upgrade` | Upgrades framework files in an existing project without touching project-specific files | Pulling latest framework updates |

#### References -- The Knowledge Base

References are Markdown files that encode your project's standards. They split into three categories:

All reference files live in `_references/`:

| Subdirectory | Purpose | Portable? |
| ------------ | ------- | --------- |
| `general/*` | Universal conventions (review perspectives, report format, coding standards) | Yes -- reuse in any project |
| `template/*` | Templates to generate `project/*` files for new projects | Yes -- used by `/design` |
| `project/*` | Project-specific standards (your backend rules, frontend rules, conceptual design) | No -- generated per-project |

**Key general references (21 top-level files + 3 subdirectories):**

- `general/review-perspectives.md` -- Index for 16 engineering and design perspectives, with conflict resolution rules and plan prefix shortcuts. Each perspective lives in its own file under `general/review-perspectives/` (e.g., `sec.md`, `perf.md`) with **Essential** questions (always evaluated) and **Deep-dive** questions (for thorough reviews).
- `general/constraints.md` -- Universal rules (no invented data, no ANSI codes, etc.)
- `general/permissions.md` -- What Claude can do without asking
- `general/coding-standards.md` -- Code style and quality rules
- `general/report-conventions.md` -- How generated reports are formatted
- `general/review-log-template.md` -- Template for structured review logs
- `general/shared-definitions.md` -- Shared definitions used across skills.
- `general/onboarding.md` -- Index for onboarding profiles, with role families (BLD/SHP/GRD) and expertise levels (L1-L5). Each profile lives in its own file under `general/onboarding/` (e.g., `builders.md`, `l3-expert.md`).
- `general/communication.md` -- Index for audience-tailored communication, with segment profiles (EVL/CLT/USR/ACD) and Diataxis mapping. Each segment lives in its own file under `general/communication/` (e.g., `evaluators.md`, `clients.md`).
- `general/skill-graph.md` -- Skill dependency graph and invocation relationships.

**Key template references (51 files):**

- `template/conventions.md` -- Project conventions template
- `template/design-intent-to-be.md`, `template/design-intent-established.md`, `template/ux-research-new.md`, `template/journey-maps-as-is.md`, `template/backend-standards.md`, `template/frontend-standards.md`, `template/testing-standards.md`, `template/i18n-standards.md`, `template/security-checklists.md` -- Project-specific standard templates
- `template/claude-md.md` -- CLAUDE.md template
- `template/rules-backend.md`, `template/rules-frontend.md`, `template/rules-i18n.md`, `template/rules-e2e.md`, `template/rules-tests.md`, `template/rules-migrations.md` -- Path-scoped rule templates
- `template/agents-*.md` -- Agent definition templates (code-reviewer, plan-reviewer, test-runner, standards-checker, migration-validator)
- `template/questionnaire.md` -- Interactive questionnaire for `/design`
- `template/project-spec.md` -- Spec file template for non-interactive `/design`
- `template/roadmap-spec.md` -- Spec file template for `/plan --roadmap`
- `template/communication-style.md` -- Communication style template for `/communication`
- `template/settings.json` -- `.claude/settings.json` template
- `template/smoke-test-registry.json` -- Smoke test endpoint registry template

#### Rules -- Contextual Auto-Rules

Rules in `.claude/rules/` are scoped by file path. When Claude edits a file matching a rule's path pattern, that rule is automatically loaded.

Example: `rules/frontend.md` applies to `frontend/src/**` and enforces TypeScript, BEM CSS, TanStack Query patterns, etc.

**Why this matters:** Rules ensure Claude follows your conventions *automatically*, without you needing to remind it every time.

#### Agents -- Specialized Sub-Processes

Agents are specialized workers that Claude can delegate tasks to. There are 10 agents organized by role:

**Evaluator agents** (7) -- review artifacts against quality perspectives:

| Agent | Purpose |
|-------|---------|
| `advisory-reviewer` | Reviews design decisions against engineering perspectives |
| `code-reviewer` | Reviews code against all 16 perspectives |
| `council-debate` | Runs structured expert council debates for high-stakes decisions |
| `migration-validator` | Validates database migration chain integrity |
| `plan-reviewer` | Reviews plans with complexity-gated two-phase process |
| `standards-checker` | Runs all validation scripts and aggregates results |
| `test-runner` | Runs tests and reports failures with context |

**Generator agents** (3) -- produce self-contained artifacts from well-defined inputs:

| Agent | Purpose |
|-------|---------|
| `communication-generator` | Produces audience-tailored stakeholder material |
| `document-generator` | Generates project documentation from templates |
| `onboarding-generator` | Produces tailored onboarding plans |

Agents run in parallel when possible and return structured reports.

#### Settings -- Permissions and Safety

`.claude/settings.json` controls:
- **Permissions:** What commands Claude can run without asking (git, tests, etc.)
- **Hooks:** Safety checks that run before/after tool calls (e.g., block destructive commands)

---

## Part 3 -- Bootstrapping Your New Project

### Step-by-Step: From Zero to a Configured Project

#### Step 1: Install Claude Code

1. Install Node.js (v18+) if not already installed
2. Install Claude Code:

   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

3. Authenticate with your Anthropic API key or organization credentials
4. Open your terminal in your project directory and type `claude` to start

#### Step 2: Set Up Your Project with the Starter Kit

1. Create your project folder and initialize git:

   ```bash
   mkdir my-new-project
   cd my-new-project
   git init
   ```

2. Copy the framework files from the SEJA repository (see Part 0) into the project root. This creates the `.claude/` directory with all skills, references, templates, agents, and scripts already in place.

#### Step 3: Run `/seed` and `/design`

Start a Claude Code session in your project folder and run `/seed` to copy the framework files:

```text
/seed <target>
```

This copies the `.claude/` and `_references/` directories into your project. If the `.claude/` directory already exists (from the zip), Claude will detect it and ask whether to merge or overwrite. Choose **merge** -- this preserves the files from the zip and layers the seed on top.

If this is your first time, try the guided hello-world experience with `/seed <target> --demo` to see the framework in action before configuring your real project.

Next, run `/design` to configure project-specific files:

```text
/design
```

The design skill supports two modes:

- **Interactive mode** (default): walks you through a questionnaire to customize your project.
- **Spec file mode**: you provide a pre-filled spec file (`/design my-spec.yaml`) that answers all questionnaire questions upfront -- useful for repeatable, non-interactive bootstrapping. Generate a blank spec skeleton with `/design --generate-spec`.

If this is your first time using the toolkit, start with **Interactive mode**. It is the easiest way to learn what the framework needs from you. Use the spec-file flow later when you want repeatable setup across multiple projects.

The `/design` skill will:

1. **Detect the existing `.claude/` structure** from the seed step
2. **Collect your project configuration** (via questionnaire or spec file)
3. **Generate project-specific files** (`project/*.md`, `CLAUDE.md`, rules, settings) based on your answers

#### Step 4: Answer the Questionnaire

The questionnaire has 12 sections (0-11), organized into three tiers. **Section 0 (metacomm-message)** is an optional first section where you write a metacommunication message (a message from you as designer to your future users -- see Key Terms above) -- an agent will extract defaults from it for subsequent questions. **Section 1 (basic-definitions)** has 10 questions and is enough for a working skeleton:

| # | Question | Example Answer |
|---|----------|---------------|
| 1.1 | Project display name? | "PortfolioManager" |
| 1.2 | What does the app do? | "Investment portfolio tracking for retail investors" |
| 1.3 | Greenfield or brownfield? | "Greenfield" |
| 1.4 | Backend framework? | "FastAPI" |
| 1.5 | Frontend framework? | "React" |
| 1.6 | Database? | "PostgreSQL" |
| 1.7 | Primary/secondary languages? | "en-US, pt-BR" |
| 1.8 | Output folder name? | "_output" |
| 1.9 | Source directories? | "backend, frontend" |
| 1.10 | Team composition? | "just me" |

**Best practice (multi-perspective):**

- **DX perspective:** Answer Section 1 (basic-definitions) first -- you get a working setup immediately. Come back to the remaining sections (see slug table in questionnaire) later as you refine.
- **DESIGN perspective:** If you are a product designer, focus on Sections 1, 2 (domain model and metacomm), 3 (UX patterns), and 4 (visual design) -- the T1 tier. For technical questions in Sections 6, 7, 8, type `?` to trigger a guided discussion or accept the **Recommended** defaults. Sections 9-11 will be auto-generated from your stack choices.
- **SEC perspective:** When choosing authentication (Section 8), prefer JWT with HttpOnly cookies over localStorage. The questionnaire explains why.
- **ARCH perspective:** The questionnaire presents pros/cons for each technology choice. Read them carefully -- the framework recommendations account for ecosystem maturity, team size, and future maintainability.
- **I18N perspective:** Even if you only support one language now, set up i18n from the start. Retrofitting is painful.

You can answer these questions in product language. If you are unsure about a technical choice, it is fine to ask Claude for a recommendation and the trade-offs before you commit to an answer.

**Pitfall to avoid:** Don't skip the conceptual-design section (Section 2). Your conceptual design drives all future planning and code review. A vague conceptual design leads to vague plans.

#### Step 5: Review the Generated Files

After `/design` completes, it will present you with three options:

1. **Review specs now** -- walk through each generated file so you can verify and adjust. This is the recommended path, especially for first-time users. Changes are easiest to make now, before any code is generated.
2. **Generate roadmap** -- auto-generate a development roadmap from your specs and optionally turn it into executable plans via `/plan --roadmap`.
3. **Done for now** -- review the files at your own pace and generate a roadmap later.

If you choose to review, here's what to check in each file:

| Generated File | What to Review |
|----------------|---------------|
| `CLAUDE.md` | Does the project summary accurately describe your app? |
| `project/conventions.md` | Are the directory paths correct? |
| `project/design-intent-to-be.md` | Part I: does it capture your target entities, permissions, and planned changes? Part II: does it reflect your intended metacommunication vision (what the product should communicate to users, in your words)? |
| `project/design-intent-established.md` | Is it correctly seeded as an empty archive of processed design decisions? |
| `project/ux-research-new.md` | Does it capture the user research context for this product? |
| `project/journey-maps-as-is.md` | Do the user journeys reflect the key flows you want to support? |
| `project/backend-standards.md` | Do the architecture rules match your team's practices? |
| `project/frontend-standards.md` | Are the component patterns what you want? |
| `project/ux-design-standards.md` | Are the UX patterns and accessibility level correct? |
| `project/graphic-ui-design-standards.md` | Are the brand colors, typography, and visual style right? |
| `project/testing-standards.md` | Are the test frameworks correct? |
| `project/i18n-standards.md` | Are the locales right? |
| `project/security-checklists.md` | Are the validation constants correct? |

**About `design-intent-to-be.md`:** This is your project's design brief. Part I describes the domain (entities, permissions, relationships — the "what exists" layer). Part II captures the metacommunication intent: what the product should communicate to users, written in your words, not implementation terms. This file replaces two older files (`conceptual-design-to-be.md` and `metacomm-to-be.md`). Design intent and communicative intent are treated as two parts of the same artifact because they are inseparable in practice — what the product does and what it says to users need to be designed together.

**For product designers:** You do not need to fill in the technical layer (Part I) perfectly on day one. Start with Part II — write what you want the product to tell users at each key moment. Claude will use that as a planning anchor, and the domain model can be refined as you build.

**Pitfall to avoid:** Don't treat these as "set and forget." They are living documents. Update them as your project evolves.

#### Step 6: Customize Settings

Review `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Read(your-project/**)",
      "Bash(git commit:*)",
      "Bash(git add:*)",
      "Bash(python -m pytest:*)",
      "Bash(npx vitest:*)"
      // Add commands your workflow needs
    ]
  }
}
```

**Best practice (SEC perspective):** Only allow commands you actually use. Don't add blanket `Bash(*)` permission. The hook for destructive operations is a safety net -- keep it.

---

## Part 4 -- Day-to-Day Workflows

### 4.0 Good Starter Prompts for Designers

If you are new to AI-assisted development, these prompt shapes work well:

```
/plan Add a first-run onboarding flow that helps a new user create their
first project without reading documentation.

/plan --framing metacomm When you open the dashboard, I want you to feel
oriented and in control, with the most important next step visually obvious.

/explain behavior Walk me through what happens from sign-up to first successful
checkout.

/check test-plan Test the new onboarding flow for first-time users on mobile.
```

Notice that none of these prompts require low-level implementation detail. Clear intent, user context, and constraints are usually enough to begin.

### 4.1 The "I Need to Build Something" Workflow

**Scenario:** You need to add a user profile page.

**Option A: Plan first, execute later** (recommended for beginners)

```
You: /plan Add a user profile page with avatar upload
```

Claude will:
1. Research your codebase to understand existing patterns
2. Create a detailed plan in `_output/generated-plans/plan-XXXX-user-profile-page.md`
3. Ask if you want to execute it

You review the plan, then:
```
You: /implement XXXX
```

**Best practices:**
- **DX:** Use `/plan` for complex features; for small fixes you can go straight to `/plan` then `/implement`
- **TEST:** After execution, Claude will ask about tests. Always say yes.
- **SEC:** Review generated code for security -- Claude is good but not infallible
- **A11Y:** Check that generated UI components have ARIA labels, keyboard navigation, and sufficient contrast

**Pitfall to avoid:** Don't execute large, ambiguous features in one shot. Break them into smaller, well-defined pieces. "Add user management" is too big. "Add user registration form" is right-sized.

### 4.2 The "I Need Advice" Workflow

```
You: /advise What's the best way to implement real-time notifications?
```

Claude will:
1. Research your codebase and architecture
2. Evaluate the question against all applicable engineering perspectives
3. Provide recommendations with pros and cons
4. Ask follow-up questions
5. Save the Q&A log for future reference

**Deep-dive mode for high-stakes decisions:**

For decisions that are hard to reverse -- choosing a database, deciding on an auth strategy, restructuring the data model -- use the `--deep` flag:

```
You: /advise --deep Should we switch from REST to GraphQL for the mobile API?
```

This activates a structured **council debate**: five expert archetypes (plus topic-specific experts) each present a position, cross-examine each other, and surface trade-offs you might miss in a standard analysis. The result is a comprehensive decision brief rather than a single recommendation.

**When to use `/advise` vs. `/plan`:** Use `/advise` when you are exploring options and need to decide *what* to do. Use `/plan` when you have already decided and need to figure out *how* to do it.

**Preserving decisions:** Follow up with `/qa-log` to save the advisory session as a permanent record of the decision rationale.

### 4.3 The "I Need to Understand Code" Workflow

```
You: /explain behavior How does the authentication flow work?
You: /explain code How does the import system work?
You: /explain data-model Describe the permissions model
You: /explain architecture Why is the backend layered this way?
```

Each type produces different output:
- **architecture** -- System structure, design decisions, trade-offs, and cross-cutting concerns
- **behavior** -- User-perspective walkthrough with analogies and diagrams
- **code** -- Developer-focused explanation for onboarding
- **data-model** -- Entity diagrams, SQL, and gotchas

### 4.4 The "I Need to Design with Metacommunication" Workflow

This is particularly relevant for designers. The `/plan --framing metacomm` command translates a **metacommunication message** (what the designer wants to tell the user through the interface) into a technical plan. Your message is recorded **verbatim** -- the framework preserves your exact wording because precise phrasing carries design intent that paraphrasing would distort.

```
You: /plan --framing metacomm When you open a project, I want you to see
what's new first -- recent activity, unread notifications -- so you can jump
right into ongoing work rather than navigating through menus.
```

Claude translates this designer intent into concrete UI/code changes that make the interface communicate that message.

### 4.5 The "Check Quality Before Committing" Workflow

```
You: /check validate
```

This runs all validation scripts:
- i18n key parity (are all strings translated?)
- Auth decorator coverage (are all endpoints protected?)
- Migration chain integrity (are database migrations consistent?)
- Constant sync (do backend and frontend constants match?)
- PO catalog parity (are .po files in sync?)
- Test coverage analysis

```
You: /check review staged
```

This reviews your staged git changes against all 16 engineering and design perspectives.

**How `/check validate` and `/check smoke` differ:** `/check validate` checks that your code follows *standards* (translations complete, auth decorators in place, constants in sync). `/check smoke` checks that the app actually *works* (every feature responds, no crashes). Use both -- they catch different kinds of problems.

**Best practice:** Run `/check validate` before every commit. Run `/check review staged` before every merge.

### 4.6 The "I Don't Know What to Do Next" Workflow

```
You: /help --browse
```

This shows a categorized menu:
1. **Code quality** -- security audits, refactoring opportunities, i18n fixes
2. **Testing** -- coverage improvements, bug fixes
3. **Documentation** -- code docs, READMEs, user docs
4. **Config and cleanup** -- unused files, config updates, error messages

Pick a category, then a specific task. Claude executes it.

### 4.7 The "I Need a Product Roadmap" Workflow

```
You: /plan --roadmap
```

Claude will:
1. Read your project's conceptual design and standards
2. Decompose features into independent work items (technical and design)
3. Group them into dependency-aware execution waves
4. Generate plans for each item via `/plan` or `/plan --framing metacomm`

You can also provide a pre-filled spec file for repeatable roadmap generation:

```
You: /plan --roadmap --from-spec roadmap-spec.yaml
```

Or generate a blank spec skeleton to fill in manually:

```
You: /plan --roadmap --generate-spec
```

### 4.8 The "I Want to Save This Discussion" Workflow

```
You: /qa-log Authentication design decisions
```

Claude captures the entire current Q&A session -- all user prompts and agent responses -- into a timestamped file in `_output/qa-logs/`. Useful for preserving advisory sessions, design discussions, or decision rationale for future reference.

### 4.9 The "Did Anything Break?" Workflow

```
You: /check smoke
```

Think of this as turning the key to see if the car still starts. After Claude makes changes, `/check smoke` automatically visits every feature and page in your app and checks that nothing crashes. You get a simple report: each feature says PASS or FAIL.

If something fails, Claude will ask whether you want it to investigate and fix the problem, create a plan for later, or move on.

**When to use it:** After any round of changes -- especially after `/implement`. It's fast (a few seconds) and catches problems before they reach real users.

**Best practice:** Make `/check smoke` part of your routine: change something -> `/check smoke` -> commit if green.

### 4.10 The "I Just Deployed, What Should Users Test?" Workflow

```
You: /check test-plan Test the new profile feature
```

Claude reads recent plans and generates a step-by-step test plan phrased as user commands:
> "Navigate to /profile. Click the avatar. Upload a PNG image. The expected outcome is: the avatar updates immediately without a page refresh."

### 4.11 The "My Design Specs Have Diverged" Workflow

**Spec drift** is when the design brief and the actual implementation diverge over time -- features added without updating the brief, or brief changes not yet reflected in code.

```
You: /explain spec-drift
```

Claude will:
1. Read `project/design-intent-to-be.md` (both parts) alongside your standards and recent plans
2. Identify gaps and conflicts between what the design brief specifies and what the codebase reflects
3. Report on the drift with clear explanations of what has diverged and why it matters

**When to use it:** After updating `design-intent-to-be.md`, or when you suspect the implementation has drifted from the original design intent. Run it periodically to keep design intent and code reality aligned.

### 4.12 The "I Need to Generate Documentation" Workflow

```
You: /document
```

After implementing a feature, `/document` generates or updates project documentation. It works in three ways:

- **From a plan:** If you just ran `/implement`, `/document` reads the plan's `Docs:` field and generates the specified documentation types (README, API reference, contextual help, changelog, ADR, help center).
- **Auto-detect:** If there is no recent plan, `/document` scans recent changes and proposes which documentation needs updating.
- **Explicit type:** `/document --type readme` generates a specific documentation type directly.

**When to use it:** After `/implement` completes, especially for user-facing features. The post-skill lifecycle hook will suggest running `/document` when a plan includes documentation tasks.

---

## Part 5 -- The 16 Review Perspectives

Every plan, review, and advisory evaluates your work against these perspectives. Understanding them helps you write better briefs and review Claude's output.

Each perspective lives in its own file under `general/review-perspectives/` with two tiers:

- **Essential** -- 3-7 P0 (critical/blocking) questions always evaluated (loaded for standard reviews)
- **Deep-dive** -- 8-12 P1-P4 questions (loaded for thorough reviews or when the perspective is the primary focus)

All questions are **priority-classified** (P0 critical through P4 informational) and **sorted by priority** within each tier. Essential = P0 only, Deep-dive = P1-P4. Total: 82 Essential + 174 Deep-dive = 256 review questions across all 16 perspectives.

### Engineering Perspectives

| Tag | Name | What It Checks |
|-----|------|---------------|
| SEC | Security | Injection, XSS, CSRF, auth bypass, secret handling |
| PERF | Performance | N+1 queries, missing indexes, caching, bundle size |
| DB | Database | Schema changes, migrations, FK constraints, soft delete |
| API | API Design | RESTful design, error responses, validation schemas |
| ARCH | Architecture | Layer boundaries, separation of concerns, simplicity |
| DX | Developer Experience | Readability, error messages, onboarding friendliness |
| I18N | Internationalization | i18n keys, locale sync, date/number formatting |
| TEST | Testability | Test coverage, edge cases, isolation |
| OPS | Operations | Docker, env vars, health checks, logging |
| COMPAT | Compatibility | API contracts, browser support, backward compatibility |
| DATA | Data Integrity | Validation rules, PII/GDPR, cascade deletes |

### Design Perspectives

| Tag | Name | What It Checks |
|-----|------|---------------|
| UX | User Experience | Flow intuitiveness, feedback, loading/empty/error states |
| A11Y | Accessibility | WCAG compliance, keyboard nav, screen readers, focus management |
| VIS | Visual Design | Design system consistency, spacing, typography, color |
| RESP | Responsive Design | Mobile/tablet/desktop breakpoints, touch targets |
| MICRO | Microinteractions | Animations, hover/focus states, reduced-motion support |

**Priority rules when perspectives conflict:**
1. **SEC always wins** -- security overrides performance or convenience
2. **A11Y is non-negotiable** -- accessibility requirements are never traded off
3. **Document the trade-off** -- when deferring one perspective, explain why

---

## Part 6 -- Best Practices for Working with Claude Code

### 6.1 Writing Good Briefs

A strong brief does not need to sound like an engineering ticket. For designers, the most useful inputs are:

- who the user is
- what they are trying to do
- what feels broken, confusing, or incomplete
- what success should feel like
- any constraints such as accessibility, localization, or reuse of existing UI patterns

**Bad brief:** "Fix the login"
**Good brief:** "Fix the login form -- submitting with an empty password field returns a 500 error instead of showing a validation message"

**Bad brief:** "Add notifications"
**Good brief:** "Add email notifications when a user receives a reply to their post. Use the existing email template system. Support pt-BR and en-US."

**Why it matters:** Claude plans based on your brief. A vague brief produces a plan that might miss your intent. A precise brief produces a plan that matches exactly what you need.

### 6.2 Reviewing Claude's Output

Always review:
- **Plans** -- before executing, read the plan. Does it match your intent? Are there steps that seem wrong or missing?
- **Code** -- Claude writes good code, but check security-sensitive areas (auth, input handling, file operations)
- **Tests** -- ensure tests cover the actual behavior, not just the happy path
- **Migrations** -- database changes are hard to reverse. Check idempotency guards.

### 6.3 The Briefs Log

Every skill invocation is logged in `_output/briefs.md` (not to be confused with the "brief" you write when invoking a skill — this is the execution log, not your input):

```
2026-03-15 14:30:00 UTC | plan | Add user profile page with avatar upload
DONE | 2026-03-15 15:00:00 UTC | 2026-03-15 14:30:00 UTC | plan | Add user profile page | PLAN | 0042
```

This gives you a timeline of all work done by Claude. Useful for:
- Tracking what was done and when
- Finding related plans after the fact
- Auditing if something went wrong

### 6.4 When to Ask Claude vs. When to Do It Yourself

| Use Claude for | Do yourself |
|---------------|-------------|
| Repetitive code changes across many files | Critical business logic decisions |
| Understanding unfamiliar code | Visual design tweaks (colors, spacing) |
| Writing and running tests | Deploying to production |
| Generating boilerplate | Reviewing Claude's security-sensitive output |
| i18n -- translating and syncing strings | Final user acceptance testing |
| Code reviews and quality checks | Architecture decisions (use `/advise` first) |

### 6.5 Safety Practices

1. **Always work in a git branch** -- never let Claude modify `main` directly
2. **Review diffs before committing** -- `git diff` is your friend
3. **Don't skip validation** -- run `/check validate` before committing
4. **Keep secrets out** -- never commit `.env`, credentials, or API keys
5. **Don't blindly execute** -- if a plan looks wrong, say so. Claude adjusts.
6. **Destructive operations require your approval** -- Claude won't `rm -rf` or `DROP TABLE` without asking (the hook in settings.json enforces this)

---

## Part 7 -- Common Pitfalls and How to Avoid Them

### Pitfall 1: "Let Claude do everything"

**Problem:** Delegating all decisions to Claude without reviewing output.
**Solution:** Claude is a tool, not a decision-maker. Review plans before executing. Review code before committing. You are the designer -- Claude implements your vision.

### Pitfall 2: "Vague briefs"

**Problem:** Saying "improve the frontend" and expecting Claude to read your mind.
**Solution:** Be specific. What should improve? Which page? What's the current behavior? What should the new behavior be? Include error messages if it's a bug fix.

### Pitfall 3: "Skipping the questionnaire"

**Problem:** Running `/design` and accepting all defaults without reading the options.
**Solution:** The questionnaire presents trade-offs for each technology choice. Reading the pros/cons takes 15 minutes but saves hours of rework. Pay special attention to Section conceptual-design (Section 2) -- it shapes all future plans.

### Pitfall 4: "Not updating reference files"

**Problem:** Your project evolves but `project/conceptual-design-as-is.md` still describes the initial version.
**Solution:** When you add new entities, permissions, or conventions, update the relevant `project/*.md` file. Claude reads these for context.

### Pitfall 5: "Ignoring the design perspectives"

**Problem:** Deferring A11Y and SEC perspectives because "we'll fix it later."
**Solution:** Security and accessibility debt compounds. Address SEC and A11Y findings immediately. Other perspectives can be deferred with documented rationale.

### Pitfall 6: "Giant feature in one command"

**Problem:** "Build the entire admin dashboard" as a single `/plan` command.
**Solution:** Break large features into small, testable increments. Each `/plan` should produce a change you can review, test, and commit independently.

### Pitfall 7: "Not reading the plan before /implement"

**Problem:** Executing a plan without reviewing it, then finding it modified files you didn't expect.
**Solution:** Plans are saved as Markdown files. Open them. Read the "actions" and "to do" sections. Check the "files" list. If something looks off, tell Claude to revise before executing.

### Pitfall 8: "Forgetting about i18n"

**Problem:** Adding user-facing strings in English only, leaving translation gaps.
**Solution:** Always mention the supported locales in your brief. Claude will add strings to all locale files. Run `/check validate` with an i18n focus to catch any misses.

---

## Part 8 -- Quick Reference Card

### Essential Commands

| Command | What It Does |
|---------|-------------|
| `/plan <brief>` then `/implement <id>` | Plan + execute a change |
| `/plan <brief>` | Plan without executing |
| `/plan --framing metacomm <message>` | Design from metacommunication intent |
| `/plan --roadmap` | Generate a product roadmap with execution waves |
| `/plan --roadmap --from-spec <file>` | Generate roadmap from a spec file |
| `/implement <id>` | Execute a saved plan |
| `/advise <question>` | Get expert advice |
| `/advise --deep <question>` | Expert council debate for high-stakes decisions |
| `/advise --inventory <pattern>` | Catalog codebase elements matching a pattern |
| `/explain architecture <scope>` | Explain system architecture and design decisions |
| `/explain behavior <topic>` | Explain system behavior |
| `/explain code <topic>` | Explain code for developers |
| `/explain data-model <scope>` | Explain database structure |
| `/explain spec-drift` | Show divergence between design and metacomm specs |
| `/check validate` | Run all quality checks |
| `/check review staged` | Review staged changes against 16 perspectives |
| `/check smoke` | Check that nothing is broken after changes |
| `/check preflight` | Validation + code review before commit |
| `/check test-plan <brief>` | Generate manual test plan |
| `/check health` | Framework self-diagnosis and integrity check |
| `/check docs` | Documentation consistency check |
| `/seed <target>` | Copy framework files into a new project |
| `/seed <target> --workspace` | Create a project workspace alongside an existing codebase |
| `/seed <target> --demo` | Guided hello-world experience |
| `/design` | Configure project-specific files (interactive questionnaire) |
| `/design --generate-spec` | Generate a blank spec skeleton |
| `/design <spec-file>` | Configure from a pre-filled spec file |
| `/upgrade` | Upgrade framework files in an existing project |
| `/document` | Generate or update project documentation |
| `/qa-log <topic>` | Save current Q&A session to a file |
| `/help` | Show skill help (overview or specific skill) |
| `/help --browse` | Browse available tasks interactively |

### Project Structure Checklist

After `/seed` + `/design`, verify you have:

- [ ] `CLAUDE.md` at project root
- [ ] `.claude/settings.json` with appropriate permissions
- [ ] `.claude/skills/` with all SKILL.md files
- [ ] `_references/general/*.md` (20 reusable standards)
- [ ] `_references/general/review-perspectives/` (16 per-perspective files)
- [ ] `_references/general/onboarding/` (8 role/level profiles)
- [ ] `_references/general/communication/` (5 audience segment profiles)
- [ ] `_references/template/` (51 templates including agent/, ci/, demo/, docs/)
- [ ] `_references/project/*.md` (customized)
- [ ] `.claude/rules/` with path-scoped rules
- [ ] `.claude/agents/` with specialized agents
- [ ] `.claude/skills/VERSION` with framework version
- [ ] `.claude/CHEATSHEET.md` (auto-generated skill reference)
- [ ] `_output/briefs.md` (or your chosen output dir)

### Workflow Cheat Sheet

```
Starting a new feature:
  /plan <brief>  ->  review plan  ->  /implement <id>  ->  commit

Quick fix:
  /plan <brief>  ->  /implement <id>  ->  commit

Before merging:
  /check review staged  ->  address findings  ->  /check validate  ->  /check smoke  ->  merge

Understanding code:
  /explain code <topic>  ->  read the generated explanation

Planning multi-feature work:
  /plan --roadmap  ->  review waves  ->  execute plans per wave  ->  /check validate  ->  commit

Capturing a design discussion:
  /qa-log <topic>  ->  file saved to qa-logs/

Checking design spec alignment:
  /explain spec-drift  ->  review the drift report  ->  update specs if needed  ->  commit

Browsing available tasks:
  /help --browse  ->  choose category  ->  choose task  ->  execute
```

---

## Recommendations Summary

1. **Install Claude Code and run `/seed` then `/design`** on your new project as the first step -- this establishes the entire skill system
2. **Invest 15 minutes in the questionnaire** -- especially Section 1 (basic-definitions) and Section 2 (conceptual-design); these drive everything else
3. **Always review the plan before `/implement`** -- reviewing plans teaches you how Claude thinks and builds your intuition for writing better briefs
4. **Run `/check validate` and `/check smoke` before every commit** -- `/check validate` checks standards, `/check smoke` checks that nothing is broken
5. **Keep reference files updated** as your project evolves -- stale references produce stale plans
6. **Break large features into small plans** -- each should be independently testable and committable
7. **Never defer SEC or A11Y findings** -- these perspectives have priority by design
8. **Use `/plan --framing metacomm` for design-driven development** -- translate designer intent into technical plans, keeping the metacommunication message at the center of design decisions. Your metacommunication messages are always recorded verbatim.
9. **Review every plan and every diff** before committing -- Claude is a powerful assistant, but you are the responsible designer
10. **Use `/help --browse` when unsure** -- it surfaces routine maintenance tasks you might otherwise forget
