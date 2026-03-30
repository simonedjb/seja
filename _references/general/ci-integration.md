# GENERAL - CI/CD INTEGRATION

> Guide for integrating SEJA framework skills and scripts into CI/CD pipelines.
> Last revised: 2026-03-28

---

## Overview

The SEJA framework includes both interactive skills (requiring Claude Code) and standalone scripts (runnable without Claude Code). This guide covers how to integrate both into automated pipelines.

---

## Standalone Script Checks (No Claude Code Required)

These scripts produce clear pass/fail exit codes and can run directly in any CI environment with Python 3.9+:

| Script | Purpose | Exit Code |
|--------|---------|-----------|
| `python .claude/skills/scripts/check_conventions.py` | Validates that all `${VAR}` references in skills have matching definitions in project/conventions.md | 0 = pass, 1 = missing vars |
| `python .claude/skills/scripts/check_skill_system.py` | Validates skill system integrity (frontmatter, Quick Guides, metadata) | 0 = pass, 1 = errors |
| `python -m pytest .claude/skills/scripts/tests/ -v` | Runs framework script unit tests | 0 = pass, 1 = failures |
| `python .claude/skills/scripts/check_secrets.py <dir>` | Scans for accidentally committed secrets (.env files, API keys) | 0 = clean, 1 = secrets found |

### Recommended CI Stage

Run these as a **pre-merge check** on every PR. They are fast (<10s total) and require no external services.

---

## Claude Code Skill Invocations (Requires Claude Code CLI)

These use `claude -p` (non-interactive/pipe mode) to invoke skills:

### Pre-merge Checks

```yaml
# GitHub Actions example
- name: SEJA Preflight
  run: claude -p "/check preflight staged"
```

### Nightly Validation

```yaml
# GitHub Actions scheduled workflow
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM UTC daily
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: SEJA Health Check
        run: claude -p "/check health"
      - name: SEJA Validation
        run: claude -p "/check validate all"
```

### Post-merge Index Regeneration

```yaml
# After merge to main
- name: Regenerate indexes
  run: |
    python .claude/skills/scripts/generate_briefs_index.py
    python .claude/skills/scripts/generate_macro_index.py
```

---

## GitLab CI Example

```yaml
seja-checks:
  stage: test
  script:
    - python .claude/skills/scripts/check_conventions.py
    - python .claude/skills/scripts/check_skill_system.py
    - python -m pytest .claude/skills/scripts/tests/ -v
  rules:
    - if: $CI_MERGE_REQUEST_ID
```

---

## Skills That Require Interactive Input

The following skills cannot run in headless CI mode because they require user decisions:

| Skill | Why interactive |
|-------|----------------|
| `/quickstart` | Questionnaire requires user answers |
| `/advise` | Q&A conversation loop |
| `/make-plan` | Review and approval step |
| `/execute-plan` | May pause for guidance on failures |
| `/help --browse` | Interactive menu selection |
| `/explain spec-drift` | Spec analysis may require user decisions |
| `/make-plan --roadmap` | Item review and approval |

Use these skills in local development sessions, not in CI.

---

## Environment Requirements

- **Python 3.9+** for standalone scripts
- **Claude Code CLI** for skill invocations (`npm install -g @anthropic-ai/claude-code`)
- **ANTHROPIC_API_KEY** environment variable for Claude Code invocations
- Scripts assume they run from the repository root directory

---

## Troubleshooting

- **Scripts fail with "project/conventions.md not found"**: This is a warning, not an error. The scripts fall back to `template/conventions.md`. In project repos (not the framework repo), ensure `/quickstart` has been run to generate project/conventions.md.
- **Claude Code invocations timeout**: Set a generous timeout (5-10 minutes) for skill invocations. `/check validate` and `/check preflight` can take several minutes on large codebases.
- **Index regeneration fails**: Ensure the `_output/` directory exists and the scripts have write access.
