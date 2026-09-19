---
status: proposed
date: 2026-09-19
decision-makers: []
---

# ADR-0002: Preserve source records before interpretation

## Context and Problem Statement

Review datasets may repeat a comment with different context or labels. Normalisation
and later human annotation need stable references to the evidence actually imported.

## Decision Drivers

- Preserve source evidence without silently selecting one interpretation.
- Make registration reproducible and idempotent across restarts.
- Keep bulk data outside operational SQLite and source control.

## Considered Options

- Identify each record by pinned source hash and index; preserve original identifiers.
- Deduplicate by repository/comment ID before registration.

## Decision Outcome

Proposed: retain each supplied record with source-hash/index identity in immutable
Parquet. SQLite registers metadata and an event atomically after publication. This
is implemented in the candidate batch, pending owner decision and merge.

### Consequences

- Different labels/context remain inspectable; absent commit SHAs stay unknown.
- Changed source bytes create new identities. Cross-revision matching is future work.
- Repeated comments are not independent evaluation examples by default; empirical
  sampling must account for related observations.
- A crash can leave an unreferenced artefact, never a partially published file;
  automatic garbage collection is deferred.

### Confirmation

Candidate tests cover repeated identities, checksum rejection, restart/idempotence,
transaction rollback and immutable-event enforcement. The pinned 1,030-record sample
registers successfully. The owner reviews this proposal with the batch. Revisit when
cross-source matching or retention requirements become concrete.

## Pros and Cons of the Options

### Preserve source records

- Maintains the imported evidence, including conflicts and duplicates.
- Requires explicit grouping/sampling later rather than assuming independence.

### Deduplicate before registration

- Simplifies browsing repeated comments.
- Discards evidence or requires an unsupported choice between different contexts.

## More Information

See the [dataset guide](../development/datasets.md). CRC-Py contains six repeated
comment identities; this exposed an invalid importer assumption during integration.
The decision follows the required provenance guarantee, not a comparative empirical
claim, so no EDR was needed. Later data-driven sampling decisions do require one.
