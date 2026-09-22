# PR descriptions and evidence summaries

Lead with the concrete problem and resulting behaviour. Include a before/after example when it clarifies the change. Use the project's template as a prompt, removing inapplicable sections. Scale the description to the review: a simple change may need only a short explanation and validation.

- Describe complete behaviours or obligations, rather than opaque task IDs or a list of files. If the project reviews semantic commits, include an ordered map when it helps a substantial series.
- State dependencies and decisions needed now. Expand project codes on first mention when they matter. Keep delivery history and raw logs in linked records.
- Explain what the validation establishes and its limits. Do not claim independent review, owner approval, empirical results or hosted checks that did not occur.
- When scope changes, rewrite around the final change. Read the current description before editing, preserve human amendments and read back the published result. If concurrent edits are detected, reconcile rather than overwrite. Editing prose does not authorise changing branches, reviews or repository settings.

## Compact validation summary

Use one short summary backed by retained evidence for the stated revision. For example, with real values substituted:

> **Standard checks:** Passed · revision `abc1234` · [Evidence]

This is a formatting example, not a claim or a link to publish unchanged. State the relevant environment once. Prefer readable text over a badge that hides its meaning behind colour or an external image service. Do not give each routine tool a table row just to list standard checks; a missing required check must still be conspicuous.

| Step | What to verify |
| --- | --- |
| Find the required checks | Read the project's current canonical check definition or declared validation contract. Do not assume a particular language, framework or toolset. |
| Match evidence to revision | Inspect the retained records and actual execution, including environment and run identity where relevant. A top-level success flag alone does not prove all required checks ran. |
| Choose an honest status | Use Passed only when all required checks ran and passed. Otherwise report Failed, Partial, Not run or Blocked, naming missing, skipped or failed required checks. Report skipped tests separately. |
| Summarise useful coverage | Use recorded test categories/counts where informative. Explain changed coverage by behaviour. Keep detailed commands and logs in the evidence record. |
| Add specific verification | Include relevant migrations, documentation checks, live workflows or other change-specific evidence; distinguish older integration evidence from current-head results. |
| Refresh after changes | Update affected evidence and the summary after a head change. Preserve human text outside generated sections and check the published result. |

Derive statuses and counts from evidence, not the previous PR. Link stable or immutable records where available. A documentation-only change often needs only the recorded test total and relevant document checks; do not invent unnecessary new gates.

Use a table only when it helps comparison. Suitable columns include:

- **Test category / Passed / Failed / Skipped**, for categories the suite actually defines.
- **Behaviour / Coverage change**, for meaningful new or changed coverage.
- **Behaviour / Added / Altered / Removed**, when reliable test-identity comparison is available and the comparison base is stated.

Do not infer unit/integration categories from test names or derive test counts from changed lines/files. Account for moves and renames when comparing identities. Counts do not establish coverage quality. Omit empty or repetitive tables; put consequential exceptions in short prose.

The summary points to existing evidence; it is not a second source of truth, a new evidence-storage design or a replacement for the project's checks. When evidence is missing, say so. Do not quietly turn “Not run” into “Passed” to make the description look complete.
