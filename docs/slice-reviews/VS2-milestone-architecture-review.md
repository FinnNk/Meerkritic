# VS2 milestone architecture and guidance review

Reviewed on 20 September 2026. Integrated baseline: PR #12 at
`ff9af2e68d989590ebe030002e2e3789c35efef0`, whose tree equals reviewed Batch B
head `dc6ba77119b2cf148cf014c54a7748953bd9735d`. Candidate inspection covered
Batch C through `878536e` and subsequent documented remedies. Exact frozen
diary/semantic identities and checkpoint evidence are bound in external DER
`vs2-interaction/r1`; this document does not relabel candidate checks as mainline
checks. This is author self-review, not independent review or owner approval.

The owner authorised autonomous completion and correction of findings. The review
covered project instructions, maintained development guidance, ADR/EDR lifecycle,
the frozen VS2 plan and applicable research requirements. Future-slice features
remain deferred. No live research data was modified; runtime tests used isolated
synthetic fixtures and copied compatibility state.

## Guidance assessment

| Area | Assessment and evidence |
| --- | --- |
| Scope and architecture | Traced frozen selection → embedding/grouping → synthesis → registry → staged decision/guidance. FastAPI, SQLite WAL/short transactions, DuckDB/Parquet, immutable files, one worker and owned MAF/routing ports remain. No excluded infrastructure, actors, production PR integration or repair UI was introduced. |
| Complexity and module depth | Selection hides eligibility/version resolution; registry hides immutable publication, inheritance and fencing; workspace hides atomic saved intent; guidance hides immutable context and advisory execution. The batch adapter composes the registry's canonical decision transaction rather than reproducing its invariants. See `application/rules.py`, `adapters/rules.py` and `adapters/interaction.py`. |
| States and failures | Challenged stale versions, concurrent drafts, partial writes, event rollback, invalid schema, missing/corrupt artefacts, worker interruption and retries. `test_interaction.py` and `test_guidance.py` prove whole-batch rollback and no automatic external replay. Superseded tasks retain replacement links; prior human answers remain immutable. |
| Interfaces and comments | Compared protocols with concrete stores, composition, CLI and HTTP consumers. Found missing HTTP caller contracts and two incomplete boundary validations, addressed below. New operations document effects, bounds, replay and failure meaning. Existing-handler backfill is a separate semantic proposition. |
| Runtime and routing | Real MAF remains behind embedding, synthesis and guidance ports. Model-specific execution controls remain in the llama.cpp adapter. Policies 1/2 remain immutable; version 3 adds guidance. Local-only constraints, context limits, provider/semantic failures and telemetry retain distinct meanings. Live local guidance returned advice without applying state. |
| Data, privacy and provenance | Immutable selections, model traces, rule bodies and guidance snapshots retain exact identities. Large analytical/body data stays outside SQLite. Source equality is provenance, not truth. Holdouts cannot enter rule evidence. Same-origin bounded forms, loopback transport and escaped rendering remain; local actor names are claims, not authentication. |
| Human interaction and research | VS1 immediate Accept/Edit/Reject is unchanged. VS2 has saved drafts, explicit application, defer/reopen/supersede, exact-version discussion and coherent sends. Promotion and advice do not claim validation. EDR-0001 remains draft; no human labels or comparative results were manufactured. |
| Quality and architecture observability | Canonical gates are unchanged. Negative controls exercise the intended boundary rather than failing during setup. Typed architecture schema 3 adds source freshness; one shared generator supplies CLI and harness. Before/after/delta are retained externally and read as projections, not readiness authority. |
| Delivery and knowledge | True diary chronology and failed attempts are retained. Semantic propositions separate guidance, existing-code documentation, complete staging, guidance execution and architecture/slice closure. ADR-0010/0011 follow verified owner merges; ADR-0012 remains proposed. Backlog, glossary, operation guides and remaining slices are reconciled. Imported research and pinned skills remain unchanged. |

## Findings and dispositions

These findings span build-time inspection, live compatibility and the final
milestone pass. Their discovery stages are explicit; regression tests added later
are not presented as the original discovery method.

