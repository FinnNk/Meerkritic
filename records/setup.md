# VS2 rule synthesis and registry — material setup

20 September 2026. Pair `vs2-rules`, round `r1`. Sole integrator: Codex.
Diary clone `extras/der-checkouts/vs2-rules`, branch `change/vs2-rules-diary`.
Both bases: `125fd8c055b9c110efa1c4dd31dcc661358b32bc`, the exact published
head of PR #11, not main. Its clean checkpoint passes 132 tests and all canonical
checks; this clone has its own locked Python 3.12 environment. Evidence stays
outside application worktrees. DER alpha.2/method 7 applies.

Classification: **material**. Hard triggers: persistent rule/evidence/decision
schema, provenance identity, structured model workflow and durable research state.
Reassess on scope growth. The owner authorises autonomous remaining VS2 work and
stacked publication at batch boundaries, never automatic integration.

## Contract and design choices before implementation

The rule registry owns immutable versions, typed evidence links and explicit human
decisions against exact versions. Callers may inspect, attach evidence, promote or
reject; they cannot replace prior statements or silently drop counterexamples.
Filesystem bodies carry rule content/provenance; SQLite carries identities and
small operational metadata/events. A new version creates a link to its parent,
not an update to its content. Evidence from a previous version remains inspectable
and is carried forward explicitly when revising.

The synthesis owner resolves one pinned cluster from a successful run, supplies a
bounded list of exact annotation/source versions, routes a model-independent task,
and validates returned references before registry publication. MAF remains behind
an owned interface. Raw invalid output and routing/framework measurements survive
failure. Model proposals start with weak evidence; source existence and matching
quotes do not prove correctness or independent human verification.

Use the existing corpus worker queue rather than introduce another process,
scheduler or replay mechanism. A synthesis request pins the cluster run digest,
cluster identity and selection. Heavy model work never runs in HTTP. The worker
can publish one rule candidate with an immutable version per explicit request;
failed calls are inspectable and never retried automatically.

Promote/reject records actor, rationale, exact version and event. Promotion means
reviewed research candidate only, never validated/advisory/enforced status or a
production deployment. Counterexamples are explicit positive/counterexample/
false-positive/false-negative/unresolved links with weak/verified classification.
Reject or absence of an issue is not automatically a verified negative.

Provisional semantic propositions: (1) activate B and define accepted scope;
(2) immutable registry/evidence/version/decision contract with inspection and tests;
(3) routed MAF synthesis and queue/browser integration, invalid-output inspection
and live synthetic compatibility. Include code/tests/docs in each complete unit.
Revisit boundaries after the diary is verified and frozen.

No empirical method adoption occurs. EDR-0001 remains draft; a real model run on
synthetic selected inputs proves compatibility only. Dependency versions remain
locked unless concrete API evidence requires a change. Next dependent batch is C,
for staged atomic decisions, per-rule discussion and coherent guidance submission.
