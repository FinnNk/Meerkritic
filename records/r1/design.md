# Human correction of failed drafts: design before implementation

2026-09-20. Base e7726500930e79f0ba69becae5d12b77edbb5dea (PR16 merged, all five ordered trees match). Classification: material. Hard triggers: human-decision/state eligibility, persistent evidence interpretation and coordinated annotation/selection contracts. DER alpha.2 method revision 7; one integrator /root. Owner explicitly authorised prospective input-preparation amendment and harness implementation. No model rerun or human judgement is authorised for the agent.

## Contract and complexity

Reuse annotation decisions and immutable human_edit publication. One application-level eligibility function owns available actions for both submission and selection verification; web renders those actions. Successful jobs keep Accept/Edit/Reject. Failed semantic normalisations with retained non-blank model text allow Edit/Reject only. Provider, interrupted, missing/corrupt and unpublished failures cannot be repaired as model drafts. An edit must still satisfy the unchanged schema and exact unique source grounding. The job status/error/result hash never changes. An original failed result can therefore coexist with a separately accepted human interpretation, without misreporting model success.

Callers rely on explicit admissible actions, atomic immutable annotation/event insertion, idempotence and conflict detection. They must not inspect a raw model response to decide eligibility or reproduce provenance rules. UI displays the original source and failed raw JSON as untrusted text; no automatic suggested correction or model call. Invalid submissions retain the draft. Existing terminal decisions remain terminal.

Selections accept verified corrected failures; rejected failed outputs have no valid interpretation and must remain explicit exclusions, not invented valid objects. New selection snapshots use a versioned nullable-interpretation contract for rejected records; old snapshots stay readable. Validate non-null interpretation for every eligible record at all snapshot entry paths. Discovery continues to read only eligible rows.

Progress counts distinguish reviewed successful results and reviewed failed outputs; a correction must not raise a success numerator above its denominator or erase failure counts. The queue may link published failures for inspection; infrastructure failures show no annotation controls. Avoid persisting a duplicate eligibility index merely to filter a small local queue.

Alternative: relabel a failed job as successful or replace its artefact. Rejected because it destroys the original execution evidence. Alternative: a separate repair workflow/database. Unnecessary; existing annotation + publication + source validation already owns the required durable state.

## Planned review units

P1: record the owner's prospective preparation amendment and durable provenance decision; keep EDR draft.
P2: complete annotation/selection/progress contracts, backwards-compatible snapshot reading and failure/restart tests.
P3: expose source-backed correction in the harness, preserve invalid drafts and explain its operation with a synthetic screenshot and browser tests.
P4: backfill current guides, status/indexes, integration evidence and the human-review handoff. Last commits backfill documentation.

One PR, four complete semantic propositions; no unmerged predecessor remains. Reassess boundaries after actual chronology. Baseline, frozen diary and every semantic checkpoint use their own locked Windows/Python 3.12 environment. Prior batch had intermittent Windows Git-fixture cleanup errors; retain failures if they recur, no ignored cleanup or weakened assertions.

## Human handoff and empirical constraints

Keep the 80-candidate order, 55 qualified origins, 33 valid drafts and 22 original failures. Human may repair a failed draft or reject it, without another model pass. Record the outcome as Edit/Reject with exact annotation/job IDs and the retained failure; input target stays 40, max five per repository. No comparison registration or group rating yet. Preserve the one existing preparation-ledger unresolved-source record. Provide an ordered local handoff; do not substitute the completion-ordered general queue for the fixed study order. Confirm live runtime is the dedicated study database and contains zero agent-generated annotations before handoff. Forty usable results are possible, not guaranteed.
