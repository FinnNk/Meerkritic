---
status: implemented
date: 2026-09-19
decision-makers:
  - Project owner
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

Retain each supplied record with source-hash/index identity in immutable
Parquet. SQLite registers metadata and an event atomically after publication. This
was implemented in the now-merged dataset batch (PR #3). The owner selected **Preserve source records**
in Codex on 2026-09-19; PR approval and merge remain separate.

### Consequences

- Different labels/context remain inspectable; absent commit SHAs stay unknown.
- Changed source bytes create new identities. Cross-revision matching is future work.
- Repeated comments are not independent evaluation examples by default; empirical
  sampling must account for related observations.
- A crash can leave an unreferenced artefact, never a partially published file;
  automatic garbage collection is deferred.

### Confirmation

The [dataset tests](../../tests/test_datasets.py) pass for repeated identities,
checksum rejection, restart/idempotence, transaction rollback and immutable-event
enforcement. All 15 tests and the canonical static checks passed again after the
commenting backfill. The pinned 1,030-record sample also registered and reopened
successfully, with one event after repeated registration, in the retained
[r3 registration evidence](https://github.com/FinnNk/Meerkritic/blob/2d8cd8d3024eeb70ef35f1afcbff8279141c71b6/p1-isolated-live.json).
The owner has now accepted the decision; implementation and confirmation are
complete and integrated through PR #3. Revisit when cross-source matching or retention
requirements become concrete.

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
