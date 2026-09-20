# Milestone architecture and guidance review

After each completed vertical slice or other explicitly agreed milestone, assess
the accumulated system before starting the next milestone. Review all applicable
project guidance, not only the area that prompted the review. A milestone review
complements semantic-commit and aggregate PR reviews; it does not replace them.

## Scope and authority

Resolve the integrated commit and tree, inspect local changes, and distinguish
the current implementation from unmerged plans and imported research snapshots.
Read project instructions, active ADRs/EDRs, current backlog, development guidance
and the relevant specification using the research index's authority order. Future
slice requirements remain deferred unless explicitly activated.

Start with read-only inspection and report findings before changing code. An
existing owner instruction to address findings autonomously authorises the bounded
follow-up; otherwise obtain that instruction after presenting the findings. Owner
approval, DER readiness, integration and milestone completion remain separate.

## What to assess and how

| Area | Inspection and evidence |
| --- | --- |
| Scope and architecture | Trace representative paths through web, application, domain, routing, adapters and worker. Compare prescribed boundaries and scope with actual responsibilities and dependencies. |
| Complexity and module depth | Describe hidden complexity and caller obligations. Inspect unchanged consumers, duplicated rules, special cases, configuration and pass-through layers. Compare a proportionate simpler alternative. Do not use file size as a verdict. |
| States and failures | Identify each material invariant and its canonical owner. Challenge invalid combinations, empty/missing values, retries, partial failure, restart and concurrency where relevant. Use focused probes or existing tests; distinguish demonstrated defects from hypotheses. |
| Interfaces and documentation | Compare declared interfaces, implementations and real callers. Check undeclared operations, payload conventions, configuration-dependent requirements, return meaning, bounds, side effects and failures. A caller must not need the implementation to discover its contract. |
| Runtime and routing | Check framework isolation, model controls, policy precedence, locality, context limits, failure classification and telemetry. Model-specific prompt controls belong behind an explicit runtime boundary, just as SDK types and concrete model selection do. |
| Data, privacy and provenance | Trace source identity, evidence publication, version retention, atomic state/events, external artefact ownership and untrusted input handling. Check reproduction claims against actual commands, versions, hashes and access limits. |
| Human interaction and research | Check the active slice's action/state boundary. Keep model output, functional-test decisions and human research judgements distinct. Check EDR applicability, registration chronology, results and limitations without requiring EDRs for incidental measurements. |
| Quality and observability | Inspect canonical checks and meaningful negative/failure tests. Bind results to exact source, lock and environment; label unrun checks. Compare typed architecture before/after/delta, including public contracts. Static dependency legality is not a design verdict. |
| Delivery and knowledge | Review semantic propositions, materiality/DER evidence, authority and integration records. Reconcile affected maintained guides, glossary, backlog, ADR/EDR indexes and status claims with delivered behaviour. Preserve imported originals and historical evidence. |

For each applicable area, record a short conclusion and a concrete source or
verification reference, or an explicit evidence gap. An area may be not applicable
with a reason. Do not convert missing evidence into a pass or impose findings quotas.

## Review method and result

1. Establish the revision, scope, applicable obligations and evidence limits.
2. Inspect the system and relevant consumers using software-design-clarity. Use
   typed architecture data to locate questions, not to infer design quality.
3. Challenge important promises: what plausible input, caller or configuration
   would expose a gap between the public contract and the implementation? Use
   risk-proportionate counterexamples, without constructing speculative systems.
4. Inspect or run appropriate verification in an isolated context. Record the
   exact commands and actual results; do not relabel candidate evidence as a new
   mainline run. Obtain authority before touching a user's live research state.
5. Report strengths, prioritised findings, governing obligations, consequences,
   suggested validation and proportionate remedies. Distinguish defects, design
   concerns, evidence gaps, preferences and accepted limitations.
6. Record dispositions: fixed with evidence, accepted with rationale, or deferred
   with owner and a concrete revisit trigger. Recheck the aggregate after fixes.
   Material unresolved issues require an explicit disposition before proceeding.

Use the [milestone review template](milestone-review-template.md). Store the
maintained report with the slice review (or another named milestone report under
`docs/architecture/`). Link canonical DER evidence rather than duplicating it.
Produce this document for every future milestone review, including reviews with
no findings. For each finding, preserve a trace from discovery to resolution and
to the earlier development/review practice intended to catch the general problem.
Use the VS1 review as an example, not a required number or catalogue of findings.
Update future work and relevant ADRs/EDRs when warranted. Do not invent empirical
claims from review judgement or rewrite a frozen EDR plan after seeing results.

## Required finding record

For each finding record:

- **Observed issue and consequence:** concrete example, affected revision and
  governing principle or contract; distinguish a defect from a design concern.
- **How it was found:** the path/interface/document comparison, question or probe
  that exposed it, with source/evidence references. Distinguish initial discovery
  from regression tests added during the fix; do not invent missing chronology.
- **How it was addressed:** the change and its invariant owner, or an explicit
  accepted/deferred disposition; link implementation and validation evidence.
- **General failure pattern:** describe the class of problem beyond the particular
  function, model, field name or document in which it appeared.
- **Earlier detection and response:** identify the pre-implementation, semantic
  checkpoint or aggregate PR check, the responsible author/reviewer, a concrete
  challenge, and the proportionate response if it exposes the same pattern.
- **Confirmation and limits:** say what establishes the fix, what remains uncertain
  and any revisit trigger. Intended prevention is not proof of effectiveness.

Keep these details in the milestone's maintained review document, with a short
disposition table for navigation. A table alone is insufficient when it omits the
discovery method or the earlier detection/response mechanism. Link raw evidence
to its canonical store. Keep original finding identifiers stable and distinguish
additional improvements discovered during the follow-up from the original findings.

## Build and PR checkpoints

Before implementing a significant abstraction, record the invariant, its owner,
the proposed interface, the complexity hidden and what callers should not know.
Reuse the batch's design notes; no separate document per interface is required.

At each relevant semantic checkpoint, examine the actual interface, implementation
and consumers together. Record a concrete contract challenge and evidence of the
result, including any limitation. Keep necessary code, failure handling, tests and
operational documentation together. Guidance changes and existing-code comment
backfills retain their separate semantic commits.

At aggregate review, revisit interactions across the series and reconcile affected
maintained documentation, including unchanged descriptions made stale by the work.
Apply the [documentation checklist](documentation-style.md#author-and-reviewer-checks):
read guides as someone new to the project, follow task steps in a disposable runtime
where useful, and compare terminology, commands, UI labels and current-behaviour claims.
Report readability and navigation problems as well as factual omissions. Check PR
descriptions for the same reader-facing issues.
The canonical quality command remains required. These judgement checks strengthen
its surrounding workflow without adding blanket type/docstring lint, arbitrary
metrics or mandatory new tests for unchanged low-risk behaviour.

Use lessons from prior milestone findings at these earlier checkpoints. Authors
apply the relevant generalised challenge while designing/building the change;
reviewers check the response and evidence before accepting the proposition or PR.
For material invariants, name the actual entry paths (for example immediate and
batched writes) and the boundary each relies on. A read-path test does not establish
write integrity. Challenge runtime-port values independently of their usual concrete
adapter, including constructed objects that can bypass normal parsing. When a
negative control fails during setup, correct the fixture and preserve the failed
attempt before claiming evidence of the intended property.
Do not postpone a known applicable check until the next milestone review. Later
reviews assess whether the practice was actually applied and record recurrences;
they must not claim that adding a checklist guarantees prevention.
