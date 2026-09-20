# Architecture evidence

Generate deterministic typed JSON from Tach, Import Linter and Python metadata:

```sh
uv run --locked python tools/architecture.py snapshot > ../extras/architecture-after.json
uv run --locked python tools/architecture.py snapshot --root <baseline-checkout> > ../extras/architecture-before.json
uv run --locked python tools/architecture.py delta ../extras/architecture-before.json ../extras/architecture-after.json > ../extras/architecture-delta.json
```

Use pinned clean checkouts and record their Git identities beside the outputs in
external review evidence. Schema version 2 contains typed module, import, boundary,
contract and public interface records. Interfaces include declared callable signatures
(annotations, defaults, decorators and async), class bases and annotated fields.
The delta includes changed settings; changed records appear
as removed plus added. Ordering is deterministic with no machine paths or timestamps.

Imports are syntax-level dependencies, including external imports and those inside
functions/type-checking blocks. They are not runtime call paths or exhaustive dynamic
import resolution. Import Linter and Tach remain the enforced checks. Later diagrams
are projections of these typed records. No Archify dependency is introduced.

Interface records describe syntax, not inferred types or behavioural compatibility.
Inherited/dynamic members and undocumented runtime conventions need manual review.
Constructors are included; other underscore-prefixed declarations are omitted.
For a before/after comparison use the same generator and Python version on both
checkouts: regenerate both sides with schema 2 rather than comparing schema 1 with
schema 2. Archived pairs of schema-1 snapshots can still be compared. Preserve the
original evidence and record the newer generator's revision alongside regenerated data.
