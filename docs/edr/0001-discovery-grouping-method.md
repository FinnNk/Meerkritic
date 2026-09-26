# EDR-0001: Choose an initial discovery grouping method

- Status: registered
- Created: 2026-09-20
- Owner: Finn Newick
- Decision-maker(s): Finn Newick
- Protocol agreement: Finn Newick, 2026-09-20; workload and criteria accepted
- Registered on: 2026-09-26
- Registered plan: `fe91fe4f888d9b5eb29e61f056f9b647a50559e4`
- Evidence outcome: pending
- Implementation: not planned until a recorded adoption decision
- Related records: [VS2 plan](../plans/VS2-plan.md), [ADR-0001](../adr/ADR-0001-record-significant-empirical-decisions.md)

## Completed prospective plan

The 40 input judgements are complete. The separate completed-plan commit above
freezes the agreed comparison before either research grouping method runs. This
registration records that commit; no grouping-quality ratings or research
comparison outputs have been collected or inspected at registration.

- Selection: `f5bc84b772da601d3a068e42cdbb77799e887628773084aa9fe9b32ca1fabdd7`
- Embedding profile: `23854bdeae747622f408c937902149651b40a4c4843c7cd48534bf9fc02bdfb6`
- Implementation: `9178de6ae6ff5aaaaf45497c0b79fd4efa217980`; registration changes documentation only.
- Identity inventory: [registration evidence](evidence/0001-registration.json).
- Execution instructions: [registered runbook](0001-runbook.md).

### Decision and hypothesis

Decide whether one fixed local embedding/grouping method merits becoming the
initial discovery default. Grouping affects which examples a researcher considers
together and which engineering rules they may propose.

The candidate is expected to improve human-rated group coherence over a simple
lexical baseline without unacceptable loss of coverage or execution reliability.
This is a small development-corpus comparison, not a repository-generalisation
claim, a model-accuracy benchmark or a search for optimal parameters.

### Inputs and prior exposure

| Item | Frozen choice or observation |
| --- | --- |
| Source | CRC-Py manual subset at revision `4176ac0013136ae3c8283fcdaf087d27159050cf`; source SHA-256 `a36405b45b65f6a193a12e15bb9c600d6c0f46d84eb4dc891f315248a7cade83` |
| Sample | Exactly 40 human Edit decisions from 21 repositories; maximum two per repository, within the agreed limit of five |
| Ordering | First 40 usable source-qualified inputs in the fixed `edr-0001-inputs-v1` candidate order; no selection by grouping output |
| Initial model outcomes | 25 successful drafts and 15 retained failed drafts; human corrections do not erase failures |
| Audit | All saved identities, edited hashes, source/result links and approved fields checked; SQLite integrity and foreign keys pass |
| Corrections | Assessments 1 and 35 have explicitly authorised replacement versions. Both originals remain: 42 historical versions, 40 selected observations |
| Representation | Assessment 20 retains a previously disclosed leading space in its source quote; assessment 33 stores a blank optional rule as null. Comparison normalises CRLF/LF only |
| Assistance | Finn Newick supplied each judgement in an agent-assisted walkthrough. These are neither unaided nor blind input labels |
| Extra context | Some judgements used separately retained public source context absent from model inputs. Annotation context digests record availability, not proof of reading |
| Negative concerns | Retain all 40 usable interpretations, including praise/no-concern judgements. Do not remove them after seeing group outputs |

The metadata-only plan examined 1,030 records across 59 claimed repository
identities. It reserved 12 holdout repositories, excluded the exposed pilot
repositories `django/django` and `paperless-ngx/paperless-ngx`, and retained 80
candidate positions across 45 development repositories. The mutually exclusive
excluded counts were 92 prior-exposure, 130 holdout, four duplicate and 724 outside
the candidate budget. Exact identities and the source/plan digests remain in
`preparation/0000.json` and the [initial preparation summary](evidence/0001-input-preparation.json).

Sampling was fixed before source inspection: hash case-folded repository identities
with `20260920:holdout:<identity>` and reserve the first ceiling of 20%; sort
development records by `20260920:sample:<source-hash>:<source-index>` within each
repository, then traverse repositories in lexical order, one record per round.
For repeated repository/comment identities keep the lowest source index; exclude
subsequent identical code/comment pairs. Deduplication does not rewrite the source.
The fixed pool has at most 80 positions, at most ten per repository. Stop human
review at 40 usable Accept/Edit judgements, with at most five per repository.

