# Semantic review map

Frozen candidate: `0c1f39f31ba6ecba36d4568eaa66ebc54056079b`; base
`c9ef38f48b10d7876fe26babee36f2f15f258bf3`. Reconstruction waits for the
checkpoint-owned final diary checks. Earlier diary `35354cc` passes 127 tests;
later diary commits separate the embedding/grouping test obligations and complete
composition annotations. No existing baseline test is retired.

## What matters and selected series

P1 (Activate autonomous stacked delivery): guidance and plan only, with verified
PR #10 integration and ADR-0009 lifecycle. No runtime changes. Check baseline suite.

P2 (Execute pinned local embeddings through MAF): reusable embedding messages,
numeric validation, embeddings routing capability/zero output capacity, local
deployment profile, bounded llama.cpp calls, shared loopback policy and real MAF
adapter. Mock provider tests exercise real MAF and privacy/token/identity/vector
failure contracts. No corpus queue is claimed yet. Existing normalisation tests
challenge the common endpoint policy.

P3 (Queue and inspect immutable embedding runs): frozen selection resolution,
short atomic queue/events, immutable ordered Parquet vectors, manifest provenance,
single-worker recovery, CLI and browser submission/inspection, ADR-0010 and guides.
Tests challenge terminal failures, partial publication, event rollback, concurrent
claims, lock fencing, corruption, source/version identity and same-origin writes.
Clustering is not exposed or accepted at this checkpoint.

P4 (Group pinned vectors reproducibly): deterministic cosine components, explicit
parameters and small-group outliers, immutable membership files and bounded source
inspection. Tests challenge deterministic repeat membership, representatives,
corrupt inputs and failed upstream runs. The numerical prototype does not adopt
an empirical method; EDR-0001 remains draft. Restores the exact frozen final tree.

Alternative: one full grouping commit after guidance, which forces model transport,
queue recovery and cluster semantics into one review proposition. Another option
was splitting by schema/adapters/UI/tests; those checkpoints would need later code
to establish their guarantees. The selected contract boundaries permit independent
assessment with complete local checks, without multiplying PRs.

Reconstruction removes later clustering operations/tests/docs from the embedding
checkpoint and introduces them with their implementation. Intermediate docs report
only available behaviour. The final tree must match the diary byte-for-byte. If a
checkpoint needs a content correction, return to the diary and preserve failed
evidence before reconstructing its changed descendants.
