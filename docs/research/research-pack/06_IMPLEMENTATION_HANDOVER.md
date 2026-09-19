# Implementation Handover: Vertical-Slice Build Plan

**Companion to:**  
- `01_SYSTEM_DESIGN.md`  
- `02_EXPERIMENTAL_PLAN.md`  
- `03_LOCAL_DATASET_STORAGE.md`  
- `04_COST_MODEL_AND_BUDGET_SCENARIOS.md`  
- `05_PROJECT_HARNESS_PLAN.md`

**Purpose:** Provide an implementation-ready handover for building the research harness and supporting programme infrastructure through a sequence of vertical slices.

---

# 1. Delivery model

## Sequence nomenclature

Three sequences appear across the bundle:

- **P0–P5** — research phases in `02_EXPERIMENTAL_PLAN.md`;
- **H0–H6** — harness capability phases in `05_PROJECT_HARNESS_PLAN.md`;
- **VS1–VS8** — implementation vertical slices in this document.

**VS1–VS8 are authoritative for build sequencing.** The other sequences describe research progression and harness capabilities. A rough crosswalk is:

| Vertical slice | Principal research/harness scope |
|---|---|
| VS1 Data-to-Annotation | P0–P1 / H0–H1 |
| VS2 Annotation-to-Rule Discovery | P2 / H2 |
| VS3 Rule-to-Historical-Replay | P3 / H3 |
| VS4 Finding-to-Agent-Repair | P4 / H4 |
| VS5 Repair-to-Behavioural-Evaluation | P4 / H5 |
| VS6 Programme Operations and Comparative Analysis | cross-cutting |
| VS7 Public-to-Internal Transfer | P5 / H6 |
| VS8 Operational Hardening | conditional, post-research |

The crosswalk is descriptive rather than a requirement to make the phases advance in lockstep.

The build should proceed as a sequence of **end-to-end vertical slices**.

Each slice should:

1. deliver a usable capability;
2. exercise multiple architectural layers;
3. produce evidence about the next slice;
4. end with explicit acceptance criteria;
5. trigger a review of all remaining slices.

The plan is intentionally **progressively elaborated**.

Later slices are defined now so that the whole programme is visible, but they are not treated as fixed implementation contracts.

The workflow is:

```text
define all slices
      ↓
build slice N
      ↓
evaluate actual behaviour
      ↓
record decisions/observations
      ↓
revise slices N+1 onward
      ↓
freeze next slice
      ↓
build
```

The immediate implementation target is Slice 1.

---

# 2. Revision principle

After each slice completes:

```text
COMPLETED SLICE
      ↓
evidence review
      ↓
architecture review
      ↓
research-plan review
      ↓
remaining-slice review
      ↓
update backlog
      ↓
freeze next slice
```

Do not revise the completed slice retrospectively except to:

- fix defects;
- clarify documentation;
- record deviations.

The remaining slices may be materially changed if evidence warrants it.

---

# 3. Slice states

Each slice has one of four states:

```text
DRAFT
READY
ACTIVE
COMPLETE
```

Definitions:

- **DRAFT** — high-level intent exists; details may change.
- **READY** — acceptance criteria and implementation tasks are frozen enough to build.
- **ACTIVE** — implementation underway.
- **COMPLETE** — exit criteria met and review performed.

Only one major slice should normally be `ACTIVE`.

---


# Baseline engineering constraints

The following are mandatory from Slice 1 onward.

## Ruff

Use Ruff for repository Python code conventions, linting and formatting.

Required checks:

```bash
ruff format --check .
ruff check .
```

## Import Linter

Use Import Linter as the authoritative human-readable architectural contract layer.

Initial contracts should cover at least:

- dependency direction between web/UI, application/services, domain/research logic and infrastructure/adapters;
- prohibition of direct web-to-persistence coupling;
- isolation of model/framework adapters from research-domain code;
- any package independence rules visible in the initial module structure.

Command:

```bash
lint-imports
```

## Tach

Use Tach for concrete Python module boundaries, declared dependencies, public interfaces and cycle enforcement.

Command:

```bash
tach check
```

The initial module definition may be deliberately coarse and refined after each slice.

Once stable enough, enable:

```toml
forbid_circular_dependencies = true
```

## Canonical project check

Create one canonical quality command used by humans, CI and coding agents:

```text
format check
+ Ruff lint
+ Import Linter
+ Tach
+ tests
```

No slice is complete while this command fails.

Agents may not weaken architecture contracts or add ignores/exceptions solely to make the check pass without explicit human approval.

---


# Knowledge and architecture continuity

The implementation repository must include from Slice 1:

```text
CONTEXT.md
docs/adr/
docs/slice-reviews/
```

`CONTEXT.md` is a glossary only. Material, durable architectural choices should be captured as ADRs. Every slice review must include a decision trace linking material decisions to their source, glossary/ADR/backlog effects, implementation and verification.

Architecture must be captured at slice entry and exit using typed snapshots derived from Tach, Import Linter and module metadata. Every slice review therefore records:

```text
architecture before
architecture after
architecture delta
intentional/unintentional change assessment
ADR/contract updates required
```

Generated architecture visuals are versioned projections and become stale when their source snapshot changes.

---

# Human interaction discipline

The interaction model is deliberately staged across slices.

**VS1** supports simple immediate annotation decisions only: `accept`, `edit`, and `reject`. VS1 also establishes the reusable foundations: append-only event history, stable subject/object identifiers, annotation history, and generic decision provenance.

**VS2** activates the richer human-interaction model: pending/answered/deferred/reopened/superseded states, staged changes before sending to an agent, per-object discussion, and batched coherent guidance/decisions.

This separation is intentional so VS1 failures can be attributed cleanly to data, model, MAF, persistence, or basic UI behaviour rather than a complex interaction state machine.

Do not implement full event sourcing. SQLite relational tables remain authoritative for current state; the event log records provenance and interaction history.

---

# Software design clarity skill

This project consumes the independent `software-design-clarity` skill for human and coding-agent design review.

The skill is advisory and complements, rather than replaces:

```text
Ruff
    code conventions

Import Linter / Tach
    dependency and module architecture enforcement

software-design-clarity
    abstraction and design quality
```

## Required use

Invoke the skill in **review mode** before completing:

- a new architectural boundary;
- a material module/API design;
- a non-trivial refactor;
- a change that introduces a new runtime/provider abstraction;
- a coding-agent change with meaningful structural impact.

Use **design mode** before implementing a significant abstraction where the interface is not already fixed.

Use **refactoring mode** when complexity reduction itself is the objective.

## Slice-review questions

Every slice review must answer:

```text
Complexity
Did the slice make the system conceptually simpler or more complex?

Depth
Are new modules hiding substantial complexity behind small interfaces?

Dependencies
Did callers gain implementation knowledge they should not need?

Layers
Did any new layer become a pass-through or shallow wrapper?

Strategic quality
Did tactical fixes or special cases increase conceptual complexity?

Configuration
Did we expose choices that should remain internal policy?

Vocabulary
Did we introduce duplicate or inconsistent concepts?
```

If a material trade-off is intentionally accepted, record it in the slice review and create an ADR when it is durable/cross-cutting.

The full project-agnostic guidance lives in the standalone skill package rather than being duplicated here.


# Microsoft Agent Framework baseline

Microsoft Agent Framework is part of the project from VS1 onward. Use it as the **default orchestration/runtime substrate** for agentic workflows while keeping it behind project-owned interfaces.

Collect `FrameworkObservation` records from first use. The implementation must preserve the ability to replace MAF if evidence later demonstrates repeated, material friction that reasonable mitigation cannot resolve.

Do not spread MAF-specific types into research-domain code. Any decision to remove MAF is ADR-worthy. Durable entity/actor-style execution need not be fully implemented in VS1 unless a real VS1 workflow benefits from it; basic MAF workflow use begins in VS1.

---




# Double-Entry Review build policy

Use the bundled `double-entry-review` alpha.2 skill for material PRs/changes inside each vertical
slice. Do **not** create one DER pair merely because a slice exists.

Before starting a PR/change-sized implementation unit:

1. assess `routine` / `material` / `critical` using `11_DOUBLE_ENTRY_REVIEW_INTEGRATION.md`;
2. record hard triggers/indicators/rationale;
3. if material/critical, establish the DER evidence store and pair before substantive diary work
   where practical;
