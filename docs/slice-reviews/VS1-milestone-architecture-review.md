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

Canonical evidence is external: DER pair `vs1-architecture-review`. Round `r1`
records the implementation and verification; `r2` adds the owner's requested
finding narratives and future-review reporting guidance without changing runtime
code. Their manifests and ledger own exact identities and readiness. The
sanitised evidence branches are `evidence/vs1-architecture-review-r1` and
`evidence/vs1-architecture-review-r2`; never merge
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

The six original findings are F1–F6. The additional interface-snapshot improvement
is retained as F7 below, separately from that original set. The following narratives
explain the inspection that exposed each issue, its resolution and the intended
earlier detection mechanism. Regression tests cited under resolution were added
or strengthened during the follow-up; they are not evidence that the original
review already had those checks. Assessment of why a gap escaped earlier review
is a process diagnosis, not a measured causal result.

### F1: Contradictory completion states

**How found and why it mattered.** Comparing the completion contract with the
store's branch conditions exposed two different meanings of success: validation
tested `error is None`, while persistence used error truthiness. The concrete
counterexample `finish(job, None, "")` could pass validation and record success
without a result. Inspection of `NormalisationOutcome` also showed independently
assignable interpretation, error and measurement fields permitting contradictions.
Passing normal successful/failed-path tests did not establish those invariants.

**Addressed.** Completion now has explicit success/failure conditions owned by
the [job store](../../src/semantic_reviewer/adapters/jobs.py), with terminal-write
constraints in migration 007. The
[outcome record](../../src/semantic_reviewer/application/normalisation.py) rejects
contradictory construction. [Job tests](../../tests/test_jobs.py) challenge empty
and whitespace errors, missing/malformed digests and direct SQL writes, checking
that rejection does not mutate state/events. [Workflow tests](../../tests/test_normalisation.py)
challenge inconsistent outcome fields. Existing corrupt history is investigated,
not silently rewritten; successful schema validation does not prove model quality.

**Generalised pattern and earlier response.** Multiple fields or layers encode
one state using slightly different predicates. Before implementation, the author
states valid combinations and their invariant owner. At the semantic checkpoint,
the reviewer compares construction, validation and persistence, challenging a
meaningful absent/empty/conflicting value and checking side effects on rejection.
If predicates diverge, consolidate the meaning at the owning boundary, constrain
persisted states where appropriate and retain the relevant regression challenge
with that proposition. A green happy path alone is insufficient evidence.

### F2: Hidden artefact publication contracts

**How found and why it mattered.** Reading the declared `ResultStore` alongside
`JsonResults`, publication callers and the maintenance CLI exposed requirements
missing from the interface. Catalogue-enabled publication inferred job/kind from
JSON keys, while optional catalogue configuration changed the obligations. The
CLI also called `index_referenced`, which the declared port did not expose. A
caller following the protocol alone could not discover the real contract.

**Addressed.** [Publication metadata and ports](../../src/semantic_reviewer/application/artefacts.py)
now declare job/kind, publication/read behaviour and separate maintenance. The
catalogue is mandatory. [The adapter](../../src/semantic_reviewer/adapters/results.py)
hides hashing, atomic publication and catalogue conflicts, while callers supply
meaning explicitly. During repair, the legacy-byte challenge also exposed the
risk of reserialising JSON during indexing; indexing now preserves the original
bytes and digest. [Artefact tests](../../tests/test_artefacts.py) cover misleading
body keys, original-byte indexing, retries, conflicts and partial failure.
[ADR-0008](../adr/ADR-0008-own-artefact-publication-metadata.md) records the choice.
Complete orphan files remain possible after a later catalogue failure.

**Generalised pattern and earlier response.** An interface looks simpler because
payload conventions, optional modes or undeclared operations hide its obligations.
Before building it, the author identifies information the caller genuinely owns.
At semantic review, compare the port, concrete implementation and at least one
real consumer, including maintenance. Challenge an innocent payload variation or
configuration change: can it silently change storage meaning or required fields?
If so, make required metadata explicit, remove an unnecessary optional mode or
declare the actual operation. Validate compatibility with real legacy shapes;
do not merely add documentation for accidental complexity that can be removed.

### F3: Complexity leaking into callers

**How found and why it mattered.** Tracing enqueue, execution and edit validation
showed repeated `source_index + 1`/page-size-one lookups. Annotation reached through
the job service to its datasets/results. Worker composition returned dependencies
that required the entry point to know lock acquisition, recovery and execution
order. These dependencies were legal to the import checkers, but callers still
needed implementation knowledge and lifecycle rules belonging further inward.

**Addressed.** [DatasetService.observation](../../src/semantic_reviewer/application/datasets.py)
owns identity lookup without a browser-page contract. Annotation receives explicit
source/result dependencies and a narrow job reader. Application-owned
[Worker.run](../../src/semantic_reviewer/application/jobs.py) owns exclusivity from
recovery through execution. [Tests](../../tests/test_jobs.py) disable application
pagination and deny the process lock to prove lookup independence and absence of
recovery/claims before exclusivity. An [annotation test](../../tests/test_annotations.py)
supplies a reader exposing only `inspect`. Existing process-death/restart tests
remain. Composition still knows concrete dependencies, as its job requires.

