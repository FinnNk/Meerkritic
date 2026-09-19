# Research and handover material

This folder holds relevant Markdown source material copied from `extras`, plus
the research pack's companion YAML files. Skill ZIP archives and datasets are not
included. Installed skills live separately under `.agents/skills/`.

`research-pack/` is an **unaltered source snapshot** of the supplied bundle. Its
glossary, backlog and review template show the initial handover state, not the
current state. Maintain these active records instead:

- [Current glossary](../../CONTEXT.md)
- [Current implementation backlog](../../IMPLEMENTATION_BACKLOG.yaml)
- [Current slice-review template](../slice-reviews/SLICE_REVIEW_TEMPLATE.yaml)
- [Empirical decisions](../edr/README.md) and [architectural decisions](../adr/README.md)

[Source provenance](../sources.md) identifies the original archives and hashes.
The [import manifest](../source-manifest.json) records exact copied-file hashes.
Keep originals intact; record subsequent decisions and explicit deviations in
maintained documents. Do not silently change or treat historical copies as live records.

## Reading order

1. [Research pack overview](research-pack/README.md)
2. [Current glossary](../../CONTEXT.md)
3. [Implementation handover](research-pack/06_IMPLEMENTATION_HANDOVER.md)
4. [Current implementation backlog](../../IMPLEMENTATION_BACKLOG.yaml)
5. [Double-Entry Review integration](research-pack/11_DOUBLE_ENTRY_REVIEW_INTEGRATION.md)
6. [Model routing subsystem](research-pack/10_MODEL_ROUTING_SUBSYSTEM_DESIGN.md)
7. [Harness plan](research-pack/05_PROJECT_HARNESS_PLAN.md)
8. [System design](research-pack/01_SYSTEM_DESIGN.md)
9. [Experimental plan](research-pack/02_EXPERIMENTAL_PLAN.md)
10. [Routing recommendations](research-pack/09_MODEL_ROUTING_POLICY.md)
11. [Reference routing YAML](research-pack/MODEL_ROUTING_POLICY.yaml)
12. [Dataset storage](research-pack/03_LOCAL_DATASET_STORAGE.md)
13. [Cost model](research-pack/04_COST_MODEL_AND_BUDGET_SCENARIOS.md)
14. [Factory framing](research-pack/08_AGENTIC_SOFTWARE_FACTORY_FRAMING.md)
15. [Design clarity integration](research-pack/07_SOFTWARE_DESIGN_CLARITY_SKILL.md)
16. [Current slice-review template](../slice-reviews/SLICE_REVIEW_TEMPLATE.yaml)

The separately supplied [coding-agent handover prompt](CODING_AGENT_INITIAL_HANDOVER_PROMPT_V3_DER.md)
is also retained as original research material.

## Authority and current qualifications

Current owner instructions govern the project. For conflicts within the supplied
specification, use: implementation handover, current backlog, DER integration,
routing subsystem design, harness plan, system/experimental designs, then
background documents. Record material departures with their source and rationale.

The owner's current requirement makes real MAF execution necessary for VS1
completion, despite the older handover's documented-blocker caveat. Rich
annotation interaction remains VS2; VS1 exposes Accept/Edit/Reject only.

Model names, prices, hardware assumptions and dependency descriptions in these
sources are dated recommendations. The reference routing YAML is not loaded as
runtime configuration. Verify provider availability and compatibility in VS1
preflight, then create explicit versioned configuration under `config/routing/`.
