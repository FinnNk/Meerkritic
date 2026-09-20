# Frozen annotation inputs

Freeze explicitly chosen annotation versions before discovery. This first VS2
capability creates reproducible inputs; it does not run grouping or establish model
quality. Existing Accept/Edit/Reject decisions and their events remain unchanged.

Open a reviewed job to copy its displayed annotation ID. Create an external JSON
request using the exact versions you intend to include:

```json
{
  "dataset_id": "crc-py-manual-4176ac0",
  "annotation_ids": ["replace-with-an-actual-annotation-id"],
  "purpose": "fixture",
  "holdout_repositories": []
}
```

Run from the repository, with the same external runtime used for annotation:

```text
uv run --locked python tools/run.py --data-root ../extras/runtime freeze-selection ../extras/selection-request.json
uv run --locked python tools/run.py --data-root ../extras/runtime selection <returned-id>
```

Open **Frozen annotation inputs** in the harness to browse metadata, then select
a snapshot to verify its content and inspect ten records per page. Included and
excluded totals, fixture/research purpose, uncertainty and original/edit hashes
remain visible. Unknown snapshots return 404; unavailable/changed bodies return 409.
The catalogue lists metadata only and does not certify body integrity.

The first command returns the frozen identity, included/excluded counts and first
registration time. The second verifies and prints the complete snapshot. Freezing
runs outside HTTP; hashing source files may take time. No model or worker is needed.
Requests are limited to 256 KB and 100 distinct annotation IDs from one dataset;
the resulting snapshot is limited to 32 MB. Choose exactly one version per source.

Accept selects the original interpretation. Edit selects its verified replacement,
retaining the original result hash. Reject is an excluded interpretation, never a
verified negative. A source in the explicit `owner/repository` holdout list is
excluded (case-insensitively), even if accepted. If both reasons apply, the holdout
reason takes precedence and the Reject decision remains visible. No automatic
"latest" selection, deduplication of repeated comment IDs, uncertainty conversion
or removal of exclusions occurs. All-excluded snapshots are permitted and report
zero included records; they are not usable discovery corpora.

For research, use `"purpose": "research"`, a non-blank `"curator"` name and
`"human_review_attested": true`. This is an explicit claim by the curator that
included decisions were human-reviewed. VS1 has no authenticated actor record:
the software cannot independently establish that claim. Do not attest automated
test decisions. Fixture requests cannot carry this attestation. Holdouts are
declared, not discovered. Freezing/inspecting an explicitly selected holdout still
reads and retains its source; record that exposure and do not describe it as
untouched evaluation data. The applicable EDR must still freeze the full sample,
split, contamination controls and methods before decision-bearing analysis.

The snapshot contains registered dataset metadata, source records, exact decisions,
effective interpretations, exclusions and policy version. Ordered inputs, curator
and holdouts are part of content identity. Identical retries return the first
identity/time and create no new event; changed content creates a new identity.
Later annotations cannot enter an existing selection. Keep original source/result/
edit artefacts alongside the snapshot to reproduce its full provenance trail.

Bodies live at `<data-root>/selections/<sha256>.json`. SQLite contains only small
metadata and append-only events. Files are published completely before an atomic
metadata/event transaction. A crash can leave an unreferenced complete file; retry
registration rather than overwriting it. Missing/corrupt evidence fails freezing;
missing/corrupt snapshots fail reading or retrying. Restore verified bytes from a
trusted backup, never edit a content-addressed file in place. Reading a snapshot
checks its own bytes/schema/metadata, not ongoing availability of the original
artefacts. The selected source and effective interpretation remain inspectable
even when originals are offline; that does not prove full independent reproduction.

See [ADR-0009](../adr/ADR-0009-freeze-explicit-annotation-selections.md) for the
proposed durable provenance contract and [EDR-0001](../edr/0001-discovery-grouping-method.md)
for the separate, still-draft empirical decision.
