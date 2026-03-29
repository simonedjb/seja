# Journey: Enterprise -- Regulated System Evolution

## Who this is for

A team working in a regulated domain (healthcare, finance, education) where compliance, security, and audit trails are critical. The system already exists and needs careful evolution.

## What you'll accomplish

A framework setup that provides audit trails for design decisions, enforces security and compliance perspectives on every change, and documents the evolution from as-is to to-be.

## Prerequisites

- Claude Code or Codex CLI installed
- Access to the existing *ProjectName* codebase (git repository)
- The foundational SEJA framework available (quickstart kit or repo)
- The [workspace setup](../recipes/recipe-workspace-setup.md) pattern is strongly recommended for team independence and governance

## Step-by-step walkthrough

### Step 1: Audit the existing system

Use `/explain architecture` / `$explain architecture` and `/explain data-model` / `$explain data-model` to document the current system. Then run `/check review` / `$check review` against the full set of perspectives, paying special attention to SEC (security), DATA (data integrity and privacy), and COMPAT (compatibility). This creates a baseline audit.

Expected output: architecture/data model documentation and review report.

### Step 2: Bootstrap with governance in mind

Set up the workspace pattern: each team member gets a *ProjectName* workspace created from the foundational SEJA framework via `/quickstart --workspace` / `$quickstart --workspace`. The workspace is its own git repo with `_output/` inside, so every plan, advisory, and brief is version-controlled -- providing a compliance-ready audit trail of all design decisions. The *ProjectName* codebase is accessed via `--add-dir` and stays clean. Run `/quickstart .` / `$quickstart .` in the workspace with careful attention to security checklists and compliance-relevant sections. See the [workspace setup recipe](../recipes/recipe-workspace-setup.md) for details.

### Step 3: Document the as-is/to-be gap

Fill in the conceptual design files carefully: `project-conceptual-design-as-is.md` for what exists, `project-conceptual-design-to-be.md` for the target state. Use `/explain spec-drift` / `$explain spec-drift` to systematically compare them.

Expected output: spec drift analysis highlighting compliance-relevant gaps.

### Step 4: Plan with compliance focus

Use `/advise` / `$advise` to evaluate changes from a compliance perspective before planning. Example: `/advise What are the data privacy implications of migrating user records to the new schema?` / `$advise What are the data privacy implications of migrating user records to the new schema?`. Then use `/make-plan` / `$make-plan` for each change -- the review log in each plan documents the SEC/DATA/COMPAT evaluation, creating a decision audit trail.

### Step 5: Execute with quality gates

Run `/execute-plan <id>` / `$execute-plan <id>` for each plan. After execution, run `/check preflight` / `$check preflight` (which includes validation and code review). The advisory reports and plan review logs serve as compliance evidence.

### Step 6: Maintain the audit trail

Use `/advise` / `$advise` for ongoing design decisions (each creates an advisory report). Use `/qa-log` / `$qa-log` to preserve important Q&A sessions. Use `/explain spec-drift` / `$explain spec-drift` periodically to verify ongoing alignment. All artifacts in `_output/` are timestamped and sequentially numbered.

## What to do next

- [Map an existing codebase](../recipes/recipe-map-existing-codebase.md)
- [Set up a project workspace](../recipes/recipe-workspace-setup.md)
- [Onboard a team member](../recipes/recipe-onboard-team-member.md)
- [Run quality gates](../recipes/recipe-quality-gates.md)
- [Plan and execute a feature](../recipes/recipe-plan-and-execute.md)
- For the full framework reference, see the onboarding guide: [Claude](../claude-onboarding-guide.md) | [Codex](../codex-onboarding-guide.md)
