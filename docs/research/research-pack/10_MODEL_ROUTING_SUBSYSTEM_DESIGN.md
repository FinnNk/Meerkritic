# Model Routing Subsystem Design

**Status:** Canonical cross-project routing architecture  
**Scope:** Generalised model selection, policy switching, escalation, context adaptation, budgeting, provider health, and telemetry.

This document defines the reusable routing subsystem used by the project. It is intentionally independent of any one model inventory.

The current concrete routing recommendations live in:

- `09_MODEL_ROUTING_POLICY.md`
- `MODEL_ROUTING_POLICY.yaml`

Those files instantiate this design for the first two inventories. The application and research-domain code should depend on the abstractions in this document, not on specific model names.

---

# 1. Design objective

The routing subsystem should support:

- different routing policies for different projects;
- different policies within the same project;
- task-level policy overrides;
- model escalation inside one policy;
- policy switching during a task;
- one-off model overrides;
- privacy/locality constraints;
- provider degradation/failure;
- budget constraints;
- context-window differences;
- independent reviewer selection;
- model retirement/addition without application-code changes;
- complete routing provenance and usage telemetry.

The stable architecture is:

```text
ModelInventory
      │
      ▼
Task ─────► TaskRequirements
                  │
                  ▼
            RoutingPolicy
                  │
                  ▼
            RoutingDecision
                  │
                  ▼
               ModelRun
                  │
          ┌───────┴────────┐
          ▼                ▼
       success         escalation
                           │
                   same policy or
                   policy transition
```

`Task`, `AgentRun`, `Experiment`, and research-domain entities must not need to know concrete model names.

---

# 2. Core entities

## 2.1 ModelInventory

A versioned statement of models that are currently available through configured providers/runtimes.

```yaml
ModelInventory:
  id:
  version:
  effective_from:
  models:
    - model_id:
      provider:
      family:
      status:
        active_current
        active_older
        deprecated
        retired
        unavailable
      locality:
        local
        remote
      capabilities:
        coding:
        tool_use:
        structured_output:
        reasoning:
        multimodal:
      context:
        advertised_input:
        advertised_output:
        practical_local_input:
      pricing:
        catalog_ref:
```

Capabilities may be populated from documented provider/model information and engineering inference. The source/evidence level should be retained.

The inventory answers:

> What can this environment use?

It does **not** decide which model should be used.

---

## 2.2 TaskRequirements

A model-independent description of what the task needs.

```yaml
TaskRequirements:
  task_id:
  task_class:
  coding:
  tool_use:
  structured_output:
  min_context:
  reasoning_level:
    low
    medium
    high
    very_high
  risk:
    low
    medium
    high
    critical
  privacy:
    public
    internal
    local_only
  reviewer_independence:
    none
    preferred
    required
  expected_duration:
  expected_output_size:
```

This object is the boundary between project logic and routing.

Application code should express requirements, not model names.

---

## 2.3 RoutingPolicy

A versioned policy that maps requirements and constraints onto a model inventory.

```yaml
RoutingPolicy:
  id:
  version:
  inventory_id:
  effective_from:

  routes:
    mechanical:
      primary:
      fallbacks:
    routine_coding:
      primary:
      fallbacks:
    difficult_reasoning:
      primary:
      fallbacks:
    architecture_high_risk:
      primary:
      fallbacks:
    long_context:
      primary:
      fallbacks:

  constraints:
    private_local_only:
    require_independent_review:
    max_task_cost:
    max_agent_run_cost:

  retry:
    deterministic_retry_limit:
    semantic_retry_limit:

  context_strategy:
    default:
    long_context:
```

The policy answers:

> Given this inventory and task requirement, how should the work be routed?

A completed task must retain the exact policy version used.

---

## 2.4 RoutingDecision

The concrete selection for one invocation or agent step.

```yaml
RoutingDecision:
  id:
  task_id:
  agent_run_id:
  policy_id:
  policy_version:
  inventory_id:
  task_class:
  selected_provider:
  selected_model:
  selected_tier:
  reason_codes:
  hard_constraints:
  soft_preferences:
  alternatives_considered:
  escalation_from:
  created_at:
```

