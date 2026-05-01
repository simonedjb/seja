---
designer_description: "Maintainer rationale for scan_public_docs_for_filenames.py: historical artifact citations and design-choice context extracted from the script body so runtime code stays concise while the audit trail remains self-contained."
---

# scan_public_docs_for_filenames rationale

Maintainer-only context for `scan_public_docs_for_filenames.py`. This file is not imported or loaded by the script; it is versioned next to the script so historical design context stays discoverable without keeping private artifact citations in runtime comments.

> Runtime contract: do not import this file from Python code. Keep each citation entry to one self-contained paragraph that explains what the cited artifact changed and why the script is marked by it.

## Citation rationale

- **plan-000281**: The scanner feeds the harness reference generator by mapping harness files to public docs that mention them. Keeping this rationale in the sibling leaves the script body focused on producing the JSON map.
