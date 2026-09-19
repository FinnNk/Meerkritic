# Agentic Software Factory Framing

**Companion to:**  
- `01_SYSTEM_DESIGN.md`  
- `02_EXPERIMENTAL_PLAN.md`  
- `05_PROJECT_HARNESS_PLAN.md`  
- `06_IMPLEMENTATION_HANDOVER.md`

**Purpose:** Explain the extent to which this programme is being built as an agent-assisted software factory, where it converges with and diverges from contemporary agentic software-factory practice, and how the semantic review system itself can become a reusable factory component.

---

# 1. Executive summary

The project can reasonably be described as an **evidence-driven, agent-assisted software factory**.

The description is accurate because the build is being organised around standardised work, reusable agent roles and skills, explicit vertical slices, machine-readable backlog and state, repeatable quality gates, architecture enforcement, experiment manifests, provenance, human approval points, parallel agent execution, and feedback-driven process revision.

However, the programme is not a classical fixed software factory. It contains a substantial **research and learning loop** in which the product definition, quality criteria, rule set, agent workflow, and even the factory process itself are revised as evidence accumulates.

The operating model is therefore better described as:

> **an agentic software factory with an experimental feedback loop**

or:

> **a research-driven software factory for building an evidence-grounded semantic code-review system**

The project has two coupled loops:

```text
PRODUCTION LOOP
specification
    ↓
agent implementation
    ↓
quality gates
    ↓
validated software

LEARNING LOOP
experiment
    ↓
evidence
    ↓
decision
    ↓
revise product / workflow / factory
```

The second loop is a deliberate part of the architecture rather than an exception.

---

# 2. What “software factory” means here

The term is used operationally rather than historically.

For this programme, a software factory means a development system in which software changes are produced through a repeatable pipeline with explicit inputs, roles, work units, validation, provenance, decision gates, and feedback.

The relevant abstraction is:

```text
intent / research evidence
        ↓
vertical slice
        ↓
coding agents
        ↓
Ruff / Import Linter / Tach
        ↓
tests / experiment checks
        ↓
architecture snapshot + delta
        ↓
software-design-clarity review
        ↓
human decision
        ↓
accepted artefact
        ↓
slice review
        ↓
revised future work
```

The goal is not to remove human judgement. The goal is to ensure that mechanical and repeatable work is automated, while human judgement is concentrated at points where ambiguity, trade-offs, or epistemic uncertainty remain.

---

# 3. Factory characteristics already present in the project

## 3.1 Standardised work

The project defines repeatable work through vertical slices, explicit entry/exit criteria, a machine-readable backlog, a canonical quality command, defined agent roles, slice-review templates, and experiment manifests.

## 3.2 Automated quality control

Quality control is layered:

```text
Ruff
    code conventions and linting

Import Linter
    high-level architecture contracts

Tach
    module graph, boundaries, cycles and interfaces

Tests
    executable behavioural checks

Replay
    held-out semantic-rule validation

Mutation testing
    targeted test adequacy

software-design-clarity
    abstraction and design quality
```

No single gate is treated as sufficient.

## 3.3 Traceability

The project preserves dataset versions, experiment manifests, model/prompt versions, rule versions, detector versions, agent runs, events, patches, architecture snapshots, architecture deltas, ADRs, slice reviews, and human decisions.

This is analogous to factory genealogy: each output can be traced back through the process that produced it.

## 3.4 Work-in-progress visibility

The proposed harness makes active jobs, active agents, blocked work, human queues, experiment state, gate state, rule maturity, and repair outcomes visible.

That supports supervision of multiple concurrent agents rather than one interactive coding session at a time.

## 3.5 Feedback-driven process improvement

Each completed slice must revise remaining slices where evidence warrants it.

```text
execute
  ↓
observe
  ↓
learn
  ↓
change process
  ↓
execute again
```

The factory itself therefore evolves through use.

---

# 4. Convergence with contemporary agentic software factories

Contemporary agentic development increasingly emphasises parallel agents, explicit orchestration, persistent state, human approval points, tool-mediated execution, and observable workflows.

The current project converges strongly with those patterns.

## 4.1 Parallel coding agents

Modern coding-agent environments increasingly support multiple concurrent agents and long-running tasks. OpenAI's Codex app explicitly positions multi-agent parallel work and supervision across the software lifecycle as a core interaction model [1].

This project adopts the same operating assumption:

```text
human
  ├── agent A: data adapter
  ├── agent B: worker/job system
  ├── agent C: architecture integration
  └── agent D: tests/documentation
```

