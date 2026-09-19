# Routing

The routing package selects from a versioned inventory without invoking providers. Application code supplies `TaskRequirements`; configuration supplies model names. `select_route` returns the selected model, policy/inventory versions, context budget, rejected alternatives and reasons. A refusal is a decision with no selected model, not permission to choose a remote fallback.

Policy resolution is invocation override, task override, project default, then system default. Unknown or inactive versions are errors. A one-off model override retains the policy and checks the same constraints. Internal and local-only tasks require local models; the project or policy can additionally require locality for public tasks. Invocation overrides cannot relax project privacy. Operator-provided locality and capabilities require operational verification before actual execution.

Hard filters cover privacy, model lifecycle, provider health, required capabilities, usable input/output limits, excluded reviewer families and explicit hard budgets. Eligible models follow policy order, preferring those within a supplied soft budget. Quotes must name their currency and price version; missing/incompatible quotes fail hard budgets. Quotes are caller-supplied estimates, not guaranteed provider charges. Provider failures remain infrastructure observations and never trigger reasoning escalation automatically.

Context limits describe usable input and output capacities separately. The selected strategy reduces the usable input budget and reserves output capacity. Actual context construction and token counting belong to the workflow adapter; selection alone does not prove a prompt fits. Health observations and cost quotes are scoped to this invocation; the caller must refresh them before use.

`config/routing/example.json` is synthetic documentation, not a live model inventory or a recommendation. It deliberately lists a remote primary so that a default local-only task demonstrates rejection and selection of the local alternative. No provider endpoint, credentials or weights are configured by this file.

## Usage and spend

`Measurement` records completion outcome, token counts and observed timings. Input totals include cached tokens; output totals include reasoning tokens. Provider adapters must normalise that convention. Unknown counts remain `null`; they are never displayed as zero. Provider failures and semantic failures are distinct outcomes. Selection does not retry or escalate either automatically.

`account_usage` uses a supplied price catalogue effective at invocation start. Rates and currency are versioned, cached input is billed once and reasoning is already part of output. A missing catalogue, rate or necessary token count leaves the estimate unknown. Different cache rates require a known cached count. Provider-reported spend remains a separate observation. Local execution reports zero API spend without estimating hardware or electricity costs. The compact summary shows model, input/output tokens, estimated spend or local, and elapsed time; this is available to callers before the live workflow UI is implemented.
