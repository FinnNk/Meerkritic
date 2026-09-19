# Coding-Agent Model Routing Policy

> **Architecture note:** This document contains concrete policy recommendations for the first two model inventories. The reusable routing architecture is defined in `10_MODEL_ROUTING_SUBSYSTEM_DESIGN.md`. Concrete model names in this document must not leak into application/research-domain logic.
**Status:** Initial pragmatic routing policy  
**Snapshot date:** 19 September 2026  
**Purpose:** Route coding-agent work to appropriate models while balancing quality, latency and cost without turning this project into a model-evaluation programme.

---

# 1. Policy principles

This policy is an **engineering heuristic**, not an experimental research stream.

Model choices are based on:

- current public availability;
- vendor positioning and documented capabilities;
- tool/agent support;
- cost;
- context requirements;
- local hardware fit where relevant;
- limited external evidence when it materially clarifies a choice.

The project should **not** run systematic coding-model bake-offs merely to optimise routing.

When model inventories change, repeat the inventory-and-routing process described in §10 rather than redesigning the task taxonomy.

---

# 2. Stable task classes

| Class | Description |
|---|---|
| T0 | Mechanical edits, formatting-adjacent changes, trivial documentation |
| T1 | Small bounded implementation with clear acceptance criteria |
| T2 | Routine multi-file feature/bug-fix work |
| T3 | Difficult debugging, stateful behaviour, non-local failures, substantial refactors |
| T4 | Architecture-sensitive changes, new abstractions, migrations, highest-risk work |
| T5 | Independent review of a material generated patch |
| T6 | Planning/decomposition before implementation |
| T7 | Long-context repository analysis |
| T8 | Reports, summaries, documentation and test scaffolding |
| T9 | Sensitive/private-code route where external APIs are not permitted |

These task classes should remain stable when models are added or retired.

---

# 3. List 1 inventory — publicly available Anthropic and OpenAI models

The routing universe includes currently public general-purpose, reasoning and coding-capable models. Specialist image/audio/video/moderation models and restricted-access models are excluded from coding-agent routing.

## 3.1 Anthropic

Current/public candidates captured for routing purposes:

```text
Claude Fable 5 / current Fable generation
Claude Opus 5
Claude Opus 4.8
Claude Opus 4.7
Claude Opus 4.6
Claude Opus 4.5
Claude Sonnet 5
Claude Sonnet 4.6
Claude Sonnet 4.5
Claude Haiku 4.5
```

Anthropic's current deprecation documentation lists Fable 5, Opus 5/4.8/4.7/4.6/4.5, Sonnet 5/4.6/4.5 and Haiku 4.5 as active API models [1]. Anthropic positions Sonnet 5 as a strong agentic coding/tool-use model at $2/M input and $10/M output, while Opus 5 is positioned for stronger long-running and difficult coding work at $5/M input and $25/M output [2], [3].

Fable is retained as a highest-capability Anthropic option rather than a routine route because its price is materially higher [4].

## 3.2 OpenAI

Current/public candidates captured for routing purposes:

```text
GPT-6 Astra
GPT-5.6 Sol
GPT-5.6 Terra
GPT-5.6 Luna
GPT-5.5
GPT-5.5 Pro
GPT-5.4
GPT-5.4 Pro
GPT-5.4 Mini
GPT-5.4 nano
GPT-5.3-Codex
GPT-5.2
GPT-5.2 Pro
GPT-5.1
GPT-5
GPT-5 Mini
GPT-5 nano
GPT-5 Pro
o3
o3-pro
GPT-4.1
GPT-4.1 Mini
GPT-4o
GPT-4o Mini
gpt-oss-20b
gpt-oss-120b
```

OpenAI's current catalogue identifies GPT-6 Astra as its highest-capability general model, GPT-5.6 Terra as the intelligence/cost balance, GPT-5.6 Luna as the cost-sensitive tier, GPT-5.6 Sol as the flagship professional tier, and GPT-5.3-Codex as a specialist agentic coding model [5], [6].

The open-weight `gpt-oss` models remain part of List 1 because they are publicly available OpenAI models; `gpt-oss-20b` is also usable locally [5], [7].

Older active models are preserved in the inventory for compatibility/fallback, but are not routed by default unless they offer a specific advantage or a current route is unavailable.

---


---

# 3A. Decision method and full recommendation reasoning

The active routes are intentionally chosen from a much larger inventory. The objective is **not** to spread traffic across every active model; it is to occupy a small number of stable operational roles with models whose documented characteristics make them a good fit.

The routing decision uses the following criteria, in approximate priority order:

| Criterion | Why it matters |
|---|---|
| Coding/agentic capability | The model must reliably edit, navigate and reason over software rather than merely generate snippets |
| Tool-use reliability | The project is agentic; shell, repository, test and structured-tool interactions are central |
| Reasoning depth | Debugging, architecture and failure diagnosis require qualitatively stronger reasoning than mechanical edits |
| Independence for review | Review should avoid correlated failure where practical by changing provider/model family |
| Latency | Routine work should not pay frontier-model latency unnecessarily |
| Token price | High-volume routine work magnifies small price differences |
| Context handling | Repository analysis occasionally requires broad context, but retrieval is preferred to context stuffing |
| Local hardware fit | For List 2, models should be interactively usable on 96 GB RAM / 16 GB VRAM |
| Privacy/locality | List 2 must support a fail-closed private-code path |
| Lifecycle stability | Active/current models are preferred over older models unless the older model has a distinct advantage |

The policy deliberately does **not** use a composite numerical model score. Such a score would create false precision and would push the project toward coding-model evaluation, which is explicitly out of scope.

## Why only a small active subset is routed

The inventories contain many older or overlapping models. Routing them all would create:

- unnecessary policy complexity;
- more failure modes;
- harder provenance analysis;
- accidental experimentation;
- weaker operational intuition.

A model remains in the inventory even when it has no default route. This preserves compatibility and gives future refreshes a known candidate set without forcing current traffic through it.

## Recommendation A reasoning — Anthropic/OpenAI-only

### Why Claude Sonnet 5 is the routine coding default

Sonnet 5 occupies the best documented balance of:

- strong agentic coding;
- tool use;
- sustained multi-step execution;
- materially lower price than the top Anthropic/OpenAI frontier tiers.

Routine coding is expected to dominate agent volume. Using Astra, Opus 5 or another maximum-capability model for that traffic would spend significantly more without a clear reason to expect proportional benefit on bounded implementation work.

Sonnet 5 is therefore selected not because it is assumed to be universally superior, but because its capability/cost positioning matches the dominant task class.

### Why GPT-5.6 Luna is restricted to mechanical work

Luna's value is cost and speed, not maximum software-engineering depth.

The route is deliberately narrow:

- documentation;
- repetitive edits;
- directly testable boilerplate;
- tiny bounded changes.

The routing policy does not ask Luna to "try harder" on an unexpectedly difficult task. Once a task becomes non-local or design-sensitive, it is reclassified.

This avoids a common false economy: repeated cheap attempts can cost more time than one correctly routed stronger attempt.

### Why GPT-5.6 Sol handles difficult debugging and substantial refactors

Sol is placed above the routine tier because these tasks have higher cost-of-error:

- uncertain root causes;
- stateful or concurrent behaviour;
- non-local test failures;
- broad refactors;
- migration logic.

It is also useful as the independent reviewer for Anthropic-generated changes because it provides provider/model-family separation while remaining cheaper than the highest OpenAI tier.

### Why GPT-6 Astra is not the default architecture model for all design work

Astra is reserved for the highest-risk class rather than used routinely.

Architecture-sensitive work does not automatically require the most expensive model. Many architecture changes are well specified and can be handled by Sol or Sonnet plus:

- `software-design-clarity`;
- Import Linter;
- Tach;
- tests;
- human review.

Astra is used when the reasoning problem itself is unusually difficult or when a strong lower tier has already failed materially. This keeps frontier spend attached to genuine uncertainty rather than prestige.

### Why Claude Opus 5 is the OpenAI-generated patch reviewer

The primary reason is **independence**, not because Opus is assumed to be the world's best reviewer.

A material OpenAI-generated patch should preferably be challenged by a strong model from another provider. Opus 5 is the strongest practical Anthropic review tier in the active policy.

For an Anthropic-generated patch, Sol serves the reciprocal role.

### Why GPT-5.6 Terra is the long-context route

Long-context analysis has a different optimisation target from difficult coding.

The router first prefers repository retrieval/search. If genuinely broad context is necessary, Terra is selected as a cost-conscious broad-context route rather than paying Sol/Astra rates solely for context capacity.

### Why older active models are not assigned routine routes

Older GPT-5.x, GPT-4.x, o-series and older Claude variants remain useful as compatibility or availability fallbacks, but a default route needs a positive reason to choose them over current models.

Merely being active is not sufficient.

## Recommendation B reasoning — local-first hybrid

List 2 has a different objective: reduce external spend and retain private/local capability **without forcing difficult work onto inadequate local models**.

### Why Devstral Small 2 is the default local coding worker

Devstral Small 2 is selected because three properties align unusually well:

1. it is explicitly designed for agentic software engineering and multi-file repository work;
2. its approximately 15 GB Q4 footprint is close to the 16 GB VRAM sweet spot;
3. it avoids making modest routine coding dependent on an external API.

This is a hardware/workload fit decision rather than a benchmark contest.

### Why Qwen3.5 9B is the mechanical local route

A small fast model is valuable for work where reasoning depth is not the bottleneck.

Its role mirrors Luna in Recommendation A:

- repetitive edits;
- documentation;
- simple tests;
- strongly bounded transformations.

It keeps trivial traffic off both larger local models and paid APIs.

### Why Qwen3-Coder 30B-A3B is used for repository-scale local work

Its sparse/MoE design and coding specialisation make it a reasonable fit for broad codebase analysis despite the larger total weight footprint.

The machine has enough system RAM for modest offload, while the active parameter count helps keep inference more practical than a similarly sized dense model.

It is therefore used when **codebase understanding** is the main problem.

### Why GLM-4.7-Flash is the difficult-local reasoning branch

Qwen3-Coder and GLM-4.7-Flash occupy different failure branches:

```text
"doesn't understand enough of the repository"
        → Qwen3-Coder

"understands the code but reasoning/debugging is hard"
        → GLM-4.7-Flash
```

The router should choose between them rather than serially trying every local model.

### Why gpt-oss-20b is the local reviewer

Review benefits from model-family diversity. `gpt-oss-20b`:

- fits comfortably enough on the target machine;
- supports agent/tool patterns;
- is from a different family than the primary Devstral generator.

It is therefore useful even if another local model might be marginally stronger at generation.

### Why architecture/high-risk work goes to cloud when allowed

The existence of local models should not force an artificial privacy/cost optimisation when the work has a high cost of error.

For architecture-sensitive tasks:

```text
cloud permitted
    → GPT-5.6 Sol, then Astra if warranted

cloud prohibited
    → strongest appropriate local route + independent local review + human gate
```

This is a deliberate quality safeguard.

### Why the local route stops instead of leaking private code

Privacy is treated as a **hard routing constraint**, not an optimisation preference.

A `private_local_only` task must fail closed. If local models are insufficient, the next step is human intervention, not silent API escalation.

## Rejected alternatives and why

The following approaches were considered implicitly and rejected:

### "Use the strongest model for everything"

Rejected because it would increase cost and latency substantially, reduce the information value of routing telemetry, and waste frontier capability on mechanical work.

### "Always use the cheapest model first"

Rejected because repeated weak attempts can increase elapsed time and produce tactical low-quality patches. Task classification should route obviously difficult work directly upward.

### "Run every material task through several models and choose the best"

Rejected because this becomes a model-evaluation programme and multiplies both spend and latency.

### "Use the same model as generator and reviewer"

Allowed only for low-risk/mechanical work. For material changes, independent review is preferred to reduce correlated blind spots.

### "Keep everything local in List 2"

Rejected because local-first is a cost/privacy strategy, not a reason to compromise quality on high-risk tasks when cloud use is permitted.

### "Use advertised maximum context routinely"

Rejected because repository retrieval is usually cheaper, faster and more selective, especially on local hardware where KV-cache/context costs are material.

---

# 3B. Confidence and evidence level of routing decisions

Each route should be understood as a **reasoned engineering recommendation**, not a proven ranking.

Use these evidence labels when refreshing the policy:

```text
DOCUMENTED
    directly supported by provider/model documentation

SUPPORTED
    documentation plus relevant independent or model-card evidence

INFERRED
    reasoned from architecture, price, hardware fit or model family characteristics

OPERATIONAL
    later supported by this project's own incidental usage observations
```

The project should collect `OPERATIONAL` evidence naturally but should not create artificial bake-offs merely to promote a route.

# 4. Recommendation A — List 1 cloud/public routing

## 4.1 Recommended active routes

| Task | Primary model | Reasoning/effort | Notes |
|---|---|---|---|
| T0 mechanical | **GPT-5.6 Luna** | none/low | Very low cost; use only for tightly bounded work |
| T1 small bounded implementation | **Claude Sonnet 5** | medium/default | Strong agentic coding at attractive cost |
| T2 routine multi-file work | **Claude Sonnet 5** | medium/high | Default coding workhorse |
| T3 difficult debugging/refactor | **GPT-5.6 Sol** | high | Stronger reasoning/tool execution; 1.05M context available |
| T4 architecture/high-risk | **GPT-6 Astra** | high/xhigh | Reserve for genuinely difficult/high-impact work |
| T5 review of Anthropic-generated change | **GPT-5.6 Sol** | high | Cross-provider independence |
| T5 review of OpenAI-generated change | **Claude Opus 5** | high | Cross-provider independence |
| T6 planning/decomposition | **Claude Sonnet 5** | medium | Escalate only for architecture-critical planning |
| T7 very long-context repo analysis | **GPT-5.6 Terra** | medium | Large context with lower price than Sol |
| T8 docs/test scaffolding | **GPT-5.6 Luna** | none/low | Escalate if reasoning/code semantics matter |

