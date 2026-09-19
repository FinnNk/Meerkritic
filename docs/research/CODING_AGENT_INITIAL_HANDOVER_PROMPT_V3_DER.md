# Coding Agent Initial Handover Prompt — DER-integrated version

You are taking over implementation of the attached **Evidence-Grounded Semantic Code Review** project.

The attached bundle is the authoritative project specification. Begin with **VS1 — Data-to-Annotation** and use the defined vertical-slice process. Do not attempt to implement the whole programme at once.

## 1. Read before coding

Read in this order:

1. `README.md`
2. `CONTEXT.md`
3. `06_IMPLEMENTATION_HANDOVER.md`
4. `IMPLEMENTATION_BACKLOG.yaml`
5. `11_DOUBLE_ENTRY_REVIEW_INTEGRATION.md`
6. `10_MODEL_ROUTING_SUBSYSTEM_DESIGN.md`
7. `05_PROJECT_HARNESS_PLAN.md`
8. `01_SYSTEM_DESIGN.md`
9. `02_EXPERIMENTAL_PLAN.md`
10. `09_MODEL_ROUTING_POLICY.md`
11. `MODEL_ROUTING_POLICY.yaml`
12. `03_LOCAL_DATASET_STORAGE.md`
13. `04_COST_MODEL_AND_BUDGET_SCENARIOS.md`
14. `08_AGENTIC_SOFTWARE_FACTORY_FRAMING.md`
15. `07_SOFTWARE_DESIGN_CLARITY_SKILL.md`
16. `SLICE_REVIEW_TEMPLATE.yaml`

Also unpack and inspect:

```text
external-skills/software-design-clarity.zip
external-skills/double-entry-review-core-0.3.0-alpha.2.zip
```

For implementation conflicts, use this authority order:

```text
06_IMPLEMENTATION_HANDOVER.md
    ↓
IMPLEMENTATION_BACKLOG.yaml
    ↓
11_DOUBLE_ENTRY_REVIEW_INTEGRATION.md
    ↓
10_MODEL_ROUTING_SUBSYSTEM_DESIGN.md
    ↓
05_PROJECT_HARNESS_PLAN.md
    ↓
01_SYSTEM_DESIGN.md / 02_EXPERIMENTAL_PLAN.md
    ↓
secondary/background documents
```

Surface any material contradiction before coding. Do not ask for clarification merely because a low-level implementation detail is unspecified.

## 2. Delivery method

The project uses progressively elaborated vertical slices:

```text
build current slice
    ↓
validate
    ↓
record evidence/deviations
    ↓
complete DER review obligations for material changes
    ↓
complete slice review + architecture delta
    ↓
revise remaining slices
    ↓
freeze next slice
```

Only VS1 is currently `READY`.

A **vertical slice is not a DER pair**. Double-Entry Review is applied per **material PR/change inside a slice**.

## 3. Double-Entry Review policy

Use `double-entry-review` alpha.2 for material/critical software changes.

Before starting each PR/change-sized implementation unit, classify it:

```text
routine
material
critical
```

Use `11_DOUBLE_ENTRY_REVIEW_INTEGRATION.md` and the skill's materiality guidance.

Default project rule:

```text
hard materiality trigger
    → DER required

no hard trigger but 2+ strong indicators
    → DER required by default

otherwise
    → routine factory workflow
```

Reassess whenever scope changes materially.

Do not classify a change as material solely because an AI agent wrote it, or solely from LOC/file count.

For a material change:

```text
actual implementation chronology
    ↓
DER diary
    ↓
verify + freeze result
    ↓
plan complete review propositions
    ↓
reconstruct semantic history
    ↓
verify each checkpoint in its own context
    ↓
prove final tracked-tree equivalence
    ↓
review / revision round
```

The **diary is canonical implementation chronology**. Never manufacture a clean chronology while coding.

Multiple agents may work in separate worktrees/contributor branches, but **one history integrator** owns the canonical DER diary/semantic pair.

DER's `semantic history` means the reconstructed proposition-led Git history. It is distinct from the **semantic review system** being built.

DER evidence must live outside application worktrees. The harness may index references/status but must not become a competing evidence source of truth.

Before DER reaches 1.0, routine changes remain on the ordinary factory path unless DER is explicitly requested.

## 4. VS1 objective

Implement:

```text
launch harness
    ↓
register one public dataset
    ↓
browse Parquet via DuckDB
    ↓
launch normalisation workflow
    ↓
route model work through routing subsystem
    ↓
orchestrate agentic workflow with Microsoft Agent Framework
    ↓
persist structured output + provenance
    ↓
show result
    ↓
human Accept / Edit / Reject
    ↓
persist annotation + event history
    ↓
show annotation progress
```

## 5. Baseline architecture

Preserve unless implementation evidence demonstrates a real problem:

```text
FastAPI            web/application boundary
SQLite             mutable operational state
DuckDB             analytical queries
Parquet            datasets / large analytical results
filesystem         immutable artefacts/logs/reports
MAF                default agentic workflow/orchestration substrate
worker/process     long-running execution outside web requests
routing subsystem  model-independent selection/provenance/context
```

Use SQLite WAL mode and short transactions.

Do not store large analytical tables or artefact bodies in SQLite.

## 6. Microsoft Agent Framework

MAF is mandatory from VS1 as the default agentic workflow/runtime substrate so the project provides longitudinal evidence about it.

Keep it behind project-owned abstractions such as `WorkflowRunner` / `AgentRuntime`.

Do not leak MAF-specific types into research/domain logic.

Record `FrameworkObservation` from first use.

Do not introduce full durable entity/actor support until an actual workflow benefits from it.

Removal of MAF later requires repeated, material, unresolved friction after mitigation and an ADR.

## 7. Model routing subsystem

Do not hard-code model names in application/domain code.

Implement the reusable abstractions defined in `10_MODEL_ROUTING_SUBSYSTEM_DESIGN.md`:

```text
ModelInventory
TaskRequirements
RoutingPolicy
RoutingDecision
ModelUsage
```

VS1 must also reserve compatible paths for:

```text
RoutingPolicyTransition
AgentHandoff
ProviderHealth
BudgetConstraint
ContextStrategy
```

Resolution hierarchy:

```text
invocation override
→ task override
→ project default
→ system default
```

Hard privacy/local-only constraints fail closed.

Provider failures are infrastructure failures, not evidence that a stronger reasoning model is needed.

## 8. Model telemetry

For routed calls, capture where available:

- inventory/policy versions;
- task class and route reason;
- provider/model;
- input tokens;
- output tokens;
- cached/reasoning tokens where exposed;
- queue time;
- time-to-first-token;
- generation time;
- total turnaround;
- price-catalog version;
- estimated/provider-reported spend;
- outcome.

SQLite holds live operational records; completed history should be available to Parquet/DuckDB.

Near-real-time UI stays terse:

```text
Model · input/output tokens · estimated spend/local · elapsed
```

Do not add electricity/hardware amortisation to the live display.

## 9. VS1 human interaction boundary

Expose only:

```text
Accept
Edit
Reject
```

Persist the decision immediately and append an event.

`uncertain` may exist in model/schema metadata, but it is not a fourth VS1 UI action.

Staging, defer/reopen/supersede, per-object discussion, and batched guidance begin in VS2.

## 10. Mandatory quality gates

From the first commit:

```bash
ruff format --check .
ruff check .
lint-imports
tach check
```

Plus relevant tests through one canonical project quality command.

Use:

- Ruff — Python code conventions;
- Import Linter — high-level architecture contracts;
- Tach — module boundaries/dependencies/interfaces/cycles;
- `software-design-clarity` — advisory abstraction/design-quality review.

Agents must not weaken contracts or add ignores merely to get green checks without explicit approval.

## 11. Design-quality method

For significant abstractions invoke `software-design-clarity`.

Before implementation answer:

```text
What does this abstraction do?
What complexity does it hide?
What may callers rely on?
What must callers not need to know?
Why is this better than a simpler direct implementation?
```

Prefer deep modules, information hiding, meaningful layers, restrained configuration, explicit valid states, and strategic simplification over tactical fixes.

## 12. Knowledge/provenance

Maintain:

```text
CONTEXT.md
docs/adr/
docs/slice-reviews/
```

`CONTEXT.md` is a glossary only.

Create ADRs for material durable/cross-cutting decisions, not routine implementation choices.

Maintain append-only operational events; do not turn the whole application into event sourcing.

## 13. Architecture observability

Generate typed architecture snapshots from:

```text
Tach
Import Linter
Python module/package metadata
```

