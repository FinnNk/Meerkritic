# Experimental Plan: Evidence-Grounded Semantic Code Review and Automated Improvement

**Companion to:** `01_SYSTEM_DESIGN.md`  
**Purpose:** Determine whether historical engineering artefacts can be transformed into reusable, reliable code-review rules that a local-model system can detect and a coding agent can safely remediate.

---

## 1. Research objective

The programme should answer four progressively harder questions:

1. **Understanding:** Can a local model reliably recognise and normalise actionable engineering concerns from heterogeneous human-authored software artefacts?
2. **Generalisation:** Can recurring observations be converted into explicit rules that detect similar issues in previously unseen repositories?
3. **Compilation:** For which rules can semantic inference be replaced or strengthened by deterministic/static measures?
4. **Repair:** When a validated rule identifies an issue, can a coding agent improve the code while preserving behaviour and avoiding regressions?

These questions must be evaluated separately. A system that generates plausible patches without establishing reliable detection is not evidence that the complete approach works.

---

## 2. Experimental philosophy

### 2.1 Public-data first

The initial feasibility study should use only public repositories/datasets.

Internal repositories should be introduced only after:

- the pipeline works end to end;
- evaluation methodology is stable;
- public baselines are recorded;
- rules and detector schemas are versioned.

This allows the later internal phase to measure **incremental organisational knowledge**, rather than mixing generic and proprietary signals from the start.

### 2.2 Repository-level generalisation

Headline results must use repository-level holdouts.

Random row-level splitting is insufficient because:

- naming;
- architecture;
- coding conventions;
- repeated review phrases;
- duplicated or related code

can leak between examples.

### 2.3 Strong negatives are scarce

Three labels must be maintained:

```text
positive:
    explicit human evidence of the target issue

weak_negative:
    no observed review comment / issue

verified_negative:
    explicitly adjudicated non-violation
```

Weak negatives may be useful for ranking studies, but they must not be treated as unquestioned ground truth when reporting precision/specificity.

### 2.4 Behavioural evaluation dominates patch similarity

The historical patch is evidence of one accepted response.

Success should be established by:

- tests;
- repository invariants;
- target-rule resolution;
- lack of new regressions;
- where appropriate, mutation testing.

Textual similarity to the human patch is secondary.

---

## 3. Research questions and hypotheses

### RQ1 — Issue extraction

**Question:** Can a local model determine whether review/PR/issue/comment text contains a generalisable engineering concern and express it canonically?

**H1:** A bounded structured prompt will substantially outperform a generic “summarise the review” prompt on human-adjudicated concern extraction.

Primary metrics:

- macro F1 for actionable/non-actionable classification;
- macro F1 for coarse category where labels exist;
- exact/semantic agreement on generalisability;
- human agreement on canonical issue correctness.

### RQ2 — Cross-source robustness

**Question:** Does the same normalisation schema work across review comments, PR descriptions, issue text, commit messages and source comments?

**H2:** Performance will vary materially by source type; source-aware prompting/context will improve the lowest-performing sources without requiring separate schemas.

Use the multi-source SATD corpus as an important controlled dataset [1].

### RQ3 — Pattern discovery

**Question:** Do normalised observations form coherent recurring clusters that humans recognise as reusable rules?

**H3:** Clustering canonical issue statements will produce higher cluster coherence and lower repo-specific fragmentation than clustering raw review text.

Compare:

- raw review embedding;
- canonical issue embedding;
- canonical issue + structural feature hybrid.

### RQ4 — Rule synthesis

**Question:** Can a larger model/agent transform coherent observation clusters into falsifiable rules with useful applicability conditions and counterexamples?

**H4:** Rules synthesised from diverse examples plus explicit counterexamples will achieve better held-out precision than rules synthesised from cluster summaries alone.

### RQ5 — Held-out rule detection

**Question:** Can the resulting rules identify matching issues in unseen repositories?

**H5:** Rules that pass a minimum evidence-diversity threshold will retain useful precision on repository-held-out data.

This is the principal feasibility gate.

