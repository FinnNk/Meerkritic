# VS2 â€” Annotation-to-Rule Discovery

Plan revision: 9, 20 September 2026. VS2 ACTIVE. A1 is integrated in PR #10 at
`c9ef38f48b10d7876fe26babee36f2f15f258bf3`; its tree equals the reviewed head and
the locked Windows baseline passes all checks and 115 tests.
A2/A3 and B are integrated, with synthetic compatibility evidence. The owner
authorises autonomous work through the remaining batches, always using stacked PRs
at dependent batch boundaries. Freeze B and C after their software prerequisites
pass; the empirical comparison remains separately gated.

Batch A2/A3 is integrated through PR #11 at `e81c2e867e714f2fed72d235eb44ba035b4bf302`,
whose tree equals reviewed head `125fd8c055b9c110efa1c4dd31dcc661358b32bc`,
with all four checkpoint checks passing and 132 tests at its final head. Real
MAF/llama.cpp embedding and grouping compatibility passed on synthetic inputs.
Batch B was frozen against that exact predecessor before the owner merged it;
its semantic PR now targets the equivalent integrated mainline. It delivers immutable rule versions/evidence/decisions and
bounded routed MAF synthesis through the existing corpus queue. Promotion means
reviewed research candidate, never validated or deployed. EDR-0001 stays draft.

Batch B is integrated through PR #12 at `ff9af2e68d989590ebe030002e2e3789c35efef0`,
whose tree equals reviewed head `dc6ba77119b2cf148cf014c54a7748953bd9735d`.
Its three semantic checkpoints pass independently, ending at 150 tests; real
local MAF synthesis produced a traceable synthetic candidate. Batch C is frozen
against this exact prerequisite. Since the owner merged it during implementation,
Batch C targets the equivalent integrated mainline. It completes
staged interaction, guidance, architecture projection and the candidate milestone
review. Owner acceptance and the unregistered empirical study remain separate gates.

## Current closure status

The owner accepted ADR-0012 and merged PR #13 on 20 September 2026. The exact
integrated revision preserves all nine ordered reviewed trees and passed all
quality checks and 172 tests; see the [integration record](../slice-reviews/VS2-integration.md).
The earlier batch narratives below retain their historical candidate status.
Software delivery is complete. The human-reviewed corpus, registered comparison
and owner empirical decision remain outstanding; VS2 stays ACTIVE.

PR #14 is integrated at `cd0a4d8c9a254e3027513274b39ce3f65cf227d2`.
All seven ordered reviewed commit trees are preserved; an isolated locked Windows
baseline passes all checks and 172 tests. The owner explicitly agreed EDR-0001's
proposed workload and criteria on 20 September 2026. Agreement does not register it.

The next frozen software batch is **reproducible input preparation** (DER
`vs2-study-tools/r1`): deterministic source/holdout/exclusion plans, a checked
preparation log, synthetic contract tests and operator instructions. It must retain
the source bytes, every attempted record and explicit incomplete/ready/shortfall
outcomes. It must not infer verified origins, human labels or registration. No UI,
model execution or database changes are needed.

Then implement the lexical baseline, method-masked rating pack and analysis using
synthetic inputs in a separate material batch, stacked if its prerequisite is still
unmerged. Source qualification and human review remain necessary before registration;
they may proceed alongside this tooling. Follow the
[human/agent preparation steps](../development/study-preparation.md).

## Activation and first batch

Main `fa6856bff52efecba55700572cb10e67f9a8f3c0` equals the reviewed PR #9 tree.
A clean locked Windows/Python 3.12 baseline passes all checks and 102 tests.
The [milestone review](../slice-reviews/VS1-milestone-architecture-review.md) closes the six
VS1 findings; apply its generalised contract challenges before this batch's review.

Separate A1 (selection, CLI freeze and browser) from A2/A3: stable input provenance
can be established without selecting an embedding model or inventing human labels.
This is one complete prerequisite PR with several semantic commits, not a PR per
layer. Keep A2/A3 together where feasible, then B and C. Their model/corpus/EDR gates
apply before dependent work, not ordinary software correctness fixtures.

