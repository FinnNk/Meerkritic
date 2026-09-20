# Development

## Implementation status

The VS1 Data-to-Annotation implementation is integrated through PRs #7 and #8
at main revision `0bf957bcb0ae47e2c525f5f652830c06d5b8b9c9`. It includes public dataset
registration/browsing, routed llama.cpp calls through MAF, a separate worker,
structured provenance, immediate human annotation, progress and failure inspection.
See the [dataset guide](datasets.md), [normalisation guide](normalisation.md),
[annotation guide](annotations.md) and [VS1 progress](../slice-reviews/VS1-progress.md).
The milestone review is integrated through PR #9 at
`fa6856bff52efecba55700572cb10e67f9a8f3c0`. The [VS2 plan](../plans/VS2-plan.md)
activates [frozen annotation inputs](selections.md). [Grouping](discovery.md) is
integrated through PR #11. The current candidate adds [rule synthesis and a
versioned registry](rules.md); empirical adoption remains gated by draft EDR-0001.

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
project code. Public contracts are declared in application protocols and typed records; review
their actual consumers alongside the static architecture checks.

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

Apply the [milestone review method](milestone-review.md) after each vertical slice
or agreed milestone. Its build/PR checkpoints make invariant ownership, caller
contracts, concrete counterexamples and maintained-documentation reconciliation
part of acceptance. Use the linked template and retain evidence-backed conclusions.

Classify each software batch before substantive work. Architecture-contract and
evidence-policy changes are material; use the installed DER skill with one history
integrator. Keep external evidence, exact identities and required qualification
separate from a branch name. The owner merges on GitHub after reviewing the branch.

Follow the [code commenting convention](code-comments.md) when implementing and
reviewing Python code. Review affected [ADR statuses](../adr/README.md#lifecycle-review)
with the batch, including confirmation evidence and matching index entries.

The initial empty baseline supported the bootstrap PR. Subsequent batches start
from an identified integrated revision or an explicit stacked predecessor.

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
because there are several semantic commits. Always use stacked PRs at dependent
batch boundaries; use additional stacked splits when size or complexity warrants
them. Target each child at its immediate predecessor, link the dependencies
and state the review/merge order. Independent work need not form an artificial stack.
After a parent lands, update the child's base and verify the resulting revision;
follow the DER revision and evidence requirements where applicable. The owner still
approves and merges each PR.

This makes the existing [DER boundary guidance](../../.agents/skills/double-entry-review/references/guidance/boundaries.md)
an explicit project review check; it does not replace its qualification requirements.

### Agent pull requests

In PR descriptions and commit comments, give each project reference its code followed by its descriptive title in parentheses on first mention, for example **A1 (immutable annotation selection and eligibility)**, within **VS2 (Annotation-to-Rule Discovery)**. Apply this to slice, batch, proposition and ADR/EDR references as appropriate. Link the source record where useful, but do not require the reader to open it to understand the reference. Later mentions in the same description or comment may use the code alone when unambiguous.

Before publishing or updating a description or comment, check that its first references are understandable without cross-referencing the plan. Preserve owner amendments when updating existing prose. This convention does not require repeating titles on every mention or rewriting historical comments.

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

The public sample, SQLite/DuckDB path and web stack are integrated. The current
[normalisation batch](normalisation.md) exercises MAF core 1.19.0 with a real
llama.cpp b10964 server and pinned Qwen3 4B GGUF fixture on Windows/CUDA. Published
download hashes were verified. Context rendering, tokenisation, structured streaming,
usage, result provenance and worker recovery are checked separately. This establishes
compatibility, not model quality. Comparative model decisions still require an EDR.
