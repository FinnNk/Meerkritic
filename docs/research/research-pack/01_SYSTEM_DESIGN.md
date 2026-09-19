# System Design: Evidence-Grounded Semantic Code Review and Automated Improvement

**Status:** Proposed architecture  
**Scope:** Public-data-first proof of concept, with later adaptation to organisation- and repository-specific review history  
**Primary objective:** Discover recurring engineering concerns from software-development artefacts, formalise them as explicit rules, detect violations using the cheapest reliable mechanism, and pass well-grounded findings to a coding agent that can generate and evaluate improvements.  
**Design constraint:** The system must not depend on TypeSafe/Jev. It should run with conventional local language models and deterministic tooling wherever practical.

---

## 1. Executive summary

This design proposes an **evidence-grounded semantic lint and repair system**.

The system learns from natural-language engineering evidence such as:

- pull-request descriptions;
- inline review comments;
- review-thread replies;
- issue descriptions;
- commit messages;
- source-code comments, including self-admitted technical debt (SATD);
- code before and after review;
- tests and other repository validation artefacts.

The central architectural decision is to make the **rule** a first-class, inspectable artefact between historical evidence and automated repair:

```text
engineering evidence
        ↓
normalised issue observations
        ↓
candidate pattern discovery
        ↓
explicit rule
        ↓
detector selection
        ↓
finding
        ↓
coding agent
        ↓
behavioural + structural + semantic evaluation
        ↓
accept / reject / refine
```

This deliberately avoids an opaque architecture of:

```text
historical reviews → large model → patch
```

The proposed system instead separates five problems:

1. **Evidence extraction** — determine whether a human-authored artefact expresses an actionable engineering concern.
2. **Rule discovery** — identify recurring concerns and convert them into bounded, falsifiable rules.
3. **Detection** — evaluate new code against a rule.
4. **Remediation** — use an agent to propose a change.
5. **Evaluation** — establish whether the change fixes the intended issue without introducing regressions.

This decomposition borrows an important idea from Jeff/Jev: semantic checks work better when framed as **narrow, atomic questions**, rather than as a request to “review this code” [1], [2]. Unlike Jeff, however, the design does not require Jev or TypeSafe. Structured local inference can be implemented with a conventional language model constrained to a JSON schema or grammar; llama.cpp, for example, supports JSON-schema-constrained generation [3].

The system is also explicitly **hybrid**. A concern initially discovered semantically should not necessarily remain an LLM check forever. If it can be represented reliably using AST analysis, metrics, data flow, a linter, or a repository invariant, it should be promoted to that cheaper and more deterministic implementation.

`big-code-analysis` (BCA) fits as a deterministic evidence and evaluation substrate: it exposes per-function complexity and maintainability metrics, threshold gates and baselines, and Git-history measures including churn, ownership dilution and bug-fix history [4]. These signals should support semantic findings and patch evaluation, not serve as ground truth for “good code”.

---

## 2. Goals and non-goals

### 2.1 Goals

The system should:

1. Mine heterogeneous engineering text for actionable concerns.
2. Preserve provenance from every rule back to human evidence.
3. Discover recurring patterns without assuming a fixed taxonomy.
4. Support a stable, human-reviewable rule schema.
5. Decide for each rule whether the appropriate detector is:
   - deterministic/static;
   - local semantic model;
   - repository-context semantic model;
   - execution-backed agentic check.
6. Use local models for routine semantic classification and rule checking.
7. Use coding agents only after a bounded issue has been identified.
8. Evaluate generated repairs using repository behaviour wherever possible.
9. Measure structural change with tools such as BCA, but prevent metric gaming.
10. Support public-data-only development before any internal-code integration.
11. Enable later organisation-specific and repository-specific rules without mixing them with generic rules.
12. Make every stage independently benchmarkable.

### 2.2 Non-goals

The initial system should **not** attempt to:

- replace human code review;
- infer that uncommented code is correct;
- optimise arbitrary scalar “code quality scores”;
- train a foundation model from scratch;
- fine-tune before prompt-based baselines are established;
- accept generated patches solely because another LLM approves them;
- treat historical human patches as the unique correct solution;
- automatically promote newly mined rules directly into blocking CI gates;
- perform fully autonomous merges.

---

## 3. Relationship to Jeff/Jev

Jeff is a read-only semantic checker with 20 general code-quality rules such as unclear responsibility, weak error handling, unnecessary complexity, duplicated domain knowledge, missing rationale and difficult-to-test structure [1]. It delegates semantic judgement to Jev.

TypeSafe describes Jev as a structured decision model operating on state plus typed questions (`Choice`, `Score`, and `Noul`) and recommends decomposing complex judgements into atomic, independently evaluated questions [2].

The proposed design retains three useful principles:

