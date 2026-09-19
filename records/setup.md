# Annotation batch setup

Materiality: material. Assessed before implementation, 20 September 2026.
Hard triggers: persistent human decisions, result identity/provenance and web mutation.
Base: b9ffa2ee49b60758dba6832f08b988f797b439af, owner-approved PR6 merge.
Pair vs1-annotation/r1. Canonical evidence outside all application worktrees.
One integrator, Codex desktop GPT-6. Owner explicitly authorises autonomous VS1
completion, a second stacked PR, and a committed VS2 plan without a plan PR.
No authority to merge either implementation PR; owner merges on GitHub.

Scope: immediate Accept/Edit/Reject, atomic immutable annotation/event records,
source/result/edit provenance, result history and honest progress. No staging,
reopen, supersede or discussions. Same completed-result repeat is idempotent;
conflicting repeat fails instead of overwriting a human decision. A fresh model
result is independently reviewable. Model/source text remains untrusted data.

Design clarity: AnnotationService validates decisions and edits against immutable
source/result identities, hiding schema/grounding from HTTP. AnnotationStore owns
short atomic metadata/event writes, idempotence and result-level uniqueness.
Edited bodies use the existing immutable filesystem store; SQLite keeps refs only.
The UI needs decision state and progress, not SQL, framework or provider types.
Simple result-level terminal decisions fit VS1 better than a general review state machine.

Provisional propositions: durable validated decisions with recovery/provenance and
CLI tests; browser Accept/Edit/Reject and progress with submission safety. ADR0006
status confirmation is independent bookkeeping after verified owner acceptance.
Canonical gates and meaningful tests run at every semantic checkpoint in its own
Windows/Python3.12 locked environment. Live browser paths checked separately.
A full slice audit and remaining operational gaps belong to the following stacked batch.
