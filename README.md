# Annotation correction evidence

Software revision `9178de6ae6ff5aaaaf45497c0b79fd4efa217980` adds explicit append-only corrections. One semantic commit
contains the complete contract, migration, operator command, tests, guide and ADR.

- `verification.json`: exact revision, environment, results and limitations.
- `semantic-check.log`: all standard checks and 259 passing tests at the semantic checkpoint.
- `diary-final-check.log`: separate full verification of the frozen diary.
- `equivalence.json`, `manifest.json` and Git bundle: exact paired history and tree evidence.
- `review.md`: contract challenges, self-review, honest failed-attempt dispositions.
- `architecture-*.json`: typed before/after/delta with no boundary or dependency change.

Research data, annotation contents, backups and credentials are excluded. The two live
corrections were separately authorised and checked against retained human approvals.
This evidence is local verification, not owner acceptance or independent review.