1. **bounded rules** rather than open-ended review;
2. **atomic judgement questions** rather than compound prompts;
3. **machine-consumable structured results**.

It replaces the Jev dependency with a model-independent inference interface:

```text
Rule + Evidence Window + Context
             ↓
     Semantic Judge API
             ↓
Structured RuleEvaluation
```

A local model is permitted to return an explanation and evidence locations, but **its generated numerical self-confidence is not treated as calibrated probability**. Confidence in production findings is instead derived from observable evidence: detector agreement, replay performance, rule maturity, stability across prompt/model variants, and empirical false-positive rates.

---

## 4. Architectural principles

### 4.1 Evidence before automation

Every rule must record:

- why it exists;
- where it came from;
- representative positive examples;
- representative counterexamples;
- known exclusions;
- validation history.

### 4.2 Separate discovery from enforcement

Rule mining is exploratory. Enforcement is conservative.

A candidate pattern may be useful for research long before it is reliable enough to create PR comments or block CI.

### 4.3 Cheapest reliable detector wins

Detector preference:

```text
deterministic syntax/AST
        ↓
static/data-flow analysis
        ↓
metric-based predicate
        ↓
small local semantic judge
        ↓
larger context-aware local model
        ↓
tool-using agent/execution
```

Move downward only when the cheaper mechanism cannot express the rule with acceptable error.

### 4.4 Behaviour beats appearance

A patch is not accepted because:

- it resembles the historical patch;
- complexity decreased;
- an LLM says it is better.

Behavioural and repository-specific validation outrank textual resemblance.

### 4.5 Human absence is not negative evidence

Historical code-review data is selectively observed.

Therefore:

- **positive** = a relevant concern is explicitly observed;
- **weak negative** = no such concern was observed;
- **verified negative** = a human or trusted process explicitly establishes non-violation.

Only verified negatives should be treated as clean ground truth for specificity/precision estimates.

### 4.6 Rules are versioned products

A rule may change because its definition, scope, detector or evidence changes. Rule versions must be immutable once used in an experiment.

---

## 5. High-level architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                    SOURCE / EVIDENCE LAYER                   │
│ PR text · review comments · code comments · issues · commits │
│ pre/post code · tests · repository metadata · Git history    │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                    INGESTION & PROVENANCE                    │
│ immutable source IDs · timestamps · commits · line anchors   │
│ licence metadata · repository split · author/reviewer masks  │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                   OBSERVATION NORMALISATION                  │
│ actionable? · issue statement · category · scope · evidence  │
│ generalisable? · proposed invariant · exclusions             │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                     PATTERN DISCOVERY                        │
│ embeddings · density clustering · duplicate collapse         │
│ taxonomy alignment · prevalence · repository diversity       │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                       RULE REGISTRY                          │
│ candidate → reviewed → validated → advisory → enforced       │
│ global / organisation / repository scope                     │
└──────────────────────────────┬───────────────────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
┌───────────────────┐ ┌──────────────────┐ ┌───────────────────┐
│ Static detectors  │ │ Semantic judges  │ │ Agentic detectors │
│ AST/lint/BCA/etc. │ │ local LLM        │ │ tools + execution │
└──────────┬────────┘ └────────┬─────────┘ └─────────┬─────────┘
           └───────────────────┼─────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                         FINDINGS                             │
│ rule · applicability · evidence · severity · detector trace  │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                      REMEDIATION AGENT                       │
│ issue + evidence + repository tools + constrained objective  │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                       EVALUATION GATE                        │
│ tests · type checks · lint · BCA · mutation · semantic replay│
│ diff risk · new-rule scan · optional human adjudication      │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
                      ACCEPT / REJECT / LEARN
```

---

## 6. Core data model

The data model should preserve source provenance and distinguish observations, rules, detector implementations, findings and patch evaluations.

### 6.1 `SourceArtifact`

```yaml
source_artifact:
  id: globally-unique-id
  source_kind: review_comment | pr_description | issue | commit_message | code_comment
  repository_id: owner/repo or internal opaque id
  repository_commit: sha
  pull_request_id: optional
  parent_artifact_id: optional
  timestamp: ISO-8601
  language: optional
  file_path: optional
  line_start: optional
  line_end: optional
  text: raw text
  licence_context: dataset/repository licence metadata
  dataset: dataset name/version
```

Personally identifying metadata should be excluded from model inputs unless genuinely needed for research. Reviewer identity is normally unnecessary; repository diversity can be measured using pseudonymous IDs.

### 6.2 `CodeContext`

```yaml
code_context:
  artifact_id: source_artifact.id
  base_commit: sha
  review_commit: optional sha
  post_response_commit: optional sha
  before_code: exact or focused source
  diff_hunk: optional
  after_code: optional
  surrounding_symbols:
    - symbol name/type/path
  test_context:
    - changed tests
    - failing tests
    - relevant test files
