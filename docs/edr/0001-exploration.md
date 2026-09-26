# Diagnose the sparse grouping result

## Scope recorded before diagnostic analysis, 26 September 2026

Finn Newick agreed to no adoption from [EDR-0001](0001-discovery-grouping-method.md)
and a bounded exploratory investigation using the existing 40 judgements. Both
registered methods produced one four-item group. That result, the group membership
identities and the assisted input walkthrough are already known. This investigation
is **post-result exploration**, not a new blind comparison or retrospective tuning
of the registered study.

| Possible explanation | Diagnostic | What it can establish |
| --- | --- | --- |
| Data or implementation fault | Verify saved hashes, IDs, text alignment, finite vectors, dimensions and norms; independently reconstruct both registered partitions | Whether these specific storage/alignment/grouping faults explain the result |
| Too few pairs clear the thresholds | Describe all 780 pair similarities, nearest-neighbour scores and edge counts at the registered thresholds | How sparse the similarity graph is; similarity does not establish engineering coherence |
| Threshold changes cannot satisfy the original workload | Examine every distinct pair-score breakpoint, plus the no-edge state, using connected components of at least two | Maximum group count and whether eight groups with 60% coverage are structurally possible; no preferred threshold is selected |
| Lower thresholds create broad chains | Report group sizes and minimum within-group pair similarity on the fixed grids below | Whether transitive linking joins members below the edge threshold; this is not a human coherence rating |
| Sample/representation favours superficial matches | Count concern/no-concern inputs, category frequencies, repository distribution and text lengths; inspect registered groups and the ten highest-scoring concern-only pairs per method | Descriptive composition and explicitly agent-authored hypotheses, not independently verified pair labels |
| Category/invariant wording dominates lexical similarity | Repeat lexical summaries and breakpoint feasibility for issue-only and issue-plus-invariant text | Lexical sensitivity to those fields only; no claim about different embeddings without rerunning them |

Fixed display grids: cosine `0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95`;
Jaccard `0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50`. Use exact rational Jaccard
scores. Report nearest-rank quantiles (minimum, 25th, 50th, 75th, 90th, 95th,
maximum), with no fitted transformations. Score ties are added together when
checking component structure. Breakpoint inspection is a feasibility check, not
an optimisation objective or evidence that a passing count implies quality.

- Read only the frozen selection, saved interpretations, registered comparison
  and vectors. Retain all 40 inputs and every original result.
- Do not touch holdout data, rerun models, change the application or manufacture
  human ratings. Keep a separate diagnostic output directory outside Git.
- Use one reproducible diagnostic pass, retaining failures if repairs are needed.
  Stop after these checks and report findings; no adaptive parameter search.
- Keep raw texts and detailed pair identities outside Git under the original
  sharing restrictions. Commit the diagnostic method and aggregate findings.
- Any recommended further investigation remains separate from adoption. A later
  confirmatory study must handle this exposure and register its own inputs and
  criteria prospectively. More human labelling is not authorised by this scope.

Materiality: routine research diagnostics and documentation, with no application
behaviour change or new DER pair. This scope and the no-adoption decision are
committed before the new diagnostic outputs are examined.

## Results

The diagnostic pass completed on 26 September 2026. The registered result and
no-adoption decision remain unchanged. **Threshold adjustment alone cannot meet
the original eight-group requirement on these retained representations.** The
registered groups also contain no affirmative engineering concerns.

| Finding | How it was established | Interpretation and limit |
| --- | --- | --- |
| No identified storage/alignment/grouping fault | Exact hashes passed; 40 IDs and texts align across selection, comparison and vectors. All vectors have 768 finite values, unit norm and no duplicate rows. Independent graph traversal reproduces both registered partitions | These checks do not validate the semantic quality of the embeddings or prove absence of every implementation fault |
| Both registered groups contain zero affirmative concerns | Each group has four inputs, all marked other than `yes` for an actionable engineering concern. Inspection shows praise/approval/excitement descriptions | A faithful interpretation can be unsuitable for discovering an engineering rule. This is an agent diagnosis using existing flags/text, not a new human group-coherence rating |
| No threshold can yield eight groups with the retained methods | Every distinct pair-score breakpoint was inspected, with ties added together. Cosine reaches at most four non-singleton components; full-text Jaccard reaches at most five | Applies to these 40 inputs, scores and connected-components method. It is not a claim about all embedding or clustering methods |
| Relaxing thresholds creates chains and large groups | Cosine at 0.80 produces groups of 12 and three; some within-group similarities are about 0.67. At 0.75, one group contains 36 inputs | Connected components permit A–B and B–C links to join A and C without a strong direct relationship. Counts/coverage alone do not demonstrate coherence |
| Removing categories or invariant text does not resolve the group-count constraint | Issue-only lexical text reaches at most five groups; issue-plus-invariant text at most four, across all score breakpoints | This only tests lexical representations. It does not establish what re-embedding different text would do |
| The corpus is diverse, without pair/group ground truth | 34 `yes`, five `no`, one `uncertain`; 21 repositories; 65 category labels, 55 occurring once | Diversity and broad category overlap do not establish enough repeated specific concerns. The current input labels cannot measure retrieval/grouping correctness by themselves |

### Threshold behaviour

These are descriptive rows from the display grid fixed in the diagnostic scope,
not candidate defaults selected for adoption. Group sizes exclude singletons.

