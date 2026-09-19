# Project Harness Plan

**Companion to:**  
- `01_SYSTEM_DESIGN.md`  
- `02_EXPERIMENTAL_PLAN.md`  
- `03_LOCAL_DATASET_STORAGE.md`  
- `04_COST_MODEL_AND_BUDGET_SCENARIOS.md`

**Purpose:** Define a practical, incrementally extensible web-based research harness for operating the evidence-grounded semantic code-review programme.

**Initial deployment assumption:** one user on one machine.

**Initial persistence strategy:** SQLite for mutable operational state; Parquet + DuckDB for analytical datasets and experiment outputs.

---

# 1. Executive summary

The project harness should be treated as **research infrastructure**, not as a polished application.

Its purpose is to make the programme:

- observable;
- reproducible;
- steerable;
- auditable;
- easier to parallelise across coding agents;
- easier to review at human decision points.

The initial system should favour a simple single-user architecture:

```text
Browser
   │
   ▼
FastAPI web application
   │
   ├── SQLite
   │     operational state
   │     jobs
   │     agents
   │     rules
   │     annotations
   │     decisions
   │
   ├── DuckDB
   │     analytical queries
   │     experiment summaries
   │     dataset exploration
   │
   ├── Parquet
   │     observations
   │     features
   │     experiment results
   │     embeddings metadata
   │
   ├── Filesystem
   │     logs
   │     patches
   │     reports
   │     Markdown documents
   │
   └── Worker processes
         agents
         dataset jobs
         replay
         tests
         mutation
```

The central principle is:

> **Extend the harness only when a concrete programme activity crosses a trigger threshold.**

For example:

- do not introduce Redis until local job coordination becomes unreliable;
- do not move to PostgreSQL until concurrent writers or multiple users justify it;
- do not add a vector database while DuckDB/Parquet/FAISS is sufficient;
- do not add Kubernetes simply because jobs can run in parallel;
- do not build a document-management system when Markdown rendering is enough.

The harness should grow with the research programme rather than preceding it.


---

# 1A. Microsoft Agent Framework as the default project runtime and evaluation track

Microsoft Agent Framework (MAF) should be used **for the duration of the project as the default orchestration/runtime substrate**, beginning in VS1/H0-H1.

The purpose is twofold:

1. use MAF pragmatically to support the project; and
2. collect longitudinal evidence about whether MAF is a good foundation for future agentic software projects.

MAF is therefore not merely a late-stage experiment. It is part of the normal execution path unless sustained, material friction remains after reasonable mitigation attempts.

## Architectural constraint

MAF must remain behind project-owned interfaces.

```python
class WorkflowRunner:
    async def run(self, definition, input, context): ...

class AgentRuntime:
    async def start(self, spec): ...
    async def resume(self, run_id, input): ...
    async def cancel(self, run_id): ...
```

The primary implementation is:

```text
MicrosoftAgentFrameworkWorkflowRunner
MicrosoftAgentFrameworkAgentRuntime
```

A native/local fallback may exist where useful for comparison, testing, or contingency, but MAF is the default path. Research-domain code must not depend directly on MAF-specific types.

## Usage from VS1 onward

Use MAF for real project work from the start where it naturally applies, including:

- dataset/normalisation workflows;
- human-in-the-loop normalisation/adjudication flow;
- later rule-synthesis flows;
- replay fan-out/fan-in;
- repair orchestration;
- long-running/durable agent sessions where appropriate.

Do not force every trivial operation into a MAF workflow merely for purity. Simple synchronous application logic may remain ordinary Python.

## Workflows and durable entity/actor-style execution

Evaluate both MAF workflows and the Durable Task extension over the life of the project. Durable entity/actor-style execution may enter later than basic workflows, but MAF itself is in use from VS1.

## Framework observations begin immediately

Capture `FrameworkObservation` records from VS1 onward. Include framework version, component, activity, observation type, mitigation attempted/result, evidence, severity and reproducibility.

Collect evidence throughout the project on modelling fit, state ownership, checkpointing, failure recovery, human interaction, observability, parallelism, local-model integration, framework coupling, debugging complexity, operational overhead, API stability and upgrade friction.

## Removal policy

Do not remove MAF because of isolated inconvenience.

```text
friction observed
      ↓
record observation
      ↓
attempt reasonable mitigation
      ↓
measure result
      ↓
material friction remains?
      ├── no → continue
      └── yes
            ↓
      repeated / cross-cutting?
            ├── no → continue with known limitation
            └── yes → consider replacement
```

MAF should only be removed from the default path when there is **repeated, material, unresolved friction** that significantly harms project delivery, correctness, observability, maintainability or architecture. Any removal decision is ADR-worthy.

## End-of-project assessment

Answer two separate questions:

```text
1. Was MAF suitable for this project?
2. Is MAF a good default for other agentic software projects?
```

The final assessment should distinguish workload classes. No preferred conclusion should be encoded in advance.

# 2. Objectives

The harness should support six operational domains.

## 2.1 Programme

Track:

- programme phase;
- milestones;
- experiment gates;
- blockers;
- active work;
- completed work;
- current research decisions.

## 2.2 Data

Browse and inspect:

- datasets;
- source records;
- code context;
- normalised observations;
- labels;
- weak negatives;
- verified negatives;
- splits;
- provenance.

## 2.3 Rules

Manage:

- candidate rules;
- supporting evidence;
- counterexamples;
- detector implementations;
- maturity state;
- validation results;
- promotion/retirement decisions.

## 2.4 Experiments

Track:

- configuration;
- inputs;
- model versions;
- prompt versions;
- detector versions;
- status;
- results;
- confidence intervals;
- failures;
- artefacts.

## 2.5 Agents

Support:

- starting work;
- monitoring runs;
- viewing agent context;
- guiding a running attempt;
- viewing patches;
- approving/rejecting outcomes;
- comparing attempts.

## 2.6 Documentation

Render:

- architecture docs;
- experimental plans;
- ADRs;
- EDRs;
- generated reports;
- Markdown notes;
- Mermaid diagrams.

---

# 3. Non-goals

The initial harness is not:

- a generic project-management platform;
- a replacement for Git;
- a full IDE;
- an enterprise multi-user service;
- a data warehouse;
- a workflow engine comparable to Airflow;
- a notebook platform;
- a chat application;
- a production PR review service.

These may become relevant later, but should not influence the first architecture.

---


---


# Knowledge continuity and decision trace

The harness should preserve durable project knowledge using three complementary artefacts:

```text
Vocabulary      → CONTEXT.md
Durable choices → ADRs
Slice evidence  → slice reviews + decision trace
```

## CONTEXT.md