```

### 6.3 `IssueObservation`

This is the principal output of semantic normalisation.

```yaml
issue_observation:
  id: unique-id
  source_artifact_id: ...
  schema_version: 1
  actionable_engineering_concern: true | false | uncertain
  issue_statement: concise, implementation-neutral statement
  coarse_category: correctness | maintainability | testing | ...
  fine_category: optional
  scope: expression | statement | function | class | file | module | repository
  generalisable: true | false | uncertain
  proposed_invariant: optional
  evidence_spans:
    - source line/range
  code_spans:
    - file + line/range
  exclusions:
    - known reasons the apparent pattern may be intentional
  normaliser_model:
    model_id: ...
    prompt_version: ...
    decoding_config: ...
  provenance:
    dataset: ...
    record_id: ...
```

### 6.4 `Rule`

```yaml
rule:
  id: ERR-014
  version: 3
  status: candidate | reviewed | validated | advisory | enforced | retired
  name: preserve-exception-causality
  level: global | organisation | repository
  statement: >
    Errors translated across an abstraction boundary should preserve
    sufficient diagnostic information about the original failure.
  applicability:
    positive_conditions: [...]
    negative_conditions: [...]
  violation_definition: ...
  counterexamples: [...]
  remediation_guidance: optional
  evidence_summary:
    observation_count: 83
    repositories: 14
    source_types: [...]
  validation:
    precision_estimate: optional
    recall_estimate: optional
    replay_set_version: ...
  detector_policy:
    preferred_detector: static | semantic | hybrid | agentic
    fallback_detector: optional
```

### 6.5 `RuleDetector`

A rule and its implementation must be separately versioned.

```yaml
rule_detector:
  id: ERR-014.semantic.local-v2
  rule_id: ERR-014
  rule_version: 3
  detector_type: semantic
  implementation_version: 2
  model_id: local-model-id
  context_builder_version: 4
  prompt_version: 6
  output_schema_version: 2
```

### 6.6 `RuleEvaluation`

```yaml
rule_evaluation:
  rule_id: ERR-014
  detector_id: ERR-014.semantic.local-v2
  applicable: true | false | uncertain
  violation: true | false | uncertain
  evidence:
    - file: ...
      start_line: ...
      end_line: ...
      rationale: ...
  explanation: bounded explanation
  execution_trace_id: ...
```

Avoid requesting an arbitrary `confidence: 0.93` from a generative LLM. If a confidence score is exposed, it should be a **system-derived reliability estimate**, e.g. calibrated on held-out data.

### 6.7 `Finding`

A finding combines rule evaluation with system evidence.

```yaml
finding:
  id: ...
  rule_evaluation_id: ...
  structural_features:
    cognitive_complexity: optional
    cyclomatic_complexity: optional
    loc: optional
    churn: optional
    ownership_dilution: optional
  corroborating_detectors: [...]
  contradiction_flags: [...]
  priority_bucket: low | medium | high
  disposition: open | dismissed | accepted | fixed
```

### 6.8 `PatchEvaluation`

```yaml
patch_evaluation:
  finding_id: ...
  patch_sha_or_diff: ...
  generated_by:
    agent: ...
    model: ...
  checks:
    build: pass | fail | unavailable
    tests: pass | fail | unavailable
    typecheck: pass | fail | unavailable
    lint: pass | fail | unavailable
    mutation: {...}
    bca_delta: {...}
    target_rule_after: pass | fail | uncertain
    new_rule_findings: [...]
  historical_patch_similarity:
    semantic: optional
    textual: optional
  disposition: accepted | rejected | needs_review
