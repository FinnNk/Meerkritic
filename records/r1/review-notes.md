# Assessment form: author self-review

Scope: the complete base-to-tip candidate, P1 and P2 in order and their aggregate.
Identities are pinned by semantic-commits.json when reconstructed. Author session
Codex /root; no independent-review or GitHub-approval claim.

## P1 contract challenges

- Compared the form adapter/route with unchanged AnnotationService.decide,
  review_actions, IssueInterpretation, ground and the existing failed-draft tests.
  Decisions still pass eligibility, schema and grounding before publication.
  GET and row operations do not call the writer. A stale conflicting submission
  returns the saved decision plus the attempted values without overwriting it.
- The form's interpretation is complete; enums are derived from the existing
  schema. Blank rows are omitted and an empty candidate rule is null; neither
  supplies a judgement. Unrepresentable failed output remains inspectable.
- Old edited_json submissions retain their API path. Mixed encodings, duplicate
  scalar inputs, unmatched evidence rows, excess lists, unknown fields and
  cross-origin/oversized bodies are rejected. Service and parser limits remain.
- HTML line-ending normalisation resolves a unique literal source substring,
  then the existing service repeats exact grounding. Overlapping occurrences
  fail; matching text never establishes review correctness. A review follow-up
  added lone-CR coverage at 97af70e (targeted test passed); the earlier verified
  diary is retained and final qualification runs against the new identity.
- Browser tests use only synthetic data: list operations preserve edits/notes;
  invalid evidence is recoverable; saved output is readable. At 600px the controls
  fit without horizontal page overflow. The default 1280px layout was inspected.

## Design clarity

1. Complexity removed: researchers no longer encode JSON arrays, nulls or quotes.
   The web adapter owns browser representation and conversion, not another store.
2. Module depth: from_output, change_rows and interpretation_json hide the actual
   encoding/invalid-draft/line-ending obligations behind a bounded form interface.
3. Leakage: application/domain code is unchanged and knows nothing about HTML.
   Typed enums remain source-owned; request bounds supplement domain validation.
4. Layers: web conversion differs from source grounding/persistence. The original
   service remains authoritative; no pass-through framework is introduced.
5. Special cases: the legacy input path is deliberate compatibility for already
   open tabs and existing callers. Revisit removal only under an explicit API
   compatibility decision; no user must switch raw and field editors manually.
6. Simplification: server-rendered row operations work without JavaScript. The
   cost is a page response for each row operation; no usability superiority is
   claimed. Adding a SPA, client state store or generic form system is unjustified.

## P2 and aggregate

- Current guides use exact button labels, plain-language field names and ordered
  steps. The field guide owns meanings; the new guide owns editing/encoding details.
  Existing documentation backfill is separate from the implementation guarantee.
- Screenshots are actual synthetic UI, with two views for the long form and a
  failed-draft view. They were cropped and inspected at native size; capture
  metadata identifies earlier/later wording. No public research data is included.
- ADR-0014's decision/status is unchanged. No schema, prompt, migration, domain
  boundary, dependency lock, sample or study criteria changed. No EDR needed for
  a prescribed presentation correction or its incidental verification.
- Known product limits remain explicit: edits are tab-local and not durable
  drafts; accepted source annotations cannot reopen. The real cross-tab save
  discrepancy is recorded outside Git and is not silently corrected by this PR.

Final readiness is conditional on exact checkpoint qualification, equivalence,
documentation/capture checks and publication evidence; those records carry the
results rather than this narrative asserting a check that has not yet run.