This separates:

```text
what the policy says
```

from:

```text
what was selected for this specific request
```

---

## 2.5 RoutingPolicyTransition

A mid-task policy switch is a first-class event.

```yaml
RoutingPolicyTransition:
  id:
  agent_run_id:
  from_policy_id:
  from_policy_version:
  to_policy_id:
  to_policy_version:
  reason:
  requested_by:
    human
    router
    system
  created_at:
```

A policy transition must never silently rewrite the previous route.

---

## 2.6 AgentHandoff

When a task changes model or policy, the next model should receive a structured handoff rather than necessarily inheriting the entire raw transcript.

```yaml
AgentHandoff:
  task_objective:
  acceptance_criteria:
  current_plan:
  completed_actions:
  changed_files:
  tool_results:
  failing_checks:
  unresolved_questions:
  relevant_context:
  previous_model_summary:
  provenance_refs:
```

The full raw transcript remains available for provenance and drill-down.

This reduces:

- context waste;
- accidental propagation of irrelevant reasoning;
- context-window incompatibility between models.

---

## 2.7 ProviderHealth

Provider/routing failures must be separated from reasoning failures.

```yaml
ProviderHealth:
  provider:
  model:
  state:
    healthy
    degraded
    rate_limited
    unavailable
  observed_at:
  retry_after:
  evidence:
```

A provider `503` or rate limit should normally trigger infrastructure fallback, not escalation to a "smarter" model.

---

## 2.8 BudgetConstraint

Budgets are explicit routing inputs.

```yaml
BudgetConstraint:
  max_invocation_cost:
  max_task_cost:
  max_agent_run_cost:
  max_project_daily_cost:
  currency:
```

Budgets are **soft** unless explicitly marked hard.

A policy may choose a lower-cost eligible model when the preferred model would exceed remaining budget.

---

## 2.9 ContextStrategy

Context construction is independent of model choice.

```yaml
ContextStrategy:
  id:
  mode:
    retrieval_first
    summary_then_retrieval
    direct_large_context
  reserve_output_tokens:
  max_fraction_of_context:
  include_raw_transcript:
```

The context builder receives the selected model's practical context limit:

```python
context = context_builder.build(
    task=task,
    requirements=requirements,
    max_context=model.practical_context,
    strategy=policy.context_strategy,
)
```

This is essential for mid-task model changes.

---

# 3. Hard constraints versus soft preferences

## Hard constraints

A model is ineligible if it violates a hard constraint.

Examples:

```text
private code must remain local
required tool calling unsupported
required structured output unsupported
minimum practical context not met
provider unavailable
model retired
```

## Soft preferences

Soft preferences rank eligible models.

Examples:

```text
prefer lower spend
prefer lower latency
prefer local execution
prefer cross-provider reviewer
prefer current model generation
```

The router should filter by hard constraints first, then apply policy preferences.

---

# 4. Policy resolution hierarchy

Resolve the active policy in this order:

```text
explicit invocation override
        ↓
task policy override
        ↓
project default
        ↓
system default
```

The resolved policy and version must be recorded before execution.

A one-off model override does not automatically change the task's policy.

---

# 5. Escalation versus policy switching

These are distinct operations.

## Escalation

A policy-defined transition:

```text
Policy A
  Tier 1
    ↓
  Tier 2
    ↓
  Tier 3
```

The policy remains unchanged.

## Policy switching

The routing philosophy changes:

```text
local-first-v3
      ↓
cloud-quality-v2
```

This creates a `RoutingPolicyTransition`.

Analysis must be able to answer:

> Did the selected model fail, or was the active policy inappropriate?

---

# 6. Mid-task switching controls

The harness should eventually expose three distinct actions:

```text
Use current policy escalation
Choose a model once
Switch policy for remainder of task
```

These produce different provenance.

Example compact UI:

```text
Model: Local coding model
Policy: Local-first v3
18.4k in / 2.1k out · local · 42s

[Change route]
```

The detailed switch UI remains hidden unless requested.

---

# 7. Reviewer routing

