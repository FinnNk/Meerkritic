# Milestone review: <name>

- Integrated revision/tree and relevant baseline:
- Scope, authority and applicable guidance:
- Evidence inspected, checks run and limitations:
- Review provenance: self-review / independently evidenced review:

## Guidance assessment

For each area in the milestone-review guide: conclusion, concrete source/evidence,
and applicability or remaining uncertainty. Cover scope/architecture; complexity;
states/failures; interfaces/comments; runtime/routing; data/privacy/provenance;
human interaction/research; quality/architecture observability; delivery/knowledge.

## Findings and dispositions

| ID | Kind/priority | Obligation and observed evidence | Consequence and remedy | Disposition/validation |
| --- | --- | --- | --- | --- |

Include invariant owners, caller obligations and meaningful contract challenges.
Distinguish confirmed defects from hypotheses. Accepted/deferred concerns name the
reason, owner and revisit trigger. Do not require a minimum number of findings.

### <Finding ID>: <short title>

Repeat for each actual finding; record explicitly if there were none.

- **Observed issue and consequence:** revision, concrete example and violated
  principle/contract; defect, design concern or evidence gap.
- **How found:** actual inspection comparison, question or probe and references.
  Separate initial discovery from later regression/confirmation work.
- **Resolution:** what changed, where the invariant now lives, implementation and
  validation references; otherwise accepted/deferred rationale and revisit trigger.
- **Generalised pattern:** what similar failures could look like elsewhere.
- **Before the next milestone review:** applicable design/build/semantic/aggregate
  checkpoint, author/reviewer responsibility, concrete detection question or
  challenge, expected evidence and action when it fails.
- **Limits and follow-up:** residual uncertainty and whether prevention is only
  intended or has been observed in later changes; record recurrences honestly.

Keep original IDs stable. Label additional follow-up improvements separately.
Do not replace this trace with a list of fixes or a claim that checks passed.

## Architecture and decisions

- Before/after/delta references and intentional changes:
- Complexity introduced/removed, module depth and knowledge leakage:
- Layer quality, state/error design and caller-contract completeness:
- Special cases/configuration and higher-leverage simplifications:
- Glossary, ADR/EDR, status and maintained documentation reconciliation:
- Reader-facing documentation: audience, terminology, structured instructions,
  current behaviour, navigation, examples/recovery and PR-description clarity:
- Required changes to the next milestone and unresolved gates:
