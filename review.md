# Annotation correction review — round 1

Author self-review in the implementation session; not independent review or owner
acceptance. Base `4ab131a08b6bae469b94ae8254c242a6ff1cad68`; diary freeze
`eca4915fee0c62e344a8d999612ed2bc0e2f9aad`; semantic checkpoint
`9178de6ae6ff5aaaaf45497c0b79fd4efa217980`; shared tree
`fb99d1a83a65076236832825f841c54b0fcba2c3`.

## Orientation and proposition

One proposition: an explicitly approved correction adds a grounded same-result
version without erasing the original or altering frozen selections. Reviewed the
complete diff, migration, initial-write path, correction path, progress/history/
selection consumers, artefact indexing, CLI, six new tests, template and guides.
Keeping the schema/service/command/tests/docs together avoids an incomplete
intermediate correction contract. No tests were removed or altered; six added.

## Contract challenges

- An old browser submission cannot overwrite the replacement. Initial writes now
  compare with the current view; conflicting writes still fail.
- Current-version comparison and replacement/event insertion share BEGIN IMMEDIATE.
  A unique predecessor plus trigger prevents competing descendants and cross-result
  or source-context substitutions. Original and replacement tables deny updates/deletes.
- Retry equality includes approved body hash, notes, context, reason and curator.
  A retry of an earlier correction returns that correction, not a rollback of later work.
- Both service paths share eligibility, exact-source grounding and context checks.
  Result artefacts retain original job/result/source identities. Conflicting requests
  may leave a complete unreferenced edit artefact, as initial edits already can.
- Progress uses current versions; history and exact-ID reads include every version.
  The original table remains sufficient for pending/source-attachment eligibility
  because every correction must descend from an existing original.
- Selection freeze continues exact-ID lookup. Old versions remain deliberate choices;
  existing frozen selections are byte-stable and do not automatically upgrade.
- Artefact indexing includes correction bodies. Original source and model records
  are never modified by the correction operation.

No unresolved defect found in this bounded self-review. The command supports Edit
corrections only and records curator claims without authentication. New source context,
multi-user permissions and correction UI are outside this batch. Runtime reconciliation
is assisted administrative transcription and is not independent human judgement.

## Design clarity and documentation

Unavoidable version/transaction complexity stays in the existing annotation store.
Callers supply one predecessor and complete approved content, without table knowledge.
No new layer or general versioning framework. Three public correction entry points
(service, protocol, adapter), no module/import/architecture-contract changes.
Reviewed the operator guide against CLI names and actual behaviour. No screenshot
needed for a command-line repair path. The current UI keeps normal judgement actions.
ADR confirmation is candidate-scoped; it does not claim PR approval or integration.

## Evidence and limitations

The first baseline full-suite attempt reported 253 passing tests but overlapped edits
to its working tree; it is retained as an observation, not clean-checkpoint evidence.
Repeated representative baseline annotation tests from an isolated base: seven passed.
First focused attempt lacked PYTHONPATH and failed to import; retained as an environment
failure, not a behavioural control. Subsequent properly bound focused runs passed.
Three Ruff line-length findings were repaired on the diary in their true chronology.

Full clean diary checks passed at a9c01f1 (259 tests) and final eca4915 (259 tests).
Final semantic-check.log belongs solely to 9178de6 and must pass separately before
publication. Canonical command is uv run --locked python tools/check.py on Windows
x64/Python 3.12.11. It sets PYTHONPATH to that checkpoint's src and invokes Ruff format,
Ruff lint, five Import Linter contracts, Tach and unittest. No ignores were added.
There is no repository CI workflow or active DER profile in this checkout; the local
canonical command is the declared required context. Hosted status is inspected separately.

Rehearsal and live correction preserved all earlier application rows and 366 runtime
files. Two new interpretation files and two correction events were added. Both corrected
records matched the retained approved drafts including notes and grounded spans; SQLite
integrity/foreign-key checks passed and both pages were inspected in the owner tab.
Research backups, approvals and individual judgements remain outside Git. The public
evidence archive contains only software-check evidence and a redacted outcome summary.
