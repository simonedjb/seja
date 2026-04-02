# GENERAL - CI/CD INTEGRATION

> Guide for integrating SEJA framework skills and scripts into CI/CD pipelines.
> Last revised: 2026-03-30

---

## Overview

The SEJA framework provides a **three-layer enforcement model** for validation:

| Layer | Mechanism | Speed | Blocking? | Install |
|-------|-----------|-------|-----------|---------|
| **Git hooks** | `.githooks/pre-commit` runs `run_preflight_fast.py` | <10s | Hard block (bypass: `--no-verify`) | `bash .githooks/install.sh` |
| **Post-skill gate** | Step 6b in post-skill runs same fast checks | <10s | Advisory (user can override) | Automatic (built into workflow) |
| **CI pipeline** | `.github/workflows/seja-validate.yml` | <30s fast / full on PR | Hard block on merge | Push workflow file to repo |

All three layers share a single entry point: `run_preflight_fast.py`.

---

## Fast Preflight Entry Point

The `run_preflight_fast.py` script is the single entry point for all fast validation gates:

```bash
# Basic (hooks, post-skill)
python .claude/skills/scripts/run_preflight_fast.py

# Extended (CI -- includes unit tests)
python .claude/skills/scripts/run_preflight_fast.py --ci

# Verbose output
python .claude/skills/scripts/run_preflight_fast.py --verbose
```

**Checks included:**
- `check_conventions.py` -- validates `${var}` references match definitions
- `check_skill_system.py` -- validates skill system integrity (frontmatter, metadata)
- `check_secrets.py` -- scans for accidentally committed secrets
- `check_spec_conformance.py` -- validates against `spec-checks.yaml` (if present)
- `pytest` (with `--ci` flag) -- runs framework unit tests

Exit code: 0 = all pass, 1 = any failure.

---

## Layer 1: Git Hooks (Local)

Install pre-commit hooks with one command:

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

---

## Layer 2: Post-Skill Gate (Workflow)

Step 6b in `/post-skill` automatically runs `run_preflight_fast.py` before committing skill outputs. This is advisory -- the user can override if the checks fail. This catches issues that the agent introduced during skill execution.

No setup required -- built into the skill workflow.

---

## Layer 3: CI Pipeline (Remote)

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

### Other CI Systems

Any CI system that can run Python 3.9+ can use the fast gate:

```bash
python .claude/skills/scripts/run_preflight_fast.py --ci
```

For full validation (requires Claude Code CLI):

```bash
claude -p "/check validate all"
```

---

## Standalone Script Checks

These scripts can also be run individually. All produce clear pass/fail exit codes:

| Script | Purpose | Exit Code |
|--------|---------|-----------|
| `check_conventions.py` | Validates `${var}` references match definitions | 0 = pass, 1 = errors |
| `check_skill_system.py` | Validates skill system integrity | 0 = pass, 1 = errors |
| `check_secrets.py [--all]` | Scans for committed secrets | 0 = clean, 1 = found |
| `check_spec_conformance.py` | Validates against spec-checks.yaml | 0 = pass, 1 = errors |
| `check_conventions.py --verbose` | Verbose output | Same |

All scripts are in `.claude/skills/scripts/` and require no dependencies beyond Python 3.9+ standard library.

---

## Skills That Require Interactive Input

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

---

## Environment Requirements

- **Python 3.9+** for standalone scripts and fast preflight
- **Claude Code CLI** for skill invocations (`npm install -g @anthropic-ai/claude-code`)
- **ANTHROPIC_API_KEY** environment variable for Claude Code invocations
- Scripts assume they run from the repository root directory

---

## Troubleshooting

- **Scripts fail with "project/conventions.md not found"**: This is a warning, not an error. The scripts fall back to `template/conventions.md`. In project repos (not the framework repo), ensure `/design` has been run to generate project/conventions.md.
- **Claude Code invocations timeout**: Set a generous timeout (5-10 minutes) for skill invocations. `/check validate` and `/check preflight` can take several minutes on large codebases.
- **Index regeneration fails**: Ensure the `_output/` directory exists and the scripts have write access.
- **Pre-commit hook not running**: Verify hooks are installed with `git config core.hooksPath`. Should show `.githooks`.