A1 freezes at most 100 explicit annotation IDs, one version per source, verified
original/edit evidence, a caller-declared holdout repository list, content identity
and atomic metadata/event registration. Accept/Edit are eligible; Reject and holdout
rows are labelled exclusions. Uncertainty is retained. VS1 lacks actor provenance:
research selections require a named curator's explicit human-review attestation;
fixture selections are labelled. This does not establish independent verification,
representativeness or EDR registration. This batch creates no live human annotations.

## Outcome and boundaries

A researcher selects explicitly reviewed observations, creates a versioned input
snapshot, runs embedding/clustering and rule synthesis in the worker through MAF,
inspects representative examples and counterexamples, and promotes or rejects
versioned candidate rules. Every rule traces back through human judgement to the
original source. Staged decisions, per-rule discussion and coherent batched
guidance become available here; they must not rewrite VS1 annotation history.

Retain FastAPI/server-rendered pages, SQLite WAL/short transactions, DuckDB,
Parquet, immutable filesystem artefacts, one worker and project-owned MAF/routing
interfaces. Heavy embedding/clustering remains outside HTTP. Store vectors and
memberships in immutable analytical files, with metadata/references in SQLite.
This is the initial prescribed architecture, not a benchmark conclusion. Revisit
only if measured evidence identifies a material problem.

## Gates for dependent work

1. Owner accepts/merges the final VS1 stack; verify the integrated proposition
   mapping and canonical checks. Preserve exact approved and mainline identities.
2. Owner reviews this plan and any durable design decisions. Bound the initial
   annotated development corpus and keep a repository-level holdout untouched.
3. Confirm actual annotation eligibility, language/content diversity and duplicate
   handling from a frozen input manifest. Automated VS1 test decisions are excluded.
4. Verify the local embedding/provider API, pinned model revision/digest, licence,
   hardware capacity and locked dependency compatibility using synthetic/pilot
   inputs. Prefer llama.cpp where it supports the chosen fixture; do not introduce
   Ollama merely for convenience. Record any concrete incompatibility before an
   alternative adapter is selected.
5. Finalise and commit the applicable EDR method, then commit its registration SHA
   and `registered` status before any decision-bearing run. The draft EDR is not
   permission to collect or analyse its evaluation data.
6. Confirm each first-batch entity/UI/acceptance contract below, practical runtime
   dependencies, out-of-scope items and DER evidence path. Freeze only the next dependent batch when its gates pass. These are operational gates, not invitations to build extra UI.

## Data and state contracts

| Record | Required identity and behaviour |
| --- | --- |
| AnnotationSelection | Immutable selection ID/version, dataset/revision/hash, exact annotation IDs, original/edit result hashes, eligibility/query version, repository split and exclusions |
| EmbeddingRun | Selection hash, model/provider revision and digest where available, preprocessing/version, dimensions, normalisation, ordered record IDs, output hash, usage and outcome |
| ClusterRun | Embedding hash, algorithm/version/parameters/seed, membership artefact, outliers, representatives and measured diagnostics; no mutable reassignment of an old run |
| RuleCandidate / RuleVersion | Stable rule ID plus immutable version, statement/scope/applicability/violation definition, synthesis prompt/schema, routing/MAF provenance and supporting cluster/annotation references |
| RuleEvidence | Typed source link: positive, counterexample, false positive, false negative or unresolved; explicit verified/weak status and annotation/result versions |
| HumanDecision | Object/version, pending/answered/deferred/reopened/superseded state, actor, rationale, timestamp and event; transitions cannot overwrite historical decisions |
| GuidanceBatch | Stable submitted batch ID, target versions and discussion references; replay-safe acknowledgement and explicit failure/unknown completion |

Reject and uncertain are not interchangeable. Rejected interpretations are not
automatically verified negatives; accept/edit eligibility is an explicit selection
policy and uncertain fields remain visible. An Edit selects its verified edited
body; Accept selects the original interpretation; both retain original provenance.
Multiple runs for one source require explicit version selection, not duplicate
counting. Do not mutate the successful VS1 result or its terminal annotation to
introduce richer VS2 state.

