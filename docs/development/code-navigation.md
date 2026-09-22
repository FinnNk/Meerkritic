# Navigate the code with CodeGraph

CodeGraph builds a local index of source symbols and their relationships. Use it
to find a starting point for a change, then read the relevant implementation and
tests. It is optional tooling, not part of running the harness.

## Working rules

- Index the application repository or a single worktree, never the parent workspace.
- Keep `.codegraph/` local and ignored. Rebuild it in each worktree; never copy an
  index between branches or between Windows and WSL.
- Keep the tool version pinned in `tools/codegraph/package-lock.json`.
- Refresh after edits or branch switches before relying on relationship results.
  A watcher only refreshes while its server is running; a saved database is not
  automatically current.
- Check consequential relationships against source. Dynamic Python calls,
  injected implementations, templates and configuration may be incomplete.
- Use `rg` for exact strings and files the index does not understand. A missing
  result does not establish unused code or permission to remove tests.
- Keep standard quality gates and typed architecture snapshots authoritative for
  their existing purposes. Graph output does not certify either.

The tracked `codegraph.json` excludes vendor skills, imported research and local
runtime/data paths. Default dependency/cache exclusions also apply. Do not broaden
the scan to find private evidence or other worktrees.

## Installation and verification

Setup commands and checked results will be recorded with the pinned installation.
Until then, use the existing source-search workflow. See
[ADR-0016: Local code navigation](../adr/ADR-0016-use-local-codegraph-for-navigation.md)
for the accepted decision and its confirmation criteria.

## Assess whether it helps

The initial index and example queries are installation checks, not proof of
efficiency. [EDR-0002](../edr/0002-code-navigation-assistance.md) defines a proposed
comparison with source search. Do not claim measured improvement or start that
comparison until its plan is registered.
