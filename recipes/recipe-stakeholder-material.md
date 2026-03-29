# Recipe: Generate Stakeholder Material

## Goal

Generate communication material tailored for a specific audience.

## Prerequisites

- SEJA framework installed and `/quickstart` / `$quickstart` completed
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

3. **Generate HTML output (optional)**
   ```
   /communication EVL --format html   # Claude
   $communication EVL --format html   # Codex
   ```
   Produces a styled HTML version suitable for sharing outside the team.

4. **Generate material for all segments at once**
   ```
   /communication --all   # Claude
   $communication --all   # Codex
   ```

5. **Review and customize**
   Generated material lands in `_output/communication/`. Edit as needed
   before sharing.

## Tips

- Each audience gets fundamentally different content -- evaluators need
  architecture and ROI, clients need outcomes and cost, end users need
  quality commitment, academics need theoretical foundation.
- Use `/communication --deep` / `$communication --deep` for expanded content beyond the essentials.
- Regenerate material after major milestones to keep it current.

## Related journeys

- [Solo Designer Greenfield](../journeys/journey-solo-designer-greenfield.md)
- [Agency Multi-Project](../journeys/journey-agency-multi-project.md)
- [Enterprise Evolution](../journeys/journey-enterprise-evolution.md)
- [Teaching/Research](../journeys/journey-teaching-research.md)
