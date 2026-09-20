# Empirical Decision Records

An Empirical Decision Record (EDR) captures a significant choice whose outcome depends on evidence. Register the question and method before collecting or analysing the evidence that will decide it; then retain the results, interpretation and decision together.

Use one Markdown record per decision, copied from [the template](template.md) and named `NNNN-short-decision-name.md`. An EDR is a record, not a new application subsystem. Keep straightforward records short; expand the method only where the stakes or uncertainty justify it.

## When an EDR is needed

Use an EDR when both conditions hold:

1. The choice materially affects research validity, product behaviour, cost, performance or a durable design direction.
2. A plausible empirical result could change which option we choose.

Examples include selecting a normalisation method based on held-out quality, changing a routing default based on measured quality and cost, or replacing a component because measured operational friction remains unacceptable.

Do not require an EDR for incidental metrics, ordinary correctness tests, routine implementation choices, or implementing an architecture already prescribed by the project. Recording token counts does not itself need an EDR. Using those counts to justify a consequential policy change might. Existing programme hypotheses in the research documents are starting points, not pre-registered experiments.

## Lightweight process

1. **Frame.** State the choice, why evidence matters, the alternatives and a falsifiable hypothesis. Identify the smallest useful investigation. Record what is already known, including any pilot work or exposure to the proposed evaluation data.
2. **Register.** Complete the plan sections in the template before decision-bearing collection or analysis. Agree the comparator, sample, metrics, decision thresholds, stopping rule and method. Commit this filled plan on the working branch. Record that commit's full SHA as the registered plan reference in a subsequent update; the registration commit cannot contain its own SHA. Commit that reference, registration date and `registered` status before the first run. A Git commit retained locally or on the project remote is sufficient; no external registry is required.
3. **Run.** Execute the registered method. Record the code revision, exact commands and configuration, dependency versions, data identity and run artefacts. Keep the method reproducible where possible and state limits where it is not. Record failures and exclusions as well as successful runs.
4. **Analyse.** Report all planned primary results against the registered rule, including negative or inconclusive outcomes. Separate any exploratory analysis. State uncertainty and threats to validity proportionately.
5. **Decide.** Record the chosen action, who decided and why. An evidence outcome does not automatically constitute a product or architecture decision. Explain any departure from the registered decision rule; do not change the hypothesis to make the result look successful.
6. **Link.** Link the implementation batch and relevant slice review when they exist. A durable architectural decision belongs in an ADR, which may cite this EDR. Update the index and retain the record even if the decision is to make no change.

Do not impose statistical significance tests, power calculations or large benchmark grids on every investigation. Use them where the claim needs them. A small reproducible measurement can be sufficient for a bounded decision; a claim of generalisation needs stronger sampling and validation. Preserve the research plan's repository-level holdouts for headline generalisation results and its distinction between weak and verified negatives.

## Status and outcomes

The current status belongs in the record header and index. Append a dated entry whenever it changes.

| Status | Meaning |
| --- | --- |
| `draft` | The question or method is still being prepared. No registered evaluation has begun. |
| `registered` | A committed plan is identified and frozen before decision-bearing work. |
| `running` | Collection or analysis is under way against the registered plan. |
| `analysed` | Results and limitations are recorded; the decision remains open. |
| `decided` | An explicit decision and rationale are recorded. This does not imply implementation. |
| `withdrawn` | The investigation has stopped without a decision; retain the reason and any evidence. |
| `superseded` | A linked later EDR replaces this record; retain its history and results. |

The usual path is `draft → registered → running → analysed → decided`. A stopped investigation may become `withdrawn`; a replacement links both records. Record evidence outcomes separately as `supports`, `does not support` or `inconclusive`. Record implementation separately as `not planned`, `pending` or `implemented`, with a reference where applicable. Neither a successful experiment nor a decided EDR marks a vertical slice or DER review complete.

## Amendments and prior exposure

Once registered, leave the original plan sections unchanged. Append dated amendments stating the reason, affected plan clauses, evidence already seen and whether the change affects validity. For a prospective amendment, commit it and record its revision before the affected work. Use a new EDR for a materially different question or decision.

Unexpected implementation failures may require a method correction. Preserve the failed run, explain the correction and record whether outcomes were visible when it was made. Unplanned analyses and changes made after observing relevant results are exploratory; they cannot retrospectively become pre-registered. If new confirmatory evidence is needed, register its plan before collecting or examining it.

Existing datasets are allowed: registration must precede the decision-bearing analysis, not the original creation of the dataset. Disclose prior access, summaries, pilot results and any overlap. Separate pilot and evaluation material when needed. If the relevant results were already inspected, say so explicitly; record the evidence and decision honestly without claiming retrospective pre-registration.

## Evidence and independent reproduction

Keep a compact evidence inventory in each EDR. Include enough information for another person to repeat the method without relying on the author's memory:

- Exact code commit, commands, configuration, dependency lock/version information, relevant environment details and seeds.
- Dataset source, pinned revision, selection/query, identifiers or hashes, licence/access conditions, and preprocessing. Record evaluation units, splits, duplicate/contamination controls and adjudication where applicable.
- Identified run outputs, raw measurements and analysis outputs, with checksums or immutable references. Keep original run outputs; corrections produce new versions rather than overwriting evidence.
- An expected result or tolerance and a short reproduction procedure. For stochastic hosted models, also record provider/model/version where exposed, prompt and routing-policy revisions, request settings and timestamps. Exact output replay may be impossible; state what can be reproduced.

Small, shareable methods and result summaries may be committed. Large or private datasets, credentials and raw artefacts stay outside Git at configured storage locations, normally under `extras`. Use a durable public location for shareable evidence where available. A local path alone is a recording location, not an independent reproduction package. Record access restrictions and the reason reproduction or sharing is difficult, together with the closest feasible substitute, such as permitted aggregates, hashes, synthetic examples or an executable method. Do not claim independent reproduction until it has actually been checked.

EDRs own empirical plans, results and decision rationale. ADRs own architectural decisions. DER owns review chronology and review evidence outside application worktrees. Link to these records rather than duplicating their evidence stores.

## Index

No EDRs have been registered. Create the first record when a qualifying empirical decision is proposed; bootstrapping these documents is not itself an empirical investigation.

| EDR | Decision | Status | Evidence outcome | Related ADR |
| --- | --- | --- | --- | --- |

- [EDR-0001: discovery grouping method](0001-discovery-grouping-method.md) — draft; no registered study or adoption decision.
