# CI/CD integration how-to

This how-to is for you when you want to wire SEJA quality checks into your CI/CD pipeline so that the same gates you run locally also run on every push and pull request. By the end of it you will have a three-layer enforcement model -- git hooks, post-skill gate, and CI pipeline -- sharing a single entry point.

## Before you start

- Your project has been seeded and configured via `/seed` + `/design`.
- You have Python 3.9+ available in your CI environment.
- The lifecycle definitions in [concepts.md -- Framework lifecycle](../concepts.md#framework-lifecycle) -- every **Framework:** callout below links back there for its definitions.

## The three-layer enforcement model

SEJA validates work at three layers, each with a different speed and blocking behavior:

| Layer | Mechanism | Speed | Blocking? | Install |
|-------|-----------|-------|-----------|---------|
| **Git hooks** | `.githooks/pre-commit` runs `run_preflight_fast.py` | <10s | Hard block (bypass: `--no-verify`) | `bash .githooks/install.sh` |
| **Post-skill gate** | Step 6b in post-skill runs the same fast checks | <10s | Advisory (user can override) | Automatic (built into workflow) |
| **CI pipeline** | `.github/workflows/seja-validate.yml` | <30s fast / full on PR | Hard block on merge | Push workflow file to repo |

All three layers share a single entry point: `run_preflight_fast.py`.

**Framework:** the fast preflight script orchestrates the validator suite (`check_conventions.py`, `check_skill_system.py`, `check_secrets.py`, `check_spec_conformance.py`) and optionally runs `pytest` in CI mode. See also [quality-gates.md](quality-gates.md) for which `/check` mode to reach for at each stage of a local workflow.

## Step 1: Install git hooks (local)

We install pre-commit hooks with one command:

```bash
bash .githooks/install.sh
```

This sets `core.hooksPath` to `.githooks/`, enabling the pre-commit hook that runs `run_preflight_fast.py` before every commit. To uninstall:

```bash
git config --unset core.hooksPath
```

To bypass for a single commit (use sparingly):

```bash
git commit --no-verify -m "message"
```

**Framework:** the git hook is the hard-block layer. If any check fails, the commit is rejected. The hook runs the same checks as post-skill step 6b, so if a skill session already passed, the hook confirms nothing regressed between skill completion and commit time.

## Step 2: Understand the post-skill gate (automatic)

No setup required. Step 6b in `/post-skill` automatically runs `run_preflight_fast.py` before committing skill outputs. This is advisory -- if the checks fail, the user can override and proceed. It catches issues the agent introduced during skill execution.

## Step 3: Add the CI pipeline (remote)

### GitHub Actions

The provided workflow at `.github/workflows/seja-validate.yml` runs two jobs:

1. **Fast gate** (every push): `run_preflight_fast.py --ci`
2. **Full validation** (PRs to main only): `claude -p "/check validate all"` (requires `ANTHROPIC_API_KEY` secret)

To use, ensure the workflow file is committed and add `ANTHROPIC_API_KEY` to your repo's GitHub Actions secrets (only needed for the full validation job).

### GitLab CI

```yaml
seja-fast-gate:
  stage: test
  script:
    - python .claude/skills/scripts/run_preflight_fast.py --ci
  rules:
    - if: $CI_MERGE_REQUEST_ID

seja-full-validation:
  stage: test
  script:
    - claude -p "/check validate all"
  rules:
    - if: $CI_MERGE_REQUEST_ID
  allow_failure: true
```

### Other CI systems

Any CI system that can run Python 3.9+ can use the fast gate:

```bash
python .claude/skills/scripts/run_preflight_fast.py --ci
```

For full validation (requires Claude Code CLI):

```bash
claude -p "/check validate all"
```

## Step 4: Run standalone script checks

These scripts can also be run individually. All produce clear pass/fail exit codes:

| Script | Purpose | Exit code |
|--------|---------|-----------|
| `check_conventions.py` | Validates `${var}` references match definitions | 0 = pass, 1 = errors |
| `check_skill_system.py` | Validates skill system integrity | 0 = pass, 1 = errors |
| `check_secrets.py [--all]` | Scans for committed secrets | 0 = clean, 1 = found |
| `check_spec_conformance.py` | Validates against spec-checks.yaml | 0 = pass, 1 = errors |

All scripts are in `.claude/skills/scripts/` and require no dependencies beyond Python 3.9+ standard library. The `--ci` flag on `run_preflight_fast.py` adds `pytest` to the suite.

## Skills that require interactive input

The following skills cannot run in headless CI mode because they require user decisions:

| Skill | Why interactive |
|-------|----------------|
| `/design` | Questionnaire requires user answers |
| `/advise` | Q&A conversation loop |
| `/plan` | Review and approval step |
| `/implement` | May pause for guidance on failures |
| `/help --browse` | Interactive menu selection |
| `/explain spec-drift` | Spec analysis may require user decisions |
| `/plan --roadmap` | Item review and approval |

Use these skills in local development sessions, not in CI.

## Environment requirements

- **Python 3.9+** for standalone scripts and fast preflight
- **Claude Code CLI** for skill invocations (`npm install -g @anthropic-ai/claude-code`)
- **ANTHROPIC_API_KEY** environment variable for Claude Code invocations
- Scripts assume they run from the repository root directory

## Troubleshooting

- **Scripts fail with "project/conventions.md not found"**: This is a warning, not an error. The scripts fall back to `template/conventions.md`. In project repos (not the framework repo), ensure `/design` has been run to generate `project/conventions.md`.
- **Claude Code invocations timeout**: Set a generous timeout (5-10 minutes) for skill invocations. `/check validate` and `/check preflight` can take several minutes on large codebases.
- **Index regeneration fails**: Ensure the `_output/` directory exists and the scripts have write access.
- **Pre-commit hook not running**: Verify hooks are installed with `git config core.hooksPath`. Should show `.githooks`.

## What to read next

- [quality-gates.md](quality-gates.md) -- which `/check` mode to run at each stage of a local workflow.
- [concepts.md -- Framework lifecycle](../concepts.md#framework-lifecycle) -- the canonical definitions the callouts above link back to.
