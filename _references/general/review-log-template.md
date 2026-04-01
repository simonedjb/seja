# FRAMEWORK - REVIEW LOG TEMPLATE

> Structured format for logging plan and code review iterations.
> Used by `plan`, `review-code`, and any skill that evaluates against `general/review-perspectives.md`.

---

## Review Log Format

```markdown
## Review Log

**Review depth:** Light | Standard | Deep
**Deep-dive budget:** 0/6 used

### Phase 1 — Perspective Scan (<datetime>)

| Perspective | Status | Concern |
|-------------|--------|---------|
| SEC | Adopted | Input validation covered in Step 3 |
| PERF | Deferred | Potential N+1 in bulk query — triggers Phase 2 |
| DB | Adopted | Migration is idempotent |
| ... | N/A | |

### Phase 2 — Deep-dive: PERF (iteration 1, deep-dive 1/6)

**Concern:** Bulk export may trigger N+1 queries for large datasets.
**Step ref:** Step 5 (bulk export query)
**Files read:** `backend/app/services/export_service.py`, `project/backend-standards.md`
**Finding:** [analysis of the referenced source files]
**Recommendation:** [specific change or confirmation that no change is needed]
**Resolution:** [Plan amended — see Plan Amendment (iteration 1) / No change needed — status changed to Adopted]

### Conflict Check (iteration 1)

[If Phase 2 recommendations conflict across perspectives, document the conflict and resolution per the conflict resolution rules in `general/review-perspectives.md`. If no conflicts, write "No inter-perspective conflicts detected."]

### Execution Metrics

| Metric | Value |
|--------|-------|
| Deep-dives used | N/6 |
| Iterations completed | N/3 |
| Perspectives shortlisted | N |
| Perspectives Adopted | N |
| Perspectives Deferred (with rationale) | N |
| Convergence reason | [all resolved / iteration limit / deep-dive budget / no changes needed] |
```

---

## Field Definitions

- **Review depth:** Set by the complexity gate (Light, Standard, Deep).
- **Deep-dive budget:** Running counter. Updated after each deep-dive. Header shows `N/6 used` to make the remaining budget visible at a glance.
- **Phase 2 header format:** `### Phase 2 — Deep-dive: <TAG> (iteration <N>, deep-dive <M>/6)` — the `M/6` counter is mandatory and tracks budget consumption.
- **Conflict Check:** Mandatory after each iteration that produces Phase 2 recommendations. Evaluates whether recommendations from different perspectives contradict each other.
- **Execution Metrics:** Mandatory section at the end of the review log. Provides data for tuning review thresholds over time.
