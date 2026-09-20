# Register and browse the public sample

The supplied dataset pairs review comments with code context. Registration downloads
its pinned source, checks the bytes and creates a Parquet copy for browsing.

## Register and inspect

Run from the repository root after `uv sync --locked`. Use a local-disk data directory
outside every Git worktree; the same directory must be used by the server and worker.

1. List available dataset manifests:

   ```text
   uv run --locked python tools/run.py --data-root ../extras/runtime catalogue
   ```

2. Register the public sample:

   ```text
   uv run --locked python tools/run.py --data-root ../extras/runtime register crc-py-manual-4176ac0
   ```

3. [Start the web application](../../README.md#browse-the-sample) and select the dataset.
   Expect 1,030 records. Repeating registration returns its existing record without
   adding another registration event.
4. For read API details, open `/docs` on the running server. Observation pages use
   `/api/datasets/{id}/observations?page=1&page_size=20`, with page sizes capped at 100.

Importing runs in the command-line process, outside web requests. Browsing queries
Parquet through DuckDB and verifies its checksum first.

## Understand the sample

| Property | Value or interpretation |
| --- | --- |
| Source | [CRC-Py](https://github.com/busraicoz/crc-py-dataset), revision `4176ac0013136ae3c8283fcdaf087d27159050cf` |
| File | `data/manual/manual_labeled_data.json`, 2,517,473 bytes |
| Licence | [Upstream MIT notice](https://github.com/busraicoz/crc-py-dataset/blob/4176ac0013136ae3c8283fcdaf087d27159050cf/LICENSE); inspect source terms before redistribution |
| Record identity | Source SHA-256 plus zero-based record index; repeated comment IDs remain distinct records |
| Missing information | Thirty records lack enriched context; it becomes null in Parquet. Commit SHAs are unavailable and remain null. |
| Duplicate comment identities | Six repeat; all supplied records are retained. |
| Labels | Upstream categories, not verified ground truth |

The upstream pipeline preprocesses comments and code. Meerkritic preserves those
supplied values; it does not claim they are verbatim original GitHub comments.
The repository's language does not establish the language of every excerpt.
No upstream code is executed during registration.

The manifest retains source URL, revision and checksum. SQLite also records the
derived Parquet hash and schema version. Changes to import/schema logic or pinned
DuckDB can change derived bytes and require explicit versioning.

## Storage and recovery

| Situation | Action |
| --- | --- |
| Registration interrupted before metadata was saved | Retry registration. A complete unreferenced file may remain; keep it for diagnosis. |
| Derived Parquet file missing | Run registration again to rebuild it from verified source. |
| A checksummed file changed | Preserve it elsewhere for inspection before restoring verified bytes. Registration will not overwrite conflicting content. |
| Backup needed | Stop application/worker processes and back up the whole runtime, including SQLite WAL files if present. |
| Network-share runtime | Use a local filesystem with hard-link support, such as NTFS; network shares are not validated. |

Source and derived files live at `datasets/<sha256>.json` and `.parquet` under the
data directory. Small metadata and events live in `state.sqlite3`, using WAL mode
and short transactions. Files are published completely before registration metadata
and its event are saved together. Do not remove unreferenced files without an explicit
retention decision.

This small sample supports integration work; it is not an empirically selected
research population. Record prior data exposure and register decision-bearing
analysis through the [EDR process](../edr/README.md). Full-file checksum checks on
each browse request would need reassessment for a much larger dataset.
