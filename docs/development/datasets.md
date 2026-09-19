# Public dataset registration

Run the root README commands with Python 3.12. `--data-root` must be outside Git
worktrees; a sibling `extras/runtime` keeps runtime files local. Importing runs in
the CLI, outside HTTP requests. `catalogue` lists manifests; `register <id>` verifies
source bytes, validates records, publishes Parquet and atomically registers metadata
with one event. Repeating registration returns the existing record without a new event.

## Source and interpretation

The first manifest pins [CRC-Py](https://github.com/busraicoz/crc-py-dataset) revision
`4176ac0013136ae3c8283fcdaf087d27159050cf`, file
`data/manual/manual_labeled_data.json` (1,030 records, 2,517,473 bytes).
The manifest contains the complete URL, revision and SHA-256. Its upstream
[MIT licence](https://github.com/busraicoz/crc-py-dataset/blob/4176ac0013136ae3c8283fcdaf087d27159050cf/LICENSE)
is copyright Büşra İçöz, 2025. Repository licensing does not establish ownership of
every originating snippet; inspect upstream terms before redistributing datasets.
No upstream code is executed and no source bodies are committed here.

The upstream pipeline preprocesses comments and code. We preserve supplied values,
not a claim of verbatim original GitHub comments. Categories are upstream labels,
not verified ground truth. Six comment identities repeat and 30 records omit
`enriched` context; all records are retained. Absent context becomes null in Parquet,
with the original bytes retained. Commit SHAs are unavailable and remain null.
A Python repository does not imply every source file is Python.

Observation identity is the source SHA-256 plus zero-based record index. Repeated
comments remain distinct; original comment IDs remain available for later analysis.
Revision, URL and hash persist in Parquet; SQLite also records the derived Parquet
hash and schema version. An importer/schema or pinned DuckDB change may alter
derived bytes and requires explicit versioning instead of replacing a registration.

This is an integration sample, not an empirically selected evaluation population.
Preflight inspected source structure, the first record and missing/repeated-field
counts. Later empirical evaluation must record prior exposure and pre-register its
decision-bearing analysis in an EDR.

## Storage and recovery

`state.sqlite3` holds small metadata and append-only events in WAL mode with short
transactions. Versioned SQL migrations use Yoyo. Bodies live in
`datasets/<sha256>.json` and `datasets/<sha256>.parquet`, never SQLite. Staging uses
the destination filesystem; exclusive hard links publish complete files without
overwriting existing different content. Use a local filesystem supporting hard
links, such as NTFS. Network shares are not validated.

A crash before SQLite commit may leave an unreferenced immutable file; repeating
registration is safe. Metadata and its event commit or roll back together. Keep
unreferenced files until an explicit retention policy permits cleanup. A missing
Parquet file can be rebuilt by registration. If a hash-addressed file has changed,
preserve it elsewhere for inspection before restoring/re-registering: the importer
never overwrites it. Back up the runtime directory with the app stopped, including
SQLite WAL files if present.

Tests use synthetic fixtures and need no network or model server. Observation
browsing and its read-time integrity checks are introduced in the next review commit.
