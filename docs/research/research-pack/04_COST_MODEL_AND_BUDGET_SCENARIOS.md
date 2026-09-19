# Cost Model and Budget Scenarios

**Companion to:**  
- `01_SYSTEM_DESIGN.md`  
- `02_EXPERIMENTAL_PLAN.md`  
- `03_LOCAL_DATASET_STORAGE.md`

**Purpose:** Identify where the evidence-grounded semantic code-review research programme is likely to incur incremental costs, provide assumption-driven budget scenarios, and define controls that prevent compute-heavy stages from dominating the programme.

**Pricing reference date:** 19 September 2026.  
All external prices in this document are **dated examples**, not forecasts. Recalculate them before committing budget.

In this document, `Phase 0–5` refers to the research phases in `02_EXPERIMENTAL_PLAN.md`, not implementation vertical slices.

---

## 1. Executive summary

Most of the proposed programme can be executed locally using public datasets and existing workstation hardware.

The cost profile is strongly asymmetric:

```text
cheap, broad stages
    dataset ingestion
    normalisation
    embeddings
    clustering
    candidate rule mining
    static/BCA feature extraction

expensive, narrow stages
    repository reconstruction
    agentic repair
    repeated test execution
    mutation testing
    human adjudication
    large-model/cloud escalation
```

The largest likely costs are therefore not dataset acquisition. They are:

1. **people time**, especially independent adjudication;
2. **execution-heavy validation**, especially mutation testing;
3. **large-scale agentic repair**, if many attempts are run;
4. **cloud GPU capacity**, if local throughput becomes insufficient;
5. **additional SSD capacity**, if repository/build caches are allowed to grow.

A sensible strategy is to let cheap stages aggressively reduce the number of examples that reach expensive ones.

With existing capable local hardware, a meaningful Phase 0–3 public-data feasibility study can plausibly incur **little direct external infrastructure spend beyond possible storage expansion**. The largest jump in cost is expected at Phase 4, where repository execution, repeated agent attempts and mutation testing become routine.

---

## 2. Cost categories

### 2.1 Dataset acquisition

Most datasets discussed in the research plan are publicly downloadable without a data-access charge.

Expected incremental cost:

```text
£0 data licence/download fee
```

subject to normal internet connectivity and any future change in dataset availability/licensing.

Potential indirect costs:

- storage;
- backup;
- data preparation;
- legal/licensing review.

---

## 3. Local storage

The structured datasets themselves are small relative to repositories, models and execution caches.

See `03_LOCAL_DATASET_STORAGE.md` for the detailed storage strategy.

### Likely one-off cost

If existing storage is sufficient:

```text
£0
```

If additional fast NVMe storage is required, treat it as a one-off capital cost rather than an experiment-level variable cost.

The project should therefore keep storage in the budget model as:

```text
C_storage = purchase cost of additional storage actually required
```

Do not assign an artificial per-GB charge to storage already owned.

---


## 4. Cloud GPU reference prices

RunPod's September 2026 pricing material lists representative hourly rates including the following [1], [3]:

| GPU | VRAM | Secure Cloud |
|---|---:|---:|
| RTX A5000 | 24 GB | $0.27/h |
| RTX 4090 | 24 GB | $0.74/h |
| A40 | 48 GB | $0.49/h |
| RTX A6000 | 48 GB | $0.53/h |
| L40S | 48 GB | $1.09/h |
| A100 PCIe | 80 GB | $1.59/h |
| H100 PCIe | 80 GB | $2.89/h |
| H100 SXM | 80 GB | $3.49/h |
| H200 | 141 GB | $4.59/h |

These rates are provider- and availability-dependent and should not be treated as guaranteed future prices.

### Formula

```text
C_cloud_gpu =
    GPU_hours
  × hourly_rate
  + persistent_volume_cost
  + data-egress_cost, if any
```

For this project, persistent cloud volumes should normally be avoided by copying only the minimum experiment bundle into temporary workers.

---

## 5. Cloud GPU examples

At September 2026 RunPod rates:

### 100 GPU-hours

| GPU | Approx. cost |
|---|---:|
| RTX 4090 | $74 |
| A100 PCIe | $159 |
| H100 PCIe | $289 |

### 500 GPU-hours

