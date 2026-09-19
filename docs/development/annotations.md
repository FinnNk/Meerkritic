# Human annotation

VS1 records one immediate Accept, Edit or Reject decision per successful
normalisation result. A repeated model run has its own decision; source coverage
counts each original observation once. Reject counts as reviewed, not accepted.
The local harness represents one human reviewer without an authentication claim.

An identical retry returns the original annotation without another event.
A conflicting decision is rejected; reopening and supersession belong to VS2.
Edits use the same interpretation schema and exact source-evidence validation as
normalisation. The original result and prompt/provenance are never overwritten.
Edited bodies are immutable, checksummed JSON files; SQLite holds references,
small decision metadata and an atomically appended event. A failure between file
publication and the transaction can leave an unreferenced file, never a partial
published decision. Source labels remain separate from human judgement.

Use `uv run --locked python tools/run.py --data-root <external-directory>
annotate <job-id> accept` (or `reject`). For `edit`, supply `--edited-json <file>`
containing a complete interpretation, optionally with `--notes`. The `progress
<dataset-id>` command reports all successful results, reviewed results and
distinct source coverage. History and pending queries are bounded and do not
depend on the recent-jobs limit.

These are correctness requirements, not an empirical comparison of annotation
policies. No annotation quality or inter-rater reliability claim follows from
the functional tests. Later research choices require pre-registered EDRs.
