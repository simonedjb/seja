# L2 — Practitioner (Mid-level)

> Team members who work independently on familiar tasks. Need context on *what* and *when*.

## Characteristics

- Solid professional experience (2-5 years)
- Can complete well-defined tasks independently
- Needs guidance on project-specific patterns, not general skills
- Starting to understand trade-offs but may not see the full picture
- Can contribute to code reviews but may miss architectural implications

## Layer 2 — Level-Specific Onboarding Content

### Support Structure

- **Onboarding buddy**: Pair with an L3+ team member for context questions. Weekly 30-minute sync for the first month.
- **Architecture walkthrough**: Dedicated 1-hour session with a senior team member to cover system design decisions and trade-offs.
- **Domain context session**: 1-hour session with a Shaper (PM or designer) to understand user goals, personas, and product direction.

### Learning Path

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1 | Environment setup, architecture overview, conventions review | First PR merged (moderate complexity) |
| 2 | Deep-dive into assigned area, dependency mapping | Second PR + one code review given |
| 3-4 | Independent feature work or significant bug fix | Feature branch completed end-to-end |
| 5-8 | Cross-area exploration, process contribution | Contribution outside initial assigned area |

### Material Format Preferences

- **Do**: Architecture diagrams, convention reference sheets, "why we chose X over Y" decision records, curated reading lists of key files
- **Don't**: Step-by-step hand-holding (too slow), full codebase walkthrough (too broad)

### AI-Assisted Development Guidance

- Use AI to **accelerate context acquisition**: "Explain the data flow for [feature]", "What are the conventions for [pattern] in this project?"
- Use AI for **code generation** but always verify against project conventions — AI may suggest patterns that don't match the project
- Start using AI for **code review assistance**: "What could go wrong with this approach?", "Are there edge cases I'm missing?"
- Begin developing **judgment about AI output**: when to trust, when to question, when to override

### Onboarding Milestones

| Milestone | Target | Verification |
|-----------|--------|-------------|
| Architecture mental model | Week 1 | Can draw the system diagram from memory |
| Convention fluency | Week 2 | PRs pass review with no convention feedback |
| Independent feature delivery | Month 1 | End-to-end feature without architectural guidance |
| Meaningful code reviews | Month 2 | Review feedback that catches real issues |
| Cross-area contribution | Month 3 | Successful PR in an unfamiliar area of the codebase |
