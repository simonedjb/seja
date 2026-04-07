# Troubleshooting for Developers

Diagnostic reference for common framework issues. Each entry follows: **Symptom**, **Cause**, **Fix**, **Prevention**.

---

## 1. Pre-skill aborts: brief-log failed

**Symptom**: Pre-skill exits with an error referencing `briefs.md` or `briefs-log.md`.

**Cause**: The briefs file is locked by another process or contains malformed YAML frontmatter.

**Fix**: Check file permissions and ensure no other editor holds a lock:

```bash
ls -la .claude/briefs.md
```

If the frontmatter is malformed, fix the YAML manually -- look for unclosed quotes or incorrect indentation.

**Prevention**: Avoid editing briefs files while a skill is running.

---

## 2. Reference file not loaded

**Symptom**: A skill runs but does not have access to expected reference content.

**Cause**: The file is missing from the `references` list in the skill's `SKILL.md` frontmatter, or the file does not exist in `_references/`.

**Fix**: Verify the frontmatter references list in the skill's `SKILL.md`, then confirm the file exists:

```bash
cat .claude/skills/<skill-name>/SKILL.md | head -20
ls _references/<expected-path>
```

**Prevention**: Run `/check validation` after adding or renaming reference files.

---

## 3. Orphaned STARTED entries accumulate

**Symptom**: `briefs-log.md` contains multiple STARTED entries without corresponding COMPLETED entries.

**Cause**: Sessions crashed or were interrupted before post-skill could finalize.

**Fix**: These are safe to ignore. Review and clean up manually if the log becomes cluttered:

```bash
grep "STARTED" .claude/briefs-log.md
```

**Prevention**: Allow skills to complete fully before closing the terminal.

---

## 4. Post-skill crashes mid-commit

**Symptom**: Post-skill fails after the skill body completed, leaving uncommitted changes.

**Cause**: A checkpoint recovery mechanism exists for this scenario.

**Fix**: Check the checkpoint file and resume:

```bash
cat .claude/.post-skill-checkpoint
```

Re-running the skill or invoking post-skill directly resumes from the last checkpoint.

**Prevention**: Ensure sufficient disk space and that git is not in a conflicted state before running skills.

---

## 5. Plan review enters infinite loop

**Symptom**: Plan review keeps iterating without converging on approval.

**Cause**: The iteration cap is 3 rounds. If perspectives provide contradictory recommendations, the review may cycle without resolution.

**Fix**: Identify which perspectives conflict by reading the review output. Resolve contradictions in the plan or temporarily disable one conflicting perspective.

**Prevention**: Ensure perspective definitions do not contain mutually exclusive pass criteria.

---

## 6. Agent returns empty or generic response

**Symptom**: The agent produces a response that lacks project-specific detail or is unusually brief.

**Cause**: The skill's context budget is too low, so critical reference files were not loaded.

**Fix**: Check the skill's `context_budget` tier in its `SKILL.md` frontmatter. Increase the tier if the skill requires more context:

```bash
grep "context_budget" .claude/skills/<skill-name>/SKILL.md
```

**Prevention**: Set context budgets based on the number and size of reference files the skill needs.

---

## 7. Index files are stale

**Symptom**: Skills reference outdated brief summaries or macro definitions.

**Cause**: Index files were not regenerated after content changes.

**Fix**: Regenerate both indexes:

```bash
python .claude/scripts/generate_briefs_index.py
python .claude/scripts/generate_macro_index.py
```

**Prevention**: Run index generation as part of your post-change workflow, or rely on post-skill to handle it automatically.

---

## 8. Skill spec validation fails

**Symptom**: `/check validation` reports errors in a skill's SKILL.md file.

**Cause**: The YAML frontmatter does not conform to the agentskills.io specification.

**Fix**: Run the spec checker for details, then correct the frontmatter:

```bash
python .claude/scripts/check_skill_spec.py .claude/skills/<skill-name>/SKILL.md
```

**Prevention**: Use an existing SKILL.md as a template when creating new skills.

---

## 9. Preflight gate blocks commit

**Symptom**: A commit is rejected by the preflight check with one or more failure messages.

**Cause**: The preflight gate runs validation checks before allowing commits. One or more checks failed.

**Fix**: Read the failure output carefully -- it identifies the specific issue. Fix the reported problem and commit again. If the check is advisory and you understand the risk, proceed with `--force`:

```bash
git commit  # after fixing the issue
```

**Prevention**: Run `/check preflight` before committing to catch issues early.

---

## 10. Telemetry record missing fields

**Symptom**: Telemetry entries in the briefs log have null or missing fields.

**Cause**: Post-skill step 1b could not parse timestamps or other metadata from the session.

**Fix**: Null fields are acceptable and do not indicate data loss. If specific fields are consistently missing, verify that the skill emits the expected output format:

```bash
grep "timestamp" .claude/briefs-log.md | tail -5
```

**Prevention**: Ensure skills follow the standard output format so post-skill can parse all fields.
