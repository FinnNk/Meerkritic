# Comparison tooling: materiality and design before implementation

2026-09-20. Pair vs2-comparison/r1; base f5b23e44e4f13237a9f505f2f8182e0561813efe.
PR15 four ordered trees match; integrated canonical checks pass, 181 tests.
Material: hard trigger changes experimental method/rating evidence contracts;
multiple independently reviewable propositions and non-trivial failure handling.
One integrator /root. Diary change/vs2-comparison-diary; eventual semantic branch
feat/vs2-comparison. Evidence external. No existing app worktree or main changes.

Scope: fixed lexical comparator, deterministic method-masked rating pack and
criterion-based report, using the agreed EDR protocol. Synthetic execution only
until qualified human inputs and actual registration exist. Source qualification
and preparing interpretations may proceed, but no human decisions are supplied.

Design clarity:
- Domain study module hides grouping/representative rules, masking/deduplication,
  complete ratings, denominators and criteria; no provider, I/O or Git types.
- Application comparison owner resolves exact selection, embedding and cluster
  evidence, validates the shared input text/identities, then invokes these rules.
- CLI owns registration-reference checks and immutable external file publication,
  reusing existing content-addressed JSON storage rather than adding DB/UI state.
- Callers rely on deterministic bounded results, explicit failures/insufficiency
  and immutable references. They supply exact runs, inputs and human ratings.
- Callers need not reconstruct mappings, denominator rules or source artefacts.
- A one-off analyst script would duplicate provenance/denominator obligations.
  A generic experiment framework is unnecessary: one fixed EDR protocol, small APIs.
- Shared interpretation text gets one owner used by current discovery and study,
  avoiding drift between candidate vectors and baseline text.

Research safeguards are operational: actual registration is required before
comparison, exact plan/input references retained, no automated human judgements.
The tool verifies record consistency; it cannot authenticate raters or establish
that operators have disclosed every external experiment. State these limits.
Fail incomplete ratings, invalid memberships or differing inputs explicitly.
Count uncertain ratings in the denominator; k<8 is insufficient, no silent adoption.
Use exact integer/fraction comparisons for thresholds, not rounded percentages.

Planned propositions (reassess after real chronology):
1. Fixed lexical grouping on the same interpretation text (code/tests/contract).
2. Masked assessment and complete criterion report (code/tests/method explanation).
3. Bind existing immutable selection/run evidence and expose reproducible CLI.
4. Current study/integration documentation backfill and source-preparation handoff.
Several related commits, one PR; stack additional batches only if warranted.
Every semantic checkpoint has its own locked Windows source/quality execution.
No test retirement, new dependency or architecture ignore planned. Author review
will be labelled self-review; owner approval/merge remain separate.
