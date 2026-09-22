# Repository structure and dependencies

Run commands from the repository root. In the original workspace it is named
`working`, with a sibling `extras` directory for local data; a clone may have a
different name. Runtime data and review evidence must remain outside Git worktrees.

## Find code and documentation

| Location | Responsibility |
| --- | --- |
| `src/semantic_reviewer/domain/` | Research records, valid states and domain rules |
| `src/semantic_reviewer/application/` | Use cases and the storage/runtime interfaces they need |
| `src/semantic_reviewer/routing/` | Model requirements, selection, policies and usage accounting |
| `src/semantic_reviewer/adapters/` | SQLite, filesystem, datasets, analytics, MAF and providers |
| `src/semantic_reviewer/web/` | FastAPI routes, forms and templates |
| `src/semantic_reviewer/bootstrap.py` | Shared dependency construction without web imports |
| `src/semantic_reviewer/asgi.py` | Web application assembly |
| `src/semantic_reviewer/worker.py` | Separate worker entry point |
| `config/` | Small public dataset manifests, model profiles and versioned routing configuration |
| `tools/` | Commands, quality checks and explicit maintenance tools |
| `tests/` | Behaviour, integration and workflow tests using permitted fixtures |
| `docs/` | [Task guides, references, decisions and history](../README.md) |
| `.agents/skills/` | Reusable documentation guidance and pinned independent review/design tooling |

Create finer packages or resource directories only when real work needs them;
empty directories are not an architecture plan.

## Dependency rules

| Layer | May depend on | Must hide or avoid |
| --- | --- | --- |
| Domain | Its own domain concepts | Routing, application, adapters and external frameworks |
| Routing | Its own reusable selection/accounting contracts | Domain, application and concrete providers |
| Application | Domain and routing | Concrete persistence, web and MAF types |
| Web | Application operations and allowed core records | Direct persistence or composition access |
| Adapters | The contracts they implement | Imports back into web assembly |
| Shared composition/worker | Concrete dependencies needed for execution | Direct or indirect web imports |

Import Linter defines high-level contracts; Tach enforces concrete module dependencies
and cycles. Callers should not manage SQL transactions, Parquet layouts or provider
response objects. Add interfaces when actual callers and implementations need them,
not as a forwarding layer for each entity. Concrete model names stay out of domain
and application routing logic.

## Local data and evidence

- Keep datasets, derived Parquet, SQLite, large outputs and model weights outside Git.
- Version small public manifests, methods, safe summaries and hashes when useful.
- Keep DER review evidence in its external store. The harness only indexes references.
- EDRs own empirical plans/results; ADRs own design decisions. Link their evidence
  rather than creating competing copies.
- A local path records where evidence lives; it is not proof that another person can reproduce it.

See [configuration](../../config/README.md) and [operational evidence](operational-evidence.md).
