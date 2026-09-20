Researchers can save decisions for several candidate rules, inspect the draft, then apply the whole batch. If a rule changed in the meantime, none of the batch is applied and the draft is retained. Selected discussion can also be sent to the model for advice; its response cannot edit rules or apply decisions.

The web application now shows saved architecture comparisons and warns when the code has changed since they were generated. This PR also adds MIT licensing and rewrites the technical guides around plain-English explanations, steps, expected results and recovery.

This is the final software batch for **VS2 (Annotation-to-Rule Discovery)**. Its prerequisite, PR #12, is merged; this PR targets `main`.

## Review sequence

| Commit | What it establishes |
| --- | --- |
| `186bff3` | Strengthen semantic boundary review and activate the final batch. |
| `89d5fca` | Explain the existing discovery and rule HTTP contracts. |
| `55001b6` | Save and apply decision batches, defer/reopen rule reviews and retain discussion against exact rule versions. |
| `ee351d3` | Send a fixed copy of selected context through the worker and return advisory guidance, with explicit handling of interrupted calls. |
| `eaeecaa` | Show architecture freshness and record the milestone review and remaining work. |
| `c86e14d` | Add the MIT licence in `LICENSE.md`, copyright 2026 Finn Newick, with matching package metadata and attribution. |
| `8cd1685` | Define writing guidance and connect it to agent instructions, review checklists and the PR template. |
| `db65516` | Backfill task and operations guides with prerequisites, steps and recovery. |
| `a2580a0` | Backfill developer references, terminology and navigation; retain historical verification separately. |

The original five commits are unchanged. The final two commits are documentation backfills. The documentation revision changes no application behaviour, tests or dependency versions.

## Validation

- Ruff formatting/lint, Import Linter, Tach and tests pass at every semantic checkpoint in a separate locked Windows/Python 3.12 environment. Each new documentation checkpoint and the frozen diary passed **172 tests**.
- Existing tests cover stale/concurrent drafts, complete rollback, corrupt evidence, invalid model output, interrupted completion and stale architecture. The original revision also passed real llama.cpp/Microsoft Agent Framework guidance and twelve loopback HTTP checks; this evidence remains tied to its unchanged code revision.
- Documentation checks resolved **264 local links/anchors across 59 Markdown files**, checked CLI examples and inspected representative rendered steps/tables. All **59 imported files** retain their recorded hashes.
- [Revision evidence and reproduction methods](https://github.com/FinnNk/Meerkritic/tree/347a6788f00bc46852dae36dba0c0d49c2580c12) include checkpoint logs, exact diary/semantic tree equivalence, scoped author review and the mapping to retained earlier evidence. This is self-review; no independent review or hosted CI execution is claimed.

## Decisions and remaining work

- [ADR-0012: Apply review intent in explicit batches](https://github.com/FinnNk/Meerkritic/blob/a2580a0785ab109c6014e404a949f60722282844/docs/adr/ADR-0012-apply-review-intent-in-explicit-batches.md) awaits owner acceptance. The [milestone architecture review](https://github.com/FinnNk/Meerkritic/blob/a2580a0785ab109c6014e404a949f60722282844/docs/slice-reviews/VS2-milestone-architecture-review.md) records the findings, fixes and earlier detection methods.
- Full research-slice closure still needs human-labelled data and the pre-registered comparison in **EDR-0001 (Choose an initial discovery grouping method)**, followed by the owner's adoption decision. Compatibility tests do not establish model or grouping quality.
- **VS3 (Rule-to-Historical-Replay)** remains drafted, not started. The owner reviews and merges; rebase merge preserves this semantic sequence.

Start with the [documentation index](https://github.com/FinnNk/Meerkritic/blob/a2580a0785ab109c6014e404a949f60722282844/docs/README.md) or the new [writing guide](https://github.com/FinnNk/Meerkritic/blob/a2580a0785ab109c6014e404a949f60722282844/docs/development/documentation-style.md).
