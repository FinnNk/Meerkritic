---
status: implemented
date: 2026-09-19
decision-makers:
  - Project owner
---

# ADR-0003: Document caller contracts and non-obvious intent

## Context and Problem Statement

The first dataset-browser PR exposes operations whose storage effects, identity
guarantees and failure behaviour cannot all be understood from their signatures.
The owner requested concise comments on exposed methods and on internal methods
whose intent or implementation is not obvious. Following discussion in Codex,
the owner accepted the convention and asked for this ADR and a completed backfill.

## Decision Drivers

- Let callers understand an operation without tracing its implementation.
- Preserve the reasons for non-obvious invariants and ordering.
- Keep comments brief, useful and maintainable as the code changes.
- Keep semantic review commits self-contained and distinguish guidance from application.

## Considered Options

- Continue relying on names, signatures and external documentation alone.
- Require exhaustive docstrings and structured parameter sections everywhere.
- Use concise caller-contract docstrings and selective explanations of internal intent.

## Decision Outcome

Use concise caller-contract docstrings and selective explanations of internal
intent, as agreed by the owner. The [code commenting guide](../development/code-comments.md)
defines the convention for maintained first-party Python code. New code carries
its comments in the same semantic commit; backfills of existing code have their
own commit. Guidance and rationale are committed separately from application.

The owner refined this decision after reviewing Google's Python guide [1, Sec. 3.8]. Adopt its caller-focused distinction between docstrings and internal comments, structured sections for richer contracts, and class-level meaning. A one-line summary is sufficient only when it fully describes the contract; completeness takes precedence over brevity. Use the project's imperative wording, British English and 100-character limit. **The Google guide has not been adopted in its entirety.** These selected conventions refine the same decision rather than superseding it.

### Consequences

- Callers can see relevant guarantees, side effects and constraints at the boundary.
- Internal comments retain reasoning that names and types cannot express.
- Authors and reviewers must keep prose accurate as behaviour changes.
- Coverage requires judgement; adding redundant prose to meet a quota is not useful.

### Confirmation

The implementing agent reviewed the exposed operations and non-obvious logic in
dataset registration, persistence, browsing, composition and architecture reporting.
The existing quality runner was backfilled separately. Comments describe the code
at each capability checkpoint; later browser behaviour is not claimed in the
registration checkpoint. Removing docstrings from the parsed Python trees leaves
the executable structure unchanged. HTTP handler docstrings also supply API
descriptions, so this comparison does not claim that documentation metadata is unchanged.

After the backfill, `uv run --locked python tools/check.py` passed Ruff formatting,
Ruff lint, Import Linter, Tach and all 15 tests on Windows/Python 3.12. The first
attempt found an overlong docstring; it was shortened and the full command rerun.
The successful application check and the earlier failure are retained in the
external DER r4 evidence linked from [PR #3](https://github.com/FinnNk/Meerkritic/pull/3).
This is implementation confirmation and self-review, not owner approval of the PR
or a claim that VS1 is complete. The owner explicitly requested `implemented`
after the backfill; the ADR and index now record that state.

The subsequent refinement expanded registration, pagination, publication, composition and architecture contracts and documented provenance records. The quality runner's result contract was backfilled separately. The canonical command passed again with all 15 tests after these edits. R5 evidence, linked from the same PR, records this verification; r4 retains the earlier implementation evidence. The refined convention is implemented in the candidate branch, with PR approval and merge still separate.

Review affected comments whenever code changes. Revisit the convention if reviews
find persistent redundancy, stale contracts or important unexplained behaviour.

## Pros and Cons of the Options

### Names and external documentation alone

- Minimises inline prose.
- Leaves important boundary guarantees and internal reasoning hard to discover.

### Exhaustive structured docstrings

- Gives a uniform layout.
- Repeats information already available in signatures and increases maintenance noise.

### Concise contracts and selective internal explanations

- Keeps relevant intent beside the code that relies on it.
- Requires judgement about which details help a caller or reviewer.

## More Information

- [Original review comment](https://github.com/FinnNk/Meerkritic/pull/3#issuecomment-5744986964),
  followed by the owner's agreement and commit-placement instructions in Codex.
- This is an owner-directed development convention, not a data-driven decision;
  no EDR is required.

## References

[1] Google, "Google Python Style Guide," *Google Style Guides*, rev. 3b8822983dc779c498961cc86332a28c07590f64, Sep. 11, 2026. Accessed: Sep. 19, 2026. [Online]. Available: [pinned guide source](https://github.com/google/styleguide/blob/3b8822983dc779c498961cc86332a28c07590f64/pyguide.md).
