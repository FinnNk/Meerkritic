# Full semantic and aggregate self-review

Scope: series.json's exact base and nine semantic commits; orientation, each
proposition in order and aggregate interactions inspected. This is author
self-review, not a fresh session or an independent reviewer. No platform approval.
Read plan.md, reconstruction-attempts.md and verification-summary.json together.

P1: Instructions, guide, templates and ADR scope match. They require evidence for
all applicable guidance without creating a findings quota or EDR for incidental
testing. Fix authority remains separate from inspection. P1 keeps 94 tests green.

P2: Reviewed completion validation, SQL write triggers, outcome construction and
unchanged MAF callers. Empty errors no longer exploit truthiness; successful
metadata needs a valid digest. Tests check no extra event/state and direct SQL.
The original reconstruction missed import ordering at this checkpoint; attempt 2
moves the existing diary correction here. Corrected P2 passes 96 tests and gates.
Migration preserves prior rows; it does not silently repair corrupt history.

P3: Read store protocol, JsonResults, all publication call sites and CLI maintenance.
Explicit metadata owns job/kind independently of body keys; non-object values fail
before files. Catalogue failure can leave a complete orphan. Maintenance uses
relational references and original bytes, not JSON reserialisation. Real legacy
hash assertion and conflict/partial-failure tests retained. No optional catalogue
configuration remains. P3 passes 97 tests and gates.

P4: Traced dataset identity lookup through the registry and Parquet adapter,
annotation through only its declared reader, and CLI/web composition. Worker
acquires an OS lock before recovery or claims and releases on error; private
execution remains in the same owning module. Tests prove lock refusal does not
recover/claim, no application pagination dependence, and reader-only annotation.
Existing subprocess death/ownership/restart and end-to-end tests remain. P4 passes
100 tests and gates. Exposing the existing declared query port avoids a shallow
pass-through facade. Composition alone sees concrete service dependencies.

P5: Application task prompt is independent of model family. Adapter Qwen control
is explicit and retained in versioned template request; non-Qwen tests exclude it.
Budget counting uses the actual rendered request. No framework/provider types leak
into domain logic, and no automatic inference escalation is introduced. P5 passes
101 tests. Exact final semantic live check verifies MAF execution, prompt/provider
versions, edit/reopen and prior database backup migration. This is compatibility,
not a prompt-quality experiment or claim about model judgement.

P6: Static signature/default/field changes appear without import changes. Schema 1
pairs remain comparable, mixed schemas fail, and schema 2 regeneration is documented.
The normalised AST whitespace assertion was corrected on the diary. Signatures
include constructors but do not infer inherited/dynamic members; class decorators
are not a complete semantic API model. Those limitations do not justify pretending
the snapshot proves runtime compatibility. P6 passes 102 tests and gates.

P7: Compared backfilled descriptions to real limits, return shapes and side effects
for annotation, job inspection/logging, composition and web optional capabilities.
The build_app return annotation does not alter a FastAPI route's validation; the
public function is composition. New-interface docs remain with their earlier
behavioural propositions; this commit backfills existing operations. P7 passes 102.

P8: Checked current status descriptions against integrated main, glossary against
source identity, and implemented ADR claims against previously merged PR3. Original
historical test counts stay historical. Research/skills/config/lock are unchanged;
source-manifest hashes verify. ACTIVE does not activate VS2, whose separate plan
branch stays outside this PR. P8 passes 102 tests and gates.

P9: Milestone report covers all guidance, all findings and proportional limitations.
ADRs 0007/0008 confirmations and index agree; ADR0001 correctly remains accepted.
ADR0006 refinement retains the same process-lock policy. Owner approval/integration
are explicitly pending; final checkpoint evidence backs candidate conclusions.
P9 passes 102 tests and gates.

Aggregate: no new infrastructure, storage architecture, quality ignores or dependency
upgrades. Existing source bytes, annotation/event history and result hashes remain
intact. The migration backup preserved 1 dataset, 5 jobs, 3 annotations, 31 events
and 24 catalogue rows. Static boundary/contract/settings deltas are empty, with
intentional interface/import changes. Live final-revision worker execution succeeds
on the first explicit invocation; all test annotations are labelled functional.
Read-only reviewer query ports, terminal VS1 decisions and external evidence ownership
remain. The final semantic tree equals the frozen diary, including tests and modes;
only semantic ancestry will be submitted, not diary/archive branches.

No unresolved defect from this review remains. Public application protocols and
composition changed together with in-repository consumers; this pre-release local
application has no declared external SDK compatibility guarantee. Snapshot schema
migration is explicit. Old schema-1 evidence is retained and not reinterpreted.
Known constraints include Windows-only execution evidence, no billed provider call,
self-review, static-analysis limits, manual catalogue relocation and no automatic
orphan cleanup. The pinned Starlette/yoyo deprecation warnings are visible, not
suppressed. Repeated state initialisation remains small composition wiring without
a demonstrated performance defect; no speculative container was introduced.

The helper's first host invocation rejected sandbox-owned repository metadata.
An approved host-owned local archive clone with identical objects allowed helper
execution without global Git trust changes; equivalence-ownership-error.json
retains the failure. Canonical manifests/bundles are outside all worktrees.
