# Architecture decision records

Record a decision when it materially constrains future architecture or when its
reasoning is significant and would not be evident from the implementation. Do
not create ADRs for routine edits, dependency maintenance or every implementation
choice. One decision has one ADR; evolve that record when the same decision is
refined, and create a linked successor when a different decision replaces it.

## Create or update a record

1. Copy the [MADR template](template.md) to `ADR-NNNN-kebab-title.md`, using the next number.
2. Name the actual decision-makers. Distinguish their decision from an agent's
   proposal or implementation; record consultation only when it occurred.
3. Keep the index in step with each status change. The date is the latest status-change date.
4. Include a linked identifier and short title for related records; retain history.

## Statuses

| Status | Meaning |
| --- | --- |
| `proposed` | Draft awaiting a decision. |
| `accepted` | Intended decision agreed by the named decision-makers; implementation and merge are separate. |
| `implemented` | The accepted decision has been put into effect and its stated confirmation has passed. |
| `rejected` | Considered and declined, with the reason retained. |
| `deprecated` | Still present, but discouraged; record migration or review conditions. |
| `superseded by ADR-NNNN` | Replaced by a linked ADR, preserving the earlier record. |
| `retired by ADR-NNNN` | Removed by a linked ADR without a replacement implementation. |

Include a link and short title whenever referencing another ADR, including a
successor or retirement record. Do not silently delete a historical decision.

## Lifecycle review

Review affected ADRs during each implementation batch and at slice completion.
Advance an accepted decision to `implemented` once its application and stated
confirmation are complete; record the evidence and update the date and index in
the same change. A decision implemented in a candidate branch may be recorded as
such before merge: identify that scope without claiming owner approval of the PR.

Code presence does not accept a proposed decision. If acceptance or confirmation
is outstanding, retain the appropriate status and state what remains. Do not
silently narrow confirmation criteria to advance a status. When implementation
changes an accepted decision, revisit its rationale and use a linked successor
if it is a different decision. Check post-merge status against what actually landed.

## Relationship to empirical decisions

An [empirical decision record](../edr/README.md) owns the pre-registered question,
hypothesis, methods, results and resulting empirical decision. An ADR records
durable architectural rationale and consequences. An ADR may cite one or more
EDRs using their identifiers and short titles, without duplicating their evidence.
Explain which claims are observations and which are judgement or constraints.
An EDR is not required merely because incidental data accompanies a decision.

## Format and attribution

The active format is the project's [MADR template](template.md), adopted on
2026-09-19. It follows the [MADR template at revision
ba75bb1b20d42af5746b246ad348c202419ae681](https://github.com/adr/madr/blob/ba75bb1b20d42af5746b246ad348c202419ae681/template/adr-template.md).
MADR is available under `MIT OR CC0-1.0`; this adaptation uses CC0-1.0.

## Index

Newest first. Status here describes the decision, not the PR or vertical slice.

| Record | Title | Status | Decision-makers | Date |
| --- | --- | --- | --- | --- |
| [ADR-0016](ADR-0016-use-local-codegraph-for-navigation.md) | Use a local CodeGraph index for code navigation | accepted | Finn Newick | 2026-09-22 |
| [ADR-0015](ADR-0015-separate-review-context-from-model-input.md) | Separate preserved review context from model input | implemented | Finn Newick | 2026-09-21 |
| [ADR-0014](ADR-0014-clarify-assessment-field-meanings.md) | Distinguish impact, applicability and evidence limits in assessments | implemented | Finn Newick | 2026-09-20 |
| [ADR-0013](ADR-0013-preserve-failed-drafts-during-human-correction.md) | Preserve failed drafts during human correction | implemented | Finn Newick | 2026-09-20 |
| [ADR-0012](ADR-0012-apply-review-intent-in-explicit-batches.md) | Apply review intent in explicit batches | implemented | Project owner | 2026-09-20 |
| [ADR-0011](ADR-0011-preserve-rule-evidence-across-revisions.md) | Preserve rule evidence across immutable revisions | implemented | Project owner | 2026-09-20 |
| [ADR-0010](ADR-0010-own-discovery-runs-under-one-worker.md) | Own immutable discovery runs under the shared worker | implemented | Project owner | 2026-09-20 |
| [ADR-0009](ADR-0009-freeze-explicit-annotation-selections.md) | Freeze explicit annotation selections before discovery | implemented | Project owner | 2026-09-20 |
| [ADR-0008](ADR-0008-own-artefact-publication-metadata.md) | Make artefact publication metadata explicit | implemented | Project owner | 2026-09-20 |
| [ADR-0007](ADR-0007-review-architecture-after-milestones.md) | Review architecture and guidance after each milestone | implemented | Project owner | 2026-09-20 |
| [ADR-0006](ADR-0006-recover-jobs-under-process-lock.md) | Recover interrupted jobs under an exclusive process lock | implemented | Project owner | 2026-09-20 |
| [ADR-0005](ADR-0005-retain-immutable-routing-provenance.md) | Retain immutable routing versions and invocation records | implemented | Project owner | 2026-09-19 |
| [ADR-0004](ADR-0004-adopt-selective-python-style.md) | Adopt a selective Python style guide | implemented | Project owner | 2026-09-19 |
| [ADR-0003](ADR-0003-document-caller-contracts-and-intent.md) | Document caller contracts and non-obvious intent | implemented | Project owner | 2026-09-19 |
| [ADR-0002](ADR-0002-preserve-source-record-identity.md) | Preserve source records before interpretation | implemented | Project owner | 2026-09-19 |
| [ADR-0001](ADR-0001-record-significant-empirical-decisions.md) | Record significant empirical decisions | accepted | Project owner | 2026-09-19 |