### RQ6 — Static versus semantic signal

**Question:** How much of human review concern can conventional structural/history features explain?

Compare:

```text
A: static/metric features only
B: semantic model only
C: static + semantic
```

**H6:** Static features will be competitive for complexity/readability hotspots but add less for architectural, rationale and domain-knowledge rules.

`big-code-analysis` supplies a practical feature baseline including complexity and Git-history measures [2].

### RQ7 — Rule compilation

**Question:** Can some validated semantic rules be promoted to deterministic detectors without unacceptable performance loss?

**H7:** A useful minority of high-frequency semantic observations will be compilable to AST/static predicates; others will require semantic or repository context.

### RQ8 — Repairability

**Question:** Given a correct finding, can a coding agent make a valid improvement?

**H8:** Bounded rule + evidence input will yield a higher behaviourally accepted patch rate than an open-ended “improve this code” instruction.

### RQ9 — Value of review language

**Question:** Does explicit natural-language review intent improve repair compared with code-only repair?

This follows the question studied by Review4Repair, which found benefits from review comments in its sequence-to-sequence setting [3].

**H9:** For agentic repair, rule/issue context will improve success particularly for changes where multiple plausible code modifications exist.

### RQ10 — Value of organisational knowledge

Later, when internal data is permitted:

```text
A = global public rules
B = global + organisation rules
C = global + organisation + repository rules
```

Measure `B-A` and `C-B`.

No assumption should be made that proprietary rule mining necessarily improves performance.

---

## 4. Datasets

### 4.1 CRC-Py — primary early Python review dataset

CRC-Py contains 16,711 Python review comments with corresponding diff hunks and taxonomy labels [4].

Use for:

- normaliser development;
- taxonomy experiments;
- manual-adjudication sampling;
- early rule discovery.

### 4.2 GitHub Code Review dataset — scale corpus

Takizawa's dataset reports:

- 167K+ positive before/review/after examples;
- 51K+ nominal negatives;
- 725 repositories;
- 37 programming languages [5].

Use initially only the Python subset, then test cross-language transfer.

Important:

Store its “no comment” examples as `weak_negative`.

### 4.3 Multi-source SATD corpus

The SATD replication package includes source-code comments, commit messages, issue sections and PR sections; the study analysed four debt types across four source classes [1].

Use for:

- source-robustness evaluation;
- testing code-comment extraction;
- comparison to an established debt taxonomy.

### 4.4 Review4Repair

Review4Repair used 55,060 review/code-change examples and explicitly studies review-assisted repair [3], [6].

Use as:

- repair benchmark;
- independent validation corpus;
- ablation for review-text value.

### 4.5 CodeReviewer

CodeReviewer defines three relevant tasks:

1. diff quality estimation;
2. comment generation;
3. code refinement [7].

Public datasets are available through Zenodo [8].

Use as:

- benchmark comparison;
- task decomposition reference;
- independent code-refinement corpus.

### 4.6 SWE-bench Verified

SWE-bench Verified contains 500 engineer-verified solvable instances; the evaluation harness applies candidate patches and executes repository tests [9], [10].

Use for:

- agent/harness validation;
- repository-scale repair mechanics.

Do not use SWE-bench as the main semantic-rule discovery corpus.

### 4.7 BugsInPy

BugsInPy provides 493 real bugs from 17 Python projects with reproducible buggy/fixed states and tests [11].

Use for:

- Python repair evaluation;
- controlled behavioural validation.

---

## 5. Dataset manifest and provenance

Before experimentation, produce a machine-readable manifest:

```yaml
datasets:
  crc_py:
    source: ...
    version: git-sha
    licence: ...
    retrieved: ...
  github_code_review:
    source: ...
    version: dataset-revision
    licence_notes: ...
```

For every record retain:

- dataset and record ID;
- repository;
- commit(s);
- timestamp;
- language;
- source type;
- source licence metadata where available.

Never rely on a mutable `main` branch or “latest” dataset without recording the exact revision.

---

## 6. Split strategy

### 6.1 Repository split

Default:

```text
train/discovery: 70% repositories
development:     15% repositories
test:            15% repositories
```

Exact proportions may change after corpus profiling.

Stratify where practical by:

- language;
- repository size;
- number of review observations.

### 6.2 Temporal secondary evaluation

Where timestamps permit, create an additional temporal test:

```text
earlier observations → discovery
later observations   → evaluation
```

This better resembles deployment but does not eliminate foundation-model pretraining contamination.

### 6.3 Cross-dataset validation

Rules mined from one corpus should be replayed on another where semantics overlap.

Examples:

- rules mined on CRC-Py → Python subset of Takizawa;
- rule-driven repair on Takizawa → Review4Repair where compatible.

### 6.4 Frozen test set

After initial manual adjudication, freeze the headline test set and prohibit prompt/rule tuning against it.

---

## 7. Manual adjudication protocol

Human labels are required because public review corpora contain selection and labelling noise.

### 7.1 Adjudication questions

For each sampled observation:

1. Does the human text identify an engineering concern?
2. Is the concern correctly localised?
3. Is the normalised issue statement faithful?
4. Is it generalisable beyond this one patch?
5. Is the proposed rule category appropriate?
6. Are applicability/exclusion conditions sufficient?
7. For detector findings: is this actually a violation?
8. For patches: does the patch address the issue without obvious undesirable change?

### 7.2 Sampling

Use stratified sampling across:

- source type;
- category;
- cluster size;
- model certainty proxy;
- repository;
- positive/weak-negative status.

Oversample difficult/disputed examples for diagnostic analysis, but report population-weighted headline estimates separately.

### 7.3 Multiple adjudicators

For the core evaluation set, use at least two independent labels plus reconciliation for disagreements.

Report:

- raw agreement;
- Cohen's kappa for two raters or an appropriate multi-rater statistic;
- reconciliation rate.

Do not use agreement statistics as evidence that the taxonomy itself is useful; they measure label reproducibility.

---

## 8. Experiment E1 — concern extraction

### Inputs

- CRC-Py;
- multi-source SATD;
- sampled GitHub review data.

### Systems

#### Baseline B0 — keyword/rule baseline

Simple SATD/TODO/error-term features where applicable.

#### Baseline B1 — generic local LLM

Prompt:

> Summarise the issue in this review.

#### System S1 — bounded structured normaliser

Atomic questions plus structured schema:

```json
{
  "actionable_engineering_concern": "...",
  "generalisable": "...",
  "issue_statement": "...",
  "category": "...",
  "applicability": [],
  "exclusions": []
}
```

### Metrics

Classification:

- precision;
- recall;
- F1;
- macro F1;
- confusion matrix.

Canonical statement:

- blinded human correctness rate;
- faithfulness rate;
- rate of material information omission;
- rate of invented constraints.

### Decision gate G1

Proceed if:

- actionable-concern precision is high enough to avoid overwhelming later clustering with noise;
- canonical statements are judged faithful in a strong majority of cases;
- no source class is catastrophically unreliable without a known mitigation.

Use a target such as **≥0.85 precision** as an initial engineering gate, but treat it as provisional until error costs are measured.

---

## 9. Experiment E2 — representation and clustering

### Representations

R0 — raw review/comment text  
R1 — canonical issue statement  
R2 — issue statement + proposed invariant  
R3 — R2 + selected BCA structural/history features

Sentence-BERT-style embeddings provide a standard semantic embedding baseline [12].

### Clustering methods

Start with:

- HDBSCAN;
- agglomerative clustering baseline;
- k-means only as a control where a fixed cluster count is intentionally imposed.

HDBSCAN is suitable for variable-density clusters and explicit noise points [13].

### Evaluation

#### Intrinsic

- silhouette score where meaningful;
- cluster persistence/stability;
- noise fraction.

Do not rely on intrinsic metrics alone.

#### Human semantic evaluation

Sample clusters and rate:

- single-concern coherence;
- rule-worthiness;
- specificity;
- repository independence.

#### Diversity

For each cluster:

- repositories represented;
- source types represented;
- unique observations;
- concentration of largest repository.

### Decision gate G2

A useful cluster should:

- be semantically coherent under blind human inspection;
- span more than one repository for a global rule;
- contain enough evidence to formulate counterexamples.

No universal minimum `n` should be hard-coded before observing corpus distribution.

---

## 10. Experiment E3 — rule synthesis

### Conditions

R-A — cluster centroid/summary only  
R-B — representative positive examples  
R-C — positives + nearest out-of-cluster examples  
R-D — positives + explicitly generated/adjudicated counterexamples

### Output schema

Every candidate rule must contain:

- statement;
- applicability;
- violation definition;
- exclusions;
- positive examples;
- counterexamples;
- proposed detector class.

### Human evaluation rubric

Score each dimension independently:

- faithfulness to evidence;
- falsifiability;
- non-triviality;
- generality;
- applicability clarity;
- counterexample quality.

Avoid a single opaque “rule quality” number as the only result.

### Decision gate G3

Promote only rules that:

- are faithful to observed evidence;
- can be evaluated against code;
- have explicit exclusions;
- are not simple duplicates of existing rules.

---

## 11. Experiment E4 — historical replay

This is the principal detector experiment.

### 11.1 Positive replay

For each held-out historical review:

1. reconstruct code at the review point;
2. hide the human comment from the detector;
3. run candidate rules;
4. measure whether the corresponding issue is rediscovered.

### 11.2 Verified-negative construction

Build verified negatives from:

- manually adjudicated non-violations;
- code explicitly discussed and accepted;
- counterexample generation followed by human validation;
- code after a fix where the exact target issue is established as resolved.

Do not simply treat every uncommented hunk as negative.

### 11.3 Metrics

At rule level:

- precision;
- recall;
- F1;
- applicability accuracy;
- false positives per 1,000 analysed functions/hunks/files;
- abstention/uncertain rate.

At system level:

- findings per PR;
- proportion of PRs with ≥1 true finding;
- nuisance finding rate.

### 11.4 Confidence intervals

Use repository-clustered bootstrap confidence intervals so thousands of examples from one repository do not create artificially narrow uncertainty.

Headline metrics should report 95% confidence intervals.

### 11.5 Decision gate G4

For advisory use, precision matters more than recall.

Initial candidate gate:

- lower bound of 95% CI for precision ≥0.80;
- manageable finding rate;
- stable results across repository holdouts.

For blocking/enforced use, require materially stronger evidence and preferably a deterministic detector.

These thresholds are engineering starting points, not claims of universal acceptability.

---

## 12. Experiment E5 — static/semantic/hybrid comparison

For each rule family with sufficient examples:

### Feature set A — static only

Possible BCA features:

- cognitive complexity;
- cyclomatic complexity;
- Halstead;
- maintainability;
- ABC;
- LOC;
- churn;
- ownership dilution;
- bug-fix history [2].

Add AST/linter-specific features where relevant.

### Feature set B — semantic only

Local rule judge.

### Feature set C — hybrid

Static features + semantic evaluation.

### Models

Keep static baselines interpretable first:

- logistic regression;
- shallow decision tree;
- gradient-boosted model only after interpretable baselines.

### Evaluation

Repository-held-out:

- precision/recall;
- PR-AUC for imbalanced tasks;
- calibration if probabilistic scores are used;
- cost per 1,000 evaluations;
- latency.

### Decision

Classify each rule:

```text
STATIC
SEMANTIC
HYBRID
AGENTIC
```

A semantic rule should graduate to static when the simpler detector has comparable held-out utility.

---

## 13. Experiment E6 — local model comparison

Do not optimise around one model family.

### Roles to benchmark

#### Normaliser

Candidate classes:

- ~7–14B instruction/coding-capable local models;
- quantised execution.

#### Semantic rule judge

Same class, but evaluate smaller models where atomic prompts permit.

#### Rule synthesiser/repair agent

Larger local coding/reasoning model if hardware permits; otherwise use the strongest local configuration available for the experiment.

### Hardware profile

