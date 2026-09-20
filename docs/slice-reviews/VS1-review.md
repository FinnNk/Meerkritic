# VS1 — Data-to-Annotation review

## Integration reconciliation — 20 September 2026

VS1 is complete after owner integration of PRs #7–#9. Main revision
`fa6856bff52efecba55700572cb10e67f9a8f3c0` exactly matches the reviewed PR #9 tree;
fresh locked Windows/Python 3.12 checks pass all gates and 102 tests. The
[milestone review](VS1-milestone-architecture-review.md) captures six findings, discovery,
fixes and earlier detection practices; ADR-0007/0008 are implemented.
Below is historical candidate evidence, not a fresh model run. Its pending-merge
statements are superseded here. VS2 plan revision 2 activates A1; EDR-0001 is draft.
Integration evidence: external DER `vs2-inputs/r1/integrated-baseline-checks.log`.

## Original candidate review (retained)


Reviewed: 20 September 2026. Scope: the complete candidate stack through
`c1d6487fe41f3165e87a2217c2733e96d5657778`, based on merged main
`b9ffa2ee49b60758dba6832f08b988f797b439af`. Implementation and local validation are
complete. The final two software PRs await owner acceptance and integration; this
review does not label their candidate tests as mainline tests or owner approval.
The [structured review](VS1-review.yaml) follows the project template.

