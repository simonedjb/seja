# L3 -- Leader (Staff / Principal / Manager)

> Team members with strategic or managerial influence. Need *organizational context* and *team dynamics*.

## Characteristics

- Deep and broad experience (10+ years or equivalent impact)
- Thinks in systems, not features -- sees cross-team and cross-domain implications
- Expected to influence technical direction beyond their immediate team (Strategist) or own process and people outcomes (Manager)
- Needs to understand organizational constraints, not just technical ones
- Must quickly earn trust and avoid disrupting working patterns unnecessarily
- May be joining to address a specific strategic challenge or to lead a team through a transition

## Layer 2 -- Level-Specific Onboarding Content

### Support Structure

**For strategists (IC-track, Staff/Principal):**
- **Executive sponsor**: Direct access to engineering leadership for strategic context, organizational history, and political landscape.
- **Cross-team liaison**: Introductions to leads of all teams that interact with this project. Schedule dedicated 1:1s within the first week.
- **Strategic context briefing**: 1-hour session covering: why the team exists, what success looks like, what the biggest risks are, what's been tried and failed.

**For managers (people-track, Tech Lead/EM):**
- **Leadership peer**: Pair with another tech lead or engineering manager for organizational context and norms.
- **Team retrospective access**: Review the last 3-6 months of retrospective notes to understand team health patterns.
- **1:1 with every team member**: Schedule 30-minute introductory 1:1s with each team member within the first two weeks. Listen more than talk.

### Learning Path

| Week | Focus (Strategist) | Focus (Manager) | Deliverable |
|------|---------------------|------------------|-------------|
| 1 | Organizational context, cross-team dependencies, strategic priorities | Team introductions, process observation, 1:1s | Stakeholder map (Strategist) / team dynamics assessment (Manager) |
| 2 | Technical debt audit, system-wide architecture review | Process review, governance audit, metrics review | Technical vision draft (Strategist) / process improvement shortlist (Manager) |
| 3-4 | First cross-cutting initiative (architectural improvement, process change, or debt reduction) | First process improvement, hiring/staffing review | Initiative proposal (Strategist) / one quick win implemented (Manager) |
| 5-12 | Strategic execution, coalition building | Team development, strategic alignment, sustainable cadence | Measurable progress on initiative (Strategist) / team operating rhythm established (Manager) |

### Material Format Preferences

**For strategists:**
- **Do**: Strategic roadmaps, cross-team dependency maps, technical debt inventories with business impact, historical incident postmortems, org charts with responsibilities
- **Don't**: Coding tutorials, convention guides (they'll absorb these from code review), isolated component documentation

**For managers:**
- **Do**: Team health dashboards, DORA metrics history, retrospective summaries, escalation path documentation, hiring pipeline status, team skill matrix
- **Don't**: Detailed coding guides (they'll code-review to learn), individual module documentation (too granular for first weeks)

### Onboarding Focus Areas

- **Technical debt landscape**: Full inventory with severity, business impact, and payoff timelines. Use `/advise --inventory` to generate if not available.
- **Cross-team dependencies**: Which teams depend on this system, what SLAs exist, where friction occurs.
- **Failed initiatives**: What has been tried before and why it didn't work -- this prevents repeating mistakes.
- **Budget and resource constraints**: Team size, hiring plans, infrastructure costs, vendor contracts.
- **Compliance and regulatory context**: What external obligations constrain technical decisions.
- **Team composition and skills** (Manager): Who does what, skill gaps, growth aspirations, flight risks.
- **Process and ceremonies** (Manager): Sprint cadence, standup format, retrospective process, planning process. What's working and what's not.
- **Escalation paths** (Manager): When and how to escalate technical issues, people issues, cross-team conflicts.
- **Hiring context** (Manager): Open roles, hiring pipeline, interview process, onboarding pipeline for future hires.

### Governance Areas to Audit

Within the first month, review and understand:

| Area | Key Questions |
|------|--------------|
| Code review | Who reviews what? Average turnaround? Quality of feedback? |
| Deployment | How often? Who approves? What's the rollback process? |
| Incident response | Who's on call? What's the SLA? How are postmortems run? |
| Technical debt | Is there an inventory? How is it prioritized against features? |
| Team development | Are there growth plans? Regular feedback? Learning budget? |

### AI-Assisted Development Guidance

- Use AI for **system-wide analysis**: "What are the common patterns across all services?", "Where are the consistency gaps?"
- Use AI for **impact assessment**: "If we change [module], what are all the downstream effects?"
- Leverage AI for **documentation generation**: Use `/explain architecture` and `/advise --inventory` to create comprehensive system maps
- Shape the team's **AI strategy**: Evaluate where AI tools add the most value and establish guidelines for their use
- Use AI for **rapid codebase orientation** (Manager): Enough to review code and make architectural decisions, not necessarily to write code
- Use AI for **process documentation** (Manager): Generate or improve team process docs, runbooks, onboarding guides for future hires
- Establish team **AI usage norms** (Manager): What AI tools are sanctioned, how AI-generated code should be reviewed, what quality bar applies

### Onboarding Milestones

| Milestone | Target | Verification |
|-----------|--------|-------------|
| Organizational context / team relationships | Week 1-2 | Can explain cross-team dynamics (Strategist) / completed 1:1s with all team members (Manager) |
| Technical vision / process understanding | Week 2 | Draft vision shared (Strategist) / can describe team cadence and pain points (Manager) |
| First strategic initiative / quick win | Month 1 | Cross-cutting improvement in progress (Strategist) / one process improvement implemented (Manager) |
| Influence established / trust earned | Month 2-3 | Other teams consult on decisions (Strategist) / team brings issues proactively (Manager) |
| Measurable impact / sustainable cadence | Month 3-6 | Visible improvement in a system-wide metric (Strategist) / team operating rhythm reflects leadership (Manager) |
