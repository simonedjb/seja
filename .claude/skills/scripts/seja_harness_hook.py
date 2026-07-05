#!/usr/bin/env python3
"""UserPromptSubmit hook: inject SEJA harness lifecycle reminder.

Invocation: hook-ci
Lifecycle: active

Bundled into every SEJA project. Runs on every user prompt submission
and outputs a reminder so Claude stays oriented to the harness lifecycle
even in auto mode or plan mode. Install via .claude/settings.json hooks.
"""
import sys

sys.stdin.read()  # consume hook payload

print(
    "[SEJA harness active] You are in a SEJA project. "
    "Follow the lifecycle in CLAUDE.md at all times — auto mode and plan mode do not override harness rules. "
    "Lifecycle: /research or /explain -> /plan -> /implement -> /critique -> /document or /communicate -> /reflect. "
    "Log conversation trace after every non-skill response."
)
