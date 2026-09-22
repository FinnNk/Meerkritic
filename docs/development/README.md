# Develop and review Meerkritic

Use this guide to prepare a change, check it and present it for review. For running
the application, start with the [task guides](../README.md). Read [AGENTS.md](../../AGENTS.md)
before implementation; it defines the active scope and required working practices.

## Set up and check

1. Use Python 3.12 and run commands from the repository root.
2. Install the locked dependencies:

   ```text
   uv sync --locked
   ```

3. Run the canonical quality command:

   ```text
   uv run --locked python tools/check.py
   ```

   | Check | Purpose |
   | --- | --- |
   | `ruff format --check .` | Python formatting |
   | `ruff check .` | Configured lint and import-order rules |
   | `lint-imports --no-cache` | High-level dependency contracts |
   | `tach check` | Declared module boundaries and cycles |
   | `python -m unittest discover -s tests -p test_*.py` | Behaviour, integration and failure checks |

The runner uses this checkout's source and interpreter environment. Use the same
command locally and in review checkouts. See [tests](../../tests/README.md) for what
it establishes and [workflow verification](verification.md) for live checks.

Ruff covers first-party Python and project TOML. Pinned third-party skills are
excluded as vendor source; their hashes are retained in `docs/source-manifest.json`.
Do not extend that exclusion or weaken contracts, tests or ignores merely to get
green checks without explicit owner approval.

## Prepare a change

Use [local code navigation](code-navigation.md) to locate symbols and callers.
The guide covers the optional pinned CodeGraph installation, per-worktree indexes
and source verification; it does not replace the checks above.

1. Identify the active batch in the maintained plan and inspect the working tree.
   Start a branch from its integrated baseline or an explicit stacked predecessor.
2. Classify the change as routine, material or critical before substantive work.
   Architecture-contract and evidence-policy changes are material. Use the pinned
   [Double-Entry Review skill](../../.agents/skills/double-entry-review/SKILL.md)
   where required, with one history integrator and evidence outside worktrees.
3. Describe the intended review commits. Each should establish a complete behaviour
   or obligation, including its necessary tests, failure handling and documentation.
4. Implement using the [Python style](python-style.md), [commenting](code-comments.md)
   and [documentation](documentation-style.md) guides. Check actual callers as well
   as declared interfaces.
5. Before changing assessment fields or collecting judgements, check the
   [assessment contract](assessment-contract.md) against prompts, schemas and UI.
6. Reconcile affected guides, glossary, backlog and [ADR statuses](../adr/README.md#lifecycle-review).
   Check whether a significant evidence-dependent choice needs an [EDR](../edr/README.md).
7. Verify the result and review the combined change before publication.

## Review boundaries

Semantic commits are the primary units of detailed review: each explains one
complete promise. A PR can contain several related capabilities. Balance useful
review boundaries against the overhead of many small PRs; use neither file count
nor a line limit as the deciding rule.

| Author/reviewer check | What to establish |
| --- | --- |
| Complete promise | State what the commit establishes and which earlier contracts it needs. |
| Plausible split | Challenge bundled independent claims; explain the coupling if keeping them together. |
| Evidence at the right point | Include required implementation, tests and operational documentation when the capability first appears. |
| No reliance on later fixes | Verify each required checkpoint with its own source, tests and locked environment. |
| Separate editorial work | Guidance updates and backfills of existing code comments/docs have their own commits. |
| Aggregate review | Revisit interactions and unchanged descriptions made stale by the change. |

For material changes, preserve actual implementation chronology in the DER diary,
then reconstruct the review sequence. Do not manufacture a tidy diary. Follow the
[DER boundary guidance](../../.agents/skills/double-entry-review/references/guidance/boundaries.md)
and the [milestone method](milestone-review.md) for the relevant checks.

When a dependent batch needs its own PR:

1. Stack it on its immediate unmerged predecessor and state the review/merge order.
2. Use additional stacked splits when complexity warrants them. Independent work
   need not form an artificial stack.
3. After the parent lands, update the child's base and verify the resulting revision
   under the applicable DER requirements. The owner approves and merges each PR.

## Commit messages

Use [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/):

```text
type(optional-scope): concise description
```

- Use `feat` for features, `fix` for fixes and appropriate types such as `docs`,
  `test`, `refactor`, `perf`, `build`, `ci` or `chore` for other changes.
- Use meaningful scopes, such as `routing` or `datasets`, and British English prose.
- Mark incompatible contracts with `!` or a `BREAKING CHANGE:` footer explaining
  the impact and migration. Apply this to diary and semantic commits alike.
- Keep any squash-merge title conforming. This convention is not server-side enforcement.

### Agent pull requests

Follow the [writing guide](documentation-style.md#pr-descriptions) and
[PR template](../../.github/pull_request_template.md). Lead with the problem and
resulting behaviour, then provide the commit map, meaningful validation and limits.

On first mention, give a relevant project code its descriptive title, for example
**ADR-0012 (Apply review intent in explicit batches)**. Later mentions may use the
code alone. Avoid references the reader does not need; preserve owner amendments
when updating descriptions or comments.

The `meerkritic-agent[bot]` App publishes branches and PRs. Use its authentication
as well as its Git author identity, keep credentials outside Git, and follow the
[owner-feedback convention](app-bot-feedback.md).

## Acceptance and milestones

- Main requires a PR, one approving review and resolved review threads. New reviewable
  pushes dismiss earlier approvals; someone other than the latest pusher must approve.
- Main blocks force pushes and deletion. Only administrators may merge through the
  separate merge gate; the App has no bypass. The owner merges on GitHub.
- Owner-authored PRs still require another reviewer. Local checks do not imply hosted
  CI execution; inspect current repository rules when qualifying a revision.
- After each slice or agreed milestone, perform the [architecture and guidance review](milestone-review.md)
  before starting the next. Record findings, remedies, evidence and future-work revisions.
- Keep owner acceptance, DER readiness, integration and milestone completion distinct.

Current delivery status belongs in the [backlog](../../IMPLEMENTATION_BACKLOG.yaml)
and [slice reviews](../slice-reviews/README.md), rather than in these instructions.
