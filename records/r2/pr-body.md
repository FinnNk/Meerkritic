Preparing study inputs by hand leaves room to change the sample accidentally or lose failed and rejected records. This adds a command-line workflow that fixes the candidate order, retains exclusions and records each source check and human review without overwriting earlier evidence.

It records Finn's agreement to **EDR-0001 (Choose an initial discovery grouping method)** while keeping the study unregistered. The prepared pool contains 80 candidates across 45 development repositories, with 12 repositories held out. These are candidates for source verification, not approved research inputs.

## Review sequence

| Commit | What it establishes |
| --- | --- |
| `eeaf5b2` | Record the explicit protocol agreement and freeze this bounded implementation scope. |
| `c3a2c54` | Reproduce candidate order, holdouts and complete exclusions from pinned source bytes. |
| `1deab3c` | Record ordered review attempts, enforce limits and preserve immutable evidence; includes the operator guide. |
| `1d56877` | Backfill preparation identities, integration history and remaining study gates. |

## Validation

**Standard checks:** Passed · revision `1d56877` · [Evidence](https://github.com/FinnNk/Meerkritic/tree/152c5af041a99fdff3a6bbcbce0cb5a99ae10155/records/r2/verification-summary.json)

181 tests passed; 0 skipped. Every semantic checkpoint passed in its own locked Windows/Python 3.12 environment.

| Behaviour | Added tests |
| --- | ---: |
| Candidate ordering, exclusions and source validation | 3 |
| Review evidence, quotas, shortfall and immutable command-line records | 6 |

No existing tests removed or altered. [Same-host replay](https://github.com/FinnNk/Meerkritic/tree/152c5af041a99fdff3a6bbcbce0cb5a99ae10155/records/r2/sample-replay-summary.json) reproduced the original plan's exact byte hash. [Documentation checks](https://github.com/FinnNk/Meerkritic/tree/152c5af041a99fdff3a6bbcbce0cb5a99ae10155/records/r2/docs-check.json) verified 316 local links and 59 imported-source hashes. [Architecture delta](https://github.com/FinnNk/Meerkritic/tree/152c5af041a99fdff3a6bbcbce0cb5a99ae10155/records/r2/architecture-delta.json): one domain module added; existing boundaries/contracts unchanged.

[DER review packet](https://github.com/FinnNk/Meerkritic/tree/152c5af041a99fdff3a6bbcbce0cb5a99ae10155): final diary/semantic trees match exactly. A reconstruction-only import-format error was caught at an intermediate checkpoint, retained and corrected before publication. Review is author self-review, not independent approval.

## Remaining work

- Qualify original sources, freeze normalisation configuration and collect the agreed human-reviewed inputs. The log records assertions; it does not authenticate people or prove source validity.
- Implement the lexical baseline, method-masked rating pack and analysis in the next material batch, stacked if this PR remains unmerged.
- Complete and commit registration before collecting grouping results or ratings. No comparison, human labels, method adoption or full slice closure is claimed here.
