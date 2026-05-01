---
designer_description: "Maintainer rationale for generate_harness_reference.py: historical artifact citations and design-choice context extracted from the script body so runtime code stays concise while the audit trail remains self-contained."
---

# generate_harness_reference rationale

Maintainer-only context for `generate_harness_reference.py`. This file is not imported or loaded by the script; it is versioned next to the script so historical design context stays discoverable without keeping private artifact citations in runtime comments.

> Runtime contract: do not import this file from Python code. Keep each citation entry to one self-contained paragraph that explains what the cited artifact changed and why the script is marked by it.

## Citation rationale

- **plan-000280 and plan-000281**: The harness reference generator consumes the public-doc filename scanner so each harness artifact can show where it is mentioned in user-facing docs. The citation is moved here because the generator only needs the scanner path and does not need private plan history inline.
- **plan-000457**: The generator classifies scripts by Invocation and Lifecycle docstring headers and renders grouped Scripts tables. The bucket ordering and header parser stay in code because they are runtime behavior; the historical reason for that shape belongs in this sibling.
