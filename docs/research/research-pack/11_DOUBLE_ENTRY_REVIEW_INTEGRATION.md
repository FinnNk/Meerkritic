# Double-Entry Review integration

**Status:** Project integration policy  
**DER skill:** `double-entry-review-core-0.3.0-alpha.2`  
**Normative DER method revision:** 7

## 1. Purpose and terminology

This project uses Double-Entry Review (DER) as the software-change preparation/review
method for **material PRs/changes inside vertical slices**.

Keep two meanings of *semantic* distinct:

```text
DER semantic history
    a curated Git history whose checkpoints express reviewer-comprehensible propositions.

Semantic review system
    the model/static/agent-assisted system this project is building to detect engineering issues.
```

The semantic-review system may contribute findings as DER review evidence. It is not DER
approval authority and DER remains usable without it.

## 2. Unit of application

A vertical slice is a programme/product increment. A DER pair is a review unit for one
material software PR/change. They do not have to coincide.

```text
Vertical Slice
  ├── routine change        → normal factory workflow
  ├── material PR/change    → DER pair A
  ├── routine change        → normal factory workflow
  └── critical PR/change    → DER pair B + stronger review gates
```

Do not create one DER pair merely because a slice exists, and do not combine independent
material changes solely to reduce DER overhead.

## 3. Materiality classes

### Routine

Ordinary factory workflow is sufficient.

Typical examples:

- typo/small documentation corrections;
- formatting-only changes;
- straightforward dependency refreshes without contract/behaviour implications;
- isolated copy/styling changes;
- tiny deterministic fixes with one clear cause and test;
- mechanical refactors strongly constrained by deterministic tooling;
- generated-file refreshes without design decisions.

### Material

DER is required.

### Critical

DER is required plus stronger surrounding review/evidence gates, normally including
independent review and explicit owner acceptance.

Critical is a factory risk class, not a different DER method.

## 4. Project hard triggers

Classify a change as at least `material` when it changes any of:

- public/API contract, persistent schema, event/protocol format or compatibility guarantee;
- architecture boundary or dependency direction;
- major abstraction, provider/runtime boundary or durable state owner;
- security, privacy, authentication, permissions or data-handling guarantee;
- concurrency, transaction, durability, recovery or state-machine semantics;
- meaning/identity/retention of experiment, review or provenance evidence;
- release/integration/build machinery that can affect delivered artefacts;
- broad behaviour requiring coordinated changes across modules;
- a durable/cross-cutting decision requiring an ADR;
- an explicit residual-risk or bounded mitigation rather than root-cause resolution.

For this project, changes to MAF/runtime boundaries, SQLite/DuckDB responsibilities,
routing-policy semantics, model handoff state, rule/evidence schemas, repair acceptance,
and architecture-contract semantics are therefore normally material.

## 5. Strong indicators

Without a hard trigger, DER is normally the default when **two or more** strong indicators
apply:

- multiple complete propositions are needed to explain the change;
- implementation chronology was exploratory or contains review-useful discoveries/dead ends;
- several modules must change together to establish one obligation;
- the reviewer needs non-obvious domain/history context;
- no single obvious deterministic validation establishes the change;
- agent/human implementation exercised meaningful design judgement among alternatives;
- temporary implementation states would mislead the final review narrative;
- feedback/revision rounds are likely;
- proposition-by-proposition review materially reduces cognitive load;
- failure has significant operational or maintenance consequences;
- the change is difficult to reverse safely.

The `two or more` threshold is an alpha/beta host-policy heuristic, not a numerical risk model.

## 6. Scope-growth reassessment

Assess materiality when a PR/change is created/planned and reassess whenever scope changes
materially.

A routine change that discovers, for example, a migration, state-machine change or new
architecture boundary becomes material.

Do not fabricate prior chronology. Preserve the actual work already performed and begin/convert
to DER using the real provenance available at that point.

## 7. Pre-1.0 policy

Until DER reaches a stable 1.0 release:

```text
clearly material     → DER mandatory
borderline           → DER encouraged/default-to-yes; host may waive with rationale
routine              → ordinary workflow
critical             → DER + stronger independent gates
```

The threshold may be broadened after 1.0 if observed review value justifies the overhead.

Collect incidental observations such as preparation/reconstruction/review time, number of
revision rounds, token/spend/turnaround where available, and reviewer judgement of whether DER
was useful. These are operational observations, not a DER evaluation programme and not readiness
gates.

## 8. Factory execution model

Multiple agents may implement concurrently in isolated worktrees or contributor branches, but
DER retains **one authorised history integrator** for the canonical paired history.

```text
parallel implementation agents
        ↓
contributor worktrees/branches
        ↓
one history integrator
        ↓
canonical diary chronology
        ↓
frozen diary
        ↓
proposition-led semantic reconstruction
```

Accepted implementation changes enter the diary in their true chronology. Never ask agents to
invent a clean chronology while implementing.

## 9. Reconstruction and evidence

For each material pair:

1. preserve diary-first chronology;
2. verify and freeze the diary result;
3. plan semantic checkpoints around bounded, complete propositions;
4. reconstruct the semantic history from the frozen result;
5. verify every semantic checkpoint in its own source/test/lock/environment context;
6. verify final tracked-tree equivalence between the frozen pair;
7. review propositions and aggregate interactions;
8. use versioned review rounds for feedback/revision;
9. keep DER evidence outside application worktrees.

Final-tree equality proves snapshot identity, not correctness, complete provenance or approval.

## 10. Readiness versus slice status

DER readiness and factory slice status answer different questions.

Factory slice states:

```text
DRAFT → READY → ACTIVE → COMPLETE
```

DER revision readiness:

```text
locally prepared
published for qualification
hosted-qualified
owner-review-ready
integrated
```

The harness should show both without conflating them.

A slice may be `ACTIVE` while a material change is only locally prepared. A slice should not be
`COMPLETE` while required material changes have unresolved DER gates relevant to the slice's
definition of done.

## 11. Harness integration

The harness should reference/index DER state rather than duplicate DER's evidence store as a
second source of truth.

Useful entities/references:

```text
MaterialityAssessment
ChangePair
ReviewRound
ReviewUnit / Proposition
CheckpointEvidence
RevisionReadiness
DER evidence path/hash
```

Display:

- materiality classification and rationale;
- current pair/round;
- diary/semantic identities;
- current readiness stage;
- proposition map;
- verification/review status;
- unmet next gate.

## 12. Model-routing and reviewer provenance

Where available, record DER author/reviewer provenance using the routing subsystem:

- model inventory version;
- routing policy version;
- routing decision ID;
- provider;
- model family/model;
- role.

Keep DER's coarse independence category and optionally record orthogonal dimensions:

```text
session independence
provider independence
model-family independence
human independence
```

This improves provenance but does not turn DER into a model benchmark.

## 13. Semantic reviewer as DER evidence

When sufficiently mature, the semantic review system may run against a DER semantic checkpoint
or aggregate candidate and contribute structured findings such as:

```text
rule finding
architecture/design concern
test-evidence concern
hypothesis
```

The reviewer is an evidence source only. It must not:

- approve its own generated change;
- replace checkpoint verification;
- grant owner/platform approval;
- alter DER authority rules.

## 14. Architecture and design evidence

For material structural changes, attach architecture snapshot/delta references when available.
They supplement DER boundary and aggregate review.

Use the independent `software-design-clarity` skill for material design review when installed;
DER's own bundled design guidance remains sufficient and the external skill is not a readiness
prerequisite.

## 15. Observational overhead

The harness may correlate DER work with existing model/factory telemetry:

- preparation/reconstruction/review elapsed time;
- input/output tokens;
- estimated/provider spend;
- tool/test time;
- revision-round count.

Keep this secondary and non-distracting. It is intended to support later decisions about whether
the materiality threshold should broaden, not to create a DER benchmark programme.