| GPU | Approx. cost |
|---|---:|
| RTX 4090 | $370 |
| A100 PCIe | $795 |
| H100 PCIe | $1,445 |

### 1,000 GPU-hours

| GPU | Approx. cost |
|---|---:|
| RTX 4090 | $740 |
| A100 PCIe | $1,590 |
| H100 PCIe | $2,890 |

This makes cloud capacity entirely plausible for targeted experiments, but expensive if it becomes the default for bulk work that could run locally.

---

## 6. Hosted LLM/API cost

Hosted APIs should be treated as an optional escalation path or benchmark, not a required dependency.

For a current high-end reference point, OpenAI lists GPT-5.6 Sol at **$4 per million uncached input tokens and $20 per million output tokens** under its current promotional pricing [2].

### Formula

```text
C_API =
    input_tokens_M × input_price_per_M
  + output_tokens_M × output_price_per_M
  + tool charges where applicable
```

### Example: rule evaluation

Suppose one evaluation uses:

```text
4,000 input tokens
300 output tokens
```

At the cited GPT-5.6 Sol rates:

```text
input  = 0.004 × $4  = $0.016
output = 0.0003 × $20 = $0.006

total ≈ $0.022 per evaluation
```

Then:

| Evaluations | Approx. API cost |
|---:|---:|
| 1,000 | $22 |
| 10,000 | $220 |
| 100,000 | $2,200 |

This demonstrates why API use is cheap for small benchmark samples but can become significant for corpus-wide repeated experiments.

Local inference removes the token fee but trades it for elapsed compute time.

---

## 7. Embedding cost

Embeddings are likely to be inexpensive if generated locally.

The main cost is:

```text
one-time local compute
+ storage
```

Embeddings should normally be generated once per model/version and cached.

Repeated re-embedding caused by unnecessary schema or text changes should be avoided.

Store:

```text
embedding_model
model_revision
source_text_hash
vector
```

so an unchanged record can reuse its vector.

---

## 8. Static and BCA analysis

Static/AST analysis and `big-code-analysis` feature extraction should be very low-cost relative to LLM inference.

Expected cost:

- local CPU time;
- disk I/O;
- negligible marginal cash cost.

This is a strong reason to push mature rules toward deterministic implementation where practical.

---

## 9. Repository acquisition and replay

Repository replay introduces:

- clone/fetch bandwidth;
- disk usage;
- dependency installation;
- compilation;
- test execution;
- historical checkout management.

The repository itself may be inexpensive; reconstructing a runnable environment is often the costly step.

### Cost-control rule

Do not reconstruct a repository merely because a dataset record exists.

Preferred funnel:

```text
all observations
      ↓
semantic/static analysis
      ↓
validated/high-value cases
      ↓
repository reconstruction
```

This avoids paying execution cost for low-quality candidate cases.

---

## 10. Container and environment costs

Locally:

```text
cash cost ≈ storage expansion, if required
```

Cloud:

```text
environment setup time consumes billable GPU/CPU hours
```

For GPU workers, avoid spending expensive GPU time performing tasks that can be done on CPU:

- Git checkout;
- dependency download;
- preprocessing;
- dataset conversion.

Prepare artefacts first and start GPU billing as late as possible.

---

## 11. Human adjudication

Human time is likely to be the most economically valuable scarce resource in the early research programme.

### Formula

For:

- `N` examples;
- `t` minutes/example;
- `R` independent raters;
- fully loaded labour rate `H` £/hour;

```text
hours = N × t × R / 60

C_human = hours × H
```

### Example

500 examples:

```text
5 minutes/example
2 independent raters
```

requires:

```text
500 × 5 × 2 / 60
= 83.3 person-hours
```

Illustrative opportunity costs:

| Fully loaded rate | Approx. cost |
|---:|---:|
| £50/h | £4,167 |
| £75/h | £6,250 |
| £100/h | £8,333 |

These are deliberately illustrative labour rates, not assumptions about actual salaries or contractor prices.

### Consequence

Improving annotation efficiency can save more money than optimising inference.

Use:

- good annotation UI;
- precomputed code context;
- balanced sampling;
- active learning/hard-example selection;
- reconciliation only where needed.

---

## 12. Mutation testing

Mutation testing is the stage most likely to create a large compute multiplier.

