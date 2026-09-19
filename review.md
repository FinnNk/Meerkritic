# Routing review

Scope: full self-review of final series 910b5d8, 55ee4bb, 638e852, 66431ee, plus a separate fresh-context boundary review. This is not owner approval or a claim of independent full correctness review.

P1: inspected precedence and all eligibility branches against the model-independent requirements. Defaults fail closed; unknown/inactive policies do not silently downgrade. Explicit model overrides consider only that model. Context, health and budget inputs retain their limitations. Synthetic configuration is explicitly labelled, not evidence of live availability. Tests cover policy precedence, private/local constraints, unavailable providers, unknown models, contexts, family exclusions, invalid schema and budget behaviour.

P2: reviewed cached/reasoning subset accounting, unknown count propagation, effective catalogue interval, local zero API spend and separate provider-reported cost. Unknown cached counts cannot obtain a falsely precise discounted estimate. Error outcomes are explicit observations; no automatic escalation logic is introduced. Tests exercise those branches and invalid observations. Provider adapters still have to normalise raw usage and populate observations; no live capture is claimed.

P3: reviewed transaction boundaries, write-before-return application contract, retained version payloads, refusal persistence, identical/conflicting retries and concurrent completion identity. Migration retains event sequence/content, append-only triggers and dataset delete/rename restrictions. SQLiteState owns the moved connection lifetime; unchanged dataset behaviour is covered by the baseline tests. The architecture snapshot test follows the moved owner, not a relaxed boundary. Price identity conflicts roll back. ADR-0005 is proposed pending owner acceptance.

P4: inspected command parsing, private error treatment for invalid Pydantic input, external runtime path checks, record-versus-preview distinction, no fabricated usage, parameterised SQL/Parquet operations and bounded SQLite row batches. File publication uses a complete staged file and a no-overwrite hard link on the same filesystem. Empty histories retain schema. Exports include exact configuration payloads, nullable metrics, provider failures and decimal strings. Existing output is preserved on conflict. Full SQLite history remains live; retention/rotation is deferred. Runtime path policy belongs to composition/CLI; low-level adapters assume trusted paths.

Aggregate: no provider or MAF dependency enters domain/application/routing; no model name enters application/domain logic; examples live in configuration. Pydantic was already locked transitively and is now explicit. Existing five Import Linter contracts and Tach boundaries are unchanged. No ignores, test deletions or architectural waivers were added. All 15 baseline tests remain, with 28 new contract/integration tests at the final checkpoint. No current evidence establishes model quality, authenticated connectivity, actual usage reporting or worker recovery.

Design-clarity review:

1. Complexity introduced/removed: typed config and provenance add validation complexity once; selection/accounting remain pure. Shared SQLiteState removes duplicated migration/connection rules.
2. Module depth: selection hides eligibility/reason construction; accounting hides subset/pricing rules; journal hides atomic version/event retention. Their exposed operations correspond to real caller decisions.
3. Knowledge leakage: provider/model identities remain routing/config data. Application uses project-owned records and its journal protocol; no framework SDK types cross boundaries.
4. Layer quality: application coordinates recording before execution and idempotent completion; adapters own SQL and export. No new wrapper exists merely to match an implementation-plan bullet.
5. Tactical cases: explicit unknown telemetry, refused decisions and immutable version conflicts are meaningful states. Future handoff/policy-switch orchestration is not speculatively implemented.
6. Simplifications: retained one small record-validation base and one SQLite owner. No material design issue identified within this scope. Future runtime integration must enforce locality against actual endpoints and verify token conventions; configuration claims alone are insufficient.

Verification: final checkpoint counts 26, 33, 40, 43; final diary 43. All canonical commands pass in separate locked Windows/Python 3.12 environments. Package source paths, lock hashes, commit/tree identities, argv and logs accompany each record. Exact final tracked trees match. Architecture before/after/delta shows additions and the SQLite owner move, with contracts/settings unchanged. No hosted CI is configured; approval and merge remain outstanding.

Known adverse evidence: initial environment installation failures, Yoyo fixture/architecture assertion corrections, formatting iterations and the initial P3 reconstruction formatting failure are retained. The replacement P3 passed; final-tree equivalence is not used as a substitute for its checkpoint test run.
