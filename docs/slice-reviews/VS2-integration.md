# VS2 software integration

Verified on 20 September 2026. The owner approved and merged
[PR #13](https://github.com/FinnNk/Meerkritic/pull/13). All planned application
batches are integrated. VS2 remains ACTIVE while its empirical decision is open.

| Item | Verified result |
| --- | --- |
| Reviewed head | `a2580a0785ab109c6014e404a949f60722282844` |
| Integrated head | `f7aa4e05411da9d804f3624abe57033544fb1073` |
| Merge mapping | Nine ordered semantic commits retain identical tracked trees after rebase merge. |
| Integrated checks | Ruff formatting/lint, Import Linter, Tach and 172 tests passed in a clean, locked Windows/Python 3.12 checkout. |
| ADR-0012 | Explicitly accepted by Finn Newick before merge; now implemented with integrated confirmation. |
| Licence | GitHub recognises the root `LICENSE.md` as MIT after merge. |
| Remaining gate | Human-reviewed inputs, registered EDR comparison, recorded results and owner decision. |

The [integration evidence](https://github.com/FinnNk/Meerkritic/tree/3a4f952818ee429f64f406fc7db3df369a087dca/integration/pr13)
contains the GitHub approval/merge record, full ordered tree mapping, quality log,
checkpoint identity, dependency versions and reproduction script. Its export index
records source and sanitised hashes. Local machine paths use placeholders.

Earlier candidate checks and live MAF/llama.cpp evidence remain bound to their
original revisions in the retained DER archive. Tree equality does not relabel them
as newly executed mainline checks; the integrated canonical run is separate.
The owner's architectural acceptance is also retained in the canonical ledger.

The [slice review](VS2-review.md) and [milestone review](VS2-milestone-architecture-review.md)
retain the delivered behaviour, findings and limitations. This record closes the
software integration gate, not the empirical study or the whole slice. No later
slice has been activated.

## Study-preparation documentation integration

The owner approved and merged [PR #14](https://github.com/FinnNk/Meerkritic/pull/14)
on 20 September 2026. Reviewed head `fb5745475e7dd7d0cf5a93e329b3cd0c34910c72`
maps to integrated head `cd0a4d8c9a254e3027513274b39ce3f65cf227d2`; all seven
ordered reviewed trees are preserved. The integrated locked Windows baseline passes
all standard checks and 172 tests. Its ordered mapping and baseline evidence are
retained with DER `vs2-study-tools/r1`, outside application worktrees.

The owner's later explicit agreement to EDR-0001's proposed workload and criteria
is recorded in that EDR. It is separate from PR acceptance and from registration.

## Input-preparation tooling integration

The owner approved and merged [PR #15](https://github.com/FinnNk/Meerkritic/pull/15)
on 20 September 2026. Reviewed head `1d56877f0ccc434344a0e67b42859f4744524767`
maps to integrated head `f5b23e44e4f13237a9f505f2f8182e0561813efe`; all four
ordered reviewed trees match. The integrated locked Windows/Python 3.12 baseline
passes every standard check and 181 tests. The exact mapping and clean-checkout
record are retained with DER `vs2-comparison/r1`, outside application worktrees.

This integrates the deterministic input order and attempt ledger. It does not
attest source authenticity, supply human reviews or register the comparison.

## Comparison tooling integration

The owner approved and merged [PR #16](https://github.com/FinnNk/Meerkritic/pull/16)
on 20 September 2026. Reviewed head `2adeb88d3bbcf1af2ee8b5c498c7a32cbe1c100c`
maps to integrated head `e7726500930e79f0ba69becae5d12b77edbb5dea`; all five
ordered reviewed trees match. Isolated locked Windows/Python 3.12 checks pass
with 215 tests. Mapping and baseline records live in DER `vs2-draft-repair/r1`.

This integrates the comparison software, not a research result. The owner also
agreed a prospective human-correction amendment, recorded in EDR-0001. Its
implementation retains the single normalisation pass; human input judgements,
selection freeze, registration, group ratings and empirical decision remain open.
