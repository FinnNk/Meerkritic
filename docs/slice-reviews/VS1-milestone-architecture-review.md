# VS1 milestone architecture review

Reviewed the integrated VS1 implementation at
`0bf957bcb0ae47e2c525f5f652830c06d5b8b9c9`, tree
`c642ecd33eb8c22d27ccb7cf3012be22ed652116`, on 20 September 2026. The owner requested
assessment of all guidance, then authorised the findings, workflow improvements
and fixes in one PR. This record describes that follow-up candidate; it does not
claim its approval or integration, or activate the separate VS2 plan.

The review used the [milestone method](../development/milestone-review.md), project
instructions, active ADR/EDR policies, maintained development guides, the backlog,
the research authority hierarchy and the pinned software-design-clarity and DER
skills. It is author self-review, not independent assurance. Ordinary correctness
and compatibility checks do not require an EDR; no comparative model-quality,
performance or review-effectiveness claim is made.

Canonical evidence is external: DER pair `vs1-architecture-review`, round `r1`.
Its manifest and ledger own exact diary/semantic identities and readiness. The
sanitised evidence branch is `evidence/vs1-architecture-review-r1`; never merge
evidence ancestry into the application. Logs, methods, architecture JSON and
checkpoint records remain evidence, not a second store maintained by this report.

## Guidance assessment

| Area | Conclusion and concrete assessment |
| --- | --- |
| Scope and architecture | Traced HTTP submission → application queue → exclusive worker → routing → MAF → provider → immutable result → human annotation. FastAPI, SQLite WAL/short transactions, DuckDB/Parquet, filesystem evidence and separate execution remain intact. Import Linter/Tach declarations are unchanged; their negative controls still challenge illegal dependencies. No VS2 workflow was added. |
| Complexity and module depth | Real consumers exposed implicit payload conventions, dependency traversal and lock/recovery choreography. Explicit publication metadata, direct observation lookup and `Worker.run` now hide those mechanics at their owning boundary. Application query ports remain directly usable; no forwarding-only query facade was added. |
| States and failures | Challenged empty completion errors, missing digests, malformed terminal metadata and contradictory workflow outcomes. Validation rejects them before state/event writes; migration 007 protects new terminal writes without rewriting history. Existing ownership, interruption, storage-failure and concurrency tests remain. |
| Interfaces and comments | Compared protocols with implementations and unchanged CLI/web consumers. Maintenance now has a declared `ArtefactIndex`; progress has a typed shape; publication requires explicit metadata and catalogue storage. A constrained job reader proves annotation no longer needs the job service's dependency graph. Bounded existing-operation docstrings were backfilled separately. |
| Runtime and routing | MAF remains behind `WorkflowRunner`, with recorded framework observations. Task context no longer embeds Qwen execution controls; the llama.cpp adapter owns them and records the actual versioned request. Local-only refusal, policy precedence, context, provider/semantic failures and telemetry remain covered by the existing suite. |
| Data, privacy and provenance | Body keys cannot choose catalogue ownership/kind. Legacy non-canonical JSON is indexed from relational references without reserialising or changing its hash. Publication still precedes metadata and accepted-result references. Tests retain partial-failure/orphan behaviour, immutable events and unsafe-input checks. A backup migration preserved all prior test-runtime rows. No private/live research state was altered. |
| Human interaction and research | VS1 still exposes only Accept/Edit/Reject with immediate immutable decisions/events and coherent progress. Full-path tests cover all three actions; a new live edit retained the original model digest and survived reopening. Functional-test decisions are labelled as such. ADR-0001 remains accepted pending its first applicable pre-registered empirical decision; tests do not satisfy that confirmation. |
| Quality and observability | The canonical command passes 102 tests, Ruff, Import Linter and Tach. Schema-2 snapshots now expose static public signatures, annotated fields and class bases; a contract-only change test demonstrates visibility without a dependency change. Before/after/delta use the same generator. Each semantic checkpoint and the frozen diary additionally require their own isolated verification before publication. |
| Delivery and knowledge | Guidance, existing-code backfill and complete behavioural propositions are separate semantic units in one PR. DER retains actual chronology and adverse results. Glossary, backlog status, maintained guides, test overview and ADR integration statements were reconciled. Imported source/skill bytes remain unchanged. The separate VS2 plan must be reconciled with this review before activation. |

## Findings and dispositions