Record:

- CPU;
- RAM;
- GPU;
- VRAM;
- quantisation;
- offload layers;
- context length;
- inference engine.

### Metrics

Quality:

- E1/E4 task metrics.

Operational:

- tokens/s;
- median and p95 latency;
- peak RAM/VRAM;
- energy if measurable;
- throughput per 1,000 observations.

### Structured output

Use schema/grammar-constrained decoding where supported. llama.cpp documents JSON-schema/grammar constraints [14].

### Robustness

For a fixed model:

- repeat deterministic/near-deterministic runs;
- vary prompt paraphrase;
- vary irrelevant context;
- test code ordering where safe.

A rule judge that changes materially under superficial prompt variation is not mature enough for enforcement.

---

## 14. Experiment E7 — repair generation

### Cohorts

R0 — open-ended improvement:

> Improve this code.

R1 — review text only.

R2 — explicit normalised issue only.

R3 — rule + evidence + applicability/exclusions.

R4 — R3 + deterministic structural feedback.

### Inputs

Use:

- Review4Repair;
- selected Takizawa positive triplets;
- BugsInPy;
- compatible SWE-bench Verified cases.

### Blinding

The agent must not receive:

- historical fixed code;
- gold patch;
- hidden test outputs unavailable in a realistic development environment.

### Patch metrics

Primary:

- test-backed success;
- target-rule resolution;
- no regression on existing tests;
- patch applies/builds.

Secondary:

- number of changed files;
- diff size;
- BCA metric deltas;
- new semantic findings;
- historical patch semantic similarity.

### Decision gate G5

A repair approach is useful if it increases **behaviourally accepted patches** over the open-ended baseline without materially increasing regressions.

---

## 15. Experiment E8 — test quality and mutation

For suitable behavioural fixes:

1. identify or generate a regression test;
2. establish failure before the fix;
3. establish pass after the fix;
4. run targeted mutation testing;
5. determine whether the test kills relevant mutants around the affected behaviour.

Compare:

- historical tests;
- agent-added tests;
- no additional test.

Do not use mutation testing for changes where mutation semantics are inappropriate.

Key metric:

```text
behaviourally constrained fix rate
```

rather than raw mutation score alone.

---

## 16. Experiment E9 — metric gaming/red-team evaluation

Construct tasks where lowering a structural metric can be achieved badly.

Examples:

- split a coherent function into trivial forwarding functions;
- move complexity into a helper without simplification;
- duplicate logic;
- introduce indirection;
- suppress warnings.

Give an agent BCA feedback and observe whether it games the metric.

Conditions:

A — metric objective only  
B — metric + semantic rule  
C — behaviour + semantic rule + metric constraint

Success:

- complexity improvement without increased duplication/indirection/regression;
- human preference;
- no new semantic findings.

This experiment is important before integrating metric feedback into autonomous repair.

---

## 17. Experiment E10 — public-to-internal transfer

Run only after public-data gates pass.

### A. Frozen public rule set

No internal adaptation.

### B. Add organisation rules

Mine internal evidence but exclude target repositories from rule discovery.

### C. Add repository rules

Allow local history.

Compare on held-out internal PRs:

- precision;
- unique useful findings;
- finding overlap;
- developer acceptance;
- repair success.

This separates generic value from organisational specificity.

---



## Double-Entry Review treatment

DER is the change-preparation/review method for material software changes made while building
the programme. It is **not a primary experimental variable** in the semantic-review research.

Record incidental operational observations (preparation/reconstruction/review time, revision
rounds and existing model-usage telemetry where available) so the host materiality threshold can
be revisited later, but do not introduce artificial DER/non-DER comparisons by default.

Software experiment artefacts, dataset labelling and model/rule experiments do not themselves
require DER unless they involve a material software change to the project/repository.


## Routing-policy treatment

Model routing is an engineering policy, not a primary experimental variable.

The research programme may use different routing policies by project/task and may switch policy mid-task when operational constraints change, but this should not become a coding-model evaluation workstream.

Every experiment must retain:

- model-inventory version;
- routing-policy version;
- concrete routing decisions;
- policy transitions;
- model-usage telemetry.

If a policy changes during an experiment, the transition must be visible in provenance so later analysis can distinguish:

```text
detector/experiment effect
from
routing-policy effect
```

Operational observations may inform future routing revisions, but no artificial model bake-off is required by default.


## 18. Statistical analysis

### 18.1 Unit of analysis

Avoid pretending examples are independent when nested in repositories.

Report both:

- example-level metrics;
- repository-level distributions.

### 18.2 Bootstrap

Use repository-cluster bootstrap for confidence intervals.

### 18.3 Paired comparisons

Where two systems evaluate the same instances:

- paired bootstrap for metric differences;
- McNemar's test for paired binary outcomes where appropriate.

### 18.4 Multiple comparisons

If evaluating many rule families/models, distinguish:

- confirmatory hypotheses;
- exploratory analyses.

Correct for multiple comparisons for confirmatory families where inferential p-values are used.

### 18.5 Effect sizes

Report effect size and confidence interval, not only significance.

### 18.6 Power

Do not choose a sample size from a generic rule of thumb.

After pilot data:

1. estimate baseline success/error rates;
2. define minimum practically meaningful improvement;
3. calculate required sample size for the paired design.

---

## 19. Evaluation metrics catalogue

### Concern extraction

- precision/recall/F1;
- macro F1;
- faithfulness;
- hallucinated-constraint rate.

### Clustering

- human coherence;
- cluster stability;
- repository diversity;
- noise fraction.

### Rule quality

- held-out precision;
- held-out recall;
- applicability accuracy;
- false positives per KLOC/function/PR;
- detector abstention.

### Repair

- patch application rate;
- build pass rate;
- target tests passed;
- full-suite non-regression;
- target-rule resolution;
- patch acceptance;
- mutation-backed test adequacy where relevant.

### Efficiency

- latency;
- throughput;
- GPU/RAM use;
- inference cost proxy;
- static-versus-semantic detector ratio.

### Human factors

Later:

- reviewer acceptance rate;
- dismissal rate;
- time-to-decision;
- perceived usefulness;
- duplicate/noisy comment rate.

---

## 20. Ablation matrix

At minimum, run these ablations.

| Factor | A | B |
|---|---|---|
| Input text | raw review | canonical issue |
| Rule prompt | compound | atomic |
| Output | free text | schema-constrained |
| Context | local hunk | retrieved repository context |
| Features | semantic only | semantic + BCA |
| Negative data | weak negatives | verified negatives |
| Repair instruction | open-ended | bounded rule |
| Repair feedback | tests only | tests + static + semantic |
| Rule synthesis | positives | positives + counterexamples |

Ablations are more informative than a single end-to-end score because they explain *why* the system works.

---

## 21. Threats to validity

### 21.1 Construct validity

A review comment is not identical to a defect.

It may express:

- preference;
- style;
- local convention;
- misunderstanding;
- negotiation.

Mitigation:

- explicit taxonomy;
- human adjudication;
- separate correctness from maintainability/design concerns.

### 21.2 Missing-negative bias

Absence of review feedback does not imply correctness.

Mitigation:

- weak-negative distinction;
- curated verified-negative set.

### 21.3 Reviewer authority bias

Human reviewers can be wrong.

Mitigation:

- post-review change is supporting evidence, not proof;
- test/behavioural validation;
- disputed/overruled threads treated separately where available.

### 21.4 Public-dataset contamination

Modern code models may have seen public code or benchmark patches in training.

Mitigation:

- repository and temporal holdouts;
- novel/internal final validation;
- never claim public benchmark performance proves unseen-repository reasoning.

### 21.5 Language bias

Python-first conclusions may not transfer.

Mitigation:

- explicitly scope the PoC;
- later replicate on at least one statically typed language.

### 21.6 Repository-size bias

Popular open-source repositories differ from ordinary enterprise codebases.

Mitigation:

- stratify by repository size/activity;
- later internal replication.

### 21.7 Test-suite oracle weakness

