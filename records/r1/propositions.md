# Source reading: semantic review plan

Frozen diary: `070d547bf0154b12282738ea499c4cb46244fb26`.
Base: `a39b989d8fbb6842c73703ff320eee81e45a1a52`.
The frozen diary passed the canonical checks in its own detached checkout before
reconstruction. The diary remains the true implementation chronology.

| Proposition | Review promise | Diary source |
| --- | --- | --- |
| P1: define preserved source context | Explain the human/model evidence boundary, prospective study amendment and accepted ADR before application. | bc33734 |
| P2: preserve source reading with assessments | Attach verified, immutable upstream text; present it separately from model input; retain the presented identity in decisions and frozen selections. Include tests, importer, operational instructions and implemented ADR status. | af811ee, f00e4f8, dde8b35 |
| P3: backfill source comparison guides | Update existing guides and the synthetic screenshot/fixture for the completed behaviour. | f425a62, 070d547 |

The important constraints are unaltered model inputs, no inferred reconstruction,
fail-closed evidence integrity, stale-form detection, transactional binding and
downstream retention. A separate storage/importer prerequisite was considered;
one end-to-end proposition is clearer here because displaying additional evidence
without recording its identity would violate the central assessment contract.
Splitting by persistence/application/web layer would expose incomplete checkpoints.
P2 remains bounded to that promise; general guidance and existing-guide backfills
are separate. No dependency, model workflow or routing changes are included.

Each semantic checkpoint must pass all canonical checks with its own source,
locked dependencies and installed environment. Final tracked-tree identity is
required separately and is not a substitute for these tests. Review is author
self-review, not independent approval. Owner merges the stacked PR.
