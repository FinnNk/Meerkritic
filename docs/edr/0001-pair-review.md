# Review engineering-concern pairs

Status: ready for human judgements. Scope fixed on 27 September 2026 before selecting this pack
or collecting pair judgements. Finn Newick authorised the next step after the
[exploratory diagnosis](0001-exploration.md). This is developmental data preparation;
EDR-0001 remains decided with no adoption. No new method is being evaluated or
adopted here, so this is not a second confirmatory experiment.

## Purpose and meanings

The existing 40 judgements describe whether interpretations faithfully capture
their sources. They do not label whether two interpretations express the same
reusable concern. This exercise creates those relationships and checks eligibility
without rewriting any original judgement.

For each item, answer **yes**, **no** or **uncertain** to:

> Does this interpretation identify a specific engineering concern or engineering
> investigation that could be useful in rule discovery?

- A question about a concrete possible defect can qualify even when the defect
  is unproven. A missing candidate rule does not automatically disqualify it.
- Praise, excitement or approval without a concern does not qualify. A faithful
  account of praise is still a valid original annotation.
- Use uncertain when the supplied interpretation/context cannot establish the
  concern. Do not infer a concern merely from a broad category name.
- Eligibility does not establish reviewer correctness, a verified defect, a valid
  general rule or suitability for deployment.

If both items are eligible, choose one relationship and give a brief reason:

| Answer | Meaning |
| --- | --- |
| Same specific concern | One specific engineering requirement, with compatible applicability conditions, explains both. Their desired actions are compatible instances of it |
| Merely related | They share a topic, mechanism or vocabulary but ask for materially different requirements/actions, or need distinct applicability conditions |
| Unrelated | No meaningful engineering-concern relationship is supported |
| Uncertain | There is not enough information to distinguish the alternatives |

If either item is **no**, record the relationship as **not applicable**, not as a
negative engineering-pair label. If neither is no but either is uncertain, record
the relationship as uncertain. Preserve the eligibility judgements independently.
Opposite surface actions may still serve the same requirement when conditions are
compatible; shared keywords or a vague rule such as “improve quality” are insufficient.

## Fixed developmental selection

Use the frozen 40-input selection
`f5bc84b772da601d3a068e42cdbb77799e887628773084aa9fe9b32ca1fabdd7`
and retained vectors/interpretations only. All sources and earlier interpretations
have been seen; the agent inspected ten top concern pairs per method during the
diagnosis. This pack is neither held out nor independently blinded.

Select **12 unique unordered pairs** in this order, excluding a pair once selected:

| Portion | Count | Selection rule |
| --- | ---: | --- |
| Semantic neighbours | 4 | Highest saved cosine similarity among existing `yes`/`yes` flags |
| Lexical neighbours | 3 | Highest exact token-set Jaccard similarity among remaining `yes`/`yes` pairs, using the registered full interpretation text |
| General comparison pairs | 2 | Seeded ordering of remaining `yes`/`yes` pairs, without using scores |
| Non-concern controls | 2 | One seeded `no`/`no` pair and one seeded `no`/`yes` pair |
| Eligibility ambiguity | 1 | One seeded `uncertain`/`yes` pair |

The existing flags define selection strata only, not expected new answers. No pair
is prelabelled same/related/unrelated. If a portion cannot be filled, stop and record
the shortfall before changing the rules. A record may appear in more than one pair;
the pairs are not independent observations.

- For each pair, sort annotation IDs lexically. Break score ties by that ordered
  tuple. Compute cosine from the saved unit vectors after verifying their bytes.
  Use ASCII `[a-z0-9]+` case-folded sets and exact fractions for Jaccard.
- For seeded ordering, hash canonical JSON with sorted keys, UTF-8, no whitespace:
  `{ "seed": 20260927, "stage": "select", "members": [sorted IDs] }`.
- After selection, rank all 12 pairs using the same recipe with `stage: "present"`.
  Assign P01–P12. Use a hash with `stage: "sides"`; an even first hexadecimal digit
  puts the first sorted ID on the left, otherwise reverse it.
- Keep scores, source-selection strata and original flags out of review cards.
  Show the exact issue statement, proposed invariant and applicability exclusions.
  Categories stay hidden. Supply links to the existing source assessment; record
  any additional context consulted in the new judgement.

## Collection and stopping rule

1. Present one pair at a time, with the plain-English rubric. The initial page is
   read-only; answer in chat rather than editing JSON or resaving source annotations.
2. Ask for the human's initial judgement before offering an interpretation. Record
   any agent assistance and suspected recognition/unmasking; do not call these
   independent labels. Clarify ambiguous replies instead of inferring an answer.
