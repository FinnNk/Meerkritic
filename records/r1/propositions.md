# Assessment clarity — semantic review plan

Base: 86a839341787e986dae6870673efeaf8251a41d0, exact PR 17 head.
Frozen candidate diary: b72beb10e80889c00e5ed69f82f7a5da5204d33f.
Full diary verification must pass before reconstruction. This plan proposes no
content changes to that snapshot.

| Unit | Complete proposition | Diary source | Evidence required |
| --- | --- | --- | --- |
| P1 | Define assessment meanings, agent/reviewer obligations and prospective study clarification before collection. Runtime support remains a subsequent checkpoint. | 46fec93 | Canonical checks; readable contract and accepted ADR; EDR remains draft |
| P2 | Apply the compatible impact/unknown contract consistently to future prompts and the review UI, retaining originals, notes and grounding. Includes the prompt provenance expectation correction and new field guide. | 5efdc2e + 59c058f | Canonical checks; old/new scope, failed grounding, saved notes/restart; synthetic browser inspection |
| P3 | Backfill current guides, navigation, glossary and synthetic screenshots; record candidate implementation confirmation. | b72beb1 | Canonical checks; documentation links/source hashes; image dimensions/digests; architecture delta |

P1 can retain its exact diary commit as semantic ancestry because it is already a
complete proposition. P2 combines the later test-expectation correction with the
contract it verifies; the failure remains in the diary and retained logs. P3 stays
last to honour the owner's requested separation of guidance and existing-doc backfills.

Alternative: one contract/code/docs commit. Rejected because it hides the durable
field-definition decision and existing-document backfill within implementation.
Alternative: separate schema, prompt, tests, styles and UI commits. Rejected because
schema/prompt/human meanings must agree at the first runtime checkpoint, with
grounding/provenance tests available there. The source-panel styling is a small
part of making that same review contract visible, not a new subsystem.

Boundary challenge: an unknown scope must not imply a repository-wide issue or
silently populate a rule's scope. Existing grouping text uses issue/invariant/
categories, not annotation notes or scope. The independent rule schema retains its
existing explicit scope contract; no rule is generated or adopted by this change.
No new service, persistence model, migration, dependencies or architecture ignore.

Only the exact semantic series may be proposed for merge. Diary repair ancestry
and archival evidence branches remain outside the submission ancestry.
