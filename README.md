# VS2 rule synthesis review evidence

This is a standalone evidence archive, not application history. The canonical
manifest, Git bundle and captured local ledger retain their original bytes.
`records/` contains sanitised methods, logs, identities, architecture data and
author self-review; export-index.json records both source and exported hashes.
Local paths use WORKSPACE and HOST_USER placeholders. No keys, tokens, runtime
databases, model weights or research datasets are included.

Verify SHA256SUMS, then use the bundled DER helper from the Git bundle to run
check-round against canonical/manifest.json. Fetch its semantic/diary objects into
a separate repository and run each recorded checkpoint with Python 3.12, uv and
its own locked environment: `uv sync --locked`, `uv run --locked python tools/check.py`.
The verification script shows the exact Windows method; adjust placeholder paths.
The live compatibility script uses synthetic fixtures and the publicly pinned
Nomic embedding and Qwen3 generation profiles, local llama.cpp servers and actual MAF. Its retained runtime
is local, not part of this archive. Model weights can be independently downloaded
at the pinned revision and verified by digest. Results are compatibility evidence,
not research labels, a registered EDR study or a method-quality claim.

Read boundaries.md and review-notes.md in records before reviewing the series.
Author self-review is not independent review or owner approval. No hosted CI run
is claimed. The owner controls acceptance and merge.
