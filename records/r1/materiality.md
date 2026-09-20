# Assessment clarity — material change

Date: 2026-09-20. Integrator: Codex /root; author self-review.
Base: 86a839341787e986dae6870673efeaf8251a41d0 (PR 17, open when inspected).
Diary: change/assessment-clarity-diary; semantic: feat/assessment-clarity.
Pair: assessment-clarity; round r1; DER 0.3.0-alpha.2, method 7.
Evidence store: extras/der-evidence, outside application worktrees.

Hard triggers: interpretation contract and meaning of research evidence.
User authorised clarification and harness/guidance changes before resuming the
first unsaved human judgement. Existing autonomous batch/stacked PR authority
applies; the owner alone merges. No model reruns or human labels are authorised.

Bounded scope: define impact scope (including unknown), distinguish applicability
limits from missing evidence, explain faithful source interpretation versus human
extensions, improve the source panel/task introduction, preserve the walkthrough.
Use existing annotation notes for evidence limitations and investigation needs;
do not introduce another schema or store for a purpose notes already supports.

Design clarity: the existing interpretation schema owns admissible scope values
and descriptions; SourceContext owns versioned model instructions; templates show
the same meaning to humans. Callers need no new service or persistence API. This
is simpler than adding parallel field-definition services or another annotation
model. Notes do not become input to grouping: limitations relevant to the concern
must also constrain the issue/invariant, without inventing source facts.

Initial semantic propositions: (1) guidance and durable decision; (2) compatible
scope contract, prompt and review UI with tests; (3) backfill affected guides,
screenshots and candidate implementation confirmation. Revisit boundaries after
the verified diary freeze. Full canonical checks at every semantic checkpoint,
isolated Windows/Python 3.12 environments; architecture before/after/delta,
synthetic browser checks and retained-study integrity checks. Baseline evidence
available at ../vs2-draft-repair/r1/p4-checks.json; new baseline verification follows.