### Why Sonnet 5 is the default generator

Anthropic explicitly positions Sonnet 5 for sustained coding, tool use and autonomous multi-step execution at $2/M input and $10/M output [2]. That makes it a strong default workhorse rather than using the most expensive frontier model on routine implementation.

### Why GPT-5.6 Sol is the default difficult-task/review tier

OpenAI positions Sol as its flagship for complex professional work; it supports configurable reasoning, tool use, structured outputs and a 1.05M-token context at $4/M input and $20/M output [6]. It also provides provider/model-family diversity when the normal generator is Sonnet 5.

### Why Astra is escalation-only

OpenAI positions GPT-6 Astra as its most capable model for software engineering and multistep professional work, but at $10/M input and $50/M output it should be reserved for tasks where the expected quality gain is worth the premium [5], [8].

---

# 5. Concrete routing rules — Recommendation A

Apply these in order.

## R1 — deterministic gates before model escalation

If Ruff, Import Linter, Tach or a test gives a precise deterministic error, first return that evidence to the current generator.

Do not escalate merely because a deterministic gate failed once.

## R2 — T0 mechanical route

Use **GPT-5.6 Luna** when all are true:

- change is bounded and unambiguous;
- no architectural/public-API/schema decision;
- normally ≤2 files and roughly ≤150 changed lines;
- expected result is directly checkable by tests/static gates.

If the change unexpectedly requires reasoning across modules, reroute rather than forcing Luna through repeated attempts.

## R3 — default implementation route

Use **Claude Sonnet 5** for normal implementation when:

- acceptance criteria are clear;
- change is roughly 1–6 files / ≤500 changed lines;
- no novel architecture boundary is required;
- repository context can be retrieved selectively.

These thresholds are routing heuristics, not hard limits.

## R4 — difficult-work escalation

Route directly to **GPT-5.6 Sol** when any of the following is true:

- root cause is unclear after initial investigation;
- concurrency/state/persistence semantics are central;
- change spans many modules;
- significant refactor or migration;
- normal model produced one materially incorrect attempt;
- test failure is non-local or difficult to reproduce;
- context requirements exceed the practical Sonnet route.

## R5 — architecture/high-risk route

Use **GPT-6 Astra** when:

- introducing/changing a major architectural boundary;
- performing a high-impact data/schema migration;
- Sol has already failed materially once;
- task requires unusually deep cross-domain reasoning;
- human reviewer explicitly marks the task highest-risk.

Use the `software-design-clarity` skill regardless of model.

## R6 — one semantic retry maximum at a tier

Do not repeatedly ask the same model to solve the same semantic failure.

- transient/tool failure: retry same route once;
- materially wrong solution: escalate immediately;
- second material failure at higher tier: stop for human review rather than blindly escalating forever.

## R7 — independent material review

For a material change, reviewer should normally be from a different provider/model family:

```text
Anthropic generator → GPT-5.6 Sol reviewer
OpenAI generator    → Claude Opus 5 reviewer
```

For T0 mechanical changes, deterministic gates may be sufficient without LLM review.

## R8 — reviewer must not silently rewrite

T5 review produces findings/recommendations. A separate repair/generator step applies changes unless the workflow explicitly authorises reviewer edits.

## R9 — long context is not a substitute for retrieval

Use **GPT-5.6 Terra** for unusually broad repository analysis, but prefer repository search/retrieval first. Do not fill 1M tokens simply because the model supports it.

## R10 — fallback order

Service/availability fallback:

```text
Luna   → Haiku 4.5
Sonnet 5 → GPT-5.6 Terra
Sol    → Claude Opus 5
Astra  → Claude Fable / strongest public Fable generation
```

Fallback is for availability/compatibility, not silent quality downgrading on high-risk tasks.

---

# 6. List 2 inventory — List 1 plus comfortable local models

List 2 contains **all of List 1 unchanged**, plus models that are practical for interactive use on a laptop with **96 GB system RAM and a 16 GB RTX 4090 Laptop GPU**.

