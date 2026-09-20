---
status: implemented
date: 2026-09-19
decision-makers:
  - Project owner
---

# ADR-0004: Adopt a selective Python style guide

## Context and Problem Statement

The project has enforced formatting and dependency boundaries, but needs a concise reference for Python choices that require judgement. The owner reviewed recommendations based on Google's Python guide and accepted a project-specific selection, including explicit references and a clear statement of adoption scope.

## Decision Drivers

- Make everyday code and caller contracts consistent and understandable.
- Preserve the project's established tooling, architecture rules and concise documentation.
- State exactly which external guidance applies and avoid silent changes from a moving upstream page.

## Considered Options

- Continue with tool configuration and individual reviewer preferences.
- Adopt the complete Google Python Style Guide.
- Adopt selected principles with explicit project choices and a pinned reference.

## Decision Outcome

Adopt the selected principles and project choices in the [Python style guide](../development/python-style.md). Google's guide [1] informs documentation, simple expressions, state, errors, resource handling, function cohesion and typing. **It has not been adopted in its entirety.** Only the scope enumerated in the project guide applies; other upstream advice remains non-binding reference material.

Retain Ruff and the 100-character limit, absolute imports with direct symbol imports permitted, British English, imperative summaries and the existing Import Linter/Tach contracts. Do not add another formatter, Pylint, mandatory boilerplate or blanket documentation quotas. Mechanical checks and human review have complementary roles. Apply annotation changes that alter framework behaviour as software changes rather than style-only edits.

The source baseline is revision `3b8822983dc779c498961cc86332a28c07590f64` [1]. Changes to that source are not automatically adopted. This broader policy complements [ADR-0003: Document caller contracts and non-obvious intent](ADR-0003-document-caller-contracts-and-intent.md); it does not supersede that decision.

### Consequences

- Contributors have a small, explicit policy with a reproducible external reference.
- Project-specific exceptions remain visible rather than relying on implied wholesale compliance.
- Reviewers still judge clarity and contract completeness; tools cannot establish those properties alone.
- Future adoption changes require a deliberate documentation update, and historical code may need bounded backfills.

### Confirmation

The implementing agent checked that the guide, agent instructions and development index agree on scope and precedence, and that ADR-0003 and this record contain numbered IEEE references to the same pinned source. Caller-contract and class documentation is applied, with the existing quality runner backfilled separately; semantic policy commits remain separate from application. After review, `uv run --locked python tools/check.py` passed Ruff formatting/lint, Import Linter, Tach and all 15 tests on Windows/Python 3.12. The external DER r5 evidence linked from [PR #3](https://github.com/FinnNk/Meerkritic/pull/3) retains the results. The policy was subsequently approved and merged in PR #3. Later implementation and bounded backfills remain subject to the same selective policy.

Existing code was reviewed within the current change's scope; adoption does not assert complete retroactive conformance. Revisit rules that repeatedly obscure intent or conflict with validated framework behaviour.

## Pros and Cons of the Options

### Existing tools and individual preferences

- Requires no new guide.
- Leaves recurring readability and documentation questions to inconsistent judgement.

### Complete Google guide

- Provides a broad external standard.
- Conflicts with deliberate project tooling and import choices and imposes unreviewed rules.

### Explicit selection with project choices

- Reuses useful guidance while preserving the project's established constraints.
- Requires maintaining the adopted scope and reviewing later changes deliberately.

## More Information

The owner accepted this recommendation in Codex on 19 September 2026. This is a prescribed development-policy decision, not a claim established by comparative data; no EDR is required. PR acceptance and merge remain separate from adopting this policy.

## References

[1] Google, "Google Python Style Guide," *Google Style Guides*, rev. 3b8822983dc779c498961cc86332a28c07590f64, Sep. 11, 2026. Accessed: Sep. 19, 2026. [Online]. Available: [pinned guide source](https://github.com/google/styleguide/blob/3b8822983dc779c498961cc86332a28c07590f64/pyguide.md).