Parallelism is used where contracts are stable enough to avoid uncontrolled merge and design conflict.

## 4.2 Explicit workflow orchestration

Microsoft Agent Framework represents agentic work as explicit workflows composed of executors, edges, state and events, with support for fan-out/fan-in, human-in-the-loop, and checkpointing [2], [3].

The project converges through explicit vertical slices, explicit job types, staged human decisions, workflow-compatible task boundaries, and longitudinal MAF evaluation through the project’s default workflow/runtime path.

## 4.3 Durable execution

Current agent platforms increasingly support agents and workflows that persist state across failures and worker lifetimes. Microsoft's durable support provides persisted sessions, workflow checkpointing, and distributed recovery [4].

The project converges conceptually through persistent `Job`, persistent `AgentRun`, append-only events, explicit restart/retry semantics, immutable artefacts, worktree preservation, and later evaluation of durable MAF agent sessions.

The distinction is that durability is introduced only when needed.

## 4.4 Human-in-the-loop control

Contemporary agentic systems increasingly treat human approval as a workflow primitive rather than an exceptional interruption.

This project explicitly models rule promotion, gate decisions, patch acceptance, retry decisions, staged guidance, and defer/reopen semantics. Human input is persisted as part of provenance.

## 4.5 Agent specialisation

Agentic systems increasingly favour specialised agents and subagents over one monolithic assistant.

The project similarly defines possible roles such as:

```text
dataset-engineer
harness-engineer
rule-synthesiser
replay-investigator
repair-agent
patch-reviewer
experiment-analyst
```

Specialisation is bounded by stable interfaces rather than role proliferation for its own sake.

## 4.6 Observability

Current agent frameworks increasingly expose workflow events, spans, metrics, and execution state. Microsoft Agent Framework includes workflow events, checkpoints, and observability capabilities [2], [3].

The harness likewise treats observability as core: job state, heartbeats, logs, events, model calls, artefacts, experiment IDs, and trace correlation.

## 4.7 Quality gates around autonomous work

A contemporary agentic software factory cannot rely on model judgement alone.

This project aligns strongly with that principle by placing deterministic and behavioural gates around agent output.

The factory does not accept:

```text
agent says done
```

as sufficient. It requires evidence.

---

# 5. Where this project diverges from contemporary agentic software factories

The differences are as important as the similarities.

## 5.1 Research is part of production

Many agentic software factories assume the target outcome is already reasonably well understood.

Here, the project is simultaneously learning what review rules matter, which rules generalise, which detector types work, where local models are sufficient, where static analysis is preferable, whether agentic repair adds value, and whether MAF abstractions are useful.

The factory is therefore partly producing **knowledge**, not just code.

## 5.2 Factory design is intentionally provisional

Later vertical slices are defined in advance but remain `DRAFT`.

After each completed slice:

```text
evidence
  ↓
slice review
  ↓
future slices revised
```

This differs from a highly standardised production line whose process is fixed before work begins.

## 5.3 Human judgement remains strategically concentrated

The aim is not maximum autonomy.

Human judgement remains authoritative for ambiguous semantic rules, architectural trade-offs, rule promotion, experimental interpretation, acceptance of design complexity, and decisions to revise the programme.

## 5.4 Local-first execution

Many commercial agentic factories assume managed cloud runtimes and hosted models.

This project deliberately favours local models, local datasets, SQLite, DuckDB, local workers, and filesystem artefacts. Cloud or distributed infrastructure is an escalation path, not the baseline.

## 5.5 Framework independence

The project does not commit the operating model to one orchestration framework.

MAF is the project’s default orchestration/runtime substrate and is evaluated longitudinally through real usage, while the domain model remains independent. OpenCode, Codex, Claude Code, and local-model runtimes are likewise adapters rather than architectural centres.

## 5.6 Architecture quality is explicitly reviewed

Many contemporary agent workflows focus strongly on task completion and verification.

This project adds a deliberate Ousterhout-inspired design-quality layer:

```text
does it work?
+
does it obey architecture?
+
is the resulting design simpler and better?
```

That additional question matters in an agent-heavy environment where tactical solutions can accumulate rapidly.

## 5.7 The factory can stop cheaply

The programme contains explicit go/no-go gates.

If held-out replay shows poor generalisation, the project can stop before expensive repair and mutation work.

This is closer to an experimental production system than a conventional continuous-delivery pipeline.

---

# 6. The two-loop operating model

## 6.1 Software-production loop