At material review/slice completion produce:

```text
before
after
delta
```

Diagrams are projections of typed architecture data, not the source of truth.

Archify is not a mandatory runtime dependency.

## 14. VS1 integration preflight

Before live integration verify and record:

- model/provider availability and authentication/connectivity;
- first public dataset access and pinned revision;
- Python/runtime dependency compatibility;
- MAF version/API compatibility;
- Ruff/Import Linter/Tach/DuckDB/SQLite/FastAPI compatibility;
- platform subprocess/worktree constraints;
- DER alpha.2 helper availability;
- DER evidence-store path outside application worktrees;
- Git/worktree prerequisites before freezing any material DER baseline.

These are operational checks, not unresolved design questions.

## 15. Explicitly out of VS1 scope

Unless a demonstrated blocker requires reconsideration, do not build:

- PostgreSQL;
- Redis/Celery;
- Kubernetes;
- object storage;
- distributed workers;
- vector database;
- multi-user auth/RBAC;
- SPA rewrite for preference only;
- WebSockets without demonstrated need;
- repair-agent UI;
- mutation UI;
- rule-discovery UI;
- production PR integration;
- internal-repository integration;
- VS2 staged/defer/reopen interaction UI;
- automatic policy optimisation/comparison dashboards;
- full MAF durable runtime without a demonstrated need;
- mandatory Archify integration.

## 16. VS1 completion requirements

Do not mark VS1 complete until:

### Functional

- local harness launches;
- public dataset registers reproducibly;
- observations browse through DuckDB/Parquet;
- normalisation runs outside web request path;
- MAF orchestrates the workflow;
- structured output/provenance persists;
- Accept/Edit/Reject persists;
- annotation progress and failed-job inspection work.

### MAF/routing/telemetry

- MAF adapter boundary exists without domain leakage;
- FrameworkObservation is captured;
- routing decisions retain inventory/policy versions;
- no application-domain model-name routing logic exists;
- provider failure and semantic failure are distinguishable;
- local-only route fails closed;
- input/output token and turnaround telemetry works;
- hosted spend uses versioned price data;
- terse live telemetry works.

### Quality/architecture

- Ruff/Import Linter/Tach/tests pass;
- typed architecture snapshot works;
- before/after/delta can be produced;
- no unjustified architecture ignores were added.

### DER

For every **material/critical PR/change** inside VS1:

- materiality assessment recorded;
- DER pair/evidence store established;
- true diary chronology preserved;
- frozen diary verified;
- semantic propositions reconstructed;
- checkpoint-local required evidence passes;
- final diary/semantic tracked trees are exactly equivalent;
- review/readiness state is recorded independently of slice state.

Do not create a DER pair for routine work merely to satisfy process appearance.

### Documentation

- terminology/ADRs are updated where needed;
- DER/routing/framework/design observations are recorded;
- slice review is complete;
- remaining slices are explicitly reviewed/revised before VS2 becomes READY.

## 17. Suggested implementation sequence

1. bootstrap Git repository;
2. install/static tooling before DER baseline freeze;
3. run integration preflight;
4. configure Ruff/Import Linter/Tach + canonical quality command;
5. create CONTEXT/ADR/slice-review scaffolding;
6. configure DER skill/evidence store and assess planned PR/change materiality;
7. establish SQLite/domain/Event models;
8. establish routing contracts/telemetry/price catalogue/context-builder boundary;
9. implement MAF adapter;
10. implement dataset/Parquet/DuckDB path;
11. implement Job/worker boundary and model adapter;
12. implement normalisation workflow through MAF;
13. implement observation/annotation UI and telemetry line;
14. implement architecture snapshot;
15. run integration/restart/failure tests;
16. complete DER freeze/reconstruction/checkpoint/equivalence/review for each material change;
17. update documentation;
18. complete VS1 slice review and revise future slices.

Do not interpret this list as one module/class per item.

## 18. Initial response expected

Before coding, briefly report:

1. your understanding of VS1;
2. architecture constraints you will preserve;
3. initial package/module structure;
4. how MAF, routing, persistence, analytics, and DER will be isolated;
5. planned materiality classification / DER change units for the first implementation work;
6. parallel workstreams you intend to use;
7. any genuine contradiction/blocker in the bundle.

If there is no material contradiction, proceed with VS1.