4. if scope grows from routine to material, preserve the true chronology and transition to DER
   without fabricating prior history.

For material changes:

- diary chronology is canonical;
- accepted agent/contributor work integrates diary-first through one history integrator;
- reconstruct only a verified frozen diary result;
- semantic commits express complete propositions rather than files/layers/size chunks;
- every semantic checkpoint passes its own applicable required checks;
- final diary/semantic tracked trees must match exactly;
- feedback produces versioned review rounds rather than silent history rewriting;
- DER readiness is recorded separately from slice state.

For critical changes, add independent review/owner gates proportionate to risk.

The semantic-review system may later contribute findings to DER review but never supplies DER
approval authority.


# Routing subsystem implementation contract

The build must follow `10_MODEL_ROUTING_SUBSYSTEM_DESIGN.md`.

VS1 should establish:

- versioned `ModelInventory` identifier;
- versioned `RoutingPolicy`;
- project default policy;
- task-level policy override;
- `TaskRequirements`;
- `RoutingDecision`;
- `ModelUsage`;
- versioned price catalogue;
- privacy/locality hard constraint;
- provider-failure classification;
- context-builder interface;
- escalation provenance.

Do not hard-code concrete model names in application or research-domain modules.

## Mid-task changes

The schema must support future:

- one-off model override;
- policy escalation;
- explicit `RoutingPolicyTransition`;
- structured `AgentHandoff`.

The UI for those features does not need to be fully exposed in VS1 if only one policy is configured.

## Definition of done for routed model calls

Every routed invocation must record:

```text
inventory version
policy version
task class
routing decision
model/provider
input/output token usage
spend estimate/provider cost where available
turnaround
outcome
```

A local/private-only task must fail closed rather than silently escalating to a remote provider.


# Model usage telemetry baseline

VS1 must establish the common telemetry schema for routed model work.

Capture:

- routing policy version and task class;
- selected model/provider and escalation source;
- provider/runtime-reported token usage where available;
- cached-input/reasoning token categories where exposed;
- versioned estimated hosted-model spend;
- provider-reported spend where available;
- queue time;
- time-to-first-token;
- generation time;
- total turnaround;
- outcome.

Use SQLite for live operational records.

Completed usage history should be exportable/materialisable to Parquet for DuckDB analysis.

Maintain a versioned model-price catalogue so historical cost estimates do not change when provider prices change.

For local models, record zero API spend; do not invent electricity/hardware amortisation.

## Minimal live UI

During model/agent work, display only:

```text
Model · input/output tokens · estimated spend/local · elapsed
```

Example:

```text
Cloud model · 12.8k in / 1.4k out · ~$0.05 · 18s
```

or:

```text
Local model · 12.8k in / 1.4k out · local · 18s
```

The display must remain visually secondary. Detailed routing/cost/token information belongs behind a drill-down.



# VS1 integration preflight

The design bundle is sufficient to begin bootstrap, but external integrations must be verified before relying on them in live execution.

At the start of VS1, verify and record:

- actual availability of at least one model/provider compatible with the configured routing policy;
- authentication/connectivity needed for that provider/runtime;
- access to the selected first public dataset and the exact pinned revision;
- Python/runtime compatibility of the selected dependency versions;
- Microsoft Agent Framework package/API version and compatibility with the chosen Python/runtime;
- Ruff, Import Linter, Tach, DuckDB, SQLite and FastAPI dependency compatibility;
- any platform-specific constraints affecting subprocess/worktree execution.
- DER alpha.2 skill/helper availability and a writable evidence-store path outside application worktrees;
- Git repository/worktree prerequisites needed before freezing a material-change DER baseline.

These checks are **preflight validation**, not unresolved design decisions.

If a concrete integration is unavailable or incompatible:

1. record the failure and evidence;
2. prefer a compatible version/provider/runtime within the existing architectural contract;
3. update the relevant version lock/manifest;
4. create an ADR only if the resolution changes a material architectural decision.

Do not treat ordinary package-version resolution as a reason to redesign the system.


# 4. Slice 1 — Data-to-Annotation Vertical Slice