Passing tests does not prove patch correctness.

Mitigation:

- rule re-evaluation;
- targeted tests;
- mutation testing;
- static checks;
- human adjudication samples.

---

## 22. Recommended staged execution

**Nomenclature:** the phases below are **research phases (P0–P5)**. They describe the evidence programme and are distinct from harness phases (`H0–H6`) and implementation vertical slices (`VS1–VS8`). The vertical-slice plan in `06_IMPLEMENTATION_HANDOVER.md` is authoritative for build sequencing.

### Phase 0 — infrastructure and corpus audit

Deliverables:

- dataset manifests;
- reproducible ingestion;
- repository-level splits;
- source artefact schema;
- local inference abstraction;
- BCA feature adapter.

Exit gate:

- exact replayable provenance for sampled records.

### Phase 1 — issue normalisation

Run E1.

Deliverables:

- versioned normaliser;
- error taxonomy;
- 500+ adjudicated examples across sources.

Exit gate:

- acceptable precision and faithfulness.

### Phase 2 — rule discovery

Run E2/E3.

Deliverables:

- cluster report;
- 10–20 candidate rules;
- counterexample set;
- rule registry v1.

Exit gate:

- coherent, falsifiable rules with multi-repository evidence.

### Phase 3 — held-out detection

Run E4/E5/E6.

Deliverables:

- repository-held-out metrics;
- static/semantic/hybrid comparison;
- local-model throughput report;
- first validated rules.

Exit gate:

- at least 5 rules with useful held-out precision.

### Phase 4 — remediation

Run E7/E8/E9.

Deliverables:

- repair harness;
- behavioural acceptance metrics;
- mutation-backed case studies;
- metric-gaming report.

Exit gate:

- bounded-rule repair beats open-ended baseline.

### Phase 5 — internal transfer

Run E10.

Deliverables:

- global vs organisation vs repository-rule comparison;
- governance recommendation for advisory deployment.

---

## 23. Suggested first experimental tranche

A compact but meaningful experimental tranche:

### Data

- 2,000 CRC-Py observations;
- 5,000 Python Takizawa observations;
- 2,000 SATD multi-source examples;
- 100 repair cases from Review4Repair/BugsInPy/SWE-bench-compatible sources.

### Human labels

- 500 observation-normalisation cases;
- 200 verified negatives;
- 100 rule-finding adjudications;
- 50 generated patches.

### Rules

Aim for:

- 20 mined candidates;
- 10 reviewed;
- 5 validated.

### Models

Benchmark:

- at least two local model sizes;
- one embedding model;
- one coding-agent configuration.

### Static tools

- BCA;
- standard Python parser/AST;
- project linters/type checkers where present.

This is sufficient to determine whether the architecture is promising without prematurely building a platform.

---

## 24. Go/no-go criteria

### Continue to larger public experiment if:

- concern extraction is precise and faithful;
- clusters yield genuinely reusable rules;
- ≥5 rules survive repository-held-out replay;
- local inference throughput is practical;
- verified negatives expose manageable false-positive rates.

### Continue to internal-data phase if:

- public-rule results are reproducible;
- repair evaluation is behaviourally grounded;
- system provenance/licensing controls are adequate;
- public rules provide a stable baseline for measuring incremental internal value.

### Reconsider the architecture if:

- rules collapse into repository-specific one-offs;
- detector precision remains poor despite explicit applicability;
- generated repairs routinely optimise metrics without resolving underlying concerns;
- human adjudicators cannot reliably agree on the proposed rule semantics.

A negative result at any of these stages is useful: it identifies the layer that fails rather than producing an uninterpretable end-to-end failure.

---

## 25. Expected final outputs from the research programme

1. **Dataset manifest and provenance report**
2. **Normalised observation corpus**
3. **Rule registry with evidence lineage**
4. **Static/semantic/hybrid detector benchmark**
5. **Local inference performance report**
6. **Historical replay benchmark**
7. **Repair benchmark and behavioural evaluation**
8. **Mutation-testing appendix for suitable repair classes**
9. **Threats-to-validity and contamination report**
10. **Deployment recommendation: research-only, advisory, or enforceable-by-rule**
11. **Later internal-transfer study**

