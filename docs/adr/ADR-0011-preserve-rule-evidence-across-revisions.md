---
status: proposed
date: 2026-09-20
decision-makers: [Project owner]
---

# ADR-0011: Preserve rule evidence across immutable revisions

## Context and Problem Statement

A candidate synthesised from related interpretations is a research proposal.
Changing its definition must not erase counterexamples, silently carry a human
approval to a different rule, or imply that model output establishes validity.

## Decision Drivers

- Inspectable provenance from exact rule versions to frozen source annotations.
- Explicit weak/verified evidence claims and separate human decisions.
- Concurrent writes and retries must preserve intent and historical decisions.
- Keep persistence and version fencing inside one registry boundary.

## Considered Options

- Immutable rule bodies with an atomic current pointer and append-only evidence.
- Mutate one rule row, retaining only its latest evidence and decision.
- Build a general event-sourced aggregate and reconstruct every read.

## Decision Outcome

Proposed and implemented in this candidate: content-addressed rule bodies live
outside SQLite. The registry owns current version/revision, evidence links and
decisions in short transactions. A revision carries all evidence classifications
and parent links but resets inherited verification to weak. Old claims remain
intact; the new version begins as a candidate. Promotion records a reviewed
research candidate, never validation, enforcement or deployment.

The planned synthesis application uses the existing corpus queue and a project-owned runtime port. MAF
prepares bounded examples, invokes the routed model and validates structured
references. Raw output and a complete trace precede rule publication. An explicit
insufficiency result creates no candidate. Infrastructure failures do not trigger
model escalation or replay.

### Consequences

Readers can inspect historical definitions, evidence and decisions independently
of the current pointer. Immutable files may be orphaned after interrupted SQL
registration. Candidate publication and job finalisation are separate: a complete
candidate can survive a worker interruption while its job is recovered as failed.
Its trace identifies that invocation; operators inspect before explicitly retrying.

One version has at most 1,000 evidence links. A revision that would exceed that
bound is rejected without dropping inherited links. The bound is an operational
constraint, not an empirical optimum. Verification is a named human attestation,
not an automatic deduction from an accepted interpretation.

### Confirmation

`tests/test_rules.py` challenges concurrent decisions, idempotent retries, event
rollback, immutable history, source identity, revision bounds and stale browser
submissions. The next proposition will supply synthesis runtime and interrupted-publication checks. External DER `vs2-rules/r1` records exact checks
and live local compatibility. Owner acceptance remains pending. Revisit on a
demonstrated evidence bound or a need for different review authority.

## Pros and Cons of the Options

The selected design retains history without requiring replay to read operational
state. A mutable row is smaller but loses the evidence needed to challenge a rule.
Full event sourcing adds schema/replay obligations without a demonstrated need.

## More Information

- [Rule inspection and synthesis](../development/rules.md).
- [ADR-0010 (Own immutable discovery runs under the shared worker)](ADR-0010-own-discovery-runs-under-one-worker.md).
- EDR-0001 (Choose an initial discovery grouping method) remains draft. This
  engineering contract does not decide model or grouping quality.
