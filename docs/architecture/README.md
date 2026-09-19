# Architecture evidence

Generate deterministic typed JSON from Tach, Import Linter and Python metadata:

```sh
uv run --locked python tools/architecture.py snapshot > ../extras/architecture-after.json
uv run --locked python tools/architecture.py snapshot --root <baseline-checkout> > ../extras/architecture-before.json
uv run --locked python tools/architecture.py delta ../extras/architecture-before.json ../extras/architecture-after.json > ../extras/architecture-delta.json
```

Use pinned clean checkouts and record their Git identities beside the outputs in
external review evidence. Schema version 1 contains typed module, import, boundary
and contract records. The delta includes changed settings; changed records appear
as removed plus added. Ordering is deterministic with no machine paths or timestamps.

Imports are syntax-level dependencies, including external imports and those inside
functions/type-checking blocks. They are not runtime call paths or exhaustive dynamic
import resolution. Import Linter and Tach remain the enforced checks. Later diagrams
are projections of these typed records. No Archify dependency is introduced.
