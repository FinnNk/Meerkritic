# Review propositions

Pair assessment-form / r1. Shared exact base:
796db0edc2032ed7ff0c518eecadd718b91c3e22 (assessment-clarity/r1 semantic tip).
Provisional diary freeze bd62a77d6b7a868533d76876d2d695a97018ab2b;
reconstruction must wait for clean diary qualification.

## P1 — Edit and verify assessments without authoring JSON

Web form adapter, route, templates, eight new behavioural tests, existing
button-label expectation, and assessment-form.md. Complete guarantee: labelled
fields represent the existing domain schema; list operations are unsaved;
validation errors preserve input; exact source evidence and immutable annotations
remain service-owned; saved results are readable. Legacy JSON submissions remain
compatible. Required canonical checks plus synthetic browser/error/narrow checks.
Prerequisite: the base's compatible unknown scope and failed-draft contracts.
History maps to 68e262b, c676a60, f2993a8 and 8f8b0c7.

## P2 — Align current guides and illustrations with field editing

Backfill annotation, assessment-fields, failed-draft and study-preparation guides,
documentation navigation and synthetic captures. Canonical checks and local
links/capture hashes. Depends on P1's labels and submission behaviour. Historical
ADRs, imported originals and earlier capture records remain historical evidence.
ADR-0014 still implemented; no change to its decision, meaning or storage contract.
No new ADR or EDR: user-prescribed presentation change, not empirical selection.
History maps to bd62a77.

Alternative considered: split server form protocol from switching the UI. It
would expose an unused protocol and need duplicate intermediate operation guides;
the guarantee under review spans rendering, field preservation and decoding.
Keeping these together lets each error/recovery obligation be assessed with its
actual caller. A separate generic form abstraction or per-layer commits would
scatter shared representation knowledge. P2 is separate under the explicit
documentation-backfill convention. One PR avoids unnecessary batch overhead;
stack on PR18 while its predecessor is unmerged.
