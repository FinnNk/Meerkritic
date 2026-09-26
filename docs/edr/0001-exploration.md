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

Pending the bounded diagnostic pass.
