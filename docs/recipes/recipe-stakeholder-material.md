# Recipe: Generate Stakeholder Material

## Goal

Generate communication material tailored for a specific audience.

## Prerequisites

- SEJA framework seeded and project configured via `/seed` + `/design` / `$seed` + `$design`
- Project conceptual design files populated (at minimum the to-be design)

## Steps

1. **Identify the audience segment**
   - **EVL** -- Evaluators (CTOs, tech leads, architects)
   - **CLT** -- Clients (VPs, budget owners, executives)
   - **USR** -- End users (product users, support teams)
   - **ACD** -- Academics (researchers, educators)

2. **Generate material for one audience**
   ```
   /communication EVL   # Claude
   $communication EVL   # Codex
   ```
   Replace `EVL` with the segment code that matches your audience.
   By default, both a Markdown artifact and a styled HTML version are
   generated -- ready for internal review and external sharing.

3. **Generate material for all segments at once**
   ```
   /communication --all   # Claude
   $communication --all   # Codex
   ```

4. **Review and customize**
   Generated material lands in `_output/communication/`. Edit as needed
   before sharing.

## Tips

- Each audience gets fundamentally different content -- evaluators need
  architecture and ROI, clients need outcomes and cost, end users need
  quality commitment, academics need theoretical foundation.
- Use `/communication --deep` / `$communication --deep` to include deeper technical sections (architecture details, development roadmap, research foundation) beyond the essentials. Useful for evaluators and academics who need comprehensive context.
- Regenerate material after major milestones to keep it current.

## Related journeys

- [Solo Designer Greenfield](../journeys/journey-solo-designer-greenfield.md)
- [Agency Multi-Project](../journeys/journey-agency-multi-project.md)
- [Enterprise Evolution](../journeys/journey-enterprise-evolution.md)
- [Teaching/Research](../journeys/journey-teaching-research.md)