Maintain a repository-root `CONTEXT.md` as a strict glossary of stable project terms. It should define concepts such as `Observation`, `Weak negative`, `Rule`, `Finding`, `Replay`, `Framework observation`, `Architecture snapshot`, and `Architecture delta`.

`CONTEXT.md` must remain a glossary rather than becoming another design document.

## ADRs

Store durable, consequential and hard-to-reverse architecture decisions under:

```text
docs/adr/
```

Routine implementation choices belong in code or slice reviews instead.

## Decision trace

Material decisions should be traceable from their source through implementation and verification:

```yaml
decision_trace:
  - source:
    decision:
    context_term:
    adr:
    backlog_item:
    implementation_commit:
    verification:
```

This prevents important intent from disappearing between discussion, specification and implementation.

---

## Design-quality review

The project should use the independent `software-design-clarity` skill for design-quality review.

It should be accessible to:

- coding agents;
- human reviewers.

The skill provides the fuller Ousterhout-inspired summary and review heuristics, while this harness plan keeps only the project-specific integration rules.

Use it before accepting material abstraction/API/module changes and during every slice review where structural design changed.

Its role is complementary:

```text
Ruff                → code conventions
Import Linter/Tach  → architecture legality
software-design-clarity → abstraction/design quality
```


# Baseline code-quality and architecture enforcement

These checks are mandatory from H0 and form part of the definition of done for every slice.

## Ruff — code conventions

Use Ruff as the unified Python formatter and linter [11], [12].

Required developer/CI checks:

```bash
ruff format --check .
ruff check .
```

Developer convenience may additionally use:

```bash
ruff format .
ruff check --fix .
```

Configuration belongs in `pyproject.toml` unless a strong reason emerges to separate it.

Ruff is responsible for:

- formatting;
- import sorting/conventions;
- general lint rules;
- selected bug-risk rules;
- selected modernisation rules;
- repository-wide Python code conventions.

Do not duplicate architecture rules in Ruff when they are more appropriately expressed in Import Linter or Tach.

## Import Linter — authoritative architecture contracts

Use Import Linter for explicit architectural invariants that should remain human-readable and reviewable as contracts [13].

Primary contract types expected:

```text
layers
forbidden
protected
independence
acyclic siblings
```

Examples:

- domain/application/infrastructure direction;
- UI must not depend directly on persistence;
- worker implementation must not import web-layer modules;
- model/runtime adapters must not leak into research-domain logic;
- specific internal modules may only be imported through approved façades.

Where Import Linter and Tach can express the same invariant, Import Linter should normally be the **authoritative high-level contract** unless the rule is specifically about Tach module declarations/public interfaces.

## Tach — module boundaries, interfaces and dependency graph

Use Tach to enforce the module/dependency controls supported by its configuration and layer model [14], [15], [16]:

- declared module dependencies;
- explicit public interfaces;
- absence of forbidden dependency cycles;
- module-level dependency boundaries;
- layered module relationships where they add value;
- incremental modularisation of the harness.

Required check:

```bash
tach check
```

Enable circular-dependency enforcement once the initial module map is stable:

```toml
forbid_circular_dependencies = true
```

Consider `layers_explicit_depends_on = true` once the project has enough modules that implicit lower-layer access obscures dependencies.

## Division of responsibility

```text
Ruff
    "Is this Python code conventionally and statically clean?"

Import Linter
    "Does the code obey the intended architectural contracts?"

Tach
    "Does the concrete module graph obey declared dependencies,
     interfaces and cycle/layer constraints?"
```

Avoid maintaining the same rule in all three tools unless intentional redundancy has a documented reason.

## Required local quality command

Provide a single project command, for example:

```bash
make check
```

or equivalent, that runs at minimum:

```text
ruff format --check .
ruff check .
lint-imports
tach check
unit/integration tests
```

The implementation may use another task runner, but contributors and coding agents must have one canonical command.

## Coding-agent requirement

Every coding-agent implementation task must be instructed to run the canonical quality command before presenting work as complete.

Agent acceptance is blocked by:

- Ruff formatting/lint failure;
- Import Linter contract failure;
- Tach dependency/interface/cycle failure;
- relevant test failure.

Architecture-check failures must be fixed by improving the design or deliberately revising the documented contract. Agents must not add ignore/exception rules merely to make checks pass without explicit human approval.


# Architecture snapshots and deltas

Architecture should be observable as data, not only enforced as pass/fail checks.

The harness should maintain a typed `ArchitectureSnapshot` derived primarily from:

- Tach module declarations/dependency graph;
- Import Linter contracts;
- Python package/module metadata.

A rendered diagram is a projection of this representation, not an independently maintained source of truth.

## ArchitectureSnapshot

```yaml
ArchitectureSnapshot:
  id:
  commit:
  slice:
  generated_at:
  generator_version:
  modules:
  edges:
  contracts:
  violations:
```

## ArchitectureDelta

At every slice boundary compare entry and exit snapshots:

```yaml
ArchitectureDelta:
  before_snapshot:
  after_snapshot:
  modules_added:
  modules_removed:
  modules_moved:
  edges_added:
  edges_removed:
  interfaces_changed:
  contracts_changed:
  violations_added:
  violations_resolved:
```

The slice review should determine whether material changes were intentional, whether an ADR is required, and whether Import Linter/Tach still encode the intended architecture.

Generated architecture diagrams and reports are versioned projections. If their source snapshot changes, mark them **stale** until regenerated.

Archify is not a mandatory dependency; its typed before/delta/after pattern is adopted while initial generation remains based on the project's enforced architecture tooling.

---

# 4. Initial technology choices

## 4.1 Backend

**FastAPI**

Reasons:

- Python-native;
- straightforward typed APIs;
- good fit with existing research tooling;
- easy integration with subprocesses, models and data science libraries;
- simple path to server-sent events or WebSockets later.

Use FastAPI's built-in background task support only for lightweight post-request activity. The FastAPI documentation explicitly recommends larger task systems for heavy computation that should run outside the web process [1].

Therefore:

```text
FastAPI BackgroundTasks
    suitable:
        small file writes
        metadata refresh
        report indexing

not suitable:
        model inference batches
        repository replay
        test execution
        mutation testing
        long agent sessions
```

Long-running work should be represented as explicit jobs and run by worker processes.

---

## 4.2 Operational database

**SQLite**

Use SQLite for:

- project state;
- job records;
- agent-run state;
- human decisions;
- annotations;
- rules;
- experiment manifests;
- pointers to large artefacts.

Enable WAL mode.

SQLite WAL permits readers and a writer to operate concurrently on the same host and is a good match for this single-user deployment [2].

Initial connection configuration:

```sql
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
PRAGMA busy_timeout=5000;
```

Use short transactions.

Do not store large datasets or model output blobs in SQLite.

---

## 4.3 Analytical engine

**DuckDB**

Use DuckDB for:

- querying Parquet;
- experiment aggregation;
- evaluation metrics;
- joins across observations/features/results;
- dashboard analytical queries.

DuckDB should not be used as the mutable operational database.

DuckDB supports strong single-process analytical concurrency, but its native database format is not primarily designed around many small multi-process writes [3].

Preferred pattern:

```text
workers
   ↓
write Parquet / result artefacts
   ↓
register result metadata in SQLite
   ↓
DuckDB queries Parquet
```

---

## 4.4 Analytical storage

**Parquet**

Use Parquet for:

- normalised observations;
- embedding metadata;
- structural features;
- replay results;
- benchmark outputs;
- large prediction tables.

Parquet datasets remain authoritative analytical artefacts.

DuckDB is the query engine, not the source of truth.

---

## 4.5 Frontend

Initial recommendation:

**server-rendered HTML + HTMX-style incremental updates**, or a comparably light frontend.

A React/Next.js application is not necessary initially unless the implementation team is materially faster with that stack.

Initial UI needs are primarily:

- tables;
- filters;
- forms;
- detail pages;
- progress updates;
- diff views;
- Markdown rendering;
- charts.

The harness can adopt a richer client framework later if interaction complexity crosses a defined trigger.

---

# Staged human interaction and event history

## Activation boundary: VS1 foundation, VS2 interaction model

The implementation boundary is deliberate:

**VS1** implements only simple, immediate annotation decisions:

```text
accept
edit
reject
```

and establishes the reusable substrate:

- append-only `Event` history;
- stable subject/object identifiers;
- annotation history;
- generic decision provenance.

**VS2** activates the richer interaction model:

```text
pending
answered
deferred
reopened
superseded
staged changes
per-object discussion
batched send-to-agent
```

This boundary is intentional for failure diagnosis: VS1 should validate the data/model/MAF/persistence path without simultaneously introducing a complex human-interaction state machine. The VS1 data model must nevertheless be extensible so VS2 does not require a structural rewrite.


Human decisions should be stageable rather than every UI action immediately triggering an agent.

Decision-bearing objects should support:

```text
pending
answered
deferred
reopened
superseded
```

A later decision that materially contradicts an earlier one should normally reopen the relevant decision rather than silently overwrite it.

Rules, findings, patches, gates and slice reviews may each have a bounded per-object discussion thread.

## StagedChange

```yaml
StagedChange:
  id:
  subject_type:
  subject_id:
  change_type:
  payload_json:
  status: staged | sent | cancelled
  created_at:
  sent_at:
```

The UI can allow several staged decisions/guidance items to be reviewed and sent to an agent as one coherent update.

## Append-only Event history

Do **not** turn the application into a fully event-sourced system. SQLite relational tables remain authoritative for current state.

Add an append-only event record for provenance and resumability:

```yaml
Event:
  id:
  aggregate_type:
  aggregate_id:
  event_type:
  payload_json:
  actor_type: human | agent | system
  created_at:
```

Examples include `RULE_REOPENED`, `GUIDANCE_STAGED`, `PATCH_ACCEPTED`, `SLICE_REVISED`, `AGENT_RESUMED`, and `VISUAL_MARKED_STALE`.

Interrupted agent runs preserve state, events, transcripts and artefacts, then require an explicit resume/retry decision rather than silently continuing.

Where long diagrams/reports would pollute a primary agent context, a dedicated render/report subagent may produce a versioned artefact from structured inputs.

---

# 5. Repository structure

Suggested project structure:

```text
harness/
├── app/
│   ├── api/
│   ├── pages/
│   ├── models/
│   ├── services/
│   ├── repositories/
│   ├── jobs/
│   ├── agents/
│   ├── datasets/
│   ├── experiments/
│   └── rules/
│
├── templates/
├── static/
├── migrations/
├── workers/
├── scripts/
├── tests/
├── docs/
├── config/
└── pyproject.toml
```

Keep domain boundaries explicit even though the application is initially one process.

Do not create microservices.

---

# 6. Core domain model

The following entities should exist early because later features depend on them.

## 6.1 ProgrammePhase

```yaml
ProgrammePhase:
  id
  name
  order
  status
  started_at
  completed_at
```

Example:

```text
P0 Infrastructure
P1 Normalisation
P2 Rule Discovery
P3 Held-out Detection
P4 Repair
P5 Internal Transfer
```

---

## 6.2 Gate

Represents an experimental go/no-go point.

```yaml
Gate:
  id
  phase_id
  name
  description
  status:
    not_ready
    ready
    passed
    failed
    waived
  evidence_summary
  decision_at
```

Example:

```text
G4
Held-out rule precision
```

The harness should never infer a gate outcome automatically from a single metric unless the experimental plan explicitly defines that behaviour.

---

## 6.3 WorkItem

A lightweight programme activity.

```yaml
WorkItem:
  id
  title
  phase_id
  type:
    engineering
    research
    annotation
    analysis
    documentation
  status
  owner_type:
    human
    agent
    mixed
  blocked_by
  linked_job_id
```

This should remain much lighter than Jira.

---

## 6.4 Dataset

```yaml
Dataset:
  id
  name
  revision
  source
  manifest_path
  raw_path
  derived_path
  status
```

---

## 6.5 Observation

Operational metadata only.

The large observation body remains in Parquet.

```yaml
ObservationRef:
  id
  dataset_id
  parquet_uri
  row_id
  repository_id
  source_type
  language
  split
```

---

## 6.6 Annotation

```yaml
Annotation:
  id
  observation_id
  schema_version
  decision
  issue_category
  generalisable
  notes
  created_at
```

Single user initially means no user table is required unless audit identity becomes necessary.

---

## 6.7 Rule

```yaml
Rule:
  id
  version
  name
  status
  level
  statement
  applicability
  violation_definition
  created_from_cluster
```

---

## 6.8 RuleEvidence

```yaml
RuleEvidence:
  rule_id
  observation_id
  evidence_type:
    positive
    counterexample
    false_positive
    false_negative
```

---

## 6.9 Experiment

```yaml
Experiment:
  id
  name
  experiment_type
  config_path
  status
  started_at
  completed_at
  result_manifest
```

---

## 6.10 Job

This is the central execution abstraction.

```yaml
Job:
  id
  type
  status
  priority
  created_at
  started_at
  finished_at
  pid
  working_directory
  input_manifest
  output_manifest
  log_path
  error_summary
  cancel_requested
```

States:

```text
queued
running
succeeded
failed
stale
cancel_requested
cancelled
```