```text
slice specification
      ↓
agent tasks
      ↓
implementation
      ↓
static gates
      ↓
tests
      ↓
architecture/design review
      ↓
accepted software
```

This loop should become increasingly repeatable.

## 6.2 Research-learning loop

```text
hypothesis
   ↓
experiment
   ↓
observations
   ↓
analysis
   ↓
decision
   ↓
rule/process/product change
```

The learning loop can alter the production loop.

Examples include replacing a semantic detector with a static rule, altering an annotation schema, revising an architecture boundary, retiring the MAF path, introducing durable agent execution, or narrowing mutation usage.

---

# 7. Factory stations in the current programme

The current system can be thought of as a set of factory stations.

## Station 1 — Intake

Inputs: public datasets, review comments, issues, code comments, PR descriptions, and repository code.

Outputs: canonical source artefacts and provenance.

## Station 2 — Semantic normalisation

Inputs: raw evidence.

Outputs: structured observations.

## Station 3 — Human adjudication

Inputs: model observations.

Outputs: accepted/edited/rejected labels, verified negatives, and feedback.

## Station 4 — Pattern and rule discovery

Inputs: observations.

Outputs: clusters, candidate rules, and counterexamples.

## Station 5 — Rule validation

Inputs: rule and held-out code.

Outputs: replay metrics, false positives, false negatives, and a gate decision.

## Station 6 — Finding production

Inputs: validated rules and new code.

Outputs: evidence-backed findings.

## Station 7 — Agent remediation

Inputs: finding and repository context.

Outputs: candidate patch.

## Station 8 — Behavioural validation

Inputs: patch.

Outputs: tests, static checks, semantic re-evaluation, and mutation evidence where applicable.

## Station 9 — Human decision

Outputs: accept, reject, retry, or refine rule.

## Station 10 — Learning

Outputs: revised rules, revised workflows, revised future slices, and architecture changes.

---

# 8. How the semantic review system can become a factory component

If the research succeeds, the review system itself becomes reusable **factory machinery**.

Its role would be broader than a PR comment bot. It can become an evidence-producing component between implementation and acceptance.

```text
coding agent
    ↓
candidate change
    ↓
semantic review component
    ↓
structured findings
    ↓
repair / human review / validation
```

---

# 9. Component role: semantic quality gate

The simplest integration is as an advisory gate.

Input:

```text
diff
repository context
rule set
```

Output:

```yaml
findings:
  - rule_id:
    applicability:
    violation:
    evidence:
    explanation:
```

The factory can then decide:

```text
no finding
    → continue

advisory finding
    → record / optionally repair

high-maturity finding
    → require resolution
```

This adds semantic quality control alongside conventional static analysis.

---

# 10. Component role: repair trigger

For rules proven to be repairable:

```text
finding
  ↓
repair agent
  ↓
candidate patch
  ↓
validation
```

The semantic reviewer becomes the **trigger** for remediation rather than the repair mechanism itself.

This separation is important:

```text
reviewer
    identifies bounded problem

repair agent
    proposes solution

evaluator
    decides whether solution works
```

Do not collapse these roles unnecessarily.

---

# 11. Component role: training signal for the factory

The review component can feed learning back into the factory.

Examples:

```text
repeated agent violation
      ↓
update coding-agent skill/instructions

repeated architecture violation
      ↓
new Import Linter/Tach rule

semantic rule with strong static correlate
      ↓
compile to deterministic checker

frequent false positive
      ↓
refine applicability / counterexamples
```

The semantic review component therefore becomes both quality control and a process-improvement sensor.

---

# 12. Component role: agent supervisor

A more advanced factory may use the reviewer as an independent supervisory agent.

```text
implementation agent
      ↓
semantic reviewer
      ↓
feedback
      ↓
implementation agent revises
      ↓
deterministic validation
```

This can run before human review.

The review system should remain independent enough that the implementation agent cannot silently alter the criteria by which it is reviewed.

---

# 13. Component role: architectural drift detector

Because the rule system can combine code semantics, architecture snapshots, Import Linter, Tach, and historical rules, it can detect changes that are technically legal but architecturally suspicious.

Example:

```text
new dependency is permitted
but
it exposes storage/runtime knowledge to a higher layer
```

This is where semantic review and the `software-design-clarity` skill complement deterministic architecture enforcement.

---

# 14. Component role: rule compiler

A successful factory should attempt to reduce expensive semantic inference over time.

The semantic review system can identify rules that are stable enough to compile into a Ruff rule/plugin, AST check, Import Linter contract, Tach boundary, or dedicated static analyser.

