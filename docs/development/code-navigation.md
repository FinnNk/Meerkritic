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

## Install and build an index

Use Node.js 24 and npm. Run these PowerShell commands from the application
repository or the worktree you intend to edit. The commands install only the
locked optional tool; the application continues to use its Python environment.

1. Install the exact packages, including the native package for your platform:

   ```powershell
   npm ci --prefix tools/codegraph --ignore-scripts --no-audit --no-fund
   node tools/codegraph/run.cjs --version
   ```

   Expect `1.6.0`. Keep optional dependencies enabled: they contain the bundled
   runtime. Lifecycle scripts are unnecessary for this package.

2. Create the index for this checkout:

   ```powershell
   node tools/codegraph/run.cjs init . --yes
   node tools/codegraph/run.cjs status
   ```

   Expect an indexed-file count and an up-to-date status. State is stored in
   this checkout's ignored `.codegraph/` directory. Counts change with the code.

3. Verify a known application symbol:

   ```powershell
   node tools/codegraph/run.cjs query create_app --json --limit 3
   node tools/codegraph/run.cjs callers create_app --json
   ```

   The definition should point to `src/semantic_reviewer/web/app.py`; callers
   include `build_app` in `src/semantic_reviewer/asgi.py`. Inspect the actual source
   before relying on a reported relationship for a change.

The launcher resolves the checkout from its own location and disables telemetry
and implicit binary downloads for its child process. It does not install global
agent configuration or change the current shell's environment. Calling it without
arguments shows help, not the upstream interactive installer.

## Use during development

The repository's agent instructions use the CLI directly; no MCP registration or
application server restart is required. Always invoke the launcher belonging to
the worktree being edited. Do not pass a parent-workspace path to `init`, `index`
or `--path`.

| Task | Command from the repository root |
| --- | --- |
| Refresh after edits or checkout changes | `node tools/codegraph/run.cjs sync` |
| Find a symbol | `node tools/codegraph/run.cjs query AnnotationService --json` |
| Read related source and call paths | `node tools/codegraph/run.cjs explore create_app --max-files 2` |
| Find callers | `node tools/codegraph/run.cjs callers create_app --json` |
| Inspect indexed files | `node tools/codegraph/run.cjs files --json` |
| Rebuild after changing exclusions | `node tools/codegraph/run.cjs index .` |
| Check state | `node tools/codegraph/run.cjs status` |

Automatic watching is available while CodeGraph's MCP server is running, but this
CLI setup starts no persistent server. Explicit sync is therefore part of the
working procedure. If MCP is connected later, configure the pinned launcher and
the intended checkout, then verify the connection; do not infer it from a CLI install.

## Recover or remove

| Symptom | Action |
| --- | --- |
| Tool not installed / native package missing | Repeat the locked npm install with optional dependencies enabled; do not use an unpinned download fallback |
| Missing or old symbols | Confirm the checkout, run `sync`, then inspect exclusions and the source; rebuild with `index .` if needed |
| Lock error | Check for an active CodeGraph process for this checkout; do not remove another process's lock |
| Template/config relationship absent | Use direct search and source reads; do not interpret an incomplete graph as proof |
| Trial is no longer useful | Stop using the CLI; remove only this checkout's `.codegraph/` and `tools/codegraph/node_modules/` directories if desired |

No application data is held in those two generated directories. Keep the pin,
configuration and guide unless deliberately retiring the project decision.

## Setup verification

The initial Windows x64 setup used CodeGraph 1.6.0, Node.js 24.18.0 and the checked-in
npm lockfile. In the `chore/codegraph-navigation` candidate worktree it indexed
115 files (110 Python, four YAML and one JavaScript), producing 2,018 nodes and
5,275 edges. These are index statistics, not correctness or efficiency scores.

| Check | Observed result |
| --- | --- |
| Known symbol and caller | `create_app` and `build_app` locations matched source |
| Scoped exploration | Returned source for `create_app` successfully |
| Incremental refresh | Temporary function addition, rename and deletion appeared after each explicit sync |
| Exclusions | Synthetic file under `.agents/` absent; enumerated paths contained no excluded research, dependency, runtime or parent paths |
| Final state | Temporary files removed; sync completed and status reported up to date |

To repeat the refresh check, add a uniquely named temporary Python function under
`tools/`, sync and query it; rename it and confirm the old name disappears; delete
the temporary file and confirm neither name remains after sync. Use a disposable
worktree and preserve any existing files. This initial smoke check did not test
branch switching, a persistent watcher or comparative task performance.

Local command transcripts and the verification script are retained outside Git
under `extras/review-evidence/codegraph-navigation/r1` in the development workspace.
They contain no human assessments. See
[ADR-0016: Local code navigation](../adr/ADR-0016-use-local-codegraph-for-navigation.md)
for the decision and [CodeGraph upstream](https://github.com/colbymchenry/codegraph)
for the tool reference. The pinned installation's help is authoritative for commands.

## Assess whether it helps

The initial index and example queries are installation checks, not proof of
efficiency. [EDR-0002](../edr/0002-code-navigation-assistance.md) defines a proposed
comparison with source search. Do not claim measured improvement or start that
comparison until its plan is registered.