---

# References

[1] Y. Li, M. Soliman, and P. Avgeriou, “Replication Package for Automatic Identification of Self-Admitted Technical Debt from Four Different Sources,” GitHub repository. [Online]. Available: https://github.com/yikun-li/satd-different-sources-data. [Accessed: Sep. 19, 2026].

[2] dekobon, “big-code-analysis: Tool to report source code metrics,” GitHub repository, 2026. [Online]. Available: https://github.com/dekobon/big-code-analysis. [Accessed: Sep. 19, 2026].

[3] F. Huq, M. Hasan, M. A. H. Pantho, S. Mahbub, A. Iqbal, and T. Ahmed, “Review4Repair: Code review aided automatic program repairing,” *Information and Software Technology*, vol. 143, Art. no. 106765, Mar. 2022, doi: 10.1016/j.infsof.2021.106765.

[4] B. Icoz, “CRC-Py Dataset: Public Dataset of Python Code Review Comments Labeled with an ESEM'23 Taxonomy,” GitHub repository. [Online]. Available: https://github.com/busraicoz/crc-py-dataset. [Accessed: Sep. 19, 2026].

[5] R. Takizawa, “GitHub Code Review Dataset,” Hugging Face Datasets, 2026. [Online]. Available: https://huggingface.co/datasets/ronantakizawa/github-codereview. [Accessed: Sep. 19, 2026].

[6] Review4Repair, “Review4Repair dataset and source code,” GitHub repository. [Online]. Available: https://github.com/Review4Repair/Review4Repair. [Accessed: Sep. 19, 2026].

[7] Z. Li *et al*., “Automating code review activities by large-scale pre-training,” in *Proc. 30th ACM Joint European Software Engineering Conf. and Symp. on the Foundations of Software Engineering (ESEC/FSE)*, 2022, pp. 1035–1047, doi: 10.1145/3540250.3549081.

[8] “Automating Code Review Activities by Large-Scale Pre-training — datasets and source code,” Zenodo, 2022. [Online]. Available: https://zenodo.org/records/6900648. [Accessed: Sep. 19, 2026].

[9] C. E. Jimenez, J. Yang, A. Wettig, S. Yao, K. Pei, O. Press, and K. Narasimhan, “SWE-bench: Can Language Models Resolve Real-World GitHub Issues?” arXiv:2310.06770, 2023. [Online]. Available: https://arxiv.org/abs/2310.06770.

[10] SWE-bench, “Datasets,” 2026. [Online]. Available: https://www.swebench.com/SWE-bench/guides/datasets/. [Accessed: Sep. 19, 2026].

[11] R. Widyasari *et al*., “BugsInPy: A Database of Existing Bugs in Python Programs to Enable Controlled Testing and Debugging Studies,” in *Proc. 28th ACM Joint Meeting on European Software Engineering Conf. and Symp. on the Foundations of Software Engineering (ESEC/FSE)*, 2020, doi: 10.1145/3368089.3417943. [Online]. Available: https://arxiv.org/abs/2401.15481.

[12] N. Reimers and I. Gurevych, “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks,” in *Proc. 2019 Conf. on Empirical Methods in Natural Language Processing and 9th Int. Joint Conf. on Natural Language Processing (EMNLP-IJCNLP)*, Hong Kong, 2019, pp. 3982–3992, doi: 10.18653/v1/D19-1410.

[13] R. J. G. B. Campello, D. Moulavi, A. Zimek, and J. Sander, “Hierarchical density estimates for data clustering, visualization, and outlier detection,” *ACM Trans. Knowledge Discovery from Data*, vol. 10, no. 1, Art. no. 5, 2015, doi: 10.1145/2733381.

[14] ggml-org, “llama.cpp grammars: JSON Schemas to GBNF,” GitHub repository documentation, 2026. [Online]. Available: https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md. [Accessed: Sep. 19, 2026].
