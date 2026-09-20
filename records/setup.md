# VS2 grouping — material change setup

20 September 2026. Pair `vs2-grouping`, round `r1`; sole integrator: Codex.
Diary repository: `extras/der-checkouts/vs2-grouping`, branch
`change/vs2-grouping-diary`. Both bases: `c9ef38f48b10d7876fe26babee36f2f15f258bf3`.
PR #10 is merged; its reviewed head `520d50fd6f9c9349773230f248ed537409edaa77`
has exactly the same tracked tree. The integrated baseline passes the canonical
checks and 115 tests in Windows/Python 3.12. Evidence is external to all worktrees.

Classification: **material**. Hard triggers: durable queue/schema and provenance
contracts, a model API boundary, worker recovery and analytical publication.
Reassess on scope change. DER alpha.2/method 7 governs true chronology, frozen
reconstruction, checkpoint-local checks and exact tree equivalence. No merge authority.
The owner authorises autonomous VS2 work and stacked PRs at each batch boundary.

## Design before implementation

The discovery owner accepts a frozen selection for embeddings, or a successful
embedding run for clustering. It hides immutable input resolution, ordered identities,
route binding, framework execution, publication and terminal failure handling.
Callers enqueue or inspect; they cannot make HTTP inference or patch a prior run.
An independent typed discovery queue avoids pretending a corpus is a VS1 source row.
The existing exclusive worker services both queues, retaining one lock and one
recovery boundary. Separate worker commands would expose avoidable scheduling and
recovery choreography to operators.

The embedding port takes ordered bounded texts and a selected route; it returns
vectors and measurement/provenance or a classified failure. Only the local adapter
knows task prefixes, HTTP payloads and server tokenisation. MAF owns the workflow
graph behind that project contract. No provider types enter application logic.

The analytical store hides atomic immutable Parquet publication and verified reads.
Only small run identities, statuses and events enter SQLite. Hashes and ordered
annotation identities bind vectors to inputs; clustering cannot consume partial or
failed embeddings. A deterministic cosine-threshold connected-component prototype
has explicit threshold/minimum size, stable representatives and singleton outliers.
It uses the existing runtime rather than adding a scientific package solely for
a bounded 100-item correctness path. Chaining is an explicit limitation, and no
claim of quality superiority or empirical adoption follows from this choice.

Provisional semantic propositions (revisit after freezing the actual result):
1. Activate remaining batches and mandatory stacking guidance separately.
2. Embedding jobs: routing, local adapter, MAF, durable worker execution, provenance,
   CLI/UI inspection and negative controls form one complete contract.
3. Deterministic clustering: verified vectors, memberships/representatives/outliers,
   browser and replay/integrity tests form one complete dependent contract.

Checks: locked canonical quality command in each checkpoint's own clean checkout,
source and environment; synthetic local live model compatibility separately.
Failure cases include shape/non-finite output, unavailable/local-only route,
corrupt inputs, interrupted workers, invalid transitions and orphan publication.
EDR-0001 remains draft: no human labels, comparative study or adoption claim.