The local criterion is deliberately stricter than “technically loads”. Q4/Q5 quantisation and modest system-RAM offload are acceptable; pathological swap use or predominantly CPU-bound huge dense models are not.

Additional local candidates:

```text
Devstral Small 2 24B
GLM-4.7-Flash 30B-A3B
Qwen3-Coder 30B-A3B
Qwen3.5 9B
Qwen3.5 27B
Mistral Small 3.2 24B
Qwen3 30B-A3B
Qwen2.5-Coder 14B
DeepSeek-Coder-V2 Lite / 16B
Phi-4 14B
Gemma 3 12B
Gemma 3 27B
Ministral 3 14B
```

`gpt-oss-20b` is already present in List 1 and is also a strong local candidate: Ollama packages it at about 14 GB and describes it as intended for lower-latency local/agentic use [7].

Notable hardware fits include Devstral Small 2 at ~15 GB Q4, Qwen3-Coder 30B at ~19 GB Q4 with only 3.3B active parameters, GLM-4.7-Flash at ~19 GB with 3B active parameters, Qwen3.5 27B at ~17 GB, Mistral Small 3.2 at ~15 GB, and Qwen2.5-Coder 14B at ~9 GB [9]–[14].

---

# 7. Recommendation B — List 2 local-first hybrid routing

The second recommendation makes local execution meaningful rather than treating local models as emergency fallbacks.

## 7.1 Recommended active routes

| Task | Primary model | Fallback/escalation | Notes |
|---|---|---|---|
| T0 mechanical/local | **Qwen3.5 9B** | GPT-5.6 Luna | Fast local route |
| T1 small bounded coding | **Devstral Small 2 24B** | Claude Sonnet 5 | Purpose-built local software-engineering agent |
| T2 routine multi-file coding | **Devstral Small 2 24B** | Qwen3-Coder 30B → Sonnet 5 | Keep routine coding local |
| T3 difficult local debugging | **GLM-4.7-Flash** | GPT-5.6 Sol | Strong local reasoning/tool tier |
| T4 architecture/high-risk | **GPT-5.6 Sol** | GPT-6 Astra | Cloud by default if policy permits |
| T5 review of local Devstral change | **gpt-oss-20b** | GPT-5.6 Sol | Different family; fits locally |
| T5 review of cloud OpenAI change | **Claude Opus 5** | — | Cross-provider review |
| T5 review of cloud Anthropic change | **GPT-5.6 Sol** | — | Cross-provider review |
| T6 planning/decomposition | **gpt-oss-20b** | Sonnet 5 | Local reasoning for routine plans |
| T7 repo-scale local analysis | **Qwen3-Coder 30B-A3B** | GPT-5.6 Terra | 256K native context; coding-specialised |
| T8 docs/test scaffolding | **Qwen3.5 9B** | Luna | Keep cheap work local |
| T9 private/local-only | **Devstral Small 2 / Qwen3-Coder / GLM-4.7-Flash** | human review | No cloud escalation without explicit approval |

### Why Devstral Small 2 is the local default generator

It is specifically designed for agentic software engineering, codebase exploration and multi-file editing, and its Ollama Q4 package is ~15 GB—close to the 16 GB GPU sweet spot [9]. The published model card reports 65.8% SWE-bench Verified, which is useful supporting evidence but is **not** being treated as a project benchmark [9].

### Why gpt-oss-20b is the local independent reviewer

It is a different model family/provider from Devstral, is explicitly agentic/tool-capable, supports structured outputs and reasoning effort, and its ~14 GB local package fits the GPU budget well [7]. This provides cheap local diversity for review.

### Why GLM-4.7-Flash is the difficult-local tier

It is a 30B-A3B MoE model with tools/thinking and a ~19 GB Q4 package, requiring only modest CPU/system-RAM offload on this machine. Its published benchmark table indicates substantially stronger software-engineering performance than smaller local reasoning alternatives, although those vendor results are treated only as directional evidence [10].

### Why Qwen3-Coder is the repository-analysis tier

Qwen3-Coder 30B has only 3.3B active parameters, a 256K context window and is explicitly trained for agentic software engineering and repository-scale work; its Q4 package is ~19 GB [11].

---

# 8. Concrete routing rules — Recommendation B

## L1 — local-first default

If a task is T0–T2 and cloud-only capabilities are not required, route locally first.

```text
T0 → Qwen3.5 9B
T1/T2 → Devstral Small 2
```

## L2 — local failure escalation

For a materially wrong local result:

```text
Devstral Small 2
    ↓
Qwen3-Coder 30B (repo-scale/code-heavy)
OR
GLM-4.7-Flash (reasoning/debugging-heavy)
    ↓
Claude Sonnet 5
    ↓
GPT-5.6 Sol
```

Do not send a task through every local model. Choose the branch based on failure type.

## L3 — architecture bypasses routine local tier

For T4 work, route directly to **GPT-5.6 Sol** when cloud use is allowed.

The local models may assist with repository exploration, but the primary design/implementation reasoning should not be downgraded merely to avoid API cost.

## L4 — private/local-only route

When source code is restricted from external APIs:

```text
routine coding → Devstral Small 2
repo-scale coding → Qwen3-Coder 30B
hard debugging/reasoning → GLM-4.7-Flash
independent review → gpt-oss-20b
```

If these disagree or fail materially on architecture-sensitive work, stop for human review rather than violating the privacy boundary.

## L5 — local review independence

A material Devstral-generated patch should be reviewed by **gpt-oss-20b**, not Devstral again.

If local reviewer confidence/evidence is insufficient and cloud use is allowed, escalate review to GPT-5.6 Sol.

## L6 — VRAM/context discipline

For ~15 GB models, do not assume the advertised maximum context is comfortable with full GPU residency.

Default local coding contexts should normally be **16K–32K**, expanding toward ~64K only when justified. Prefer retrieval/search over context stuffing.

Models with ~17–19 GB Q4 weights should be treated as hybrid GPU/RAM routes with modest offload.

## L7 — route on failure type

After deterministic gates fail:

- simple local code error → same model once with exact error;
- repeated logic/test failure → higher reasoning tier;
- Import Linter/Tach/design failure → architecture tier;
- repository-understanding failure → Qwen3-Coder/long-context tier.

## L8 — no automatic cloud leakage

`private_local_only=true` is a hard routing constraint.

The router must fail closed rather than silently escalating to an API model.

---

# 9. Shared routing telemetry

Record for each agent task:

```yaml
routing:
  policy_version:
  task_class:
  selected_model:
  provider:
  local_or_remote:
  reason:
  escalation_from:
  attempt_number:
  input_tokens_or_context_estimate:
  output_tokens:
  latency:
  provider_cost:
  outcome:
    success
    deterministic_failure
    semantic_failure
    human_escalation
```

This telemetry exists to monitor the policy, not to create a model-evaluation programme.

A routing change should be considered when operational evidence shows persistent waste or failure, but the project should not optimise small performance differences between models.

---


---

# 9A. Detailed usage, cost and turnaround telemetry

Routing telemetry should support later operational analysis without becoming a model-benchmark programme.

## ModelUsage record

Capture one record per model invocation or provider response:

```yaml
ModelUsage:
  id:
  agent_run_id:
  job_id:
  experiment_id:
  routing_policy_version:
  task_class:
  attempt_number:

  provider:
  model:
  endpoint_or_runtime:
  local_or_remote:
  route_reason:
  escalation_from:

  timestamps:
    queued_at:
    request_started_at:
    first_token_at:
    response_completed_at:

  tokens:
    input_tokens:
    cached_input_tokens:
    output_tokens:
    reasoning_tokens:
    total_tokens:
    usage_source:
      provider_reported
      runtime_reported
      estimated

  timing_ms:
    queue:
    time_to_first_token:
    generation:
    total_turnaround:
    tool_wait:
    deterministic_validation:

  spend:
    currency: USD
    price_catalog_version:
    estimated_input_cost:
    estimated_output_cost:
    estimated_cached_input_cost:
    estimated_total_cost:
    provider_reported_cost:
    cost_source:
      estimated
      provider_reported
      local_no_api_charge

  outcome:
    success
    deterministic_failure
    semantic_failure
    cancelled
    human_escalation
```

Provider-specific fields may be retained in a JSON metadata column, but the common fields above should remain stable.

## Token accounting

Prefer, in order:

1. provider-reported usage;
2. local-runtime reported usage;
3. tokenizer-based estimate.

Do not silently compare estimated token counts with provider-billed counts as if they were identical.

Where providers expose cache usage or reasoning-token usage, retain those separately rather than flattening them away.

## Spend estimation

Maintain a versioned `ModelPriceCatalog`.

```yaml
ModelPriceCatalog:
  version:
  effective_at:
  provider:
  model:
  input_per_million:
  cached_input_per_million:
  output_per_million:
  currency:
  source:
```

A historical `ModelUsage` record must retain the price-catalog version used to estimate its spend.

This prevents later price changes from rewriting historical estimates.

If the provider exposes an actual billed/request cost, store it alongside the estimate rather than overwriting the estimate.