Reviewer selection should be expressed as policy requirements rather than fixed provider pairs.

Example:

```yaml
review:
  low_risk:
    independent_model: optional

  material:
    different_model_family: preferred

  high_risk:
    different_provider: preferred
    different_model_family: required
```

The policy resolves these requirements against the active inventory.

This lets the same review policy work across cloud-only, hybrid, or private/local inventories.

---

# 8. Failure taxonomy

Routing telemetry should distinguish at least:

```text
deterministic_failure
    tests/lint/static gate failed

semantic_failure
    solution materially misunderstood task

provider_failure
    timeout/5xx/rate limit/unavailable

context_failure
    request cannot fit/construct useful context

budget_failure
    eligible route exceeds hard budget

policy_failure
    no eligible model satisfies constraints
```

Each failure type has different routing behaviour.

---

# 9. Usage and spend telemetry

The common `ModelUsage` design records:

- policy/inventory version;
- task class;
- route reason;
- provider/model;
- input/output/cached/reasoning tokens where available;
- queue time;
- time to first token;
- generation time;
- end-to-end turnaround;
- price-catalog version;
- estimated/provider-reported spend;
- escalation and policy transition history;
- outcome.

Near-real-time UI remains terse:

```text
Model · input/output tokens · estimated spend/local · elapsed
```

Detailed routing analysis remains behind drill-down.

---

# 10. Project-general policy portability

A project should normally need only:

```yaml
ProjectRoutingConfig:
  project_id:
  default_policy:
  allowed_inventories:
  privacy_default:
  budget:
  policy_overrides:
```

The semantic-code-review project is one consumer of this subsystem.

Future projects may choose different inventories and policies without changing the application-layer routing abstractions.

---

# 11. Policy lifecycle

Policies should have explicit states:

```text
draft
active
superseded
retired
```

A new policy version does not rewrite historical work.

Changes that justify a new version include:

- model added/removed from an active route;
- escalation order changed;
- review-independence rule changed;
- hard privacy constraint changed;
- budget semantics changed;
- context strategy changed materially.

Pure documentation clarification need not create a new policy version.

---

# 12. Model inventory lifecycle

When models are released or retired:

1. update `ModelInventory`;
2. preserve old inventory versions referenced by historical runs;
3. mark deprecated/retired models;
4. refresh policies only when a current route is affected or a new model has a clear operational reason to replace it;
5. do not run artificial bake-offs by default;
6. document whether route changes are based on:
   - provider documentation;
   - external supporting evidence;
   - engineering inference;
   - incidental operational evidence.

---


# Double-Entry Review provenance integration

A host using DER may attach `RoutingDecision` references to author/reviewer records and may express
reviewer independence in session/provider/model-family dimensions. These are provenance fields,
not routing requirements unless the host's material/critical review policy says otherwise.


# 13. VS1 implementation scope

VS1 should implement the **core contracts**, not every switching feature.

Required:

- `ModelInventory` version identifier;
- `RoutingPolicy` + version;
- `TaskRequirements`;
- `RoutingDecision`;
- `ModelUsage`;
- versioned price catalogue;
- project default policy;
- task-level override field;
- hard privacy/locality constraint;
- generic escalation provenance;
- context builder interface;
- provider failure classification;
- concise usage UI.

May be deferred until more than one policy exists:

- rich policy-switch UI;
- automatic mid-task policy transitions;
- policy comparison dashboards;
- complex budget optimisation;
- provider-health dashboard.

The design should make those later additions additive rather than requiring schema replacement.

---

# 14. Invariants

The routing subsystem must preserve these invariants:

1. Application/research-domain code does not hard-code model names.
2. Every model invocation has a recorded `RoutingDecision`.
3. Every completed run retains inventory + policy versions.
4. Policy switches are explicit events.
5. Local/private constraints fail closed.
6. Provider failures are not misclassified as reasoning failures.
7. Historical spend uses the price catalogue effective at execution time.
8. Model changes do not require rewriting task-domain entities.
9. Context construction adapts to the selected model.
10. The router can be replaced without changing the project's research logic.
