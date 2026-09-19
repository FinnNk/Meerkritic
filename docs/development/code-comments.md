# Code comments and docstrings

Use Python docstrings on module-exposed functions and methods: interfaces consumed by other modules, application entry points and HTTP handlers. Give callers enough information to use an operation without reading its body. Explain relevant side effects, failures and constraints. Prefer the shortest complete explanation; brevity must not hide part of the contract.

Document internal methods when their intent or implementation is not obvious.
Within an implementation, explain the reason for a choice, an invariant or required
ordering. For example, explain why verified artefacts must be published before
registry metadata makes them discoverable. Do not narrate individual statements,
repeat type annotations or add comments to obvious helpers just for coverage.

Start with an imperative summary such as "Return a page of observations." A single sentence is sufficient for a simple contract. For richer contracts, use Google-style `Args`, `Returns` or `Yields`, and `Raises` sections as applicable, with four-space section indentation. Describe meaning, bounds, units, ordering, empty results and caller-relevant failures; do not repeat annotated types or catalogue incidental implementation exceptions. Omit empty or redundant sections. Describe decorated functions as callers experience them: a context manager returns a managed context rather than exposing a generator API.

Add class docstrings explaining what instances represent and any significant invariants or provenance semantics. Use `Attributes` for fields that need explanation; typed, self-explanatory fields do not need restating. Distinguish expected values from validation actually performed by the class. Test names often suffice; document unusual setup or constraints rather than repeat the test name.

Put the shared contract on the interface and explain implementation-specific behaviour where needed. Comments must describe the code present at that revision. Keep British English and the project's 100-character limit; Google is a source for these selected conventions, not an adopted whole-project standard. The choice and pinned source are recorded in [ADR-0003](../adr/ADR-0003-document-caller-contracts-and-intent.md).

For new or changed code, include its comments in the same semantic commit as that
code. Backfilling existing code is a separate commit. Keep changes to this guidance
and its rationale separate from their application. Preserve actual chronology on
the DER diary before reconstructing those semantic boundaries.

During review, check exposed operations and non-obvious internal logic, and update
stale comments alongside implementation changes. This is a judgement-based review,
not a docstring-count target or a new lint exemption. Existing quality gates still
apply. Do not change imported research or third-party skill files to impose this
first-party convention.

See [ADR-0003: Document caller contracts and non-obvious intent](../adr/ADR-0003-document-caller-contracts-and-intent.md).
