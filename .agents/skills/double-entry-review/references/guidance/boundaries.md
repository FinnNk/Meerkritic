# Challenge authoring boundaries

Apply this component when preparing substantive changes or assessing their semantic boundaries. It adds an early authoring check to the core frozen-result boundary procedure; it does not permit redesign during reconstruction.

## Start provisionally, then inspect what accumulated

Before substantive implementation, sketch the propositions that might become independently assessable. Treat this as a hypothesis, not a commitment to manufacture those boundaries. Before freezing, compare the actual changes with that sketch: diagnostics, policy decisions or compatibility behaviour discovered along the way may now deserve their own units.

A PR answers an overall review question; a semantic commit establishes a checkpoint proposition; a module owns design knowledge. Their boundaries need not coincide. One feature, one file or one module can contain multiple independently assessable changes. Conversely, one guarantee can require changes across several modules.

For a substantial single-commit candidate, compare at least one plausible alternative series. State what each checkpoint would guarantee, which prerequisite contracts it uses, what evidence is available and what remains unavailable. Explain the concrete coupling that justifies combining changes, or the contract that makes splitting meaningful. "One feature", "documentation only", "the same file" and "fewer CI runs" are not coupling arguments. Qualification cost matters, but cannot by itself justify combining independent claims.

Use a fresh-context boundary challenge for a substantial ambiguous series when independent review is available: provide the change, candidate propositions and relevant contracts without asking the reviewer to endorse the author's preferred grouping. Record useful disagreement and its disposition. Do not add this ceremony to an obvious small edit or describe self-review as independent.

## Preserve complete checkpoints

Keep implementation, error paths, tests and documentation needed by a guarantee at the checkpoint where that guarantee first becomes available. An ordered dependency can be legitimate without being independently deployable or arbitrarily cherry-pickable. An intermediate state must honestly describe its limited contract, not borrow safety from a later commit.

Do not invent abstractions, split coherent design knowledge or perform speculative refactoring to achieve a preferred commit count. There is no universal line limit or minimum number of commits. When no honest split exists, retain the larger unit and give the reviewer an internal map. If the analysis discovers a root-cause correction or other content change, return it to the diary, verify and freeze again before reconstructing.

## Fictional contrasts

- An export change adds validated file publication and an independently useful report of export durations. Compare a complete publication guarantee followed by duration reporting with one combined unit; neither a shared command nor cheaper qualification proves inseparability. Logging required to satisfy the publication contract is different from optional operational reporting.
- A writer now promises that invalid output never replaces the last usable file. Validation, failure handling, publication behaviour and their tests belong with that first guarantee. "Write directly now; validate and preserve the old file later" is not a safe split of that promise.
- Correcting a misspelt documented option name can remain one small commit. Separating each paragraph or introducing a documentation abstraction would not create a more meaningful checkpoint.