**Status:** READY  
**Goal:** Prove the foundational harness architecture.

## User-visible outcome

The user can:

1. launch the harness locally;
2. register one dataset;
3. browse records;
4. run a normalisation job;
5. view structured model output;
6. accept/edit/reject the result;
7. see annotation progress.

## Architecture exercised

```text
Browser
  ↓
FastAPI
  ↓
SQLite state
  ↓
Job / RoutingDecision
  ↓
Microsoft Agent Framework workflow
  ↓
model/provider adapter
  ↓
Parquet/DuckDB
  ↓
human annotation
```

## Must build

### Backend

- FastAPI application;
- SQLite migration setup;
- WAL mode;
- dataset registry;
- job table;
- worker process;
- annotation table;
- artefact table;
- basic structured logging;
- Ruff configuration;
- Import Linter configuration/contracts;
- Tach module map/configuration;
- canonical `check` command used by humans and agents;
- `CONTEXT.md` glossary scaffold;
- ADR and slice-review directories/templates;
- append-only `Event` table;
- versioned `ModelInventory` / `RoutingPolicy` references;
- `TaskRequirements`, `RoutingDecision` and `ModelUsage` operational records;
- project default routing policy and task-level override field;
- provider-failure classification and context-builder interface;
- typed architecture snapshot generation from Tach, Import Linter and module metadata.

### Data

- one public dataset adapter;
- canonical Parquet representation;
- DuckDB query service;
- record provenance.

### UI

- dataset list;
- observation browser;
- observation detail;
- normalisation result;
- annotation controls;
- progress display.

### Model integration

- local model abstraction;
- MAF workflow/runtime adapter as the default orchestration path;
- FrameworkObservation persistence from first MAF workflow use;
- model usage telemetry tables and price-catalog support;
- concise live model/tokens/spend/elapsed UI summary;
- structured output;
- prompt/version metadata;
- failure handling.

VS1 human interaction is limited to immediate accept/edit/reject. Rich staging, defer/reopen semantics, and per-object discussions begin in VS2.

## Acceptance criteria

- one dataset can be registered reproducibly;
- one record can be retrieved via DuckDB;
- normalisation runs outside the web process;
- job state survives application restart;
- model output is persisted with version/provenance;
- the normalisation workflow executes through the MAF orchestration path unless a documented blocker prevents it;
- at least one FrameworkObservation can be recorded and inspected;
- model token usage and turnaround are captured for a VS1 normalisation call;
- hosted-model estimated spend uses a versioned price catalogue when applicable;
- the live UI shows only the terse model/input-output-tokens/spend-or-local/elapsed summary;
- annotation is persisted in SQLite;
- annotation progress is visible;
- failed jobs are inspectable;
- no large analytical table is stored in SQLite;
- `ruff format --check .` passes;
- `ruff check .` passes;
- `lint-imports` passes;
- `tach check` passes;
- architecture exceptions/ignores are absent unless explicitly documented and approved;
- initial architecture snapshot can be generated deterministically;
- slice review template contains decision-trace and architecture-delta sections;
- project documentation references the independent `software-design-clarity` skill and its required review triggers.
- every material/critical VS1 PR/change has a recorded DER materiality assessment and required paired history;
- every completed material DER pair has checkpoint-local required evidence and exact final diary/semantic tracked-tree equivalence;
- DER readiness and slice status are recorded separately;

## Explicitly out of scope

- rule registry;
- clustering;
- repair agents;
- mutation;
- PostgreSQL;
- Redis;
- multi-user support;
- remote workers.

## Exit review

Revisit:

- SQLite schema;
- worker design;
- Parquet schema;
- UI framework choice;
- model invocation ergonomics;
- whether Import Linter contracts and Tach module boundaries remain appropriately scoped or need refinement;
- whether the architecture snapshot/delta mechanism remains lightweight and useful.

---

# 5. Slice 2 — Annotation-to-Rule Discovery

**Status:** DRAFT  
**Goal:** Turn reviewed observations into inspectable candidate rules.

## User-visible outcome

The user can:

1. browse annotated observations;
2. generate embeddings;
3. run clustering;
4. inspect clusters;
5. synthesise candidate rules;
6. attach evidence/counterexamples;
7. promote/reject a candidate.

