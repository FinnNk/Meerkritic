# Model routing reference

Routing chooses a model that meets a task's needs and explains that choice. It does
not call a provider. Use [routing commands](routing-operations.md) to preview choices
or inspect retained usage.

## Inputs and selection

| Input or output | Meaning |
| --- | --- |
| `TaskRequirements` | Capabilities, privacy, context and other constraints supplied by the application |
| Model inventory | Versioned available models and their declared capabilities |
| Routing policy | Ordered preferences and constraints; model names live in configuration |
| `RoutingDecision` | Selected model or explicit refusal, versions, context budget and reasons |

Resolve a policy in this order:

1. Invocation override.
2. Task override.
3. Project default.
4. System default.

Unknown/inactive versions are errors. A one-off model override retains the policy
and cannot bypass constraints. Internal/local-only tasks require local models;
project or policy settings can also require locality for public input. Verify
operator-declared locality, capabilities and availability before execution.

| Selection rule | Behaviour |
| --- | --- |
| Hard constraints | Filter privacy, lifecycle, health, capabilities, input/output capacity, excluded reviewer families and hard budgets. |
| Eligible choices | Follow policy order, preferring models inside a supplied soft budget. |
| Hard cost budget | Require compatible currency and versioned quotes; absent/incompatible quotes fail the check. |
| Refusal | Return a decision without a selected model; it does not authorise a remote fallback. |
| Provider failure | An infrastructure observation, not a reason to automatically escalate reasoning strength. |

Cost quotes are caller-supplied estimates, not guaranteed provider charges. Health
and quotes apply to this invocation; callers must refresh them before use.

Input and output capacity are separate. The context strategy reduces usable input
space and reserves output capacity. The workflow adapter must render/count actual
prompt tokens; a selected route alone does not prove that a prompt fits.

## Usage and spend

`Measurement` describes outcome, token counts and timings. Adapters must use these
accounting conventions:

| Value | Convention |
| --- | --- |
| Input tokens | Include cached tokens. |
| Output tokens | Include reasoning tokens when exposed. |
| Unavailable count | `null`, never an invented zero. |
| Estimated hosted spend | Use the price catalogue effective at invocation start; retain its version/currency. |
| Cached-input pricing | Count cached input once; different cache rates require a known cached count. |
| Missing price or required count | Leave the estimate unknown. |
| Provider-reported spend | Retain separately from the estimate. |
| Local execution | Report local/zero API spend, excluding electricity and hardware. |

The compact display shows model, input/output tokens, spend basis and elapsed time.
Provider failures and invalid model output remain distinct outcomes; routing does
not automatically retry either.

## Persistence contract

| Operation | Guarantee |
| --- | --- |
| `RoutingService.route` | Save the decision and exact inventory/policy snapshots before returning, including refusals. |
| Worker invocation | Act only on a returned decision and bind its identity before model work. |
| Record retry | Accept identical identity/content without duplicate events; reject conflicting content. |
| `RoutingService.complete` | Retain one completion per decision. Identical concurrent retries return its original ID. |
| Conflicting completion | Reject changed measurements, outcomes or price-version content without partial writes. |

Each route call represents a new invocation. See
[ADR-0005: Retain immutable routing versions and invocation records](../adr/ADR-0005-retain-immutable-routing-provenance.md)
for the retention decision.

## Examples and reserved interfaces

`config/routing/example.json` is synthetic: it deliberately rejects a remote first
choice for local-only input. It supplies no live endpoint, credentials or weights.
See the [configuration guide](../../config/README.md) for runnable examples.

`routing.continuity` defines records for future policy transitions and agent handoffs:

- A transition retains both policies, requesting actor, reason and time; a no-op is invalid.
- A handoff carries structured task context and evidence references, not an implicit transcript.
- These schemas do not currently execute switching, persist a durable session or
  perform a handoff. Add runtime/persistence support only for a concrete workflow.

Health, budget and context records already participate in selection. Context
construction, provider calls and completion storage belong to the live workflow.
