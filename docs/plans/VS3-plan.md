# VS3 preparation and remaining-slice revision

20 September 2026. Status: **DRAFT; not frozen or started**. VS2 software has a
review candidate for staged interaction and validation; owner integration and the
empirical registration/adoption gate remain distinct. This document revises future
work using observed contracts and limits, not speculative infrastructure needs.

## Entry gates

- Owner accepts the final VS2 batch; verify actual integrated proposition mapping
  and required checks without relabelling earlier candidate evidence.
- Resolve EDR-0001 (Choose an initial discovery grouping method): a permitted,
  explicitly human-labelled corpus, exact baseline/candidate method and thresholds
  must be registered before the comparison. Record an adoption, no-adoption or
  inconclusive outcome honestly. No automated fixture labels substitute for people.
- Identify a small candidate rule set, exact immutable versions, explicit evidence
  classifications and a repository-held-out historical sample. Promotion alone
  is not validation; source linkage alone is not a correct expected finding.
- Preflight permitted historical source access, pinned revisions and executable
  environments before freezing the first replay batch.

The owner may explicitly bound a software-only replay fixture before empirical
adoption, but that is not automatically authorised by this draft. Do not expand
into production PR integration, repair or internal repositories here.

## Proposed replay batches

**R1 — freeze replay inputs and outcomes.** A replay request binds exact rule
versions, repository/commit identities, allowed files, expected-label provenance
and split membership. Hide source retrieval and version resolution behind one
replay owner. Test missing/corrupt sources, duplicate units and holdout exclusion.
Deliver an inspectable immutable manifest before adding inference fan-out.

**R2 — execute and inspect historical findings.** Run deterministic checks where
sufficient, otherwise bounded routed MAF work behind owned contracts. Preserve
source spans, rule versions, raw output, usage and framework observations. Invalid
references fail visibly. Extend the shared worker queue contract; introduce
fan-out/fan-in only when this concrete workload benefits and record its evidence.
Do not add durable actors or distributed workers by default.

**R3 — compare and decide.** Show findings against independently reviewed historical
labels, including missed cases, false positives, exclusions and denominators.
Use version-fenced staged gate decisions and immutable generated reports. Significant
data-driven thresholds/method choices need pre-registration; correctness fixtures
do not. Reuse architecture freshness and perform the full milestone review with
finding discovery/remedy/earlier-detection traces before advancing.

Keep these substantial review batches, with complete semantic propositions inside
each and stacked PRs at unmerged batch boundaries. Finalise exact contracts and
acceptance evidence only for the next batch when its entry gates pass.

## Explicit revisions to VS4–VS8

| Slice | Revision informed by VS2 | Gate / trigger |
| --- | --- | --- |
| VS4 (Finding-to-Agent-Repair) | Bind repair guidance to exact finding/rule/source versions; agent responses remain distinct from applied edits. Retain explicit uncertain completion and no automatic replay. | Accepted replay contract and a concrete repair workflow; consider durable entities only for demonstrated long-lived coordination. |
| VS5 (Repair-to-Behavioural-Evaluation) | Separate source grounding, functional tests and empirical correctness. Preserve baseline/candidate artefacts and adverse outcomes; never infer validation from promotion. | Reproducible execution and independently justified expected behaviour before comparative claims. |
| VS6 (Programme Operations and Comparative Analysis) | Reuse immutable run identities, versioned routing/usage and honest denominators. Register meaningful comparative decisions before analysis. | Actual research volume and decision questions; no automatic optimisation dashboard for its own sake. |
| VS7 (Public-to-Internal Transfer) | Carry exact provenance and fail-closed locality to permissioned inputs; publish methods/hashes with explicit reproduction limits. | Owner-authorised internal data access and privacy boundaries; no internal data ingestion now. |
| VS8 (Operational Hardening) | Retain one worker, SQLite and filesystem until measured operational needs justify alternatives. Review authentication if the single-operator assumption changes. | Multiple users, persistent contention, distribution or remote artefact access; not routine growth in file count. |

All remain DRAFT except VS8, which remains CONDITIONAL. No later slice is READY.
