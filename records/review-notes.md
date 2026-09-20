# VS2 interaction: full author self-review

Scope: semantic base ff9af2e68d989590ebe030002e2e3789c35efef0 to eaeecaafd37883f2cb6da09d2845886413a9a530.
Frozen diary 6bf1544b1fa1f70f188ae19fd08f55df78574787, diary base
dc6ba77119b2cf148cf014c54a7748953bd9735d. This is author self-review,
not an independent review or platform approval. The owner controls acceptance.

## Orientation and proposition review

The important promises are atomic saved intent, exact-version provenance, explicit
lifecycle transitions, advice that cannot apply state, no uncertain-call replay,
and a source-bound architecture projection. Inspected the frozen plan, ADR12,
current protocols, composition, migrations, actual HTTP consumers and tests.
The project does not promise authenticated actors or hostile local-file defence.

| Proposition | Identity | Inspection and evidence |
| --- | --- | --- |
| P1 review guidance and activation | 186bff35b6410320762383e35f6229a3853c6de9 | Compared guidance/backlog/plan/ADR changes against merged PR12. No feature is claimed available early. Required checks use unchanged baseline code; owner merge is verified separately. |
| P2 existing HTTP contract backfill | 89d5fcae41c35f5716ed881615d684d072af451d | Diff contains only five discovery and five rule-handler docstrings. Existing code behaviour is unchanged; documentation describes effects and bounds. |
| P3 staged review | 55001b6374fefdaaf1634674bdb431c4af7d48e6 | Traced save/read/apply through immutable body verification and draft/target CAS. Registry owns the decision transaction; no duplicate decision logic. Read rollback, concurrency, retry, lifecycle and discussion tests. Checked direct decisions also verify bodies and defer requires reopen. UI retains rejected intent and escapes discussion. |
| P4 coherent guidance | ee351d3d7b70774c610a1e8e446c64aad8720448 | Traced selected immutable notes/versions through atomic queue registration, one-worker ownership, route binding, real MAF schema coverage and fenced completion. Application revalidates constructed objects. Later notes are absent from submitted context; old results identify historical targets. Advice never calls the decision or revision operations. |
| P5 architecture and milestone | eaeecaafd37883f2cb6da09d2845886413a9a530 | Compared the moved generator with the baseline command; same typed contract plus schema-3 fingerprint. Read resource/newline/staleness/hash/delta tests and same-generator before/after. Reviewed all-guidance findings, current statuses, EDR limitations and explicit future-slice revisions. No later slice is activated. |

## Aggregate contract challenges

- Decisions: a later stale target or event-write failure rolls back earlier decisions
  and preserves the draft. Concurrent drafts cannot both apply. Receipt replay does
  not repeat transitions. Read-only historical versions retain replacement links.
- Persistence: migrations backfill existing decisions/current candidates, SQL history
  is append-only, body publication precedes short WAL transactions, and immutable
  files remain external. Immediate/staged decisions share one canonical operation.
- Guidance: context comes only from a frozen request; selected notes must belong to
  exact targets. Bounds reject rather than truncate. Corrupt input prevents inference;
  invalid output retains the raw trace, while provider failures remain distinct.
  An interrupted completion becomes unknown on the next exclusive worker restart.
- Composition: one lock owns normalisation, discovery and guidance recovery; rotating
  queues prevent starvation in the continuous worker. No second scheduler or MAF types
  enter domain/application contracts. Local-only route failure remains closed.
- Projection: immutable before/after/delta uses one final generator, readback checks
  content and computed delta, and resource/body edits mark the view stale. A matching
  source fingerprint is explicitly not proof of check success or dynamic dependencies.
- Delivery: no existing test or architecture contract was removed/weakened. Each new
  behaviour has its evidence at the introducing checkpoint. Guidance and backfill are
  separate. Final tracked trees must match exactly; no diary/archive ancestry lands.

## Software-design-clarity assessment

Complexity is introduced by saved-intent lifecycle, CAS and asynchronous advisory
completion, and is hidden within the workspace, registry and guidance owners.
Module depth is substantive: callers submit a bounded intent/context and inspect a
result rather than coordinating transactions, immutable files and recovery themselves.
Knowledge leakage is restricted to adapter-local transaction composition; the caller
must verify bodies before the transaction, and both existing callers do so. Layers
have distinct purposes: HTTP validates bounded transport, applications prepare work,
adapters own atomic storage/framework details. No speculative configuration or
pass-through interface was added solely for a backlog noun. The highest-value
simplification is the shared worker lifecycle and canonical registry decision path.
No further material design defect was confirmed in this final scope. Dict-shaped
operational metadata and explicit local bounds remain pragmatic limitations, not
claims of an unconstrained multi-user workflow.

## Repairs and evidence limits

The maintained milestone document traces six build/live/milestone findings and their
remedies, plus final punctuation repair. Original failed fixture checks, initial
frozen checks and earlier reconstruction identities are retained. A later inspection
caught an intermediate header transplant error despite final-tree equality; see
reconstruction-correction.md. It was corrected from the same frozen content and
all affected checkpoints receive new checks. This is why tip equality is insufficient.

Final live guidance and loopback HTTP runs use isolated synthetic runtime copies.
HTTP inspection covers rendered text, saved/apply behaviour, restart retention,
historical-advice warning and architecture freshness; it is not visual layout testing.
No human labels, prompt-quality comparison or EDR adoption result is manufactured.
Windows/Python 3.12 is the required tested context. Existing dependency deprecation
warnings remain visible. No hosted CI run or independent review is claimed.

Full software delivery remains separate from owner acceptance and empirical slice
closure. EDR-0001 stays draft; VS3-VS8 remain inactive. Review readiness is recorded
only after remote archive/head/base and required hosted-context inspection.
