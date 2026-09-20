# VS1 verification and reproduction

The integrated VS1 implementation exercises the complete Data-to-Annotation path.
PRs #7 and #8 have been approved and merged. The milestone architecture follow-up
has its own verification and owner-review gate. The final slice review and VS2
plan remain on their separate local branch; this is an operational verification guide.

## Acceptance map

| Obligation | Implementation and evidence |
| --- | --- |
| Launch and reproducible public data | `tools/run.py register/serve`; pinned manifest and source/Parquet checksums; dataset tests |
| DuckDB browsing | Bounded observation queries over verified Parquet, preserving original records |
| Work outside requests | HTTP enqueues only; `worker` process owns OS lock, route, MAF execution and completion |
| MAF without core leakage | Owned workflow/model contracts; real MAF graph tests and live local calls; FrameworkObservation in bundles |
| Structured output/provenance | Source IDs, prompt, schema, raw model response, spans, inventory/policy, usage and immutable artefacts |
| Immediate human judgement | Accept/Edit/Reject; immutable result-level annotation and atomic event; grounded edits preserve original output |
| Progress and failures | Result and distinct-source denominators, pending queue, retained terminal failures and source decision history |
| Crash/restart | Process-death lock release, interruption without automatic replay, stale-worker fencing and retained partial evidence |
| Routing/privacy | Override hierarchy, version retention, hard locality/budget/context filters; infrastructure and semantic failure remain distinct |
| Telemetry/analytics | Input/output/cache/available timing, local spend or versioned hosted estimate; immutable Parquet usage export queried by DuckDB |
| Future routing compatibility | Reserved strict policy-transition and handoff records; health, budget and context records; no switch workflow in VS1 |
| Operational evidence | Artefact metadata, immutable structured lifecycle logs and explicit external DER reference index |
| Quality/architecture | Canonical Ruff/Import Linter/Tach/tests; typed snapshots and before/after/delta; no weakened contracts |
| DER | Separate material pairs, canonical diaries, reconstructed propositions, checkpoint-owned verification and exact tracked-tree equality |

`tests/test_vs1_path.py` joins the real MAF graph to synthetic deterministic model
responses, real SQLite/Parquet, HTTP submission and all three annotation actions,
then reopens services and queries exported usage. It complements narrower tests
for failed calls, source integrity, concurrency, publication failures and browser
security. It does not replace the separate-process, real-model live check.

## Live reproduction

1. Use Python 3.12 and `uv sync --locked` in an isolated checkout of the reviewed
   semantic SHA. Run `uv run --locked python tools/check.py`.
2. Follow [local inference](local-inference.md) to verify/start the pinned llama.cpp
   and model fixture, and [normalisation](normalisation.md) for the worker.
3. Choose a fresh external runtime. Register `crc-py-manual-4176ac0`, launch the
   harness and browse the public sample. Keep all commands on that same runtime.
4. Normalise an observation, verify that HTTP returns a queued job before the
   worker runs, then process it with `worker --once`. Inspect source, output,
   framework observation and telemetry. Retain failed outputs; do not bypass
   grounding merely to obtain a successful example.
5. Exercise Accept, Edit and Reject on separate successful results. In an automated
   check, label notes as functional-test decisions, not human research labels.
   Verify the original output hash remains unchanged after an edit. Restart the
   web/worker processes and inspect decisions, events and progress again.
6. In this disposable verification runtime, use an unavailable loopback endpoint
   for one explicit call. Confirm a provider failure, not a semantic-quality
   escalation. Interrupt a claimed worker, restart under the process lock and
   confirm one failed interruption, retained history and no automatic replay.
7. Export completed usage with `tools/route.py`, query it using DuckDB, and verify
   that unavailable counts remain null. Run `job-log` and, after an upgrade,
   `index-artefacts`. Index an explicitly qualified DER event and inspect its
   separate readiness page as described in [operational evidence](operational-evidence.md).

External `vs1-validation/r1` evidence retains the executable live method, actual
job/result identities, counts, usage/framework observations and logs. The public
DER evidence branch provides a sanitised replica and reproduction instructions.
Private data, credentials, weights and raw runtime bodies do not enter the repo.
No independent third-party reproduction is claimed.

## Limits

The tested platform is Windows/Python 3.12 with the pinned local GPU fixture.
Hosted spend is verified with synthetic versioned prices, not a billed hosted
call. No hosted CI is configured. Model output varies; successful schema and
grounding checks do not establish engineering correctness or generalisation.
The inspected model occasionally extrapolates beyond quoted evidence. Comparative
model, prompt or clustering choices therefore need a pre-registered EDR.

VS1 deliberately keeps one worker and reviewer, terminal annotations and a JSON
editor. It does not include staged decisions, discussions, rule discovery, a
vector store or durable MAF sessions. Runtime relocation needs a catalogue-path
migration. Diagnostic exports are regenerable; their failure does not undo a
committed job. Pending offset pages may shift during review.
