---
status: implemented
date: 2026-09-20
decision-makers: [Project owner]
---

# ADR-0009: Freeze explicit annotation selections before discovery

## Context and Problem Statement

VS2 needs reproducible inputs without changing VS1 terminal decisions. Several
model runs can exist for one source; edits replace interpretation content while
preserving original provenance. VS1 does not record an authenticated human actor,
and earlier functional tests created decisions which are not research labels.

## Decision Drivers

- Trace exact source, annotation, original result and effective edited body.
- Preserve uncertainty and keep rejected interpretations distinct from negatives.
- Keep provenance validation and atomic publication away from UI/CLI callers.
- Retain a simple local architecture and avoid inventing retrospective human labels.

## Considered Options

- Immutable explicit selections with a separate research-purpose attestation.
- Query the latest accepted/edited results whenever a discovery job runs.
- Infer human provenance from annotation notes or retrospectively label every decision.

## Decision Outcome

Freeze bounded explicit versions and policy in content-addressed filesystem
snapshots, with only summary metadata and an atomic event in SQLite. The selection
service owns input resolution/eligibility; its store owns publication/idempotence.
Each source appears at most once; repeated upstream comment IDs remain distinct
source records under [ADR-0002](ADR-0002-preserve-source-record-identity.md).

Record explicit holdout repositories and exclusions. Research use requires a named
curator's human-review attestation; fixture purpose cannot carry it. This records a
claim, not authentication or proof. The EDR still owns sampling and validity.
This extends prescribed VS2 provenance requirements by engineering judgement;
ordinary integrity tests do not need an empirical decision record.

### Consequences

Selections survive later decisions and can be inspected independently of moving
queries. Bodies duplicate bounded source/interpretation data outside SQLite; full
provenance reproduction still needs the referenced original artefacts. The curator
must make an honest explicit claim. No software rule can infer human review from
the old records, and the design deliberately makes that limitation visible.

### Confirmation

The owner approved and merged PR #10 on 20 September 2026. Main
`c9ef38f48b10d7876fe26babee36f2f15f258bf3` has the reviewed head's exact tracked
tree; integrated canonical checks and 115 tests pass. The author
checks effective edits, exclusions, retained uncertainty, duplicate rejection,
corrupt/missing evidence, concurrent retries, failed-event rollback and restart in
`tests/test_selections.py`, with final canonical evidence in DER `vs2-inputs/r3`.
Review exact results with the PR. Revisit on authenticated multi-user requirements,
a demonstrated corpus-size limit or richer version-selection needs; do not silently
upgrade fixture records to human evidence.

## Pros and Cons of the Options

Explicit snapshots add a freeze step and bounded duplicate bodies, but make the
input identity and claim inspectable. A latest-result query is shorter but changes
the corpus when new decisions arrive. Inferring provenance from notes is convenient
but unreliable; it could silently include automated decisions in research.

## More Information

- [VS2 plan](../plans/VS2-plan.md), A1.
- [EDR-0001: grouping method](../edr/0001-discovery-grouping-method.md), draft;
  no empirical comparison or adoption decision has occurred in this batch.
