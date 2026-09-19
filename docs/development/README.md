# Development

## Implementation status

VS1 is in progress. Its first material batch implements public dataset registration,
the local observation browser, SQLite metadata/events and typed architecture snapshots.
The worker, model routing, MAF normalisation and human annotation remain the next
batch. See the [dataset guide](datasets.md) and [VS1 progress](../slice-reviews/VS1-progress.md).

## Setup and checks

Use the [Python style guide](python-style.md) for the adopted conventions and their project-specific scope. It incorporates selected Google guidance, not the entire upstream guide.

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
persistence access. Behaviour tests exercise real SQLite/DuckDB, import failures,
provenance, restart/idempotence, atomic events and HTML escaping. Use the same quality
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

Follow the [code commenting convention](code-comments.md) when implementing and
reviewing Python code. Review affected [ADR statuses](../adr/README.md#lifecycle-review)
with the batch, including confirmation evidence and matching index entries.

The empty initial Git baseline exists only to allow the first documentation branch
to target `main`. It carries no project files. All substantive files are introduced
on the review branch, with quality evidence before its first source commit.

### Review boundaries

Semantic commits are the primary units of detailed review. A PR can contain several
related capabilities and commits; it need not be limited to one capability. Balance
the overall review burden against the overhead of many small PRs. Neither a fixed
line limit nor a preferred commit count determines the boundary.

Before implementation, sketch the expected propositions. Revisit them against the
actual change before reconstructing semantic history, and check the resulting series
before presenting it for review:

- State what each commit establishes and which earlier contracts it depends on.
- Challenge commits that bundle independently assessable claims. For a substantial
  single-commit candidate, compare a plausible split and explain the concrete
  coupling if keeping it together.
- Keep the implementation, failure handling, tests and documentation needed by a
  proposition at the checkpoint where that proposition first becomes available.
  A checkpoint may depend on earlier commits; it must not borrow correctness from
  later ones. Preserve the separate guidance and existing-code backfill commits
  required by the project's commenting convention.
- Verify each required checkpoint in its own context and provide an ordered commit
  map in the PR description, proportionate to the change. Do not rewrite the actual
  DER diary chronology to match the proposed semantic series.

Split PRs when that meaningfully improves review or delivery, rather than merely
because there are several semantic commits. When splitting dependent work, normally
use stacked PRs: target each child at its immediate predecessor, link the dependencies
and state the review/merge order. Independent work need not form an artificial stack.
After a parent lands, update the child's base and verify the resulting revision;
follow the DER revision and evidence requirements where applicable. The owner still
approves and merges each PR.

This makes the existing [DER boundary guidance](../../.agents/skills/double-entry-review/references/guidance/boundaries.md)
an explicit project review check; it does not replace its qualification requirements.

### Agent pull requests

The dedicated `meerkritic-agent[bot]` GitHub App pushes work to topic branches and
opens PRs. Configure both Git attribution and authentication for the App; setting
a commit author alone does not select the account used to push or open a PR.
Keep the App's private key and generated tokens outside source control.

For the owner's comments on PRs, reviews and commits, the App bot follows the
[feedback acknowledgement and reply convention](app-bot-feedback.md): eyes after
reading; thumbs up plus a reply when agreeing and planning revisions, including
partial agreement; an explanatory reply otherwise. This convention is bot-only.

The repository's [active rulesets](https://github.com/FinnNk/Meerkritic/rules)
require PRs into `main`, one approving review and resolved review threads. New
reviewable pushes dismiss previous approvals, and the latest push needs approval
from someone other than its pusher. Force pushes and deletion of `main` are blocked.

Only repository administrators may merge through the separate merge gate; the App
has no bypass. The owner reviews, approves and merges the App's PR. The administrator
exemption applies to the separate update restriction; review and history protections
still apply. Owner-authored PRs also need another
reviewer's approval. Local quality checks remain required; these rules do not
establish hosted CI checks.

## Integration preflight

The public sample, SQLite/DuckDB path and web stack are exercised in the first
batch. MAF 1.19.0 completed an executor-only compatibility probe outside the
application; this is not model integration. The owner's local runtime preference
is llama.cpp. Its installation, selected model, inference compatibility and worker
recovery remain preflight obligations before the next batch can complete.
