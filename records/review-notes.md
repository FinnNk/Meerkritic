# Full author self-review — VS2 grouping, round r1

Base `c9ef38f48b10d7876fe26babee36f2f15f258bf3`; diary
`0c1f39f31ba6ecba36d4568eaa66ebc54056079b`; semantic
`125fd8c055b9c110efa1c4dd31dcc661358b32bc`. This is author self-review,
not an independent reviewer or GitHub approval. Scope covers the ordered series
and aggregate result, against the active plan and milestone contract challenges.

## Ordered propositions

- P1 (`ab010c4`): reviewed guidance/plan/ADR-0009 updates against verified PR #10
  integration. It does not claim that subsequent batches or the EDR are complete.
  Canonical checkpoint: 115 tests; architecture and formatting contracts pass.
- P2 (`12f166a`): checked model/profile identity, loopback policy, zero-output
  embedding capacity, actual token bounds before inference, unknown accounting,
  vector validation, safe failures and the real MAF boundary. Existing generation
  tests retain the shared endpoint obligations. Checkpoint: 118 tests.
- P3 (`a2150f7`): traced CLI/browser -> selection -> queue -> shared lock/recovery ->
  route -> MAF -> complete Parquet/JSON publication -> terminal event. Checked
  same-origin forms, explicit fixture purpose, bounded reads, event rollback,
  orphan files, no automatic replay and fenced completion. No clustering operation
  is exposed at this checkpoint. Checkpoint: 127 tests.
- P4 (`125fd8c`): checked the embedding digest/ordered annotation prerequisite,
  cosine component algorithm, stable representative ties, outlier denominators,
  membership publication and bounded source inspection. Repeat grouping preserves
  membership; model replay is not claimed deterministic. Checkpoint: 132 tests.

All checkpoints use their own clean source, tests, lock and installed environment.
Final diary also passes 132 tests. No baseline tests or architecture ignores were
removed. Final tracked trees are exactly equal. A separate real local compatibility
run uses the exact final semantic checkout and retains its isolated synthetic runtime.

## Complexity introduced or removed

The corpus queue adds necessary invocation state without overloading source-index
jobs. One worker retains process-lock/recovery ownership, with alternating queues.
Both local adapters share endpoint validation. Numeric grouping rules remain in
the domain; transport messages do not import selection or queue internals.

## Module depth

DiscoveryService hides input resolution and queue requests. DiscoveryExecution
owns routing/runtime/publication order. SQLiteDiscovery owns transactions and
fencing; ParquetDiscovery owns complete immutable analytical publication and
verified reads. These contracts carry real obligations rather than forwarding
arbitrary payloads between layers. The small CorpusQueue port prevents a circular
worker/selection dependency without adding another operator lifecycle.

## Knowledge/dependency leakage

Web uses application ports; it does not import persistence or model frameworks.
Model-specific prefix and deployment identity stay in the adapter/profile.
MAF types stay in the concrete adapter. Vector tables and texts do not enter
SQLite. Typed architecture delta changes no layer contracts or settings.

## Layer quality and tactical cases

The separate discovery queue is justified by different input identity and durable
state, rather than convenience flags on VS1 jobs. JSON manifests are versioned
provenance documents, not hidden instructions selecting storage behaviour.
The single optional corpus queue is composition of the supported workflow, not a
speculative distributed scheduler. Restart explicitly fails uncertain work.

## Findings addressed during diary work

1. Cross-module inspection found duplicated local endpoint validation. It now has
   one common owner; existing generation and new embedding tests cover consumers.
2. A malformed runtime vector could have been accounted as model success before
   application validation. Validation now precedes usage completion; a dedicated
   negative control proves semantic-failure accounting and no vector publication.
3. Boundary review found grouped embedding/clustering assertions impeded local
   checkpoint evidence. Their distinct obligations are separate tests and accompany
   their semantic propositions. Earlier tests and failure logs remain in the diary.

These are author-detected implementation findings, not a new completed milestone
review. No unresolved finding currently prevents this bounded batch's review.

## Limits and next gate

Only Windows/Python 3.12 is exercised. Local model-file hashing plus API metadata
does not cryptographically attest the server's loaded bytes. Cosine chaining can
produce incoherent groups; the prototype has no empirical quality/adoption claim.
EDR-0001 remains draft and human labels/registered comparison remain outstanding.
ADR-0010 is proposed, despite implemented candidate code. Owner approval/integration
remain separate. Next authorised step: publish this batch, then stack rule synthesis
and later staged interaction; do not merge or start VS3.
