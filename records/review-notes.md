# Annotation review and dispositions

Scope: complete backend/CLI and browser annotation change from merged main
b9ffa2ee49b60758dba6832f08b988f797b439af. Integrator self-review plus fresh-context
annotation_review source/boundary challenge (not platform approval).

AR-01: progress used independent SQLite reads, allowing mixed denominators during
concurrent completion/annotation. Fixed through an explicit read snapshot and a
test committing from a separate connection between queries.
AR-02: asynchronous form handling called synchronous disk/SQLite/DuckDB work on
the event loop. Fixed with thread-pool execution, including failed-draft rendering;
test observes distinct loop and storage thread identities.

P0 records accepted prior recovery policy. P1 establishes atomic terminal
judgements, idempotence, grounding, immutable edits and bounded review queries,
including CLI/tests/docs. P2 applies those contracts through same-origin bounded
forms, escaping, draft retention, result history and progress. Alternative: split
progress/history into a third software proposition. Rejected for this small query
surface; its snapshot and denominator rules form the review-store contract.
More complex queue/reporting semantics would justify reconsideration.

No test removed or weakened. New tests cover transaction rollback, competing
submissions, immutable state, source-grounded edit bodies, unavailable evidence,
source/result counts, browser injection/input bounds and event-loop isolation.

Software-design-clarity: validation and publication are centralised behind a
meaningful service; SQL/idempotence belong to the store. The application-owned
query port exposes no concrete adapter and needs no forwarding-only facade.
Transport parsing stays in the web layer. No new architecture ignore or boundary.

Limitations: single local reviewer; JSON edit form; latest 100 source decisions;
offset pages can shift as pending results are reviewed, so return to page one to
refresh the queue. Immutable orphan edit files may remain after partial failure.
These limits are explicit and do not imply staged/reopen/supersede support.

Browser verification: candidate port 8002 uses an isolated SQLite backup and copied
public artefacts, not the user's runtime. Submitted Reject for job
563c3c68-f783-46ca-a0ad-b53bc41ee210 with an explicit automated-test note. Browser
confirmed terminal decision/history and 1/3 reviewed results, 1/1030 source
coverage, one rejected result and two pending links. No model quality claim.
