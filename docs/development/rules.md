# Inspect and challenge candidate rules

This checkpoint exposes immutable registry publication through RuleService.propose
and human inspection in **Rule registry**. A caller supplies a verified cluster,
definition and origin; tests use explicit synthetic human-origin proposals.
The next proposition adds routed MAF synthesis, queue submission and CLI access.

## Evidence and research decisions

Attach positive, counterexample, false-positive, false-negative or unresolved
evidence from the same frozen selection. Repository holdouts remain excluded.
Rejected interpretations may be weak evidence; they are not verified negatives.
Choose verified only when explicitly attesting that claim for this rule version,
with your name and rationale. A source match establishes provenance, not validity.

Promote or reject a current candidate with a rationale. Promotion means a reviewed
research candidate; it does not validate, enforce or deploy the rule. Concurrent
changes produce a conflict and preserve submitted values for correction. Decision
retries with the same identity and content return the original decision.

Revise to create an immutable child version. Prior decisions remain historical.
Every evidence classification carries forward with a parent link and weak status;
verification must be reassessed against the new definition. A revision cannot
silently discard counterexamples. Each version is bounded at 1,000 links, and a
revision exceeding that limit fails without changing the current version.

