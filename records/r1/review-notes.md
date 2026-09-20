# Assessment clarity — author review

Pair assessment-clarity/r1. Base 86a839341787e986dae6870673efeaf8251a41d0.
Diary b72beb10e80889c00e5ed69f82f7a5da5204d33f.
Semantic tip 796db0edc2032ed7ff0c518eecadd718b91c3e22.
This is author self-review, not an independent review or owner approval. Final
readiness depends on the exact checkpoint results in verification-summary.json.

## Orientation and checkpoint review

| Commit | Contract challenge and disposition |
| --- | --- |
| 46fec936e3305c4fab7e6fd47f9855d4fdf81d8d | Does guidance retrospectively reinterpret collected data? No: it pauses the first unsaved judgement, preserves the original pass and records assistance/prospective clarification. ADR accepted at this checkpoint; runtime support is explicitly subsequent. |
| 81d5ee307ca39857ae69d6f3052f2138bf92d8dd | Can unknown impact flow through MAF and human edits without weakening grounding, modifying originals or turning notes into applicability conditions? Domain enumeration gains only unknown; schema descriptions/prompt v3/UI align. Existing validation, publication, events and notes storage are reused. Tests cover real MAF with deterministic inference, rejected invalid scope, original preservation, notes and restart. The corrected prompt-provenance expectation is here with its contract, not deferred. |
| 796db0edc2032ed7ff0c518eecadd718b91c3e22 | Do current guides/screenshots describe the visible controls, and does implemented status overclaim approval? Navigation and glossary point to field meanings; failed screenshot caption explains its manually collapsed editor. ADR confirmation states candidate implementation and separate full qualification, not owner acceptance. Imported research remains unchanged. |

## Aggregate and compatibility

- Compared the base-to-tip production/test diff and affected guide/navigation
  changes with the field contract and the owner's walkthrough feedback.
- Inspected unchanged AnnotationService publication and SQLite decision behaviour:
  no write path changed. Existing successful/failed review eligibility remains.
- Compared JSON schemas after removing descriptions: the only validation difference
  is the new unknown scope value. Required fields and bounds remain identical.
- All 33 original successful study outputs parse and serialise identically under
  the new schema; hashes of all 55 original result files are unchanged.
- Inspected SelectionRequest/selection interpretation validation and grouping's
  interpretation_text: the shared domain schema accepts the new value, while
  grouping uses only issue, candidate invariant and categories. Notes and scope
  are not implicitly added to the frozen comparison representation. The rule
  schema is unchanged; this PR does not promote unknown scope into a rule.
- Synthetic UI checks cover source/help disclosure, all three successful actions,
  failed-draft Edit/Reject only, and 600/1000-pixel containment. Browser capture
  artefacts were rejected and replaced with visually inspected native crops.
- Live restart used the verified-equivalent semantic tree, with a database backup.
  Post-restart counts remain 55 jobs, 331 events, zero annotations/discovery runs.
  Original statuses and files remain unchanged; no worker or inference was started.
- Architecture before/after/delta shows only the three domain field declarations
  changing. No module, dependency edge, high-level contract, ignore or migration.

## Design clarity

- Complexity removed: fields no longer depend on contradictory oral explanations;
  uncertainty has an explicit supported value.
- Module depth: validation remains in the existing domain model, source instructions
  in SourceContext and evidence publication in AnnotationService. No new wrapper.
- Knowledge leakage: UI and prose deliberately explain the same research meanings;
  no MAF/provider type enters domain code. Future meanings must be reviewed across
  these representations; the new author checklist records that obligation.
- Layer quality: existing interfaces and transaction ownership are unchanged.
- Tactical cases: no special treatment of the first real input or its repository.
  All human assessments receive the same prospective guidance.
- Simplification: use existing notes for evidence limitations instead of adding
  another persistence schema without a structured consumer. Consequence: notes do
  not feed grouping; meaning-changing uncertainty must also qualify the issue/rule.

## Test disposition and limitations

Four new tests; one existing failure-provenance test changes only its expected
prompt version from v2 to v3. No test removed and no suppression/ignore added.
The initial complete run failed that stale expectation; its log is retained and
the correction is a real later diary commit. Targeted command import failures
are operational setup failures, not successful controls or application regressions.

No unresolved correctness finding was identified in this bounded author review.
It does not demonstrate improved human agreement, model quality or general rule
validity. No new model inference was run. The user's final first-input judgement
is still required; the saved feedback is preliminary and assistance is recorded.
Research registration and grouping comparison remain outside this PR.