Exact table/class names are implementation details. Prefer a small set of deep
modules: a selection owner for eligibility/versioning, a discovery contract for
immutable run inputs/outputs, a rule registry for version/evidence transitions,
and a decision-workflow owner for staging/submission. Document each contract with
software-design-clarity before introducing it; avoid one class per backlog noun.

## Batches and semantic propositions

Use the substantial batches below, with A1 separated as explained above. Each may contain several complete semantic commits. Prefer stacked
PRs when later work depends on an unmerged predecessor; this is mandatory at batch
boundaries. Avoid many tiny PRs.
Assess materiality before each unit, keep true chronology in one external DER pair
per material PR, and challenge semantic boundaries before freezing.

### Batch A â€” reproducible discovery inputs and grouping

Overall review question: can a reviewed, versioned corpus be grouped reproducibly
without losing its human/source provenance?

- A1: immutable annotation selection and eligibility, complete with source/edit
  resolution, duplicate/version handling, corrupt/missing evidence failures and
  a browsable selection summary. No selection silently consumes later annotations.
- A2: embedding adapter and worker execution behind owned contracts, local-only
  routing, actual model/version preflight, bounded input, usage/artefact provenance
  and failure inspection. Add an embedding capability/task class through routing
  contracts rather than hard-coding a model in domain logic.
- A3: worker clustering over pinned embedding artefacts, deterministic parameter/
  seed manifest, membership/outlier output and a cluster browser with inspectable
  representatives. Required algorithm packages enter the lock only after preflight.

Acceptance: rerunning a deterministic grouping fixture preserves membership and
identity rules; a changed model/preprocessor/selection creates a new run. A model
failure cannot produce an apparently complete cluster. No source body/vector table
enters SQLite. The UI shows eligible, excluded, failed and outlier denominators.
Use synthetic deterministic fixtures for correctness; real comparative selection
is governed by the EDR, including an inconclusive/no-adoption outcome.

### Batch B â€” evidence-grounded rule synthesis and versioned registry

Overall review question: can a candidate rule be traced, challenged and revised
without overstating the source evidence?

- B1: immutable rule versions and typed supporting/counterexample links, validation
  of source/annotation identities and append-only transitions. Include a candidate
  detail view that distinguishes model proposals from human decisions.
- B2: MAF discovery/synthesis workflow over bounded cluster inputs with owned
  structured outputs, provenance, routing/usage and FrameworkObservation. Record
  failure as data; preserve rejected/invalid output for inspection. No automatic
  stronger-model escalation from infrastructure failure.
- B3: representative/evidence/counterexample inspection and explicit promote/reject
  decisions, with criteria and rationale recorded against exact versions. A rule
  promotion is a research decision, not a production deployment or replay pass.

Acceptance: every candidate links to a frozen selection and original observations;
invented/missing references fail; counterexamples retain their classification and
do not disappear on rule revision. At least one full live discovery run uses MAF
and captures framework/usage evidence. Human rejection remains a useful result.

### Batch C â€” staged research interaction and slice validation

Overall review question: can a researcher collect coherent decisions and guidance,
apply them deliberately and recover from interruption without losing intent?

- C1: pending/answered/deferred/reopened/superseded transition rules and staged
  changes. Saving a draft must not be shown as applied; applying a batch is atomic
  for operational decisions, version-checked and idempotent. Conflicts retain the
  draft and explain which target version changed.
- C2: per-rule discussion and coherent batched send-to-agent, with immutable
  submission identity, source-version binding and append-only interactions. Keep
  uncertain external completion explicit; no automatic replay. Use ordinary MAF
  execution unless a demonstrated workflow need justifies a durable session ADR.
- C3: end-to-end/restart/failure validation, typed architecture before/delta/after
  view, stale projection detection and slice review. Update ADR/EDR states with
  actual evidence; revise VS3â€“VS8 before freezing VS3.

Acceptance: staged actions survive restart, apply exactly once on identical retry,
and do not silently overwrite a concurrent version. Deferred/reopened/superseded
states have explicit source/replacement links and visible history. A sent guidance
batch is distinct from a response and from applied decisions. The architecture
view identifies its source snapshot and warns when stale.

