# Evidence-Grounded Semantic Code Review Research Pack

This pack contains:

- `01_SYSTEM_DESIGN.md` — architecture, data model, rule lifecycle, local inference, static/semantic detector strategy, BCA integration, repair and evaluation design.
- `02_EXPERIMENTAL_PLAN.md` — research questions, hypotheses, datasets, splits, manual adjudication, ablations, metrics, statistical treatment, go/no-go gates and staged execution.
- `03_LOCAL_DATASET_STORAGE.md` — local working-copy strategy, storage budgeting, immutable/derived layouts, Parquet/DuckDB usage, repository caching, worktrees, reproducibility and cleanup policy.
- `04_COST_MODEL_AND_BUDGET_SCENARIOS.md` — incremental cost model, cloud GPU/API examples, human adjudication, mutation/agent costs, cost controls, and local/hybrid/large-scale budget scenarios.
- `05_PROJECT_HARNESS_PLAN.md` — single-user research harness architecture, SQLite/DuckDB boundaries, programme/data/rule/experiment/agent workflows, MAF as default orchestration/runtime, DER status integration, knowledge continuity, staged interaction, architecture snapshots/deltas and extension triggers.
- `06_IMPLEMENTATION_HANDOVER.md` — implementation-ready vertical-slice delivery plan with entry/exit criteria, coding-agent guidance, quality gates, DER material-change policy and mandatory review/revision after every slice.
- `07_SOFTWARE_DESIGN_CLARITY_SKILL.md` — project integration note for the independent Ousterhout-inspired `software-design-clarity` skill.
- `08_AGENTIC_SOFTWARE_FACTORY_FRAMING.md` — the project as an evidence-driven agentic software factory, including DER as a material-change discipline and the semantic reviewer as a future factory component.
- `09_MODEL_ROUTING_POLICY.md` — versioned coding-agent model inventories and pragmatic routing recommendations.
- `10_MODEL_ROUTING_SUBSYSTEM_DESIGN.md` — project-agnostic model-routing architecture covering inventories, task requirements, policies, decisions, transitions, handoffs, provider health, budgets and context strategies.
- `11_DOUBLE_ENTRY_REVIEW_INTEGRATION.md` — materiality policy and host integration for DER pairs inside vertical slices.
- `IMPLEMENTATION_BACKLOG.yaml` — machine-readable slice/backlog definition.
- `SLICE_REVIEW_TEMPLATE.yaml` — mandatory review record for completed vertical slices.
- `CONTEXT.md` — strict glossary of stable project vocabulary.
- `external-skills/software-design-clarity.zip` — independently reusable design-review skill package.
- `external-skills/double-entry-review-core-0.3.0-alpha.2.zip` — paired-history review skill for material software changes.

All documents use independently resolvable references where external sources materially support the content.

## Baseline build policy

- Ruff enforces Python code conventions.
- Import Linter is the authoritative high-level architecture-contract layer.
- Tach enforces concrete module dependencies/interfaces/cycles.
- `software-design-clarity` provides advisory abstraction/design-quality review.
- Double-Entry Review is mandatory for material/critical PRs/changes before 1.0; routine changes use the normal factory flow unless DER is explicitly requested.

## Additional harness patterns incorporated

- `grill-with-docs` style vocabulary/ADR continuity through `CONTEXT.md`, ADRs and explicit decision traces.
- Archify-style typed architecture snapshots and before/delta/after review, generated from enforced architecture data rather than diagrams as source of truth.
- `grill-with-ui` style staged human decisions, defer/reopen semantics, per-object discussion, append-only interaction events, resumable agent interactions, and versioned/stale visual artefacts.

MAF policy: Microsoft Agent Framework is used from VS1 onward as the default orchestration/runtime substrate, isolated behind project-owned interfaces and retained unless repeated, material, unresolved friction provides evidence to replace it.

Interaction policy: VS1 uses immediate accept/edit/reject while establishing the generic event/provenance substrate; VS2 introduces staging, defer/reopen/supersede semantics, per-object discussion, and batched agent guidance.

The harness captures model token usage, versioned estimated/provider spend, routing/escalation history and turnaround timings, with only a terse near-real-time summary shown in the primary UI.

VS1 begins with an explicit integration preflight for model/provider availability, dataset access, and dependency/runtime compatibility; these are operational checks rather than unresolved specification decisions.


Terminology: **DER semantic history** means the reconstructed proposition-led Git history; **semantic review** means the code-quality review system being built. Keep them distinct.
