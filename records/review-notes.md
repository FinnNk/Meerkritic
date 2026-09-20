# Full author review: vs2-rules/r1

Self-review by the authoring Codex desktop/GPT-6 session, not independent review.
Semantic base e81c2e867e714f2fed72d235eb44ba035b4bf302; final semantic
dc6ba77119b2cf148cf014c54a7748953bd9735d; frozen diary
ebd6d9eff6d74340ba15266217b6d9ce063d4dbf. Manifest binds the same identities.

## Orientation and proposition review

Reviewed the frozen plan, application registry/discovery/synthesis ports, rule
models and migration, SQLite implementation, MAF adapter, unchanged source
selection/annotation contracts, web/CLI composition and related tests/docs.
The primary claim is traceable provisional candidates with durable human review,
not empirical validity. No hosted CI or independent review is claimed.

- P1 dd2a1ff5d5e2b620c2b37c22362623320d1bfeee: records activation and owner-merged
  prerequisite. No runtime change; checkpoint tests 132. ADR10 integration matches
  the owner's merge and exact ordered proposition-tree mapping.
- P2 45683c9359db803b4911467dddb6e9344af242d7: registry/body/source boundary,
  immutable history, weak inherited evidence, explicit promotion/rejection, UI and
  actor/rationale/CAS. Tests 142, including event rollback and concurrent winner.
  The standalone proposal port works with synthetic human-origin inputs; no
  absent MAF feature is needed to verify the registry contract. Prior version
  bodies remain exact bytes. Decisions/events are in one transaction.
- P3 dc6ba77119b2cf148cf014c54a7748953bd9735d: full synthesis application plus
  policy version2 retaining version1, real MAF graph, typed candidate/insufficiency,
  invalid-reference rejection with raw output, old-manifest compatibility and
  live telemetry. Tests 150. Source-reference validation sits in RuleProposal
  and is applied at runtime and application entry, not independently reinvented.

## Aggregate and design review

Complexity introduced: immutable version lineage, evidence attestations and a
separate synthesis outcome. The registry owns version fencing, event atomicity
and inheritance; callers do not implement SQL or discard history themselves.
The synthesis owner hides representative selection, six-example context, route,
usage and trace publication. Web handlers only parse bounded same-origin intent.

Module depth: RuleService exposes provenance/evidence operations; SQLiteRules
owns the complete transaction obligations. MAF is isolated behind SynthesisRuntime.
No new worker lifecycle, framework type in domain, model-name routing in domain,
dependency/lock change, architecture ignore or speculative actor abstraction.
Task prompt schema belongs to the application; deployment controls stay in LlamaClient.

Knowledge leakage: the trace is an explicit registry input contract rather than
an undocumented filesystem convention. Rule bodies/vectors/traces remain external;
SQL holds operational pointers and bounded claims. Models cannot invent references
outside supplied context. Source equality remains provenance rather than truth.

Layer quality: corpus jobs delegate the genuinely rule-specific operation rather
than growing provider branches. Existing storage and worker contracts are reused.
Expected insufficiency is a typed success; provider/semantic/context failures retain
distinct accounting. UI explains pending routing and preserves conflict values.

Tactical cases and resolved findings: reviewed evidence-bound inheritance and
found that adding new support could exceed the 1,000-link inspection bound; fixed
before freeze with an explicit all-or-nothing rejection and a preservation test.
New optional request fields initially threatened old manifests; validated semantic
comparison preserves existing hashes and tests a legacy manifest. The privacy
negative-control fixture now updates all immutable policy references so it reaches
the intended refusal; no assertion was weakened. A late Ruff line-length failure
was retained and corrected on diary before new freeze/checkpoint verification.

Highest-leverage simplification: one corpus queue and process lock cover embedding,
grouping and synthesis. Do not add separate scheduler/retry logic for rule creation.
No further material issue found in this bounded author review.

## Evidence and limits

Every checkpoint and frozen diary has its own clean checkout, installed source,
lock and canonical Windows/Python3.12 checks. Baseline integration checks also pass.
No tests deleted or skipped. Final tracked-tree equality is checked separately.
Live final run 1b250c59-74e6-4fa5-8267-1d087662eb83 used real pinned local embedding,
clustering and Qwen generation through MAF. Results and full request/trace retained.
Prior insufficient runs remain adverse/neutral evidence, not quietly replaced.

Known scope limits: at most six examples per synthesis and 1,000 evidence links per
version; one sequential worker; local operator must launch the pinned model bytes.
Candidate publication and terminal job write are separate, so interruption can
leave a candidate with a failed/unknown-completion job. A test proves inspection
and no automatic replay; docs direct inspection before another explicit call.
The framework still emits its existing SQLite/httpx deprecation warnings; checks
pass without suppressing them. No comparative quality, human labels, EDR adoption,
owner approval of this PR or non-Windows platform claim. Batch C interactions remain
planned rather than claimed as delivered here.
