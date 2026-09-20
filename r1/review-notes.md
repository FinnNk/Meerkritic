# Full semantic and aggregate self-review

Exact base fa6856bff52efecba55700572cb10e67f9a8f3c0; frozen diary f669491ca9890796fa4d8723f733506669c9b96a;
semantic 4abbcdd20f0dfe339e53f8332d3b509b07753341. Author self-review, not independent assurance.
Reviewed final source, consumers, tests, docs and ordered commit diffs/statistics. Own-source checkpoint
checks pass separately (P1 102, P2 113, P3 115); diary 115. No tests retired or ignores weakened.

P1: Reconciles actual PR9 tree/integration and records historical candidate observations as historical.
VS1 completion does not claim a fresh model-quality run. VS2 A1 activation derives from current owner
instruction; corpus, model and prospective EDR gates remain dependent requirements. Draft EDR is not
registration. Fixed stale slice index and progress statements, and checked changed Markdown links.

P2: Traced CLI -> SelectionService -> AnnotationStore.by_id/JobReader.inspect/direct source lookup ->
ResultStore.read -> snapshot policy validation -> JsonSelections. Accept/Edit choose different verified
bodies; tests deliberately make those bodies differ. Original result provenance remains in the snapshot.
Duplicate source versions fail, repeated comment IDs do not collapse source identities. Reject and holdout
remain exclusions; uncertain remains data. Research attestation is explicit and strict boolean, not actor
proof. No synthetic decision is represented as observed human research. Full sample/split remains EDR-owned.
Publication is complete before BEGIN IMMEDIATE; concurrent retry retains first ID/time and one event.
Failed event rolls back metadata; a complete orphan is documented and retryable. File failure/size bound
leave no registration. Reuse/read of changed files fails, not automatic repair. Own tests challenge the
reader-only port and forbid application pagination. Migration adds metadata/triggers without rewriting
old annotations, jobs or event bodies. The store read checks its own content, not ongoing original-file
availability. Holdout inspection itself constitutes exposure and is documented, not hidden.

P3: HTTP exposes bounded read-only metadata/detail pages and annotation IDs. Template autoescape handles
source/model strings, invalid query bounds fail before handlers, absent IDs return404, corrupt/missing
bodies409 without filesystem paths. Detail verifies snapshot schema/hash/metadata before display. List
only claims metadata. Real composed-app tests reopen the runtime, inspect exclusions and show uncertainty.
No freeze POST, model execution, new runtime dependency or framework-type leak appears in HTTP.

Aggregate: existing annotation workflow remains immediate/immutable. Application ports and concrete
composition are separated; SQL stores only summary metadata. Typed architecture before/after/delta
captures two owned modules and new signatures without boundary changes. Existing worker/MAF/routing and
negative architecture controls still pass. CLI and UI share store integrity ownership, no shallow query
facade. Documentation, glossary, backlog and ADR/EDR indexes agree; ADR9 is proposed pending owner acceptance.

Design clarity: complexity added is bounded snapshot validation/publication; callers do not manage
transactions, hashes, edited-body selection or source projection. Module depth is meaningful (freeze vs
verified storage/inspection). No provider/framework or concrete storage dependency crosses application.
Exclusion has one policy helper reused during construction and validation. A separate store is justified
because job-result catalogue requires a real job; a generic provenance framework would add complexity.
No additional tactical configuration. Highest-leverage simplification was reusing the direct observation
and reader contracts, not a new graph of forwarding services.

Earlier milestone challenges applied: F1 contradictory purpose/attestation and duplicate versions;
F2 explicit store contract including partial failure; F3 constrained reader and paging denial;
F4 bounded returns, side effects, failures compared to real callers; F5 no provider changes applicable;
F6 active docs/status/links reconciled. This shows application of checks, not measured prevention success.

Limitations: no independent reviewer/reproduction, other-platform check, live human corpus or embedding
preflight in A1. Tests use synthetic data; no EDR collection/analysis. Curator attestation is a claim and
holdouts are declared, not authenticated/enforced globally. Snapshots cap100 records/32MB; no scale claim.
Remaining model/corpus gates are explicit before grouping/adoption. No unresolved defect found in scope.