## Empirical work and stopping rules

The first anticipated significant empirical choice is whether a candidate local
embedding/grouping method provides enough research value over a simple baseline
to become the discovery default. A [draft EDR](../edr/0001-discovery-grouping-method.md)
defines the question and remaining registration requirements. Do not use the
three automated VS1 annotations as evaluation labels. Record prior exposure to
the public sample and model outputs; keep development/pilot and evaluation units
separate. Headline generalisation must use repository-level holdouts.

Keep the first comparison small: one defensible baseline, one candidate, a fixed
human-labelled sample, explicit failure/outlier handling and quality/runtime
guardrails. Freeze exact methods, sample IDs, seeds and thresholds before running.
Do not optimise on the evaluation split or grow a benchmark grid after seeing
results. Retain adverse/inconclusive findings and let the owner decide adoption.
Larger quality or cost claims require a stronger design, not more confident prose.

No EDR is needed for ordinary schema, transaction, source-integrity or API
compatibility tests. A comparative choice that could change the default does need
one. If evidence drives a durable architecture change, record an ADR citing it.

## Validation and observability

Canonical command remains `uv run --locked python tools/check.py`; no weakened
Ruff, Import Linter, Tach or test contracts. Each semantic checkpoint verifies its
own source/lock in the required Windows context. Add other platforms only when
they are part of supported execution, recording untested contexts honestly.

Cover corrupted/missing artefacts, changed source versions, duplicate memberships,
embedding shape/NaN errors, local-only route refusal, provider/semantic/framework
failures, output-size/context bounds, orphan publication, worker death, concurrent
staged submissions and restart. Inspect live source/evidence links and SQL/Parquet
boundaries. Make deterministic replay claims only for deterministic parts.

Record per-stage queue/turnaround, known tokens, spend/price versions, output sizes
and framework observations. Explain model/embedding API accounting differences;
unknown tokens are null. Evaluate MAF friction longitudinally without inventing a
performance comparison. Typed architecture snapshots remain authoritative; visuals
are projections with snapshot identity, not a separate architecture model.

## Explicit exclusions and reconsideration triggers

Do not build production PR integration, internal repositories, repair/mutation UI,
multi-user auth, distributed workers, PostgreSQL, Redis/Celery, Kubernetes, object
storage, a vector database, an SPA rewrite, automatic policy optimisation or a full
durable MAF runtime. Rich interaction is limited to the discovery workflow.

Reconsider storage only for measured size/query/retention problems; the worker model
only for persistent contention or needed parallelism; MAF only under its repeated,
material, unresolved-friction policy and an ADR. Human labelling availability is
an input constraint: if insufficient, pause empirical adoption and retain the
explicit baseline/prototype, without fabricating labels or declaring generalisation.

## Exit and pause boundary

VS2 completion requires the full annotated-selection â†’ grouping â†’ candidate rule â†’
evidence/counterexample â†’ human decision path, real MAF use, recorded state/history,
reproducible artefact identities, all quality gates, completed material DER reviews,
an honest EDR outcome/decision where applicable, a slice review and explicit
remaining-slice revision. PR acceptance, ADR/EDR state and slice state remain distinct.

The planning-only pause is lifted by the owner. Continue through A2/A3, B and C,
publishing each completed batch for review without waiting for preceding merges.
Comparative work remains gated and EDR-0001 stays draft until genuinely registered.

## Candidate milestone review

Batch C implementation is complete for software review: staged atomic decisions,
version-bound discussion, frozen advisory guidance and typed architecture freshness.
The [slice review](../slice-reviews/VS2-review.md) records delivery, limitations and
separate owner/empirical gates. The [milestone architecture review](../slice-reviews/VS2-milestone-architecture-review.md)
records actual findings, how they were found/fixed and intended earlier detection.
[VS3 preparation and remaining-slice revision](VS3-plan.md) leaves later slices
unfrozen. No comparative quality claim or full slice closure is made while the
human-labelled corpus and EDR registration/decision remain outstanding.
