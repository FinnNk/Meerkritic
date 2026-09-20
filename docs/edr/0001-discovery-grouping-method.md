# EDR-0001: Choose an initial discovery grouping method

- Status: draft
- Created: 2026-09-20
- Owner: Project owner
- Decision-maker(s): Project owner
- Registered on: pending
- Registered plan: pending; this draft is not a frozen registration
- Evidence outcome: pending
- Implementation: not planned until a recorded adoption decision
- Related records: [VS2 plan](../plans/VS2-plan.md), [VS1 review](../slice-reviews/VS1-review.md), [ADR-0001](../adr/ADR-0001-record-significant-empirical-decisions.md)

## Registered plan

This section is a prospective draft. Registration is blocked on the concrete
candidate's operational preflight, a permitted human-labelled sample and agreement
on the bounded comparison. Do not collect or analyse decision-bearing results
until these details and the registration commit are recorded. No selection decision
has been made from the functional VS1 data.

### Decision and hypothesis

- **Choice and significance:** decide whether a candidate local embedding/grouping
  method merits becoming the initial discovery default. This changes the examples
  a researcher sees together and therefore which rules are likely to be proposed.
- **Options and comparator:** one embedding-based candidate versus a simple lexical
  grouping baseline over the same reviewed interpretation text. Freeze exact
  model/revision/digest, algorithm/version, preprocessing and parameters after
  synthetic compatibility preflight and before registration. No broad benchmark grid.
- **Hypothesis:** on the bounded development-research corpus, the candidate improves
  human-rated grouping coherence without an unacceptable loss of coverage or
  local execution reliability. This is not a repository-generalisation claim.
- **Prior knowledge and exposure:** the public CRC sample was browsed in VS1 and
  records 0 and 2 were used during live compatibility work. Model interpretations,
  source text and unsupported extrapolations were observed. The three final VS1
  functional annotations are automated test decisions, not eligible human labels.
  Exclude exposed pilot records and disclose repository overlap before registration.

### Data and design

- **Unit and target population:** a pair/group of explicitly human-reviewed
  engineering concerns within a fixed development corpus; repository is the
  dependence/holdout unit for any later headline claim.
- **Sample and selection:** provisionally 30–60 eligible accepted/edited observations,
  selected by a seeded, versioned query before method outputs are inspected. Exact
  count, IDs, source revision/hashes and seed must be frozen at registration. Stop
  rather than substituting automated judgements if human labels are insufficient.
- **Partitions and independence:** separate synthetic compatibility fixtures,
  disclosed pilot material and the evaluation selection. Deduplicate repeated
  source/model runs; retain repository identities. Do not tune against the
  evaluation selection or use the reserved VS3 repository holdout.
- **Labels and adjudication:** the owner/researcher rates whether presented concerns
  express a coherent reusable engineering issue, with a short written rubric.
  Randomise and mask method identity where feasible. Record ambiguous and missing
  ratings. A single rater limits reliability claims; do not imply inter-rater agreement.
  Rejected interpretations are not automatically verified negative examples.
- **Comparison procedure:** paired inputs, fixed preprocessing, fixed seed and
  randomised presentation order. Match the review budget per method; retain
  outliers/failures in denominator reporting. Pin the exact clustering and
  representative-selection procedures before registration.

### Measures and decision rule

| Measure | Definition and aggregation | Draft interpretation | Role |
| --- | --- | --- | --- |
| Coherence | Fraction of rated, budget-matched groups judged coherent under the frozen rubric; report numerator/denominator by method | Candidate must improve by a pre-agreed margin; freeze margin before registration | Primary |
| Coverage | Unique eligible observations represented, outliers, omitted and failed records reported separately | Reject a gain obtained mainly by excluding difficult records; freeze tolerance | Guardrail |
| Execution reliability | Failed/invalid embedding and grouping runs over attempted runs | No silent missing vectors or invalid memberships | Guardrail |
| Cost and turnaround | Recorded local elapsed time, available usage and artefact sizes on specified hardware | Descriptive feasibility check; set any adoption limit before registration | Secondary |

- **Rule:** adopt the candidate only if the frozen primary margin and all guardrails
  pass. Retain the baseline for ties/inconclusive results, or record an explicit
  owner decision to gather new prospectively registered evidence. Any departure
  is recorded without rewriting this plan. Exact numerical thresholds remain a
  registration prerequisite, not an invitation to choose them after results.
- **Stopping rule and limits:** one frozen evaluation selection and one run of each
  deterministic configuration; at most one technical rerun after a recorded
  implementation failure, preserving the original. No post-hoc model/parameter
  search. Final resource/time cap must be fixed after compatibility preflight.
- **Analysis:** report raw paired judgements, counts, coverage and failures; describe
  disagreements/ambiguity and repository concentration. This small exploratory
  default-selection study does not support population-wide superiority claims.

### Method and reproduction plan

- **Code and commands:** implement the runner and analysis in VS2 Batch A, with
  actual invocation commands and full code SHA frozen before the first study run.
  A script name alone is insufficient; no runnable method is claimed yet.
- **Environment:** Python 3.12/locked dependencies, Windows and actual GPU/CPU/RAM;
  record embedding provider/build and any nondeterminism.
- **Configuration:** pin model weights, preprocessing, clustering, randomisation,
  routing inventory/policy and prompts where used. Keep credentials outside Git.
- **Data identity:** use immutable AnnotationSelection and source/result hashes;
  record exact source licence/access constraints before sharing derived text.
- **Outputs:** preserve original run manifests, vector/membership artefacts, raw
  blinded ratings, analysis, failures and SHA-256 inventory under external runtime
  evidence; commit a small permitted summary and reproduction instructions.
- **Independent reproduction:** another researcher must be able to recover the
  permitted inputs, execute pinned commands and inspect the same rating rubric.
  Share methods, hashes and permitted outputs; if raw data redistribution is
  restricted, record access instructions and limitations. Exact stochastic output
  equality and independent reproduction are not assumed.

## Amendments and deviations

None. Draft completion is still prospective; no registered plan exists to amend.

## Runs and evidence inventory

No runs. VS1 compatibility and integration checks are prior exposure, not study results.

## Results and interpretation

Pending. No comparison has been collected or analysed.

## Decision

Pending. No grouping method has been adopted from empirical evidence.

## History

| Date | Status or event | Author | Reference / reason |
| --- | --- | --- | --- |
| 2026-09-20 | draft | Meerkritic agent | Prospective VS2 method-selection question; no registration or run |
