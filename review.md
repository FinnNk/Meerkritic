# R3 semantic review

Author-session self-review, complete for the new three-commit series and aggregate.
Owner approval remains outstanding. The user's boundary feedback is accepted.

Base: 3db848bd0992d0686bb5c45ddadd87ec6fbde8d2
Diary: 951a28fc3da35160a01c61ba1e310f44b0d6d299
Final semantic: 8e5e77f406639c88655c88c20341083f655e7013
Final tree: d75b25159a67a88e375babbd1c6d917476015a91
Manifest SHA-256: e6033aca059dbe8994fda72ee77789d9ce70be57410b7450c016c5f955009fea

## P1 — register pinned source evidence

cc0bca41402601028826865539c819375e23f0b9
Complete catalogue/import CLI, source hash validation, immutable Parquet, SQLite
migration/registry/events, runtime-root guard and provenance. Browser-facing DTOs,
browse methods, routes and serve command are absent. The lock has only registration
runtime dependencies, with no FastAPI. Tests travel with the registration contracts.
An exact-checkpoint CLI smoke registers/reopens/repeats the 1030-record sample in
separate processes, retaining one event and WAL mode. 11 tests plus all static gates
pass in a fresh environment. Documentation only claims registration at this point.

## P2 — browse registered observations

16a2b9daf89544df4550f53dda41f48f2c921b31
Adds read DTOs, bounded application/DuckDB paging, read-time integrity verification,
FastAPI UI/API and serve CLI. Includes its locked web dependencies and tests for
pagination/restart, corruption, escaping and invalid requests. Consumes P1's dataset
identity and registered Parquet, without revisiting storage correctness internals.
14 tests and all static gates pass in its own fresh environment; the public sample
HTTP/read/reopen/repeat smoke also passes from that exact checkout.

## P3 — report typed architecture

8e5e77f406639c88655c88c20341083f655e7013
Adds the typed snapshot/delta tool, deterministic structural test and usage docs.
No dataset/browser production code changes. 15 tests and all static gates pass in
its own fresh environment. The architecture contracts and allowed dependency
boundaries remain unchanged. The final tracked tree equals both the frozen diary
and the previously published r2 candidate byte-for-byte.

## Verification and test disposition

Use p1/p2/p3-isolated-checks.log and corresponding environment records. Initial
in-place runs retained surplus packages; environment-correction.md explains why
those runs are not used to establish strict dependency isolation. Fresh checkouts
and uv sync --locked resolved that gap; adverse logs remain retained. P1's package
inventory confirms FastAPI is absent. No later editable application code is loaded.

P1 carries eight existing registration tests plus three architecture negative controls.
The combined restart/pagination, corrupt-read and web test functions enter in P2,
where their complete capabilities exist. P1's CLI smoke independently verifies the
repeat/reopen/WAL obligation in the meantime. P3 adds the existing architecture
snapshot test. No final tests are removed, skipped or weakened; final lock and source
are unchanged. Intermediate CLI/docs are projections for capability availability,
not invented implementation chronology. The canonical diary is unchanged.

## Design clarity and remaining scope

Module depth, dependency hiding and layer responsibilities remain those of the
reviewed frozen implementation. The revised boundaries reduce the amount of shared
implementation a reviewer must keep in view: persistence first, its browsing consumer
second, structural reporting third. No new abstraction or tactical flag was introduced
just to split commits. No unresolved code/boundary finding from this self-review.
This is not independent review. Windows/Python 3.12 only; no model inference,
annotation, large-scale or power-loss qualification. Source progress docs retain the
original r2 batch reference; current DER round/readiness is in this external record
and the PR rather than changing application content for a history-only revision.
