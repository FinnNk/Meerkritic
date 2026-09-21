# Assessment form — material change

Assessed 2026-09-21 by Codex /root, sole history integrator. DER alpha.2,
method 7. Pair assessment-form, round r1. Base: PR18 at
796db0edc2032ed7ff0c518eecadd718b91c3e22. PR17 and PR18 remain open.

Classification: material. Hard trigger: browser submission contract changes
from a raw JSON editor to labelled fields. Strong indicators: coordinated form
rendering/submission/validation and error retention; more than one meaningful
validation path; design judgement about representation and failed model drafts.
No persistence, judgement meaning, model prompt or study-selection changes.
Reassess if scope changes. Policy: research-pack/11_DOUBLE_ENTRY_REVIEW_INTEGRATION.md.

The owner explicitly requests this UX correction. Existing autonomous batch and
stacked PR authorisation applies. The owner alone saves research judgements and
merges PRs. Development and synthetic browser tests use separate worktrees and
runtime data. Do not refresh the owner's unsaved tab or submit their assessment.

Initial propositions: (1) complete field-based assessment editing, compatible old
form submissions, recoverable errors, tests and form reference; (2) backfill guides
and synthetic screenshots. No new general policy or ADR is initially required:
this applies the existing assessment contract and information-hiding principles.

Design clarity: a web-owned form adapter hides browser field encoding, optional
values, list rows and display of incomplete failed drafts. The application service
retains all decision eligibility, schema, exact grounding and persistence rules.
Callers supply HTTP form values and need not construct JSON. No generic form
framework, new domain model, dependency or durable store is justified. Browser
editing is reversible; the explicitly labelled save action remains terminal.

Required checks: canonical tools/check.py in each checkpoint's own Windows,
Python3.12 locked environment; synthetic browser editing and validation recovery;
typed architecture before/after/delta; exact frozen diary/semantic trees;
author self-review of each proposition and aggregate. No independent review claim.

Evidence lives in extras/der-evidence outside all application worktrees. Diary
change/assessment-form-diary; semantic feat/assessment-form. Source material and
private research records stay outside the public evidence archive.
