# R3 boundary revision

Owner feedback: https://github.com/FinnNk/Meerkritic/pull/3#issuecomment-5744852362
"This seems quite broad - please break it down into smaller reviewable units - I'd like each capability in its own semantic commit as its introduced."

Accepted. The prior single-proposition rationale over-weighted end-to-end coherence.
Registration has its own complete contract, browsing can consume it, and architecture
reporting is independently useful. No new application behaviour is requested.

P1: pinned dataset registration. CLI catalogue/register; verified source, canonical
Parquet publication, SQLite metadata/events, identity and data-root safety. Its tests
cover registration integrity/failure/concurrency. No browser/query API is advertised.
P2: bounded observation browser. Add DuckDB reads, application paging, FastAPI/HTML/API
and serve CLI with their provenance, escaping/restart/query tests. Depends only on P1.
P3: typed architecture reporting. Add snapshot/delta tool and its test/documentation.

Each checkpoint includes only its implemented capability and relevant documentation.
The final tracked tree must exactly equal frozen diary 951a28fc3da35160a01c61ba1e310f44b0d6d299
and published semantic 6556aa4e784d0713f3029b3140ae87c5c1b55767. Intermediate interfaces and
CLI are projections of that frozen content: browse/serve are introduced with P2;
no final source change, test retirement or invented implementation chronology.
Tests for later capabilities enter with their capability; P1 live registration also
checks repeat/reopen/WAL before the combined pagination regression enters in P2.
Run the canonical command in each checkpoint's own locked environment and source.

Original published round r2 and both histories already have a verified retained bundle
on evidence/vs1-dataset-browser-r2 at a1d853273c0ede460fc4bb9a806b50b7488fb811. Preserve PR
comments/reviews/timeline before updating. Local and published r3 state will be separate
from slice status; the retained application progress document is the original r2 snapshot.
The user's request to replace the current PR history authorises the necessary scoped
rewrite; use only --force-with-lease for the exact previously published head.