For local models:

```text
estimated API spend = 0
cost_source = local_no_api_charge
```

The project deliberately does not invent electricity/hardware amortisation for the live harness display. Local compute time remains observable through turnaround and runtime metrics.

## Turnaround time

Record at least:

```text
queue time
time-to-first-token
generation/model time
end-to-end turnaround
```

For agentic tasks, the model call itself may be a small fraction of total time. Therefore aggregate at both:

```text
model invocation
AgentRun / Job
```

At run level also retain:

- total model time;
- total tool/test time;
- total queue time;
- total wall-clock time;
- number of model calls;
- number of escalations.

## Persistence

For near-real-time operation:

```text
SQLite
    current ModelUsage / run aggregates
```

For durable analysis:

```text
periodic/export-on-completion
    ↓
Parquet
    ↓
DuckDB
```

This keeps the live harness simple while allowing later cross-run analysis.

## RoutingDecision record

Keep the model-selection decision separate from usage so later analysis can distinguish:

```text
what the router intended
vs
what the model actually consumed
```

```yaml
RoutingDecision:
  id:
  task_id:
  policy_version:
  task_class:
  selected_model:
  selected_provider:
  selected_tier:
  reason_codes:
  alternatives_considered:
  constraints:
    private_local_only:
    max_cost:
    max_latency:
  created_at:
```

This is especially important for escalations.

## Suggested later analyses

The harness should make the following possible without making them prominent during normal work:

- spend by slice / job / agent / model / task class;
- token use by route;
- median/p95 turnaround;
- time-to-first-token;
- escalation rate;
- retries per successful task;
- cost per accepted patch;
- wall time per accepted patch;
- proportion of work kept local;
- reviewer/generator model-family separation;
- deterministic-failure versus semantic-failure rates.

These are operational diagnostics, not a benchmark leaderboard.

---

# 9B. Near-real-time user summary

The normal harness view should show only a **small, non-distracting status line**.

### While running

Example:

```text
Sonnet 5 · 12.8k in / 1.4k out · ~$0.05 · 18s
```

For a local model:

```text
Devstral 24B · 12.8k in / 1.4k out · local · 18s
```

### When complete

Example:

```text
Sonnet 5 · 18.4k in / 2.1k out · ~$0.08 · 42s
```

The exact UI may abbreviate further on small screens.

## Display rules

Show only:

1. model short name;
2. token count;
3. estimated/provider spend, or `local`;
4. elapsed turnaround.

Do not display:

- routing rationale;
- price-table details;
- cache/reasoning-token breakdown;
- provider metadata;
- comparison against other models

unless the user opens the detail view.

## Live updates

Update opportunistically from streaming/runtime usage events.

Do not create high-frequency polling merely to animate token counters.

A refresh cadence of roughly **1–2 seconds while active** is sufficient if streaming usage is available; otherwise update at meaningful lifecycle events.

The telemetry UI must remain secondary to the actual coding/research workflow.



# Double-Entry Review routing provenance

When a DER material-change review uses coding/review agents, record the normal routing provenance
(policy/inventory/decision/provider/model-family/model) against the DER review evidence where
available. For critical/material independent review, prefer a reviewer whose provider/model family
is independent from the authoring route when policy permits.

This supports provenance and correlated-failure analysis; it does not make DER a model benchmark.


# Policy portability and switching

The two recommendations in this document are policy instances, not application architecture.

Projects may choose either policy (or future policies) through configuration.

Tasks may override the project default.

During a task, the harness may:

```text
escalate within the current policy
choose a model once
switch policy for the remainder of the task
```

A policy switch creates a `RoutingPolicyTransition` and a structured `AgentHandoff`.

The full raw transcript remains available for provenance but should not automatically be replayed into a different model/context envelope.

Model/provider availability, privacy constraints, remaining budget and practical context are evaluated at routing time.

Provider outage/rate limiting is an infrastructure condition and should not be treated as evidence that a stronger reasoning model is required.


# 10. Repeatable refresh procedure

When models are released or retired:

1. **Refresh provider inventories** from official OpenAI and Anthropic model/deprecation pages.
2. Mark models `ACTIVE_CURRENT`, `ACTIVE_OLDER`, `DEPRECATED`, `RESTRICTED`, or `IRRELEVANT_MODALITY`.
3. Remove deprecated/retired models from new default routes, retaining them only in historical manifests.
4. For List 2, refresh local candidates using:
   - interactive hardware fit on 96 GB RAM / 16 GB VRAM;
   - agent/tool support;
   - coding/reasoning positioning;
   - roughly ≤20 GB Q4-class weight footprint unless sparse execution makes a larger artefact clearly practical.
