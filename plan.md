# Annotation correction — DER round 1

Base: 4ab131a08b6bae469b94ae8254c242a6ff1cad68. Diary branch:
`diary/annotation-corrections`; intended semantic branch: `fix/annotation-corrections`.
Integrator: current Codex session. Skill alpha.2, method 7.

Material: persistent schema, evidence identity/retention and transaction semantics
change. Owner explicitly requested reconciliation of two approved judgements.
No new model work, new judgements, destructive data repair or source replacement.

Design (software-design-clarity): AnnotationService validates and grounds a complete
replacement; the annotation store owns atomic predecessor fencing, replay and events.
Callers provide an exact predecessor ID, approved interpretation/notes, curator and
reason. They need not know table layout, current-version resolution or transaction
ordering. This is preferable to direct database repair or study-only override files,
which would bypass normal selection validation and hide corrections from the harness.
Keep original rows untouched in their existing table; append correction versions and
provide shared read views. One current decision per job, all versions addressable.

Provisional semantic proposition: one complete append-only correction contract,
including storage, service, CLI, tests, ADR and guide. Splitting by layer would leave
unusable intermediate interfaces and repeat the same provenance obligations.

Verification: baseline canonical check; meaningful correction, replay, race, rollback,
grounding, migration, selection and stale-form tests; full canonical check on clean
diary and clean semantic checkpoint; typed architecture before/after/delta; exact Git
tree equivalence and aggregate self-review. Hosted checks remain distinct.

Operational rollout: SQLite online backup, rehearsal on a runtime copy, all table and
artefact preservation checks, then the same exact two approved corrections live.
Retain old and new identities, command/evidence hashes and append-only research log.
Record the administrative transcription as agent-executed with owner authorisation,
not an independent judgement or an owner-clicked submission.
