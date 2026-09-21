Flattened dataset diffs make unrelated lines appear connected during assessment. This change shows **Preserved GitHub source**, with its retained line breaks, above **Dataset text supplied to the model**. Difference labels distinguish whitespace changes from other changes; the original model input and outputs remain untouched.

New decisions record which additional source was presented. Old tabs cannot silently save against newly attached context, and missing or damaged attachments block review. Exact evidence quotes still come from the dataset text. [ADR-0015](https://github.com/FinnNk/Meerkritic/blob/4e63077c389af19806317edf4b9124063927b2cd/docs/adr/ADR-0015-separate-review-context-from-model-input.md) records the decision and limits.

The shared header also groups links under **Research**, **Review** and **Project**, with separate links for the current assessment. Groups share a compact desktop row and wrap on smaller screens.

**Stacked on #21. Merge order: #17, #18, #20, #21, then this PR.**

![Synthetic source panel showing preserved line breaks and the separate dataset view.](https://raw.githubusercontent.com/FinnNk/Meerkritic/4e63077c389af19806317edf4b9124063927b2cd/docs/images/preserved-source.png)

[Synthetic capture notes](https://github.com/FinnNk/Meerkritic/blob/4e63077c389af19806317edf4b9124063927b2cd/docs/images/README.md). No research judgement is shown.

## Review sequence

| Commit | What it establishes |
| --- | --- |
| `d14fbf4` | Assessment policy, accepted ADR and prospective study-preparation amendment. |
| `f3e39e3` | Complete import, two-view assessment, immutable source identity, stale-form protection and selection provenance, with tests and operating instructions. |
| `4e63077` | Backfill current guides, backup instructions and the synthetic screenshot. |
| `9d2fe65` | Group shared navigation, retain conditional destinations and separate assessment links. |
| `13b635a` | Explain navigation in the task-guide index with a synthetic header capture. |

![Grouped navigation with assessment-specific links below.](https://raw.githubusercontent.com/FinnNk/Meerkritic/13b635a221fa9178f922e2ef1b946c0d45081077/docs/images/harness-navigation.png)

[Navigation browser checks](https://github.com/FinnNk/Meerkritic/tree/013134fdab0851ebf5f38699fbe045353488db44/records/r2/browser-check.json): 1280px and 375px layouts, link visibility and keyboard focus.

## Validation

**Standard checks: passed** at `13b635a` - [evidence](https://github.com/FinnNk/Meerkritic/tree/013134fdab0851ebf5f38699fbe045353488db44/records/r2/verification-summary.json). **253 tests; 0 skipped.** Each checkpoint passed in its own locked Windows/Python 3.12 environment; the first three commits retain their unchanged exact-SHA results. The navigation refinement changes no tests.

| Test changes from #21 | Added | Altered | Removed |
| --- | ---: | ---: | ---: |
| Source identity, retention, redirects, standalone import, escaping, stale forms, races, exact quotes and selection integrity | 12 | 0 | 0 |
| Existing thread-boundary spy forwards the new keyword argument; its assertion is unchanged | 0 | 1 | 0 |

- [Live migration/import](https://github.com/FinnNk/Meerkritic/tree/d16c2882815b9f11c298eec98c7cb34cb63baac7/records/r1/live-runtime.json): 54 attachments; the existing annotation, 58 dataset/result files and 332 earlier events preserved. No new research decisions or model calls.
- [Browser verification](https://github.com/FinnNk/Meerkritic/tree/d16c2882815b9f11c298eec98c7cb34cb63baac7/records/r1/browser-check.json): synthetic save retains context and notes; [live read-only check](https://github.com/FinnNk/Meerkritic/tree/d16c2882815b9f11c298eec98c7cb34cb63baac7/records/r1/live-browser-check.json) confirms the new source views and matching form identity.
- [Documentation](https://github.com/FinnNk/Meerkritic/tree/013134fdab0851ebf5f38699fbe045353488db44/records/r2/docs-check.json): 389 local links and 59 imported source hashes checked. Screenshot inspected directly; local-file rendered-guide preview was blocked and is not claimed as verified.
- [Architecture](https://github.com/FinnNk/Meerkritic/tree/d16c2882815b9f11c298eec98c7cb34cb63baac7/records/r1/architecture-delta.json): two modules isolate source-reading contracts and storage; no architecture contracts, ignores or dependencies changed.
- [Double-Entry Review evidence](https://github.com/FinnNk/Meerkritic/tree/013134fdab0851ebf5f38699fbe045353488db44): exact diary/semantic tracked-tree equivalence, checkpoint checks and author self-review. Failed diagnostics and corrections are retained.

## Limits

The recorded source was presented, not necessarily read. Retained receipts establish local consistency, not independent GitHub authentication. Existing annotations are not backfilled. This change makes no claim that formatting improves model quality; that would require a separately pre-registered comparison. An earlier cross-tab assessment discrepancy remains a separate research reconciliation task.
