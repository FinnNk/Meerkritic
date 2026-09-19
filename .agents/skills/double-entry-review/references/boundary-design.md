# Plan the semantic series

## Purpose

Design the explanation of one frozen result. Do not redesign that result here.
The rules adapt Ousterhout's design/complexity principles; they are not his Git
prescriptions or evidence that the method improves review outcomes.

## Procedure

1. **Decide what matters.** State the whole-change objective, governing contracts,
   constraints and uncertain assumptions. Link requirements or decision evidence.
   Distinguish assertions by the author from established requirements.
2. **Name propositions.** For each candidate checkpoint state what complete change
   becomes assessable, why, prerequisites, guarantees, evidence, external context and
   limitations. Use the proposition template proportionately, before staging commits.
3. **Group shared obligations.** Keep changes together when correctness depends on
   the same design knowledge or mutual implementation-level understanding. A common
   directory or broad feature label is not sufficient. Keep necessary implementation,
   tests, schemas and documentation with the proposition they establish.
4. **Split at contracts.** A verified prerequisite contract may support separate review
   of its application. Independence does not require independent deployment or arbitrary
   cherry-picking. Do not invent reusable abstractions merely to create commit boundaries.
5. **Compare alternatives.** For nontrivial/ambiguous changes, sketch two materially
   different series. Compare local review burden, repeated reconstruction, evidence
   availability, boundary clarity and honest checkpoint contracts. Record the choice
   and an observation that would challenge it. No ceremony for an obvious edit.
6. **Order afterwards.** Introduce prerequisite contracts before their uses. Do not split
   into “models, adapters, tests, docs” by default. Do not defer required error/recovery
   behaviour to a later “hardening” patch while claiming it earlier.
7. **Challenge the framing.** What small condition would invalidate the main claim?
   What important obligation is missing? Purposeful reminders of an invariant are not
   the same as repeatedly reopening predecessor implementations.
8. **Check feasibility.** Every checkpoint needs available evidence and a clean-state
   verification plan. A large coherent unit may need an internal review map or real
   transitional boundaries; size alone does not dictate a split.

## Contrast

Bad: entities → repositories → controller → all tests, where no intermediate step
has an understandable contract. Potentially good: complete idempotency storage
contract → renewal-specific use → independently meaningful operational visibility.
Use the latter only if the actual frozen design supports it. Storage uniqueness alone
is not proof of exactly-once external payment effects.

A compatibility migration can legitimately establish “accept both formats”, then
“switch writers”, then “remove obsolete support”, with tests for each transitional
contract. It must not borrow correctness from a later state.

## Completion

An ordered proposition map, stable IDs where useful, dependencies, test-obligation
mapping, candidate outlines and material boundary rationale. Reviewers remain free
to challenge every claim. Proposed code/test changes go back to `work`/`revise` on
the diary, then require a new freeze and plan. Do not optimise a synthetic cohesion score.
