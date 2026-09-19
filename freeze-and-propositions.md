# Frozen diary and proposition plan — vs1-dataset-browser / r1

Frozen diary: 44327420bca713e3c0c3b2d39b652723a46bf58a
Tree: c6cf46aeb3f2870ac8f3bb386f0d449042d7037c
Both bases: 3db848bd0992d0686bb5c45ddadd87ec6fbde8d2

Freeze follows passing canonical checks in a clean isolated clone using its own
locked environment and source. Evidence: diary-frozen-checks.log and diary-environment.log.
Windows/Python 3.12.14; 15 tests. No application edits after this freeze are permitted
on the semantic branch. The original diary remains intact in the working repository.

What matters: source bytes and every record survive interpretation-free registration;
SQLite metadata/event atomicity; bounded DuckDB browsing; web/storage isolation;
repeat/restart/failure behaviour; inspectable provenance and architecture evidence.

Selected proposition P1: register and browse pinned review evidence locally.
One complete end-to-end contract spans the catalogue, importer, registry, domain
read models, web, composition, CLI, migrations, tests and user documentation.
Architecture snapshots establish the batch's required structural evidence alongside
the enforced boundaries. Prerequisite: bootstrap at the pinned base only.

Alternative: P1 registration/storage and P2 browser/architecture. This would expose
a storage implementation checkpoint without the promised observable path and require
reviewers to reopen provenance/read contracts in the second commit. Another split
could isolate the architecture generator, but its current purpose is evidence for
this same material batch and the documentation describes the combined increment.
Choose one bounded proposition for this first usable path, with this internal map:
1 domain/read contracts and catalogue; 2 importer and source interpretation;
3 SQLite migration/atomicity; 4 CLI/web composition and escaping; 5 tests and tooling;
6 operational docs/ADR proposal and outstanding VS1 scope.
Challenge: if structural tooling grows into an independently operated feature, split
that future change at its own contract rather than carrying it in dataset work.

Evidence obligations: all four static gates and all 15 tests at the exact semantic
checkpoint, isolated locked interpreter/source; live 1030-record sample HTTP paging;
exact final tracked-tree equivalence; whole-proposition and aggregate self-review.
No model inference, performance claim, independent review or owner approval implied.

Actual chronology retained:
262fd8a initial implementation, seven tests reveal COPY binding error;
258c20c named COPY parameters and explicit closure of test SQLite connections;
541df38 live source repeats six comment IDs, so retain records by hash/index;
26d6384 source omits enriched context in 30 records, preserve null optional context;
b74b13d typed architecture evidence, test tuple/list mistake corrected before commit;
fe14ffd existing negative controls decode UTF-8 explicitly after observed failure;
4432742 usage, provenance, ADR proposal and progress documentation.
No tests were retired. Assertions against duplicate source comments were corrected
against the actual preservation requirement, replaced by assertions that both records
retain distinct observation IDs and source comment IDs. No architectural ignores added.

Preflight/operational limits: helper strips Git trust environment; mixed Windows
ownership blocked original checkout inspection. Ownership mutation was denied and
not performed. A same-owner isolated clone allows the unmodified helper to run.
The initial ledger entry was appended after these mechanical failures, not backdated;
assessment.md was written before implementation. Its relative assessment reference
is clarified here: ../vs1-dataset-browser/assessment.md from the evidence-store root.
Canonical diary commits, logs and this explanation preserve actual chronology.
