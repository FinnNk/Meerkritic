# Compare grouping methods

Use this command-line workflow to compare the two fixed methods in
[EDR-0001](../edr/0001-discovery-grouping-method.md). It creates a rating pack that
hides method names, then reports the agreed criteria from the human's ratings.
It does not choose an application default or replace the owner's decision.

**Research use requires registration.** Synthetic fixtures can exercise these
commands without registration; their outputs remain labelled `fixture`. Preparing
sources and interpretations is a separate [input-review workflow](study-preparation.md).

## Before running either method

- Finish source qualification and the 40 human-reviewed interpretations. Freeze
  exactly those annotation versions, with no excluded records, in a research
  selection. Keep the preparation history, source receipts and access terms.
- Record the exact code, locked environment, hardware, model loading time,
  normalisation configuration and embedding profile in the EDR. Record available
  tokens, local elapsed time and artefact sizes; unknown measurements stay unknown.
- Commit the completed plan before any research grouping. Include these lines,
  using actual values rather than the placeholders below:

  ```text
  - Selection: `<selection SHA-256>`
  - Embedding profile: `<canonical profile SHA-256>`
  ```

- In a second commit, set `Status: registered` and add:

  ```text
  - Registered plan: `<full completed-plan commit SHA>`
  ```

  Supply the **second commit's full SHA** as `--registration-commit` below.
  The command checks that the first commit is an ancestor and that tracked
  implementation/configuration still matches it. Run from that registered checkout.
- Hash the parsed profile as canonical JSON: sorted keys, UTF-8, no ASCII escaping,
  no whitespace separators and no non-finite numbers. This is the `digest` function
  in `semantic_reviewer.domain.study`, also used for study artefacts.
- Start the pinned local embedding server before timing the candidate. Retain its
  startup duration separately. Follow the [local inference guide](local-inference.md).

The registration check verifies recorded identities. It cannot authenticate a
curator, establish source permissions or detect undisclosed earlier experiments.
The researcher remains responsible for those facts. Existing exploratory controls
do not enforce the study protocol; do not use them to tune the research sample.

## Run and retain the two methods

These examples use PowerShell variables to make the identities visible. Replace
the paths and values once; keep the exact command transcript with the evidence.
All runtime and study evidence directories must remain outside Git worktrees.

```powershell
$data = 'D:/research/runtime'
$evidence = 'D:/research/comparison'
$registration = '<full registration commit SHA>'
$selection = '<frozen selection SHA-256>'
$baseline = '<baseline SHA-256 returned by the first command>'
```

| Step | Action | Retain |
| --- | --- | --- |
| Baseline | Run the lexical command below once. | Returned baseline digest; start/end times, elapsed execution and full partition are in the immutable record. |
| Embedding | Queue the exact selection with the existing `embed` command; run the configured worker once. | Embedding run ID, exact result/vector digests, model/routing provenance, usage and framework observation. |
| Candidate groups | After successful embedding, queue `cluster` with threshold `0.85` and minimum size `2`; run the worker once. | Clustering run ID, result and membership digests, execution times and failures. |
| Attempt record | Write the attempt JSON shown below, including failed executions. | Exact run IDs and any permitted retry diagnosis. |
| Assessment pack | Run `pack` below. | Comparison, rating-pack, blank rating-template and private mapping digests. |

```powershell
uv run --locked python tools/study_compare.py --data-root $data --evidence $evidence --registration-commit $registration baseline $selection
uv run --locked python tools/run.py --data-root $data embed $selection
# Run the worker with the frozen routing/profile/model paths; see the discovery guide.
uv run --locked python tools/run.py --data-root $data cluster '<embedding run ID>' --threshold 0.85 --minimum-size 2
```

The existing [discovery guide](discovery.md) covers worker configuration. Both
model execution and clustering retain the usual worker/event history. The study
command does not call a model or bypass Microsoft Agent Framework.

Save an attempt file outside Git, for example `D:/research/candidate-attempts.json`:

```json
[
  {"embedding_run": "<embedding run ID>", "cluster_run": "<clustering run ID>"}
]
```

- For a failed embedding, omit `cluster_run`; retain that failure rather than
  inventing a completed partition.