5. Place new models into the **existing T0–T9 task classes** based on documented characteristics; do not invent new classes just for a model.
6. Prefer a new default only when there is a clear engineering case: materially better quality, materially lower cost/latency at similar quality, better privacy/locality, or a capability the existing route lacks.
7. Do not run a benchmark campaign unless two candidates are genuinely indistinguishable and the choice materially affects the programme.
8. Record the new policy version, date, sources and changed routes.

This process is intentionally lightweight and repeatable.

---

# 11. Recommended initial configuration summary

## List 1

```text
cheap/mechanical      GPT-5.6 Luna
routine coding        Claude Sonnet 5
difficult coding      GPT-5.6 Sol
architecture/highest  GPT-6 Astra
Anthropic-gen review  GPT-5.6 Sol
OpenAI-gen review     Claude Opus 5
long-context analysis GPT-5.6 Terra
```

## List 2

```text
cheap/local           Qwen3.5 9B
routine local coding  Devstral Small 2 24B
repo-scale local      Qwen3-Coder 30B-A3B
hard local reasoning  GLM-4.7-Flash
local review          gpt-oss-20b
cloud routine fallback Claude Sonnet 5
cloud difficult       GPT-5.6 Sol
cloud highest         GPT-6 Astra
```

---

# References

[1] Anthropic, “Model deprecations,” *Claude Platform Docs*, 2026. [Online]. Available: https://docs.anthropic.com/en/docs/about-claude/model-deprecations. [Accessed: Sep. 19, 2026].

[2] Anthropic, “Introducing Claude Sonnet 5,” Jun. 30, 2026. [Online]. Available: https://www.anthropic.com/news/claude-sonnet-5. [Accessed: Sep. 19, 2026].

[3] Anthropic, “Introducing Claude Opus 5,” Jul. 24, 2026. [Online]. Available: https://www.anthropic.com/news/claude-opus-5. [Accessed: Sep. 19, 2026].

[4] Anthropic, “Claude Fable,” 2026. [Online]. Available: https://www.anthropic.com/claude/fable. [Accessed: Sep. 19, 2026].

[5] OpenAI, “All models,” *OpenAI API Documentation*, 2026. [Online]. Available: https://developers.openai.com/api/docs/models/all. [Accessed: Sep. 19, 2026].

[6] OpenAI, “GPT-5.6 Sol Model,” *OpenAI API Documentation*, 2026. [Online]. Available: https://developers.openai.com/api/docs/models/gpt-5.6-sol. [Accessed: Sep. 19, 2026].

[7] Ollama, “gpt-oss:20b,” 2026. [Online]. Available: https://ollama.com/library/gpt-oss:20b. [Accessed: Sep. 19, 2026].

[8] OpenAI, “Model guidance — GPT-6 Astra,” *OpenAI API Documentation*, 2026. [Online]. Available: https://developers.openai.com/api/docs/guides/latest-model. [Accessed: Sep. 19, 2026].

[9] Ollama, “Devstral Small 2,” 2026. [Online]. Available: https://ollama.com/library/devstral-small-2:latest. [Accessed: Sep. 19, 2026].

[10] Ollama, “GLM-4.7-Flash,” 2026. [Online]. Available: https://ollama.com/library/glm-4.7-flash. [Accessed: Sep. 19, 2026].

[11] Ollama, “Qwen3-Coder,” 2026. [Online]. Available: https://ollama.com/library/qwen3-coder. [Accessed: Sep. 19, 2026].

[12] Ollama, “Qwen3.5,” 2026. [Online]. Available: https://ollama.com/library/qwen3.5. [Accessed: Sep. 19, 2026].

[13] Ollama, “Mistral Small 3.2,” 2026. [Online]. Available: https://ollama.com/library/mistral-small3.2. [Accessed: Sep. 19, 2026].

[14] Ollama, “Qwen2.5-Coder,” 2026. [Online]. Available: https://ollama.com/library/qwen2.5-coder. [Accessed: Sep. 19, 2026].

[15] Ollama, “DeepSeek-Coder-V2,” 2026. [Online]. Available: https://ollama.com/library/deepseek-coder-v2. [Accessed: Sep. 19, 2026].

[16] Ollama, “Gemma 3,” 2026. [Online]. Available: https://ollama.com/library/gemma3. [Accessed: Sep. 19, 2026].

[17] Ollama, “Ministral 3,” 2026. [Online]. Available: https://ollama.com/library/ministral-3. [Accessed: Sep. 19, 2026].
