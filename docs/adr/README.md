# Architecture decision records

The active format is the project's [MADR template](template.md), adopted on
2026-09-19. It follows the [MADR template at revision
ba75bb1b20d42af5746b246ad348c202419ae681](https://github.com/adr/madr/blob/ba75bb1b20d42af5746b246ad348c202419ae681/template/adr-template.md).
MADR is available under `MIT OR CC0-1.0`; this adaptation uses CC0-1.0.

Record a decision when it materially constrains future architecture or when its
reasoning is significant and would not be evident from the implementation. Do
not create ADRs for routine edits, dependency maintenance or every implementation
choice. One decision has one ADR; evolve that record when the same decision is
refined, and create a linked successor when a different decision replaces it.

Use sequential filenames `ADR-NNNN-kebab-title.md`. Copy the template and keep the
index below in step with each status change. The date records the latest status
change. Name the actual decision-makers; distinguish their decision from an
agent's proposal or implementation. Record consultation only when it occurred.

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

## Index

Newest first. Status here describes the decision, not the PR or vertical slice.

| Record | Title | Status | Decision-makers | Date |
| --- | --- | --- | --- | --- |
| [ADR-0004](ADR-0004-adopt-selective-python-style.md) | Adopt a selective Python style guide | implemented | Project owner | 2026-09-19 |
| [ADR-0003](ADR-0003-document-caller-contracts-and-intent.md) | Document caller contracts and non-obvious intent | implemented | Project owner | 2026-09-19 |
| [ADR-0002](ADR-0002-preserve-source-record-identity.md) | Preserve source records before interpretation | implemented | Project owner | 2026-09-19 |
| [ADR-0001](ADR-0001-record-significant-empirical-decisions.md) | Record significant empirical decisions | accepted | Project owner | 2026-09-19 |
