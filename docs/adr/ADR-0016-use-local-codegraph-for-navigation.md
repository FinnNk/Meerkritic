---
status: implemented
date: 2026-09-22
decision-makers: [Finn Newick]
---

# ADR-0016: Use a local CodeGraph index for code navigation

## Context and Problem Statement

As the application grows, locating callers, implementations and related tests
requires repeated source exploration. We want a reusable navigation aid while
preserving source verification, worktree isolation and existing architecture gates.
The owner authorised CodeGraph setup and an initial index on 22 September 2026.

## Decision Drivers

- Navigate Python symbols and relationships across application layers.
- Keep private research, credentials and duplicate checkouts out of the index.
- Refresh navigation as code changes without making generated graphs review artefacts.
- Distinguish a working tool from evidence that it improves development efficiency.

## Considered Options

- Local `colbymchenry/codegraph`, alongside source reads and text search.
- Graphify for a combined code-and-document knowledge graph.
- Continue with text search, direct reads and existing architecture snapshots only.

## Decision Outcome

Use the MIT-licensed `@colbymchenry/codegraph` package, pinned to 1.6.0, as an
optional developer tool. This identifies the particular CodeGraph project; other
projects with the same name were not selected. Finn Newick accepted the proposed
capability-based choice, not a claim of measured speed or accuracy improvement.

Keep a separate ignored index inside each application checkout. Install the tool
under `tools/codegraph`, independently of the Python application environment.
Disable its usage telemetry for project commands. Do not scan the parent workspace,
install global agent permissions, or copy vendor instructions over project policy.

For relationship questions, start with a focused CodeGraph query when a current
index is available, then verify consequential findings against source. Use direct
search for exact text and unsupported files. An absent edge is not proof of an
absent dependency, particularly for Python dispatch and template connections.

Tach, Import Linter, tests and typed architecture snapshots retain their existing
roles. The index neither replaces these checks nor becomes DER/research evidence.
Graphify remains an option for later cross-document exploration; it is not part
of this setup. Follow [code navigation](../development/code-navigation.md).

### Consequences

- Agents gain local symbol, caller and dependency queries with a reproducible tool pin.
- Every worktree needs installation/index refresh; indexes cannot be shared across branches.
- Static resolution can omit or misattribute relationships; source verification remains necessary.
- Local smoke checks establish operability only. Long-term preference remains subject to
  [EDR-0002: Evaluate code navigation assistance](../edr/0002-code-navigation-assistance.md).

### Confirmation

Implemented in the `chore/codegraph-navigation` candidate worktree on 22 September
2026. The pinned installation, initial index, known symbol and caller, exclusions,
and refresh after adding, renaming and deleting a disposable function passed the
[setup checks](../development/code-navigation.md#setup-verification). Generated
state is ignored. The canonical quality command passed all standard checks and
253 tests. This status records working local setup, not PR approval or demonstrated
efficiency. Revisit on stale results, missed important relations, Windows/worktree
friction or an unfavourable EDR result.

## Pros and Cons of the Options

| Option | Advantage | Trade-off / disposition |
| --- | --- | --- |
| CodeGraph | Focused symbol navigation, local index and incremental updates | Selected for trial; effectiveness on this application is unmeasured |
| Graphify | Links code with documents and rationale | Defer until that need recurs; semantic document extraction adds inference and refresh work |
| Existing approach | No new tooling; exact source remains directly accessible | Retain as fallback and comparator, with more manual relationship tracing |

## More Information

The EDR owns any future comparative measurements. Installation checks are ordinary
verification, not decision-bearing efficiency data. The owner's initial choice is
based on requirements and documented capabilities.

[1] C. McHenry, “CodeGraph,” GitHub. [Online]. Available:
https://github.com/colbymchenry/codegraph. [Accessed: Sep. 22, 2026].

[2] Graphify Labs, “Graphify,” GitHub. [Online]. Available:
https://github.com/Graphify-Labs/graphify. [Accessed: Sep. 22, 2026].