---

## 6.11 AgentRun

```yaml
AgentRun:
  id
  job_id
  purpose
  client
  model
  repository
  base_commit
  finding_id
  status
  transcript_path
  patch_path
  started_at
  finished_at
```

---

## 6.12 HumanDecision

Use this for important intervention points.

```yaml
HumanDecision:
  id
  decision_type
  subject_type
  subject_id
  options
  selected_option
  rationale
  created_at
```

Examples:

```text
promote_rule
accept_patch
retry_agent
reject_cluster
approve_counterexample
```

This preserves where human judgement entered the process.

---

## 6.13 Event

Append-only provenance/interaction history. Current state remains in ordinary relational tables.

```yaml
Event:
  id
  aggregate_type
  aggregate_id
  event_type
  payload_json
  actor_type
  created_at
```

## 6.14 StagedChange

```yaml
StagedChange:
  id
  subject_type
  subject_id
  change_type
  payload_json
  status
  created_at
  sent_at
```

## 6.15 ArchitectureSnapshot

```yaml
ArchitectureSnapshot:
  id
  commit
  slice_id
  artifact_id
  generator_version
  created_at
```

The full typed graph may remain an immutable JSON artefact.

## 6.16 ArchitectureDelta

```yaml
ArchitectureDelta:
  id
  before_snapshot_id
  after_snapshot_id
  artifact_id
  created_at
```

## 6.17 DiscussionThread

```yaml
DiscussionThread:
  id
  subject_type
  subject_id
  status
  created_at
```

Messages may be represented as events or a small dedicated message table depending on implementation simplicity.

---

# 7. UI information architecture

Initial navigation:

```text
Dashboard
Programme
Datasets
Annotations
Rules
Experiments
Agents
Jobs
Documents
Architecture
Decisions
```

---

# 8. Dashboard

The dashboard should answer:

```text
Where are we?
What is running?
What needs attention?
What decision is next?
```

Initial widgets:

## Programme

```text
Phase 0  complete
Phase 1  active
Phase 2  not started
```

## Gates

```text
G1 Normaliser viable       ready
G2 Clusters coherent       blocked
G3 Rules falsifiable       not ready
```

## Jobs

```text
queued     3
running    2
failed     1
```

## Agents

```text
repair-0048       running
dataset-loader-2  complete
```

## Annotation progress

```text
173 / 500
```

Do not add complicated project charts initially.

---

# 9. Programme view

The programme page should render phases and dependencies.

Example:

```text
P0 Infrastructure
   ✓ data manifests
   ✓ local inference
   ✓ harness foundation

P1 Normalisation
   ✓ schema
   ● annotation batch 1
   ○ normaliser freeze

P2 Rule discovery
   blocked by G1
```

Each activity can link to:

- jobs;
- experiments;
- documents;
- decisions.

---

# 10. Dataset explorer

The first valuable research UI.

Features:

- dataset selector;
- filters;
- pagination;
- code/review side-by-side;
- observation metadata;
- provenance link;
- normalised output;
- simple immediate annotation controls (`accept` / `edit` / `reject`).

Do not expose defer/reopen/staging/per-object discussion in VS1; those activate in VS2.

Example:

```text
Dataset: CRC-Py

Filters
language      Python
category      error_handling
split         test
status        unreviewed

--------------------------------

Review comment

"Don't lose the original exception..."

Before code

...

After code

...

Normalised issue

...

[Accept] [Edit] [Reject]
```

DuckDB should execute analytical filtering over Parquet.

SQLite stores annotations.

---

# 11. Annotation workflow

Optimise for rapid expert review.

Initial keyboard actions:

```text
A accept
E edit
R reject
N next
P previous
```

Track:

- time spent;
- changed model fields;
- disagreement between model and human;
- reason for rejection.

The harness should support staged annotation:

```text
batch 1
    100 examples
        ↓
schema review

batch 2
    200 examples
        ↓
freeze

batch 3
    remainder
```

This mirrors the experimental plan.

---

# 12. Rule registry

The rule page should become the central research object.

Example:

```text
ERR-014
Preserve exception causality

Status
VALIDATED

Evidence
83 observations
14 repositories

Detector
semantic-v3

Performance
precision   0.91
recall      0.61

Tabs
Overview
Evidence
Counterexamples
Replay
Detectors
History
Decisions
```

Actions:

```text
Edit draft
Replay
Add counterexample
Promote
Retire
Clone version
```

Rule versions should be immutable once referenced by a completed experiment.

---

# 13. Experiment registry

Each experiment page should include:

```text
Experiment
E4-replay-017

Status
complete

Inputs
dataset      ...
split        ...
rules        ...
model        ...
prompt       ...

Outputs
results.parquet
metrics.json
report.md

Metrics
precision
recall
CI

Links
false positives
false negatives
jobs
logs
```

The harness should not compute every statistical result itself initially.

Experiment scripts may generate:

```text
results.parquet
summary.json
report.md
```

The harness registers and renders them.

---

# 14. Job execution model

Do not start with Celery/Redis.

Use:

```text
SQLite job table
+
local worker process
```

Worker loop:

```text
poll queued job
    ↓
atomically claim
    ↓
launch handler
    ↓
capture stdout/stderr
    ↓
update heartbeat
    ↓
write artefacts
    ↓
complete/fail
```

A separate process isolates heavy work from the FastAPI process.

---

# 15. Worker process

Initial:

```text
python -m harness.worker
```

One worker may execute one heavy job at a time.

Later:

```text
worker --concurrency N
```

for jobs known to be safe to parallelise.

The worker should use subprocesses for:

- coding agents;
- tests;
- repository operations;
- mutation tooling.

---

# 16. Job claiming

Use a short SQLite transaction.

Conceptually:

```sql
BEGIN IMMEDIATE;

SELECT id
FROM job
WHERE status = 'queued'
ORDER BY priority DESC, created_at
LIMIT 1;

UPDATE job
SET status = 'running',
    started_at = CURRENT_TIMESTAMP,
    worker_id = ?
WHERE id = ?;

COMMIT;
```

With one user and a small number of local workers, this is adequate.

---

# 17. Job heartbeats

Long jobs should update:

```text
last_heartbeat_at
progress_current
progress_total
progress_message
```

The UI can display:

```text
Replay
381 / 1000
38%
```

If no heartbeat arrives for a configured interval:

```text
status → stale
```

but do not automatically mark the job failed without checking process state.

---

# 18. Cancellation

Every long-running job should support:

```text
cancel_requested = true
```

The worker checks between safe units of work.

For external agent/test processes:

1. request graceful termination;
2. wait;
3. kill process tree if necessary;
4. preserve logs and partial artefacts.

