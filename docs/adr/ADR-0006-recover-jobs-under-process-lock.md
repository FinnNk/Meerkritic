---
status: implemented
date: 2026-09-20
decision-makers:
  - Project owner
---

# ADR-0006: Recover interrupted jobs under an exclusive process lock

## Context and Problem Statement

VS1 executes model work outside HTTP and needs restart recovery on one local machine.
A late heartbeat does not prove process death; replaying an uncertain invocation can
duplicate model work. SQLite state and immutable artefact publication cannot be one
transaction with the provider call.

## Decision Drivers

- Preserve honest outcomes and uncertain completion after crashes.
- Allow one heavy local job without introducing a distributed queue.
- Keep web requests short and operational history append-only.

## Considered Options

- OS-held process lock with explicit failed-interruption records and no automatic replay.
- Heartbeat expiry followed by automatic requeue.
- A distributed queue or durable framework runtime.

## Decision Outcome

Accepted through the owner's approval and merge of PR #6: the worker holds an OS lock on the local
data root for its lifetime. On startup, after acquiring it, mark old running jobs failed
and append interruption events. Preserve existing route, usage and artefact evidence.
The operator can inspect and explicitly submit a new invocation. Heartbeat age only
affects the inspection display. Database ownership checks fence obsolete writes.

Publish complete hash-addressed result bundles before committing completion references.
Retain orphaned complete bundles on partial failure. A completed job is immutable.
This extends [ADR-0005: immutable routing provenance](ADR-0005-retain-immutable-routing-provenance.md).

### Consequences

- No repeated call is disguised as recovery of the original invocation.
- A live hung worker requires operator intervention; an overdue heartbeat cannot evict it.
- The runtime needs a local filesystem supporting process locks and atomic hard links.
- More than one machine or automatic replay would require a new decision.

### Confirmation

The `vs1-normalisation` DER evidence records Windows subprocess lock exclusion/release,
concurrent claims, restart interruption events, old-worker rejection and artefact integrity.
Real MAF/inference and browser evidence supplements deterministic tests. PR #6 was
approved and merged on 19 September 2026. All five integrated proposition trees
match the reviewed series, and all 72 tests plus architecture/style gates passed
on the merged revision in a clean Windows checkout. The integration record is
indexed by `vs1-annotation/r1/pr6-integration.json` in the external DER store.
The ordinary workspace's Ruff crash is retained separately; no ignore was added.

The milestone follow-up makes this existing policy structural: application-owned
`Worker.run` acquires exclusivity before recovery or claims and retains it through
execution. Lock-refusal and existing process-death/recovery tests confirm that
callers no longer coordinate the lifecycle themselves. This is a refinement of the
same policy, not a new recovery or replay decision.

## More Information

This is a correctness/recovery design constrained by the single-worker VS1 architecture,
not a comparative data-driven choice. No EDR is required. Its concurrency assumptions
must be revisited if workers can run outside the cooperating entry point or on other hosts.
