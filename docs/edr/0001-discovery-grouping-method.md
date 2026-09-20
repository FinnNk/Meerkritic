# EDR-0001: Choose an initial discovery grouping method

- Status: draft
- Created: 2026-09-20
- Owner: Project owner
- Decision-maker(s): Project owner
- Protocol agreement: Finn Newick, 2026-09-20; proposed workload and criteria accepted
- Registered on: pending
- Registered plan: pending; this draft is not a frozen registration
- Evidence outcome: pending
- Implementation: not planned until a recorded adoption decision
- Related records: [VS2 plan](../plans/VS2-plan.md), [VS1 review](../slice-reviews/VS1-review.md), [ADR-0001](../adr/ADR-0001-record-significant-empirical-decisions.md)

## Registered plan

This section is a prospective draft. Registration is blocked on the concrete
permitted human-labelled sample and runnable, pinned methods. The owner agreed the
proposed workload and criteria on 20 September 2026. Synthetic
local model/runtime compatibility preflight has passed; the exact evaluation method
and sample remain unfrozen. Do not collect or analyse decision-bearing results
until these details and the registration commit are recorded. No selection decision
has been made from the functional VS1 data.

VS2 software compatibility also exercised pinned local embeddings, exploratory
grouping, provisional rule synthesis and advisory guidance on explicitly synthetic
interpretations. Insufficiency outputs and a prompt-contract clarification are
retained in DER `vs2-rules/r1`; neither they nor automated fixture decisions are
evaluation labels or evidence of comparative quality. This draft has not been
registered, and no decision-bearing comparison has been run.

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
- **Sample and selection:** provisionally 40 eligible accepted/edited observations,
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

- **Code and commands:** `tools/study_compare.py` provides the lexical execution,
  masked pack and analysis commands. Follow the [comparison guide](../development/study-comparison.md).
  Freeze actual invocation commands and full code SHA before the first study run;
  software verification does not register the study.
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

## Concrete proposal for owner review

Prepared after PR #13 integration on 20 September 2026. Everything in this section
is **proposed, not registered or adopted**. The thresholds are prospective judgement
calls for a small local study, not values optimised on results. The owner agreed
the proposed workload and criteria on 20 September 2026. Qualified inputs, runnable
tooling and exact identities are still required; that agreement is not registration.

### Prepare the input sample

| Choice | Proposed procedure |
| --- | --- |
| Source | The pinned CRC-Py manual file in `config/datasets/crc-py-manual.json`; retain its source hash and zero-based indexes. Its upstream category labels are not our evaluation labels. |
| Prior exposure | Exclude records from the two known pilot repositories, `django/django` and `paperless-ngx/paperless-ngx`. Add any further disclosed exposure before selection. |
| Repository holdout | Sort the remaining case-folded `owner/repository` identities by SHA-256 of UTF-8 `20260920:holdout:<identity>`; reserve the first ceiling of 20% of identities. Record the list before reading their source bodies or producing interpretations. Existing restrictions take precedence. |
| Candidate order | Within each development repository, sort records by SHA-256 of UTF-8 `20260920:sample:<source-hash>:<source-index>`. Traverse repositories in case-folded lexical order, taking one record per repository per round. Do not use category, comment wording or later model output to select promising concerns. |
| Source qualification | Check each candidate's repository, PR/comment identity and provenance against its original public source before annotation. Preserve supplied/preprocessed text; record the original reference and discrepancies separately. Exclude unresolved origins or unusable context with reasons. An unfamiliar repository name alone is not an exclusion. |
| Duplicates | For repeated case-folded repository/comment identities retain the lowest source index; also exclude subsequent identical code/comment pairs. Retain the excluded identities. Do not deduplicate or rewrite the imported source file. |
| Human-review budget | Inspect at most 80 candidate records, at most ten from any repository, stopping when 40 usable Accept/Edit interpretations have been collected. Limit the final selection to five accepted/edited observations per repository. Retain every attempted, failed, skipped and rejected record. |
| Shortfall | If the fixed budget cannot yield 40 eligible observations, stop preparation and revise this draft prospectively. Do not substitute automated decisions or quietly extend the budget. |

