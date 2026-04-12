# L2 -- Expert (Senior)

> Team members with deep domain expertise. Need context on *why* and *trade-offs*.

## Characteristics

- Extensive professional experience (5-10 years)
- Strong opinions informed by experience -- needs to understand *why* things are done this way, not just *what*
- Can independently design and implement complex features
- Expected to mentor others and improve team practices
- May challenge existing patterns (productively) -- needs decision history to distinguish intentional choices from accidental ones

## Layer 2 -- Level-Specific Onboarding Content

### Support Structure

- **Architecture sponsor**: Pair with a tech lead or L3 to discuss system-wide design decisions and their rationale.
- **Decision history access**: Provide access to Architecture Decision Records, plan history (`${PLANS_DIR}/INDEX.md`), and historical briefs. Use `/explain behavior-evolution` for key features.
- **Stakeholder introductions**: Schedule 1:1s with key stakeholders (PM, design lead, other tech leads) within the first two weeks.

### Learning Path

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1 | Architecture deep-dive, decision history review, stakeholder 1:1s | Architecture critique document (what's strong, what could improve) |
| 2 | Technical debt exploration, codebase audit of assigned area | Technical debt assessment with prioritized recommendations |
| 3-4 | First significant contribution (complex feature or architectural improvement) | PR demonstrating understanding of project patterns and trade-offs |
| 5-8 | Cross-cutting improvement, mentoring contribution | System-wide improvement + mentoring an L1 member |

### Material Format Preferences

- **Do**: Architecture Decision Records, trade-off analyses, behavior evolution timelines, technical debt inventories, system design diagrams with rationale
- **Don't**: Step-by-step tutorials (too basic), convention lists without rationale (need the *why*)

### AI-Assisted Development Guidance

- Use AI for **rapid codebase comprehension**: "Trace the data flow from [entry point] to [database]", "What are all the callers of [function]?"
- Use AI as a **sounding board for design decisions**: "What are the trade-offs of approach A vs B for [problem]?"
- Leverage AI for **comprehensive code reviews**: Use `/check review` with the full perspective framework
- Contribute to **AI workflow improvement**: Identify where AI tools help most and where they fall short in this project's context

### Onboarding Milestones

| Milestone | Target | Verification |
|-----------|--------|-------------|
| System understanding | Week 1 | Can explain architectural trade-offs to a newcomer |
| Decision context | Week 2 | Understands *why* key decisions were made, not just *what* |
| First significant contribution | Month 1 | Complex PR that respects existing patterns while improving quality |
| Mentoring active | Month 2 | Actively mentoring at least one L1 member |
| Process improvement | Month 3 | Proposed and implemented at least one team practice improvement |