## Architecture exercised

```text
Annotations
   ↓
embedding job
   ↓
Parquet vectors
   ↓
clustering
   ↓
candidate rule
   ↓
human decision
```

## Likely additions

- embedding job type;
- clustering job type;
- cluster entity/view;
- rule registry;
- rule evidence;
- human decision records;
- counterexample management;
- staged rule decisions;
- defer/reopen semantics;
- per-rule discussion threads;
- architecture before/delta/after view.

## MAF usage in this slice

Continue using MAF and evaluate its fit for the rule-discovery workflow.

Candidate:

```text
normalise
  ↓
validate
  ↓
request human review if needed
  ↓
persist final observation
```

MAF remains the default orchestration/runtime path and isolated behind a project-owned adapter. This slice should continue to collect framework observations rather than re-evaluate whether MAF is in scope.

## Acceptance criteria

- candidate rules trace back to source observations;
- representative examples are inspectable;
- counterexamples can be attached;
- rule state transitions are recorded;
- the rule-discovery workflow runs through the MAF path and produces framework observations suitable for later longitudinal assessment.

## Revision focus after Slice 1

Before freezing this slice, reassess:

- embedding storage;
- whether clustering belongs in-process or worker-only;
- observation schema stability;
- whether the MAF workflow pattern used in this slice remains appropriate or should be adjusted based on accumulated framework observations.

---

# 6. Slice 3 — Rule-to-Historical-Replay

**Status:** DRAFT  
**Goal:** Evaluate rules on held-out historical data.

## User-visible outcome

The user can:

1. select a rule version;
2. select a held-out split;
3. run replay;
4. inspect metrics;
5. browse true/false positives and negatives;
6. record gate decisions.

## Architecture exercised

```text
Rule version
   ↓
detector
   ↓
replay job
   ↓
result Parquet
   ↓
DuckDB metrics
   ↓
failure browser
   ↓
gate decision
```

## Likely additions

- experiment registry;
- detector registry;
- replay job type;
- result manifests;
- false-positive/false-negative views;
- gate entity;
- staged gate decisions;
- confidence interval reporting;
- versioned/stale experiment visual artefacts.

## BCA integration

Add deterministic/static feature collection here if not earlier.

## MAF evaluation focus

Evaluate MAF workflow fan-out/fan-in for replay:

```text
rule
  ↓
fan-out cases
  ↓
parallel evaluations
  ↓
aggregate
```

Evaluate MAF fan-out/fan-in against the replay requirements. A native implementation may be created only as a targeted diagnostic/reference if a concrete MAF friction hypothesis requires it; maintaining parallel runtimes is not a slice objective.

## Acceptance criteria

- rule replay is reproducible from a manifest;
- held-out results are queryable;
- false positives are inspectable;
- rule version and detector version are immutable for completed runs;
- gate decisions can cite experiment evidence;
- MAF fan-out/fan-in observations are recorded, including any targeted diagnostic comparison performed to investigate concrete friction.

---

# 7. Slice 4 — Finding-to-Agent-Repair

**Status:** DRAFT  
**Goal:** Turn a validated finding into an agent-generated candidate patch.

## Entry condition

At least one rule passes the held-out replay gate.

## User-visible outcome

The user can:

1. open a finding;
2. start a repair agent;
3. observe activity;
4. add guidance;
5. inspect the patch;
6. run tests/static checks;
7. accept/retry/reject.

## Architecture exercised

```text
Finding
  ↓
repository worktree
  ↓
agent runtime
  ↓
patch
  ↓
tests/BCA
  ↓
human decision
```

## Likely additions

- AgentRun;
- agent adapter;
- OpenCode/Codex integration;
- repository mirror/worktree manager;
- patch viewer;
- test result viewer;
- guidance records;
- patch evaluation;
- staged human guidance;
- explicit interrupted/resume event history;
- optional render/report subagent for large visual/report artefacts.

## MAF durable entity/actor-style evaluation

This is the first point at which durable MAF entity/actor-style execution is expected to become materially useful.

Use only selected repair sessions.

