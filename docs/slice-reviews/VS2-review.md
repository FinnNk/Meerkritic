# VS2 - Annotation-to-Rule Discovery review

Reviewed 20 September 2026. **Software accepted and integrated; slice closure
remains pending the empirical gate.** A1, A2/A3 and B are integrated through
PRs #10-#12. Batch C is integrated through PR #13 at
`f7aa4e05411da9d804f3624abe57033544fb1073`, with nine ordered reviewed trees
preserved and all quality checks and 172 tests passing on that exact revision.
See the [integration record](VS2-integration.md). The empirical study remains
unregistered and unrun.

## Delivered path

Explicit annotation versions freeze with eligibility, edits, source hashes and
holdout exclusions. A local worker embeds and groups the frozen inputs, retaining
vectors, memberships, outliers and representatives. Routed MAF synthesis proposes
an immutable rule or explains insufficient evidence. Candidate versions retain
source/cluster/model provenance, typed evidence, counterexamples and human decisions.

The researcher can save a coherent draft, apply all its decisions atomically,
defer/reopen work and inspect superseded versions. Exact-version discussion can be
sent in an immutable guidance batch. MAF returns advice without changing decisions;
unknown external completion is explicit. Architecture shows typed before/delta/after
and warns when the captured source is stale. VS1 annotations remain immediate and
immutable. The [interaction guide](../development/research-interaction.md) describes
the operation and bounds.

## Evidence and design observations

Canonical Windows/Python 3.12 checks cover source integrity, legacy manifests,
concurrent writes, atomic event rollback, saved-draft restart, idempotency, inherited
counterexamples, route/locality constraints, invalid runtime values, context bounds,
provider failures and interrupted work. Each semantic checkpoint and final diary
receives its own clean source/lock/environment verification through DER.

Real local Nomic/llama.cpp embedding and Qwen synthesis ran through MAF on synthetic
inputs in `vs2-grouping/r1` and `vs2-rules/r1`. Real advisory guidance in
`vs2-interaction/r1` used a copy of that synthetic candidate and left its rule state
unchanged. Earlier insufficiency outputs and failed checks are retained separately.
These runs establish compatibility, not a measured quality improvement.

The [milestone architecture review](VS2-milestone-architecture-review.md) assesses
all guidance and records six findings from build/live/milestone inspection with
their remedies and intended earlier detection. Complexity remains inside selection,
registry, workspace and guidance owners. One worker owns exclusivity/recovery and
fair queue processing; no second scheduler, durable actor or infrastructure tier
was needed. Architecture snapshots use one generator and remain evidence projections.

## Deviations, limitations and decisions

- EDR-0001 (Choose an initial discovery grouping method) remains **draft**. Human
  labels, exact registered method/thresholds and an owner adoption decision are
  outstanding. No decision-bearing comparison was run. The grouping method is an
  explicitly parameterised exploratory prototype.
- Operational bounds are explicit: 100 selected inputs, six synthesis examples,
  1,000 evidence links per rule version, twenty staged decisions, six guidance
  targets and bounded selected discussion/context. They are not empirical optima.
- Candidate publication and terminal job registration are separate. A complete
  candidate may survive an interrupted job; its trace remains inspectable. Recovery
  never automatically repeats the external call. Local model-file verification
  cannot attest the bytes already loaded by another process.
- MAF handled typed bounded workflows and advisory responses without durable
  entities. Provider failures and task-validation failures remain distinct. Existing
  SQLite adapter/httpx deprecation warnings are retained, not suppressed.
- Actor names are local attestations; no multi-user authentication claim. Windows
  is the tested context. Author self-review is not independent review.
- ADR-0010/0011 are implemented after verified owner merges. ADR-0012 (Apply review
  intent in explicit batches) is also implemented after explicit owner acceptance
  and verified PR #13 integration on 20 September 2026. ADR-0001 remains
  accepted pending its first applicable registered empirical decision.

## Remaining slices and pause boundary

[VS3 preparation](../plans/VS3-plan.md) revises replay inputs, execution and comparison
around immutable rule versions, explicit evidence labels and the existing review
contracts. VS4-VS8 are explicitly revised there; none is activated. Software
integration is verified. Resolve the human-review and EDR gates before claiming
full VS2 closure or freezing later work.