If:

```text
T = selected-test runtime
M = number of mutants
```

a naïve upper bound resembles:

```text
T × M
```

although selection, parallelism, mutant filtering and early termination can reduce this substantially.

This is why mutation testing should be:

- change-triggered;
- targeted;
- applied after cheaper gates;
- reserved for behavioural changes where it adds evidence.

### Funnel

```text
candidate patch
    ↓
build/type/lint
    ↓
ordinary relevant tests
    ↓
semantic/static re-evaluation
    ↓
targeted mutation
```

Never run mutation testing first.

---

## 13. Agentic repair cost

Agentic repair can consume considerably more inference than atomic rule checking because it may perform:

- repository searches;
- repeated context reads;
- multiple model turns;
- test runs;
- retries;
- patch revisions.

Track cost per **attempt**, not merely tokens per request.

Recommended metrics:

```text
agent attempts / accepted patch
GPU-hours / accepted patch
API £/$ / accepted patch
test minutes / accepted patch
```

This provides a useful economic measure:

```text
cost per behaviourally accepted improvement
```

---

## 14. Scenario A — local-only feasibility study

### Objective

Validate Phases 0–3 using existing workstation hardware.

### Workload

Illustrative:

- download/store public datasets;
- normalise 10k–50k observations;
- embed corpus;
- cluster observations;
- synthesise 10–20 rules;
- run historical replay;
- limited manual adjudication;
- no large-scale mutation campaign;
- only small repair pilot.

### Incremental cash costs

Likely:

| Item | Range |
|---|---:|
| Dataset fees | £0 |
| Cloud GPU | £0 |
| Hosted API | £0 |
| Additional storage | £0 if existing capacity sufficient |
| Human adjudication | organisation-dependent |
| Total infrastructure | typically low |

### Character

This should be the default initial configuration.

The principal economic cost is staff time, not compute.

---

## 15. Scenario B — hybrid local/cloud experiment

### Objective

Keep bulk processing local but use cloud GPUs for:

- large-model rule synthesis;
- difficult semantic cases;
- agentic repair batches;
- faster experimental turnaround.

### Illustrative workload

```text
local:
    normalisation
    embeddings
    clustering
    static/BCA
    most rule evaluation

cloud:
    100–300 A100 GPU-hours
```

At the September 2026 RunPod A100 PCIe reference rate of $1.59/h [1]:

```text
100 h ≈ $159
300 h ≈ $477
```

Add:

- modest storage/transfer;
- human adjudication.

### API benchmark allowance

For occasional frontier-model comparison, a fixed experiment allowance of:

```text
$100–$500
```

would support thousands to tens of thousands of bounded evaluations depending on token usage and model selection.

This is a budget envelope, not a recommendation to spend it.

### Character

Likely the best configuration if local throughput becomes inconvenient but data/privacy permits cloud use.

---

## 16. Scenario C — larger-scale public research programme

### Objective

Run broad repair/replay experiments across many repositories and multiple model/detector configurations.

Illustrative workload:

- multiple normaliser variants;
- several embedding/clustering experiments;
- dozens of rules;
- hundreds/thousands of reconstructed repositories/cases;
- repeated agent repair attempts;
- targeted mutation testing;
- several GPU model variants.

### Example cloud envelope

Suppose:

```text
1,000 A100 GPU-hours
```

At $1.59/h:

```text
≈ $1,590
```

or:

```text
500 A100 hours + 250 H100 PCIe hours
```

gives approximately:

```text
$795 + $722.50
= $1,517.50
```

before storage/transfer.

The infrastructure bill remains potentially modest relative to hundreds of hours of expert human review.

### Character

At this scale, orchestration and cache discipline matter more than individual GPU prices.

---

## 17. Scenario D — internal pilot/deployment

An internal pilot introduces costs that the public feasibility study does not:

- secure compute;
- CI runners;
- artifact storage;
- access-control/audit infrastructure;
- operational monitoring;
- engineering support;
- ongoing model/rule maintenance.

If the system evaluates every PR, cost should be modelled per PR:

```text
C_PR =
    static_compute
  + semantic_checks
  + repository-context retrieval
  + optional agent repair
  + validation execution
```

The design should avoid running expensive remediation automatically on every advisory finding.

A better deployment shape:

```text
static checks        → always
cheap semantic rules → always/advisory
large-model analysis → selected findings
agent repair         → explicit request / high-value case
mutation testing     → behaviourally relevant accepted candidate
```

---

## 18. Cost funnel

A core architectural objective should be to shrink the candidate population before each expensive stage.

Example:

```text
100,000 source observations
        ↓ cheap normalisation
 20,000 actionable
        ↓ deduplication/clustering
  2,000 representative cases
        ↓ rule synthesis
     50 candidate rules
        ↓ replay
     10 validated rules
        ↓ targeted findings
    500 repair candidates
        ↓ cheap validation
    150 execution candidates
        ↓ tests
     50 mutation-worthy cases
```

Numbers are illustrative, but the architecture is intentional.

---

## 19. Cost controls by stage

### Ingestion

- download once;
- hash/version locally.

### Normalisation

- batch requests;
- use smaller model;
- constrain outputs;
- cache by input hash.

### Embeddings

- compute once per model/revision;
- never silently regenerate.

### Rule synthesis

- use representative examples rather than entire clusters;
- reserve stronger model for this stage.

### Historical replay

- snippet-level first;
- reconstruct repository only when necessary.

### Agent repair

- limit retry count;
- set wall-clock/token budget;
- terminate when cheap validation fails.

### Tests

- run targeted tests before full suite.

### Mutation

- change-based scope;
- test selection;
- mutant pruning;
- hard compute ceiling.

### Cloud

- ephemeral workers;
- auto-shutdown;
- no idle GPU notebooks/pods;
- pre-stage data.

---

## 20. Cost telemetry

Every experiment should collect enough telemetry to answer:

```text
what did this result cost?
```

Recommended fields:

```yaml
cost:
  local_compute_hours:
  cloud_gpu:
    type:
    hours:
    provider_cost:
  api:
    input_tokens:
    output_tokens:
    cost:
  execution:
    test_cpu_minutes:
    mutation_cpu_minutes:
  human:
    annotation_minutes:
    reconciliation_minutes:
```

Then calculate:

- cost per observation normalised;
- cost per validated rule;
- cost per true finding;
- cost per attempted repair;
- cost per behaviourally accepted repair.

---

## 21. Cost-aware experimental metrics

Model/detector comparisons should not use accuracy alone.

Useful measures:

```text
precision per £
true findings per GPU-hour
accepted repairs per GPU-hour
accepted repairs per £
human-review minutes per validated rule
```

A smaller model with slightly worse recall may be operationally superior if it has similar precision and substantially greater throughput.

---

## 22. When cloud use is justified

Cloud GPU use is sensible when one or more of these apply:

1. the required model does not fit/usefully run on local hardware;
2. experiment turnaround is blocking research progress;
3. high parallelism is temporarily required;
4. a short burst is cheaper than buying hardware;
5. benchmark comparability requires a specific GPU/runtime.

Cloud should not be the default merely because it is easy to start.

---

## 23. When purchasing additional hardware is justified

Consider hardware acquisition only after measuring sustained demand.

A simple break-even approximation:

```text
break_even_hours =
    incremental_hardware_cost
    / equivalent_cloud_cost_per_hour
```

Then adjust for:

- utilisation;
- maintenance;
- useful lifetime;
- model-size constraints;
- convenience.

For intermittent research, renting is often economically preferable.

For continuous high-utilisation workloads, ownership may become attractive.

---

## 24. Human-time optimisation

Because expert adjudication is expensive, prioritise tooling here.

Potential investments:

- review UI with diff + source context;
- keyboard shortcuts;
- pre-filled model suggestion that can be accepted/edited;
- disagreement highlighting;
- automated duplicate detection;
- uncertainty sampling;
- representative cluster sampling.

Measure:

```text
median annotation seconds/example
```

and:

```text
reconciliation fraction
```

before and after UI/process changes.

---

## 25. Recommended initial budget posture

For the first meaningful PoC:

### Required

- existing workstation;
- local storage already available;
- public datasets;
- staff time.

### Optional contingency

- modest SSD upgrade;
- ≤100–300 cloud GPU-hours;
- small hosted-model benchmark allowance.

### Avoid initially