3. Retain the final human-confirmed eligibility labels, relationship and reason with
   pair/pack identity, timestamp, reviewer and consulted context. Use a new immutable
   response file for each save/correction, retaining any superseded response.
4. If a repeated item's eligibility appears inconsistent, ask the human to resolve
   it; do not silently copy or override the earlier answer. Leave it unresolved if
   the human is unsure.
5. Stop after these 12 pairs, or earlier if the owner pauses. Missing and uncertain
   judgements remain explicit. Do not replace awkward pairs or extend the budget.

Report counts by eligibility and relationship, unresolved conflicts, missingness
and assistance. A pair is a developmental positive only when both items are human-
eligible and the relationship is same specific concern. Merely related/unrelated
pairs with two eligible items are contrast examples; non-concern controls remain
a separate category. Report zero positives honestly. No model-quality score,
statistical independence or adoption decision follows from these purposive labels.

## Evidence and boundaries

Commit this protocol before generating the pack. Keep its exact method, input
identities, generated pack digest, reviewer-facing content and private selection
map so generation can be replayed. Raw text and responses remain outside Git under
the original sharing restrictions. Keep the read-only cards separate from private
maps and responses. No new model calls or holdout access are needed.

Materiality: routine research preparation using existing evidence; no application
schema, workflow or saved annotation is changed. A future model/grouping comparison
needs a separately completed prospective plan before execution. Further application
work remains a separate reviewed batch.

## Preparation record

Prepared on 27 September 2026 after scope commit
`9213bbd10c2320ff8f6fb42143d8f20a961e6aba`. The pack contains **12 pairs from 17
distinct inputs**, with every planned portion filled. No pair judgements have
been collected. Repeated inputs are deliberate; they do not provide independent
observations. The original 40 assessments and registered comparison are unchanged.

The [manifest](evidence/0001-pair-pack.json) records the pack, frozen inputs and
method hashes. The [generator](evidence/prepare_0001_pairs.py) uses the locked
DuckDB dependency and standard library; it makes no model calls. Raw cards, the
selection map and future responses stay outside Git at
`extras/research/edr-0001/development-pairs-20260927/`, relative to the workspace.

### Review a pair

1. Open [the first card](http://127.0.0.1:8011/P01.html) while the local card server
   is running. Widen the browser panel to compare the two items side by side;
   narrower panels show them one above the other.
2. Read the concern, candidate rule and limits for A and B. Open a source
   assessment only when needed, and mention any extra context you consult.
3. Reply in chat with each item's eligibility, their relationship and a brief
   reason. The agent asks about ambiguity before saving a confirmed answer.
4. Continue to the next numbered card. Do not save the original assessment again.

The cards are read-only and do not track progress. Only confirmed responses count
towards the running total. The agent retains each answer as a new file under
`responses/`, using the generated `response-template.json` fields. Each correction
names the SHA-256 of the response it supersedes; retain both files. Use UTC
timestamps, identify the reviewer, record assistance and recognition explicitly,
and hash the saved bytes for the response identity. Never infer an answer from
opening a page or from a selection flag.

### Reproduce the pack

Permitted access to the original study files is required: hashes alone cannot
recreate human-edited text or retained model vectors. From the application
repository in PowerShell, with the locked dependencies installed:

```powershell
uv run --locked python docs/edr/evidence/prepare_0001_pairs.py --study D:/codex/semantic-reviewer/extras/research/edr-0001 --output D:/codex/semantic-reviewer/extras/research/edr-0001/pair-pack-reproduction
uv run --locked python docs/edr/evidence/check_0001_pairs.py D:/codex/semantic-reviewer/extras/research/edr-0001/development-pairs-20260927 D:/codex/semantic-reviewer/extras/research/edr-0001/pair-pack-reproduction
```

- Use a new output directory; generation refuses to overwrite an existing pack.
- Run the comparison before collection, or compare only the immutable pack/card
  files afterwards: the verifier expects an empty response directory.
- Expect 12 pairs and identical bytes in the 16 generated files when using the
  recorded methods. Source-file hashes require the same file bytes, including
  line endings. Retain the exact source with the external pack for replay.
- Serve only `cards/` on loopback, never the parent directory containing the
  selection map and responses. For example, from a separate terminal:

```powershell
uv run --locked python -m http.server 8011 --bind 127.0.0.1 --directory D:/codex/semantic-reviewer/extras/research/edr-0001/development-pairs-20260927/cards
```

Local replay reproduced all 16 files byte for byte. Synthetic checks cover score
ties, selection uniqueness, input-order stability, missing control pools and HTML
escaping without exposing original flags/categories. This is local verification,
not independent reproduction or evidence of grouping quality. The
[validation record](evidence/0001-pair-validation.json) records the quality checks.
