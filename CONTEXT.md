# Project Context Glossary

This file defines stable project vocabulary only. Keep definitions concise; put design rationale in ADRs or design documents.

## Embedding run
One explicit invocation over a frozen selection, retaining ordered annotation
identities, a pinned model profile and immutable vectors.

## Cluster run
Deterministic grouping over one pinned embedding artefact, with explicit algorithm
parameters, membership, representatives and outliers.

## Observation
A preserved source record from a review comment, PR description, issue, commit message or code comment, identified before model interpretation. An interpretation is a separate, evidence-linked output.

## Weak negative
An example where no relevant issue was observed, but correctness/non-violation has not been explicitly established.

## Verified negative
An example explicitly adjudicated as not violating the target rule.

## Rule
A versioned, inspectable statement describing an engineering condition, its applicability, violation definition, and exclusions.

## Detector
A concrete implementation used to evaluate a rule against code or repository context.

## Finding
A detector result asserting that a particular rule appears to be violated in a specific code context.

## Replay
Historical evaluation of a rule/detector against held-out code and review history.

## Repair attempt
An agent-generated candidate change intended to resolve a finding.

## Behavioural acceptance
Acceptance based on executable or otherwise independently verifiable evidence that the intended issue is resolved without unacceptable regression.

## Framework observation
An evidence-backed observation about Microsoft Agent Framework collected during normal programme use.

## Architecture snapshot
A typed representation of declared modules, dependency edges, contracts and static public interfaces at a specific commit/slice point. Checker results are separate evidence; the snapshot does not establish compliance.

## Architecture delta
The typed difference between two architecture snapshots.

## Model inventory
A versioned catalogue of models/providers/runtimes available to the routing subsystem. It describes availability and capabilities but does not choose a route.

## Task requirements
A model-independent statement of what a task needs, including reasoning, tools, context, risk and privacy constraints.

## Routing policy
A versioned set of rules that maps task requirements and an inventory onto preferred routes, fallbacks, review rules and constraints.

## Routing decision
The concrete provider/model selection made for one invocation under a specific policy and inventory version.

## Routing policy transition
An explicit mid-task switch from one routing policy/version to another.

## Agent handoff
A structured task-state package passed between models when a task changes route, avoiding a requirement to replay an entire transcript.

## Provider health
The current operational availability/degradation state of a provider/model endpoint.

## Model usage

Observed outcome, token counts, timings and spend for one routed invocation; unavailable measurements remain unknown.

## Price catalogue

A versioned set of API rates with an effective interval, retained to reproduce historical spend estimates.

## Context strategy
The policy-controlled approach used to construct model context, such as retrieval-first or direct large-context execution.

## Double-Entry Review (DER)
The paired-history review method used for material software PRs/changes in the factory.

## DER diary
The canonical chronological implementation history for a material change.

## DER semantic history
A reconstructed Git history of the frozen diary result, organised as complete review propositions. This is distinct from the project's semantic code-review system.

## DER pair
The diary and semantic histories for one material PR/change and its review rounds.

## Materiality assessment
A host-policy classification of a software change as routine, material or critical for deciding whether DER is required.

## Review proposition / Review-Unit
A bounded, complete claim established by one DER semantic checkpoint.

## DER readiness
The revision state tracked separately from slice status: locally prepared, published for qualification, hosted-qualified, owner-review-ready or integrated.

## History integrator
The single authorised role that owns integration into the canonical DER diary/semantic pair while contributors/agents may work concurrently in separate worktrees or branches.


## Artefact catalogue

Small immutable metadata identifying filesystem evidence by checksum, job, kind,
path, size and publication time; it does not contain the evidence body.

## Job log snapshot

An immutable filesystem projection of committed job lifecycle events, with a
mutable pointer to the latest snapshot; event history remains authoritative.

## Empirical Decision Record (EDR)

A pre-registered record of a significant evidence-dependent decision, its hypothesis, method, results, limitations and decision status.

## Pre-registration

An identified, committed plan recorded before decision-bearing data collection or analysis; subsequent amendments preserve the original plan and disclose evidence already seen.

## Architecture Decision Record (ADR)

A MADR-formatted record of a consequential architecture choice, its rationale and consequences; it may cite EDRs as supporting evidence.

## Annotation selection

An immutable snapshot of explicitly chosen annotation versions, source and effective
interpretation content, eligibility policy, exclusions and declared research or fixture
purpose. A curator attestation records a claim of human review, not authentication.

## Rule version

An immutable candidate definition with source selection, cluster, origin and parent
identity. A separate current pointer and revision counter fence operational writes.

## Rule evidence

A typed source annotation link with a named weak or verified claim for an exact
rule version. Inherited claims retain classification but require fresh verification.

## Rule promotion

A recorded human decision to retain a reviewed research candidate; it is not
validation, enforcement, deployment or demonstrated generalisation.

## Review draft

A saved coherent set of named human intentions against exact rule versions and
revisions. Saving does not apply decisions; explicit batch application is atomic.

## Review task

The pending, answered, deferred, reopened or superseded interaction state of one
rule version. Supersession identifies a replacement and retains historical answers.

