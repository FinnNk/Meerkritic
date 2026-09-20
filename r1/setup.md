# VS2 inputs, r1 — assessed before implementation, 2026-09-20
Material: persistent schema, durable evidence identity, caller and transaction contracts.
DER alpha.2 method7; one integrator; evidence outside application worktrees.
Diary change/vs2-inputs-diary; semantic feat/vs2-input-selections. Both bases:
fa6856bff52efecba55700572cb10e67f9a8f3c0, tree ed0820f6d806eab6cbe19b8582e2bb2fd39daca7.
PR9 main tree equals reviewed f353cfed1299608234f21e7159c6b0331e5b0660 exactly.
Canonical baseline: all gates, 102 tests; integrated-baseline-checks.log.
No DER profile present. Required Windows/Python3.12 locked own-source checks at each checkpoint.
Owner authorised VS2, topic branch/PR; owner alone merges. Routine bounded repairs authorised.

Design: SelectionService owns exact version/eligibility, verified source/result/edit resolution,
and exclusions. Callers submit bounded explicit IDs; no job service graph traversal or source
pagination knowledge. SelectionStore owns immutable file publication and atomic metadata/event,
idempotent retries and digest-verified reads. File bodies outside SQLite. Failed DB registration
may leave a complete unreferenced file. This is simpler than a generic artefact framework or
misusing job-bound ResultStore. Typed requests reject contradictory states.
VS1 lacks actor provenance: research needs explicit curator human-review attestation, a recorded
claim not authentication. Fixtures remain labelled, uncertain fields retained, Reject never a
verified negative. Freeze explicit holdout list; empirical registration still owns sampling.
Planned propositions: reconciled plan; frozen selections/CLI/durability; browsable snapshots.
Separate A1 prerequisite from A2/A3 because model and human-corpus gates remain pending.
No empirical comparison, new dependency or architecture ignore planned. Reassess scope growth.
