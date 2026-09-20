# Project glossary

Stable vocabulary only. Guides explain terms at the point of use; design rationale belongs in ADRs.

## Harness
The local web application used to browse source material, run workflows and review results.

## Normalisation
Turning a source comment and code excerpt into a structured proposed interpretation.

## Interpretation
A model's or reviewer's account of a concern, its supporting evidence and possible wider use.

## Annotation
A human Accept, Edit or Reject decision on a particular model result. An edit retains a corrected interpretation alongside the original.

## Fixture
Synthetic or permitted example data/configuration used to check software behaviour; it is not a human-labelled research sample.

## Frozen selection
A saved copy of explicitly chosen annotations and source material. Later decisions cannot change its inputs. See annotation selection for the recorded fields.

## Embedding
A numerical representation of text used to compare examples for similarity.

## Holdout
Material reserved from the current development/discovery work for later evaluation. Reading it is still data exposure and must be recorded where relevant.

## Immutable
Stored content that is never edited in place. Corrections create a new version and retain the old one.

## Atomic
A group of state changes that is saved entirely or not at all; a failed batch cannot leave some decisions applied.

## Idempotent retry
Repeating the same request identity and content returns the existing result without applying the operation again.

## Provenance
The retained source, versions, transformations and decisions that explain where a result came from.

## Embedding run
One requested conversion of selected text into vectors, retaining input order,
annotation identities and the exact model profile.

## Cluster run
Grouping one saved set of embedding vectors using recorded parameters. Results
identify members, representatives and ungrouped examples (outliers).

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
A typed representation of declared modules, dependency edges, contracts and static public interfaces at a specific code revision. Checker results are separate evidence; the snapshot does not establish compliance.

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
A software review method retaining both actual implementation chronology and a
reconstructed sequence of commits organised for review.

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
identity. A separate current-version record and counter let writes reject changes made since
the caller read the rule.

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

## Guidance batch

An immutable explicit submission of selected rule versions, discussion and human
instruction. An advisory response is distinct from an applied decision; interruption
can leave external completion unknown without automatic replay.

## Architecture projection

A saved view of before/after architecture records and their differences. A source
checksum detects code/configuration changes; the view does not certify quality or review readiness.
