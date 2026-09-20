This adds a reproducible command-line comparison of the fixed lexical baseline and embedding-based grouping method. It binds both methods to the same saved inputs, prepares a rating pack with method names hidden, and reports the agreed criteria from completed human ratings.

It also records the completed input-preparation pass: **33 valid drafts from 55 qualified sources**, below the agreed target of 40. All 22 failed outputs and 25 unresolved source checks are retained. EDR-0001 remains unregistered; no human labels, research grouping runs or adoption decision are claimed.

## Review sequence

| Commit | What it establishes |
| --- | --- |
| `69548cb` | Shared input text and the deterministic lexical baseline. |
| `ec5f15f` | Equal assessment budgets, masked groups and exact decision criteria. |
| `dadc3bb` | Exact stored-input/run binding, replay checks and failed-attempt accounting. |
| `4b5fc59` | Registration checks, immutable rating/report files and the operator guide. |
| `2adeb88` | Current-document backfills and the measured input-preparation shortfall. |

## Validation

**Standard checks: passed** at `2adeb88`. [Evidence](https://github.com/FinnNk/Meerkritic/tree/5d3612cee3163e1652683ed35233e3cf555d1ca5/records/r2/verification-summary.json)

215 tests passed; 0 skipped. All five semantic checkpoints passed separately with locked dependencies on Windows/Python 3.12.

| Behaviour | Tests added |
| --- | ---: |
| Lexical grouping and shared text | 5 |
| Masking, completeness and criterion boundaries | 13 |
| Stored evidence, failures and retry timing | 11 |
| Registration and command-line publication | 5 |

Two earlier full runs hit an intermittent Windows temporary-Git cleanup lock. Isolated checks and the diagnostic full suite passed unchanged; the lock cause remains uncertain. [All attempts are retained](https://github.com/FinnNk/Meerkritic/tree/5d3612cee3163e1652683ed35233e3cf555d1ca5/records/r2/verification-summary.json). Compared with base `f5b23e4`, no existing tests were removed or altered. [Documentation checks](https://github.com/FinnNk/Meerkritic/tree/5d3612cee3163e1652683ed35233e3cf555d1ca5/records/r2/docs-check.json): 326 local links, 77 tables, 59 imported-source hashes and actual command help. [Architecture delta](https://github.com/FinnNk/Meerkritic/tree/5d3612cee3163e1652683ed35233e3cf555d1ca5/records/r2/architecture-delta.json): two modules added and shared grouping logic updated; contracts unchanged.

[DER review packet](https://github.com/FinnNk/Meerkritic/tree/5d3612cee3163e1652683ed35233e3cf555d1ca5): exact diary/semantic tree equivalence and full author self-review. The earlier final documentation commit was superseded before verification/publication; both rounds are retained. This is local verification, not a hosted CI or independent approval claim.

## Decision needed before the study

The fixed candidate pool and single model pass cannot yield 40 usable inputs. Human repair of failed drafts is proposed, preserving the original failures and avoiding another model pass; it needs owner agreement and a separate workflow change. The current harness cannot edit failed jobs. No preparation rule or validation check has been relaxed.

After that decision: finish human input review, freeze and register the study, collect masked group ratings, record the outcome/owner decision, then complete the milestone review. This PR delivers the comparison tooling; it does not close VS2.
