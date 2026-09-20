---
status: implemented
date: 2026-09-20
decision-makers:
  - Project owner
---

# ADR-0007: Review architecture and guidance after each milestone

## Context and Problem Statement

The VS1 review found contract and documentation gaps despite passing dependency
checks and prior design reviews. Existing principles covered most issues, but
review conclusions described intended abstractions without sufficiently checking
real consumers, invalid states and accumulated knowledge drift.

## Decision Drivers

- Assess the whole accumulated system before extending it.
- Make existing guidance actionable with proportionate evidence.
- Preserve semantic review and avoid duplicate evidence or procedural overhead.

## Considered Options

- Rely on per-change checks alone.
- Add a large set of mandatory automated style/design rules.
- Add milestone reviews and concrete contract challenges to existing checkpoints.

## Decision Outcome

Choose milestone reviews and contract challenges, as instructed by the owner on
20 September 2026. Follow the [milestone review guide](../development/milestone-review.md)
after each vertical slice or agreed milestone, covering all applicable guidance.
Record invariant ownership and caller obligations before significant abstractions;
check contracts and consumers at semantic checkpoints; reconcile interactions and
maintained knowledge at aggregate review. Findings precede fixes unless existing
owner authority covers the follow-up. This extends ADR-0003's caller-contract
policy and ADR-0004's selective style policy; neither is superseded.

### Consequences

- Reviews need concrete evidence and explicit limits, not only checkmarks.
- Existing canonical checks and independent skill files remain unchanged.
- No automatic finding quota, new infrastructure or EDR for ordinary review is required.

### Confirmation

The [VS1 milestone review](../slice-reviews/VS1-milestone-architecture-review.md)
applies the method across all guidance, records finding dispositions and architecture
effects, and distinguishes confirmed behaviour from limitations. Agent instructions,
build/PR guidance and both review templates agree. This confirms implementation
in the candidate; owner approval and integration of this PR remain separate.

## More Information

This is an owner-prescribed workflow decision, not an empirical result. The
milestone review complements DER and does not confer platform approval or merge
authority. Relevant decisions: [ADR-0003](ADR-0003-document-caller-contracts-and-intent.md)
and [ADR-0004](ADR-0004-adopt-selective-python-style.md).