| ID | Kind/priority | Discovery stage | Remedy and disposition |
| --- | --- | --- | --- |
| VS2-F1 | Evidence-retention defect / medium | Batch B inspection | Reject an overflowing evidence inheritance operation atomically; fixed and tested. |
| VS2-F2 | Compatibility defect / medium | Batch B request-extension inspection | Compare validated request values while preserving old artefact bytes; fixed and tested. |
| VS2-F3 | Task-contract ambiguity / medium | Batch B live compatibility | Distinguish provisional rules from demonstrated generalisability; clarified, prior insufficiency outputs retained. |
| VS2-F4 | Integrity-boundary gap / medium | Milestone path comparison | Verify immutable rule bodies before immediate decisions, as staged application already does; fixed and tested. |
| VS2-F5 | Runtime-contract gap / medium | Milestone port comparison | Revalidate complete advisory schema at the application boundary, including constructed model objects; fixed and tested. |
| VS2-F6 | Caller-documentation gap / low | Milestone handler inventory | Backfill existing discovery/rule handlers separately; document new handlers with their implementation; fixed. |

### VS2-F1: Evidence inheritance could exceed the inspection bound

**Observed issue:** the initial Batch B registry inherited all parent links, then
added new support. A parent at the 1,000-link limit could create a larger child
while reads exposed only 1,000, hiding retained evidence. The problem was found
by comparing publication arithmetic with the read and append bounds, before freeze.

**Resolution:** the registry calculates inherited plus new support before any
metadata publication and rejects an overflow without changing the current version.
The regression test fills the boundary, attempts new support and verifies every
counterexample and prior pointer remains. Original diary chronology is in
`vs2-rules/r1`; no history was rewritten to conceal the discovery.

**General pattern and earlier response:** authors and semantic reviewers must
compare composition/inheritance bounds with individual write and read bounds.
Challenge “maximum existing state plus one legitimate addition”; require explicit
rejection, pagination or another coherent policy, never silent omission. This
extends the existing state/contract challenge, not a file-size rule. The operational
limit remains a constraint to revisit if real research needs more evidence.

### VS2-F2: New defaults threatened immutable manifest compatibility

**Observed issue:** synthesis added optional request fields. A raw dictionary
comparison would reject prior embedding/grouping manifests that lacked the new
null fields, even though they represented the same request. Inspection of an
unchanged reader against the expanded model exposed the mismatch.

**Resolution:** inspection compares validated request values; old bytes and hashes
are preserved. A legacy-manifest test omits the new fields and proves readability.

**General pattern and earlier response:** whenever a persisted record changes,
the author and checkpoint reviewer should supply an actual older representation
to the new reader. Separate semantic compatibility from serialisation equality;
do not rewrite immutable evidence merely to match a new default expansion. This
does not promise arbitrary future-schema compatibility.

### VS2-F3: The task confused proposing a rule with proving generalisation

**Observed issue:** live Qwen runs returned valid insufficiency responses for
coherent synthetic concerns, describing a shared invariant as insufficiently
novel/generalised. Reading the exact prompt beside the outputs exposed a tension:
it asked for a rule while forbidding generalisation without distinguishing a
proposal from an empirical claim. These are observed outputs, not a quality study.

**Resolution:** `rule-synthesis-v2` allows a provisional shared invariant, states
that novelty is unnecessary and forbids claims of demonstrated validation or
generalisability. Subsequent compatibility produced a candidate. Earlier outputs
and the fixture correction remain in the evidence; no comparative superiority is
claimed and EDR-0001 was not retrospectively registered.

**General pattern and earlier response:** at task-contract review, authors should
compare each requested outcome with its prohibitions and supply one permitted
positive and one legitimate abstention example. Review exact provider-bound text,
not only a high-level description. If choosing between prompts on quality/cost
evidence, pre-register the applicable EDR before decision-bearing analysis.

### VS2-F4: Immediate decisions did not verify the stored body

