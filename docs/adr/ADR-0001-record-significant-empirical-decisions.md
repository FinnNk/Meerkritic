---
status: accepted
date: 2026-09-19
decision-makers:
  - Project owner
---

# ADR-0001: Record significant empirical decisions

## Context and Problem Statement

Meerkritic will make choices whose justification depends on observed data, such
as evaluation outcomes, model behaviour and performance measurements. Those
choices need a record that distinguishes a hypothesis from a finding and makes
the methods, data and reasoning available for independent scrutiny.

The project owner has instructed us to use a lightweight, hypothesis-driven
process for significant decisions where data genuinely drives the choice. This
requirement does not extend to cases where data is incidental. This ADR records
that instructed process decision; it does not claim experimental validation of
the process or acceptance of any software implementation.

## Decision Drivers

- Make consequential empirical choices traceable to stated hypotheses and results.
- State the intended method and decision criteria before evaluating the evidence.
- Enable sharing and independent reproduction where possible, while recording
  access restrictions and reproduction limits where necessary.
- Keep ordinary engineering work and prescribed project requirements lightweight.
- Keep empirical evidence distinct from durable architectural rationale.

## Considered Options

- Continue with informal notes and general project documentation.
- Require an empirical record whenever a decision involves any data.
- Require a pre-registered empirical decision record only for significant choices
  whose outcome is materially determined by evidence.

## Decision Outcome

Choose targeted, pre-registered empirical decision records (EDRs), as instructed
by the project owner. Maintain the process, template and index in `docs/edr/`.
Before evaluating decision evidence, record the question, testable hypothesis,
method, relevant data and the criteria for interpreting the result. Commit the
registration before the decision experiment or confirmatory analysis begins.
Record prior exposure or exploratory analysis honestly; never describe it as
unseen evidence or backdate a registration.

Record the resulting observations, uncertainty, deviations and decision in the
same EDR. Preserve the registered plan and identify subsequent amendments so
readers can distinguish the original plan from later changes. Include enough
provenance and instructions to reproduce the work independently when feasible;
otherwise explain the limitation and retain the best available record. Keep
large or private data outside source control.

Routine choices, decisions already prescribed by the specification or owner,
and decisions for which data is merely incidental do not need EDRs. An EDR is
not automatically an ADR. Where empirical results lead to a material durable
architecture decision, an ADR cites the EDR and explains the architectural
consequences without becoming another evidence store.

### Consequences

- A reader can separate the planned question and decision criteria from results
  and later judgement.
- Significant empirical choices gain a discoverable status and an evidence trail.
- Experiment authors undertake a small amount of planning and provenance work
  before collecting or analysing the deciding evidence.
- Reproducibility is bounded by data access, provider availability and other
  practical constraints; those limits must be explicit rather than hidden.
- The team must apply the significance threshold with judgement to avoid turning
  every measurement or routine change into a formal study.

### Confirmation

During documentation review, check that the EDR guide, template and index agree
on applicability, pre-registration, statuses, deviations and reproduction
information. Check that the ADR index and this record have matching metadata.
These are document-consistency checks; their completion is recorded with the
bootstrap change's validation evidence, not represented here as experimental
results.

For the first applicable empirical decision, confirm that a committed plan
precedes the deciding experiment or analysis and that the completed EDR links
methods, data provenance, results and the decision. Revisit this process if
actual use reveals disproportionate overhead or insufficient reproducibility.
No such empirical decision has been completed by this ADR.

Status reviewed on 2026-09-19: the process documentation is present, but the
first-use confirmation above remains outstanding. Retain `accepted` until that
confirmation is recorded; incidental integration measurements and ordinary tests
do not constitute an empirical decision under this process.

## Pros and Cons of the Options

### Informal notes

- Requires little process overhead.
- Does not reliably separate prior intent from explanations written after seeing
  a result, and makes independent reproduction harder.

### Records for every decision involving data

- Provides broad coverage with a simple trigger.
- Creates unnecessary work for incidental measurements and routine engineering,
  contrary to the owner's requested scope.

### Targeted pre-registered EDRs

- Concentrates planning and evidence capture on decisions where they matter.
- Supports transparent results, revisions and reproducibility without requiring
  an ADR for each experiment.
- Requires a reasoned applicability judgement and honest recording of prior
  exposure and practical limits.

## More Information

- [Empirical decision records: process and index](../edr/README.md).
- [ADR process and index](README.md).
- This decision comes from the project owner's instruction on 2026-09-19.
  It is a prescribed process requirement, so no EDR was required to adopt it.
- `accepted` records that instructed intent. It does not mean the owner has
  approved the bootstrap PR, that the process has been tested in practice, or
  that VS1 has been implemented.