```

---

## 7. Source datasets and their roles

The system should not treat all public corpora as interchangeable.

### 7.1 GitHub Code Review dataset

The public dataset by Takizawa contains over 167,000 positive review-before/after triplets from 725 repositories, plus over 51,000 examples where no inline review was observed, spanning 37 languages [5].

Recommended use:

- primary high-volume review observation corpus;
- rule discovery;
- pre/post response studies;
- cross-language analysis.

Important caveat:

The dataset describes uncommented chunks as negatives. For this project they should be stored as **weak negatives**, not verified negatives. Human review is incomplete and selective.

### 7.2 CRC-Py

CRC-Py provides 16,711 Python review comments with diff context and coarse/fine labels [6].

Recommended use:

- initial Python PoC;
- taxonomy bootstrapping;
- supervised validation of issue categorisation;
- constructing strata for manual adjudication.

### 7.3 Multi-source SATD

Li, Soliman and Avgeriou's replication package combines code comments, commit messages, issues and pull requests, and labels debt types including code/design, requirement, documentation and test debt [7].

Recommended use:

- learning whether heterogeneous engineering prose contains an actionable concern;
- source-type robustness;
- code-comment ingestion design;
- comparing discovered taxonomy with established SATD categories.

SATD is narrower than general code review and should not define the full ontology.

### 7.4 Review4Repair

Review4Repair links natural-language review with before/after code and was built from 55,060 code-review examples [8], [9].

Recommended use:

- independent repair benchmark;
- testing whether review text improves patch generation;
- patch-evaluation methodology.

### 7.5 CodeReviewer

CodeReviewer explicitly separates code-review automation into:

- diff quality estimation;
- review-comment generation;
- code refinement.

Its public resources provide datasets for these tasks [10], [11].

Recommended use:

- external baseline;
- comparison with established review tasks;
- ablations around whether review language improves refinement.

### 7.6 SWE-bench

SWE-bench evaluates repository-level repair from real GitHub issue descriptions and corresponding fixes. The full benchmark contains 2,294 problems; SWE-bench Verified contains 500 engineer-validated solvable instances [12], [13].

Recommended use:

- downstream agent/harness validation;
- execution-backed patch acceptance;
- testing repository navigation and multi-file repair.

SWE-bench is **not** primarily a review-rule discovery dataset.

### 7.7 BugsInPy

BugsInPy provides reproducible real Python bugs with buggy/fixed versions and test suites; the published benchmark describes 493 bugs from 17 Python projects [14].

Recommended use:

- behavioural repair;
- test-based evaluation;
- Python-specific controlled experiments.

---

## 8. Evidence normalisation pipeline

### 8.1 Stage N0 — source filtering

Reject or separately label:

- bot-generated comments;
- formatting-only automation;
- pure social acknowledgements;
- duplicate quoted material;
- generated files;
- comments without resolvable code context when code context is required.

Do not discard non-code concerns prematurely: documentation, testing, observability and build/configuration issues may become useful rule families.

### 8.2 Stage N1 — actionable concern classification

Atomic question:

> Does this artefact express a specific engineering condition that could in principle be checked, improved, or verified?

Outputs:

```text
yes / no / uncertain
```

A separate question should assess whether the issue is **generalisable** beyond the exact historical change.

### 8.3 Stage N2 — canonical issue statement

Generate a short implementation-neutral statement.

Bad:

> Change line 43 to call `foo()`.

Better:

> The function bypasses the repository's canonical validation path.

### 8.4 Stage N3 — applicability and exclusions

Extract conditions under which the concern applies and obvious counterexamples.

This step is critical to avoiding broad, noisy rules.

### 8.5 Stage N4 — taxonomy assignment

Assign a coarse category, but permit `other` and multi-label output.

The taxonomy is descriptive metadata, not the rule itself.

### 8.6 Structured generation

The normaliser should produce JSON constrained by schema. llama.cpp can convert supported JSON Schema into a grammar and constrain generation [3].

Constrained syntax provides **format correctness**, not semantic correctness. Semantic validity remains an experimental question.

---

## 9. Pattern discovery and rule induction

### 9.1 Embed normalised observations, not raw comments

Raw review prose contains greetings, repo-specific identifiers, patch instructions and style variation.

Preferred embedding input:

```text
issue_statement
+ proposed_invariant
+ coarse category
+ optional minimal code signature
```

Sentence-transformer-style representations are a reasonable baseline because they are designed for efficient semantic similarity and clustering [15].

### 9.2 Cluster using a method that tolerates noise

Density-based clustering such as HDBSCAN is attractive because:

- the number of clusters need not be specified in advance;
- rare observations can remain noise;
- clusters of differing density can be represented [16].

The exact clustering method must be evaluated rather than assumed.

### 9.3 Candidate cluster quality

A candidate cluster should be ranked by more than frequency:

```text
cluster utility =
    prevalence
  × repository diversity
  × reviewer/source diversity
  × generalisability rate
  × response-to-review rate
  × semantic cohesion
```

Do not use this literal formula as ground truth; it represents the dimensions that should be retained separately.

### 9.4 Candidate rule synthesis

A stronger model/agent may transform a coherent cluster into:

- statement;
- applicability conditions;
- violation definition;
- counterexamples;
- remediation hints;
- candidate detector class.

The generated rule must then pass human or experimental validation before promotion.

---

## 10. Rule lifecycle

```text
candidate
   ↓
reviewed
   ↓
validated
   ↓
advisory
   ↓
