VS2 (Annotation-to-Rule Discovery) can now freeze explicitly chosen annotation versions and inspect them in the harness. Accept uses the original interpretation; Edit uses its verified replacement. Snapshots retain source and result provenance, uncertainty and labelled exclusions, so later annotations cannot silently change discovery inputs.

This PR delivers A1 (immutable annotation selection and eligibility) from the reconciled VS2 plan. Freezing runs through the CLI; the harness shows annotation IDs and browses verified snapshots. Creation is idempotent, metadata and events commit atomically, and corrupt or missing evidence fails closed. Bodies stay outside SQLite.

VS1 (Data-to-Annotation) did not record authenticated reviewers. Research selections therefore require a named curator's explicit human-review attestation; fixture inputs remain labelled. The attestation is a claim, not independent verification. Reject is not a verified negative, and selected holdouts remain excluded. [ADR-0009 (Freeze explicit annotation selections before discovery)](https://github.com/FinnNk/Meerkritic/blob/4abbcdd20f0dfe339e53f8332d3b509b07753341/docs/adr/ADR-0009-freeze-explicit-annotation-selections.md) is proposed for owner acceptance.

Review the semantic commits in order:

| Commit | Complete proposition | Canonical tests |
| --- | --- | --- |
| `4c45515` | Reconcile integrated VS1, activate A1 and retain later empirical/model gates | 102 |
| `6e2cd57` | Freeze exact annotation versions: eligibility, provenance, durable publication, CLI and failure handling | 113 |
| `4abbcdd` | Browse verified snapshots, expose annotation IDs and handle unavailable evidence | 115 |
| `0683769` | Give project references their code and title on first mention in PR descriptions and commit comments | 115 |

Every checkpoint and the frozen diary passed Ruff format/check, Import Linter, Tach and tests in its own clean, locked Windows/Python 3.12 environment. Tests challenge effective edits, duplicate versions, corrupt source/results/snapshots, concurrent retries, failed publication/events, restart, HTML escaping and HTTP bounds. Typed architecture before/after/delta is recorded; dependency contracts and ignores are unchanged.

DER `vs2-inputs/r2` preserves actual chronology, adverse checks, full author self-review and exact final tracked-tree equality. [The immutable evidence packet](https://github.com/FinnNk/Meerkritic/tree/5e7987c8b64257342ea407a887471c994feca35b) contains the bundle, checkpoint logs, proposition map and reproduction method. This is not independent review or an empirical quality result.

A1 is separated from embedding/grouping because input integrity can be delivered before model preflight and a bounded human-reviewed corpus are ready. A2 (embedding adapter and worker execution) and A3 (worker clustering over pinned embedding artefacts) remain the next substantive batch. EDR-0001 (Choose an initial discovery grouping method) is still draft, with no decision-bearing run or adoption decision. No live research annotations were created or changed. VS2 remains active, not complete.