**Generalised pattern and earlier response.** Callers repeat representation
conversions, traverse dependency chains or coordinate another module's lifecycle.
During design/build, the author lists what each caller must know and identifies
the canonical owner of sequencing, identity and resource rules. At semantic
review, trace a real consumer and challenge whether using only its declared port
is enough; for resource ownership, try refusal or interruption at the boundary.
Move the coherent operation inward when that removes caller obligations. Retain
direct query ports where appropriate; do not replace leakage with forwarding-only
layers or split modules merely to reduce their size.

### F4: Incomplete public caller documentation and types

**How found and why it mattered.** Comparing public docstrings/signatures against
implementations and consumers exposed omitted bounds, return meanings, side
effects and errors. Progress was a bare dictionary and worker composition lacked
a return contract. The commenting principle already existed, but checking for
the presence of comments did not establish that a caller could rely on them.

**Addressed.** New interfaces carry their contracts with the behavioural commits;
the separate existing-code backfill covers annotation limits/idempotence, history
ordering, job inspection/log publication, composition and optional web capabilities.
`AnnotationProgress` defines counts and denominators; worker and result interfaces
declare their shapes. See [annotation contracts](../../src/semantic_reviewer/application/annotations.py)
and [the commenting convention](../development/code-comments.md). Review compared
the text to actual branches and writes; existing functional tests still pass.
No blanket documentation/type checker or claim of exhaustive historical cleanup
was introduced.

**Generalised pattern and earlier response.** An operation is documented but its
usable contract is incomplete or misleading. While implementing a significant
interface, the author states the information callers need without reading its
body. At semantic review, the reviewer walks one real invocation using the
declared contract: inputs/bounds, result meaning, effects, failures and retry or
ordering guarantees. Compare those claims against implementation and consumers,
then fix the contract, type shape or behaviour where they disagree. Put new-code
documentation with its code; keep unrelated existing-code backfills separately
reviewable. Appropriate functional checks remain necessary when annotations can
alter framework behaviour; prose presence or lint success is not the verdict.

### F5: Model-specific control in model-independent context

**How found and why it mattered.** Inspecting `SourceContext` alongside the llama.cpp
request construction found `/no_think` in the application task prompt and related
thinking controls at the provider boundary. The domain had no SDK imports or
model-name routing branch, yet its supposedly general prompt still assumed a
particular model convention. Dependency checks alone could not expose that coupling.

**Addressed.** The [context builder](../../src/semantic_reviewer/application/normalisation.py)
now expresses only the task. The [llama.cpp adapter](../../src/semantic_reviewer/adapters/llama.py)
applies Qwen controls for the configured family and retains the actual template
request with adapter/prompt versions. [Tests](../../tests/test_llama.py) compare
Qwen and non-Qwen routes, ensure the task request is not modified and inspect
provenance. The exact final implementation also completed through real MAF and
the pinned local fixture. That demonstrates compatibility, not comparative quality
or universal support for every model family.

**Generalised pattern and earlier response.** Vendor, model or runtime assumptions
can leak through strings, payloads and conventions even when imports are clean.
During design/build, the author separates task meaning from execution controls.
At semantic review, trace the task request through the adapter and ask what would
become invalid for another eligible provider/model. Inspect the actual retained
request, not only the selection logic. Move applicable controls into their owning
adapter, version material request changes and test both their application and
their absence where inappropriate. Use live preflight when compatibility changes;
use an EDR only if a significant empirical choice, rather than a prescribed
boundary correction, is being made.

### F6: Maintained knowledge diverging from implementation

**How found and why it mattered.** Cross-reading the delivered source/tests, guides,
glossary, backlog and ADR confirmations exposed incompatible descriptions. Guides
called delivered worker/MAF/annotation features future work; the test overview said
there were no behaviour tests. Observation meant a normalised result despite the
source-preservation decision, and `IN_PROGRESS` differed from the defined active
slice status. Older ADR text still described merged work as awaiting integration.
Checking only documents edited alongside each feature had missed accumulated drift.

**Addressed.** Maintained descriptions now match delivered VS1, Observation names
the preserved source before interpretation, the backlog uses `ACTIVE`, and ADR
confirmation prose distinguishes historical candidate evidence from later merge.
See [development status](../development/README.md), [the test overview](../../tests/README.md),
[the glossary](../../CONTEXT.md) and [the backlog](../../IMPLEMENTATION_BACKLOG.yaml).
Imported research and pinned skills remain byte-preserved; original historical
test results are not rewritten as new verification. VS2 remains inactive.

**Generalised pattern and earlier response.** Individually correct changes leave
cross-cutting status, vocabulary and usage descriptions inconsistent. Before
implementation, the author identifies which maintained claims the change may
invalidate. At aggregate PR review, the author reconciles and the reviewer compares
entry-point guidance, relevant unchanged guides, glossary/backlog and ADR/EDR
indexes against the actual delivered behaviour and integration evidence. Look
for stale future-tense, conflicting terminology and status mismatches, but judge
their meaning rather than mechanically replacing words. Update current claims,
retain historical/source records, and state uncertainty where integration or
confirmation is still pending.

### F7: Supplementary improvement to architecture evidence

The follow-up also made public signatures, class bases and annotated fields visible
in typed snapshots. A module/import-only delta could miss a changed caller contract.
[Snapshot tests](../../tests/test_architecture_snapshot.py) now challenge that case
without changing imports; schema/version limits are documented in the
[architecture guide](../architecture/README.md). This supports the earlier interface
checks for F2–F4. It is additional review evidence, not a seventh original finding
or a substitute for reading behaviour and actual consumers.

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
