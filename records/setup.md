# VS2 Batch C setup and materiality

Authorised autonomous continuation; one history integrator, no delegated agents.
Diary base dc6ba77119b2cf148cf014c54a7748953bd9735d, PR12 (Batch B). Final B checks
150, each semantic checkpoint passed and exact tracked-tree equality proved.
C will be a stacked PR targeting feat/vs2-rules while B is unmerged.

Material: persistent interaction states, atomic multi-target decisions, replay and
unknown external completion, new guidance runtime and architecture projection
identity. DER required. Evidence lives here outside application worktrees; pinned
DER alpha2 and software-design-clarity apply. Canonical gates unchanged.

Design before implementation:
- Interaction owner hides saved immutable draft payloads, CAS, atomic application,
  per-version review lifecycle, discussion and submitted guidance identity. Callers
  provide named intent and expected revisions; they need not know transaction order.
- Reuse the registry's canonical decision transaction operation inside the batch
  transaction, rather than duplicate promote/reject invariants or orchestrate many
  independent commits. A narrow adapter-local transaction operation is justified
  by the shared atomicity obligation, not speculative extensibility.
- Draft save is not decision application. Apply checks all targets and commits all
  decisions/events or none. Retries return the original receipt; conflicts retain
  the saved draft. Definition revision supersedes the old review task explicitly.
- Discussion is append-only, tied to exact versions. Guidance freezes selected
  discussion IDs, definitions and revisions before queueing. Submission, response
  and applied decision remain distinct. Ordinary MAF returns advice, never edits
  or applies human decisions. No automatic replay after uncertain completion.
- Architecture view loads typed before/after/delta artefacts, checks hashes and
  current source fingerprint; diagrams/views are projections and stale is visible.

Bounded prototypes: at most 20 decisions per draft and six targets per guidance
submission, bounded text and finite output. No distributed scheduler, actor runtime,
new auth model or data-driven quality claim. EDR0001 stays draft. Finish with an
all-guidance candidate milestone review, record findings/remedies/earlier detection,
revise remaining slices and retain owner/empirical completion gates separately.