enforced
```

Possible side transitions:

```text
candidate → rejected
reviewed → merged-with-existing
validated → revised
advisory → retired
enforced → rolled-back
```

### 10.1 Candidate

Machine-generated. Not surfaced to developers.

### 10.2 Reviewed

Definition inspected for coherence, scope and obvious counterexamples.

### 10.3 Validated

Passes held-out replay thresholds.

### 10.4 Advisory

May appear in reports/PR feedback but does not block.

### 10.5 Enforced

Only suitable for rules with very low false-positive cost, preferably deterministic or strongly corroborated.

---

## 11. Detector selection and rule compilation

Every validated semantic rule should be assessed for deterministic compilation.

### 11.1 Detector classes

#### A. Syntactic/static

Examples:

- bare `except`;
- swallowed exception;
- prohibited API;
- missing timeout on a known call;
- architectural dependency violation that can be expressed as an import rule.

#### B. Metric-assisted

Examples:

- extreme complexity hotspot;
- high-churn/high-complexity combination.

BCA provides complexity, Halstead, maintainability, ABC and LOC metrics, as well as VCS measures including churn, ownership dilution and bug-fix history [4].

Metric thresholds must not be interpreted as universal design truths.

#### C. Semantic local

Examples:

- misleading naming;
- missing rationale;
- premature abstraction;
- duplicated domain knowledge in nearby context.

#### D. Repository-context semantic

Examples:

- local architectural conventions;
- domain invariants;
- business concepts represented inconsistently.

#### E. Agentic/execution-backed

Examples:

- test claims to cover a failure but does not;
- behaviour only established by running code;
- multi-file state transition requiring exploration.

### 11.2 Compilation experiment

For each semantic rule with a measurable correlate:

1. collect positive and verified-negative examples;
2. compute candidate static/metric features;
3. fit interpretable baselines;
4. compare static, semantic and hybrid detectors;
5. promote to deterministic only if held-out performance is acceptable.

The goal is not to approximate every semantic rule with metrics. It is to discover where inference is unnecessary.

---

## 12. Role of `big-code-analysis`

BCA should be integrated in three places.

### 12.1 Feature extraction

Attach structural and historical features to observations:

- cyclomatic complexity;
- cognitive complexity;
- LOC;
- Halstead measures;
- maintainability index;
- ABC;
- churn;
- ownership dilution;
- bug-fix history.

### 12.2 Repair evaluation

Record before/after metric deltas for generated patches.

Example:

```text
cognitive complexity: 31 → 17
cyclomatic complexity: 19 → 10
```

A favourable delta is supporting evidence, not acceptance by itself.

### 12.3 Agent feedback

BCA provides threshold gating and examples of feedback loops for Claude Code and OpenCode [4]. The proposed system can use the same pattern:

```text
agent edit
   ↓
bca check
   ↓
violations returned to agent
```

### 12.4 Anti-gaming principle

Do not optimise directly for:

```text
minimise complexity
```

An agent could improve the number while worsening the design.

Instead:

```text
required:
    behaviour preserved
    target concern resolved
    no new critical findings

constraints:
    structural metrics do not materially regress

preference:
    relevant structural metrics improve
```

---


## Model-routing subsystem

Model selection is a reusable infrastructure concern rather than application logic.

The system should use the abstractions defined in `10_MODEL_ROUTING_SUBSYSTEM_DESIGN.md`:

```text
ModelInventory
TaskRequirements
RoutingPolicy
RoutingDecision
RoutingPolicyTransition
AgentHandoff
ProviderHealth
BudgetConstraint
ContextStrategy
```

Research-domain entities must not hard-code model names.

A project resolves routing through:

```text
invocation override
→ task override
→ project default
→ system default
```

Hard constraints such as local-only privacy, provider availability, required tool support and minimum context filter the inventory before soft preferences such as cost, latency and reviewer independence are applied.

A mid-task policy switch must be recorded as a transition rather than silently replacing the route.

The context builder is model-independent and must be able to rebuild a task context when the selected model or policy changes.


## 13. Local inference architecture

### 13.1 Model roles

Use separate roles rather than one universal model.

#### Small/medium semantic worker

Used for:

- concern classification;
- canonical issue generation;
- rule applicability;
- bounded rule checking.

Characteristics:

- high throughput;
- structured output;
- modest context;
- quantised local execution.

#### Embedding model

Used for:

- duplicate detection;
- clustering;
- nearest-neighbour retrieval;
- candidate example selection.

#### Larger coding/reasoning worker

Used for:

- candidate rule synthesis;
- counterexample generation;
- repository-context analysis;
- patch generation.

#### Optional independent judge

Used only as a secondary signal in evaluation, never as the sole behavioural oracle.

### 13.2 Model API

Define an internal OpenAI-compatible or simple HTTP abstraction so engines can be exchanged:

```text
POST /normalise-observation
POST /evaluate-rule
POST /synthesise-rule
POST /generate-counterexamples
```

The system should be independent of Ollama, llama.cpp, vLLM or any specific serving layer.

### 13.3 Context construction

For rule checks, provide the **minimum sufficient context**:

```text
rule
+ target code
+ relevant imports/types/callers
+ repository-specific rule context if needed
```

Do not dump the entire repository into every request.

Repository retrieval must itself be versioned so detector changes can be attributed correctly.

---

## 14. Remediation-agent contract

The remediation agent should receive a bounded task:

```yaml
finding:
  rule: ERR-014
  statement: ...
  evidence: ...
  applicability: ...
