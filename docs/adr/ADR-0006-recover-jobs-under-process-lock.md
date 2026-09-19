---
status: proposed
date: 2026-09-19
decision-makers:
  - Project owner (acceptance pending)
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

Proposed and implemented in this candidate: the worker holds an OS lock on the local
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
Real MAF/inference and browser evidence supplements deterministic tests. Owner acceptance
is pending; passing candidate tests does not itself advance this ADR to implemented.

## More Information

This is a correctness/recovery design constrained by the single-worker VS1 architecture,
not a comparative data-driven choice. No EDR is required. Its concurrency assumptions
must be revisited if workers can run outside the cooperating entry point or on other hosts.
