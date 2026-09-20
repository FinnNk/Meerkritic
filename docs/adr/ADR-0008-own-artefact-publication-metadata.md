---
status: implemented
date: 2026-09-20
decision-makers:
  - Project owner
---

# ADR-0008: Make artefact publication metadata explicit

## Context and Problem Statement

The VS1 result store inferred evidence kind and job ownership from JSON body keys
only when optional catalogue storage was enabled. Its declared interface omitted
those requirements and a maintenance operation used by the CLI. The owner
authorised correction of these findings in the milestone review batch.

## Decision Drivers

- Hide storage mechanics without hiding caller obligations.
- Preserve immutable evidence, existing hashes and publication ordering.
- Avoid separate optional runtime behaviours and speculative service layers.

## Considered Options

- Document the existing payload-key conventions and optional catalogue mode.
- Supply explicit publication metadata and expose maintenance independently.
- Introduce a generic artefact framework and a schema registry.

## Decision Outcome

Use explicit application-owned `Publication` metadata and a mandatory runtime
catalogue. JSON body keys do not choose evidence kind or owner. `ResultStore`
declares publication/read semantics; `ArtefactIndex` declares maintenance used by
the CLI. Keep file publication before catalogue registration and accepted-result
references. This refines the storage boundary without changing evidence ownership.

### Consequences

- Callers supply job and kind directly; filesystem/catalogue mechanics remain hidden.
- Legacy references are indexed from relational job/annotation ownership, with
  integrity checks and unchanged payload bytes. Existing hashes remain valid.
- A later catalogue failure may leave a complete orphan file; retries are explicit.
- New artefact kinds still require a deliberate schema/contract change.

### Confirmation

The artefact/job tests demonstrate that payload keys cannot alter catalogue metadata,
non-object input fails before publication, legacy bodies retain their exact bytes/hash,
retries preserve identity, metadata conflicts fail, and publication failures retain
consistent references. All 102 tests and canonical gates passed; the
[VS1 milestone review](../slice-reviews/VS1-milestone-architecture-review.md) records
the live compatibility and backup-migration checks. Implementation is confirmed in
this candidate; owner PR approval and integration remain separate.

## More Information

This implements an authorised design correction, not an empirical choice.
See [operational evidence](../development/operational-evidence.md) and
[ADR-0006](ADR-0006-recover-jobs-under-process-lock.md) for completion ordering.

Integration confirmation, 20 September 2026: owner-approved PR #9 landed at
`fa6856bff52efecba55700572cb10e67f9a8f3c0`, with exactly the reviewed tree and
a fresh canonical run passing 102 tests. Decision status remains implemented.
