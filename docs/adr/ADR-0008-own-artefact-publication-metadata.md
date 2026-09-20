---
status: accepted
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

Verify payload keys cannot alter catalogue metadata, real legacy bodies index
without rewriting, retries preserve identity, metadata conflicts fail, and partial
publication failures preserve existing state. Canonical checks and milestone review
record implementation confirmation separately from owner PR approval.

## More Information

This implements an authorised design correction, not an empirical choice.
See [operational evidence](../development/operational-evidence.md) and
[ADR-0006](ADR-0006-recover-jobs-under-process-lock.md) for completion ordering.
