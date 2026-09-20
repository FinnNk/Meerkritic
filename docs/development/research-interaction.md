# Stage research decisions and send guidance

Open **Review workspace**, or use a rule's **Stage decisions, defer or reopen**
link. Choose actions and rationales for up to twenty rule versions, enter your
name and **Save draft only**. The saved draft survives restart; no decision has
been applied. Reopen it, inspect the target versions and **Apply this saved batch**.

All decisions and events apply together. A stale version or evidence revision
leaves every decision unchanged and keeps the draft. The page identifies the
conflicting version and shows the saved and current revision. Inspect that rule
before deliberately correcting the draft's target revision or action. An applied
draft is immutable; start a new draft for further intent. Identical Apply retries
return the original receipt rather than applying again.

## Review states

New versions are pending. Promote/reject answers a pending or reopened task.
Defer pauses a pending/reopened task; explicitly reopen a deferred or answered
task before another decision. Reopening preserves earlier answers and returns
the rule to candidate status. A definition revision supersedes the previous task
with a replacement link and creates a pending task for the new version. Evidence
added after a decision remains visibly newer than that decision.

Immediate promote/reject remains available for pending/reopened versions. Both
paths use the same registry contract. Promotion is a research judgement, never
validation or deployment. Names/rationales are recorded local claims, not identity
authentication. VS1 Accept/Edit/Reject annotations remain unchanged.

## Discussion and coherent guidance

Add discussion to a rule version. Messages are immutable and remain on that version
after it is superseded. Adding a message neither sends it to an agent nor applies
a decision. Open **Guidance**, choose rule versions and explicitly check the notes
to include, then submit one coherent instruction. The form shows up to six rules
and the latest twenty notes per rule; a rule's guidance link puts it first.

Submission freezes exact definitions, expected revisions and selected messages.
Later messages or revisions cannot silently enter the context. A duplicate send
with the same identity/content returns the existing batch; changed content requires
a new identity. Stale targets fail before queueing. Context exceeding 18,000 characters
is rejected before queueing rather than truncated; the model adapter also checks
the real token/template budget.

The existing worker handles guidance alongside source normalisation and discovery,
under one lock with round-robin scheduling. Use routing policy version 3 from
`config/routing/discovery-local.json`; earlier policy versions remain available
for historical resolution. A generation-only worker can answer guidance without
loading the embedding runtime. No HTTP request performs inference.

A **responded** batch contains advisory text, routing/usage, MAF observation and
raw provenance. It never applies a rule edit or human decision. Missing/invented
version references or invalid output fail visibly. A **failed** batch differs from
**unknown** completion after worker interruption. Recovery never resends; inspect
the retained context before making a new explicit submission. The page warns when
the target versions/revisions have changed since submission.

Live telemetry refreshes every five seconds. Unknown tokens remain unknown.
Responses and submitted context are external immutable artefacts; SQLite holds
queue metadata, small claims, receipts and append-only operational events.

## Compatibility and research limits

On 20 September 2026, real local Qwen/llama.cpp and MAF returned advice on a copy
of the synthetic Batch B candidate, with exact source/context provenance and no
rule-state change. External DER `vs2-interaction/r1` retains the method and result.
Automated fixture decisions are not human research labels. EDR-0001 remains draft;
these functional tests do not select a superior model, prompt or grouping method.