---

# 19. Agent integration

Create an adapter interface.

```python
class AgentAdapter:
    start(...)
    send_guidance(...)
    status(...)
    cancel(...)
    collect_artifacts(...)
```

Initial adapters:

```text
OpenCode
Codex
```

Claude Code may follow.

OpenCode supports reusable project-local agents and subagents through `.opencode/agents` definitions [4]. This maps well to explicit harness agent roles.

---

# 20. Agent roles

Define programme-specific agent profiles.

Examples:

```text
dataset-engineer
harness-engineer
rule-synthesiser
replay-investigator
repair-agent
patch-reviewer
experiment-analyst
```

Each profile specifies:

- purpose;
- tools;
- writable directories;
- model;
- permission boundaries.

Do not give every agent unrestricted repository access.

---

# 21. Agent-run page

Show:

```text
Agent Run repair-00482

Purpose
repair finding ERR-014-882

Repository
...

Status
running

Current activity
running targeted tests

Timeline
10:11 created
10:12 repository prepared
10:14 model started
10:18 patch produced
10:19 tests running

Tabs
Summary
Transcript
Files
Patch
Tests
Evaluation
Guidance
```

---

# 22. Human guidance

The harness should allow adding guidance to a running agent.

Examples:

```text
Preserve the public API.

Investigate the failing test before changing implementation.

Do not alter this generated file.
```

Every guidance message must be persisted.

The run provenance becomes:

```text
initial task
+ agent operations
+ human guidance
+ agent continuation
```

---

# 23. Human decision points

Create explicit UI states for decisions.

Examples:

## Candidate rule

```text
[Promote to reviewed]
[Reject]
[Merge with existing]
```

## Repair attempt

```text
[Accept]
[Retry]
[Reject]
```

## Experiment gate

```text
[Pass]
[Fail]
[Waive]
```

Require rationale only for consequential transitions.

---

# 24. Patch viewer

Implement:

- unified diff;
- side-by-side diff later if needed;
- linked tests;
- linked finding;
- BCA/static deltas;
- rule re-evaluation.

Do not build a full code editor initially.

Open changed files externally when deeper editing is required.

---

# 25. Documentation view

Index Markdown files under:

```text
docs/
reports/
ADRs/
EDRs/
```

Features:

- rendered Markdown;
- Mermaid diagrams;
- full-text search;
- version/source path;
- links to experiment IDs/rule IDs.

Do not build collaborative document editing.

The filesystem/Git remains the authoring source.

---

# 26. Search

Initial search can use SQLite FTS5 for:

- rule names;
- experiment names;
- document metadata;
- job names;
- annotation notes.

Dataset-content exploration remains DuckDB-based.

Add semantic search only when a concrete retrieval need emerges.

---

# 27. Logging

Every job should produce structured logs.

Suggested format:

```json
{
  "timestamp": "...",
  "job_id": "...",
  "level": "INFO",
  "event": "test_started",
  "data": {}
}
```

Persist large logs as files.

SQLite stores:

```text
log_path
last_log_event
```

---

# 28. Artefact model

Jobs should produce immutable artefacts.

Examples:

```text
results.parquet
summary.json
patch.diff
report.md
metrics.json
stdout.log
```

Each artefact gets:

```yaml
Artifact:
  id
  job_id
  type
  path
  sha256
  size
  created_at
```

---

# 29. Provenance graph

Do not build a graph database.

Represent provenance through relational links.

Example:

```text
Observation
   ↓
RuleEvidence
   ↓
RuleVersion
   ↓
DetectorVersion
   ↓
Experiment
   ↓
Finding
   ↓
AgentRun
   ↓
PatchEvaluation
```

The UI can render this as a graph/tree.

---

# 30. Security model

Single-user does not mean no security boundaries.

Initial assumptions:

- bind web server to localhost;
- no external authentication;
- repositories treated as untrusted input;
- agent permissions constrained;
- shell commands run in controlled workspaces.

If remote access is later required, authentication becomes an extension trigger.

---

# 31. Phase-aligned implementation plan

**Nomenclature:** `H0–H6` below describe harness capability phases, not the implementation vertical slices. Build sequencing is governed by `VS1–VS8` in `06_IMPLEMENTATION_HANDOVER.md` / `IMPLEMENTATION_BACKLOG.yaml`. Research phases `P0–P5` belong to the experimental plan.

---

## Harness Phase H0 — Foundation

**When:** programme week 1.

Build:

- FastAPI app;
- SQLite schema/migrations;
- WAL mode;
- base navigation;
- programme phases;
- job table;
- worker process;
- document rendering;
- `CONTEXT.md` rendering;
- ADR index/rendering;
- append-only event table;
- dataset registry;
- Ruff configuration and canonical quality command;
- Import Linter architecture contracts;
- initial Tach module map and dependency checks.

Deliverable:

```text
ruff/import-linter/tach quality gates pass
browser opens
programme visible
dataset registered
job can run
logs visible
```

Expected agent-assisted elapsed effort:

```text
~1–2 days
```

---

## Harness Phase H1 — Observation and annotation

**Trigger:** first normaliser outputs exist.

Add:

- DuckDB dataset query service;
- observation browser;
- code/review viewer;
- annotation form;
- annotation progress;
- basic quality dashboard.

Deliverable:

```text
model prediction
    ↓
human review
    ↓
stored annotation
```

Expected elapsed effort:

```text
~1–2 days
```

---

## Harness Phase H2 — Rule discovery

**Trigger:** first clustering run produces candidate clusters.

Add:

- cluster browser;
- representative observations;
- candidate-rule page;
- counterexample management;
- rule evidence links;
- rule lifecycle state;
- staged rule decisions with defer/reopen semantics;
- per-rule discussion threads;
- first architecture before/delta/after view.

Deliverable:

```text
cluster
  ↓
candidate rule
  ↓
review decision
```

Expected elapsed effort:

```text
~1–2 days
```

---

## Harness Phase H3 — Experiment/replay

**Trigger:** first versioned rule set is ready for held-out replay.

Add:

- experiment registry;
- replay job;
- metrics rendering;
- false-positive browser;
- false-negative browser;
- detector comparison;
- gate evidence view;
- staged gate decisions;
- stale/versioned generated visual/report handling.

Deliverable:

```text
rule version
  ↓
replay
  ↓
metrics
  ↓
failure inspection
```

Expected elapsed effort:

```text
~2–3 days
```

---

## Harness Phase H4 — Agent remediation

**Trigger:** at least one rule passes the held-out replay gate.

Do **not** build repair-agent UI before this point.

Add:

- AgentRun model;
- MAF durable entity/agent-runtime evaluation for selected long-running repair sessions when the slice provides a genuine durability use case;
- agent adapter;
- repository worktree preparation;
- patch viewer;
- agent transcript;
- human guidance;
- test results;
- accept/retry/reject controls.

Deliverable:

```text
finding
  ↓
agent
  ↓
patch
  ↓
evaluation
  ↓
human decision
```

Expected elapsed effort:

```text
~2–4 days
```

---

## Harness Phase H5 — Mutation and advanced evaluation

**Trigger:** repair experiments demonstrate enough valid patches that test adequacy becomes a real question.

Add:

- mutation job type;
- mutation result viewer;
- survivor categorisation;
- patch/test/mutation trace;
- targeted retry controls.

Do not build this simply because mutation tooling exists.

---

## Harness Phase H6 — Internal data

**Trigger:** public-data feasibility gates pass.

Add:

- internal dataset namespace;
- confidentiality markers;
- source-boundary indicators;
- organisation/repository rule levels;
- public-vs-internal comparison pages.

Keep local-only deployment unless another requirement appears.

---

# 32. Extension trigger catalogue

The following triggers should govern architectural growth.

---

## 32.1 SQLite → PostgreSQL

Stay on SQLite until one or more of these occur:

### Trigger A — multiple active human users

```text
>1 concurrent person regularly writing state
```

### Trigger B — write contention

Observed repeated:

```text
SQLITE_BUSY
database locked
```

despite:

- WAL;
- short transactions;
- busy timeout.

### Trigger C — distributed workers

Workers need to update operational state from multiple machines.

### Trigger D — stronger operational requirements

Need:

- remote DB access;
- managed backup;
- HA;
- production service deployment.

Do not migrate merely because the schema grows.

---

## 32.2 Simple SQLite queue → dedicated queue

Stay with the SQLite job table while:

```text
workers <= ~4 local processes
jobs <= hundreds/day
single host
```

Extend when one or more occur:

### Trigger

- jobs execute on several machines;
- retries/dead-letter semantics become complicated;
- queue throughput becomes a bottleneck;
- task dependency scheduling becomes substantial;
- worker discovery/leases become fragile.

Candidate next step:

```text
Redis + RQ
```

or another intentionally simple job system.

Celery is justified only if advanced workflow semantics are genuinely required.

---

## 32.3 Filesystem artefacts → object storage

Stay with filesystem storage until:

- workers execute on different machines;
- artefacts must be remotely accessible;
- storage exceeds comfortable local capacity;
- versioned retention needs become operationally complex.

Next step:

```text
S3-compatible object storage
```

Do not introduce it for a single local workstation.

---

## 32.4 DuckDB/Parquet → server analytical platform

Stay local while:

- one researcher;
- analytical results fit comfortably on local storage;
- queries complete interactively;
- only one process needs write access to the DuckDB database.

Extend when:

- multiple users require concurrent analytical sessions;
- datasets exceed practical local storage;
- distributed compute is actually necessary;
- remote dashboards require central access.

Until then, DuckDB + Parquet remains preferable.

---

## 32.5 No vector DB → vector DB

Stay with:

```text
Parquet
+
embedding arrays
+
FAISS or DuckDB-supported retrieval
```

until:

- interactive semantic retrieval latency is poor;
- vectors reach millions/tens of millions at a scale that matters;
- metadata filtering becomes cumbersome;
- remote concurrent query serving is required.

A vector database should solve a measured problem.

---

## 32.6 Server-rendered UI → React/SPA

Stay simple until:

- multiple independently updating panes become common;
- agent interaction resembles a live IDE;
- client-side graph exploration becomes important;
- UI state becomes difficult to manage server-side.

A rich framework is an interaction-complexity decision, not a prestige decision.

---

## 32.7 Polling → SSE/WebSockets

Start with:

```text
browser polls job status every 2–5 seconds
```

Extend to Server-Sent Events when:

- live logs become valuable;
- agent streaming becomes part of routine use;
- polling noticeably harms UX.

Use WebSockets only if true bidirectional real-time interaction is required.

---

## 32.8 Local subprocess agents → remote agent workers

Stay local until:

- agent workloads exceed local capacity;
- multiple GPUs/hosts are used;
- repository sandboxes must run remotely.

The `AgentAdapter` interface should hide this transition.

---

## 32.9 Localhost → authenticated service

Stay localhost-only until:

- another user needs access;
- access from another machine is required;
- a remote GPU worker requires callback access.

Then add:

- authentication;
- HTTPS/reverse proxy;
- explicit user identity;
- permissions.

Do not build RBAC before multiple users exist.

---

## 32.10 Basic docs viewer → knowledge system

Stay with Markdown + search until:

- document cross-linking becomes difficult;
- generated research reports become numerous;
- semantic search provides demonstrated value.

Avoid creating another documentation platform.

---

# 33. Parallelisation model

The harness should make agent parallelism visible.

Dashboard example:

```text
ACTIVE

Agent A
dataset adapter
█████████░

Agent B
BCA integration
██████░░░░

Agent C
replay harness
████████░░

Experiment
normalisation
2,413 / 5,000

Human queue
143 / 500
```

Coding agents should implement independent workstreams concurrently where interfaces are stable.

Examples:

```text
Agent A → dataset adapters
Agent B → worker/job system
Agent C → DuckDB query layer
Agent D → annotation UI
```

Human review integrates the branches.

---

# 34. Harness self-observability

The harness should monitor itself.

Initial metrics:

- jobs queued/running/failed;
- worker heartbeat;
- average job duration;
- job failure rate;
- local disk usage;
- annotation throughput;
- agent attempt counts.

Do not deploy Prometheus/Grafana initially.

Render these from SQLite and filesystem statistics.

---

# 35. Testing strategy

## Unit tests

Cover:

- state transitions;
- dataset registration;
- rule version immutability;
- job claiming;
- cancellation;
- artefact hashing.

## Integration tests

Cover:

```text
enqueue job
    ↓
worker claims
    ↓
handler executes
    ↓
artefact produced
    ↓
UI displays result
```

## Browser tests

Initially only critical flows:

- annotation;
- rule promotion;
- experiment launch;
- agent approval.

Coding agents can generate much of this test suite.

---

# 36. Migration strategy

Use a proper SQLite migration tool from day one.

Every schema change should be reproducible.

Never perform manual production-like edits to the SQLite file.

Because initial deployment is local:

```text
backup database
run migration
verify
```

is sufficient.

---

# 37. Failure recovery

Every heavy job should be restartable from its manifest.

If the application crashes:

```text
SQLite survives
Parquet survives
logs survive
worktree survives
```

On startup:

1. locate jobs marked `running`;
2. inspect worker/PID state;
3. mark dead jobs `stale`;
4. permit retry.

Do not silently resume arbitrary agent runs.

---

# 38. Suggested API surface

Initial routes:

```text
GET  /api/programme
GET  /api/gates
GET  /api/datasets
GET  /api/observations
POST /api/annotations

GET  /api/rules
POST /api/rules
POST /api/rules/{id}/transition

GET  /api/experiments
POST /api/experiments

GET  /api/jobs
POST /api/jobs
POST /api/jobs/{id}/cancel

GET  /api/agents
POST /api/agents
POST /api/agents/{id}/guide

GET  /api/artifacts/{id}
```

Keep page routes separate from API contracts.

---

# 39. Trigger-driven roadmap

A concise view:

```text
START
  │
  ▼
H0 Foundation
  │
  │ first normaliser output
  ▼
H1 Annotation
  │
  │ first coherent clusters
  ▼
H2 Rules
  │
  │ versioned rules ready
  ▼
H3 Replay
  │
  │ rule passes G4
  ▼
H4 Agent repair
  │
  │ enough valid repairs
  ▼
H5 Mutation
  │
  │ public feasibility passes
  ▼
H6 Internal transfer
```

Architecture extensions occur separately:

```text
SQLite
  │ contention/multi-user
  ▼
PostgreSQL

SQLite queue
  │ distributed workers
  ▼
Redis/RQ or equivalent

filesystem
  │ remote workers
  ▼
object storage

server HTML
  │ interaction complexity
  ▼
SPA

polling
  │ live interaction need
  ▼
SSE/WebSockets
```

---

# 40. Estimated implementation effort

With coding agents used aggressively:

| Harness stage | Elapsed effort |
|---|---:|
| H0 Foundation | 1–2 days |
| H1 Annotation | 1–2 days |
| H2 Rules | 1–2 days |
| H3 Replay | 2–3 days |
| H4 Agent remediation | 2–4 days |
| H5 Mutation | 1–2 days |
| H6 Internal extensions | 1–3 days |

These should not be summed as a purely sequential project.

Much of the harness can be built in parallel with the underlying research programme.

A useful first version should exist within the first few days.

A mature public-research console can emerge over approximately **1–2 weeks of cumulative engineering effort**, distributed across the broader 4–6 week feasibility programme.

---

# 41. First vertical slice

Build this first:

```text
Dataset
   ↓
Observation browser
   ↓
Normaliser output
   ↓
Human annotation
   ↓
Experiment summary
```

Do not start with:

- agent chat;
- mutation dashboards;
- Gantt charts;
- distributed workers;
- semantic document search.

This vertical slice proves the state/data/UI architecture.

---

# 42. Second vertical slice

After rule discovery begins:

```text
Cluster
   ↓
Rule
   ↓
Evidence
   ↓
Replay
   ↓
False-positive inspection
```

This proves the experiment/rule architecture.

---

# 43. Third vertical slice

Only after validated rules exist:

```text
Finding
   ↓
Agent
   ↓
Patch
   ↓
Tests
   ↓
Evaluation
   ↓
Human decision
```

This proves the remediation architecture.

---

# 44. Definition of success

The harness is successful if it makes the research programme easier to operate without becoming a project of its own.

Specifically, it should allow the single researcher to answer quickly:

```text
What is running?

What failed?

What result supports this rule?

What changed between these experiments?

Why was this patch accepted?

What human decisions affected this result?

Can I reproduce it?

What should happen next?
```

If those questions are easy to answer, the harness is doing its job.

---

# References

[1] FastAPI, “Background Tasks,” FastAPI Documentation, 2026. [Online]. Available: https://fastapi.tiangolo.com/tutorial/background-tasks/. [Accessed: Sep. 19, 2026].

[2] SQLite, “Write-Ahead Logging,” SQLite Documentation, 2026. [Online]. Available: https://www.sqlite.org/wal.html. [Accessed: Sep. 19, 2026].

[3] DuckDB Foundation, “Concurrency,” DuckDB Documentation, 2026. [Online]. Available: https://duckdb.org/docs/current/connect/concurrency. [Accessed: Sep. 19, 2026].

[4] OpenCode, “Agents,” OpenCode Documentation, 2026. [Online]. Available: https://opencode.ai/v2/docs/agents. [Accessed: Sep. 19, 2026].

[5] Microsoft, “Workflow concepts,” Microsoft Agent Framework Documentation, Aug. 25, 2026. [Online]. Available: https://learn.microsoft.com/en-us/agent-framework/concepts/workflows/. [Accessed: Sep. 19, 2026].

[6] Microsoft, “Workflow capabilities,” Microsoft Agent Framework Documentation, Aug. 25, 2026. [Online]. Available: https://learn.microsoft.com/en-us/agent-framework/workflows/. [Accessed: Sep. 19, 2026].

[7] Microsoft, “Durable Task Extension for Microsoft Agent Framework,” Microsoft Learn, 2026. [Online]. Available: https://learn.microsoft.com/en-us/azure/durable-task/sdks/durable-agents-microsoft-agent-framework. [Accessed: Sep. 19, 2026].

[8] Microsoft, “Microsoft Agent Framework Workflows — Observability,” Microsoft Agent Framework Documentation, 2026. [Online]. Available: https://learn.microsoft.com/en-us/agent-framework/workflows/observability. [Accessed: Sep. 19, 2026].

[9] Microsoft, “Evaluation,” Microsoft Agent Framework Documentation, 2026. [Online]. Available: https://learn.microsoft.com/en-us/agent-framework/agents/evaluation. [Accessed: Sep. 19, 2026].

[10] Microsoft, “Agent Harness,” Microsoft Agent Framework Documentation, 2026. [Online]. Available: https://learn.microsoft.com/agent-framework/agents/harness. [Accessed: Sep. 19, 2026].


[11] Astral, “The Ruff Formatter,” Ruff Documentation, 2026. [Online]. Available: https://docs.astral.sh/ruff/formatter/. [Accessed: Sep. 19, 2026].

[12] Astral, “Configuring Ruff,” Ruff Documentation, 2026. [Online]. Available: https://docs.astral.sh/ruff/configuration/. [Accessed: Sep. 19, 2026].

[13] Import Linter, “Contract types,” Import Linter Documentation, 2026. [Online]. Available: https://import-linter.readthedocs.io/en/stable/contract_types/. [Accessed: Sep. 19, 2026].

[14] Tach, “Overview,” Tach Documentation, 2026. [Online]. Available: https://docs.gauge.sh/getting-started/introduction/. [Accessed: Sep. 19, 2026].