All 80 origins had already been checked and 55 qualified records normalised before
human collection. The one fixed model pass produced 33 successful and 22 failed
drafts. That preparation exposure includes 15 qualified but unused later records;
it is disclosed rather than presented as collection that stopped at the fortieth
source check. No model was rerun to improve an interpretation.

On 26 September the ledger was reconciled from retained receipts and saved human
decisions, without backdating it. Records `0002.json`–`0065.json` extend the original
two records: 40 usable decisions and 25 unresolved-source positions through the
stopping point. The terminal state is `ready`; its byte hash is
`5cdf78d995767fcdd609daeaa0969c3373650534b9b052dde13131b40453ebf8`.
The frozen selection contains exactly the audited current versions and no holdout
records. The inventory lists every selected source index, annotation and hash.

### Fixed methods

| Part | Registered choice |
| --- | --- |
| Shared text | Issue statement, newline, invariant or empty line, newline, categories joined by comma and space. No raw source, upstream taxonomy or annotation notes enter either method |
| Baseline | Case-fold; extract sets of ASCII tokens matching `[a-z0-9]+`; no stemming, stop-word list or fitted vocabulary. Connect pairs with Jaccard similarity ≥0.25; connected components of at least two. Empty sets are outliers |
| Candidate | Nomic `nomic-embed-text-v1.5.f16.gguf`, repository `nomic-ai/nomic-embed-text-v1.5-GGUF`, revision `0188c9bf409793f810680a5a431e7b899c46104c`, weights SHA-256 `f7af6f66802f4df86eda10fe9bbcfc75c39562bed48ef6ace719a251cf1c2fdb` |
| Embedding settings | Prefix `clustering: `; 768 dimensions; mean pooling; 2,048-token context; F16, CPU, eight threads; pinned llama.cpp `b10964-b29c606e2` |
| Candidate grouping | `cosine-components-v1`, threshold 0.85, minimum size two |
| Representatives | Greatest summed within-group similarity; ties follow input order. Human assessment covers every member |
| Runtime | Existing routed worker and Microsoft Agent Framework adapter; `config/routing/discovery-local.json` and `config/models/nomic-embedding-fixture.json`, whose exact hashes are in the inventory |
| Attempts | One run per configuration. At most one technical rerun across the whole study after a diagnosed implementation failure; retain original attempts. No tuning or successful reruns for different groups |
| Cap | Sum of execution attempts ≤30 minutes per method after loading. Exclude queueing and human review; record loading separately. Stop an over-cap run and retain the failure |

These thresholds were agreed on 20 September. Candidate 0.85 was an existing
exploratory example; baseline 0.25 is an untuned comparator. Neither is an adopted
default. If a repair changes registered implementation, stop, record the deviation
and amend prospectively before further research execution.

### Human rating and decision rule

- Build a method-masked pack with seed `20260920`. Sort each group's member IDs,
  hash canonical JSON `{seed, stage: "select", members}`, and rank within each
  method. Take `k = min(12, baseline groups, candidate groups)`.
- Fewer than eight groups per method makes the primary comparison insufficient.
  Do not relax that threshold, tune parameters or collect replacement inputs.
- Deduplicate identical membership sets; rate each once and reuse its judgement.
  Rank presentation with the same recipe and `stage: "present"`; present members
  in sorted identity order. Keep the method mapping separate.
- Finn Newick rates every displayed member set as `coherent`, `not coherent` or
  `uncertain`, with a short reason and any suspected unmasking. A coherent group
  expresses one specific reusable engineering concern across all members. A broad
  language/library/topic match is insufficient; contradictory or unrelated members
  make it not coherent; inadequate context makes it uncertain.
- Freeze all ratings before revealing method identities or comparative scores.
  Agents must not substitute their own ratings. Missing ratings leave analysis
  incomplete; similar content may compromise masking and must be disclosed.

| Criterion | Decision rule |
| --- | --- |
| Coherence | Candidate ≥75% coherent and at least 10 percentage points above baseline. Uncertain ratings remain in the denominator as not established coherent |
| Coverage | Candidate covers ≥60% of all 40 inputs and is no more than 10 percentage points below baseline. Report outliers and unassessed groups separately |
| Completeness | Every selected group rated; all final vectors and memberships valid and complete |
| Reliability | Both methods within the registered cap; retain every attempted failure and permitted retry |
| Adoption | Recommend candidate only if all applicable criteria pass. Otherwise record no adoption or insufficiency; Finn Newick makes the final decision |