The implemented preparation procedure is `edr-0001-inputs-v1`. It partitions the
claimed repository identities first, deduplicates by original source position,
then applies the seeded candidate ordering. A duplicate of an earlier excluded
record remains excluded. The fixed pool contains at most 80 positions; a later
skip after five usable reviews from a repository consumes its position, without
replacement from outside that pool. These operational details were fixed before
source qualification or human input review, not selected from grouping results.

On 20 September 2026, metadata-only preparation retained 80 candidates across 45
development repositories and reserved 12 repository identities. Of the 950 other
records, 92 have prior-exposure precedence, 130 holdout precedence, four duplicate
precedence and 724 fall outside the candidate budget. These are mutually exclusive
planning reasons, not source-authenticity judgements. Automatic exact-text hashes
were used only for deduplication; source bodies were not displayed or interpreted.

- Source bytes: `a36405b45b65f6a193a12e15bb9c600d6c0f46d84eb4dc891f315248a7cade83`.
- Plan content: `de2a70fbbf1510389627e68fce37b1d49389c82bf0eb2138901fcab78a33458c`.
- Initial external record: `bef06bf63a6f3f4f8842aa0dc0714dc8accceb18fbc36111acbcbcd80aa13cf2`.
- Preparation code: diary `f027a95765c5309d863392509ca4594c0951b811`, retained with
  DER `vs2-study-tools/r1`; replay with the [preparation command](../development/study-preparation.md#create-the-fixed-input-order).

The plan is retained outside Git at `extras/research/edr-0001/preparation/0000.json`
relative to the workspace parent. That initial record contains zero attempts or
human labels. The normalisation configuration was subsequently frozen before
source inspection and inference; the preparation outcome is recorded below. Exact
research annotation versions and registration remain pending. Neither the metadata
plan nor its software verification is a grouping run.

Source qualification, normalisation and human input review prepare the corpus;
they are not the grouping comparison. They follow the agreed sampling procedure.
Group outputs and coherence ratings must not be produced before registration.
One fixed normalisation configuration produces one initial interpretation per
candidate; retain failures and use human Edit to correct a usable interpretation.
Do not keep sampling model outputs until a preferred interpretation appears.
Freeze its exact model/prompt/routing configuration before input preparation and
include that provenance at registration.

Metadata-only preparation inspected 1,030 records and 59 claimed repository
identities; 369 records name `TheAlgorithms/Python`. Some other identities resemble
example repositories. These observations motivate provenance checks and a
concentration limit; they do not prove that particular records are synthetic or
that this sampling design is optimal. No source comments, grouping outputs or
coherence ratings were inspected in that preparation. The upstream description
alone does not validate every record in the manual subset. Record verification
results before declaring any selected observation a historical example.

### Compare two fixed methods

| Part | Proposed fixed choice |
| --- | --- |
| Shared input | The existing discovery interpretation-text builder applied to exactly the same ordered, human-reviewed selection. No source taxonomy labels or extra code enter either method. Freeze the builder's code SHA. |
| Candidate | `nomic-embed-text-v1.5.f16.gguf`, revision `0188c9bf409793f810680a5a431e7b899c46104c`, SHA-256 `f7af6f66802f4df86eda10fe9bbcfc75c39562bed48ef6ace719a251cf1c2fdb`; existing pinned llama.cpp profile, 768 dimensions and `clustering: ` prefix. Use `cosine-components-v1`, threshold 0.85, minimum size 2. |
| Baseline | Case-fold the shared text; extract sets of ASCII tokens matching `[a-z0-9]+`. No stop-word list, stemming or fitted vocabulary. Connect pairs whose token-set Jaccard similarity is at least 0.25; groups are connected components of size at least 2. Empty token sets are reported as outliers and cannot match one another. |
| Representatives | Select the member with greatest summed within-group similarity; ties follow frozen input order. Rate all group members, not only the representative. |
| Reason for these settings | Candidate 0.85 is the existing documented exploratory example; baseline 0.25 is a simple untuned comparator. Neither is an adopted default. This study compares these configurations, not the best possible version of either method. |
| Execution | One run per configuration, using an immutable embedding artefact. At most one technical rerun across the study after a diagnosed implementation failure; retain the original failure and any exposed outputs. No parameter search. |
| Resource limit | A proposed 30-minute wall-clock cap for each method after model loading, excluding input curation and human rating. Record hardware, model loading separately, timeouts and all known usage. Synthetic preflight must establish feasibility before registration. |

The baseline, rating pack and analysis commands are implemented as material DER
change `vs2-comparison` (review round `r2`), with synthetic fixtures and the existing quality gates.
They bind the exact selection, interpretation text, vectors and memberships; no
new research UI or database state is required. Freeze exact commands, code, runtime
versions and input/output formats before registration. No research comparison has run.

The deterministic masking procedure uses canonical JSON SHA-256, seed `20260920`
and sorted membership IDs. Rank groups independently within each method with stage
`select`, take the equal budget, deduplicate identical membership sets, then rank
presentation with stage `present`. The [reproduction table](../development/study-comparison.md#reproduce-the-ordering-and-report)
specifies the complete hash input and member order. This implements the previously
proposed seeded ordering before any research grouping or rating exposure.

### Rate the groups and decide

1. Create a deterministic, method-masked assessment pack. Record the randomisation
   procedure and seed `20260920`, and keep the method mapping out of the rating pack.
2. Match the number of assessed groups: `k = min(12, baseline groups, candidate groups)`.
   Select groups by a documented seeded ordering. Fewer than eight groups per
   method makes the primary comparison insufficient; do not relax this after results.
3. Present complete member texts. Give identical membership sets one rating and
   reuse it for both methods; retain the mapping so this is not hidden independence.
4. Record `coherent`, `not coherent` or `uncertain`, plus a short reason. A coherent
   group expresses one specific reusable engineering concern across every member;
   sharing a language, library or broad topic is insufficient. Contradictory or
   unrelated members make it not coherent; inadequate context makes it uncertain.
5. Freeze completed ratings before revealing method identities. The named human
   rater must supply the judgements. Similar group content may reveal the method;
   record suspected unmasking and do not claim perfect blinding.

| Criterion | Proposed decision rule |
| --- | --- |
| Primary | Candidate coherent-group fraction exceeds the baseline by at least 10 percentage points and is at least 75%. Count uncertain ratings in the assessed denominator as not established coherent. |
| Rating completeness | Require all selected groups to be rated. Missing ratings leave analysis incomplete; do not silently drop them or substitute agent judgements. |
| Coverage | Candidate groups of size at least 2 cover at least 60% of the 40 inputs, and coverage is no more than 10 percentage points below the baseline. Report all outliers and unassessed groups separately. |
| Reliability and resource limits | Final method runs have complete, valid outputs and finish within the registered cap. A technical rerun does not erase the initial failure. |
| Adoption | Recommend the candidate only when every applicable criterion passes. Otherwise record no adoption or an inconclusive result with the exact failed/unevaluable criteria; the owner makes the final decision. |

Report raw numerators/denominators, group sizes, repository concentration, failures
and limitations. Shared inputs do not create matched output groups. This small,
single-rater comparison does not establish population-wide superiority. An
inconclusive result can support an explicit decision to keep the current method
exploratory or commission a new registered study; it cannot be relabelled success.
Choosing the baseline does not imply it is already an application default: any
implementation needed for that choice requires its own verification.

### Registration checklist

- [x] Owner agrees the bounded question, workload, rubric, thresholds and limits
  (Finn Newick, 2026-09-20: “I agree with Edr-0001’s proposed workload and criteria”).
- [ ] Input preparation follows the agreed procedure; qualified sources, exclusions,
  holdouts, prior exposure and 40 human-reviewed versions are frozen and permitted.
- [ ] Exact selection/hash, normalisation configuration and curator attestation recorded.
- [ ] Baseline/runner, masking, analysis and failure checks pass on synthetic inputs.
- [ ] Exact code SHA, commands, hardware, versions and configuration recorded; no placeholders.
- [ ] Commit the completed plan, then commit its SHA, date and `registered` status
  before executing either method on the research selection or collecting group ratings.

Use [the study preparation guide](../development/study-preparation.md) for the
human and agent hand-off. Neither merging this draft nor accepting the software
registers the experiment or adopts a method.

## Amendments and deviations

None. Draft completion is still prospective; no registered plan exists to amend.

## Runs and evidence inventory

No research grouping runs. Earlier compatibility and integration checks are prior
exposure, not comparative study results.

### Input preparation on 20 September 2026

The fixed pool and one initial normalisation pass have been inspected. This is
corpus preparation, not a grouping comparison or a model-quality benchmark.

| Stage | Recorded outcome |
| --- | ---: |
| Fixed candidate positions inspected | 80 |
| Public origins/context qualified for input review | 55 |
| Origins unresolved after public comment endpoints returned 404 | 25 |
| Initial normalisation attempts | 55 |
| Schema- and evidence-valid drafts | 33 |
| Retained failed outputs | 22 |
| Failures from missing or ambiguous exact evidence quotes | 21 |
| Failure from an affirmative concern without required source evidence | 1 |
| Human Accept/Edit/Reject decisions | 0 |
| Model reruns or research grouping runs | 0 |

The agreed target of 40 usable human-reviewed inputs is **unreachable under the
current preparation rules**: only 33 valid drafts are available, before any human
rejection. Stop before registration. Do not extend the pool, retry models, relax
evidence validation or treat an automated decision as a human label. The owner
must choose an explicit prospective amendment. Human correction of repairable
failed drafts has been proposed, preserving the original failures and single model
pass; it has not been agreed or implemented. The current annotation controls require
a successful normalisation and cannot yet apply such corrections to failed jobs.

Source checks retained the original imported bytes and separate public responses.
Observed differences include case/formatting changes, removed suggestion blocks
and collapsed diff whitespace, consistent with the upstream preprocessing description.
The public `httpie/httpie` endpoint redirects to `httpie/cli`; matching comment IDs,
PR numbers, paths and content were verified without rewriting imported identities.
Public origin does not establish a comment's correctness. Some original comments
were authored by bots; human assessment is still required.

The [preparation summary](evidence/0001-input-preparation.json) records exact code,
model/prompt/routing settings, counts and evidence hashes. The full per-candidate
inventory, response receipts, failed and successful outputs, runtime files and
validation replay remain under `extras/research/edr-0001` outside Git. Its digest
is included in the summary. The retained initial ledger has one unresolved-source
outcome and stops before the first human decision; it does not pretend that all
later input reviews have occurred. Separate source/job records cover all 80 positions.

Reproduce the candidate order with the preparation command and pinned source hash;
then use the recorded configuration and normalisation code to inspect the initial
pass. Original upstream README/licence receipts are retained. That repository's
MIT licence is recorded, without asserting that it grants every right in the
third-party comments/code it collected. No raw source or model output is republished
here. Access dates, response hashes and local runtime evidence support inspection;
independent reproduction and byte-identical model output have not been demonstrated.

## Results and interpretation

Pending. No comparison has been collected or analysed.

## Decision

Pending. No grouping method has been adopted from empirical evidence.

## History

| Date | Status or event | Author | Reference / reason |
| --- | --- | --- | --- |
| 2026-09-20 | draft | Meerkritic agent | Prospective VS2 method-selection question; no registration or run |
| 2026-09-20 | draft elaborated | Meerkritic agent | Software integrated; proposed bounded protocol and source-qualification gate for owner agreement; no study run |
| 2026-09-20 | protocol agreed; draft retained | Finn Newick | Explicit agreement to the proposed workload and criteria; source preparation, tooling and registration remain outstanding |
| 2026-09-20 | input order recorded; draft retained | Meerkritic agent | Reproducible metadata-only candidate/holdout plan; no source qualification, human labels or comparison |
| 2026-09-20 | comparison tooling prepared; draft retained | Meerkritic agent | Fixed lexical method, masking and criterion report with synthetic checks; registration and human judgements remain outstanding |
| 2026-09-20 | input preparation infeasible; draft retained | Meerkritic agent | All 80 origins checked; 55 initial normalisations produced 33 valid drafts and 22 retained failures. No human labels or grouping results; owner amendment required before continuing. |
