---
status: accepted
date: 2026-09-20
decision-makers: [Finn Newick]
---

# ADR-0013: Preserve failed drafts during human correction

## Context and Problem Statement

A model can return an interpretation whose schema or quoted evidence fails
validation. The original output is useful to a human reviewer, but the existing
annotation path requires a successful job. Changing that job to successful after
a human correction would confuse model performance with human judgement.

## Decision Drivers

- Keep original execution outcomes and human decisions independently inspectable.
- Reuse the existing immutable annotations, edit artefacts and atomic event writes.
- Apply the same schema and source-grounding checks to every human correction.
- Keep failed or rejected records visible without inventing valid interpretations.

## Considered Options

- Store a separate human annotation while retaining the failed job unchanged.
- Replace the failed result and mark the job successful.
- Introduce a separate repair queue and evidence store.

## Decision Outcome

Use the existing annotation path for **Edit or Reject** of a retained semantic
failure. Accept remains available only for successful interpretations. Early,
provider and interrupted failures without a reviewable model draft remain failures
for inspection. The owner authorised this behaviour on 20 September 2026.

The annotation service owns admissible actions and validation. Selection freezing
rechecks that contract and the corrected artefact's provenance. A rejected failed
draft may remain in a selection as an explicit exclusion with no interpretation;
new snapshots version this representation and old snapshots remain readable.

### Consequences

- Model success/failure counts stay truthful after human correction.
- Human edits remain traceable to exact original bytes and source quotes.
- UI and selection readers must distinguish absent rejected interpretations from
  eligible data. No model rerun, automatic correction or authenticated identity is added.
- Research suitability still requires human judgement and the agreed EDR procedure.

### Confirmation

Before marking this implemented, verify unchanged failed job/result bytes, valid
and invalid corrections, rejection, duplicate/conflicting submissions, atomic
events, restart, selection freezing and legacy snapshot reading. Exercise the
browser with synthetic data, including a retained invalid edit. Keep the live
study free of agent-generated annotations. Evidence belongs to DER
`vs2-draft-repair/r1`; confirmation is pending at this accepted decision commit.

## Pros and Cons of the Options

Separate annotations reuse established persistence and preserve chronology, with
some extra eligibility and display rules. Replacing a result would simplify the
screen but destroy execution provenance. A separate repair queue duplicates state
and adds coordination without a distinct workflow owner.

## More Information

- [ADR-0009: explicit annotation selections](ADR-0009-freeze-explicit-annotation-selections.md).
- [EDR-0001: grouping method](../edr/0001-discovery-grouping-method.md) owns the
  prospective preparation amendment and later comparison. The architectural choice
  above is a provenance requirement, not an empirical claim that correction works.
