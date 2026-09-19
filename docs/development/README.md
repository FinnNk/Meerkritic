# Development

## Bootstrap status

The repository has documentation, pinned independent skills, a locked Python
quality toolchain and declared package boundaries. Package docstrings establish
importable boundaries for enforcement; no harness, worker, model adapter or
dataset pipeline is implemented. VS1 remains READY.

## Setup and checks

Use Python 3.12 and uv. The tested interpreter patch version and tool versions are
recorded with batch evidence; `uv.lock` fixes the development dependencies.

```text
uv sync --locked
uv run --locked python tools/check.py
```

The canonical command runs:

```text
ruff format --check .
ruff check .
lint-imports --no-cache
tach check
python -m unittest discover -s tests -p test_*.py
```

`tools/check.py` supplies this checkout's `src` path and resolves executables from
the current interpreter environment, including on Windows. Three architecture
negative-control tests inject forbidden imports into temporary copies and require
the appropriate checkers to fail for the intended reason, including direct external
persistence access. There are currently zero
application behaviour tests: that is an explicit bootstrap limitation. Add relevant
behavioural tests with each implementation change, and use the same quality
command locally, in review worktrees and in future CI.

Ruff checks Python source and project TOML; research Markdown is original source
material, not Python code to restyle. Within that scope it excludes only the
separately pinned upstream skill directory in addition to its standard exclusions.
We preserve those third-party files byte-for-byte rather
than restyle them. Their hashes are recorded in `docs/source-manifest.json`.
Import Linter and Tach enforce first-party package boundaries with no architecture
ignore rules. This vendor distinction must not be extended to bypass checks on
project code. Required public interfaces will be declared when real APIs exist.

## Commit messages

Use [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/):

```text
type(optional-scope): concise description
```

Use `feat` for features, `fix` for fixes, and appropriate types such as `docs`,
`test`, `refactor`, `perf`, `build`, `ci` and `chore` for other work. Scopes name a
meaningful area, such as `edr`, `routing`, `datasets` or `repo`. Keep descriptions
in British English and explain non-obvious reasons in the body.

Examples:

```text
docs(edr): define pre-registration and reproducible evidence
fix(routing): reject remote fallbacks for local-only tasks
feat(annotations)!: change the annotation decision contract
```

Mark incompatible contract changes with `!` before the colon or a
`BREAKING CHANGE:` footer that explains the impact and migration. This convention
also applies to DER diary and semantic commits. It does not authorise rewriting
diary chronology or splitting a complete review proposition by file/type.
For a squash merge, the owner should retain a conforming final commit title.
This foundation documents the convention; it does not claim server-side enforcement.

## Batches and review

Classify each software batch before substantive work. Architecture-contract and
evidence-policy changes are material; use the installed DER skill with one history
integrator. Keep external evidence, exact identities and required qualification
separate from a branch name. The owner merges on GitHub after reviewing the branch.

The empty initial Git baseline exists only to allow the first documentation branch
to target `main`. It carries no project files. All substantive files are introduced
on the review branch, with quality evidence before its first source commit.

## Integration preflight still required for VS1

Verify provider credentials/connectivity and capability, a pinned public dataset,
runtime dependency compatibility (FastAPI, SQLite, DuckDB and MAF), worker/recovery
behaviour, and DER worktree/evidence operations. Toolchain installation in this
batch is not evidence that those integrations work. Do not run paid model work or
download large datasets as part of this documentation bootstrap.