Review [PR #7: human annotation](https://github.com/FinnNk/Meerkritic/pull/7) before
[PR #8: operational evidence and validation](https://github.com/FinnNk/Meerkritic/pull/8),
which targets #7's branch. After the first merge, reconcile the second PR's base
without losing its semantic propositions and verify the actual integrated context.
The [annotation archive](https://github.com/FinnNk/Meerkritic/tree/evidence/vs1-annotation-r1)
and [validation archive](https://github.com/FinnNk/Meerkritic/tree/evidence/vs1-validation-r1)
are evidence replicas; neither branch belongs in application ancestry.

## Delivered and confirmed

The local harness registers the pinned 1,030-record public sample, browses verified
Parquet through DuckDB, queues normalisation outside HTTP, routes a local model
call through the owned MAF adapter, persists structured interpretations and full
provenance, and supports immediate Accept/Edit/Reject with immutable history and
progress. Failed/interrupted jobs remain inspectable. Source records and upstream
labels are preserved independently of interpretations and human judgement.

Routing retains exact inventory/policy versions, context and selection reasons.
The adapter verifies the served local model and actual prompt capacity. Usage,
available token/timing fields and local spend are recorded; synthetic versioned
hosted-price tests verify accounting without making a billed hosted call. Completed
usage exports to immutable Parquet for DuckDB queries. Continuity schemas are
reserved without enabling policy switches or durable sessions.

The final candidate passes 94 tests plus Ruff, Import Linter and Tach. Each
semantic checkpoint has its own source/lock/environment verification. Typed
architecture snapshots show additions within the existing allowed dependencies;
no contract or ignore was weakened. The material DER pairs retain actual diaries,
reconstructed propositions, exact final-tree equality and review/readiness records.

Live verification used a fresh public-data runtime and the pinned llama.cpp/Qwen
fixture. Three real MAF successes received explicitly test-only Accept/Edit/Reject
decisions. A closed-port call produced a provider failure; a claimed worker exit
produced one retained interruption without automatic replay. Annotation events,
WAL, source/result denominators, artefact metadata, structured logs and usage
analytics were checked. These functional decisions are not owner-labelled research
data. Exact runs, hashes, source/model identities and reproduction method are in
the external `vs1-validation/r1` evidence and its published replica.

## What worked and what changed

| Earlier assumption or requirement | Evidence | Decision and affected work |
| --- | --- | --- |
| Preserve raw records before research interpretation | Source hashes/IDs survive registration, result publication and edits | Keep ADR-0002; VS2 references immutable annotation/result versions |
| SQLite is sufficient for local operational state | Short atomic claims, concurrent annotation retry and restart tests pass | Retain SQLite/WAL; no evidence for PostgreSQL or a distributed queue |
| Heartbeat expiry could identify abandoned work | A late heartbeat cannot prove death; process tests establish lock release | ADR-0006 uses OS ownership and explicit interruption, not replay |
| MAF can orchestrate without entering domain logic | Real graph and live calls work; copied failure exceptions initially caused friction | Pass plain failure records; keep MAF and record longitudinal observations |
| Independent progress queries describe one state | Fresh review identified possible mixed denominators | One SQLite read snapshot; carry that discipline into VS2 reporting |
| Async form handling keeps the web service responsive | Synchronous validation/filesystem work was initially on the event loop | Offload blocking storage; retain regression evidence |
| Diagnostic errors can be surfaced normally | Log export can fail after a job transition committed | Warn for automatic export; strict explicit inspection and regeneration |
| A model's quoted evidence makes its interpretation useful | Inspected output included unsupported extrapolation despite matching quotes | No quality conclusion; require human labels and pre-registered selection evidence |
| Future routing records were adequately reserved by prose | Final backlog audit required explicit schemas | Add strict transition/handoff records; keep execution deferred |

No comparative benchmark selected a model, storage system or orchestration framework
in VS1. The local model is a compatibility fixture. Timing/token observations and
correctness tests are incidental to prescribed implementation; no retrospective
EDR was manufactured. ADR-0001 remains accepted pending first real empirical use.

## Architecture and design assessment

**SQLite and events:** operational tables hold bounded metadata, versions and
append-only events. Large source, prompt/output and diagnostic bodies remain on
the filesystem or in Parquet. Annotation insertion and its event are atomic.
There is no full event-sourcing rewrite. Contention and restart tests support the
current single-worker scope, not a claim of multi-user scalability.

**Worker and MAF:** a separate process, one OS lock and short database transactions
are sufficient so far. Framework-specific execution types remain in the adapter.
Workflow observations distinguish provider, semantic and framework failure. No
repeated unresolved material MAF friction justifies removal or a durable runtime.
VS2 can use another small workflow behind the same owned boundary.

**DuckDB/Parquet:** source browsing and completed-usage analytics fit the existing
split. VS2 should start with immutable, versioned embedding/cluster artefacts and
small SQLite references. Embedding scale and query patterns must be measured
before changing storage; no vector database is justified by VS1 evidence.

**UI:** server-rendered pages support the full functional path without an SPA or
WebSockets. The JSON editor is usable for a technical prototype but has not had
an ergonomics study. Pending offset pages can shift as reviews are completed.
VS2's staged rule work needs explicit draft/apply semantics and a stable queue;
preserving terminal VS1 decisions prevents silent reinterpretation of past work.

**Design clarity:** source registration, routing, workflow, jobs and annotations
hide meaningful complexity behind owned contracts. Storage adapters own atomicity,
integrity and concurrency. The small DER reference port does not duplicate evidence
or confer approval. Composition remains separate from the worker and web layers.
No additional abstraction was introduced merely to split a commit.

## Review process and remaining limitations

The final stack balances related work in two PRs with multiple complete semantic
commits. Annotation has a separate prior-ADR status commit, durable decision/query
contract and browser application. Validation separates operational artefacts/logs,
DER indexing, routing continuity and aggregate verification. Fresh-context scoped
reviews found useful concurrency/error-handling defects. Full review is still
integrator self-review; owner review remains outstanding.

DER adds preparation, reconstruction and isolated-checkpoint cost. The retained
logs provide timestamps, but no controlled overhead comparison was conducted.
Do not infer empirical benefit or a numeric overhead estimate. Keep the material
threshold and use ordinary workflow for routine changes. If overhead becomes a
significant decision, pre-register its measurement rather than guess from anecdotes.

The tested context is Windows/Python 3.12 with the documented local GPU fixture.
No POSIX execution, billed hosted-model integration, multi-user security or hosted
CI is claimed. Existing FastAPI/httpx and SQLite adapter deprecation warnings are
recorded, not suppressed. Ruff crashed in the older ordinary workspace containing
inaccessible temporary directories; clean own-source checkouts passed unchanged
gates. Unrelated user files were not removed.

Runtime paths are fixed once catalogue metadata is published; relocation needs an
explicit migration. A failed publication may leave a complete orphan file. Logs
are regenerable snapshots, and DER status requires explicit re-indexing. Model
output and timings are stochastic, so reproduction means the same method and
traceable artefacts, not guaranteed byte-identical new generations. Independent
third-party reproduction has not yet been attempted.

## Remaining slices and next gate

- **VS2:** retain Annotation-to-Rule Discovery, adding an immutable input selection
  and explicit human-labelled eligibility before embedding. Plan worker-only heavy
  computation, no vector database, evidence/counterexample links, versioned rules,
  staged interaction and MAF observations. Pre-register any consequential method
  selection. See the [detailed VS2 plan](../plans/VS2-plan.md).
- **VS3:** retain held-out historical replay. Freeze repository-level splits and
  distinguish weak from verified negatives before reporting headline metrics.
  Pin rule, annotation and input versions rather than consuming moving defaults.
- **VS4:** retain repair with explicit resume/retry and provenance. Consider durable
  MAF sessions only when the repair workflow demonstrates a need; preserve uncertain
  completion and provider-failure distinctions.
- **VS5:** retain behavioural evaluation. Pin tests, environments, patches and
  repair/result provenance; no automatic success from model judgement alone.
- **VS6:** retain programme/comparative analysis. Build on existing usage exports
  and versioned prices; significant routing/quality/cost choices need EDRs.
- **VS7:** retain internal transfer as a separate privacy/access/licensing gate.
  Reverify local-only routing and data handling on the actual internal fixture;
  no private data has been used to claim transfer performance.
- **VS8:** remain conditional on multiple users, distributed execution, measured
  contention, remote artefacts or long-lived operational use. None was established
  here; do not pre-emptively add PostgreSQL, Redis, Kubernetes or RBAC.

VS1's candidate exit obligations are satisfied with this review and explicit
remaining-slice revision. Mainline completion still awaits the owner merging the
two software PRs and confirming their integrated state. VS2 remains DRAFT: its
reviewable plan is committed, but entry/preflight and empirical-method registration
gates must be satisfied before marking it READY. Work pauses here; no VS2 code or
decision-bearing experiment has been started, and no plan PR is opened.
