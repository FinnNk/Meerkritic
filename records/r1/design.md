# Frozen scope: reproducible study input preparation

Recorded 2026-09-20, before implementation. Pair vs2-study-tools, round r1.
Baseline cd0a4d8c9a254e3027513274b39ce3f65cf227d2; baseline checks pass (172 tests).
Owner explicitly agreed EDR-0001 workload/criteria during this turn. Its status stays draft.

The earlier proposed scope included comparison/masking/report tools. Input inspection
showed that source qualification is a separate prerequisite: the claimed repository
identities cannot be treated as verified origins. Prioritise the bounded preparation
contract in this batch. Comparison tooling remains a subsequent material batch, using
synthetic fixtures while human input review is pending. No evidence has been discarded.

Deliver deterministic metadata-only sample/holdout/exclusion plans and a checked
preparation log, a CLI that refuses to replace published evidence, synthetic contract
tests and current operator documentation. No model execution, automatic labels, study
registration, comparative analysis, UI or schema migration.

Design clarity:
- What it does: owns the agreed sampling and preparation progress rules.
- Complexity hidden: partition ordering, duplicate identities/text, bounded round-robin
  sampling and prefix/quota/stopping validation.
- Caller guarantees: deterministic plan tied to source bytes, explicit exclusions and
  incomplete/ready/shortfall states; no inferred human review or source verification.
- Callers need not know hashing/sort/dedup sequencing; they supply original bytes and
  explicit evidence for attempts. Operators still verify sources and interpretations.
- Simpler alternative: one-off external script. Rejected because manually reproducing
  these eligibility/stopping rules across sessions would duplicate research obligations.
  Use one cohesive domain module plus a file/CLI boundary, no service framework.

Hard trigger retained: evidence identity/eligibility contract. One integrator /root.
Semantic propositions anticipated: (1) explicit owner agreement; (2) reproducible
sample plus complete attempt ledger, tests and operational guide; (3) delivery records.
Reassess these boundaries after the actual frozen implementation chronology.