Lifecycle:

```text
human observation
      ↓
semantic rule
      ↓
validated examples
      ↓
static correlate identified
      ↓
deterministic implementation
```

The review system thereby helps improve the factory's own efficiency.

---

# 15. Component interface

A factory-compatible semantic review component should expose a stable interface independent of model/runtime.

Conceptually:

```python
review(
    code_change,
    repository_context,
    rule_set,
    policy
) -> ReviewResult
```

Where:

```yaml
ReviewResult:
  findings:
  detector_versions:
  rule_versions:
  evidence:
  execution_metadata:
```

The component should not expose model-provider details, prompt internals, or orchestration-framework details unless needed for provenance.

---

# 16. Component maturity levels

The semantic reviewer should graduate through maturity levels.

## Research

- offline datasets;
- experimental rules;
- human inspection.

## Advisory

- real code;
- non-blocking findings;
- human adjudication.

## Repair-assisted

- selected findings trigger agent remediation.

## Policy-backed

- high-maturity rules affect acceptance gates.

## Factory infrastructure

- reviewer becomes a standard component used across coding-agent workflows.

Rules may exist at different maturity levels simultaneously.

---

# 17. Factory integration patterns

## Pattern A — post-agent review

```text
coding agent
  ↓
semantic review
  ↓
tests/static
  ↓
human
```

## Pattern B — iterative repair loop

```text
coding agent
  ↓
semantic review
  ↓
agent correction
  ↓
review again
  ↓
tests
```

## Pattern C — parallel reviewers

```text
candidate patch
   ├── tests
   ├── Ruff
   ├── Import Linter/Tach
   ├── semantic review
   └── design review
          ↓
       aggregator
```

## Pattern D — pre-merge supervisory workflow

```text
PR / patch
  ↓
quality workflow
  ↓
findings + evidence
  ↓
repair suggestions / human gate
```

---

# 18. Risks of factory integration

## 18.1 Feedback loops between agents

If implementation and review agents use similar models/prompts, they may share blind spots.

Mitigation: independent prompts/roles, deterministic checks, behavioural tests, and human sampling.

## 18.2 Review noise

A noisy semantic reviewer can reduce trust quickly. Precision should be prioritised over recall for advisory factory use.

## 18.3 Automation bias

Evidence-backed findings should remain inspectable. The system should show why a rule fired.

## 18.4 Metric and quality gaming

Agents may optimise to satisfy the reviewer rather than improve the design.

Mitigation: multiple independent gates, behavioural evidence, architecture-delta review, and human sampling.

## 18.5 Factory rigidity

Once a rule is embedded in a production workflow it can become difficult to challenge.

Rules should remain versioned, reviewable, and retireable.

---

# 19. Relationship to the harness

The harness is effectively the **factory control plane** for the research phase.

It manages work, agents, experiments, rules, artefacts, decisions, framework observations, and programme state.

If the semantic reviewer later becomes an operational component, the harness may remain the place where new rules are developed, rules are replayed, false positives are analysed, rules are promoted, and agent-repair behaviour is evaluated.

The runtime reviewer and the research harness therefore have different roles:

```text
runtime component
    executes mature rules

research harness
    develops, validates and governs rules
```

---

# 20. Relationship to Microsoft Agent Framework

MAF is the current project’s default factory-runtime/orchestration technology, while remaining isolated behind project-owned interfaces so that the software-factory architecture itself is framework-independent.

Its current workflow model supports explicit graph execution, fan-out/fan-in, human-in-the-loop, checkpoints, and multi-agent orchestration [2], [3]. Its durable extension supports persisted agent state, failure recovery, and distributed execution [4].

This project uses MAF as the default orchestration/runtime substrate from VS1 onward while keeping it behind project-owned interfaces, and evaluates its suitability continuously through real programme activities.

Possible long-term outcomes include:

```text
adopt MAF as a default for future projects
adopt MAF selectively by workload class
recommend MAF selectively/optionally for future projects by workload class
replace MAF if repeated, material, unresolved friction emerges
```

The software-factory concept remains independent of the framework choice.

---

# 21. Relationship to contemporary coding-agent products

The wider industry direction is increasingly toward supervising multiple agents rather than interacting with a single coding assistant.

OpenAI's Codex app describes parallel multi-agent work and supervision across the software lifecycle [1]. Commercial engineering-agent platforms likewise position autonomous coding agents as workers operating against enterprise engineering tasks rather than merely as autocomplete assistants [5].