[15] Tach, “Configuration,” Tach Documentation, 2026. [Online]. Available: https://docs.gauge.sh/usage/configuration/. [Accessed: Sep. 19, 2026].

[16] Tach, “Layers,” Tach Documentation, 2026. [Online]. Available: https://docs.gauge.sh/usage/layers/. [Accessed: Sep. 19, 2026].

---



## Routing-domain records

The harness operational model also includes:

```text
ModelInventoryRef
TaskRequirements
RoutingPolicyRef
RoutingDecision
RoutingPolicyTransition
AgentHandoff
ProviderHealth
BudgetConstraint
ContextStrategyRef
ModelUsage
```

The authoritative schemas and invariants are defined in `10_MODEL_ROUTING_SUBSYSTEM_DESIGN.md`.

SQLite stores operational references/decisions/transitions; versioned policy/inventory definitions may remain configuration artefacts; completed usage history is exported to Parquet for DuckDB analysis.



# Double-Entry Review integration

DER is mandatory only for material/critical changes before 1.0; routine changes remain on the ordinary factory path unless DER is explicitly requested.

The harness surfaces DER for material PRs/changes without becoming DER's evidence source of truth.
Use `11_DOUBLE_ENTRY_REVIEW_INTEGRATION.md` as the project policy.

## Materiality

At change/PR planning, record:

```text
routine
material
critical
```

Apply project hard triggers first; without a hard trigger, two or more strong indicators defaults
to `material`. Reassess when scope grows.

## Harness records

Add operational references such as:

```text
MaterialityAssessment
ChangePair
ReviewRound
ReviewUnit / Proposition
CheckpointEvidence
RevisionReadiness
```

DER's external evidence store remains authoritative for its evidence records.

## Parallel agents

Multiple coding agents may work concurrently in isolated worktrees/contributor branches, but a
single history integrator owns the canonical diary/semantic pair. The harness should make the
integrator/lock visible.

## Readiness UI

Show DER readiness independently from slice status. Do not infer readiness from branch names.

## Reviewer provenance

When DER reviews are model-assisted, link optional model-routing provenance and independence
dimensions. Existing token/spend/turnaround telemetry may be associated with DER activity but is
not a readiness gate.


# Generalised model-routing control

The harness should treat routing as a reusable subsystem, using `10_MODEL_ROUTING_SUBSYSTEM_DESIGN.md` as the canonical design.

## Project and task policy selection

Each project has a default routing policy.

A task may override it.

Resolution:

```text
explicit invocation override
→ task override
→ project default
→ system default
```

## Mid-task controls

When more than one policy is configured, the harness should eventually expose:

```text
Use current policy escalation
Choose model once
Switch policy for remainder of task
```

These actions are distinct and must produce distinct provenance.

## Structured handoff

When a task changes model/policy, build an `AgentHandoff` containing:

- objective;
- acceptance criteria;
- current plan;
- completed actions;
- changed files;
- tool/test results;
- unresolved questions;
- relevant context;
- concise previous-model summary.

The raw transcript remains available but is not necessarily replayed into the new model.

## Provider state

The router should understand:

```text
healthy
degraded
rate_limited
unavailable
```

Provider failures should use infrastructure fallback rather than intelligence escalation.

## User-visible routing summary

The normal live status remains intentionally terse:

```text
Model · input/output tokens · estimated spend/local · elapsed
```

The policy name may appear adjacent to this only when useful, for example after a switch:

```text
Local-first v3 → Cloud-quality v2
```

Detailed route reasoning remains behind drill-down.

## VS1 scope

VS1 implements the routing contracts, version tracking and provenance.

The rich switch-policy UI may remain dormant until at least two policies are configured.


# Model usage, spend and turnaround telemetry

Model usage telemetry is a first-class operational concern because the project intentionally routes work across local and hosted models.

The purpose is to support later analysis of:

- routing efficiency;
- spend;
- turnaround;
- escalation;
- local/cloud mix;

without making model comparison a primary research objective.

## Operational records

Add:

```yaml
RoutingDecision:
  id
  task_id
  policy_version
  task_class
  selected_model
  selected_provider
  selected_tier
  reason_codes
  constraints_json
  created_at

ModelUsage:
  id
  agent_run_id
  job_id
  experiment_id
  routing_policy_version
  task_class
  attempt_number
  provider
  model
  local_or_remote
  route_reason
  escalation_from

  queued_at
  request_started_at
  first_token_at
  response_completed_at

  input_tokens
  cached_input_tokens
  output_tokens
  reasoning_tokens
  total_tokens
  usage_source

  queue_ms
  time_to_first_token_ms
  generation_ms
  total_turnaround_ms
  tool_wait_ms
  deterministic_validation_ms

  price_catalog_version
  estimated_total_cost
  provider_reported_cost
  cost_source
  outcome
```

Current/live records belong in SQLite.

Completed analytical history should be exported or materialised to Parquet and queried through DuckDB.

## Price catalogue

Maintain a versioned model-price catalogue.

Historical spend estimates must retain the catalogue version used at execution time.

Do not recalculate old runs using today's prices.

When actual provider request/billing cost is available, preserve both:

```text
estimated cost
provider-reported cost
```

For local models, record:

```text
API spend = 0
cost source = local_no_api_charge
```

Do not add local electricity/hardware amortisation to the near-real-time UI.

## Token accounting

Prefer:

```text
provider-reported
→ runtime-reported
→ tokenizer estimate
```

Retain cached-input and reasoning-token counts separately where available.

## Turnaround

Capture both model-call and agent/job-level timing.

At minimum:

```text
queue
time to first token
generation
end-to-end turnaround
tool/test time
```

This distinguishes a slow model from a slow tool/test workflow.

## Near-real-time UI summary

The user should see a very short status line during active work.

Hosted example:

```text
Cloud model · 12.8k in / 1.4k out · ~$0.05 · 18s
```

Local example:

```text
Local model · 12.8k in / 1.4k out · local · 18s
```

On completion, an optional concise split is:

```text
Sonnet 5 · 18.4k in / 2.1k out · ~$0.08 · 42s
```

Only show:

- model;
- tokens;
- spend or `local`;
- elapsed time.

Everything else belongs in a drill-down.

Do not place routing rationale, detailed token categories, price-table information or model comparisons in the primary workflow.

Update the display from stream/runtime events when available. Approximately 1–2 second updates are sufficient; avoid high-frequency polling solely for animation.


VS1 deliberately exposes only **Accept / Edit / Reject** as human annotation actions. An `uncertain` value may exist inside model-normalisation output or annotation metadata where the schema requires it, but it is not a fourth VS1 UI decision. Richer defer/reopen/uncertainty interaction semantics begin in VS2.
