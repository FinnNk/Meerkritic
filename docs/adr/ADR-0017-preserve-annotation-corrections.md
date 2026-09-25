---
status: implemented
date: 2026-09-25
decision-makers: [Project owner]
---

# ADR-0017: Preserve saved assessments when recording corrections

## Context and Problem Statement

Two labelling walkthroughs ended with the original model values saved from another
tab instead of the approved edits. The owner authorised reconciliation on
25 September. Saved annotations are immutable, and study selections identify exact
annotation versions. Directly repairing existing rows would destroy that history.

## Decision Drivers

- Recover the approved judgements without rerunning a model or inventing new labels.
- Preserve original decisions, model outputs, source context and frozen selections.
- Make correction provenance and competing submissions explicit.

## Considered Options

- Append linked correction versions through the annotation service.
- Modify the original rows after taking a backup.
- Apply study-only override files during selection.

## Decision Outcome

Use append-only corrections. The owner's authorisation covers restoring the two
approved judgements while preserving history; the storage layout is an implementation
choice. A correction names the current predecessor, a complete approved Edit and
notes, a reason and curator. Schema, source grounding and context checks remain
shared with initial decisions. Store the replacement and its event atomically.

Keep original annotation rows unchanged. A correction table and read views expose
all versions and one current version per result. Resolve exact IDs across both
tables. Progress counts current decisions; frozen selections continue using explicit
IDs under [ADR-0009: Explicit selections](ADR-0009-freeze-explicit-annotation-selections.md).
Identical retries return the same replacement; competing changes are rejected.

### Consequences

- The harness and future selections can use the approved correction without
  silently rewriting prior evidence.
- Operators must retain human approval and old/new IDs. A curator string is not
  authentication. Agent transcription remains agent-assisted evidence.
- There are two storage tables but one annotation interface. Corrections initially
  use a command-line repair path; source forms still cannot overwrite a save.
- Existing selections do not automatically gain later corrections. Any replacement
  study selection must be explicit and recorded.

### Confirmation

Candidate implementation confirmed on 25 September. Six focused integrity tests
cover preserved originals and frozen selections, single-result progress, concurrent
and conflicting retries, stale forms, immutable rows, rollback, source/result
provenance and the operator command. The isolated diary's canonical checks passed
all 259 tests. A rehearsal of both approved corrections on a copied runtime matched
all fields, notes and grounded quotes while preserving the original application
records and all 366 existing files. Evidence is retained outside Git in
`extras/review-evidence/annotation-corrections/r1` and the study reconciliation log.
This confirms the candidate behaviour, not PR acceptance or integration. Revisit
if corrections require new source context, different decision types or multi-user
authorisation.

## Pros and Cons of the Options

Append-only versions add a small amount of storage/read logic but preserve auditability.
Updating rows is simpler only for the write; it invalidates immutable identifiers and
old decisions. Sidecar overrides preserve files but create a second interpretation
source outside normal selection validation and the harness.

## More Information

This is a recovery and integrity decision, not a data-driven claim about annotation
quality. The study records the incidents and assistance as method limitations; its
workload and decision criteria are unchanged.