The project aligns with that direction but adds stronger emphasis on explicit evidence, research methodology, architecture quality, rule provenance, controlled escalation, and process learning.

---

# 22. Recommended terminology

For internal documentation, use:

> **agentic software factory with an experimental feedback loop**

For a more formal description:

> **an evidence-driven, agent-assisted software factory for developing and validating semantic software-review capabilities**

For the semantic review system once mature:

> **a semantic quality-control and remediation component within the software factory**

These phrases convey the operating model without implying fully autonomous software production.

---

# 23. Practical implications for the build

The factory framing should influence implementation in concrete ways.

## Preserve standard interfaces

Agent/runtime/provider implementations should remain replaceable.

## Preserve provenance

Factory outputs without genealogy are difficult to trust or improve.

## Prefer independent gates

Do not let one agent both generate and certify its own work.

## Treat human decisions as first-class

They are part of the production process and should be recorded.

## Instrument the workflow

A factory that cannot observe its own performance cannot improve.

## Keep the learning loop open

Future slices, rules, and workflow design remain revisable.

## Avoid over-automation

Only automate decisions once their evidence and error costs are understood.

---



# Double-Entry Review as factory change-production discipline

For material software changes, the factory uses Double-Entry Review to separate truthful
implementation chronology from the curated history presented for review.

This complements parallel agent execution:

```text
parallel agents
  ↓
separate worktrees/contributor branches
  ↓
one history integrator
  ↓
canonical diary
  ↓
frozen verified result
  ↓
semantic proposition history
```

DER therefore acts as a factory component for **change preparation, review provenance and revision
readiness**, while the semantic-review system acts as a **quality evidence component**. Neither
substitutes for the other.

Before DER 1.0 the factory requires it only for material/critical changes to avoid excessive
process overhead; the threshold can be revisited using incidental operational observations.


# Model routing as factory infrastructure

The model router is a reusable software-factory component rather than a property of the semantic-review product.

It allows different factory workloads and projects to apply different routing policies while preserving a common execution contract.

A factory may therefore run:

```text
Project A
  cloud-balanced policy

Project B
  local-first policy

Task X
  temporary high-quality policy override
```

without changing the agent/task domain model.

Mid-task policy transitions are explicit factory events and remain visible in provenance.

This makes the routing layer itself reusable alongside other factory components such as:

- job execution;
- agent runtime;
- semantic review;
- deterministic quality gates;
- artefact/provenance storage.


# 24. Conclusion

The software-factory characterisation is accurate provided the project is not mistaken for a fixed autonomous assembly line.

It is better understood as:

```text
repeatable software production
        +
agent parallelism
        +
automated quality control
        +
human judgement
        +
experimental learning
```

The resulting system is valuable in two ways.

First, the factory-like development process helps build the semantic review capability efficiently and reproducibly.

Second, if the research succeeds, the semantic review capability itself becomes reusable factory machinery: a component that can inspect agent-generated changes, produce evidence-backed findings, trigger repair, and feed new knowledge back into the engineering process.

This creates a recursive but controlled improvement loop:

```text
factory builds reviewer
      ↓
reviewer improves factory output
      ↓
observations improve reviewer and factory
```

That is the most important strategic implication of the project.

---

# References

[1] OpenAI, “Introducing the Codex app,” Feb. 2, 2026. [Online]. Available: https://openai.com/index/introducing-the-codex-app/. [Accessed: Sep. 19, 2026].

[2] Microsoft, “Workflow concepts,” Microsoft Agent Framework Documentation, Aug. 25, 2026. [Online]. Available: https://learn.microsoft.com/en-us/agent-framework/concepts/workflows/. [Accessed: Sep. 19, 2026].

[3] Microsoft, “Workflow capabilities,” Microsoft Agent Framework Documentation, Aug. 25, 2026. [Online]. Available: https://learn.microsoft.com/en-us/agent-framework/workflows/. [Accessed: Sep. 19, 2026].

[4] Microsoft, “Durable Extension,” Microsoft Agent Framework Documentation, 2026. [Online]. Available: https://learn.microsoft.com/en-us/agent-framework/hosting/azure-functions. [Accessed: Sep. 19, 2026].

[5] Reuters, “AI coding agent startup Factory triples valuation to $5 billion in latest funding round,” Sep. 15, 2026. [Online]. Available: https://www.reuters.com/business/ai-coding-agent-startup-factory-triples-valuation-5-billion-latest-funding-round-2026-09-15/. [Accessed: Sep. 19, 2026].
