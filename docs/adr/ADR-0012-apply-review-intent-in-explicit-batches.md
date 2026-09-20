---
status: implemented
date: 2026-09-20
decision-makers: [Project owner]
---

# ADR-0012: Apply review intent in explicit batches

## Context and Problem Statement

Discovery review needs saved intent, deferral and coherent guidance across several
rule versions. A saved draft or an agent response must not appear to be an applied
human decision. Partial application and automatic retries could lose intent or
repeat external work after uncertain completion.

## Decision Drivers

- Preserve exact source versions, named intent and append-only history.
- Apply a human decision batch atomically with optimistic version checks.
- Keep one worker lifecycle and explicit unknown external completion.
- Hide transaction choreography and framework details from UI callers.

## Considered Options

- Explicit saved drafts, atomic registry transactions and immutable advisory submissions.
- Apply each form change immediately and send each discussion message separately.
- Introduce full durable actors and replay model work automatically.

## Decision Outcome

Finn Newick accepted this architectural decision on 20 September 2026 in the
project conversation, separately from PR review. The owner subsequently
approved and merged PR #13; implementation and integrated confirmation are complete.

A review workspace owns saved
immutable draft payloads and version-checked application. Its storage adapter uses
the registry's canonical decision operation within one transaction. Every target
and event commits together or none does. Identical application retries return the
original receipt. Stale targets retain the saved draft for correction.

Review tasks expose pending, answered, deferred, reopened and superseded states.
Reopening is explicit; previous answers remain historical. Rule revision marks
the old task superseded with a replacement link. Discussion is append-only on an
exact version. Adding a message does not send it to an agent.

An explicit guidance send freezes selected definitions, revisions, instructions
and discussion messages. A separate bounded queue shares the existing worker lock
and round-robin lifecycle. Ordinary MAF returns advice only. Submission, response
and decision application are distinct; recovery marks interrupted work unknown
without replay. No durable framework actor is needed for this bounded operation.

### Consequences

The UI gains deliberate Save and Apply steps, and an explicit Send operation.
The registry remains the decision invariant owner rather than duplicating checks
in bulk handlers. Storage keeps small operational records while draft/context/
response bodies remain external immutable JSON. Files can be orphaned after SQL
failure; they cannot make a partially applied decision batch appear successful.

Drafts contain at most twenty targets. Guidance contains at most six versions and
twenty selected notes per version, within an 18,000-character context bound and
the provider's actual token budget. These are explicit operational limits, not
empirically chosen optima. Named actors remain local claims rather than authentication.

### Confirmation

`tests/test_interaction.py` covers restart, stale/concurrent drafts, rollback,
idempotency, lifecycle and exact-version discussion. `tests/test_guidance.py`
covers frozen context, invented output, provider failures, unknown completion,
context bounds and advice that never applies state. Real local MAF compatibility
is retained in external DER `vs2-interaction/r1`; the documentation revision's
checkpoint checks are retained in `vs2-interaction/r2`. The owner has accepted the
decision and merged [PR #13](https://github.com/FinnNk/Meerkritic/pull/13). Its integrated
revision `f7aa4e05411da9d804f3624abe57033544fb1073` preserves all nine ordered reviewed
commit trees and passed the canonical quality checks and 172 tests in its own clean,
locked Windows/Python 3.12 checkout. The post-merge evidence is indexed by the
[VS2 integration record](../slice-reviews/VS2-integration.md).
Revisit durable orchestration only when a concrete longer-lived workflow benefits.

### Status history

| Date | Status | Record |
| --- | --- | --- |
| 2026-09-20 | proposed | Decision and implementation submitted in the PR #13 review candidate. |
| 2026-09-20 | accepted | Finn Newick: "I accept adr-0012". PR acceptance and integrated confirmation were still pending. |
| 2026-09-20 | implemented | Owner merged PR #13; exact integrated trees and canonical checks verified. |

## Pros and Cons of the Options

Explicit batches retain intent and provide coherent review at the cost of a
small draft/lifecycle model. Immediate writes are simpler per form but cannot
represent deliberate staged decisions. Durable actors add replay and framework
coupling without an established need and could obscure uncertain side effects.

## More Information

- [Review workspace and guidance](../development/research-interaction.md).
- [ADR-0011 (Preserve rule evidence across immutable revisions)](ADR-0011-preserve-rule-evidence-across-revisions.md).
- [ADR-0006 (Recover interrupted jobs under an exclusive process lock)](ADR-0006-recover-jobs-under-process-lock.md).