Use exact fractions for thresholds; report counts, group sizes, repository
concentration, uncertainty and failures. Shared input does not imply matched groups.
One rater and a small exploratory corpus cannot establish inter-rater agreement
or population-wide superiority. An insufficient result may justify another
prospective study, but must not be relabelled success or used to adopt a default.

### Environment, evidence and reproduction

Windows 11 Pro `10.0.26200`, Python 3.12.11, Intel i9-13980HX (24 cores/32 logical
processors), 102,673,936,384 bytes RAM. Embeddings use CPU; the available RTX 4090
Laptop GPU is not used. The inventory records all relevant package versions,
`uv.lock`, routing, profile and server-binary hashes. Floating-point equality on
different hardware is not guaranteed.

The pinned synthetic live preflight returned three valid 768-dimensional vectors
through MAF 1.19.0. Two earlier synthetic attempts also completed inference but
the evidence helper failed while querying an absent optional package and then
serialising a measurement; their outputs remain. The helper was corrected before
registration. No research text was involved. Server logs show 2.922287 seconds
from startup to listening, with 0.301998 seconds between load-start and loaded.
The standard quality command passed Ruff formatting/lint, Import Linter, Tach and
all 259 tests on the unchanged implementation.

Retain selection bytes, source/context receipts, original model results, human
edits, vectors, memberships, attempts, framework/usage records, masked ratings and
analysis under `extras/research/edr-0001`, outside application worktrees. Commit
only permitted aggregate summaries, identities and reproduction instructions.
Hosted spend is not applicable to this local run; unavailable timing components
remain unknown. No electricity or hardware amortisation is inferred.

The pinned dataset URL is in `config/datasets/crc-py-manual.json`. Upstream README
and licence receipts are retained. Its MIT licence does not establish rights to
redistribute every third-party comment/code excerpt. Source receipts, annotation
text and raw model outputs remain local pending any sharing-rights review. Hashes
allow verification but cannot reconstruct the human labels: independent exact
reproduction requires permitted access to that bundle. Fresh judgements or model
runs are a new replication, not the original result. Independent reproduction and
byte-identical model output have not been demonstrated.

## Preparation amendments and history

| Date | Event | Effect and retained evidence |
| --- | --- | --- |
| 2026-09-20 | Finn Newick agreed workload and criteria | Fixed target, methods, budget and criteria; registration awaited actual inputs |
| 2026-09-20 | Metadata order and initial normalisation pass | 80 candidates, 12 repository holdouts; 55 attempts, 33 valid and 22 failed drafts; no human labels then. [Initial summary](evidence/0001-input-preparation.json) |
| 2026-09-20 | Owner permitted correction/rejection of failed drafts | Preserve one model pass and all failures; do not fabricate an empty draft or rerun until acceptable |
| 2026-09-20 | Assessment meanings clarified before first saved judgement | [ADR-0014](../adr/ADR-0014-clarify-assessment-field-meanings.md): investigation needs are not impact scope; applicability exceptions are not missing evidence. Walkthrough feedback 01/02 retained |
| 2026-09-21 | Owner agreed preserved source context | [ADR-0015](../adr/ADR-0015-separate-review-context-from-model-input.md): show separately retained originals, record context digests and extra human advice; preserve model inputs and earlier provenance |
| 2026-09-26 | Forty judgements audited; ledger reconciled; selection frozen | Agent-assisted inputs, authorised corrections 1/35 and representation allowances retained. No research grouping outputs yet |
| 2026-09-26 | Completed prospective plan | Exact code, inputs, configuration, environment and commands fixed; second commit will register this plan |
| 2026-09-26 | Registered | Names the separate completed-plan commit before either research method runs; no change to agreed criteria |

Prior compatibility work used synthetic embeddings, grouping, rule synthesis and
guidance under DER `vs2-rules/r1`; comparison tooling used synthetic checks under
`vs2-comparison/r2`. Exposed functional pilot annotations were automated decisions,
not eligible human labels. Those records are prior exposure, not evidence of
comparative quality. Earlier EDR drafts remain in Git history.

## Results and interpretation

Pending. No research comparison has been run.

## Decision

Pending. No grouping method has been adopted from this evidence.
