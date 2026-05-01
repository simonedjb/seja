---
designer_description: "Maintainer rationale for generate_call_graph.py: historical artifact citations and design-choice context extracted from the script body so runtime code stays concise while the audit trail remains self-contained."
---

# generate_call_graph rationale

Maintainer-only context for `generate_call_graph.py`. This file is not imported or loaded by the script; it is versioned next to the script so historical design context stays discoverable without keeping private artifact citations in runtime comments.

> Runtime contract: do not import this file from Python code. Keep each citation entry to one self-contained paragraph that explains what the cited artifact changed and why the script is marked by it.

## Citation rationale

- **plan-000438**: The call graph gained conditional edge annotations so delegations gated by command flags can carry a `when` value instead of appearing unconditional. The extractor keeps this conservative and pattern-based so unmatched prose still yields ordinary unannotated edges.
- **check-000440 Finding 2 and plan-000443**: The scope-restriction fix prevents conditional prose from fabricating edges that the baseline extractor did not find. This keeps the annotation pass as an enrichment step over real edges, avoiding false-positive graph relationships.
- **plan-000466**: The call graph reads SKILL-quickguide.md siblings for skill descriptions because Quick Guide narrative no longer lives in SKILL.md. This keeps graph node descriptions designer-facing without reloading runtime execution instructions.
- **plan-000475**: The graph understands Dispatch B internal worker skills and emits dashed `dispatches-inline` edges from wrapper skills to `_internal/<wrapper>/<mode>/SKILL.md`. These edges document inlined execution topology without treating internal workers as user-facing skills.
