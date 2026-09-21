---
status: implemented
date: 2026-09-21
decision-makers: [Finn Newick]
consulted: [Meerkritic agent]
informed: []
---

# ADR-0015: Separate preserved review context from model input

## Context and problem statement

The imported dataset can collapse code/diff whitespace. In the second assisted
assessment, adjacent upgrade notes were mistaken for one related change. The
preserved GitHub response retained their line boundaries; the imported record did
not. Model input uses the imported strings. This observation does not establish
how often formatting affects model quality.

## Decision drivers

- Make the supplied source readable without inventing formatting.
- Preserve the exact evidence available to each model run and human assessment.
- Keep existing decisions, dataset bytes and the frozen model pass unchanged.
- Avoid network retrieval inside a page request.

## Considered options

- Replace imported source text with the GitHub version.
- Infer line breaks from the flattened text.
- Present an explicitly imported, verified GitHub response alongside model input.

## Decision outcome

Choose separate views. Import a retained public response and retrieval receipt
explicitly for an existing job, checking their hash, comment/PR/path identities
against its observation. Retain the exact response and receipt with a content
digest outside SQLite; metadata binds the context permanently to the job. Do not
infer missing lines or fetch external links when viewing a page.

The UI names the dataset text as the model's input and the preserved response as
additional human reading context. Show retrieval identity and whether each text
is identical, differs only in whitespace, or has other differences. Render source
as escaped plain text. A successful identity check is not proof of completeness,
correctness, or an authenticated historical snapshot.

Save the presented context digest with each new annotation and its event. A stale
form must not silently gain new context. Presentation is not proof the reviewer
read it. Existing annotations have no recorded context; never backfill exposure.
Evidence quotes continue to match the original dataset strings. If extra context
changes a judgement, record the distinction in notes and avoid attributing facts
only present there to the model's input.

### Consequences

- Reviewers can read original line breaks without changing the study's model pass.
- Context files and annotation references must remain available for reproduction.
- Old tabs may require a refresh before saving, preserving unsaved edits first.
- Imported receipts are locally supplied evidence, not cryptographic attestation
  by GitHub. Missing or damaged attached context blocks review rather than silently
  changing what the form represents.
- Future model-input changes need their own versioned run/protocol. A claim that
  original formatting improves quality requires a pre-registered comparison.

## Confirmation

Implemented in the source-reading candidate, before owner merge. The source-context
tests cover identity/hash failures, exact receipt retention, HTML escaping, stale
forms, annotation/event provenance, retries, attachment races, command execution and
selection integrity. Browser verification saved a synthetic assessment with its
context digest. A migration/import rehearsal retained the existing annotation,
58 original dataset/result files and 332 events while attaching 54 unreviewed
sources. No research decision or model call was made. Canonical verification and
the exact reviewed identities are recorded in DER `source-reading/r1`.

Revisit this contract before replacing attachments, changing model inputs or
allowing evidence quotes from sources other than the original dataset strings.

## More information

This supplements [ADR-0002](ADR-0002-preserve-source-record-identity.md) and the
[assessment contract](../development/assessment-contract.md). The prospective
preparation amendment belongs to [EDR-0001](../edr/0001-discovery-grouping-method.md).
