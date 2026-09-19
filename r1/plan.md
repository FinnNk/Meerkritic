# Frozen proposition plan

Pair vs1-normalisation/r1. Base f1478217d43414da6e55599a5bf390c7f957dadb.
Diary frozen at 75feedbeef016036909a3458e66a06741e206e17. Source chronology remains
on change/vs1-normalisation-diary. An owned mirror preserves identical objects for
Windows helper/checkpoint execution without changing global Git trust.

The review question is whether one public observation can safely become an inspectable
model interpretation through local routing, MAF and a recoverable worker. It does not
claim model quality, annotation completion, distributed reliability or VS1 completion.

- P0: confirm owner-accepted ADR0005 implementation; docs/index only, baseline tests.
- P1: bounded literal-loopback transport with model/context checks, shared deadline,
  streamed usage and safe failures. ModelClient, adapter, HTTPX lock, tests and local guide.
- P2: proposed interpretation schema, unique exact evidence spans and real MAF graph.
  Depends on P1's owned inference contract; deterministic clients exercise MAF independently.
  Includes MAF dependency, framework failure observations, prompt provenance and contract guide.
- P3: durable single-worker queue, ownership/events, immutable bundles, process-lock
  recovery without replay, routing/usage integration and CLI. Includes actual process-death
  and storage-failure tests, ADR0006, routing fixture and CLI/recovery instructions.
- P4: local browser submission/read protection, queue/result rendering, escaped source,
  terse telemetry, templates, web tests and public/progress docs. Depends on P3 enqueue/read
  contracts; no model execution occurs in HTTP. Final bytes exactly equal the diary.

Alternative: combine P1/P2 as local normalisation, followed by jobs and browser. The
chosen split is clearer because transport and framework are independently testable
through ModelClient; neither needs knowledge of the other's internals. Separating
schema, code, tests and docs would create incomplete claims and was rejected.
Keep one related PR to avoid review overhead. P0 is independent accepted-decision
bookkeeping, not new governance. No commenting policy change or backfill is introduced.

A fresh-context reviewer challenged the series and identified stream/host protection
defects plus missing recovery tests. All were applied to the diary before freeze.
The reviewer agreed the four code propositions are defensible with their own complete
tests/docs. The full final review is self-review, not independent approval.

Required evidence: each of five semantic checkpoints and frozen diary in a clean
Windows/Python3.12 own-source/lock environment; Ruff/Import Linter/Tach/tests; architecture
before/after/delta; actual local model and browser flow; equality and ancestry; full
self-review. Hosted CI required set is empty under current project policy. No unsupported
POSIX execution claim. Publication and owner approval remain separate later gates.
