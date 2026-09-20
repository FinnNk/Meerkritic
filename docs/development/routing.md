# Routing

The routing package selects from a versioned inventory without invoking providers. Application code supplies `TaskRequirements`; configuration supplies model names. `select_route` returns the selected model, policy/inventory versions, context budget, rejected alternatives and reasons. A refusal is a decision with no selected model, not permission to choose a remote fallback.

Policy resolution is invocation override, task override, project default, then system default. Unknown or inactive versions are errors. A one-off model override retains the policy and checks the same constraints. Internal and local-only tasks require local models; the project or policy can additionally require locality for public tasks. Invocation overrides cannot relax project privacy. Operator-provided locality and capabilities require operational verification before actual execution.

Hard filters cover privacy, model lifecycle, provider health, required capabilities, usable input/output limits, excluded reviewer families and explicit hard budgets. Eligible models follow policy order, preferring those within a supplied soft budget. Quotes must name their currency and price version; missing/incompatible quotes fail hard budgets. Quotes are caller-supplied estimates, not guaranteed provider charges. Provider failures remain infrastructure observations and never trigger reasoning escalation automatically.

Context limits describe usable input and output capacities separately. The selected strategy reduces the usable input budget and reserves output capacity. Actual context construction and token counting belong to the workflow adapter; selection alone does not prove a prompt fits. Health observations and cost quotes are scoped to this invocation; the caller must refresh them before use.

`config/routing/example.json` is synthetic documentation, not a live model inventory or a recommendation. It deliberately lists a remote primary so that a default local-only task demonstrates rejection and selection of the local alternative. No provider endpoint, credentials or weights are configured by this file.

## Usage and spend

`Measurement` records completion outcome, token counts and observed timings. Input totals include cached tokens; output totals include reasoning tokens. Provider adapters must normalise that convention. Unknown counts remain `null`; they are never displayed as zero. Provider failures and semantic failures are distinct outcomes. Selection does not retry or escalate either automatically.

`account_usage` uses a supplied price catalogue effective at invocation start. Rates and currency are versioned, cached input is billed once and reasoning is already part of output. A missing catalogue, rate or necessary token count leaves the estimate unknown. Different cache rates require a known cached count. Provider-reported spend remains a separate observation. Local execution reports zero API spend without estimating hardware or electricity costs. The compact summary shows model, input/output tokens, estimated spend or local, and elapsed time; the live workflow UI displays it while fuller provenance remains inspectable.

## Durable provenance

`RoutingService.route` persists a decision and exact inventory/policy snapshots before returning. The worker acts only on a successfully returned decision and binds its identity before inference. Refusals are recorded too. Each call represents a distinct invocation. The journal accepts identical record retries without duplicate events and rejects conflicting identities.

`RoutingService.complete` retains one completion per decision. Identical concurrent retries return the original completion ID. Changed metrics, outcomes or price-version contents are rejected without partial writes. The event migration preserves dataset history while adding routing and usage subjects; [ADR-0005](../adr/ADR-0005-retain-immutable-routing-provenance.md) records the implemented retention decision.

`routing.continuity` reserves strict `RoutingPolicyTransition` and `AgentHandoff`
records. Transitions retain both versioned policies, requesting actor, reason and
time; a no-op transition is invalid. Handoffs carry structured task context and
provenance references, with no implicit raw-transcript field. These schemas do not
enable switching, create a durable session or perform a handoff in VS1. The runtime
and persistence protocol will be implemented only when a later workflow needs it.
Health, budgets, context strategies and escalation references are selection inputs
now. The live adapter constructs context, invokes the provider and persists completion.
Routing selection itself never invokes a model.
