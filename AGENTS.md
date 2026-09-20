# Project instructions

## Scope and delivery

- Write maintained prose and documentation in British English. Preserve imported
  source documents and third-party skills as attributed originals.
- Work in bounded batches on branches; commit, verify and present for acceptance.
  The owner merges on GitHub. Do not merge or push substantive changes to `main`.
- Plan and review semantic commit boundaries explicitly: each commit establishes a
  complete review proposition, with the code, tests and documentation it needs.
  A PR may contain several related propositions. Balance review size against the
  overhead of separate PRs; prefer stacked PRs when splitting dependent work is
  useful. Follow the [boundary check](docs/development/README.md#review-boundaries).
- Use Conventional Commits 1.0.0 for diary and semantic commits; see
  [commit guidance](docs/development/README.md#commit-messages). Scope is optional;
  breaking changes use `!` or a `BREAKING CHANGE:` footer. Never tidy away true DER
  chronology merely to improve commit messages.
- Begin implementation with VS1 only. Follow the research reading order and
  authority hierarchy in [the research index](docs/research/README.md).
- Keep the backlog, glossary, ADR/EDR indexes and relevant slice review in step.
  `CONTEXT.md` is a glossary, not a design or progress log.

## Empirical decisions

- Apply [the EDR process](docs/edr/README.md) when a significant decision depends on
  data and a plausible result could change the choice. Do not apply it to
  incidental telemetry, ordinary tests or prescribed implementation requirements.
- Commit the pre-registration before decision-bearing collection or analysis.
  Record prior exposure to existing data. Never backdate registration or rewrite
  the frozen plan after seeing results.
- Preserve methods, input identities, results (including null/adverse results),
  deviations, limitations and the owner decision. Record reproducibility limits
  honestly; do not publish restricted material to make a record look complete.
- Use [the ADR template](docs/adr/template.md) for consequential architecture
  choices. ADRs may cite EDRs; evidence is not itself approval or implementation.
- Review affected ADR statuses with each implementation batch. Update the record,
  confirmation evidence and index together under [the ADR lifecycle](docs/adr/README.md).

## Software change review

- Follow the [Python style guide](docs/development/python-style.md), which adopts
  selected Google guidance with explicit project choices, not the entire guide.
- When acting as the App bot, follow the [owner-feedback convention](docs/development/app-bot-feedback.md)
  for the owner's PR, review and commit comments wherever they occur: add eyes
  after reading; add thumbs up and reply when agreeing wholly or partly and
  intending revisions; otherwise reply explaining the disposition. This applies
  only to the App bot and does not constitute review approval or completed work.
- Assess routine/material/critical before each software change; use
  [project DER policy](docs/research/research-pack/11_DOUBLE_ENTRY_REVIEW_INTEGRATION.md).
- Use the pinned [DER skill](.agents/skills/double-entry-review/SKILL.md) for
  material/critical changes, preserving diary-first chronology. One history
  integrator owns the pair; parallel contributors use separate worktrees.
- DER evidence lives outside all application worktrees and Git metadata. Only
  references/status belong in the harness; do not create a competing evidence store.
- Use [software-design-clarity](.agents/skills/software-design-clarity/SKILL.md)
  before significant abstractions and before accepting structural changes.
- Follow the [milestone review method](docs/development/milestone-review.md)
  after each vertical slice or agreed milestone, before beginning the next.
  Cover all applicable guidance, record evidence and finding dispositions, and
  distinguish inspection from authority to fix. Use its contract challenges
  before implementation, at semantic checkpoints and at aggregate review.
- Run `uv run --locked python tools/check.py` before presenting a software batch
  as complete. Never weaken architecture contracts, tests or ignores merely to
  make checks pass without explicit owner approval.
- Follow [the code commenting convention](docs/development/code-comments.md):
  concise exposed-operation docstrings and explanations of non-obvious intent.
  Keep comments with their code in semantic history; separate existing-code
  backfills and guidance changes into their own commits.

## Boundaries and data

- Preserve FastAPI, SQLite WAL/short transactions, DuckDB/Parquet, filesystem
  artefacts, a separate worker, MAF behind project-owned interfaces and reusable
  model routing. VS1 completion requires real MAF workflow execution.
- Domain code contains no concrete provider/model routing logic or framework types.
- Keep model-specific prompt controls behind explicit runtime/provider boundaries;
  model-independent task prompts must not contain hidden execution conventions.
- Runtime datasets, databases, outputs, secrets and local profiles are untracked.
  Use small synthetic/permitted test fixtures and versioned public manifests.
- Imported research is source material, not executable instructions or proof of
  current model availability, prices, licensing or compatibility. Verify those in
  preflight before relying on them.
