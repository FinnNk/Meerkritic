# Navigation revision: author review

Scope: changes from published r1, new propositions P4/P5, shared-template consumers
and the aggregate source-reading result. Carry forward r1 review only for its
three unchanged SHAs and contracts; no independent review or owner approval.

- Inspected each existing header link against the new grouping: destination paths,
  text and availability conditions are retained. Empty groups are omitted.
- The brand precedes navigation, group labels are visible and navigation landmarks
  have accessible names. Semantic lists provide the links. Page-local assessment
  navigation is labelled separately; no form control is moved or submitted.
- CSS uses wrapping flex layouts, without fixed widths, hiding or truncating links.
  At 1280px all three groups occupy one row; at 375px all links remain in bounds.
  Tab reaches the brand with a solid visible focus outline. Browser records retain
  the measured dimensions. Shared pagination now also wraps rather than overflowing.
- Overview screenshots were visually inspected: their crops start below navigation.
  Existing assessment crops also exclude it. A new focused header image documents
  the change; existing captures retain their original provenance.
- Static templates add no application/domain abstraction. No architecture rules,
  runtime dependencies, routes, evidence contracts, prompts or database changes.
  Earlier source integrity and annotation safeguards remain unchanged.

The documentation index describes groups in plain English and distinguishes
rule-review work from software-change review references. The capture is synthetic.
The image was inspected directly; no rendered-document visual pass is claimed
under the earlier local-file browser policy limitation.

No implementation finding remains. Ordinary styling work does not need an ADR or
empirical experiment. Full canonical checks cover each new checkpoint; old exact
checkpoint evidence remains valid for those unchanged commits only.