Evaluate durable MAF entity/session execution on selected repair sessions, using the existing project-owned runtime boundary. A native subprocess path may be used only as a targeted diagnostic/reference if needed to investigate specific framework friction.

Observe:

- restart behaviour;
- state persistence;
- human pause/resume;
- provenance;
- complexity.

## Acceptance criteria

- an agent can operate in an isolated worktree;
- generated patch is preserved;
- tests execute outside the web process;
- guidance is recorded;
- target rule is re-evaluated;
- patch decision is explicit;
- MAF remains the default agent runtime; durable entity/session use is adopted where it provides value and its operational observations are recorded.

---

# 8. Slice 5 — Repair-to-Behavioural-Evaluation

**Status:** DRAFT  
**Goal:** Strengthen patch evaluation beyond ordinary tests.

## Entry condition

Enough agent-generated patches exist to make test adequacy a real question.

## User-visible outcome

The user can:

1. select a candidate repair;
2. run targeted mutation analysis;
3. inspect mutants/survivors;
4. compare test adequacy;
5. see structural/semantic regression signals;
6. make an evidence-backed decision.

## Likely additions

- mutation job type;
- targeted mutation adapter;
- mutation results model;
- survivor categorisation;
- test-selection metadata;
- patch comparison views.

## Acceptance criteria

- mutation is change-triggered, not blanket;
- expensive analysis occurs only after cheaper gates pass;
- mutation output is linked to patch/test context;
- failed/timeout mutation jobs do not compromise harness state.

## Revision focus

Reassess whether mutation provides sufficient additional evidence to remain in the standard workflow.

---

# 9. Slice 6 — Programme Operations and Comparative Analysis

**Status:** DRAFT  
**Goal:** Make programme-level progress and cross-experiment analysis first-class.

## User-visible outcome

The user can:

- see phase/gate status;
- compare experiments;
- compare detector types;
- compare local model variants;
- view compute/cost telemetry;
- inspect framework observations;
- generate progress reports.

## Likely additions

- programme dashboard;
- experiment comparison;
- cost telemetry;
- model comparison;
- framework-observation browser;
- automated report generation.

## Acceptance criteria

- programme status is evidence-backed;
- comparisons link to raw experiment outputs;
- no KPI exists without traceable source data;
- MAF observations can be reviewed independently of research outcomes.

---

# 10. Slice 7 — Public-to-Internal Transfer

**Status:** DRAFT  
**Goal:** Extend the validated public-data machinery to internal repositories.

## Entry condition

Public-data feasibility gates pass.

## User-visible outcome

The user can:

- register internal datasets;
- distinguish global/organisation/repository rules;
- compare public-only vs organisation-specific performance;
- run held-out internal replay.

## Likely additions

- internal data namespace;
- confidentiality labels;
- organisation/repository rule levels;
- public/internal comparison views;
- stricter local-model enforcement.

## Acceptance criteria

- internal and public provenance remain distinct;
- no internal code is sent to public endpoints;
- global/public rules remain reproducible;
- incremental value of organisation/repository rules is measurable.

---

# 11. Slice 8 — Operational Hardening (Conditional)

**Status:** DRAFT / CONDITIONAL  
**Goal:** Improve reliability only if the research harness becomes long-lived.

## Trigger conditions

Build this only if one or more occur:

- daily operational use continues after research phase;
- repeated failures require stronger scheduling;
- remote workers are introduced;
- second human user becomes regular;
- artefact volume exceeds local operational comfort.

## Possible extensions

- PostgreSQL;
- Redis/RQ;
- object storage;
- authentication;
- SSE/WebSockets;
- richer frontend;
- remote workers;
- backup automation.

## Acceptance criteria

Defined only when a real trigger occurs.

---

# 12. Revision protocol after every slice

At completion of each slice, create a short review record:

```yaml
slice_review:
  slice:
  completed_at:
  delivered:
  deviations:
  architecture_observations:
  research_observations:
  performance_observations:
  framework_observations:
  technical_debt:
  decisions:
  decision_trace:
  architecture_before:
  architecture_after:
  architecture_delta:
  context_updates:
  adrs_created_or_updated:
  design_clarity_review:
  changes_to_remaining_slices:
```