- At most one technical rerun is allowed **across both methods**, following a
  diagnosed implementation failure. A candidate retry is a second array entry
  with `retry_reason`. Reuse successful embeddings after a clustering failure;
  their execution time is counted once. A successful method cannot be rerun to
  obtain different groups.
- A baseline retry uses `baseline $selection --previous <failed baseline digest>
  --retry-reason '<diagnosis>'`. Its predecessor remains linked and its failed
  attempt remains in the new record. Never overwrite an earlier record.
- If a fix changes registered implementation, stop research execution and record
  the protocol deviation/amendment before continuing. Registration checks must
  not be disabled to make a changed method appear registered.
- Keep the sum of method execution attempts within 30 minutes per method after
  model loading. Queueing and human review are excluded. The report checks retained
  timestamps; it is not a process supervisor. Stop a run that reaches the cap and
  retain the interrupted failure. The existing embedding adapter also has a bounded
  request deadline. Do not discard failed attempts to reduce the reported time.

```powershell
uv run --locked python tools/study_compare.py --data-root $data --evidence $evidence --registration-commit $registration pack $baseline --attempts D:/research/candidate-attempts.json --profile config/models/nomic-embedding-fixture.json
```

The profile's filename reflects its compatibility origin, not approval of the
method. Research requires its exact content identity in the registered plan.
The pack command checks IDs, shared text, profile, fixed parameters and deterministic
membership replay against the saved selection and vector artefacts. Replay verifies
the existing result; it does not resample a model or search alternative parameters.

## Give the human reviewer only the masked pack

- Copy the files named by `pack_sha256` and `ratings_template_sha256` to a separate
  review directory. Each digest names `<digest>.json` under the evidence directory.
  Keep the comparison, baseline, run records and `private_mapping_sha256` separate
  until ratings are complete: these expose method identities.
- Edit a **copy** of the rating template. Supply the reviewer's name and, for every
  group, `coherent`, `not coherent` or `uncertain`, plus a short reason. Read every
  member, using the rubric included in the pack. Record suspected unmasking, or an
  empty string when none was noticed. Keep `pack_sha256` and `purpose` unchanged.
- The pack uses equal budgets: at most 12 groups per method, limited by the method
  with fewer groups. Identical membership sets appear once and share their rating.
  Fewer than eight groups per method is insufficient for the primary comparison;
  do not expand the budget or change parameters after seeing that outcome.
- Submit the completed file before opening the private mapping or comparative
  scores. The command freezes the submitted ratings before calculating the report.

```powershell
uv run --locked python tools/study_compare.py --data-root $data --evidence $evidence --registration-commit $registration analyse '<comparison SHA-256>' --ratings D:/research/completed-ratings.json
```

Missing ratings block this command. Malformed, duplicated or foreign ratings fail
validation. The report keeps uncertain judgements in the denominator, separates
outliers from failed inputs, lists unassessed groups and preserves attempt failures.
Its recommendation remains separate from the owner's recorded decision.

## Reproduce the ordering and report

| Part | Fixed procedure |
| --- | --- |
| Input text | Issue statement, newline, invariant or empty line, newline, categories joined by comma and space. Both methods use these exact strings. |
| Lexical groups | Case-folded ASCII `[a-z0-9]+` token sets; Jaccard similarity at least `1/4`; connected components of at least two. Empty token sets are outliers. |
| Representative | Greatest summed similarity within the group; ties follow frozen input order. Assessment includes all members. |
| Group selection | Sort each group's member IDs. Hash canonical JSON with keys `seed: 20260920`, `stage: "select"`, `members: <sorted IDs>`. Sort groups by that hash independently within each method; take the equal budget. |
| Presentation | Deduplicate selected membership sets, then sort using the same hash recipe with `stage: "present"`. Assign `G01`, `G02`, etc. Member order is sorted identity order. |
| Criteria | Use exact fractions for coherence, improvement and coverage thresholds. Rounded display percentages do not determine a pass. |

Retain the registration commits, original runtime artefacts, every study JSON file,
submitted ratings and command transcript. Replaying the report requires no model
call. Share only permitted inputs and outputs; hashes identify evidence but do not
grant redistribution rights. One rater and a small development sample cannot
establish population-wide superiority or inter-rater agreement.
