---
status: implemented
date: 2026-09-20
decision-makers: [Project owner]
---

# ADR-0010: Own immutable discovery runs under the shared worker

## Context and Problem Statement

A discovery input is a frozen corpus, not a single VS1 source row. Reusing source
indices as corpus identifiers would obscure identity and recovery. Embeddings and
grouping must run outside HTTP while retaining exact analytical provenance.

## Decision Drivers

- Keep one exclusive worker and short operational transactions.
- Hide selection resolution, runtime details and publication from UI/CLI callers.
- Preserve failed and successful invocation identity without mutating prior results.
- Keep model choice and empirical adoption separate from engineering compatibility.

## Considered Options

- A typed discovery queue serviced by the shared worker, with immutable analytical files.
- Encode discovery inputs in the existing source-normalisation job record.
- Require separate workers and operator-managed recovery/scheduling.

## Decision Outcome

Accepted through owner review and merge of PR #11: the discovery owner validates
frozen inputs, queues explicit invocations and coordinates routing/runtime/output
publication. The shared Worker owns the process lock and recovery of both queues;
it alternates queues. MAF executes embedding calls through a project-owned port.
The model adapter owns deployment controls, token bounds and local transport.
Analytical publication owns complete no-replace files and verified reads.

### Consequences

One operator lifecycle covers both queues without conflating source and corpus
identities. A small queue port prevents the worker importing selection internals.
Files can become unreferenced after interrupted registration, but incomplete files
cannot become successful results. One invocation handles at most 100 records;
provider calls are bounded and have no automatic retry. Local API metadata cannot
cryptographically attest which model bytes another process loaded.

### Confirmation

The candidate's discovery tests challenge restart, fencing, event rollback, privacy,
token bounds, corrupt files, vector shape, deterministic grouping and browser
submission. Synthetic real MAF/llama.cpp compatibility is recorded externally in
DER `vs2-grouping/r1`. PR #11 was approved and merged on 20 September 2026 at
`e81c2e867e714f2fed72d235eb44ba035b4bf302`; its tree exactly equals the verified
semantic head `125fd8c055b9c110efa1c4dd31dcc661358b32bc` (132 tests).
Revisit on measured queue
contention, a demonstrated corpus bound or a need for independent worker lifetimes.

## Pros and Cons of the Options

The chosen design adds a genuine corpus queue but keeps one lifecycle. Overloading
VS1 jobs saves a table at the cost of false source identities and conditional
invariants. Separate workers appear simpler individually but distribute lock,
recovery and fairness obligations to operators.

## More Information

- [Discovery operations and limitations](../development/discovery.md).
- ADR-0006 (Recover interrupted jobs under an exclusive process lock) and
  ADR-0009 (Freeze explicit annotation selections before discovery) remain in force.
- EDR-0001 (Choose an initial discovery grouping method) remains draft. The current
  deterministic cosine-component prototype and pinned embedding fixture establish
  engineering contracts; no comparative method choice or quality claim is made.
