# Source reading: author self-review

Scope: all three propositions in `semantic-commits.json`, followed by the aggregate
diff from the stated base. This is author self-review, not independent review or
GitHub approval. The canonical verification summary records checkpoint outcomes.

## Orientation and boundaries

P1 establishes the distinction between human context and model input, the accepted
ADR and a prospective study-preparation amendment. It makes no model-quality claim
and does not pretend to pre-register a comparison already performed. P2 implements
the complete evidence contract. P3 backfills existing guides and synthetic captures.
The proposition plan records the alternative split and its rejected incomplete
states. The final series preserves the actual diary, including failed attempts.

## Contract challenges and dispositions

| Challenge | Inspection and result |
| --- | --- |
| Can the reading view rewrite the research source or silently rerun a model? | Importer only consumes explicit retained files and a terminal job. No network or runtime/model call path. Original dataset/result hashes were compared in the runtime rehearsal. |
| Can corrupt, wrong or unsafe source be shown? | Adapter owns bounded receipt/response parsing, exact response hashing, source identities, canonical URLs and per-read integrity. Template escapes text. Tests cover wrong identities/hash, unsafe URL, corruption, missing files and escaping. Local receipts establish consistency, not external authenticity. |
| Can a stale form silently gain context? | The presented digest survives form conversion, row actions and validation errors. Application checks the current digest; SQLite checks again under the write transaction and by trigger. Race and stale-form tests retain edits and prevent an unattributed decision. |
| Does an attachment imply the human read it? | Guide, protocol and ADR explicitly say presented/available, not read. Old decisions cannot receive new attachments; their nullable context remains absent. |
| Can external text become an exact model evidence quote? | The existing grounding path still uses original dataset strings. A negative test submits a quote only in external context and observes refusal. |
| Does downstream freezing lose or dangle the context identity? | Existing selection snapshots embed the annotation and retain its optional digest. Inspection found a verification gap, corrected in the diary with a missing-context test. Freezing now verifies the attachment before publication. |
| Do real preserved redirects work? | Initial rehearsal exposed three numeric GitHub redirects. General numeric-URL support checks the same comment ID while retaining the receipt and canonical PR/path checks. A fresh complete rehearsal attached all 54 inputs. |
| Is the tool reproducible outside the agent environment? | Inspection found the standalone importer depended on PYTHONPATH. Its own-checkout source binding and subprocess test now cover execution without that variable. |

## Design and aggregate review

The adapter hides receipt verification, immutable publication, catalogue binding
and event creation. The application consumes a small read contract, and domain
logic has no GitHub/storage types. Existing atomic file publication is reused.
The typed architecture delta contains two new modules and no changed architecture
contracts, boundary rules, ignores or dependencies. SQLite holds only references;
receipt bodies remain in files. Annotation and attachment transactions are short.
The same optional field is consumed consistently by record loading, form parsing,
event persistence and selection snapshots. No historical annotation is rewritten.

Code docstrings explain guarantees, failures and the non-obvious redirect and
race constraints. Existing prose-heavy guides are updated with view/step tables;
the new screenshot uses synthetic data and retains crop/fixture provenance.
No model claim or new comparison is inferred from this usability change.

## Limits and open research matters

- Windows/Python 3.12 verification; no independent reviewer or hosted CI claimed.
- No guarantee of GitHub receipt authenticity beyond retained local consistency.
- Attachment replacement and reopening immutable human assessments are outside
  this change. Missing attached evidence blocks assessment/freezing until restored.
- Existing cross-tab first-assessment discrepancy remains a separate local research
  reconciliation task; no intended human judgement has been fabricated or replaced.
- The screenshot was inspected directly and synthetic browser behaviour verified.
  A local-file rendered-guide preview was blocked by browser URL policy; no workaround
  was attempted. Generated Markdown HTML and link/hash checks are retained, without
  claiming that blocked visual preview passed.

No unresolved implementation finding remains within this batch after the recorded
diary fixes. Model-formatting efficacy remains an untested hypothesis requiring a
future pre-registration if pursued.