- dedicated cloud cluster;
- persistent paid GPU workers;
- large API corpus runs;
- mass repository reconstruction;
- exhaustive mutation testing;
- fine-tuning.

---

## 26. Recommended budget gates

### Gate C1 — before cloud GPU

Demonstrate that local throughput is actually a bottleneck.

### Gate C2 — before hosted API at scale

Demonstrate that the API materially improves quality over local models on a representative sample.

### Gate C3 — before large repository replay

Demonstrate useful rule precision on snippet/history replay.

### Gate C4 — before mutation testing at scale

Demonstrate that ordinary tests + rule re-evaluation leave meaningful uncertainty mutation testing can resolve.

### Gate C5 — before buying hardware

Collect at least several weeks of actual GPU utilisation and cloud demand.

---

## 27. Indicative scenario comparison

| Scenario | External infrastructure spend | People-time | Best use |
|---|---|---|---|
| Local-only | Very low | Moderate | Feasibility, E1–E6 |
| Hybrid local/cloud | Low–moderate | Moderate | Faster synthesis/repair experiments |
| Large public programme | Moderate | High | Broad replay and repair validation |
| Internal pilot | Moderate and recurring | High | Operational validation |
| Production service | Workload-dependent | Ongoing | Only after economic value established |

The strongest conclusion is that **people-time is likely to dominate early research economics**, while compute becomes more important only after the system reaches repository execution and automated repair.

---

## 28. Recommended strategy

The cost-efficient architecture is:

```text
LOCAL + CHEAP
    datasets
    filtering
    normalisation
    embeddings
    clustering
    static analysis
    BCA
    most semantic rule checks

        ↓ only promising cases

EXPENSIVE
    stronger model
    repo reconstruction
    repair agent
    tests
    mutation
    human adjudication
```

This aligns economic cost with evidential value.

The programme should not attempt to minimise spend at the expense of valid evaluation. Instead, it should avoid using expensive evidence where cheaper evidence has already ruled a candidate out.

---


## Model usage cost accounting

The harness should estimate hosted-model spend from actual token usage and a **versioned price catalogue**.

For every invocation retain:

```text
provider/model
input tokens
cached input tokens
output tokens
reasoning tokens where exposed
price-catalog version
estimated cost
provider-reported cost if available
```

Historical estimates must not be silently recomputed when provider prices change.

For local models, record zero API spend and preserve compute/turnaround telemetry rather than inventing an electricity or hardware-amortisation charge.

The primary live UI should show only a concise spend estimate. Detailed cost analysis belongs in the analytical drill-down and later programme reports.



## Routing-aware budgets

Budgets should be expressible as routing constraints rather than informal guidance.

Supported scopes should include:

```text
invocation
task
agent run
project/day
```

A `BudgetConstraint` may be soft or hard.

Hard budget constraints can make an otherwise preferred model ineligible.

Soft budgets may cause the router to prefer a cheaper eligible route.

A policy switch must not reset accumulated spend for the logical task/agent run.

Provider failures and model-quality escalations must be distinguished in cost analysis: retrying after a provider outage is infrastructure overhead, while escalating after a semantic failure is a routing-quality event.



## Double-Entry Review overhead

DER adds preparation/reconstruction/review work for material changes. Before DER 1.0 the project
therefore limits mandatory DER to material/critical changes rather than all non-trivial work.

The harness may record existing operational telemetry against DER activity:

- elapsed preparation/reconstruction/review time;
- model input/output tokens;
- estimated/provider spend;
- revision-round count.

These measurements are observational and should inform later materiality-policy refinement. They
are not correctness/readiness criteria and should not become a model/method benchmarking stream.


# References

[1] RunPod, “What an AI Server Costs: Buy Price vs Rental Price Guide,” updated Sep. 13, 2026. [Online]. Available: https://www.runpod.io/articles/guides/ai-server-cost. [Accessed: Sep. 19, 2026].

[2] OpenAI, “GPT-5.6 Sol Model,” OpenAI API Documentation, 2026. [Online]. Available: https://developers.openai.com/api/docs/models/gpt-5.6-sol. [Accessed: Sep. 19, 2026].

[3] RunPod, “GPU Cloud Pricing,” updated Sep. 13, 2026. [Online]. Available: https://www.runpod.io/pricing. [Accessed: Sep. 19, 2026].
