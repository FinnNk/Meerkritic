# Author review: comparison tooling

Pair `vs2-comparison`, round `r2`; base `f5b23e44e4f13237a9f505f2f8182e0561813efe`, final semantic `2adeb88d3bbcf1af2ee8b5c498c7a32cbe1c100c`. This is full author self-review, not an independent review or platform approval. Exact checkpoint results are in verification-summary.json; earlier P1-P4 retain their identical r1 SHAs. r1's earlier P5 was not verified and was never published.

## Semantic review and contract challenges

| Proposition | Inspected contract and challenge | Evidence and limits |
| --- | --- | --- |
| P1 | Both methods must use the identical text; empty token sets must not make artificial groups; the inclusive Jaccard boundary and representative ties must be deterministic. | Compared the existing discovery consumer and new interpretation_text owner; test_study_grouping covers boundaries, transitivity, ties and bounds. Existing cosine discovery tests remain. No model-selection policy change. |
| P2 | Missing/uncertain ratings, shared groups or unequal group counts must not improve the result by changing denominators. Invalid partitions and successful-method reruns must fail. | Inspected Comparison/assessment/analyse and test_study. Explicit incomplete/insufficient/failed states; exact Fraction criteria; one failed-predecessor retry across methods; resource cap includes retained attempts. This validates fixed rules, not statistical superiority. |
| P3 | Plausible, valid Parquet can still contain the wrong text or grouping. Queue delay and a reused embedding must not inflate execution time. | Inspected baseline/assemble and existing discovery/storage/worker paths. test_comparison changes texts, membership, profile, parameters, timestamps and failure outputs; real SQLite/Parquet/MAF fixture workflow verifies saved provenance. Successful embedding reuse is counted once; failed embeddings cannot be reused. No human labels inferred. |
| P4 | A fixture, unregistered run or changed implementation must not claim a registered research comparison. Incomplete ratings must not expose scores. | Inspected registration and CLI branches; test_study_cli exercises isolated Git registration and immutable fixture publication. Full plan/registration SHA, exact selection/profile, code/configuration comparisons, timestamps and complete ratings are checked. The operator still owns truthful attestations, disclosure and private mapping separation; this is not authentication. A changed registered implementation requires an explicit stop/amendment. |
| P5 | Current guides and study records must describe the actual delivered capability and actual preparation shortfall without turning observations into human decisions or method results. | Inspected final documentation diff and aggregate-only preparation JSON. 80 sources, 55 qualified, 33 valid drafts, 22 failed outputs, no human labels or comparative run. EDR remains draft. Owner amendment is pending. docs-check.json covers actual command help, links, tables and imported hashes; no UI change warrants new screenshots. |

## Aggregate guidance review

- Architecture: two new modules own assessment rules and stored-evidence binding; existing grouping changes share text/component logic. Domain has no storage, provider or framework dependencies. Typed before/after/delta retains Import Linter/Tach contracts; no ignores, new dependencies, database schema or UI are added.
- Failures and evidence: whole partitions and bounded inputs are checked at the comparison boundary; expected failed/insufficient/incomplete outcomes remain explicit. Existing immutable JSON/Parquet ownership is reused. Registered execution checks are consistency checks and not a defence against forged or undisclosed activity.
- Runtime: this batch does not change routes, model controls or worker execution. Candidate inspection uses existing MAF-produced records; fixture integration checks run that workflow. Public input preparation used frozen code/model/prompt/routing controls separately; 22 model failures remain inspectable, not silently retried.
- Data: source bytes and model outputs stay outside Git. The committed preparation record contains counts, configuration and hashes, with reproduction/access limitations. A source 404 is unresolved, not evidence of fabricated data. Upstream licensing is not assumed to grant every third-party redistribution right.
- Knowledge and workflow: the existing EDR owns this fixed empirical protocol; no durable architectural decision needs a new ADR. Existing implemented ADR statuses do not change. Plan/backlog/integration records retain human/registration/milestone gates. A completed milestone architecture review cannot yet claim VS2 closure.
- Delivery: five complete propositions within one PR; P1-P4 contain their own relevant tests, P4 owns its new operator guide and P5 backfills existing documents. Main is untouched. Diary chronology and both rounds remain in the external pair. No test was removed or weakened.
- Validation limits: Windows/Python 3.12 and locked dependencies only. Existing library deprecation warnings remain visible. Synthetic test ratings are explicitly fixtures. No independent empirical replication, human approval, hosted CI run or grouping-method adoption is claimed.

## Complexity introduced or removed

The comparison introduces unavoidable study rules, but removes duplicated interpretation-text construction. A single domain owner handles assessment budgets, masking, denominators and thresholds, instead of making commands or analysts repeat them.

## Module depth

assessment/analyse expose small operations over explicit bounded state. baseline/assemble hide run resolution, replay checks, exact input binding and retry accounting. Their public contracts explain caller-supplied run IDs and the limits of provenance checks.

## Knowledge/dependency leakage

The application layer understands immutable run and selection records because binding those records is its responsibility. The pure domain layer sees only items, partitions, attempts and ratings. The command boundary owns Git registration and external publication. No concrete provider name or MAF type enters domain logic.

## Layer quality

Each layer changes the level of abstraction: stored evidence becomes a validated comparison, then masked groups and criterion results; CLI adds registration and publication. There is no added pass-through service or second evidence database.

## Tactical special cases

The fixed protocol is intentionally specific to EDR-0001. Thresholds and budgets are not exposed as tuning knobs. The two-commit registration format is documented and tested. Future registered code fixes currently require a stop/amendment; a generic amendment or experiment framework would add unneeded complexity now.

## Highest-leverage simplifications

Retain one text owner and reuse existing immutable storage/worker records. No material design defect was found in this bounded review. This does not prove correctness or replace owner review. The measured corpus shortfall is a research preparation gate, documented separately; its remedy must not be smuggled into the software comparison batch.

## Retained verification failure

The first r2 P5 canonical run executed 215 tests but ended with one cleanup error in RegistrationTest.test_changed_or_untracked_implementation_cannot_claim_registered_code. TemporaryDirectory.cleanup raised Windows WinError 32 deleting the temporary Git repository; no assertion failure was reported. The test subprocesses are synchronous. The process holding the directory was not identified, so an antivirus or indexing cause is not asserted. The four unchanged registration tests then passed with their ordinary cleanup. A new isolated checkout repeats the complete unchanged suite; both original and repeat records remain visible. No cleanup ignore, sleep or weakened test was added. A future recurrence warrants identifying the lock holder and addressing that cause.

The unchanged canonical repeat hit the same cleanup error a second time. Isolated registration checks with all test modules imported, with the preceding study tests, and with the exact Git environment each passed. A diagnostic full run (215 tests) instrumented cleanup to record the test process's own directory handles on failure; it passed without entering that error handler. Thus the lock holder is not established. A final ordinary canonical run is recorded separately; neither a successful rerun nor absence under instrumentation demonstrates a fix. Treat this as an intermittent Windows test-cleanup limitation, retain both failed runs, and revisit with lock-holder tracing if it recurs. No source, expected assertion, standard check or cleanup policy changed.

The final canonical run passed all 215 tests with no skips and all standard checks, at unchanged commit 2adeb88d3bbcf1af2ee8b5c498c7a32cbe1c100c. See p5-final-checks.json/log; this does not resolve the intermittent lock's cause.
