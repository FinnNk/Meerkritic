# Repository structure and boundaries

`working/` is the repository root. Its sibling `extras/` is outside Git. The layout
below describes intended ownership; create finer packages only when real work
needs them. Documentation replaces empty placeholder directory trees.

| Location | Responsibility |
| --- | --- |
| `src/semantic_reviewer/domain/` | Research concepts, explicit outcomes and invariants |
| `src/semantic_reviewer/application/` | Use cases and project-owned persistence/runtime contracts |
| `src/semantic_reviewer/routing/` | Reusable requirements, policy resolution, decisions and context contracts |
| `src/semantic_reviewer/adapters/` | SQLite/migrations, datasets, DuckDB/Parquet, filesystem, MAF and providers |
| `src/semantic_reviewer/web/` | FastAPI routes, forms, templates and static presentation |
| `src/semantic_reviewer/bootstrap.py` | Shared concrete dependency construction, without web imports |
| `src/semantic_reviewer/asgi.py` | Web-specific assembly |
| `src/semantic_reviewer/worker.py` | Separate worker entry point |
| `src/semantic_reviewer/resources/` | Packaged, versioned prompts when introduced |
| `config/datasets/` | Small public source/revision/hash/licence manifests |
| `config/routing/` | Validated versioned inventories, policies, prices and contexts |
| `tools/` | Canonical checks and explicit maintenance/generation entry points |
| `tests/` | Unit, integration and critical-flow tests; small permitted fixtures |
| `docs/research/` | Attributed original research and handover snapshot |
| `docs/edr/` | Pre-registered empirical plans, results and decisions |
| `docs/adr/` | MADR architecture decisions referencing EDRs where relevant |
| `docs/slice-reviews/` | Slice evidence summaries, deviations and future-slice revisions |
| `docs/architecture/` | Typed architecture snapshots and derived projections |
| `.agents/skills/` | Pinned independent DER and design-clarity tooling |

## Contract intent

The application exposes operations such as registering data, requesting
normalisation and recording annotation. Callers rely on explicit outcomes and
stable references; they should not manage SQL transactions, Parquet layouts, MAF
types or provider response objects. Those details belong to adapters. These
boundaries hide genuinely different dependencies without a forwarding layer per
entity. Add interfaces only when their callers and implementation exist.

Domain and routing are independent. Application may depend on both. Web calls
application; it cannot reach persistence adapters directly. Shared composition
constructs adapters, while web assembly and worker startup remain separate. The
worker must not import the web indirectly through shared composition.

Import Linter holds the human-readable high-level contracts; Tach declares
concrete allowed dependencies and rejects cycles. No model names belong in domain
or application routing logic. Later public API declarations must hide adapter
internals without creating speculative interfaces.

## Local data and evidence

Configure separate data, runtime and DER roots outside every application worktree,
normally under the parent `extras/`. Keep raw datasets immutable. Derived Parquet,
SQLite databases, large artefacts and model weights are untracked. Public manifests,
methods, safe summaries and hashes can be versioned for reproducibility.

DER evidence remains exclusively in its external store. EDRs may refer to it, but
empirical evidence and DER review evidence have distinct owners and purposes.
Never use a local path alone as a claim of independent reproducibility.
