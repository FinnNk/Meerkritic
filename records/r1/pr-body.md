Correcting an interpretation currently requires editing raw JSON, and the **Edit** button does not explain that it saves immediately. This change provides labelled text fields, judgement dropdowns and add/remove controls for categories, quotes and applicability limits.

**Save edited assessment** saves the corrected fields and notes. **Accept original** explicitly keeps the model interpretation. List controls only update the unsaved form; validation errors retain its contents. Saved interpretations are readable without opening JSON. Existing open JSON forms remain compatible.

**Stacked on #18. Merge order: #17 → #18 → this PR.**

![Synthetic assessment editor with labelled issue text and judgement dropdowns.](https://raw.githubusercontent.com/FinnNk/Meerkritic/437220ac6186cf8e4dd100a5f32a3bef8903db8c/docs/images/annotation-assessment.png)

[Synthetic capture notes](https://github.com/FinnNk/Meerkritic/blob/437220ac6186cf8e4dd100a5f32a3bef8903db8c/docs/images/README.md). No research judgement is shown.

## Review sequence

| Commit | What it establishes |
| --- | --- |
| `5942722` | Complete field editing, unsaved list operations, recoverable validation, compatible old submissions and readable saved results, with tests and editing instructions. |
| `437220a` | Backfill the current guides and synthetic screenshots. |

## Validation

**Standard checks: passed** at `437220a` — [evidence](https://github.com/FinnNk/Meerkritic/tree/9e7d68fe30952f382c647572e385b759e563bdcc/records/r1/verification-summary.json). Both semantic checkpoints and the frozen diary use their own locked Windows/Python 3.12 environments. **241 tests; 0 skipped.**

| Test changes from #18 | Added | Altered | Removed |
| --- | ---: | ---: | ---: |
| Field submission, row operations, validation recovery, failed drafts, input bounds, exact source line endings and stale-tab protection | 8 | 0 | 0 |
| Existing decision-button expectations | 0 | 1 | 0 |

- [Browser checks](https://github.com/FinnNk/Meerkritic/tree/9e7d68fe30952f382c647572e385b759e563bdcc/records/r1/browser-check.json): synthetic editing through save, retained invalid input, visible errors and a 600px layout.
- [Documentation](https://github.com/FinnNk/Meerkritic/tree/9e7d68fe30952f382c647572e385b759e563bdcc/records/r1/docs-check.json): 367 local links and 59 imported source hashes checked; three synthetic captures inspected, including in the rendered guide.
- [Architecture](https://github.com/FinnNk/Meerkritic/tree/9e7d68fe30952f382c647572e385b759e563bdcc/records/r1/architecture-delta.json): one web form adapter; no domain, persistence, dependency or architecture-contract changes.
- [DER evidence](https://github.com/FinnNk/Meerkritic/tree/9e7d68fe30952f382c647572e385b759e563bdcc): exact diary/semantic tracked-tree equivalence, checkpoint checks and author self-review. Earlier failures and their corrections are retained. No independent approval or hosted CI run is claimed.

## Limits

Edits remain tab-local until submitted; this is not a durable draft workspace. Saved source assessments cannot be reopened or overwritten. The UI now makes these limits explicit and retains attempted values on a stale-tab conflict. A real cross-tab save discrepancy was recorded separately for research reconciliation; this change does not rewrite that judgement, rerun models or alter study criteria.