constraints:
  - preserve externally observable behaviour except where the finding requires change
  - do not weaken or delete tests to obtain a pass
  - minimise unrelated changes
required_validation:
  - repository tests
  - target rule re-evaluation
  - static checks
```

The agent should not receive the historical human patch during normal evaluation.

It may use:

- repository search;
- tests;
- static tools;
- BCA;
- mutation testing;
- compiler/type checker;
- local documentation.

---

## 15. Patch evaluation architecture

Patch evaluation should be layered.

### Gate 1 — repository validity

- patch applies;
- code parses/builds;
- formatting/type checks/lint pass where available.

### Gate 2 — behavioural validity

- previously passing tests remain passing;
- issue-specific tests pass;
- failing-to-passing tests improve where known.

SWE-bench provides a mature pattern: checkout the repository environment, apply the patch and run designated tests [12], [13].

### Gate 3 — target-rule resolution

Re-run the exact detector version that produced the finding.

### Gate 4 — regression scan

Run:

- other high-maturity rules in changed scope;
- static/structural checks;
- dependency rules.

### Gate 5 — mutation testing where appropriate

For behavioural changes, mutation testing can test whether added/changed tests meaningfully constrain the affected behaviour.

Mutation score is not universally applicable and should not gate documentation-only or purely structural refactoring.

### Gate 6 — structural deltas

Record BCA metrics and flag pathological movements.

### Gate 7 — optional semantic comparison

Ask an independent detector whether:

- target concern remains;
- patch introduces a new concern;
- patch takes an implausibly indirect route.

This is supporting evidence only.

---

## 16. Public-to-internal adaptation model

Keep three rule namespaces.

### 16.1 Global rules

Derived from public data and broadly applicable engineering practice.

### 16.2 Organisation rules

Repeated patterns across an organisation's repositories.

### 16.3 Repository rules

Local architecture, conventions or domain invariants.

This permits a clean incremental-value study:

```text
generic rules → performance A

generic + organisation rules → performance B

generic + organisation + repository rules → performance C
```

Then:

- `B - A` estimates the contribution of organisation-specific knowledge;
- `C - B` estimates additional repository-specific value.

These are empirical comparisons, not assumed benefits.

---

## 17. Security, privacy and licensing

### 17.1 Public-data phase

Record:

- dataset licence;
- repository source licence;
- whether redistribution of derived text/code is permitted;
- dataset version/hash.

Do not assume permissively licensed repositories automatically settle every dataset redistribution or model-training question.

### 17.2 Internal phase

Recommended controls:

- local inference by default;
- no source code sent to public endpoints;
- pseudonymise reviewer/developer identity;
- strip credentials/secrets before persistence;
- separate raw evidence from derived observations;
- audit every prompt/context materialised to a model;
- configurable retention.

### 17.3 Prompt injection

Repository text is untrusted input to an agent.

Comments, READMEs and test fixtures may contain instructions. The agent must treat repository content as **data**, not authority. Tool permissions should be bounded independently of model instructions.

---

## 18. Observability and reproducibility

Every model-dependent operation should record:

- dataset record ID;
- exact source revision;
- model identifier/hash;
- quantisation;
- inference engine/version;
- prompt template version;
- schema version;
- sampling configuration;
- context-builder version;
- retrieved files/spans;
- raw structured output;
- wall time;
- token counts if available.


### Model-routing telemetry

In addition to reproducibility metadata, every model invocation should retain:

- routing-policy version and task class;
- selected model/provider and escalation path;
- provider/runtime-reported token usage where available;
- cached-input and reasoning-token usage where exposed;
- versioned estimated spend;
- provider-reported spend where available;
- queue, first-token, generation and total turnaround timings;
- outcome.

Live operational state belongs in SQLite; completed analytical usage history belongs in Parquet/DuckDB.

The purpose is operational analysis, not creation of a coding-model benchmark programme.

Every experiment should be reproducible from a manifest.

Example:

```yaml
experiment:
  id: replay-2026-09-001
  dataset: crc-py
  dataset_version: git-sha
  split_manifest: splits/v3.json
  normaliser: normaliser-v5
  rule_set: rules-2026-09-15
  detector_set: detectors-v8
  inference:
    engine: llama.cpp
    version: ...
    model: ...
    quantisation: ...