**Observed issue:** staged application read and verified each immutable rule body,
but immediate `SQLiteRules.decide` checked only relational identity/revision. A
corrupt body could therefore receive an immediate decision even though inspection
would reject it. Comparing the two consumers of the shared invariant exposed this
gap; the earlier corruption test covered reads rather than approval writes.

**Resolution:** immediate decisions verify the body before the short transaction.
The adapter-local transaction operation documents the verified-body precondition
for batch callers. The corruption test now also attempts a decision and proves
no decision row is written. Both paths retain CAS and atomic event handling.

**General pattern and earlier response:** before accepting a new write surface,
list the entry paths for a material invariant and challenge each with corrupt or
missing evidence. Authors and reviewers should not infer write coverage from a
read-path test or assume that the UI already validated input. This is a recurrence
of the broader boundary-coverage risk highlighted in the VS1 review; the existing
guidance alone did not prevent it. Concurrent hostile mutation of local immutable
files remains outside the single-operator trust model.

### VS2-F5: Advisory coverage validation did not validate every field

**Observed issue:** the concrete MAF adapter parsed the complete response schema,
but the application initially checked only its exact target IDs. A different
runtime could return a Pydantic object constructed with an invalid advice field
and still pass coverage checks. Comparing the declared runtime port with its
concrete implementation exposed this dependency on a particular adapter.

**Resolution:** the application revalidates the complete schema before target
coverage and publication. A constructed-object negative control retains valid IDs
but an empty advice field, and proves semantic failure with no accepted response.

**General pattern and earlier response:** at runtime-port design and semantic
review, challenge a return value that satisfies one visible property but violates
another. Put canonical validation at the boundary that relies on it; annotations
or one trustworthy adapter are not validation. The test covers malformed advisory
shape, not truth or usefulness of model advice.

### VS2-F6: New HTTP surfaces lacked their caller contracts

**Observed issue:** an AST inventory of decorated handlers, followed by inspection,
found missing docstrings in discovery/rule handlers introduced during VS2, despite
the existing commenting convention. Broad route-registration docstrings did not
describe each handler's effect, bounds or conflicts.

**Resolution:** a dedicated existing-code backfill documents those handlers.
New staged/guidance/architecture handlers receive contracts in their behavioural
semantic propositions. Existing tests remain; documentation does not claim to
change runtime semantics. Maintained guides also reflect the delivered surfaces.

**General pattern and earlier response:** authors should include newly exposed
handlers and indirect entry points in their interface inventory. Checkpoint
reviewers compare the declared contract with real callers and failure tests,
rather than counting docstrings. A present sentence can still be incomplete;
future review must examine meaning. No blanket lint suppression was introduced.

## Architecture, evidence and remaining gates

The highest-value simplification remains one exclusive worker lifecycle. Adding
guidance required another work type but no distributed queue, actor runtime or
operator-managed lock choreography. The registry owns decisions; the workspace
composes that contract atomically. These are deeper modules with meaningful
responsibilities, not pass-through classes per backlog noun.

Architecture generation moved from the standalone command into a shared adapter;
the command is now an entry point. Schema 3 fingerprints behaviour/resource/config
changes as well as static declarations. Tests expose a stale view even when public
interfaces are unchanged. Projection readback verifies hashes and delta consistency.
The initial tuple/list and browser-host fixture failures are retained in
`architecture-view-checks.log`; corrected checks are separate evidence. No failing
negative control is counted as a pass.

The maintained [slice review](VS2-review.md) and [remaining-slice revision](../plans/VS3-plan.md)
separate software delivery from owner acceptance and empirical adoption. Human
labelling and a committed EDR registration remain necessary before the comparison.
No later milestone is started. These earlier-detection practices are intended
improvements; this review does not claim measured prevention effectiveness.

### Final presentation check

After the six contract findings above were addressed, final inspection found
encoding damage in the shared header, rule labels and pending telemetry. The
diary corrects these separators, including inherited labels. The original frozen
checks and reconstructed candidates remain in external evidence; affected
checkpoints are rebuilt and checked under new identities. This is a presentation
repair, not an additional empirical result. Future live review should inspect
rendered text as well as HTTP status and structured state.
