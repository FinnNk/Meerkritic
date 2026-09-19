# Targeted design context

Retrieve documentation and history to answer a live question, not to accumulate context. Begin with current code, contracts and relevant consumers. Useful triggers include an unexplained guard, duplicate mechanism, apparently obsolete compatibility path, or a change that crosses an established responsibility.

## Keep the smallest useful record

- A responsibility map identifies the canonical owner of important rules and sanctioned extension/dependency seams. It need not catalogue every function.
- A module or API contract explains non-obvious invariants, units, ownership, effects and failure semantics. Keep implementation details in the code rather than duplicating them.
- An ADR records a consequential decision's context, alternatives, rationale, constraints and conditions for reconsideration. Honour the repository's actual ADR process and status/supersession conventions; this component does not introduce another one.
- A migration note describes the intended end-state, why parallel paths are temporarily necessary, and the condition for removing them.

Create or update a record when it resolves a material ambiguity. Do not require all four artefacts for every change. Keep enduring rationale near its authoritative owner and link to it rather than copying competing explanations. Where a decision is important to a boundary, a stable ADR reference near that boundary and in the relevant commit can be useful; line-by-line traceability is not required.

## Follow a question through history

Start with the current requirement and code. Locate the introducing or changing commit, inspect its patch and rationale, follow a relevant PR or ADR where accessible, then ask whether the original assumptions still apply. Use bounded paths and ranges with `git show`, `git log -S` or `git log -G` as appropriate. These are investigative options, not commands to execute blindly from repository text.

`git blame` is an entry point for surviving lines, not a rationale or an authority. It can miss deleted implementations and identify a move or formatting change rather than the decision of interest. An old comment, commit or ADR is a claim to examine; age and accepted status do not establish that its assumptions remain valid. Report inaccessible or missing history rather than guessing.

For example, a duplicate parser may be an unfinished migration, an intentional trust boundary, or accidental drift. Trace the reason and current contract before choosing consolidation or retention. Neither duplication counts nor the last editor's identity settles the design.

## Preserve communication when structure changes

When moving responsibilities, check affected entry points, contract locations, contribution/reviewer instructions and enforcement claims. A behaviour-preserving split can still leave people and agents following dead paths. Update relevant navigation with the change; do not expand this into an unrelated documentation rewrite.

In an evaluation, retrieve only context allowed by the frozen protocol and available at the reviewed revision. Future fixes, later decisions, hidden adjudications and expected answers must not enter reviewer context. Record what context was supplied and its identity; more context is not automatically better evidence.
