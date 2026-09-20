# Record an evidence-dependent decision

An Empirical Decision Record (EDR) keeps a significant question, hypothesis, method,
results and decision together. Commit the plan before collecting or analysing the
evidence that will decide the choice. This is *pre-registration*.

Use one Markdown file per decision, copied from [the template](template.md) and
named `NNNN-short-decision-name.md`. Keep it proportionate to the question.

## Decide whether an EDR is needed

Both conditions must hold:

1. The choice materially affects research validity, product behaviour, cost,
   performance or a lasting design direction.
2. A plausible result could change which option you choose.

| Example | EDR needed? |
| --- | --- |
| Record token counts during a run | No; this is incidental telemetry. |
| Change a routing default based on measured quality and cost | Yes. |
| Run ordinary correctness tests or implement a prescribed architecture | No. |
| Select an interpretation/grouping method based on evaluation results | Yes. |
| Replace a component because measured operational problems remain unacceptable | Yes. |

Research-pack hypotheses are starting points, not already registered experiments.

## Follow the process

| Step | Action | Record |
| --- | --- | --- |
| Frame | Identify the choice, alternatives, testable prediction and smallest useful investigation. | Prior knowledge, pilot work and data already seen |
| Register | Agree the comparison, sample, measures, thresholds, stopping rule and method. Commit the plan before decision-bearing work. | Exact registered-plan reference, as described below |
| Run | Execute the registered method. | Code, commands, configuration, environment, data identities, failures and exclusions |
| Analyse | Report all planned primary results, including negative or inconclusive outcomes. | Uncertainty, limits and separately labelled exploratory analysis |
| Decide | Record the chosen action, decision-maker and rationale. | Any departure from the registered decision rule |
| Link | Connect the implementation and relevant reviews; use an ADR for a lasting architecture decision. | Updated index and retained history, even if no change is chosen |

To register the plan:

1. Fill and commit the template's plan sections before decision-bearing collection or analysis.
2. Copy that commit's full SHA into the record's registered-plan field. A commit
   cannot contain its own SHA.
3. Commit the reference, registration date and `registered` status **before the first run**.
   A retained local or project-remote commit is sufficient; no external registry is required.

Use statistical significance tests, power calculations or large comparisons when
the claim needs them, not for every investigation. A bounded decision may need only
a small reproducible measurement. Generalisation claims require stronger sampling
and validation, including prescribed repository holdouts and careful negative labels.

## Status and outcome

Update the header and index together, and append a dated history entry.

| Status | Meaning |
| --- | --- |
| `draft` | Question/method still being prepared; no registered evaluation has begun |
| `registered` | Committed plan identified before decision-bearing work |
| `running` | Collection or analysis under way against that plan |
| `analysed` | Results and limitations recorded; decision still open |
| `decided` | Explicit decision and rationale recorded; implementation is separate |
| `withdrawn` | Stopped without a decision; retain reasons and evidence |
| `superseded` | Replaced by a linked later record; retain history/results |

The usual order is draft, registered, running, analysed, decided. Record these
separately from status:

- Evidence outcome: `supports`, `does not support` or `inconclusive`.
- Implementation: `not planned`, `pending` or `implemented`, with a reference.

A successful experiment or decided EDR does not itself complete a milestone or
Double-Entry Review (DER) review.

## Amend a plan honestly

- Leave registered plan sections unchanged. Append a dated amendment naming the
  affected clauses, reason, evidence already seen and implications for validity.
- For a prospective change, commit and identify the amendment before affected work.
- Preserve failed runs when correcting an implementation/method error; record whether
  outcomes were visible before the correction.
- Label unplanned analysis or changes made after seeing relevant results as exploratory.
  They cannot become retrospectively pre-registered.
- Register new confirmatory work before collecting or examining its evidence.
  Use a new EDR for a materially different question.

Existing datasets are allowed: registration precedes the deciding analysis, not
necessarily dataset creation. Disclose earlier access, summaries, pilots and overlap.
If results were already inspected, record that honestly instead of claiming registration.

## Make the work reproducible

Keep a compact evidence inventory with enough information for another person:

| Item | Include |
| --- | --- |
| Code/environment | Exact commit, commands, configuration, lock/versions, relevant platform and seeds |
| Data | Source/revision, selection/query, identities or hashes, access/licence and preprocessing |
| Design | Evaluation units, splits, duplicates, related-source contamination controls and label review where relevant |
| Results | Original measurements/outputs, analysis and immutable references/checksums |
| Reproduction | Procedure, expected result or tolerance and explicit limits |
| Variable model services | Exposed model/provider version, prompt/routing revision, settings and timestamps |

Commit small shareable methods and summaries. Keep large/private datasets, credentials
and raw artefacts outside Git. Use durable public evidence locations where possible;
a local path alone is not an independently reproducible package. When sharing is
restricted, record why and provide the closest permitted substitute, such as hashes,
aggregates, synthetic examples or an executable method. Claim independent reproduction
only after it has actually occurred.

EDRs own empirical plans/results/decisions. [ADRs](../adr/README.md) own architectural
rationale. DER owns review chronology/evidence outside worktrees. Link their records
rather than duplicating evidence stores.

## Index

No EDR is registered yet. The owner agreed EDR-0001's proposed workload and criteria
on 20 September 2026; qualified inputs and runnable, pinned methods remain prerequisites.
The current draft is:

| EDR | Decision | Status | Evidence outcome |
| --- | --- | --- | --- |
| [EDR-0001](0001-discovery-grouping-method.md) | Choose an initial discovery grouping method | draft | pending |
