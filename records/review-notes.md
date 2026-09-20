# Documentation revision: author review

This is a changes review from r1 to r2, with aggregate inspection. It is not a new
independent review of the original software. The original five semantic commits
are unchanged; their exact-identity review and checks are mapped in
`carry-forward.json`. The original public archive remains available at
`2894cbdbe22b5a84ba387e7c710115b591698388`. No approval transfers to the new head.

Frozen diary: `4e26b9e7bc4b762425586eab80a3aa9011d094f9`.
Semantic result: `a2580a0785ab109c6014e404a949f60722282844`.
The application source, executable tools, tests, dependency lock, imported source
and third-party skills are unchanged. Licence metadata changes the architecture
source fingerprint, but does not add a module or change an import contract.

## Proposition review

| Unit | Complete obligation and inspection |
| --- | --- |
| P6 `c86e14d` | Standard MIT permission/disclaimer, copyright 2026 Finn Newick, one root LICENSE.md, package metadata and source attribution agree. Imported notices remain intact. The diary preserves the initial redundant LICENSE file and the owner's correction; the semantic unit contains only the agreed result. GitHub recognition will be checked on the published revision. |
| P7 `8cd1685` | Writing guidance defines reader/purpose, plain language, procedures, current behaviour and review checks. Agent instructions, milestone review/template and a PR template point to it. It does not invent prose quotas, extra product requirements or new permission gates. |
| P8 `db65516` | Task guides lead with outcomes and prerequisites, then ordered actions, expected results and recovery. Read commands against CLI help and existing command definitions. Source annotations remain immediate and cannot reopen; staged rule decisions have separate lifecycle semantics. Model advice cannot mutate decisions. Setup distinguishes generation, embeddings, web and worker. Routing preview was executed without a model call. |
| P9 `a2580a0` | References retain exact contracts without delivery-history introductions. The old verification record was moved, not erased; a reusable verification guide replaces it. Checked links, glossary definitions, reserved configuration, EDR registration/decision separation, ADR lifecycle, current tests and architecture fingerprint instructions. No registration or adoption decision was manufactured. |

The first five units retain their original boundaries and SHA-bound evidence. The
licence and writing policy are separate complete units. The final two commits are
backfills as requested: operational tasks, then developer/reference navigation.
Their volume reflects distinct reader needs, not an arbitrary file-count rule.

## Accepted findings and disposition

| Problem | Applied remedy | Earlier detection in future changes |
| --- | --- | --- |
| Unnecessary milestone history in current instructions | Current task language; historical verification moved under slice reviews; historical records/imports preserved. | Check currency and purpose in the author/reviewer checklist. |
| Mixed tasks, reference detail and history | Task-led sections and links to reference/history. | Identify reader and first useful action before drafting. |
| Procedures hidden in prose | Numbered steps, independent bullets and action/result tables. | Review prerequisites, order, expected outcomes and recovery together. |
| Implementation jargon before meaning | Plain-English introductions, concrete verbs, glossary foundations and explained contracts. | Read from a technically aware newcomer's perspective. |
| Incomplete setup and examples | Explicit working directory/environment, worker/server prerequisites, exact flags and placeholder sources. | Check examples against current CLI and consumers; run safe examples where useful. |
| Failure descriptions without next action | Recovery tables preserve evidence, prevent automatic replay and distinguish stale intent from applied changes. | Challenge an ordinary failure alongside the successful path. |
| Repeated qualifications obscure the task | Keep relevant limits by the affected operation and link shared policy. | Review for proportion and duplication, without deleting material limits. |
| Weak navigation and insufficient structure | Task index, purpose-led headings, tables and foundational definitions. | Check links and inspect representative rendered documents. |
| Guidance not at agent/author/reviewer entry points | AGENTS, development guide, milestone method/template and PR template link the writing rules. | Apply the checklist during implementation, semantic review and aggregate review. |
| Dense PR description | User-visible behaviour first, concise ordered propositions, meaningful validation and linked evidence. | Rewrite around the final change, preserve owner amendments and separate evidence from approval. |

## Verification and limitations

- Each appended checkpoint and the frozen diary passed the canonical quality
  command in its own clean Windows/Python 3.12 checkout and locked environment:
  Ruff formatting/lint, Import Linter, Tach and 172 tests each.
- Parsed 59 maintained Markdown documents: 264 local links/anchors resolved and
  62 tables parsed. All 59 imported files match the source-manifest hashes.
- Rendered five representative pages with Markdown-it. Inspected the research
  interaction guide's browser layout and table/step structure and the README's
  browser accessibility structure. This is a sample review, not a claim of full
  visual coverage or an exact reproduction of GitHub's stylesheet.
- Safe CLI help and the documented synthetic routing preview passed. No private
  research data, licence key or model call was needed for this revision.
- Initial link inspection found the renamed commit-messages anchor; it was
  restored on the diary before the final freeze. A first helper run used the
  wrong working directory. The later external documentation check itself used
  `work` instead of `worker` and omitted preview arguments. These were checker
  errors, not defects in the documented commands; the failed record is retained
  as `docs-check-initial.json`, followed by the corrected passing run.
- Existing r1 real MAF/llama.cpp and loopback HTTP evidence remains bound to its
  original exact source revision. No new live workflow/model execution is claimed.
- No additional confirmed defect remains within this revision's scope. Author
  review is not independent review or owner acceptance. Human-labelled data,
  EDR pre-registration/comparison and adoption remain outstanding; no later slice
  begins as part of these editorial changes.

## Reproduction

Use `verify.py <label> <full-sha>` with fresh paths to create a checkpoint-owned
environment and run the required checks. `docs_check.py` uses the pinned project's
Markdown-it package. Local output paths are sanitised in the public export; adapt
them to the checkout. The archive's export index retains source/export hashes.
Use the canonical manifest/bundle to verify tree equality and exact identities.
