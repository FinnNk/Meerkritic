# Host and software-factory integration

Double-Entry Review remains usable without a harness. Hosts may consume its machine-readable
state and evidence to coordinate agents, display progress and study method overhead.
The host must not become a second source of truth for Git identities or DER evidence.

## Recommended integration surface

A host may index/reference:

- materiality assessment and classification;
- pair/round IDs;
- diary/semantic base/tip/tree identities;
- proposition / Review-Unit map;
- checkpoint verification records;
- review reports and review-round state;
- readiness stage and unmet next gate;
- evidence-event hashes and external evidence-store paths;
- integration records.

Prefer references/hashes to copying mutable prose into application state.

## Parallel agent work

DER permits many implementation agents, but paired-history integration remains single-owner:

```text
contributor/agent worktrees or branches
        ↓
one authorised history integrator
        ↓
canonical diary chronology
        ↓
frozen diary
        ↓
semantic reconstruction
```

Concurrent agents must not independently rewrite the canonical diary/semantic pair.

## Routing/model provenance

When a host has a model-routing subsystem, it may record optional provenance alongside
review/evidence records:

```yaml
inventory_version: ...
routing_policy_version: ...
routing_decision_id: ...
provider: ...
model_family: ...
model: ...
role: author | reviewer | analyst
```

These fields support audit and reviewer-independence analysis. They are not correctness
evidence and must not turn DER into a model benchmark.

## Reviewer-independence dimensions

Keep the existing coarse provenance label (`self-review`, `fresh-session`, `external`),
but a host may additionally record orthogonal dimensions:

- session: same / fresh / external / unknown;
- provider: same / different / human / unknown;
- model family: same / different / human / unknown;
- human identity/organisation: same / different / none / unknown.

Do not claim stronger independence than the recorded dimensions justify.

## Optional effort telemetry

For studying method overhead, a host may retain:

- input/output tokens;
- estimated/provider spend;
- turnaround/model/tool time;
- reconstruction time;
- review time;
- number of revision rounds.

This telemetry is observational only. It is not a readiness gate and does not determine
whether a review is valid.

## Architecture evidence

When the host can produce deterministic architecture snapshots/deltas, a material change
may attach `before`, `after` and `delta` artefact references to the proposition plan or
aggregate review. Architecture evidence supplements, but does not replace, code review,
repository contracts or checkpoint verification.

## Staged interaction

A host UI may represent feedback/decision state as `pending`, `answered`, `deferred`,
`reopened` or `superseded`. The durable DER record remains append-only: reopening or
superseding an earlier decision creates a new event/round disposition rather than editing
history in place.

## Optional design-skill integration

DER is self-contained. If a compatible design-review skill such as
`software-design-clarity` is installed, a host may invoke it for consequential design
changes and attach the resulting report as review evidence. The bundled DER design
guidance remains sufficient when no external skill exists.
