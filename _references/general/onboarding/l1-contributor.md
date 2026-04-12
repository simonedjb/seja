# L1 -- Contributor (Junior to Mid-level)

> Individual contributors learning the project. Need guidance on *how*, *what*, and *where*.

## Characteristics

- Professional experience ranging from newcomer (0-2 years) to mid-level practitioner (2-5 years)
- Newcomers need explicit step-by-step instructions; practitioners can complete well-defined tasks independently
- Benefits from structured mentorship, though the intensity varies with experience
- Newcomers learn best through guided practice; practitioners need project-specific context, not general skills
- May not yet see the full picture of architectural trade-offs

## Layer 2 -- Level-Specific Onboarding Content

### Support Structure

**For newcomers (0-2 years):**
- **Buddy/mentor assignment**: Pair with an L2+ team member. Schedule daily 15-minute check-ins for the first two weeks, then twice weekly for the next month.
- **Pair programming sessions**: Minimum 2 hours per week for the first month, working on real tasks together.
- **Code review mentoring**: First 5 PRs should be reviewed with detailed, educational feedback -- not just approval/rejection but explanation of *why*.

**For practitioners (2-5 years):**
- **Onboarding buddy**: Pair with an L2+ team member for context questions. Weekly 30-minute sync for the first month.
- **Architecture walkthrough**: Dedicated 1-hour session with a senior team member to cover system design decisions and trade-offs.
- **Domain context session**: 1-hour session with a Shaper (PM or designer) to understand user goals, personas, and product direction.

### Learning Path

| Week | Focus (Newcomer) | Focus (Practitioner) | Deliverable |
|------|-------------------|----------------------|-------------|
| 1 | Environment setup, project overview, first guided task | Environment setup, architecture overview, conventions review | First commit/PR merged |
| 2 | Conventions deep-dive, second guided task | Deep-dive into assigned area, dependency mapping | Second commit + one code review given (practitioner) |
| 3-4 | First independent task (well-scoped, with safety net) | Independent feature work or significant bug fix | Independent PR / feature branch completed |
| 5-8 | Gradual task complexity increase | Cross-area exploration, process contribution | Consistent contributions with decreasing review feedback / contribution outside initial area |

### Material Format Preferences

**For newcomers:**
- **Do**: Step-by-step walkthroughs, annotated code examples, video recordings of pair sessions, checklists
- **Don't**: Dense reference documents, architecture decision records (too abstract), large-scope tasks

**For practitioners:**
- **Do**: Architecture diagrams, convention reference sheets, "why we chose X over Y" decision records, curated reading lists of key files
- **Don't**: Step-by-step hand-holding (too slow), full codebase walkthrough (too broad)

### AI-Assisted Development Guidance

- Start by using AI to **explore and understand** the codebase: "What does this function do?", "How is this component used?"
- Always **read and understand** AI-generated code before committing -- never treat it as a black box
- Use AI to **explain error messages** and suggest fixes, then verify the suggestion makes sense
- Use AI to **accelerate context acquisition**: "Explain the data flow for [feature]", "What are the conventions for [pattern] in this project?"
- Use AI for **code generation** but always verify against project conventions -- AI may suggest patterns that don't match the project
- Start using AI for **code review assistance**: "What could go wrong with this approach?", "Are there edge cases I'm missing?"
- Begin developing **judgment about AI output**: when to trust, when to question, when to override
- **Red flag**: If you can't explain what the code does in plain language, don't commit it

### Onboarding Milestones

| Milestone | Target | Verification |
|-----------|--------|-------------|
| Environment running | Day 1 | All tests pass locally |
| First commit | Week 1 | PR merged with mentor/buddy approval |
| Architecture mental model | Week 1-2 | Can draw the system diagram from memory (practitioner) |
| Convention fluency | Week 2-4 | PRs pass review with minimal style/convention feedback |
| Independent feature delivery | Month 1-2 | End-to-end feature without architectural guidance |
| Meaningful code reviews | Month 2-3 | Review feedback that catches real issues |
| Cross-area contribution | Month 3+ | Successful PR in an unfamiliar area of the codebase |
