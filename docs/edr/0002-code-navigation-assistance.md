# EDR-0002: Evaluate code navigation assistance

- Status: draft
- Created: 2026-09-22
- Owner: Finn Newick
- Decision-maker(s): Finn Newick
- Registered on: pending
- Registered plan: pending; commit the completed protocol and then its full SHA before evaluation
- Evidence outcome: pending
- Implementation: local trial setup authorised; comparative evaluation not started
- Related records: [ADR-0016: Local code navigation](../adr/ADR-0016-use-local-codegraph-for-navigation.md)

## Registered plan

This is a prospective draft, not a registered evaluation. Complete task identities
and reference answers on a pinned checkout, commit this plan, then record that
commit and registration status before running the comparison.

### Decision and hypothesis

- **Choice:** whether to retain CodeGraph as the preferred first step for structural
  code questions or return to direct search as the default.
- **Comparator:** `rg` and direct source reads; both approaches retain source verification.
- **Hypothesis:** CodeGraph reduces median tool calls by at least 20% without
  reducing correctness or missing a consequential relationship.
- **Prior exposure:** the agent has implemented and inspected this application,
  read upstream feature/benchmark claims and recommended a trial. Installation
  queries and refresh checks are pilot exposure, excluded from evaluation tasks.

### Data and design

- **Unit:** one navigation task on a pinned Meerkritic commit; no claim about other repositories.
- **Sample:** six preselected tasks: find an entry point, trace a service-to-store
  call, identify a provider implementation, locate relevant tests, trace a
  template-to-handler connection, and assess callers of a changed interface.
  Exact prompts, expected source locations and consequential relationships remain
  to be committed before registration.
- **Independence:** use fresh task contexts for each arm, the same model/settings,
  no access to the other answer, and alternate arm order across the six tasks.
  Author familiarity limits generalisation; disclose it in results.
- **Adjudication:** owner reviews answers against the preregistered source references,
  marking unsupported claims, missed required locations and missed consequential edges.
- **Procedure:** one attempt per arm/task, maximum ten minutes each; keep failures
  and timeouts. Log installation/index time separately from task time.

### Measures and decision rule

| Measure | Definition | Criterion | Role |
| --- | --- | --- | --- |
| Correctness | Required source locations and relationships found per task | No reduction versus baseline; no consequential unsupported claim | Primary |
| Missed relationships | Required consequential edges omitted | Zero additional consequential misses | Guardrail |
| Tool calls | Calls used to reach the final supported answer | At least 20% lower paired median | Secondary |
| Elapsed time | Wall time per task, including verification | Report all pairs and median; no speed claim from index counts | Secondary |
| Refresh reliability | Known edits and branch switches visible after explicit sync | Correct checkout and no stale answer presented as current | Guardrail |

- **Rule:** retain preferred status if correctness and refresh guardrails pass and
  the tool-call threshold is met. Otherwise retain only as optional assistance or
  withdraw, with the owner's rationale. Treat ambiguous small-sample results as inconclusive.
- **Stopping:** twelve task runs, plus two fixed refresh scenarios; no extra tasks
  selected to improve the outcome. Stop for an isolation failure and retain evidence.
- **Analysis:** report every task, paired differences, medians, failures and missing
  data. No significance or broad performance claim from this small convenience sample.

### Method and reproduction plan

- Record exact Git commit, CodeGraph lockfile, Node/Python/OS versions, model and
  reasoning settings, prompts, task order and source reference answers.
- Save tool transcripts, timestamps, results and checksums outside worktrees under
  the local EDR-0002 evidence directory; publish shareable methods and summaries.
- Use only application source and synthetic refresh fixtures; exclude annotations,
  private data and credentials. Independent reproduction remains unperformed.
- Use the documented setup/sync/query commands; freeze a runnable task manifest and
  scoring instructions before registration. No automatic model runner exists yet.

## Amendments and deviations

None. Setup smoke checks are not registered evaluation runs.

## Runs and evidence inventory

No comparative runs recorded. Installation verification belongs in the navigation guide.

## Results and interpretation

Pending.

## Decision

Pending. The owner authorised installing the trial, not an empirical conclusion.

## History

| Date | Event | Author | Reason |
| --- | --- | --- | --- |
| 2026-09-22 | draft | Codex | Preserve the proposed comparison before any decision-bearing evaluation |
