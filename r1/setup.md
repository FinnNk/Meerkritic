# VS1 milestone architecture review

Assessed 20 September 2026: material. Hard triggers: public/runtime contracts,
persistent completion invariants, abstraction ownership and review policy.
Owner authorised all reported findings, workflow improvements and one PR; owner
retains merge authority. No VS2 implementation or plan PR is authorised here.

Base: 0bf957bcb0ae47e2c525f5f652830c06d5b8b9c9, merged main, tree
c642ecd33eb8c22d27ccb7cf3012be22ed652116. Dedicated App author/authentication.
Diary: change/vs1-architecture-review-diary. One integrator, no parallel authors.
DER alpha.2/method 7; canonical evidence outside application worktrees in this
directory and the helper's pairs/vs1-architecture-review store. Preserve all
discoveries/failures in actual chronology. No empirical selection is proposed;
correctness and prescribed guidance changes do not require an EDR.

Provisional propositions (reassess before reconstruction):
1. Define milestone-wide reviews and evidence-backed contract acceptance checks.
2. Enforce completion/outcome invariants with regression evidence.
3. Make artefact publication metadata and maintenance operations explicit.
4. Own source lookup, typed review queries and exclusive worker lifecycle.
5. Keep model execution controls behind the provider boundary.
6. Backfill remaining caller documentation and reconcile maintained knowledge.
7. Apply the milestone review with architecture/evidence and finding dispositions.

Each behavioural proposition includes its callers, tests and operational docs.
Guidance and existing-code docstring backfill remain separate semantic commits.
Tests are retained unless genuinely superseded with explicit rationale.

Design before implementation: prefer small records/validation over class
hierarchies for outcomes; explicit artefact metadata over inference from payload
keys; a direct observation lookup over pagination arithmetic; a worker session
owning lock/recovery/run over exposing ordering to callers. Keep existing
application-owned query ports without forwarding-only services. Do not introduce
unused configuration or change the storage/runtime architecture. Immutable
historical artefacts remain readable and indexing legacy references is explicit.

Required context: Windows/Python 3.12, locked dependencies, canonical quality
command at every semantic checkpoint and frozen diary; relevant live llama.cpp/
MAF verification, existing-data compatibility, typed architecture before/after/
delta and exact tracked-tree equivalence. Review claims remain self-review unless
independent evidence is actually obtained. No hosted CI exists; do not invent it.
