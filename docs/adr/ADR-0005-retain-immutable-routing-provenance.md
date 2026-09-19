---
status: implemented
date: 2026-09-19
decision-makers:
  - Project owner
---

# ADR-0005: Retain immutable routing versions and invocation records

## Context and Problem Statement

Normalisation must retain each invocation's inventory and policy, and historical spend must not change when prices change. The existing event table only permits dataset subjects. A future worker must not execute a model before its routing provenance has been committed.

## Decision Drivers

- Preserve historical provenance and reject reused configuration identities.
- Keep operational writes short and atomic in SQLite WAL mode.
- Preserve existing events and keep large data outside SQLite.
- Allow later policy transitions and handoff references without rewriting decisions.

## Considered Options

- Immutable version snapshots and invocation records, with shared append-only events.
- References to mutable configuration files, which cannot reproduce historical routes.
- Separate routing events, which fragment the operational history.

## Decision Outcome

Retain inventory, policy and price snapshots by kind/ID/version. Persist a selected or refused decision and its event atomically, before execution. Retain one immutable completion per invocation; identical retries return the original completion and conflicts fail. Changed configuration needs a new version. SQLite contains small metadata, never prompt or dataset bodies.

Extend event subjects beyond datasets. The migration preserves existing sequences and content, with triggers for known event-subject relationships and append-only behaviour. A shared SQLite adapter owns connection/migration policy for the dataset and routing repositories. The owner accepted this decision by approving and merging [PR #5](https://github.com/FinnNk/Meerkritic/pull/5).

### Consequences

- Provenance survives configuration edits and restarts.
- New event kinds must define subject integrity rules; this is not event sourcing.
- Corrections and transitions require new records, not in-place edits.
- Configuration growth into large artefacts would require filesystem references.

### Confirmation

Journal tests check migration preservation, referential triggers, atomic rollback, immutable records, conflicting retries, restarts and concurrent completion. All 43 canonical tests passed on integrated main `f1478217d43414da6e55599a5bf390c7f957dadb`. All four integrated proposition trees match the reviewed series. Exact checkpoint and integration evidence lives in DER pair `vs1-routing`, round `r1`; its integration record confirms owner acceptance and implementation separately.

## More Information

The routing specification prescribes versioned provenance and SQLite state. This record explains retention enforcement and event subjects. No comparative data-driven choice is made, so an EDR is not required. Existing ADR-0001 remains accepted pending its first applicable empirical decision; ADRs 0002–0004 remain implemented.
