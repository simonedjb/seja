# L4 — Strategist (Staff / Principal)

> Team members with cross-cutting influence. Need *organizational context*.

## Characteristics

- Deep and broad experience (10+ years or equivalent impact)
- Thinks in systems, not features — sees cross-team and cross-domain implications
- Expected to influence technical direction beyond their immediate team
- Needs to understand organizational constraints, not just technical ones
- May be joining to address a specific strategic challenge

## Layer 2 — Level-Specific Onboarding Content

### Support Structure

- **Executive sponsor**: Direct access to engineering leadership for strategic context, organizational history, and political landscape.
- **Cross-team liaison**: Introductions to leads of all teams that interact with this project. Schedule dedicated 1:1s within the first week.
- **Strategic context briefing**: 1-hour session covering: why the team exists, what success looks like, what the biggest risks are, what's been tried and failed.

### Learning Path

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1 | Organizational context, cross-team dependencies, strategic priorities | Stakeholder map + initial assessment of strategic landscape |
| 2 | Technical debt audit, system-wide architecture review | Technical vision draft (where should the system be in 12 months?) |
| 3-4 | First cross-cutting initiative (architectural improvement, process change, or debt reduction) | Initiative proposal with impact analysis and phased rollout plan |
| 5-12 | Strategic execution, coalition building | Measurable progress on cross-cutting initiative |

### Material Format Preferences

- **Do**: Strategic roadmaps, cross-team dependency maps, technical debt inventories with business impact, historical incident postmortems, org charts with responsibilities
- **Don't**: Coding tutorials, convention guides (they'll absorb these from code review), isolated component documentation

### Onboarding Focus Areas

- **Technical debt landscape**: Full inventory with severity, business impact, and payoff timelines. Use `/advise --inventory` to generate if not available.
- **Cross-team dependencies**: Which teams depend on this system, what SLAs exist, where friction occurs.
- **Failed initiatives**: What has been tried before and why it didn't work — this prevents repeating mistakes.
- **Budget and resource constraints**: Team size, hiring plans, infrastructure costs, vendor contracts.
- **Compliance and regulatory context**: What external obligations constrain technical decisions.

### AI-Assisted Development Guidance

- Use AI for **system-wide analysis**: "What are the common patterns across all services?", "Where are the consistency gaps?"
- Use AI for **impact assessment**: "If we change [module], what are all the downstream effects?"
- Leverage AI for **documentation generation**: Use `/explain architecture` and `/advise --inventory` to create comprehensive system maps
- Shape the team's **AI strategy**: Evaluate where AI tools add the most value and establish guidelines for their use

### Onboarding Milestones

| Milestone | Target | Verification |
|-----------|--------|-------------|
| Organizational context | Week 1 | Can explain cross-team dynamics and dependencies |
| Technical vision | Week 2 | Draft vision shared with team and stakeholders |
| First strategic initiative | Month 1 | Cross-cutting improvement in progress with stakeholder buy-in |
| Influence established | Month 3 | Other teams consult on technical decisions |
| Measurable impact | Month 6 | Visible improvement in a system-wide metric |