```

---

## 19. Suggested implementation components

A pragmatic Python-first PoC:

```text
Python orchestration
├── ingestion/
├── provenance/
├── normalisation/
├── embeddings/
├── clustering/
├── rules/
├── detectors/
│   ├── static/
│   ├── semantic/
│   └── agentic/
├── context/
├── agents/
├── evaluation/
├── experiments/
└── reports/
```

Supporting tools:

- SQLite/DuckDB or Postgres for metadata;
- Parquet for large observation/features tables;
- Git worktrees/containers for historical replay;
- local inference server;
- BCA CLI or Python bindings;
- existing repository test toolchain;
- optional mutation-testing adapters.

Do not introduce a vector database until corpus size or serving requirements justify it. For early research, embeddings in Parquet plus FAISS/NumPy-compatible indexing are sufficient.

---

## 20. API boundaries

### `ObservationNormaliser`

```python
normalise(source_artifact, code_context) -> IssueObservation
```

### `RuleMiner`

```python
cluster(observations) -> list[ObservationCluster]
synthesise(cluster) -> RuleCandidate
```

### `Detector`

```python
evaluate(rule, code_context) -> RuleEvaluation
```

### `RemediationAgent`

```python
repair(finding, repository_workspace) -> Patch
```

### `PatchEvaluator`

```python
evaluate(patch, finding, repository_workspace) -> PatchEvaluation
```

This separation allows components to be benchmarked or replaced independently.

---

## 21. Key failure modes and mitigations

### 21.1 Reviewer-selection bias

**Failure:** only commented code is observed as problematic.

**Mitigation:** weak/verified-negative distinction; manual negative adjudication; counterexample sets.

### 21.2 Repository leakage

**Failure:** same project patterns appear in train and test.

**Mitigation:** repository-level splits; no random row split for headline results.

### 21.3 Foundation-model contamination

**Failure:** model may have seen public repository code or benchmark patches during pretraining.

**Mitigation:** held-out newer repositories where possible; compare code-free issue classification; evaluate on later internal data; report contamination as a threat rather than claiming pure generalisation.

### 21.4 Patch memorisation

**Failure:** agent reproduces a known public fix.

**Mitigation:** behavioural evaluation remains useful, but do not interpret public-benchmark performance alone as proof of reasoning; use unseen/internal replication later.

### 21.5 Metric gaming

**Failure:** agent optimises BCA metrics while harming design.

**Mitigation:** metrics are constraints/evidence, not sole objective; scan for semantic regressions.

### 21.6 Rule over-generalisation

**Failure:** cluster synthesis creates a broad slogan instead of a falsifiable condition.

**Mitigation:** mandatory applicability conditions and counterexamples; replay precision gate.

### 21.7 LLM self-confidence misuse

**Failure:** generated probability-like values are treated as calibrated confidence.

**Mitigation:** system-derived reliability using held-out calibration and detector history.

### 21.8 Rule duplication

**Failure:** many near-identical rules create noisy review.

**Mitigation:** embedding-based duplicate search plus explicit supersedes/merges relationships.

### 21.9 Historical fix as false oracle

**Failure:** alternative correct patches are scored wrong.

**Mitigation:** behaviour and invariants outrank textual patch similarity.

---

## 22. Recommended PoC scope

Start with **Python** and public datasets.

Recommended first scope:

- CRC-Py for labelled review taxonomy;
- a Python subset of the larger GitHub review corpus;
- SATD multi-source data;
- BugsInPy and selected SWE-bench Verified cases for execution-backed repair;
- BCA for structural features/evaluation.

Initial target:

- 500–2,000 high-quality review observations for manual study;
- top 10–20 recurring candidate rules;
- 5–10 validated rules;
- at least three detector classes represented:
  - deterministic;
  - semantic;
  - hybrid.

Do not fine-tune a model in the first phase.

---

## 23. Definition of success

A successful first system is **not** one that produces many comments.

It should demonstrate that:

1. actionable review concerns can be normalised reliably;
2. recurring concerns form coherent, reusable rules;
3. held-out repositories can be checked with useful precision;
4. some semantic rules can be compiled into cheaper deterministic detectors;
5. a coding agent can repair a useful subset of detected issues;
6. behavioural validation rejects superficially plausible but incorrect changes;
7. the process is reproducible and every rule/finding has provenance.

The experimental plan in the companion document defines concrete hypotheses, datasets, splits, metrics and decision gates.

---

# References

[1] Alurith, “jeff: Catch code issues before they catch you,” GitHub repository, 2026. [Online]. Available: https://github.com/Alurith/jeff. [Accessed: Sep. 19, 2026].

[2] TypeSafe AI, “Introduction — Jev and TypeSafe primitives,” TypeSafe AI Documentation, 2026. [Online]. Available: https://docs.typesafe.ai/introduction. [Accessed: Sep. 19, 2026].

[3] ggml-org, “llama.cpp grammars: JSON Schemas to GBNF,” GitHub repository documentation, 2026. [Online]. Available: https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md. [Accessed: Sep. 19, 2026].

[4] dekobon, “big-code-analysis: Tool to report source code metrics,” GitHub repository, 2026. [Online]. Available: https://github.com/dekobon/big-code-analysis. [Accessed: Sep. 19, 2026].

[5] R. Takizawa, “GitHub Code Review Dataset,” Hugging Face Datasets, 2026. [Online]. Available: https://huggingface.co/datasets/ronantakizawa/github-codereview. [Accessed: Sep. 19, 2026].

[6] B. Icoz, “CRC-Py Dataset: Public Dataset of Python Code Review Comments Labeled with an ESEM'23 Taxonomy,” GitHub repository. [Online]. Available: https://github.com/busraicoz/crc-py-dataset. [Accessed: Sep. 19, 2026].

[7] Y. Li, M. Soliman, and P. Avgeriou, “Replication Package for Automatic Identification of Self-Admitted Technical Debt from Four Different Sources,” GitHub repository. [Online]. Available: https://github.com/yikun-li/satd-different-sources-data. [Accessed: Sep. 19, 2026].

[8] F. Huq, M. Hasan, M. A. H. Pantho, S. Mahbub, A. Iqbal, and T. Ahmed, “Review4Repair: Code review aided automatic program repairing,” *Information and Software Technology*, vol. 143, Art. no. 106765, Mar. 2022, doi: 10.1016/j.infsof.2021.106765.

[9] Review4Repair, “Review4Repair dataset and source code,” GitHub repository. [Online]. Available: https://github.com/Review4Repair/Review4Repair. [Accessed: Sep. 19, 2026].

[10] Z. Li *et al*., “Automating code review activities by large-scale pre-training,” in *Proc. 30th ACM Joint European Software Engineering Conf. and Symp. on the Foundations of Software Engineering (ESEC/FSE)*, 2022, pp. 1035–1047, doi: 10.1145/3540250.3549081.

[11] “Automating Code Review Activities by Large-Scale Pre-training — datasets and source code,” Zenodo, 2022. [Online]. Available: https://zenodo.org/records/6900648. [Accessed: Sep. 19, 2026].

[12] C. E. Jimenez, J. Yang, A. Wettig, S. Yao, K. Pei, O. Press, and K. Narasimhan, “SWE-bench: Can Language Models Resolve Real-World GitHub Issues?” arXiv:2310.06770, 2023. [Online]. Available: https://arxiv.org/abs/2310.06770.

[13] SWE-bench, “Datasets,” 2026. [Online]. Available: https://www.swebench.com/SWE-bench/guides/datasets/. [Accessed: Sep. 19, 2026].

[14] R. Widyasari *et al*., “BugsInPy: A Database of Existing Bugs in Python Programs to Enable Controlled Testing and Debugging Studies,” in *Proc. 28th ACM Joint Meeting on European Software Engineering Conf. and Symp. on the Foundations of Software Engineering (ESEC/FSE)*, 2020, doi: 10.1145/3368089.3417943. [Online]. Available: https://arxiv.org/abs/2401.15481.

[15] N. Reimers and I. Gurevych, “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks,” in *Proc. 2019 Conf. on Empirical Methods in Natural Language Processing and 9th Int. Joint Conf. on Natural Language Processing (EMNLP-IJCNLP)*, Hong Kong, 2019, pp. 3982–3992, doi: 10.18653/v1/D19-1410.

[16] R. J. G. B. Campello, D. Moulavi, A. Zimek, and J. Sander, “Hierarchical density estimates for data clustering, visualization, and outlier detection,” *ACM Trans. Knowledge Discovery from Data*, vol. 10, no. 1, Art. no. 5, 2015, doi: 10.1145/2733381.



## Double-Entry Review for material software changes

The factory uses Double-Entry Review (DER) for **material PRs/changes inside vertical slices**.
It is not applied automatically to every edit and a vertical slice is not itself a DER pair.

The project-specific materiality policy and integration contract are defined in
`11_DOUBLE_ENTRY_REVIEW_INTEGRATION.md`.

For a material change:

```text
actual implementation chronology
        ↓
DER diary
        ↓
verified frozen result
        ↓
proposition-led semantic history
        ↓
checkpoint-local evidence
        ↓
review round
```

Multiple implementation agents may operate concurrently, but one history integrator owns the
canonical pair. DER evidence is stored outside application worktrees and referenced by the
harness.

DER semantic history must not be confused with the semantic-review product. The latter may
contribute findings to DER review but is never approval authority.

The factory records DER revision readiness separately from programme/slice status.