| Method | Threshold | Groups | Group sizes | Covered / 40 |
| --- | ---: | ---: | --- | ---: |
| Cosine | 0.90 | 1 | 4 | 4 |
| Cosine, registered | 0.85 | 1 | 4 | 4 |
| Cosine | 0.80 | 2 | 12, 3 | 15 |
| Cosine | 0.75 | 1 | 36 | 36 |
| Cosine | 0.70 | 1 | 39 | 39 |
| Jaccard, registered | 0.25 | 1 | 4 | 4 |
| Jaccard | 0.20 | 2 | 5, 2 | 7 |
| Jaccard | 0.15 | 4 | 20, 3, 2, 2 | 27 |
| Jaccard | 0.10 | 1 | 40 | 40 |

Across all 780 pairs, median cosine similarity is 0.698 and median nearest-neighbour
similarity is 0.779, below the registered 0.85 threshold. The corresponding lexical
medians are 0.085 and 0.158, below 0.25. Similarity scores are not probabilities of
matching concerns. Full grids, quantiles and breakpoint counts are retained in
the [aggregate summary](evidence/0001-exploration-summary.json).

### What the strongest concern pairs suggest

The agent inspected the ten highest-scoring pairs whose existing concern flags
were both `yes`, separately for each method. This was the prospectively scoped
inspection rule; it is not an exhaustive manual review or a human-labelled benchmark.

- The strongest cosine pair, 0.849886, concerns concise documentation references.
  It falls just below 0.85, but its two requests address different aspects of a
  reference. Proximity to the threshold is not sufficient reason to lower it.
- Another high cosine pair, 0.839771, links correcting indentation with avoiding
  unrelated indentation changes. Shared vocabulary/topic can hide materially
  different requested actions and applicability conditions.
- The strongest lexical concern pair, 0.204082, links documentation-directive
  indentation and relocating doctests. Common explanatory wording can contribute
  overlap without identifying the same reusable engineering concern.

These examples suggest testing whether a representation preserves the engineering
issue, desired action and relevant conditions while reducing generic review
wording. They do not prove that a revised representation would improve results.
The existing category labels are descriptive, not a controlled vocabulary or
verified rule taxonomy. Removing them alone did not solve the measured constraint.

## Recommended next step — not yet executed

Keep the no-adoption decision. Do not request another broad batch of source labels
or choose a threshold from this exploration.

1. Define **discovery eligibility** separately from whether an interpretation is
   faithful. Retain praise/non-concern records as negative controls; do not silently
   remove them from the completed study. Decide how `uncertain` inputs should be
   handled before any new method comparison.
2. Prepare a small pair-level challenge set from the already reviewed inputs:
   candidate instances of the same specific concern, shared-topic/different-action
   examples, and no-concern controls. The agent may propose pairs, but the owner
   must judge those relationships before they can serve as evaluation labels.
   The 40 existing judgements do not already supply those pair labels.
3. Use that explicitly developmental set to investigate representation and a
   grouping rule that limits chaining. Fix the precise alternatives and budget
   before running them. Do not claim that this exploratory work confirms quality.
4. Only then decide whether a new confirmatory study is worthwhile. Register its
   sampling, exposure controls, feasible workload and criteria before collection.
   Keep the existing repository holdouts unexamined unless a new plan authorises
   their use; do not recycle this explored sample as unseen confirmation data.

This follow-up needs agreement on its concrete scope before additional human
judgements, model calls or application changes. The bounded investigation here is
complete. VS3 has not been activated and no new grouping default is proposed.

## Reproduce and inspect

The [diagnostic method](evidence/diagnose_0001.py) uses the existing locked DuckDB
dependency and Python standard library. It reads immutable files, not the live
SQLite database. From the application repository in PowerShell:

```powershell
uv run --locked python docs/edr/evidence/diagnose_0001.py --study D:/codex/semantic-reviewer/extras/research/edr-0001 --output D:/codex/semantic-reviewer/extras/research/edr-0001/exploration-reproduction
```

- Obtain permitted access to the retained study directory; identities and hashes
  alone cannot reconstruct the human-edited text or model vectors.
- Use a new output directory. The command refuses to overwrite an earlier run.
- Read `summary.json` for aggregate findings. Keep `details.json` local: it contains
  the full breakpoint inspections, pair identities and text used for interpretation.
- Compare the measured fields with the committed summary. Environment/source
  commit fields may differ on a later checkout; use the recorded script hash to
  identify the exact method. No model inference is required for this replay.

| Evidence | Identity or location |
| --- | --- |
| Scope commit | `d1a1e39cd59ed17708476c40c6ecfa6c6287d420` |
| Successful original output | `extras/research/edr-0001/exploration-20260926-r2/`, relative to the workspace parent |
| Summary SHA-256 | `77e8b5a9fbe92c2ae142934c59cda296a4941e8ab0d8bdbac9aa2584c5fdd2f9` |
| Local details SHA-256 | `d12d33e6ea5fe33ada3e6c11b94e18293c920cb4d579ef687f09ec6b28a9a9ec` |
| Diagnostic script SHA-256 | `7eff6e71c4c8c80187847de283063cf95227cde8fc56146771fa802672d1c4d1` |

The first diagnostic helper failed before publishing outputs because it treated
the `yes`/`no`/`uncertain` concern field as a boolean. Its source and failure record
remain in `exploration-20260926/`. The corrected helper compares explicitly with
`yes` and reports all three labels. This repair did not change the diagnostic
scope, source judgements, registered runs or application code.

Synthetic method checks cover inclusive thresholds, tied edges, transitive chains,
empty lexical input and quantile calculation. Independent traversal then reproduces
the two retained registered partitions. The graph structure is exhaustively checked
over its score breakpoints; the semantic interpretation remains an agent-authored
exploratory assessment. Independent reproduction has not been demonstrated.

The [validation record](evidence/0001-exploration-validation.json) identifies the
checked source and retained log: all standard checks and 259 tests passed. The
registered plan, application implementation and existing tests remain unchanged.
