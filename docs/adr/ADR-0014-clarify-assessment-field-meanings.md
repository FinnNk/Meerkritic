---
status: accepted
date: 2026-09-20
decision-makers: [Finn Newick]
---

# ADR-0014: Distinguish impact, applicability and evidence limits in assessments

## Context and Problem Statement

The first real input walkthrough exposed ambiguous assessment fields before a
decision was saved. The agent described scope as the area needed for investigation
and exclusions as missing evidence. The existing guide instead defined exclusions
as applicability conditions; the schema listed scope values without explanations
or an unknown value. Agreeing with those explanations could produce inconsistent
research labels. The owner agreed to pause and clarify before saving.

## Decision Drivers

- Preserve the meaning and provenance of human judgements.
- Express insufficient evidence without guessing.
- Make the same contract accessible to researchers, models and coding agents.
- Retain the fixed initial model pass and existing annotations unchanged.

## Considered Options

- Clarify the existing interpretation contract and use annotation notes for limits.
- Rename exclusions to evidence limitations and reuse its stored values.
- Introduce new structured annotation fields for every distinction.

## Decision Outcome

Use the [assessment contract](../development/assessment-contract.md). Scope means
the smallest affected code unit established by the source, with `unknown` available
when needed. Investigation extent belongs in notes. Keep `exclusions` as known
applicability exceptions, displayed as **Applicability limits**. Record missing
evidence and human extensions separately in existing annotation notes.

Add descriptions to the existing domain schema and version future model prompts.
Preserve all prior model outputs, successful/failed status and source bytes. Old
scope values remain valid. Human corrections use the current compatible schema
and unchanged exact-quote checks. Do not rerun the study's frozen initial pass.

### Consequences

- No SQLite migration, new state owner or parallel interpretation type is needed.
- Notes retain qualifications without representing them as model evidence or
  silently feeding them into grouping. Meaning-changing uncertainty must also
  qualify the issue/invariant.
- Historical drafts may misuse the old labels. Explain that they are original
  model claims requiring assessment; do not relabel their content as corrected.
- The first walkthrough is assisted preparation with prior exposure, not an
  independent or blind rating. Usability improvements are design judgements,
  not demonstrated increases in annotation accuracy.

### Confirmation

Before marking implemented: verify old and unknown scopes, exact grounding and
immutable result preservation; inspect the synthetic review UI and affected guides;
retain the paused assessment and verify that the live study has not been changed.
Record candidate revision and evidence in the confirmation update.

## Pros and Cons of the Options

| Option | Benefit | Cost or reason not chosen |
| --- | --- | --- |
| Clarify and reuse notes | Preserves existing meanings and storage; limited contract change | Notes need clear attribution and do not feed grouping |
| Repurpose exclusions | Shorter apparent change | Silently changes meaning of historical data |
| Add many structured fields | More machine-readable distinctions | Introduces schema and interaction complexity before a consumer requires it |

## More Information

- [EDR-0001](../edr/0001-discovery-grouping-method.md): prospective preparation clarification; no grouping results.
- [ADR-0013](ADR-0013-preserve-failed-drafts-during-human-correction.md): original draft and correction remain separate.
- Discovery source: the owner's first input walkthrough and inspection of the
  existing schema, prompt and guide. This contract correction follows an identified
  contradiction; it is not selection of a method based on comparative results.
