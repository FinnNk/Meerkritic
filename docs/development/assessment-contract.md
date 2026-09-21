# Define an assessment before collecting judgements

An interpretation describes a concern raised by the supplied comment and code.
Accepting it does not establish that the original reviewer was correct or that a
proposed general rule is valid. Keep a reviewer's additional engineering advice
distinct from what the source establishes.

## Meanings to preserve

| Concept | Meaning | Where to record it |
| --- | --- | --- |
| Impact scope | The smallest affected code unit supported by the evidence, not the area a reviewer must search. | Interpretation `scope`; use `unknown` when the affected extent is not established. |
| Applicability limits | Known exceptions or conditions under which the proposed concern or rule does not apply. | Interpretation `exclusions`; an empty list means none identified, not proof there are none. |
| Evidence limitations | Facts the supplied material cannot establish. | Annotation notes, explicitly identified as evidence limitations. |
| Investigation needs | Further code, history or other context needed to assess the concern. | Annotation notes; a broad search does not imply broad impact. |
| Additional advice | A human's extension beyond the supplied evidence. | Annotation notes, attributed to the human rather than the original commenter. |

These meanings apply to model prompts, schemas, guides, UI explanations and agent
walkthroughs. The implementation decision is [ADR-0014](../adr/ADR-0014-clarify-assessment-field-meanings.md).
Until that implementation is available, pause an assessment that cannot be expressed
faithfully; do not force a known scope merely to satisfy validation.

Notes are retained alongside the annotation but are not interpretation text for
grouping. If uncertainty changes the concern's meaning, qualify the issue statement
and candidate rule too. Use `null` for a proposed invariant that the evidence cannot
justify; do not turn additional advice into a source-derived rule.

## Author and reviewer checks

When additional source context is available, follow
[ADR-0015](../adr/ADR-0015-separate-review-context-from-model-input.md): distinguish
the exact model input from preserved upstream material, retain its identity and
record what was presented with new judgements. Never silently rewrite source
strings, infer lost formatting or attribute new context to an earlier model run.

- Define the question each field answers, its allowed values and how uncertainty
  is represented before collecting judgements.
- Check an ordinary example and an ambiguous example. Distinguish the affected
  area from investigation needs, applicability exceptions from absent context,
  and faithful interpretation from endorsement of a reviewer's correctness.
- Compare model instructions, schema descriptions, UI labels and guidance. A
  rename must preserve meaning; otherwise record a contract decision.
- Test compatibility with stored outputs and grounded human edits. Preserve original
  bytes, execution outcomes, evidence spans and model/prompt provenance.
- If a walkthrough reveals ambiguity, pause saving, retain preliminary feedback
  and document the correction. Record assistance and prior exposure; do not call
  an agent-assisted judgement independent or blind.
- Apply clarified guidance prospectively. Do not silently relabel old annotations,
  rerun models or alter the sample to accommodate inconvenient outputs. Record
  study-method changes in the EDR before resuming affected collection.

This is a contract review, not an empirical claim that a particular label improves
accuracy. A comparative usability or judgement-quality claim would need its own
appropriate evidence.
