A retained draft that fails schema or source-evidence validation can now be corrected or rejected in the harness. The page shows the original source, preserves an invalid edit for correction, and saves a valid human interpretation separately. **The original job stays failed and its output remains unchanged.** No additional model pass is introduced.

This implements the agreed EDR-0001 preparation amendment. Successful drafts still offer Accept/Edit/Reject; failed drafts offer Edit/Reject only. Provider or missing-output failures remain for inspection. Corrected drafts can enter saved selections; rejected failures remain explicit exclusions. Existing selection files stay readable.

![Synthetic failed-draft assessment with its original draft and Edit/Reject controls.](https://raw.githubusercontent.com/FinnNk/Meerkritic/86a839341787e986dae6870673efeaf8251a41d0/docs/images/failed-draft-assessment.png)

[Synthetic capture notes](https://github.com/FinnNk/Meerkritic/blob/86a839341787e986dae6870673efeaf8251a41d0/docs/images/README.md). The image illustrates the controls, not a research judgement.

## Review sequence

| Commit | Review proposition |
| --- | --- |
| `9e8e91d` | Record the agreed preparation amendment and preservation decision. |
| `d9933b6` | Preserve failed outputs through decisions, progress and versioned selections, including legacy compatibility. |
| `72ca780` | Add the source-backed correction screen, focused guide and browser coverage. |
| `86a8393` | Backfill current guides, screenshots and implementation records; mark ADR-0013 implemented. |

## Validation

**Standard checks: passed** at `86a8393`. [Evidence](https://github.com/FinnNk/Meerkritic/tree/03c3c30bde01106710135e42999f90ced0d47ce0/records/r1/verification-summary.json). All four semantic checkpoints passed separately with locked dependencies on Windows/Python 3.12; final total **229 tests, 0 skipped**.

| Coverage added | Tests |
| --- | ---: |
| Decision eligibility, immutable provenance, atomic events, restart, progress and selection compatibility | 10 |
| Browser controls, escaped text, retained edits and infrastructure failures | 4 |

No existing test was removed or altered. A full run caught a legacy-result compatibility regression; it was fixed before reconstruction. Earlier runs also hit an intermittent Windows temporary-Git cleanup lock. A 40-run isolated check passed using the normal OS temporary directory, which subsequent verification uses; the lock owner remains unidentified. [Failures and dispositions](https://github.com/FinnNk/Meerkritic/tree/03c3c30bde01106710135e42999f90ced0d47ce0/records/r1/backend-discovery.md) are retained, with no ignored errors or weakened checks.

- [Upgrade rehearsal](https://github.com/FinnNk/Meerkritic/tree/03c3c30bde01106710135e42999f90ced0d47ce0/records/r1/upgrade-rehearsal.json): every application table unchanged on a study-database copy; all 33 successful and 22 failed outputs retain their hashes and correct actions.
- [Live upgrade](https://github.com/FinnNk/Meerkritic/tree/03c3c30bde01106710135e42999f90ced0d47ce0/records/r1/live-after.json): all 55 original result files unchanged; zero research annotations or grouping runs.
- [Synthetic browser exercise](https://github.com/FinnNk/Meerkritic/tree/03c3c30bde01106710135e42999f90ced0d47ce0/records/r1/browser-check.json): invalid correction retained, valid correction saved, original failure still visible.
- [Documentation](https://github.com/FinnNk/Meerkritic/tree/03c3c30bde01106710135e42999f90ced0d47ce0/records/r1/docs-check.json): links, tables, imported-source hashes and screenshots checked. [Typed architecture delta](https://github.com/FinnNk/Meerkritic/tree/03c3c30bde01106710135e42999f90ced0d47ce0/records/r1/architecture-delta.json): existing interfaces extended; no new modules or boundary exceptions.
- [DER packet](https://github.com/FinnNk/Meerkritic/tree/03c3c30bde01106710135e42999f90ced0d47ce0): exact diary/semantic tracked-tree equivalence and full author self-review. This is local verification, not independent approval or a hosted CI claim.

## Study handoff

The database is backed up before upgrade. No research annotation or additional model call was made. Human **input reviews** can now proceed in the fixed candidate order, stopping at 40 usable inputs or the agreed shortfall limit, with at most five per repository. Forty is possible, not guaranteed. Group-coherence ratings wait for the reviewed selection to be frozen and EDR-0001 registered; VS2 remains active.
