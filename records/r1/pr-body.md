The first human walkthrough exposed ambiguous field meanings: investigation needs were being treated as impact scope, and missing evidence as applicability exceptions. The harness now explains those distinctions and accepts **unknown impact scope** when the supplied evidence does not establish the affected extent.

The source opens in a distinct panel, a task introduction explains what acceptance means, and field help separates **Applicability limits** from **Assessment notes and evidence limitations**. Existing notes retain investigation needs and human advice beyond the source. Original model outputs remain unchanged; future prompts are versioned as `normalisation-v3`.

**Stacked on #17. Review and merge #17 first, then this PR.**

![Synthetic assessment controls with field help and separate evidence notes.](https://raw.githubusercontent.com/FinnNk/Meerkritic/796db0edc2032ed7ff0c518eecadd718b91c3e22/docs/images/annotation-assessment.png)

[Synthetic capture notes](https://github.com/FinnNk/Meerkritic/blob/796db0edc2032ed7ff0c518eecadd718b91c3e22/docs/images/README.md). No research judgement is shown or submitted.

## Review sequence

| Commit | What it establishes |
| --- | --- |
| `46fec93` | Define field meanings, author/reviewer guidance and the prospective study clarification in ADR-0014. |
| `81d5ee3` | Apply the compatible schema, prompt and UI contract, with grounded-edit and provenance tests. |
| `796db0e` | Backfill guides, glossary, navigation and screenshots; record candidate implementation. |

## Validation

**Standard checks: passed** at `796db0e` — [retained evidence](https://github.com/FinnNk/Meerkritic/tree/ac4bd226a299199e061b970db7cad6618e90cd46/records/r1/verification-summary.json). Each semantic checkpoint and the frozen diary passed with locked dependencies on Windows/Python 3.12. Final total: **233 tests, 0 skipped**.

| Coverage change from #17 | Added | Altered | Removed |
| --- | ---: | ---: | ---: |
| Unknown/invalid impact scope through the MAF workflow | 2 | 0 | 0 |
| Field help, separate notes, immutable originals and saved edits after restart | 2 | 0 | 0 |
| Failure provenance expects the new prompt version | 0 | 1 | 0 |

The initial complete run caught the old prompt-version expectation. It was corrected on the diary before reconstruction; all other assertions remain. [Failure and disposition](https://github.com/FinnNk/Meerkritic/tree/ac4bd226a299199e061b970db7cad6618e90cd46/records/r1/discoveries.md).

- [Schema compatibility](https://github.com/FinnNk/Meerkritic/tree/ac4bd226a299199e061b970db7cad6618e90cd46/records/r1/schema-compatibility.json): only the unknown scope option changes validation; all 33 original successful drafts round-trip unchanged.
- [Live harness](https://github.com/FinnNk/Meerkritic/tree/ac4bd226a299199e061b970db7cad6618e90cd46/records/r1/live-after.json): 55 unchanged outputs; 55 jobs, 331 events, zero annotations and zero discovery runs after restart.
- [Documentation](https://github.com/FinnNk/Meerkritic/tree/ac4bd226a299199e061b970db7cad6618e90cd46/records/r1/docs-check.json): 359 local links and 59 preserved source files checked; affected synthetic screenshots refreshed.
- [Architecture delta](https://github.com/FinnNk/Meerkritic/tree/ac4bd226a299199e061b970db7cad6618e90cd46/records/r1/architecture-delta.json): no new modules, dependencies, boundary exceptions or database migration.
- [Double-Entry Review evidence](https://github.com/FinnNk/Meerkritic/tree/ac4bd226a299199e061b970db7cad6618e90cd46): exact diary/semantic tree equivalence and full author self-review. This is not independent approval or a hosted CI claim.

## Research handoff

The first judgement remains unsaved and its preliminary observations are retained locally. The EDR records the clarified method and assistance; it remains draft. No model rerun or grouping comparison was performed. Notes are retained with annotations but are not interpretation text for grouping, so meaning-changing uncertainty must also qualify the issue or candidate rule.
