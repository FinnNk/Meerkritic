# Documentation skill extraction evidence

Routine documentation change at f574faddfcc10aa774995094a998b2b2ce3db57a. No DER pair is claimed. The canonical check log, exact revision/environment, link/source checks and skill installation hashes are retained under records/. Self-review is not independent approval. No application behaviour or research data changed.

Reproduce software checks from the stated commit using Python 3.12 and `uv sync --locked`, then `uv run --locked python tools/check.py`. Validate the skill with the host skill-creator quick_validate helper using Python UTF-8 mode. Paths in auxiliary records are sanitised as listed in export-index.json.

Refinement r2 at 8d97bd67ddc09dbbbd9d140fb58199e6ec733ee0 adds a tick-box checklist and conditional commit advice, and clarifies shared/local project guidance. Current verification is under records/r2; earlier evidence remains unchanged.