The review should answer:

1. What worked as expected?
2. What was harder than expected?
3. What became unnecessary?
4. What new requirement emerged?
5. Which assumptions were falsified?
6. Do any extension triggers now apply?
7. What must change in the next slice?

---

# 13. Change control

Remaining slices may be changed freely if evidence supports it.

However, every material change should record:

```text
old assumption
new evidence
decision
affected slices
```

This prevents silent architectural drift.

---

# 14. Definition of READY

A slice becomes READY only when:

- entry conditions are satisfied;
- required entities are defined;
- UI outcomes are clear;
- acceptance criteria are testable;
- dependencies are available;
- explicit out-of-scope items are listed.

---

# 15. Definition of COMPLETE

A slice is COMPLETE only when:

- acceptance criteria pass;
- tests pass;
- documentation is updated;
- produced artefacts are reproducible;
- review record exists;
- remaining slices have been reviewed.

---

# 16. Coding-agent workflow

Coding agents should be used aggressively but with bounded tasks.

Recommended pattern:

```text
human selects slice task
      ↓
agent receives:
    architecture context
    exact acceptance criteria
    allowed files
    test expectations
      ↓
agent implements
      ↓
tests
      ↓
human/agent review
      ↓
merge
```

Parallel work is encouraged where interfaces are stable.

Examples in Slice 1:

```text
Agent A — FastAPI + SQLite foundation
Agent B — dataset adapter + Parquet
Agent C — DuckDB observation query
Agent D — annotation UI/tests
```

Do not parallelise tightly coupled schema changes without an agreed contract.

---

# 17. Handover start point

Implementation should begin with:

```text
Slice 1 — Data-to-Annotation
```

The first implementation checkpoint is:

```text
local harness starts
   ↓
dataset visible
   ↓
one record browsable
   ↓
normalisation job runs
   ↓
annotation saved
```

Once this works, review and freeze Slice 2.

---

# 18. Do not build yet

Until triggered, do not build:

- PostgreSQL;
- Redis;
- Celery;
- Kubernetes;
- remote workers;
- vector database;
- SPA rewrite;
- WebSockets;
- authentication/RBAC;
- production CI integration;
- full durable entity/actor-style MAF runtime beyond the needs demonstrated by the current slice;
- mandatory Archify runtime;
- mutation dashboard;
- internal repository integration.

---

# 19. Suggested implementation order for Slice 1

1. Repository bootstrap and initial Git repository
2. Install/static project tooling before any DER baseline is frozen
3. Configuration and VS1 integration preflight
4. Ruff configuration and canonical quality command
5. Initial Import Linter contracts
6. Initial Tach module boundaries
7. `CONTEXT.md`, ADR and slice-review scaffolding
8. DER alpha.2 availability/evidence-store setup and materiality assessment for planned PR/change units
9. SQLite migrations + WAL
10. Core domain models and append-only Event model
11. ModelInventory / RoutingPolicy / TaskRequirements contracts
12. RoutingDecision + ModelUsage + versioned price catalogue
13. Provider-failure classification + context-builder boundary
14. Microsoft Agent Framework workflow/runtime adapter
15. Dataset registration and canonical Parquet adapter
16. DuckDB query service
17. Job/worker process boundary
18. Local/provider model adapter
19. Normalisation workflow through MAF
20. Observation browser
21. Annotation API/state
22. Simple Accept/Edit/Reject UI
23. Annotation progress and terse input/output-token/spend/elapsed display
24. Architecture snapshot generation
25. Integration and restart/failure-path tests
26. For each material VS1 change: verify/freeze diary, plan propositions, reconstruct, checkpoint-verify and prove equivalence
27. Documentation updates
28. DER review/readiness check for required material changes
29. VS1 slice review, architecture delta and remaining-slice revision

The exact number of DER pairs depends on actual PR/change boundaries. Do not create one pair per slice by default.

---

# 20. Final handover instruction

The implementation team should treat this plan as:

```text
fixed immediate slice
+
provisional future slices
+
mandatory evidence-driven revision
```

The objective is not to implement the entire document unchanged.

The objective is to preserve a visible end-to-end programme while allowing each completed slice to improve the design of everything that follows.