| ID | Kind/priority | Original gap and governing obligation | Remedy and validation |
| --- | --- | --- | --- |
| F1 | Correctness, high | `finish(job, None, "")` could produce success without a result; workflow outcome fields could disagree. Valid states and honest provenance must be enforced by their owner. | Fixed: store validation, terminal-write triggers and outcome validation. Counterexamples leave job state/events unchanged; direct SQL malformed digest/blank error writes fail. No automatic repair of old corrupt records. |
| F2 | Contract/design, medium | Generic result bodies carried undocumented job/kind conventions, optional catalogue behaviour and undeclared maintenance. | Fixed: `Publication`, mandatory catalogue and separate `ResultStore`/`ArtefactIndex` contracts. Body-key deception, non-object input, retry/conflict and old-byte indexing tests challenge the actual boundary. ADR-0008 records the durable choice. |
| F3 | Complexity/ownership, medium | Callers used pagination for identity lookup, traversed service dependencies and assembled worker lock/recovery order. | Fixed: direct observation lookup, explicit annotation dependencies and a worker that owns exclusivity through recovery/execution. Tests disable application paging and deny the worker lock to prove consumers cannot accidentally perform those operations first. |
| F4 | Documentation/interface, medium | Public contracts omitted return meaning, bounds, side effects and failure behaviour; progress and worker composition were insufficiently typed. | Fixed within the reviewed operations: typed progress/worker/result contracts and separately committed backfill. Compared documentation against actual reads, writes, limits and exceptions; no blanket docstring lint or speculative typing framework. |
| F5 | Boundary, medium | `/no_think` lived in model-independent task context as well as provider controls. | Fixed: adapter-owned Qwen control, prompt `normalisation-v2`, adapter `llama-native-v2`, with actual request provenance. Unit checks distinguish Qwen/non-Qwen routes; the live pinned fixture completed through MAF with the new boundary. |
| F6 | Knowledge drift, medium | Delivered features appeared as future work; Observation terminology contradicted preserved-source identity; the backlog used an undefined active-state spelling. | Fixed: maintained documentation and ADR confirmations reconciled, Observation defined before interpretation, backlog uses `ACTIVE`. Historical research and original check evidence remain unchanged. |
| F7 | Evidence gap, medium | Module/import snapshots could miss changes to a public method contract. | Fixed: static interface records and same-schema delta, with explicit limits. This improves review evidence without pretending to infer runtime compatibility or certify design quality. |

No original finding is deferred. The process weakness was principally insufficient
application of existing principles. ADR-0007 adds milestone-wide assessment and
concrete contract challenges to build/checkpoint/aggregate review, plus explicit
state/error and caller-contract fields in the slice template. This is a prescribed
working method; whether it improves review outcomes has not been measured.

## Architecture and design consequences

- **Complexity removed:** callers no longer infer artefact kind from payload shape,
  select an optional catalogue mode, derive a browser page from a source identity,
  navigate annotation dependencies through jobs, or coordinate worker lock/recovery.
- **Module depth:** `JsonResults` still owns hashing, atomic publication, integrity
  and catalogue conflicts; `Worker` owns an execution lifetime. Small typed records
  expose required knowledge without a generic artefact framework or state hierarchy.
- **Knowledge and layers:** model controls stay in the provider adapter. Application
  services still express use cases, domain code validates evidence, adapters own
  storage/runtime details, and composition wires concrete dependencies.
- **State/error design:** expected routing refusals and annotation decisions remain
  explicit results; invalid contracts raise errors before mutation. Provider and
  semantic failures remain distinct; late heartbeats cannot authorise replay.
- **Special cases:** Qwen's documented runtime convention is one explicit adapter
  case, recorded in request provenance. No caller-selectable flag was introduced.
- **Highest-leverage simplification:** ownership was moved inwards at real fault
  lines rather than splitting large modules mechanically. Repeated idempotent
  SQLite initialisation in composition remains small local wiring; a generic
  dependency container would add a new concept without resolving a demonstrated
  defect. Revisit if measured startup or migration contention makes it material.

Typed before/after/delta show no changed boundary declarations, contract declarations
or enforcement settings. Import/interface changes reflect the new artefact contract,
typed queries and execution ownership. Snapshot generation does not establish rule
compliance; the canonical checker results provide that separate evidence.

## Verification and limits

The integrated baseline passed 94 tests. Development verification of the final
behaviour passed 102 tests and all static gates on Windows/Python 3.12 with the
unchanged dependency lock. The live compatibility method uses a fresh external
runtime, revalidates the pinned 1,030-row source and runs the worker as a separate
process against the existing local llama.cpp/Qwen fixture. It completed on the first
explicit invocation. An isolated backup upgrade preserved 1 dataset, 5 jobs,
3 annotations, 31 events and 24 artefact rows exactly.

External evidence retains an early sandbox SQLite-access failure, an architecture
test's incorrect expectation about `ast.unparse` whitespace, and a working-file
mixed-line-ending formatting failure. These were diagnosed; no quality rule or
asserted behavioural obligation was weakened. Isolated semantic checks, equivalence,
review coverage and archive integrity are publication gates recorded in the DER
packet, not inferred from this development run.

Limits remain explicit: Windows is the exercised platform; no billed hosted call,
independent reviewer or newly configured hosted CI is claimed. Static snapshots
cannot infer inherited/dynamic interfaces or behavioural compatibility. Model output
can be wrong despite valid structure/grounding. Runtime relocation still needs a
catalogue-path migration; automatic orphan cleanup, distributed workers and annotation
reopening remain outside VS1. These existing constraints were inspected, not silently
expanded or presented as completed features.

ADRs 0007 and 0008 are implemented and confirmed in this candidate. ADRs 0002–0006
remain implemented; ADR-0001 remains accepted. Owner PR acceptance and integration
are outstanding. Before starting VS2, reconcile the separately committed plan with
these contracts and this milestone review, then explicitly freeze its next batch.
